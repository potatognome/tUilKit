# tUilKit Compositor — Terminal Windowing System

**Package:** `tUilKit.output`  
**Introduced in:** v0.6.0

This document describes the terminal windowing, compositing, and rendering
subsystem added in v0.6.0.  It covers architecture, quick-start usage, and
the public API for every subpackage.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                       Your Application                    │
│                                                          │
│  wm = WindowManager()          # create / manage windows │
│  wid = wm.create_window(…)     # add a widget as content │
│  comp.render_frame(wm.…)       # composite + flush       │
└───────────────────────┬──────────────────────────────────┘
                        │
           ┌────────────▼────────────┐
           │       Compositor        │  double-buffered frame assembly
           │  back buffer            │
           │  front buffer           │
           └─────────┬──────┬────────┘
                     │      │
         z-order sort│      │DrawContext (clipped)
                     │      │
           ┌─────────▼──────▼────────┐
           │    Window (per window)  │
           │  border drawing         │
           │  Widget.render(ctx)     │
           └────────────┬────────────┘
                        │ changed cells only
           ┌────────────▼────────────┐
           │   RenderBackendInterface│
           │   AnsiRenderBackend     │  ANSI escape sequences
           └─────────────────────────┘
```

### Double Buffering

The compositor maintains a **back buffer** and a **front buffer**, both sized
`width × height` cells.  On every `render_frame()` call:

1. The back buffer is cleared to blank cells.
2. Every window is painted into the back buffer in ascending z-order.
3. The back and front buffers are compared cell by cell.
4. Only *changed* cells are forwarded to the backend — minimising terminal I/O.
5. The back buffer is promoted to the front buffer.

---

## Quick Start

```python
import sys
from tUilKit.output.backend.ansi_backend import AnsiRenderBackend
from tUilKit.output.compositor.compositor import Compositor
from tUilKit.output.window.window_manager import WindowManager
from tUilKit.output.widgets.widget import TextWidget
from tUilKit.output.backend.backend import Style

# 1. Create the rendering backend (writes to stdout by default).
backend = AnsiRenderBackend()

# 2. Create the compositor (sized to your terminal).
comp = Compositor(backend, width=120, height=40)

# 3. Create a window manager and open a window.
wm = WindowManager()
wid = wm.create_window(
    x=5, y=5,
    width=30, height=10,
    title="Hello",
    border_style="double",
    content=TextWidget("Welcome to tUilKit!", Style()),
)

# 4. Render a frame.
backend.hide_cursor()
comp.render_frame(wm.list_windows_in_z_order())
backend.show_cursor()
```

---

## Subpackage Reference

### `tUilKit.output.backend`

| Symbol | Description |
|---|---|
| `Style` | Dataclass holding fg colour, bg colour, bold, dim, underline, reverse. |
| `RenderBackendInterface` | Abstract base class for all rendering backends. |
| `AnsiRenderBackend` | Default ANSI backend — absolute cursor positioning, diff-flush. |

**`AnsiRenderBackend` methods:**

| Method | Description |
|---|---|
| `draw_rune(x, y, ch, style)` | Stage a single character. |
| `draw_string(x, y, s, style)` | Stage a string. |
| `flush()` | Write changed cells and reset the back buffer. |
| `clear_region(x, y, w, h)` | Fill a region with blank cells. |
| `move_cursor(x, y)` | Emit a cursor-position escape to the stream. |
| `hide_cursor()` | Suppress hardware cursor flicker during redraws. |
| `show_cursor()` | Restore the hardware cursor. |

---

### `tUilKit.output.zorder`

| Symbol | Description |
|---|---|
| `ZOrderManager` | Maintains a list of windows sorted by `z_index`. |

**`ZOrderManager` methods:**

| Method | Description |
|---|---|
| `add(window)` | Register a window. |
| `remove(window_id)` | Deregister a window by id. |
| `raise_window(window_id)` | Move window above all others. |
| `lower_window(window_id)` | Move window below all others. |
| `set_z_index(window_id, z)` | Assign an explicit z-index. |
| `list_in_z_order()` | Return windows sorted bottom-to-top. |
| `get(window_id)` | Look up a window by id. |

---

### `tUilKit.output.window`

#### `Window` dataclass

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | UUID auto-generated on creation. |
| `x`, `y` | `int` | Top-left position in screen coordinates. |
| `width`, `height` | `int` | Dimensions in columns / rows. |
| `z_index` | `int` | Paint order — higher draws on top. |
| `content` | `Widget \| None` | Root widget rendered inside this window. |
| `border_style` | `str` | `"single"` \| `"double"` \| `"heavy"` \| `"rounded"` \| `"none"`. |
| `focusable` | `bool` | Whether this window accepts keyboard focus. |
| `title` | `str` | Text embedded in the top border. |
| `focused` | `bool` (read-only) | Currently holds keyboard focus. |

#### `WindowManager`

| Method | Description |
|---|---|
| `create_window(…)` | Create a new window and return its UUID. |
| `close_window(id)` | Destroy a window. |
| `move_window(id, x, y)` | Reposition a window. |
| `resize_window(id, w, h)` | Change a window's dimensions. |
| `focus_window(id)` | Grant keyboard focus (also raises to top). |
| `raise_window(id)` | Raise above all other windows. |
| `lower_window(id)` | Lower below all other windows. |
| `set_z_index(id, z)` | Assign a specific z-index. |
| `list_windows_in_z_order()` | Return all windows sorted bottom-to-top. |
| `get_window(id)` | Retrieve a `Window` by UUID. |
| `focused_id` | UUID of the focused window, or `None`. |
| `window_count` | Number of live windows. |

---

### `tUilKit.output.draw`

#### `Rect`

Simple dataclass: `x`, `y`, `width`, `height`.  
Helper methods: `contains(sx, sy)`, `intersects(other)`.

#### `DrawContext`

Passed to every `Widget.render()` call.  All coordinates are **window-local**
(origin at the widget's assigned position).

| Method | Description |
|---|---|
| `draw_rune(x, y, ch, style)` | Draw one character, clipped. |
| `draw_string(x, y, s, style)` | Draw a string, each character clipped. |
| `sub_context(lx, ly, w, h)` | Create a child context for a sub-region. |
| `clip` | The clip `Rect` in screen coordinates (read-only). |
| `width`, `height` | Dimensions of the clip rectangle. |

#### Border utilities

```python
from tUilKit.output.draw.border import draw_border, draw_titled_border

