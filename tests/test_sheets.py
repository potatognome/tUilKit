"""
Tests for tUilKit.utils.sheets functions using DataFrameInterface and ConfigLoader.
"""

import sys
import os
import json
import time
import argparse
import pandas as pd

# --- 1. Command line argument for log cleanup ---
parser = argparse.ArgumentParser(description="Run tUilKit test suite.")
parser.add_argument('--clean', action='store_true', help='Remove all log files in the test log folder before running tests.')
args, unknown = parser.parse_known_args()

# --- 2. Imports and initialization ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.sheets import (
    hash_row, smart_diff, find_common_columns, find_fuzzy_columns, find_composite_keys, SmartDataFrameHandler
)
from tUilKit.config.config import ConfigLoader

COLOUR_CONFIG_PATH = os.path.join(base_dir, "tUilKit", "config", "COLOURS.json")
with open(COLOUR_CONFIG_PATH, "r") as f:
    colour_config = json.load(f)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
config_loader = ConfigLoader()

TEST_LOG_FOLDER = os.path.join(os.path.dirname(__file__), "testOutputLogs")
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_sheets_output.log")

if not os.path.exists(TEST_LOG_FOLDER):
    os.makedirs(TEST_LOG_FOLDER, exist_ok=True)

# Remove all log files if --clean is passed
if args.clean:
    for fname in os.listdir(TEST_LOG_FOLDER):
        if fname.endswith('.log'):
            try:
                os.remove(os.path.join(TEST_LOG_FOLDER, fname))
            except Exception as e:
                print(f"Could not remove {fname}: {e}")

# --- 3. Test variables ---
df1 = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
df2 = pd.DataFrame({"A": [3, 2, 1], "B": ["z", "y", "x"]})
df3 = pd.DataFrame({"A": [1, 2, 4], "B": ["x", "y", "w"]})
handler = SmartDataFrameHandler()

