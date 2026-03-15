"""
Minimal test for tUilKit ConfigLoader: verifies config loading and basic path resolution.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from tUilKit.utils.config import ConfigLoader

# Instantiate ConfigLoader
loader = ConfigLoader()

# Print loaded global config keys
print("Loaded config keys:", list(loader.global_config.keys()))

# Test basic config path resolution
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
