"""
Minimal test for tUilKit ConfigLoader: verifies config loading and basic path resolution.
"""

import os
import sys
import json

import getpass
import datetime
username = getpass.getuser()
current_path = os.getcwd()
starttime = datetime.datetime.now()


os.system("cls")
print("=== Starting tUilKit ConfigLoader Minimal Test ===")
print(f"Date/Time: {starttime.strftime('%Y-%m-%d %H:%M:%S')}")
print("User:", username)
print("Working Directory:", current_path)  
print("Command:", " ".join(sys.argv))
print("=== Running tUilKit ConfigLoader Minimal Test ===")

# Load paths and config file from test_paths.json
paths_json = os.path.join(os.path.dirname(__file__), "test_paths.json")
try:
    with open(paths_json, "r") as f:
        paths = json.load(f)
        print(f"\n(1) JSON file found: {paths_json}")
    tUilKit_src_folder = paths["tUilKit_src_folder"]
    tests_config_folder = paths["tests_config_folder"]
    config_file_path = os.path.join(tests_config_folder, "tUilKit_CONFIG.json")
    print(f"tUilKit src: {tUilKit_src_folder}")
    print(f"Tests config: {tests_config_folder}")
    print(f"Config file path: {config_file_path}")
except Exception as e:
    print("\n(1)Error loading test paths:", e)
    sys.exit(1)

# Ensure tUilKit src is in sys.path for absolute imports
if tUilKit_src_folder not in sys.path:
    sys.path.insert(0, tUilKit_src_folder)
    print(f"\n(2) Added tUilKit src {tUilKit_src_folder} to sys.path for imports.")
from tUilKit.utils.config import ConfigLoader

# Load config and resolve root mode
with open(config_file_path, "r") as f:
    config_data = json.load(f)
root_modes = config_data.get("ROOT_MODES", {})
paths_cfg = config_data.get("PATHS", {})
shared_cfg = config_data.get("SHARED_CONFIG", {})

# Determine root mode and absolute root path
root_mode = root_modes.get("CONFIG", "workspace")
if root_mode == "workspace":
    root_path = paths_cfg.get("WORKSPACE_ROOT_PATH")
elif root_mode == "project":
    root_path = paths_cfg.get("PROJECT_ROOT_PATH")
else:
    root_path = os.getcwd()

# Resolve shared config files if enabled
shared_enabled = shared_cfg.get("ENABLED", False)
shared_path = shared_cfg.get("PATH", "GLOBAL_SHARED.d/")
shared_files = shared_cfg.get("SHARED_CONFIG_FILES", {})

def get_shared_config_file(key):
    if shared_enabled and key in shared_files:
        return os.path.join(tests_config_folder, shared_path, shared_files[key])
    return None


print("\nRunning minimal config test...")
print(f"\n(3) Reading TESTS level JSON config file {config_file_path}")
print(f"JSON config contains PATH information... {paths_cfg}")
tuilkit_config_path = config_file_path
print(f"tUilKIt TESTS configuration stored in PATH: {tuilkit_config_path}")
print(f"Creating ConfigLoader to read {tuilkit_config_path}...\n...")

# Instantiate ConfigLoader with verbose mode
loader = ConfigLoader(verbose=True)
print("Done!\n")

# Print loaded global config keys
print("Loaded config keys:", list(loader.global_config.keys()))

# Test basic config path resolution for COLOURS
colours_path = get_shared_config_file("COLOURS")
print("COLOURS config path:", colours_path)
if colours_path and os.path.exists(colours_path):
    with open(colours_path, "r") as f:
        colours_data = json.load(f)
    print("Loaded COLOURS keys:", list(colours_data.keys()))
else:
    print("COLOURS config file not found.")

# Test basic config path resolution using ConfigLoader
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

endtime = datetime.datetime.now()
duration = (endtime - starttime).total_seconds()
print("")
print("=== tUilKit ConfigLoader Minimal Test ===")
print(f"Date/Time: {endtime.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Duration: {duration:.2f} seconds")
print("=== tUilKit Tests Completed ===")
