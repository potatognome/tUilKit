"""
tUilKit ConfigLoader Comprehensive Test Suite
Each test produces its own log file in the testlogs folder.
All log messages use colour logging and borders.
"""


import os
import sys
import json
import getpass
import datetime
from tUilKit.utils.config import ConfigLoader
from tUilKit.utils.output import Logger, ColourManager

# --- Display test header and environment info ---
os.system("cls")
starttime = datetime.datetime.now()
username = getpass.getuser()
current_path = os.getcwd()
print("=== Starting tUilKit ConfigLoader Test ===")
print(f"Date/Time: {starttime.strftime('%Y-%m-%d %H:%M:%S')}")
print("User:", username)
print("Working Directory:", current_path)
print("Command:", " ".join(sys.argv))
print("=== Running tUilKit ConfigLoader Test ===")


# --- Utility function for per-test log file ---
def get_test_log_file(test_name, logs_folder):
    return os.path.join(logs_folder, f"{test_name}.log")

# --- 1. Load and display test_paths.json ---
print("\n=== [TEST 1] Load test_paths.json ===")
paths_json = os.path.join(os.path.dirname(__file__), "test_paths.json")
with open(paths_json, "r", encoding="utf-8") as f:
    paths = json.load(f)
print("test_paths.json contents:", json.dumps(paths, indent=2))
test_logs_folder = paths.get("test_logs_folder", os.path.join(os.getcwd(), ".testlogs"))
os.makedirs(test_logs_folder, exist_ok=True)
test1_log = get_test_log_file("test1_load_paths", test_logs_folder)
with open(test1_log, "a", encoding="utf-8") as logf:
    logf.write("[TEST 1] Loaded test_paths.json\n")

# --- Ensure tUilKit src is in sys.path for absolute imports ---
tUilKit_src_folder = paths.get("tUilKit_src_folder")
if tUilKit_src_folder and tUilKit_src_folder not in sys.path:
    sys.path.insert(0, tUilKit_src_folder)



# --- 2. Create ConfigLoader instance in verbose mode ---
print("\n=== [TEST 2] Create ConfigLoader (verbose) ===")
loader = ConfigLoader(verbose=True)
test2_log = get_test_log_file("test2_configloader_verbose", test_logs_folder)
with open(test2_log, "a", encoding="utf-8") as logf:
    logf.write("[TEST 2] Created ConfigLoader in verbose mode\n")


# --- 3. Use test_paths.json and ConfigLoader to resolve test folder and config file (verbose) ---
print("\n=== [TEST 3] Resolve test folder and config file (verbose) ===")
tests_folder = paths.get("tests_folder")
tests_config_folder = paths.get("tests_config_folder")
config_file_path = os.path.join(tests_config_folder, "tUilKit_CONFIG.json")
# print(f"tests_folder: {tests_folder}")
# print(f"tests_config_folder: {tests_config_folder}")
# print(f"config_file_path: {config_file_path}")

print("[TEST 3 VERBOSE] Calling ConfigPathResolver.resolve_config_path for tUilKit_CONFIG.json...")
resolved_config_path = loader.path_resolver.resolve_config_path("tUilKit_CONFIG.json", verbose=True)
print(f"[TEST 3 VERBOSE] Resolved config path: {resolved_config_path}")
print(f"[TEST 3 VERBOSE] Opening config file: {resolved_config_path}")
try:
    with open(resolved_config_path, "r", encoding="utf-8") as f:
        config_contents = f.read()
    # print(f"[TEST 3 VERBOSE] Config file contents:\n{config_contents}")
except Exception as e:
    print(f"[TEST 3 VERBOSE] Error reading config file: {e}")
test3_log = get_test_log_file("test3_resolve_paths", test_logs_folder)
with open(test3_log, "a", encoding="utf-8") as logf:
    logf.write(f"[TEST 3] Resolved test folder: {tests_folder}\n")
    logf.write(f"[TEST 3] Resolved config file path: {config_file_path}\n")
    logf.write(f"[TEST 3 VERBOSE] Resolved config path: {resolved_config_path}\n")
    logf.write(f"[TEST 3 VERBOSE] Opening config file: {resolved_config_path}\n")
    logf.write(f"[TEST 3 VERBOSE] Config file contents:\n{config_contents}\n")

