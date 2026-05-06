"""
Style dataclass and RenderBackendInterface for the tUilKit rendering pipeline.

Architecture
------------
RenderBackendInterface defines the contract every backend must satisfy.
Concrete backends (e.g. AnsiRenderBackend) translate the abstract draw calls
into terminal escape sequences or other output formats.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Style:
    """Visual style for a single terminal cell.

    Attributes
    ----------
    fg : str
        ANSI foreground colour escape sequence (e.g. ``'\\033[38;2;255;0;0m'``).
        Empty string means default/terminal foreground.
    bg : str
        ANSI background colour escape sequence.  Empty string means default.
    bold : bool
        Apply bold (increased intensity) attribute.
    dim : bool
        Apply dim (decreased intensity) attribute.
    underline : bool
        Apply underline attribute.
    reverse : bool
        Swap foreground and background colours.
    """

    fg: str = ""
    bg: str = ""
    bold: bool = False
    dim: bool = False
    underline: bool = False
    reverse: bool = False


class RenderBackendInterface(ABC):
    """Abstract base for terminal rendering backends.

    Implementations convert abstract draw operations into terminal output.
    All coordinates are zero-based (column 0, row 0 is the top-left cell).
    """

    @abstractmethod
    def move_cursor(self, x: int, y: int) -> None:
        """Move the physical terminal cursor to column *x*, row *y*."""

    @abstractmethod
    def draw_rune(self, x: int, y: int, ch: str, style: Style) -> None:
        """Schedule a single character *ch* at (*x*, *y*) with *style*.

        Only the first character of *ch* is used if a multi-character string
        is supplied.
        """

    @abstractmethod
    def draw_string(self, x: int, y: int, s: str, style: Style) -> None:
        """Schedule every character of *s* starting at (*x*, *y*)."""

    @abstractmethod
    def flush(self) -> None:
        """Push all pending draws to the terminal output stream."""

    @abstractmethod
    def clear_region(self, x: int, y: int, width: int, height: int) -> None:
        """Fill a rectangular region with blank space cells."""
