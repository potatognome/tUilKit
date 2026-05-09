#!/usr/bin/env python3
"""
examples/compositor_examples.py — tUilKit compositor demonstration suite.

Demonstrates the full compositor stack:
    backend     → AnsiRenderBackend / StringCaptureBackend
    zorder      → ZOrderManager (layered window stacking)
    window      → Window dataclass + WindowManager
    draw        → DrawContext (clipped drawing)
    widgets     → Widget subclasses
    compositor  → Compositor (double-buffered frame assembly)

Run individual demos:
    python compositor_examples.py --demo basic
    python compositor_examples.py --demo zorder
    python compositor_examples.py --demo borders
    python compositor_examples.py --demo widget
    python compositor_examples.py --demo capture
    python compositor_examples.py --demo all

Options:
    --delay SECS    Pause between frames (default 0.5).
    --width  COLS   Terminal width for demos  (default 80).
    --height ROWS   Terminal height for demos (default 24).
    --no-clear      Do not clear the screen between demos.
"""

from __future__ import annotations

import argparse
import sys
import time
from io import StringIO
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: resolve src path from test_paths.json
# ---------------------------------------------------------------------------
import json

HERE = Path(__file__).resolve()
_paths_file = HERE.parent / "test_paths.json"
if not _paths_file.exists():
    raise FileNotFoundError(
        "test_paths.json not found.  Run 'python TESTS_CONFIG.py' first."
    )
with open(_paths_file, encoding="utf-8") as _f:
    _p = json.load(_f)

PROJECT_ROOT = Path(_p["project_root"])
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# ---------------------------------------------------------------------------
# Compositor imports (after sys.path is set)
# ---------------------------------------------------------------------------
from tUilKit.output.backend.backend import RenderBackendInterface, Style  # noqa: E402
from tUilKit.output.backend.ansi_backend import AnsiRenderBackend  # noqa: E402
from tUilKit.output.compositor.compositor import Compositor  # noqa: E402
from tUilKit.output.window.window_manager import WindowManager  # noqa: E402
from tUilKit.output.widgets.widget import Widget  # noqa: E402
from tUilKit.output.draw.draw_context import DrawContext, Rect  # noqa: E402


# ---------------------------------------------------------------------------
# StringCaptureBackend — records draw calls to a string buffer (no ANSI I/O)
# ---------------------------------------------------------------------------

class StringCaptureBackend(RenderBackendInterface):
    """A test / headless backend that captures draw calls as plain text.

    Call :meth:`render_text` after :meth:`flush` to get a grid of characters
    that can be printed or asserted in tests.
    """

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._cells: dict[tuple[int, int], str] = {}

    def move_cursor(self, x: int, y: int) -> None:  # noqa: D401
        pass  # No cursor movement needed for capture.

    def draw_rune(self, x: int, y: int, ch: str, style: Style) -> None:
        if 0 <= x < self._width and 0 <= y < self._height and ch:
            self._cells[(x, y)] = ch[0]

    def draw_string(self, x: int, y: int, s: str, style: Style) -> None:
        for offset, ch in enumerate(s):
            cx = x + offset
            if 0 <= cx < self._width and 0 <= y < self._height:
                self._cells[(cx, y)] = ch

    def flush(self) -> None:
        pass  # Nothing to flush — cells are already captured in memory.

    def clear_region(self, x: int, y: int, width: int, height: int) -> None:
        for row in range(y, y + height):
            for col in range(x, x + width):
                self._cells[(col, row)] = " "

    def render_text(self) -> str:
        """Return the captured frame as a multi-line string of plain characters."""
        lines = []
        for row in range(self._height):
            line = "".join(self._cells.get((col, row), " ") for col in range(self._width))
            lines.append(line.rstrip())
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Concrete widget implementations used by demos
# ---------------------------------------------------------------------------

class TextWidget(Widget):
    """Widget that renders a list of text lines into the draw context."""

    def __init__(self, lines: list[str], style: Style | None = None) -> None:
        super().__init__()
        self._lines = lines
        self._style = style or Style()

    def render(self, ctx: DrawContext) -> None:
        for row, line in enumerate(self._lines):
            if row >= self._height:
                break
            ctx.draw_string(0, row, line[: self._width], self._style)


class ClockWidget(Widget):
    """Widget that renders the current time (updated each :meth:`tick`)."""

    def __init__(self) -> None:
        super().__init__()
        self._text = ""

    def tick(self) -> None:
        import datetime
        self._text = datetime.datetime.now().strftime("%H:%M:%S")

    def render(self, ctx: DrawContext) -> None:
        ctx.draw_string(0, 0, self._text.center(self._width), Style(bold=True))


class GridWidget(Widget):
    """Fills the content area with a repeating dot pattern to demonstrate clipping."""

    def render(self, ctx: DrawContext) -> None:
        for row in range(self._height):
            for col in range(self._width):
                ch = "·" if (row + col) % 2 == 0 else " "
                ctx.draw_rune(col, row, ch, Style(dim=True))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_ansi(width: int, height: int) -> tuple[AnsiRenderBackend, Compositor]:
    backend = AnsiRenderBackend()
    comp = Compositor(backend, width=width, height=height)
    return backend, comp


