"""
ZOrderManager — sorted registry of windows by z-index.

Higher z-index values sort later in the list, meaning those windows are
drawn on top of windows with lower z-index values.
"""

from __future__ import annotations
from typing import List, Optional


class ZOrderManager:
    """Manages a z-ordered list of window objects.

    Windows are kept sorted by their ``z_index`` attribute (ascending).
    The *last* window in the sorted list is visually on top.

    The manager does **not** own the windows — it merely holds references.
    Ownership belongs to :class:`~tUilKit.output.window.window_manager.WindowManager`.
    """

    def __init__(self) -> None:
        # Internal list maintained in ascending z_index order.
        self._windows: list = []

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------

    def add(self, window) -> None:
        """Add *window* and re-sort the list."""
        self._windows.append(window)
        self._sort()

    def remove(self, window_id: str) -> None:
        """Remove the window identified by *window_id* (no-op if absent)."""
        self._windows = [w for w in self._windows if w.id != window_id]

    def raise_window(self, window_id: str) -> None:
        """Move *window_id* above all other windows.

        Sets the window's ``z_index`` to ``max(existing) + 1``.
        """
        win = self._find(window_id)
        if win is None:
            return
        max_z = max((w.z_index for w in self._windows), default=0)
        win.z_index = max_z + 1
        self._sort()

    def lower_window(self, window_id: str) -> None:
        """Move *window_id* below all other windows.

        Sets the window's ``z_index`` to ``min(existing) - 1``.
        """
        win = self._find(window_id)
        if win is None:
            return
        min_z = min((w.z_index for w in self._windows), default=0)
        win.z_index = min_z - 1
        self._sort()

    def set_z_index(self, window_id: str, z: int) -> None:
        """Set an explicit z-index for *window_id*."""
        win = self._find(window_id)
        if win is not None:
            win.z_index = z
            self._sort()

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def list_in_z_order(self) -> list:
        """Return a shallow copy of the window list in ascending z-order."""
        return list(self._windows)

    def get(self, window_id: str):
        """Return the window with *window_id*, or ``None``."""
        return self._find(window_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find(self, window_id: str):
        for w in self._windows:
            if w.id == window_id:
                return w
        return None

    def _sort(self) -> None:
        self._windows.sort(key=lambda w: w.z_index)
