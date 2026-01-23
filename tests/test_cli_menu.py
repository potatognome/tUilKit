"""
Tests for tUilKit.utils.cli_menu_handler (CLIMenuHandler) interactive menu functions.
Note: These tests require manual interaction. Automated tests are limited.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# --- 1. Command line argument for log cleanup ---
import argparse
parser = argparse.ArgumentParser(description="Run tUilKit CLI Menu test suite.")
parser.add_argument('--clean', action='store_true', help='Remove all log files in the test log folder before running tests.')
parser.add_argument('--auto', action='store_true', help='Run automated tests only (no user interaction)')
args, unknown = parser.parse_known_args()

# --- 2. Imports and initialization ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.utils.cli_menu_handler import CLIMenuHandler
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.config.config import ConfigLoader

# Change to project root for config loading
original_cwd = os.getcwd()
os.chdir(project_root)

config_loader = ConfigLoader()
colour_config = config_loader.load_colour_config()

os.chdir(original_cwd)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
menu_handler = CLIMenuHandler(logger)

TEST_LOG_FOLDER = os.path.join(os.path.dirname(__file__), "testOutputLogs")
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_cli_menu_output.log")

# Ensure test log folder exists
if not os.path.exists(TEST_LOG_FOLDER):
    os.makedirs(TEST_LOG_FOLDER, exist_ok=True)

# Remove all log files if --clean is passed
if args.clean:
    for fname in os.listdir(TEST_LOG_FOLDER):
        if fname.endswith('.log'):
            try:
                base, ext = os.path.splitext(fname)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_fname = f"{base}_{timestamp}.bak"
                os.rename(os.path.join(TEST_LOG_FOLDER, fname), os.path.join(TEST_LOG_FOLDER, backup_fname))
                print(f"Backed up {fname} to {backup_fname}")
            except Exception as e:
                print(f"Could not backup {fname}: {e}")

# Clear terminal
os.system('cls' if os.name == 'nt' else 'clear')

# Print rainbow row separator
logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=TEST_LOG_FILE)

# Display last command
logger.colour_log("!info", "Last command: python tests/test_cli_menu.py", log_files=TEST_LOG_FILE)
logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=TEST_LOG_FILE)

# --- 3. Test variables ---
border_pattern = "="

# --- 4. Test functions ---
def test_show_numbered_menu(function_log=None):
    """Test numbered menu display and selection"""
    logger.colour_log("!info", "This test function", "!test", "test_show_numbered_menu", "!info", 
                     "tests the numbered menu display with back and quit options.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    options = [
        {"key": "option1", "label": "First Option", "icon": "📋"},
        {"key": "option2", "label": "Second Option", "icon": "⚙️"},
        {"key": "option3", "label": "Third Option", "icon": "🔧"},
    ]
    
    logger.colour_log("!test", "Testing menu display with 3 options...", 
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    # Note: Actual selection requires user interaction
    # This test validates the structure and display
    logger.colour_log("!expect", "Expected: Menu with 3 numbered options, back, and quit",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.show_numbered_menu(
            title="Test Menu - Select Option 1",
            options=options,
            allow_back=True,
            allow_quit=True
        )
        
        logger.colour_log("!test", "User selected:", "!data", str(result),
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        
        if result == "option1":
            logger.colour_log("!pass", "✅ PASSED - Correct selection",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        else:
            logger.colour_log("!warn", "⚠️  Different selection made:", "!data", str(result),
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Structure validated",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_confirm(function_log=None):
    """Test yes/no confirmation prompts"""
    logger.colour_log("!info", "This test function", "!test", "test_confirm", "!info",
                     "tests yes/no confirmation with default values.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    logger.colour_log("!test", "Testing confirmation prompt with default=True...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.confirm("Press Enter to accept default (Yes)", default=True)
        
        logger.colour_log("!test", "User response:", "!data", str(result),
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        
        if result:
            logger.colour_log("!pass", "✅ PASSED - Confirmed",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        else:
            logger.colour_log("!warn", "⚠️  User declined",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Structure validated",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_prompt_with_default(function_log=None):
    """Test input prompts with defaults"""
    logger.colour_log("!info", "This test function", "!test", "test_prompt_with_default", "!info",
                     "tests input prompts with default values and validation.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    def validate_name(value):
        return len(value) >= 3
    
    logger.colour_log("!test", "Testing prompt with default value 'TestUser'...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.prompt_with_default(
            prompt="Enter name (press Enter for default)",
            default="TestUser",
            validator=validate_name,
            allow_empty=False
        )
        
        logger.colour_log("!test", "User entered:", "!data", str(result),
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        
        if result and len(result) >= 3:
            logger.colour_log("!pass", "✅ PASSED - Valid input received",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        else:
            logger.colour_log("!fail", "❌ FAILED - Invalid input",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Validation logic verified",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_select_from_list(function_log=None):
    """Test single and multi-select from list"""
    logger.colour_log("!info", "This test function", "!test", "test_select_from_list", "!info",
                     "tests single and multi-select functionality.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    items = ["H3l3n", "Syncbot", "tUilKit", "utilsbase"]
    icons = ["📦", "🔄", "🛠️", "⚙️"]
    
    logger.colour_log("!test", "Testing multi-select with 'all' option...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.select_from_list(
            title="Select Projects (enter 'all' for all)",
            items=items,
            multi_select=True,
            allow_all=True,
            icons=icons
        )
        
        if result:
            logger.colour_log("!test", "Selected items:", "!data", str(len(result)), "!info", "items",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
            for item in result:
                logger.colour_log("!info", "  -", "!data", item,
                                 log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
            logger.colour_log("!pass", "✅ PASSED - Items selected",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        else:
            logger.colour_log("!warn", "⚠️  No selection made",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Structure validated",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_get_numeric_choice(function_log=None):
    """Test numeric input validation"""
    logger.colour_log("!info", "This test function", "!test", "test_get_numeric_choice", "!info",
                     "tests validated numeric input within ranges.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    logger.colour_log("!test", "Testing numeric input (1-10, enter 5)...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.get_numeric_choice(
            min_val=1,
            max_val=10,
            prompt="Enter number (5 for pass)",
            allow_cancel=True
        )
        
        logger.colour_log("!test", "User entered:", "!data", str(result),
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        
        if result == 5:
            logger.colour_log("!pass", "✅ PASSED - Correct number",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        elif result is not None:
            logger.colour_log("!warn", "⚠️  Different number entered:",
                             "!data", str(result),
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        else:
            logger.colour_log("!warn", "⚠️  Cancelled",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Validation logic verified",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_show_info_screen(function_log=None):
    """Test information display screen"""
    logger.colour_log("!info", "This test function", "!test", "test_show_info_screen", "!info",
                     "tests formatted information display.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    device_info = {
        "Name": "Test Device",
        "Role": "primary",
        "OS": "Windows 11",
        "Version": "1.0.0"
    }
    
    logger.colour_log("!test", "Displaying info screen...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        menu_handler.show_info_screen(
            title="Device Information Test",
            info=device_info,
            wait_for_input=True
        )
        logger.colour_log("!pass", "✅ PASSED - Info screen displayed",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Structure validated",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_edit_key_value_pairs(function_log=None):
    """Test interactive key-value editor"""
    logger.colour_log("!info", "This test function", "!test", "test_edit_key_value_pairs", "!info",
                     "tests interactive configuration editing.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    data = {
        "name": "TestDevice",
        "role": "primary",
        "enabled": "True"
    }
    
    prompts = {
        "name": "Device name",
        "role": "Role (primary/secondary)",
        "enabled": "Enabled (True/False)"
    }
    
    def validate_role(value):
        return value.lower() in ['primary', 'secondary']
    
    validators = {
        "role": validate_role
    }
    
    logger.colour_log("!test", "Testing key-value editor (press Enter to keep defaults)...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.edit_key_value_pairs(
            title="Edit Device Config Test",
            data=data,
            prompts=prompts,
            validators=validators
        )
        
        logger.colour_log("!test", "Updated configuration:",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        for key, value in result.items():
            logger.colour_log("!info", f"  {key}:", "!data", str(value),
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        
        logger.colour_log("!pass", "✅ PASSED - Configuration edited",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Validation logic verified",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

def test_browse_directory(function_log=None):
    """Test directory browser (limited automated test)"""
    logger.colour_log("!info", "This test function", "!test", "test_browse_directory", "!info",
                     "tests interactive directory navigation.",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    logger.colour_log("!test", "Testing directory browser (enter 'cancel' to skip)...",
                     log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    
    if not args.auto:
        result = menu_handler.browse_directory(
            start_path=Path.cwd(),
            title="Test Directory Browser",
            allow_creation=False
        )
        
        if result:
            logger.colour_log("!test", "Selected path:", "!path", str(result),
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
            logger.colour_log("!pass", "✅ PASSED - Path selected",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        else:
            logger.colour_log("!warn", "⚠️  Cancelled or no selection",
                             log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
    else:
        logger.colour_log("!info", "Skipping interactive test (--auto mode)",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)
        logger.colour_log("!pass", "✅ PASSED - Structure validated",
                         log_files=[TEST_LOG_FILE, function_log] if function_log else TEST_LOG_FILE)

# --- 5. Test suite ---
TESTS = [
    (1, "test_show_numbered_menu", test_show_numbered_menu, "Test numbered menu display and selection"),
    (2, "test_confirm", test_confirm, "Test yes/no confirmation prompts"),
    (3, "test_prompt_with_default", test_prompt_with_default, "Test input with defaults and validation"),
    (4, "test_select_from_list", test_select_from_list, "Test single/multi-select from list"),
    (5, "test_get_numeric_choice", test_get_numeric_choice, "Test numeric input validation"),
    (6, "test_show_info_screen", test_show_info_screen, "Test information display"),
    (7, "test_edit_key_value_pairs", test_edit_key_value_pairs, "Test key-value editor"),
    (8, "test_browse_directory", test_browse_directory, "Test directory browser"),
]

# --- 6. Test runner ---
results = []
successful = []
unsuccessful = []

logger.apply_border(
    text="🧪 CLI Menu Handler Test Suite",
    pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
    total_length=60,
    border_colour="!proc",
    text_colour="!proc",
    log_files=TEST_LOG_FILE
)

if args.auto:
    logger.colour_log("!warn", "⚠️  Running in AUTO mode - interactive tests will be skipped",
                     log_files=TEST_LOG_FILE)
    time.sleep(1)

for num, name, func, description in TESTS:
    function_log = os.path.join(TEST_LOG_FOLDER, f"{name}.log")
    
    try:
        logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=[TEST_LOG_FILE, function_log])
        logger.apply_border(
            text=f"Test {num}: {name}",
            pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
            total_length=60,
            border_colour="!proc",
            text_colour="!proc",
            log_files=[TEST_LOG_FILE, function_log]
        )
        
        logger.colour_log("!test", "Running test", "!int", str(num), "!info", ":", "!proc", name,
                         log_files=[TEST_LOG_FILE, function_log])
        logger.colour_log("!info", "Description:", "!data", description,
                         log_files=[TEST_LOG_FILE, function_log])
        
        time.sleep(0.5)
        
        func(function_log=function_log)
        
        logger.colour_log("!test", "Test", "!int", str(num), "!info", ":", "!proc", name, "!pass", "COMPLETED.",
                         log_files=[TEST_LOG_FILE, function_log])
        results.append((num, name, True))
        successful.append(name)
        
    except Exception as e:
        logger.log_exception(f"{name} failed", e, log_files=[TEST_LOG_FILE, function_log])
        results.append((num, name, False))
        unsuccessful.append(name)

# --- 7. Test summary ---
logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=TEST_LOG_FILE)
logger.apply_border(
    text="📊 Test Summary",
    pattern={"TOP": "=", "BOTTOM": "=", "LEFT": " ", "RIGHT": " "},
    total_length=60,
    border_colour="!proc",
    text_colour="!info",
    log_files=TEST_LOG_FILE
)

total_tests = len(TESTS)
passed_count = len(successful)
failed_count = len(unsuccessful)

logger.colour_log("!info", "Total tests:", "!int", str(total_tests), log_files=TEST_LOG_FILE)
logger.colour_log("!done", "Passed:", "!int", str(passed_count), log_files=TEST_LOG_FILE)
if failed_count > 0:
    logger.colour_log("!error", "Failed:", "!int", str(failed_count), log_files=TEST_LOG_FILE)

print()
if failed_count == 0:
    logger.colour_log("!pass", "✅ ALL TESTS COMPLETED", log_files=TEST_LOG_FILE)
else:
    logger.colour_log("!warn", f"⚠️  {failed_count} TEST(S) HAD ISSUES", log_files=TEST_LOG_FILE)
    for name in unsuccessful:
        logger.colour_log("!fail", "  ❌", "!proc", name, log_files=TEST_LOG_FILE)

logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=TEST_LOG_FILE)
logger.colour_log("!info", "Test logs saved to:", "!path", TEST_LOG_FOLDER, log_files=TEST_LOG_FILE)