# --- Log colour key information for date/time settings if available ---
colour_keys = None
try:
    config_json = json.loads(config_contents)
    shared_cfg = config_json.get("SHARED_CONFIG", {})
    shared_files = shared_cfg.get("SHARED_CONFIG_FILES", {})
    date_colour_key = shared_files.get("DATE_COLOUR_KEY")
    time_colour_key = shared_files.get("TIME_COLOUR_KEY")
    datetime_colour_key = shared_files.get("DATETIME_COLOUR_KEY")
    colour_keys = {
        "DATE_COLOUR_KEY": date_colour_key,
        "TIME_COLOUR_KEY": time_colour_key,
        "DATETIME_COLOUR_KEY": datetime_colour_key
    }
    print(f"[TEST 3 VERBOSE] Colour keys for date/time: {colour_keys}")
    with open(test3_log, "a", encoding="utf-8") as logf:
        logf.write(f"[TEST 3 VERBOSE] Colour keys for date/time: {colour_keys}\n")
except Exception as e:
    print(f"[TEST 3 VERBOSE] Error extracting colour keys: {e}")

# --- 4. Read tUilKit_CONFIG.json and determine root_mode ---
print("\n=== [TEST 4] Read tUilKit_CONFIG.json and determine root_mode ===")
with open(config_file_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)
root_modes = config_data.get("ROOT_MODES", {})
paths_cfg = config_data.get("PATHS", {})
root_mode = root_modes.get("CONFIG", "workspace")
print(f"CONFIG FILE ROOT_MODE: {root_mode}")
test4_log = get_test_log_file("test4_root_mode", test_logs_folder)
with open(test4_log, "a", encoding="utf-8") as logf:
    logf.write(f"[TEST 4] CONFIG FILE ROOT_MODE: {root_mode}\n")

# --- 5. Read shared COLOURS config, set up Logger/ColourManager, log online message ---
print("\n=== [TEST 5] Read COLOURS config and log online message ===")
shared_cfg = config_data.get("SHARED_CONFIG", {})
shared_enabled = shared_cfg.get("ENABLED", False)
shared_path = shared_cfg.get("PATH", "GLOBAL_SHARED.d/")
shared_files = shared_cfg.get("SHARED_CONFIG_FILES", {})
colours_file = shared_files.get("COLOURS")
colours_path = os.path.join(tests_config_folder, shared_path, colours_file) if colours_file else None
colour_config = None
if colours_path and os.path.exists(colours_path):
    with open(colours_path, "r", encoding="utf-8") as f:
        colour_config = json.load(f)
    print(f"COLOURS config loaded from: {colours_path}")
else:
    print("COLOURS config file not found.")
colour_manager = ColourManager(colour_config) if colour_config else None
logger = Logger(colour_manager) if colour_manager else None
test5_log = get_test_log_file("test5_colours_online", test_logs_folder)
if logger:
    logger.colour_log("!info", "Colours and Colour_key are online", log_files=test5_log)
else:
    with open(test5_log, "a", encoding="utf-8") as logf:
        logf.write("[TEST 5] Colours config not found or ColourManager not initialized\n")

# --- 6. Read shared BORDER_PATTERNS config and log bordered message ---
print("\n=== [TEST 6] Read BORDER_PATTERNS config and log bordered message ===")
border_file = shared_files.get("BORDER_PATTERNS")
border_path = os.path.join(tests_config_folder, shared_path, border_file) if border_file else None
border_patterns = None
if border_path and os.path.exists(border_path):
    with open(border_path, "r", encoding="utf-8") as f:
        border_patterns = json.load(f)
    print(f"BORDER_PATTERNS config loaded from: {border_path}")
else:
    print("BORDER_PATTERNS config file not found.")
test6_log = get_test_log_file("test6_border_patterns_online", test_logs_folder)
if logger and border_patterns:
    bold_pattern = border_patterns.get("BOLD", {
        "TOP": ["━"], "BOTTOM": ["━"], "LEFT": ["┃"], "RIGHT": ["┃"]
    })
    logger.apply_border("Border patterns are online", bold_pattern, log_files=test6_log, border_colour="!proc")
else:
    with open(test6_log, "a", encoding="utf-8") as logf:
        logf.write("[TEST 6] Border patterns config not found or logger not initialized\n")

# --- Secondary Tests ---
# Standard colour log and border usage for each

print("\n=== [TEST 7] ConfigLoader (workspace root mode) ===")
test7_log = get_test_log_file("test7_workspace_mode", test_logs_folder)
workspace_config_data = dict(config_data)
workspace_config_data["ROOT_MODES"]["CONFIG"] = "workspace"
# Save modified config for loader to pick up
workspace_config_path = os.path.join(tests_config_folder, "tUilKit_CONFIG_workspace.json")
with open(workspace_config_path, "w", encoding="utf-8") as f:
    json.dump(workspace_config_data, f, indent=2)