draw_border(ctx, rect, style="single", border_style=None)
draw_titled_border(ctx, rect, style="double", title="My Window", border_style=None)
```

Supported *style* values: `"single"`, `"double"`, `"heavy"`, `"rounded"`.

---

### `tUilKit.output.widgets`

#### `Widget` (abstract base class)

Subclass and implement `render(ctx)`.

| Method | Override? | Description |
|---|---|---|
| `render(ctx)` | **Required** | Paint the widget into `ctx`. |
| `measure()` | Optional | Return preferred `(width, height)`. |
| `layout(x, y, w, h)` | Optional | Called by layout engine before render. |

#### Built-in widgets

| Widget | Description |
|---|---|
| `TextWidget(text, style)` | Renders a single line of text. |
| `FilledWidget(ch, style)` | Floods the entire area with a fill character. |

---

### `tUilKit.output.compositor`

#### `Compositor(backend, width, height)`

| Method | Description |
|---|---|
| `render_frame(windows)` | Full render cycle: clear → composite → diff-flush. |
| `resize(width, height)` | Resize both buffers; next frame repaints fully. |
| `draw_rune(x, y, ch, style)` | Write directly to the back buffer (used by `DrawContext`). |
| `draw_string(x, y, s, style)` | Write a string to the back buffer. |

---

## Writing a Custom Widget

```python
from tUilKit.output.widgets.widget import Widget
from tUilKit.output.backend.backend import Style

class ClockWidget(Widget):
    def __init__(self):
        super().__init__()

    def measure(self):
        return (8, 1)  # "HH:MM:SS"

    def render(self, ctx):
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        ctx.draw_string(0, 0, now, Style())
```

Attach it to a window:

```python
wid = wm.create_window(
    x=2, y=2, width=12, height=3,
    content=ClockWidget(),
    border_style="rounded",
    title="Clock",
)
```

---

## Writing a Custom Backend

Subclass `RenderBackendInterface` and implement all five abstract methods:

```python
from tUilKit.output.backend.backend import RenderBackendInterface, Style

class NullBackend(RenderBackendInterface):
    def move_cursor(self, x, y): pass
    def draw_rune(self, x, y, ch, style): pass
    def draw_string(self, x, y, s, style): pass
    def flush(self): pass
    def clear_region(self, x, y, w, h): pass
```

Pass it to `Compositor` in place of `AnsiRenderBackend`.

---

## Running the Tests

```bash
python -m pytest tests/output/ -v
```

All 80 tests are in `tests/output/` and run without any external dependencies.
