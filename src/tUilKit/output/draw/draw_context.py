"""
Rect and DrawContext — the clipped drawing surface passed to widgets.

Architecture
------------
When the compositor renders a window it creates a :class:`DrawContext` that
knows:

1. The *clip rectangle* — the screen-coordinate bounding box outside which
   nothing may be drawn.
2. The *surface* — any object implementing ``draw_rune(x, y, ch, style)``
   and ``draw_string(x, y, s, style)``.  In production this is the
   :class:`~tUilKit.output.compositor.compositor.Compositor`'s back-buffer.
3. The *offset* — the screen position of the window's local origin ``(0, 0)``.

Widgets draw using *window-local* coordinates.  The DrawContext translates
those coordinates to screen coordinates and clips before forwarding to the
surface.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Rect:
    """Axis-aligned rectangle in screen (column, row) coordinates.

    Attributes
    ----------
    x : int
        Left column (inclusive).
    y : int
        Top row (inclusive).
    width : int
        Number of columns.
    height : int
        Number of rows.
    """

    x: int
    y: int
    width: int
    height: int

    def contains(self, sx: int, sy: int) -> bool:
        """Return ``True`` if the screen point (*sx*, *sy*) lies inside."""
        return (
            self.x <= sx < self.x + self.width
            and self.y <= sy < self.y + self.height
        )

    def intersects(self, other: "Rect") -> bool:
        """Return ``True`` if this rect and *other* overlap."""
        return (
            self.x < other.x + other.width
            and self.x + self.width > other.x
            and self.y < other.y + other.height
            and self.y + self.height > other.y
        )


class DrawContext:
    """Clipped drawing surface passed to widgets during rendering.

    All coordinates supplied to :meth:`draw_rune` and :meth:`draw_string`
    are **window-local** — the origin ``(0, 0)`` is the top-left of the
    window's content area.

    The DrawContext silently discards any draw calls whose translated screen
    coordinate falls outside the clip rectangle.

    Parameters
    ----------
    surface :
        Object with ``draw_rune(x, y, ch, style)`` and
        ``draw_string(x, y, s, style)`` methods.  Typically the
        :class:`~tUilKit.output.compositor.compositor.Compositor` instance.
    clip : Rect
        Screen-coordinate rectangle that constrains all drawing.
    offset_x : int
        Column offset added to every x coordinate before clipping.
    offset_y : int
        Row offset added to every y coordinate before clipping.
    """

    def __init__(
        self,
        surface: Any,
        clip: Rect,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> None:
        self._surface = surface
        self._clip = clip
        self._offset_x = offset_x
        self._offset_y = offset_y

    # ------------------------------------------------------------------
    # Drawing methods (window-local coordinates)
    # ------------------------------------------------------------------

    def draw_rune(self, x: int, y: int, ch: str, style) -> None:
        """Draw a single character at window-local (*x*, *y*).

        The call is silently ignored if the translated screen position is
        outside the clip rectangle or *ch* is empty.
        """
        if not ch:
            return
        sx = self._offset_x + x
        sy = self._offset_y + y
        if self._clip.contains(sx, sy):
            self._surface.draw_rune(sx, sy, ch[0], style)

    def draw_string(self, x: int, y: int, s: str, style) -> None:
        """Draw every character of *s* starting at window-local (*x*, *y*).

        Characters whose translated screen position falls outside the clip
        rectangle are silently skipped.
        """
        for offset, ch in enumerate(s):
            self.draw_rune(x + offset, y, ch, style)

    # ------------------------------------------------------------------
    # Sub-context factory
    # ------------------------------------------------------------------

    def sub_context(self, local_x: int, local_y: int, width: int, height: int) -> "DrawContext":
        """Create a child DrawContext for a sub-region of this context.

        The child's local origin is at window-local (*local_x*, *local_y*).
        The child's clip is the intersection of the parent clip and the
        sub-region so children cannot escape their parent.

        Parameters
        ----------
        local_x, local_y : int
            Top-left corner of the sub-region in the *parent's* local coords.
        width, height : int
            Dimensions of the sub-region.
        """
        # Convert sub-region to screen coordinates.
        sx = self._offset_x + local_x
        sy = self._offset_y + local_y
        sub_clip = Rect(
            max(sx, self._clip.x),
            max(sy, self._clip.y),
            min(sx + width, self._clip.x + self._clip.width) - max(sx, self._clip.x),
            min(sy + height, self._clip.y + self._clip.height) - max(sy, self._clip.y),
        )
        # Clamp negative dimensions to zero.
        sub_clip = Rect(
            sub_clip.x,
            sub_clip.y,
            max(0, sub_clip.width),
            max(0, sub_clip.height),
        )
        return DrawContext(self._surface, sub_clip, sx, sy)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def clip(self) -> Rect:
        """The clip rectangle in screen coordinates."""
        return self._clip

    @property
    def width(self) -> int:
        """Width of the clip rectangle."""
        return self._clip.width

    @property
    def height(self) -> int:
        """Height of the clip rectangle."""
        return self._clip.height
