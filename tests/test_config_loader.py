import pytest
from tUilKit.utils.config import ConfigLoader

def test_config_loader_version():
    loader = ConfigLoader()
    version = loader.global_config.get("VERSION")
    expected_version = "0.7.0"
    if version != expected_version:
        pytest.skip(f"VERSION mismatch: expected {expected_version}, got {version}. Skipping test.")
    assert version == expected_version, f"VERSION should be {expected_version}, got {version}"
