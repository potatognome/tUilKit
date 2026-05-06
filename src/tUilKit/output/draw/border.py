"""
Border drawing utilities for terminal windows.

Supported styles
----------------
``"single"``
    Box-drawing light lines: ┌ ─ ┐ │ └ ┘
``"double"``
    Box-drawing double lines: ╔ ═ ╗ ║ ╚ ╝
``"heavy"``
    Box-drawing heavy/thick lines: ┏ ━ ┓ ┃ ┗ ┛
``"rounded"``
    Light lines with rounded corners: ╭ ─ ╮ │ ╰ ╯

All characters are standard Unicode box-drawing code points (U+2500 block).
"""

from __future__ import annotations
from typing import Dict, Optional
from tUilKit.output.draw.draw_context import DrawContext, Rect


# ---------------------------------------------------------------------------
# Border character sets
# ---------------------------------------------------------------------------

_BORDER_CHARS: Dict[str, Dict[str, str]] = {
    "single": {
        "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
        "h":  "─", "v":  "│",
    },
    "double": {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h":  "═", "v":  "║",
    },
    "heavy": {
        "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛",
        "h":  "━", "v":  "┃",
    },
    "rounded": {
        "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
        "h":  "─", "v":  "│",
    },
}


def get_border_chars(style: str) -> Dict[str, str]:
    """Return the character mapping for *style*, defaulting to ``"single"``."""
    return _BORDER_CHARS.get(style, _BORDER_CHARS["single"])


def draw_border(
    ctx: DrawContext,
    rect: Rect,
    style: str,
    border_style=None,
) -> None:
    """Draw a rectangular border onto *ctx*.

    Parameters
    ----------
    ctx : DrawContext
        The drawing surface (window-local coordinates).
    rect : Rect
        The bounding rectangle for the border in *ctx*-local coordinates.
        Must be at least 2×2; smaller rects are silently ignored.
    style : str
        Border character style: ``"single"``, ``"double"``, ``"heavy"``,
        or ``"rounded"``.
    border_style :
        A :class:`~tUilKit.output.backend.backend.Style` instance used for
        every border cell.  Pass ``None`` for the default terminal style.

    Notes
    -----
    If *border_style* is ``None`` the function imports
    :class:`~tUilKit.output.backend.backend.Style` lazily to avoid circular
    imports.
    """
    if border_style is None:
        from tUilKit.output.backend.backend import Style
        border_style = Style()

    chars = get_border_chars(style)
    x, y = rect.x, rect.y
    w, h = rect.width, rect.height

    if w < 2 or h < 2:
        return

    # Corners
    ctx.draw_rune(x,         y,         chars["tl"], border_style)
    ctx.draw_rune(x + w - 1, y,         chars["tr"], border_style)
    ctx.draw_rune(x,         y + h - 1, chars["bl"], border_style)
    ctx.draw_rune(x + w - 1, y + h - 1, chars["br"], border_style)

    # Horizontal edges
    for col in range(x + 1, x + w - 1):
        ctx.draw_rune(col, y,         chars["h"], border_style)
        ctx.draw_rune(col, y + h - 1, chars["h"], border_style)

    # Vertical edges
    for row in range(y + 1, y + h - 1):
        ctx.draw_rune(x,         row, chars["v"], border_style)
        ctx.draw_rune(x + w - 1, row, chars["v"], border_style)


def draw_titled_border(
    ctx: DrawContext,
    rect: Rect,
    style: str,
    title: str,
    border_style=None,
    title_style=None,
) -> None:
    """Draw a border with an optional *title* embedded in the top edge.

    The title is centred between the top-left and top-right corners.
    It is truncated if it would overflow the available space.

    Parameters
    ----------
    ctx : DrawContext
        The drawing surface (window-local coordinates).
    rect : Rect
        Bounding rectangle for the border.
    style : str
        Border character style.
    title : str
        Text to embed in the top border.  Pass empty string to omit.
    border_style :
        :class:`~tUilKit.output.backend.backend.Style` for border characters.
    title_style :
        :class:`~tUilKit.output.backend.backend.Style` for title characters.
        Falls back to *border_style* if not supplied.
    """
    draw_border(ctx, rect, style, border_style)

    if not title:
        return

    if border_style is None:
        from tUilKit.output.backend.backend import Style
        border_style = Style()
    if title_style is None:
        title_style = border_style

    # Inner width available for the title (between the corner characters).
    inner_w = rect.width - 2
    if inner_w <= 0:
        return

    # Centre the title; truncate if necessary.
    label = f" {title} "
    if len(label) > inner_w:
        label = label[:inner_w]

    start_col = rect.x + 1 + max(0, (inner_w - len(label)) // 2)
    ctx.draw_string(start_col, rect.y, label, title_style)
