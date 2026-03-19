"""
Minimal test for tUilKit ConfigLoader: verifies config loading and basic path resolution.
"""

import os
import sys
import json

# Load absolute paths from test_paths.json
paths_json = os.path.join(os.path.dirname(__file__), "test_paths.json")
with open(paths_json, "r") as f:
    paths = json.load(f)
tUilKit_src_folder = paths["tUilKit_src_folder"]
config_folder = paths["config_folder"]

# Ensure tUilKit src is in sys.path for absolute imports
if tUilKit_src_folder not in sys.path:
    sys.path.insert(0, tUilKit_src_folder)
from tUilKit.utils.config import ConfigLoader

print("Running minimal config test...")
print("")
# Instantiate ConfigLoader
loader = ConfigLoader()

# Print loaded global config keys
print("Loaded config keys:", list(loader.global_config.keys()))

# Test basic config path resolution using config_folder
try:
    config_path = loader.get_config_file_path("COLOURS")
    print("COLOURS config path:", config_path)
except Exception as e:
    print("Error resolving COLOURS config path:", e)

# Test loading colour config
try:
    colour_config = loader.load_colour_config()
    print("Loaded COLOUR_KEY count:", len(colour_config.get("COLOUR_KEY", {})))
except Exception as e:
    print("Error loading colour config:", e)
