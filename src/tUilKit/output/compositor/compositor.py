"""
Compositor — assembles the final terminal frame from layered windows.

Architecture
------------
The compositor maintains two equal-sized cell matrices:

*back buffer*
    Receives all draw calls for the current frame.

*front buffer*
    Represents what was last flushed to the terminal.

On every call to :meth:`render_frame`:

1. The back buffer is cleared to blank cells.
2. Windows are iterated in ascending z-order (bottom → top).
3. Each window's border (if any) is painted into the back buffer via a
   :class:`~tUilKit.output.draw.draw_context.DrawContext`.
4. The window's root :class:`~tUilKit.output.widgets.widget.Widget` (if set)
   is rendered into the content area via a second, inset DrawContext.
5. The back and front buffers are compared cell by cell; only *changed*
   cells are forwarded to the :class:`~tUilKit.output.backend.backend.RenderBackendInterface`.
6. The back buffer is promoted to the front buffer ready for the next frame.

The compositor itself exposes ``draw_rune`` and ``draw_string`` so it can
act as the *surface* parameter accepted by
:class:`~tUilKit.output.draw.draw_context.DrawContext`.
"""

from __future__ import annotations
from typing import List

from tUilKit.output.backend.backend import RenderBackendInterface, Style
from tUilKit.output.draw.draw_context import DrawContext, Rect
from tUilKit.output.draw.border import draw_titled_border


# Sentinel blank cell reused across the module.
_BLANK_STYLE = Style()
_BLANK_CELL: tuple[str, Style] = (" ", _BLANK_STYLE)


class Compositor:
    """Double-buffered terminal frame compositor.

    Parameters
    ----------
    backend : RenderBackendInterface
        The rendering backend used to flush changed cells.
    width : int
        Terminal width in columns.
    height : int
        Terminal height in rows.

    Example
    -------
    ::

        from tUilKit.output.backend.ansi_backend import AnsiRenderBackend
        from tUilKit.output.compositor.compositor import Compositor
        from tUilKit.output.window.window_manager import WindowManager

        backend = AnsiRenderBackend()
        comp = Compositor(backend, width=120, height=40)
        wm = WindowManager()
        wid = wm.create_window(x=5, y=5, width=30, height=10, title="Demo")
        comp.render_frame(wm.list_windows_in_z_order())
    """

    def __init__(
        self,
        backend: RenderBackendInterface,
        width: int,
        height: int,
    ) -> None:
        self._backend = backend
        self._width = width
        self._height = height

        # Back buffer — accumulates the current frame.
        self._back: list[list[tuple[str, Style]]] = self._alloc_buffer()
        # Front buffer — what was last sent to the terminal.
        self._front: list[list[tuple[str, Style]]] = self._alloc_buffer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_frame(self, windows: list) -> None:
        """Render all *windows* and flush only the changed cells to the backend.

        Parameters
        ----------
        windows : list[Window]
            Windows in ascending z-order (bottom-most first).
            :meth:`~tUilKit.output.window.window_manager.WindowManager.list_windows_in_z_order`
            already returns them in the correct order.
        """
        # Step 1 — clear the back buffer.
        self._clear_back()

        # Step 2 — draw each window in z-order (bottom → top).
        for win in windows:
            self._draw_window(win)

        # Step 3 — flush only changed cells to the backend.
        self._flush_diff()

    def resize(self, width: int, height: int) -> None:
        """Resize both buffers; the next :meth:`render_frame` will repaint fully."""
        self._width = width
        self._height = height
        self._back = self._alloc_buffer()
        self._front = self._alloc_buffer()

    # ------------------------------------------------------------------
    # Surface interface (consumed by DrawContext)
    # ------------------------------------------------------------------

    def draw_rune(self, x: int, y: int, ch: str, style: Style) -> None:
        """Write a single character directly into the back buffer.

        Out-of-bounds writes are silently discarded.
        """
        if 0 <= x < self._width and 0 <= y < self._height:
            self._back[y][x] = (ch, style)

    def draw_string(self, x: int, y: int, s: str, style: Style) -> None:
        """Write each character of *s* into the back buffer starting at (*x*, *y*)."""
        for offset, ch in enumerate(s):
            self.draw_rune(x + offset, y, ch, style)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _alloc_buffer(self) -> list[list[tuple[str, Style]]]:
        """Allocate a clean (blank) cell matrix."""
        return [[_BLANK_CELL] * self._width for _ in range(self._height)]

    def _clear_back(self) -> None:
        """Reset every cell in the back buffer to blank."""
        for row in self._back:
            for col in range(self._width):
                row[col] = _BLANK_CELL

    def _draw_window(self, win) -> None:
        """Paint a single *win* into the back buffer."""
        # Full window clip in screen coordinates.
        win_clip = Rect(win.x, win.y, win.width, win.height)
        win_ctx = DrawContext(self, win_clip, win.x, win.y)

        # Draw border (and optional title) in window-local coordinates.
        if win.border_style and win.border_style != "none":
            border_rect = Rect(0, 0, win.width, win.height)
            draw_titled_border(
                win_ctx,
                border_rect,
                win.border_style,
                win.title,
                border_style=_BLANK_STYLE,
            )

        # Render widget content in the inset content area.
        if win.content is not None:
            cx, cy, cw, ch = win.inner_rect()
            content_clip = Rect(cx, cy, cw, ch)
            content_ctx = DrawContext(self, content_clip, cx, cy)
            win.content.render(content_ctx)

    def _flush_diff(self) -> None:
        """Forward changed cells to the backend and promote the back buffer."""
        for y in range(self._height):
            for x in range(self._width):
                cell = self._back[y][x]
                if cell != self._front[y][x]:
                    ch, style = cell
                    self._backend.draw_rune(x, y, ch, style)
        self._backend.flush()

        # Promote back buffer → front buffer.
        for y in range(self._height):
            self._front[y] = list(self._back[y])
