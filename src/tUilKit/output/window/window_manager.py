"""
WindowManager — owns the window registry, focus state, z-order, and geometry.

Usage
-----
::

    from tUilKit.output.window.window_manager import WindowManager

    wm = WindowManager()
    wid = wm.create_window(x=2, y=2, width=40, height=12, title="Hello")
    wm.focus_window(wid)
    windows = wm.list_windows_in_z_order()
"""

from __future__ import annotations
import uuid
from typing import Any, List, Optional

from tUilKit.output.window.window import Window
from tUilKit.output.zorder.zorder import ZOrderManager


class WindowManager:
    """Central registry that owns all live windows.

    Responsibilities
    ----------------
    *   Create and destroy windows.
    *   Track which window has keyboard focus.
    *   Delegate z-order manipulation to :class:`~tUilKit.output.zorder.zorder.ZOrderManager`.
    *   Provide geometry mutation (move / resize).
    """

    def __init__(self) -> None:
        # id -> Window mapping.
        self._registry: dict[str, Window] = {}
        self._zorder = ZOrderManager()
        self._focused_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def create_window(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 80,
        height: int = 24,
        z_index: int = 0,
        content: Optional[Any] = None,
        border_style: str = "single",
        focusable: bool = True,
        title: str = "",
    ) -> str:
        """Create a new window and return its unique identifier.

        Parameters
        ----------
        x, y : int
            Top-left position in screen coordinates.
        width, height : int
            Dimensions in columns and rows.
        z_index : int
            Initial z-index (higher = drawn on top).
        content :
            Root :class:`~tUilKit.output.widgets.widget.Widget` to render
            inside the window, or ``None``.
        border_style : str
            Border style name (``"single"``, ``"double"``, ``"heavy"``,
            ``"rounded"``, or ``"none"``).
        focusable : bool
            Whether the window can receive focus.
        title : str
            Optional title string embedded in the top border.

        Returns
        -------
        str
            The UUID of the newly created window.
        """
        win = Window(
            id=str(uuid.uuid4()),
            x=x,
            y=y,
            width=width,
            height=height,
            z_index=z_index,
            content=content,
            border_style=border_style,
            focusable=focusable,
            title=title,
        )
        self._registry[win.id] = win
        self._zorder.add(win)
        return win.id

    def close_window(self, window_id: str) -> None:
        """Destroy the window identified by *window_id*.

        If the window held focus the focus state is cleared.
        """
        if window_id not in self._registry:
            return
        del self._registry[window_id]
        self._zorder.remove(window_id)
        if self._focused_id == window_id:
            self._focused_id = None

    # ------------------------------------------------------------------
    # Geometry mutation
    # ------------------------------------------------------------------

    def move_window(self, window_id: str, x: int, y: int) -> None:
        """Move *window_id* to (*x*, *y*) in screen coordinates."""
        win = self._registry.get(window_id)
        if win is not None:
            win.x, win.y = x, y

    def resize_window(self, window_id: str, width: int, height: int) -> None:
        """Resize *window_id* to *width* × *height*."""
        win = self._registry.get(window_id)
        if win is not None:
            win.width, win.height = width, height

    # ------------------------------------------------------------------
    # Focus management
    # ------------------------------------------------------------------

    def focus_window(self, window_id: str) -> None:
        """Give keyboard focus to *window_id*.

        The previously focused window loses focus.  The newly focused window
        is also raised to the top of the z-order.
        """
        if self._focused_id and self._focused_id in self._registry:
            self._registry[self._focused_id]._focused = False
        win = self._registry.get(window_id)
        if win is not None and win.focusable:
            win._focused = True
            self._focused_id = window_id
            self._zorder.raise_window(window_id)

    # ------------------------------------------------------------------
    # Z-order API
    # ------------------------------------------------------------------

    def raise_window(self, window_id: str) -> None:
        """Raise *window_id* above all other windows."""
        self._zorder.raise_window(window_id)

    def lower_window(self, window_id: str) -> None:
        """Lower *window_id* below all other windows."""
        self._zorder.lower_window(window_id)

    def set_z_index(self, window_id: str, z: int) -> None:
        """Assign an explicit *z* index to *window_id*."""
        self._zorder.set_z_index(window_id, z)

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def list_windows_in_z_order(self) -> List[Window]:
        """Return all windows sorted by z-index (bottom to top)."""
        return self._zorder.list_in_z_order()

    def get_window(self, window_id: str) -> Optional[Window]:
        """Return the :class:`Window` for *window_id*, or ``None``."""
        return self._registry.get(window_id)

    @property
    def focused_id(self) -> Optional[str]:
        """The UUID of the currently focused window, or ``None``."""
        return self._focused_id

    @property
    def window_count(self) -> int:
        """Number of live windows."""
        return len(self._registry)