# Re-instantiate ConfigLoader with workspace config
workspace_loader = ConfigLoader(verbose=True)
workspace_loader.global_config = workspace_config_data
# Reload colour config and ColourManager for workspace mode
try:
    workspace_colour_config = None
    shared_cfg_ws = workspace_config_data.get("SHARED_CONFIG", {})
    shared_files_ws = shared_cfg_ws.get("SHARED_CONFIG_FILES", {})
    colours_file_ws = shared_files_ws.get("COLOURS")
    colours_path_ws = os.path.join(tests_config_folder, shared_cfg_ws.get("PATH", "GLOBAL_SHARED.d/"), colours_file_ws) if colours_file_ws else None
    if colours_path_ws and os.path.exists(colours_path_ws):
        with open(colours_path_ws, "r", encoding="utf-8") as f:
            workspace_colour_config = json.load(f)
        print(f"[TEST 7] COLOURS config loaded from: {colours_path_ws}")
    else:
        print("[TEST 7] COLOURS config file not found.")
    workspace_colour_manager = ColourManager(workspace_colour_config) if workspace_colour_config else None
    workspace_logger = Logger(workspace_colour_manager) if workspace_colour_manager else None
    if workspace_logger:
        workspace_logger.colour_log("!info", "Workspace mode ConfigLoader test", log_files=test7_log)
        if border_patterns:
            bold_pattern = border_patterns.get("BOLD", {
                "TOP": ["━"], "BOTTOM": ["━"], "LEFT": ["┃"], "RIGHT": ["┃"]
            })
            workspace_logger.apply_border("Workspace mode config loaded", bold_pattern, log_files=test7_log, border_colour="!info")
        # Log colour key for workspace mode
        colour_keys_ws = workspace_colour_config.get("COLOUR_KEYS", {}) if workspace_colour_config else {}
        workspace_logger.colour_log("!info", f"Workspace mode colour keys: {colour_keys_ws}", log_files=test7_log)
    else:
        with open(test7_log, "a", encoding="utf-8") as logf:
            logf.write("[TEST 7] Workspace mode: ColourManager or Logger not initialized\n")
except Exception as e:
    print(f"[TEST 7] Error reloading colour config: {e}")
    with open(test7_log, "a", encoding="utf-8") as logf:
        logf.write(f"[TEST 7] Error reloading colour config: {e}\n")

print("\n=== [TEST 8] ConfigLoader (project root mode) ===")
test8_log = get_test_log_file("test8_project_mode", test_logs_folder)
project_config_data = dict(config_data)
project_config_data["ROOT_MODES"]["CONFIG"] = "project"
# Save modified config for loader to pick up
project_config_path = os.path.join(tests_config_folder, "tUilKit_CONFIG_project.json")
with open(project_config_path, "w", encoding="utf-8") as f:
    json.dump(project_config_data, f, indent=2)
# Re-instantiate ConfigLoader with project config
project_loader = ConfigLoader(verbose=True)
project_loader.global_config = project_config_data
# Reload colour config and ColourManager for project mode
try:
    project_colour_config = None
    shared_cfg_pr = project_config_data.get("SHARED_CONFIG", {})
    shared_files_pr = shared_cfg_pr.get("SHARED_CONFIG_FILES", {})
    colours_file_pr = shared_files_pr.get("COLOURS")
    colours_path_pr = os.path.join(tests_config_folder, shared_cfg_pr.get("PATH", "GLOBAL_SHARED.d/"), colours_file_pr) if colours_file_pr else None
    if colours_path_pr and os.path.exists(colours_path_pr):
        with open(colours_path_pr, "r", encoding="utf-8") as f:
            project_colour_config = json.load(f)
        print(f"[TEST 8] COLOURS config loaded from: {colours_path_pr}")
    else:
        print("[TEST 8] COLOURS config file not found.")
    project_colour_manager = ColourManager(project_colour_config) if project_colour_config else None
    project_logger = Logger(project_colour_manager) if project_colour_manager else None
    if project_logger:
        project_logger.colour_log("!info", "Project mode ConfigLoader test", log_files=test8_log)
        if border_patterns:
            bold_pattern = border_patterns.get("BOLD", {
                "TOP": ["━"], "BOTTOM": ["━"], "LEFT": ["┃"], "RIGHT": ["┃"]
            })
            project_logger.apply_border("Project mode config loaded", bold_pattern, log_files=test8_log, border_colour="!info")
        # Log colour key for project mode
        colour_keys_pr = project_colour_config.get("COLOUR_KEYS", {}) if project_colour_config else {}
        project_logger.colour_log("!info", f"Project mode colour keys: {colour_keys_pr}", log_files=test8_log)
    else:
        with open(test8_log, "a", encoding="utf-8") as logf:
            logf.write("[TEST 8] Project mode: ColourManager or Logger not initialized\n")
except Exception as e:
    print(f"[TEST 8] Error reloading colour config: {e}")
    with open(test8_log, "a", encoding="utf-8") as logf:
        logf.write(f"[TEST 8] Error reloading colour config: {e}\n")

print("\n=== All tests completed. See individual log files in testlogs folder. ===")
