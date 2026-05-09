#!/usr/bin/env python3
"""
Example: Customizing tUilKit Logging Categories

This example shows different ways to customize logging categories in tUilKit.
Run from the examples/ folder: python customize_categories.py
"""

import sys
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: resolve src path and config from test_paths.json
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve()
_paths_file = HERE.parent / "test_paths.json"
if not _paths_file.exists():
    raise FileNotFoundError(
        "test_paths.json not found. Run 'python TESTS_CONFIG.py' first."
    )
with open(_paths_file, encoding="utf-8") as _f:
    _p = json.load(_f)

PROJECT_ROOT = Path(_p["project_root"])
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _resolve_config_file(p: dict) -> Path:
    for key in ("config_file", "tuilkit_config_file"):
        raw = p.get(key)
        if raw:
            c = Path(raw)
            if c.exists():
                return c
    for folder_key in ("config_folder", "tests_config_folder", "test_config_folder"):
        folder = p.get(folder_key)
        if folder:
            c = Path(folder) / "tUilKit_CONFIG.json"
            if c.exists():
                return c
    return PROJECT_ROOT / "config" / "tUilKit_CONFIG.json"


CONFIG_FILE = _resolve_config_file(_p)

# Pre-seed the factory ConfigLoader so all factory calls resolve correctly.
import tUilKit.factories as _factories
from tUilKit.utils.config import ConfigLoader as _ConfigLoader

_factories.reset_factories()
_factories._config_loader = _ConfigLoader(config_path=str(CONFIG_FILE))

# ---------------------------------------------------------------------------
# Imports (after sys.path is set)
# ---------------------------------------------------------------------------
from tUilKit.utils.output import Logger, ColourManager  # noqa: E402
from tUilKit.utils.fs import FileSystem  # noqa: E402


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _make_logger() -> Logger:
    """Return a fresh Logger seeded from the project config."""
    loader = _ConfigLoader(config_path=str(CONFIG_FILE))
    return Logger(ColourManager(loader.load_colour_config()))

def example_1_modify_global_config():
    """
    Method 1: Modify GLOBAL_CONFIG.json to add custom categories
    This is the easiest method for persistent customization.
    """
    print("=== Method 1: Modify GLOBAL_CONFIG.json ===")

    logger = _make_logger()

    # Now you can use the custom categories defined in GLOBAL_CONFIG.json
    logger.colour_log("!info", "Testing custom 'debug' category", category="debug")
    logger.colour_log("!info", "Testing custom 'database' category", category="database")
    logger.colour_log("!info", "Testing custom 'warning' category", category="warning")
    logger.colour_log("!info", "Testing 'all' category (logs to all files)", category="all")

def example_2_runtime_customization():
    """
    Method 2: Create custom Logger/FileSystem with runtime category customization
    Useful for temporary or per-session customization.
    """
    print("\n=== Method 2: Runtime Customization ===")

    loader = _ConfigLoader(config_path=str(CONFIG_FILE))
    colour_manager = ColourManager(loader.load_colour_config())

    # Define custom log files
    custom_log_files = {
        "SESSION": "logs/custom_session.log",
        "MASTER": "logs/custom_master.log",
        "ERROR": "logs/custom_error.log",
        "API": "logs/api.log",
        "NETWORK": "logs/network.log"
    }

    # Define custom categories
    custom_categories = {
        "default": ["MASTER", "SESSION"],
        "error": ["ERROR", "SESSION", "MASTER"],
        "api": ["API", "SESSION", "MASTER"],
        "network": ["NETWORK", "SESSION"],
        "security": ["ERROR", "MASTER", "API"],  # Custom security category
        "all": ["MASTER", "SESSION", "ERROR", "API", "NETWORK"]
    }

    # Create logger with custom setup
    logger = Logger(colour_manager, log_files=custom_log_files)
    # Override the LOG_KEYS with custom categories
    logger.LOG_KEYS = custom_categories

    # Create filesystem with same custom setup
    fs = FileSystem(logger, custom_log_files)
    fs.LOG_KEYS = custom_categories

    # Test custom categories
    logger.colour_log("!info", "Testing custom 'api' category", category="api")
    logger.colour_log("!info", "Testing custom 'network' category", category="network")
    logger.colour_log("!info", "Testing custom 'security' category", category="security")

    # Test filesystem with custom categories
    fs.validate_and_create_folder("test_custom_logs", category="security")

def example_3_category_inheritance():
    """
    Method 3: Create category inheritance/combinations
    Shows how to build complex logging setups.
    """
    print("\n=== Method 3: Category Inheritance ===")

    loader = _ConfigLoader(config_path=str(CONFIG_FILE))
    colour_manager = ColourManager(loader.load_colour_config())

    # Advanced category setup with inheritance
    advanced_categories = {
        "default": ["MASTER", "SESSION"],
        "error": ["ERROR", "SESSION", "MASTER"],
        "fs": ["MASTER", "SESSION", "FS"],
        "init": ["INIT", "SESSION", "MASTER"],

        # Application-specific categories
        "auth": ["MASTER", "SESSION", "ERROR"],  # Authentication logs
        "business": ["MASTER", "SESSION"],       # Business logic logs
        "performance": ["MASTER", "DEBUG"],      # Performance monitoring

        # Combined categories (multi-category logging)
        "critical": ["ERROR", "MASTER", "SESSION", "DEBUG"],  # All important logs
        "verbose": ["MASTER", "SESSION", "ERROR", "FS", "INIT", "DEBUG"],  # Everything
    }

    logger = Logger(colour_manager)
    logger.LOG_KEYS = advanced_categories

    # Demonstrate different logging levels
    logger.colour_log("!info", "Standard business operation", category="business")
    logger.colour_log("!warn", "Authentication attempt", category="auth")
    logger.colour_log("!calc", "Performance metric: 150ms", category="performance")
    logger.colour_log("!error", "Critical system error", category="critical")

def example_4_dynamic_categories():
    """
    Method 4: Dynamic category creation based on runtime conditions
    Useful for plugins or modular applications.
    """
    print("\n=== Method 4: Dynamic Categories ===")

    logger = _make_logger()

    # Start with base categories
    dynamic_categories = {
        "default": ["MASTER", "SESSION"],
        "error": ["ERROR", "SESSION", "MASTER"],
    }

    # Dynamically add categories based on available modules/plugins
    available_modules = ["user_mgmt", "payment", "inventory", "reporting"]

    for module in available_modules:
        # Create module-specific log file
        log_key = module.upper()
        log_path = f"logs/{module}.log"

        # Add to log files (in real usage, you'd create the file)
        logger.log_files[log_key] = log_path

        # Add category for this module
        dynamic_categories[module] = ["MASTER", "SESSION", log_key]
        dynamic_categories[f"{module}_error"] = ["ERROR", "SESSION", "MASTER", log_key]

    logger.LOG_KEYS = dynamic_categories

    # Test dynamic categories
    for module in available_modules:
        logger.colour_log("!info", f"Module {module} initialized", category=module)
        logger.colour_log("!warn", f"Module {module} warning", category=f"{module}_error")

if __name__ == "__main__":
    print("tUilKit Logging Categories Customization Examples")
    print("=" * 50)

    # Run examples
    example_1_modify_global_config()
    example_2_runtime_customization()
    example_3_category_inheritance()
    example_4_dynamic_categories()

    print("\n" + "=" * 50)
    print("All examples completed! Check the logs/ directory for output files.")