def _pause(delay: float) -> None:
    if delay > 0:
        time.sleep(delay)


def _clear() -> None:
    import os
    os.system("cls" if sys.platform == "win32" else "clear")


def _safe_print(text: str = "") -> None:
    """Print text without crashing on legacy console encodings (e.g. cp1252)."""
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        sanitized = str(text).encode(encoding, errors="replace").decode(encoding, errors="replace")
        sys.stdout.write(sanitized + "\n")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Demo 1 — Basic: one window with text content
# ---------------------------------------------------------------------------

def demo_basic(width: int = 80, height: int = 24, delay: float = 0.5, clear: bool = True) -> None:
    """Minimal compositor setup: one window with a TextWidget."""
    print("=== Demo: basic ===")
    print("Creates a single window with a text widget and renders two frames.\n")

    backend, comp = _build_ansi(width, height)
    wm = WindowManager()

    content = TextWidget([
        "Welcome to tUilKit compositor!",
        "",
        "This is a basic single-window demo.",
        "The double-buffered compositor only",
        "flushes changed cells on each frame.",
    ])
    content.layout(0, 0, width - 4, height - 4)

    wid = wm.create_window(
        x=2, y=2, width=width - 4, height=height - 4,
        title=" Basic Window ",
        border_style="single",
        content=content,
    )

    backend.hide_cursor()
    try:
        if clear:
            _clear()
        # Frame 1 — initial render
        comp.render_frame(wm.list_windows_in_z_order())
        _pause(delay)

        # Frame 2 — update content and redraw (only changed cells are flushed)
        content._lines[2] = "Frame 2: only changed cells flushed."
        comp.render_frame(wm.list_windows_in_z_order())
        _pause(delay)
    finally:
        backend.show_cursor()
        # Move cursor below the window
        sys.stdout.write(f"\033[{height + 1};1H\n")
        sys.stdout.flush()

    print("\ndemo_basic complete.")


# ---------------------------------------------------------------------------
# Demo 2 — Z-order: three overlapping windows
# ---------------------------------------------------------------------------

def demo_zorder(width: int = 80, height: int = 24, delay: float = 0.8, clear: bool = True) -> None:
    """Three windows with explicit z-order; demonstrates raise/lower API."""
    print("=== Demo: zorder ===")
    print("Three overlapping windows; cycles through raising each to the top.\n")

    backend, comp = _build_ansi(width, height)
    wm = WindowManager()

    specs = [
        dict(x=2,  y=2,  width=30, height=10, title=" Window A (z=0) ", z_index=0,
             lines=["Window A", "z_index = 0", "I start at the bottom."]),
        dict(x=8,  y=5,  width=30, height=10, title=" Window B (z=1) ", z_index=1,
             lines=["Window B", "z_index = 1", "I start in the middle."]),
        dict(x=14, y=8,  width=30, height=10, title=" Window C (z=2) ", z_index=2,
             lines=["Window C", "z_index = 2", "I start on top."]),
    ]

    wids = []
    for spec in specs:
        lines = spec.pop("lines")
        widget = TextWidget(lines)
        widget.layout(0, 0, spec["width"] - 2, spec["height"] - 2)
        spec["content"] = widget
        wids.append(wm.create_window(**spec))

    backend.hide_cursor()
    try:
        if clear:
            _clear()

        # Initial render
        comp.render_frame(wm.list_windows_in_z_order())
        _pause(delay)

        # Cycle: raise each window in turn
        for i, wid in enumerate(wids):
            wm.raise_window(wid)
            comp.render_frame(wm.list_windows_in_z_order())
            _pause(delay)
    finally:
        backend.show_cursor()
        sys.stdout.write(f"\033[{height + 1};1H\n")
        sys.stdout.flush()

    print("\ndemo_zorder complete.")


# ---------------------------------------------------------------------------
# Demo 3 — Move / resize a window across frames
# ---------------------------------------------------------------------------

def demo_move_resize(width: int = 80, height: int = 24, delay: float = 0.4, clear: bool = True) -> None:
    """Shows move_window and resize_window updating across frames."""
    print("=== Demo: move_resize ===")
    print("Animates a window sliding right and growing taller.\n")

    backend, comp = _build_ansi(width, height)
    wm = WindowManager()

    widget = TextWidget(["Moving window", "Each frame shifts right +4"])
    widget.layout(0, 0, 28, 8)

    wid = wm.create_window(x=1, y=2, width=30, height=6, title=" Moving ", content=widget)

    backend.hide_cursor()
    try:
        if clear:
            _clear()
        for step in range(6):
            wm.move_window(wid, x=1 + step * 4, y=2)
            wm.resize_window(wid, width=30, height=6 + step)
            comp.render_frame(wm.list_windows_in_z_order())
            _pause(delay)
    finally:
        backend.show_cursor()
        sys.stdout.write(f"\033[{height + 1};1H\n")
        sys.stdout.flush()

    print("\ndemo_move_resize complete.")


# ---------------------------------------------------------------------------
# Demo 4 — Border styles
# ---------------------------------------------------------------------------

def demo_borders(width: int = 80, height: int = 24, delay: float = 1.0, clear: bool = True) -> None:
    """Four windows side by side — one for each supported border style."""
    print("=== Demo: borders ===")
    print("Displays all four border styles side by side.\n")

    backend, comp = _build_ansi(width, height)
    wm = WindowManager()

    styles = ["single", "double", "heavy", "rounded"]
    col_w = max(12, width // len(styles))

    for idx, style in enumerate(styles):
        widget = TextWidget([style])
        widget.layout(0, 0, col_w - 2, 3)
        wm.create_window(
            x=idx * col_w, y=2,
            width=col_w - 1, height=5,
            title=f" {style} ",
            border_style=style,
            content=widget,
        )

    backend.hide_cursor()
    try:
        if clear:
            _clear()
        comp.render_frame(wm.list_windows_in_z_order())
        _pause(delay)
    finally:
        backend.show_cursor()
        sys.stdout.write(f"\033[{height + 1};1H\n")
        sys.stdout.flush()

    print("\ndemo_borders complete.")


# ---------------------------------------------------------------------------
# Demo 5 — Custom widget (GridWidget + ClockWidget)
# ---------------------------------------------------------------------------

def demo_widget(width: int = 80, height: int = 24, delay: float = 0.5, clear: bool = True) -> None:
    """Shows two custom widget types: GridWidget and ClockWidget (animated)."""
    print("=== Demo: widget ===")
    print("GridWidget fills its area with a pattern; ClockWidget shows a ticking clock.\n")

    backend, comp = _build_ansi(width, height)
    wm = WindowManager()

    grid = GridWidget()
    grid.layout(0, 0, 36, 10)
    wm.create_window(x=1, y=2, width=38, height=12, title=" Grid ", content=grid)

    clock = ClockWidget()
    clock.layout(0, 0, 20, 3)
    wm.create_window(x=42, y=2, width=22, height=5, title=" Clock ", content=clock)

    backend.hide_cursor()
    try:
        if clear:
            _clear()
        for _ in range(6):
            clock.tick()
            comp.render_frame(wm.list_windows_in_z_order())
            _pause(delay)
    finally:
        backend.show_cursor()
        sys.stdout.write(f"\033[{height + 1};1H\n")
        sys.stdout.flush()

    print("\ndemo_widget complete.")


# ---------------------------------------------------------------------------
# Demo 6 — StringCaptureBackend (headless / test mode)
# ---------------------------------------------------------------------------

def demo_capture(width: int = 60, height: int = 10, delay: float = 0.0, clear: bool = False) -> None:
    """Renders a frame to StringCaptureBackend and prints the captured text grid.

    This pattern lets you write unit tests for compositor output without
    requiring a real terminal.
    """
    _safe_print("=== Demo: capture ===")
    _safe_print("Renders to StringCaptureBackend (no ANSI escape sequences).\n")

    backend = StringCaptureBackend(width, height)
    comp = Compositor(backend, width=width, height=height)
    wm = WindowManager()

    content = TextWidget([
        "Captured output — no ANSI codes,",
        "no terminal required.",
        "Perfect for automated tests.",
    ])
    content.layout(0, 0, width - 4, height - 4)
    wm.create_window(
        x=1, y=1, width=width - 2, height=height - 2,
        title=" Headless Frame ",
        border_style="double",
        content=content,
    )

    comp.render_frame(wm.list_windows_in_z_order())
    backend.flush()

    captured = backend.render_text()
    _safe_print("--- captured frame ---")
    _safe_print(captured)
    _safe_print("----------------------")
    _safe_print("\ndemo_capture complete.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

_DEMOS = {
    "basic":        demo_basic,
    "zorder":       demo_zorder,
    "move_resize":  demo_move_resize,
    "borders":      demo_borders,
    "widget":       demo_widget,
    "capture":      demo_capture,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="tUilKit compositor demonstration suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--demo",
        choices=list(_DEMOS) + ["all"],
        default="all",
        help="Which demo to run (default: all)",
    )
    parser.add_argument("--delay", type=float, default=0.5, metavar="SECS",
                        help="Pause between frames (default 0.5)")
    parser.add_argument("--width", type=int, default=80, help="Terminal width (default 80)")
    parser.add_argument("--height", type=int, default=24, help="Terminal height (default 24)")
    parser.add_argument("--no-clear", dest="clear", action="store_false", default=True,
                        help="Do not clear screen between demos")
    args = parser.parse_args()

    if args.demo == "all":
        for name, fn in _DEMOS.items():
            print()
            try:
                fn(width=args.width, height=args.height, delay=args.delay, clear=args.clear)
            except Exception as exc:
                print(f"[{name}] ERROR: {exc}")
    else:
        fn = _DEMOS[args.demo]
        fn(width=args.width, height=args.height, delay=args.delay, clear=args.clear)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
