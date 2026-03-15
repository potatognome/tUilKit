
"""
Workspace-policy compliant test for tUilKit ConfigLoader: argparse, log folder resolution, rainbow row, border, colour logging, no plain prints.
"""
import sys
import os
import argparse
import time
import shutil
import tempfile
from datetime import datetime
from tUilKit.utils.fs import normalize_path, colourize_path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Dev', 'tUilKit', 'src')))
try:
    from tUilKit.utils.config import ConfigLoader
except ModuleNotFoundError:
    # Fallback for local test runs
    from utils.config import ConfigLoader
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem

# --- 1. Command Line Args ---
parser = argparse.ArgumentParser(description="tUilKit ConfigLoader test suite")
parser.add_argument('--clean', choices=["local", "all", "master", "tests"], help="Clean log files: local, all, master, tests")
args = parser.parse_args()

# --- 2. Imports and Initialization ---
config_loader = ConfigLoader()
colour_config = config_loader.load_colour_config()
colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
file_system = FileSystem(logger)

# --- 2.5. Test Log Folder Resolution ---
TESTS_OPTIONS = config_loader.global_config.get("TESTS_OPTIONS", {})
TEST_LOGS_FOLDER = TESTS_OPTIONS.get("TEST_LOGS_FOLDER", ".testlogs")
TEST_LOG_FILE = os.path.join(TEST_LOGS_FOLDER, "test_config.log")
if not os.path.exists(TEST_LOGS_FOLDER):
    os.makedirs(TEST_LOGS_FOLDER, exist_ok=True)

# --- Clean log files if requested ---
if args.clean:
    for fname in os.listdir(TEST_LOGS_FOLDER):
        if fname.endswith('.log'):
            try:
                base, ext = os.path.splitext(fname)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_fname = f"{base}_{timestamp}.bak"
                shutil.move(os.path.join(TEST_LOGS_FOLDER, fname), os.path.join(TEST_LOGS_FOLDER, backup_fname))
                logger.colour_log("!info", f"Backed up {fname} to {backup_fname}", log_files=TEST_LOG_FILE)
            except Exception as e:
                logger.log_exception(f"Could not backup {fname}", e, log_files=[TEST_LOG_FILE])

# --- Rainbow row and border for test start ---
logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=[TEST_LOG_FILE], log_to="file")
border_patterns = config_loader.load_border_patterns_config()
bold_pattern = border_patterns.get("BOLD", {
    "TOP": ["━"],
    "BOTTOM": ["━"],
    "LEFT": ["┃"],
    "RIGHT": ["┃"]
})
logger.apply_border("ConfigLoader Test Suite", bold_pattern, log_files=[TEST_LOG_FILE], border_colour="!proc", log_to="file")
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Dev', 'tUilKit'))
cwd = os.getcwd()
logger.colour_log("!debug", "Project root:", "!path", colourize_path(project_root, colour_manager), log_files=TEST_LOG_FILE)
logger.colour_log("!debug", "Current working directory:", "!path", colourize_path(cwd, colour_manager), log_files=TEST_LOG_FILE)
logger.colour_log("!info", "Test log folder:", "!path", colourize_path(TEST_LOGS_FOLDER, colour_manager), log_files=TEST_LOG_FILE)
logger.colour_log("!info", "COLOURS config path:", "!path", colourize_path(config_loader.get_config_file_path('COLOURS'), colour_manager), log_files=TEST_LOG_FILE)
logger.colour_log("!info", "BORDER_PATTERNS config path:", "!path", colourize_path(config_loader.get_config_file_path('BORDER_PATTERNS'), colour_manager), log_files=TEST_LOG_FILE)
time.sleep(0.5)

# --- 3. Test variables ---
temp_dir = tempfile.mkdtemp()

# --- 4. Test functions ---
def test_config_loader_init(function_log=None):
    """Test ConfigLoader initialization and global_config loading from tUilKit_CONFIG.json."""
    try:
        # Test initialization
        loader = ConfigLoader()
        assert loader.global_config is not None, "global_config should not be None"
        assert "PROJECT_NAME" in loader.global_config, "PROJECT_NAME should be in global_config"
        assert "VERSION" in loader.global_config, "VERSION should be in global_config"
        assert loader.global_config["VERSION"] == "0.7.0", f"VERSION should be 0.7.0, got {loader.global_config['VERSION']}"
        
        logger.colour_log("!proc", "ConfigLoader initialization tests passed.", log_files=test_log_file)
        if function_log:
            logger.colour_log("!proc", "ConfigLoader initialization tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_config_loader_init failed", e, log_files=[test_log_file, function_log] if function_log else [test_log_file])
        raise

