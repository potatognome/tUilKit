
import os
import sys
import json
from pathlib import Path

# Load absolute paths from test_paths.json
paths_json = os.path.join(os.path.dirname(__file__), "test_paths.json")
with open(paths_json, "r") as f:
    paths = json.load(f)
tUilKit_src_folder = paths["tUilKit_src_folder"]
config_folder = paths["config_folder"]

# Ensure tUilKit src is in sys.path for absolute imports
if tUilKit_src_folder not in sys.path:
    sys.path.insert(0, tUilKit_src_folder)

from tUilKit.utils.fs import normalize_path, detect_os, colourize_path
from tUilKit.utils.output import ColourManager
from tUilKit.utils.config import ConfigLoader


def _colour_manager():
    cfg_loader = ConfigLoader()
    colours_path = SRC_DIR / "tUilKit" / "config" / "COLOURS.json"
    colour_cfg = cfg_loader.load_config(str(colours_path))
    return ColourManager(colour_cfg)


def test_normalize_path_posix():
    raw = r"C:\\Temp\\foo\\bar.txt"
    norm = normalize_path(raw, style="posix")
    assert norm == "C:/Temp/foo/bar.txt"


def test_normalize_path_windows():
    raw = r"C:/Temp/foo/bar.txt"
    norm = normalize_path(raw, style="windows")
    assert norm == "C:\\Temp\\foo\\bar.txt"


def test_colourize_path_auto_strips_to_original():
    cm = _colour_manager()
    raw = os.path.join("tmp", "folder", "file.txt")
    coloured = colourize_path(raw, cm, style="auto")
    stripped = cm.strip_ansi(coloured)
    # colour_path preserves separators for current platform
    assert stripped == raw


def test_detect_os_returns_known_value():
    assert detect_os() in {"Windows", "Linux", "Darwin"}
