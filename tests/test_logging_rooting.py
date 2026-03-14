"""
tUilKit Logging Rooting & Dual Logging Tests
App: tUilKit Logging Tests
"""
import os
import shutil
import pytest
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.config import ConfigLoader

TEST_APP_NAME = "tUilKitLoggingTests"
TEST_LOG_ROOT = ".logs/tUilKitLoggingTests/"
TUILKIT_LOG_ROOT = ".logs/tUilKit/"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Clean up test log folders before and after
    for folder in [TEST_LOG_ROOT, TUILKIT_LOG_ROOT]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    yield
    for folder in [TEST_LOG_ROOT, TUILKIT_LOG_ROOT]:
        if os.path.exists(folder):
            shutil.rmtree(folder)


def get_test_logger():
    config_loader = ConfigLoader()
    colour_config = config_loader.load_colour_config()
    colour_mgr = ColourManager(colour_config)
    tests_options = config_loader.global_config.get("TESTS_OPTIONS", {})
    test_logs_folder = tests_options.get("TEST_LOGS_FOLDER", ".testlogs/tUilKit/")
    log_files = {
        "SESSION": os.path.join(test_logs_folder, "SESSION.log"),
        "MASTER": os.path.join(test_logs_folder, "MASTER.log"),
        "ERROR": os.path.join(test_logs_folder, "ERROR.log")
    }
    os.environ["TUILKIT_TEST_MODE"] = "1"
    return Logger(colour_mgr, log_files=log_files)

def test_dual_logging_session():
    logger = get_test_logger()
    msg = "Dual logging test message"
    logger.log_message(msg, log_files=[f"{TEST_LOG_ROOT}SESSION.log"], log_to="file", time_stamp=False)
    # Check app log
    with open(f"{TEST_LOG_ROOT}SESSION.log", "r", encoding="utf-8") as f:
        content_app = f.read()
    # Check tUilKit central log
    with open(f"{TUILKIT_LOG_ROOT}SESSION.log", "r", encoding="utf-8") as f:
        content_tuilkit = f.read()
    assert msg in content_app, "App SESSION log missing message"
    assert msg in content_tuilkit, "tUilKit SESSION log missing message"

def test_log_root_env_override(monkeypatch):
    monkeypatch.setenv("TUILKIT_LOG_ROOT", ".logs/CustomRoot/")
    config_loader = ConfigLoader()
    colour_config = config_loader.load_colour_config()
    colour_mgr = ColourManager(colour_config)
    log_files = {
        "SESSION": "SESSION.log"
    }
    os.environ["TUILKIT_TEST_MODE"] = "1"
    logger = Logger(colour_mgr, log_files=log_files)
    msg = "Env override test"
    logger.log_message(msg, log_files=["SESSION.log"], log_to="file", time_stamp=False)
    # Should write to .logs/CustomRoot/tUilKit/SESSION.log
    custom_log = ".logs/CustomRoot/tUilKit/SESSION.log"
    assert os.path.exists(custom_log), "Env override log file not created"
    with open(custom_log, "r", encoding="utf-8") as f:
        assert msg in f.read(), "Env override log missing message"
    # Cleanup
    shutil.rmtree(".logs/CustomRoot/")

def test_log_message_to_master():
    logger = get_test_logger()
    msg = "Master log test"
    logger.log_message(msg, log_files=[f"{TEST_LOG_ROOT}MASTER.log"], log_to="file", time_stamp=False)
    with open(f"{TEST_LOG_ROOT}MASTER.log", "r", encoding="utf-8") as f:
        assert msg in f.read(), "Master log missing message"

def test_log_message_to_error():
    logger = get_test_logger()
    msg = "Error log test"
    logger.log_message(msg, log_files=[f"{TEST_LOG_ROOT}ERROR.log"], log_to="file", time_stamp=False)
    with open(f"{TEST_LOG_ROOT}ERROR.log", "r", encoding="utf-8") as f:
        assert msg in f.read(), "Error log missing message"