def test_get_json_path(function_log=None):
    """Test get_json_path method."""
    try:
        loader = ConfigLoader()
        
        # Test getting GLOBAL_CONFIG.json path
        global_config_path = loader.get_json_path('GLOBAL_CONFIG.json')
        assert os.path.exists(global_config_path), f"GLOBAL_CONFIG.json path should exist: {global_config_path}"
        assert "GLOBAL_CONFIG.json" in global_config_path, "Path should contain GLOBAL_CONFIG.json"
        
        # Test with non-existent file (should still return a path)
        test_path = loader.get_json_path('NONEXISTENT.json')
        assert "NONEXISTENT.json" in test_path, "Path should contain NONEXISTENT.json"
        
        logger.colour_log("!proc", "get_json_path tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "get_json_path tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_get_json_path failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_load_config(function_log=None):
    """Test load_config method."""
    try:
        loader = ConfigLoader()
        
        # Load GLOBAL_CONFIG.json
        global_config_path = loader.get_json_path('GLOBAL_CONFIG.json')
        loaded_config = loader.load_config(global_config_path)
        
        assert isinstance(loaded_config, dict), "load_config should return a dict"
        assert "VERSION" in loaded_config, "Loaded config should contain VERSION"
        assert "LOG_FILES" in loaded_config, "Loaded config should contain LOG_FILES"
        
        logger.colour_log("!proc", "load_config tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "load_config tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_load_config failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_load_colour_config(function_log=None):
    """Test load_colour_config method."""
    try:
        loader = ConfigLoader()
        
        # Load colour config
        colour_config = loader.load_colour_config()
        
        assert isinstance(colour_config, dict), "load_colour_config should return a dict"
        assert "COLOUR_KEY" in colour_config, "Colour config should contain COLOUR_KEY"
        assert isinstance(colour_config["COLOUR_KEY"], dict), "COLOUR_KEY should be a dict"
        assert len(colour_config["COLOUR_KEY"]) > 0, "COLOUR_KEY should not be empty"
        
        logger.colour_log("!proc", "load_colour_config tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "load_colour_config tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_load_colour_config failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_load_border_patterns_config(function_log=None):
    """Test load_border_patterns_config method."""
    try:
        loader = ConfigLoader()
        
        # Load border patterns config
        border_config = loader.load_border_patterns_config()
        
        assert isinstance(border_config, dict), "load_border_patterns_config should return a dict"
        assert len(border_config) > 0, "Border patterns should not be empty"
        # Check for at least one standard border pattern
        assert any(key in border_config for key in ["SINGLE_LINE", "DOUBLE_LINE", "BOLD"]), "Should contain standard border patterns"
        
        logger.colour_log("!proc", "load_border_patterns_config tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "load_border_patterns_config tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_load_border_patterns_config failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_get_config_file_path(function_log=None):
    """Test get_config_file_path method."""
    try:
        loader = ConfigLoader()
        
        # Test getting COLOURS config path
        colours_path = loader.get_config_file_path("COLOURS")
        assert "COLOURS.json" in colours_path, "Path should reference COLOURS.json"
        
        # Test getting BORDER_PATTERNS config path
        patterns_path = loader.get_config_file_path("BORDER_PATTERNS")
        assert "BORDER_PATTERNS.json" in patterns_path, "Path should reference BORDER_PATTERNS.json"
        
        # Test with invalid key (should raise ValueError)
        try:
            loader.get_config_file_path("NONEXISTENT_KEY")
            assert False, "Should raise ValueError for non-existent key"
        except ValueError as e:
            assert "not found" in str(e), "Error message should indicate key not found"
        
        logger.colour_log("!proc", "get_config_file_path tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "get_config_file_path tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_get_config_file_path failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_get_log_file_path(function_log=None):
    """Test get_log_file_path method."""
    try:
        loader = ConfigLoader()
        log_path = loader.get_log_file_path("SESSION")
        norm_path = normalize_path(log_path)
        logger.colour_log("!proc", "Normalized log file path:", "!path", colourize_path(norm_path, colour_manager), log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "Normalized log file path:", "!path", colourize_path(norm_path, colour_manager), log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_get_log_file_path failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise
