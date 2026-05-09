"""ANSI capability helpers for terminal modules."""

import os
import platform
import sys


def is_ansi_supported():
    """Return whether ANSI escape codes should be emitted."""
    force = os.environ.get("TUILKIT_FORCE_ANSI")
    if force is not None:
        return force.lower() in ("1", "true", "yes", "on")

    if not sys.stdout.isatty():
        return False

    if sys.platform == "win32":
        version_parts = platform.version().split(".")
        try:
            return int(version_parts[0]) >= 10
        except (TypeError, ValueError, IndexError):
            return False

    return True
