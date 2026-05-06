"""
Widget — abstract base class for all renderable UI components.

Widgets live in a tree rooted at a :class:`~tUilKit.output.window.window.Window`'s
``content`` attribute.  The compositor calls ``render(ctx)`` on the root
widget after setting up a correctly clipped :class:`~tUilKit.output.draw.draw_context.DrawContext`.

Layout contract
---------------
1.  The compositor calls :meth:`measure` to obtain the widget's preferred
    (width, height).
2.  The compositor calls :meth:`layout` to assign the widget's final bounding
    box within the window's content area.
3.  The compositor calls :meth:`render` with a matching :class:`DrawContext`.

Widget authors
--------------
Override at minimum :meth:`render`.  Override :meth:`measure` when the widget
has a meaningful preferred size.  Override :meth:`layout` when child widgets
need to be repositioned after a resize.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple


class Widget(ABC):
    """Abstract base for all tUilKit UI components.

    Attributes
    ----------
    _x, _y : int
        Position within the parent DrawContext's local coordinate system.
    _width, _height : int
        Assigned dimensions (set by :meth:`layout`).
    """

    def __init__(self) -> None:
        self._x: int = 0
        self._y: int = 0
        self._width: int = 0
        self._height: int = 0

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    @abstractmethod
    def render(self, ctx) -> None:
        """Paint this widget into *ctx*.

        Parameters
        ----------
        ctx : DrawContext
            The clipped drawing surface.  Coordinates are local to the
            window's content area.  The compositor guarantees that *ctx*
            is already clipped to this widget's assigned bounds.
        """

    def measure(self) -> Tuple[int, int]:
        """Return the widget's preferred ``(width, height)``.

        The compositor may or may not honour this; the final size is always
        determined by :meth:`layout`.  The default returns the currently
        assigned dimensions.
        """
        return (self._width, self._height)

    def layout(self, x: int, y: int, width: int, height: int) -> None:
        """Assign the widget's bounding box in parent-local coordinates.

        Parameters
        ----------
        x, y : int
            Top-left corner in the parent widget's (or window content's)
            local coordinate system.
        width, height : int
            Available dimensions for this widget.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height


# ---------------------------------------------------------------------------
# Built-in concrete widgets
# ---------------------------------------------------------------------------


class TextWidget(Widget):
    """A simple single-line text label.

    Parameters
    ----------
    text : str
        The text to display.
    style :
        A :class:`~tUilKit.output.backend.backend.Style` for the text, or
        ``None`` for the default terminal style.
    """

    def __init__(self, text: str = "", style=None) -> None:
        super().__init__()
        self.text = text
        self.style = style

    def measure(self) -> Tuple[int, int]:
        return (len(self.text), 1)

    def render(self, ctx) -> None:
        if self.style is None:
            from tUilKit.output.backend.backend import Style
            self.style = Style()
        ctx.draw_string(0, 0, self.text, self.style)


class FilledWidget(Widget):
    """A widget that floods its entire area with a single character.

    Useful for backgrounds and testing the clip/compositor pipeline.

    Parameters
    ----------
    ch : str
        The fill character (only the first code-point is used).
    style :
        A :class:`~tUilKit.output.backend.backend.Style` for fill cells.
    """

    def __init__(self, ch: str = " ", style=None) -> None:
        super().__init__()
        self.ch = ch[0] if ch else " "
        self.style = style

    def render(self, ctx) -> None:
        if self.style is None:
            from tUilKit.output.backend.backend import Style
            self.style = Style()
        for row in range(ctx.height):
            for col in range(ctx.width):
                ctx.draw_rune(col, row, self.ch, self.style)
