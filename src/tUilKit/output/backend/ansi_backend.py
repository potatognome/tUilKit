"""
AnsiRenderBackend — default terminal backend using ANSI escape sequences.

Design
------
*   Absolute cursor positioning via ``\\033[row;colH`` — no scrolling side-effects.
*   Internal back-buffer accumulates draw calls between flushes.
*   On ``flush()`` only cells that differ from the front buffer are written,
    minimising terminal I/O and visible flicker.
*   The front buffer is updated to match the back buffer after every flush.
"""

import sys
from tUilKit.output.backend.backend import RenderBackendInterface, Style

# Compile-time constants for ANSI escape sequences.
_RESET = "\033[0m"
_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"


def _build_style_seq(style: Style) -> str:
    """Return the opening ANSI sequence for *style*, or empty string."""
    if not style:
        return ""
    codes = []
    if style.bold:
        codes.append("1")
    if style.dim:
        codes.append("2")
    if style.underline:
        codes.append("4")
    if style.reverse:
        codes.append("7")
    seq = ("\033[" + ";".join(codes) + "m") if codes else ""
    return style.fg + style.bg + seq


class AnsiRenderBackend(RenderBackendInterface):
    """ANSI-escape-sequence rendering backend.

    Parameters
    ----------
    stream :
        Output stream to write to.  Defaults to ``sys.stdout``.

    Notes
    -----
    The backend operates entirely through an internal back-buffer.
    Callers accumulate draw calls and then call ``flush()`` once per frame.
    """

    def __init__(self, stream=None) -> None:
        self._stream = stream or sys.stdout
        # Mapping (col, row) -> (char, Style) for the current frame.
        self._back: dict[tuple[int, int], tuple[str, Style]] = {}
        # Mapping (col, row) -> (char, Style) for the last flushed frame.
        self._front: dict[tuple[int, int], tuple[str, Style]] = {}

    # ------------------------------------------------------------------
    # RenderBackendInterface implementation
    # ------------------------------------------------------------------

    def move_cursor(self, x: int, y: int) -> None:
        """Write an absolute cursor-positioning sequence to the stream."""
        self._stream.write(f"\033[{y + 1};{x + 1}H")

    def draw_rune(self, x: int, y: int, ch: str, style: Style) -> None:
        """Stage a single character at (*x*, *y*).  Only the first code-point is used."""
        if ch:
            self._back[(x, y)] = (ch[0], style)

    def draw_string(self, x: int, y: int, s: str, style: Style) -> None:
        """Stage every character of *s* starting at (*x*, *y*)."""
        for offset, ch in enumerate(s):
            self._back[(x + offset, y)] = (ch, style)

    def flush(self) -> None:
        """Write only the cells that changed since the last flush.

        Cells are written with absolute cursor positioning so the output is
        order-independent and requires no scrolling.
        """
        buf = []
        for (x, y), (ch, style) in self._back.items():
            if self._front.get((x, y)) != (ch, style):
                # Move to the cell position.
                buf.append(f"\033[{y + 1};{x + 1}H")
                seq = _build_style_seq(style)
                if seq:
                    buf.append(seq)
                buf.append(ch)
                if seq:
                    buf.append(_RESET)
        if buf:
            self._stream.write("".join(buf))
            self._stream.flush()
        # Promote back buffer to front buffer.
        self._front = dict(self._back)
        self._back = {}

    def clear_region(self, x: int, y: int, width: int, height: int) -> None:
        """Stage blank-space cells over the given rectangular region."""
        blank_style = Style()
        for row in range(y, y + height):
            for col in range(x, x + width):
                self._back[(col, row)] = (" ", blank_style)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def hide_cursor(self) -> None:
        """Hide the hardware cursor (reduces flicker during redraws)."""
        self._stream.write(_HIDE_CURSOR)

    def show_cursor(self) -> None:
        """Restore the hardware cursor."""
        self._stream.write(_SHOW_CURSOR)