# --- 4. Test functions ---
def test_hash_row(function_log = None):
    row = df1.iloc[0]
    h1 = hash_row(row, ["A", "B"])
    h2 = hash_row(row, ["B", "A"])
    assert h1 == h2, f"Hashes should be equal regardless of column order: {h1} vs {h2}"
    # Edge case: empty columns
    h_empty = hash_row(row, [])
    assert isinstance(h_empty, int), "Hash of empty columns should be int"
    logger.colour_log("PROC", "hash_row", "PASSED", "produces consistent hash:", "DATA", h1, log_file=TEST_LOG_FILE)
    logger.colour_log("PROC", "hash_row", "INFO", f"Hash with empty columns: {h_empty}", log_file=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("PROC", "hash_row", "PASSED", "produces consistent hash:", "DATA", h1, log_file=function_log)
        logger.colour_log("PROC", "hash_row", "INFO", f"Hash with empty columns: {h_empty}", log_file=function_log)

def test_smart_diff(function_log = None):
    diff = handler.compare(df1, df3)
    assert not diff.empty, "Diff should not be empty for different dataframes"
    # Edge case: identical dataframes
    diff_identical = handler.compare(df1, df1)
    assert diff_identical.empty, "Diff should be empty for identical dataframes"
    logger.colour_log("PROC", "smart_diff found", "OUTPUT", f"{len(diff)}", "LIST", "differing rows.", log_file=TEST_LOG_FILE)
    logger.colour_log("PROC", "smart_diff identical", "OUTPUT", f"{len(diff_identical)}", "LIST", "identical rows.", log_file=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("PROC", "smart_diff found", "OUTPUT", f"{len(diff)}", "LIST", "differing rows.", log_file=function_log)
        logger.colour_log("PROC", "smart_diff identical", "OUTPUT", f"{len(diff_identical)}", "LIST", "identical rows.", log_file=function_log)

def test_find_common_columns(function_log = None):
    cols = find_common_columns([df1, df2, df3])
    assert "A" in cols and "B" in cols, f"Expected columns 'A' and 'B' in common columns: {cols}"
    # Edge case: no common columns
    df_no_common = pd.DataFrame({"X": [1], "Y": [2]})
    cols_none = find_common_columns([df1, df_no_common])
    assert cols_none == [], f"Expected no common columns, got: {cols_none}"
    logger.colour_log("PROC", "find_common_columns:", "OUTPUT", cols, log_file=TEST_LOG_FILE)
    logger.colour_log("PROC", "find_common_columns (none):", "OUTPUT", cols_none, log_file=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("PROC", "find_common_columns:", "OUTPUT", cols, log_file=function_log)
        logger.colour_log("PROC", "find_common_columns (none):", "OUTPUT", cols_none, log_file=function_log)

def test_find_composite_keys(function_log = None):
    keys = find_composite_keys(df1, df2)
    assert isinstance(keys, list), f"Composite keys should be a list, got {type(keys)}"
    # Edge case: no keys
    df_empty = pd.DataFrame()
    keys_empty = find_composite_keys(df_empty, df_empty)
    assert keys_empty == [], f"Expected no composite keys for empty dataframes, got: {keys_empty}"
    logger.colour_log("PROC", "find_composite_keys:", "OUTPUT", keys, log_file=TEST_LOG_FILE)
    logger.colour_log("PROC", "find_composite_keys (empty):", "OUTPUT", keys_empty, log_file=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("PROC", "find_composite_keys:", "OUTPUT", keys, log_file=function_log)
        logger.colour_log("PROC", "find_composite_keys (empty):", "OUTPUT", keys_empty, log_file=function_log)

def test_smart_merge(function_log = None):
    merged = handler.merge([df1, df2], merge_type="outer", config_loader=config_loader)
    assert len(merged) == 6, f"Expected 6 rows after outer merge, got {len(merged)}"
    # Edge case: merge with empty dataframe
    merged_empty = handler.merge([df1, pd.DataFrame()], merge_type="outer", config_loader=config_loader)
    assert len(merged_empty) == len(df1), f"Expected {len(df1)} rows when merging with empty, got {len(merged_empty)}"
    logger.colour_log("PROC", "smart_merge produced", "OUTPUT", f"{len(merged)}", "LIST", "rows.", log_file=TEST_LOG_FILE)
    logger.colour_log("PROC", "smart_merge (empty):", "OUTPUT", f"{len(merged_empty)}", "LIST", "rows.", log_file=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("PROC", "smart_merge produced", "OUTPUT", f"{len(merged)}", "LIST", "rows.", log_file=function_log)
        logger.colour_log("PROC", "smart_merge (empty):", "OUTPUT", f"{len(merged_empty)}", "LIST", "rows.", log_file=function_log)

def test_find_fuzzy_columns(function_log = None):
    df_fuzzy1 = pd.DataFrame({"Name": ["Alice", "Bob", "Charlie"], "Amount": [100, 200, 300]})
    df_fuzzy2 = pd.DataFrame({"FullName": ["Alic", "B0b", "Charley"], "Amount": [100, 200, 300]})
    df_fuzzy3 = pd.DataFrame({"Name": ["Alice", "Bob", "Charlie"], "Total": [100, 200, 300]})
    cols = find_fuzzy_columns([df_fuzzy1, df_fuzzy2, df_fuzzy3])
    assert "Name" in cols or "Amount" in cols, f"Expected 'Name' or 'Amount' in fuzzy columns: {cols}"
    # Edge case: no fuzzy matches
    df_no_fuzzy = pd.DataFrame({"X": [1], "Y": [2]})
    cols_none = find_fuzzy_columns([df_fuzzy1, df_no_fuzzy])
    assert isinstance(cols_none, list), f"Expected list for fuzzy columns, got {type(cols_none)}"
    logger.colour_log("PROC", "find_fuzzy_columns:", "OUTPUT", cols, log_file=TEST_LOG_FILE)
    logger.colour_log("PROC", "find_fuzzy_columns (none):", "OUTPUT", cols_none, log_file=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("PROC", "find_fuzzy_columns:", "OUTPUT", cols, log_file=function_log)
        logger.colour_log("PROC", "find_fuzzy_columns (none):", "OUTPUT", cols_none, log_file=function_log)

# --- 5. TESTS tuple ---
TESTS = [
    (1, "test_hash_row", test_hash_row),
    (2, "test_smart_diff", test_smart_diff),
    (3, "test_find_common_columns", test_find_common_columns),
    (4, "test_find_composite_keys", test_find_composite_keys),
    (5, "test_smart_merge", test_smart_merge),
    (6, "test_find_fuzzy_columns", test_find_fuzzy_columns),
]

# --- 6. Test runner ---
if __name__ == "__main__":
    results = []
    successful = []
    unsuccessful = []

    border_pattern = {
        "TOP": ["==="],
        "LEFT": ["|"],
        "RIGHT": ["|"],
        "BOTTOM": ["==="]
    }

    for num, name, func in TESTS:
        function_log = os.path.join(TEST_LOG_FOLDER, f"{name}.log")
        try:
            logger.print_rainbow_row(pattern="X-O-", spacer=2, log_file=TEST_LOG_FILE)
            logger.print_rainbow_row(pattern="X-O-", spacer=2, log_file=function_log, log_to="file")
            logger.print_top_border(border_pattern, 40, log_file=TEST_LOG_FILE)
            logger.print_top_border(border_pattern, 40, log_file=function_log, log_to="file")
            logger.print_text_line("TEST", "Running test", "INT", num, "INFO", ":", "PROC", name, log_file=TEST_LOG_FILE, log_to="both")
            logger.colour_log("TEST", "Running test", "INT", num, "INFO", ":", "PROC", name, log_file=TEST_LOG_FILE, log_to="both")
            logger.colour_log("TEST", "Running test", "INT", num, "INFO", ":", "PROC", name, log_file=function_log, log_to="file")
            time.sleep(1)
            func(function_log=function_log)
            logger.colour_log("TEST", "Test", "INT", num, "INFO", ":", "PROC", name, "PASSED", "PASSED.", log_file=TEST_LOG_FILE, log_to="both")
            logger.colour_log("TEST", "Test", "INT", num, "INFO", ":", "PROC", name, "PASSED", "PASSED.", log_file=function_log, log_to="file")
            results.append((num, name, True))
            successful.append(name)
        except Exception as e:
            logger.log_exception(f"{name} failed", e, log_file=TEST_LOG_FILE)
            logger.log_exception(f"{name} failed", e, log_file=function_log, log_to="file")
            results.append((num, name, False))
            unsuccessful.append(name)

    total_count = len(TESTS)
    count_successes = sum(1 for _, _, passed in results if passed)
    count_unsuccessfuls = total_count - count_successes

    logger.colour_log("PASSED", "Successful tests:", "INT", f"{count_successes} / {total_count}", "LIST", successful, log_file=TEST_LOG_FILE)
    if count_unsuccessfuls > 0:
        logger.colour_log("FAIL", "Unsuccessful tests:", "FAIL", count_unsuccessfuls, "INT", f"/ {total_count}", "LIST", unsuccessful, log_file=TEST_LOG_FILE)
        for num, name, passed in results:
            if not passed:
                logger.colour_log("TEST", "Test", "INT", num, "INFO", ":", "PROC", name, "FAIL", "FAILED.", log_file=TEST_LOG_FILE)
    else:
        logger.colour_log("DONE", "All tests passed!", log_file=TEST_LOG_FILE)