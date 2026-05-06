"""
Window dataclass — the fundamental unit of screen real-estate.

A Window is a rectangular region on the terminal screen.  It has a
position, size, z-index, an optional content widget, and a border style.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class Window:
    """Represents a single terminal window.

    Attributes
    ----------
    id : str
        Universally-unique identifier.  Auto-generated if not supplied.
    x : int
        Left edge column (0-based screen coordinates).
    y : int
        Top edge row (0-based screen coordinates).
    width : int
        Width in terminal columns.
    height : int
        Height in terminal rows.
    z_index : int
        Painting order — higher values appear on top of lower values.
    content : Widget or None
        Root widget rendered inside this window's content area.
    border_style : str
        One of ``"single"``, ``"double"``, ``"heavy"``, ``"rounded"``,
        or ``"none"``.  Defaults to ``"single"``.
    focusable : bool
        Whether this window can receive keyboard focus.
    title : str
        Optional title displayed in the top border (not rendered if empty).
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    x: int = 0
    y: int = 0
    width: int = 80
    height: int = 24
    z_index: int = 0
    content: Optional[Any] = field(default=None, repr=False)
    border_style: str = "single"
    focusable: bool = True
    title: str = ""
    # Internal: whether this window currently holds keyboard focus.
    _focused: bool = field(default=False, repr=False, compare=False)

    @property
    def focused(self) -> bool:
        """``True`` when this window holds keyboard focus."""
        return self._focused

    def inner_rect(self):
        """Return (x, y, width, height) of the content area.

        If a border is drawn the content area is inset by one cell on every
        side.  If no border is requested the full window area is returned.
        """
        if self.border_style and self.border_style != "none":
            return (
                self.x + 1,
                self.y + 1,
                max(0, self.width - 2),
                max(0, self.height - 2),
            )
        return (self.x, self.y, self.width, self.height)
