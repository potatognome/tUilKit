# Lib/site-packages/tUilKit/config/config.py
"""
   Load JSON configuration of GLOBAL variables.
"""
import os
import json
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
        log_files = self.global_config.get("LOG_FILES", {})
        for log_path in log_files.values():
            folder = os.path.dirname(log_path)
            if folder:
                file_system.validate_and_create_folder(folder)

# Create a global instance
config_loader = ConfigLoader()
global_config = config_loader.global_config



