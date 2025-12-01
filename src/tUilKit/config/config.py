# Lib/site-packages/tUilKit/config/config.py
"""
   Load JSON configuration of GLOBAL variables.
"""
import os
import json
from tUilKit.utils.fs import FileSystem
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface
from tUilKit.interfaces.file_system_interface import FileSystemInterface
 

class ConfigLoader(ConfigLoaderInterface):
    def __init__(self):
        self.global_config = self.load_config(self.get_json_path('GLOBAL_CONFIG.json'))

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        if cwd:
            local_path = os.path.join(os.getcwd(), file)
            if os.path.exists(local_path):
                return local_path
        return os.path.join(os.path.dirname(__file__), file)

    def load_config(self, json_file_path: str) -> dict:
        with open(json_file_path, 'r') as f:
            return json.load(f)

    def ensure_folders_exist(self, file_system: FileSystemInterface):
        make_folders = self.global_config.get("MAKE_FOLDERS", {})
        for folder in make_folders.values():
            file_system.validate_and_create_folder(folder)

# Only load GLOBAL_CONFIG.json
config_loader = ConfigLoader()
global_config = config_loader.load_config(config_loader.get_json_path('GLOBAL_CONFIG.json'))

# LOG_FILE usage below assumes the keys exist in your config
if 'FOLDERS' in global_config and 'TEST_LOG_FILES' in global_config['FOLDERS'] and 'FILES' in global_config and 'INIT_LOG' in global_config['FILES']:
    LOG_FILE = f"{global_config['FOLDERS']['TEST_LOG_FILES']}{global_config['FILES']['INIT_LOG']}"
else:
    LOG_FILE = None



