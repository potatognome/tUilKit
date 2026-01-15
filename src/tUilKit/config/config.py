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
        """
        Find config file by checking multiple locations in priority order.
        Supports both tUilKit package structure and retrofitted project structure.
        Searches upward from cwd to find project root with config/ directory.
        
        Search order:
        1. cwd/file (e.g., Syncbot/GLOBAL_CONFIG.json)
        2. cwd/config/file (e.g., Syncbot/config/GLOBAL_CONFIG.json)
        3. Walk up parent directories looking for config/file
        4. tUilKit package config/ (fallback)
        """
        import os
        from pathlib import Path
        
        current_dir = Path(os.getcwd())
        
        # Check current directory root
        root_path = current_dir / file
        if root_path.exists():
            return str(root_path)
        
        # Check current directory config/ subdirectory
        config_path = current_dir / "config" / file
        if config_path.exists():
            return str(config_path)
        
        # Walk up parent directories looking for config/ folder
        for parent in current_dir.parents:
            parent_config = parent / "config" / file
            if parent_config.exists():
                return str(parent_config)
            # Stop at root or common project boundaries
            if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                # Found a project root, check its config
                if parent_config.exists():
                    return str(parent_config)
                break
        
        # Fall back to tUilKit's config directory
        return os.path.join(os.path.dirname(__file__), file)

    def load_config(self, json_file_path: str) -> dict:
        with open(json_file_path, 'r') as f:
            return json.load(f)

    def ensure_folders_exist(self, file_system: FileSystemInterface):
        log_files = self.global_config.get("LOG_FILES", {})
        for log_path in log_files.values():
            folder = os.path.dirname(log_path)
            if folder:
                file_system.validate_and_create_folder(folder, category="fs")

    def get_config_file_path(self, config_key: str) -> str:
        """
        Get the path to a config file from the CONFIG_FILES section of global config.
        Searches upward from cwd to find the project root.
        """
        from pathlib import Path
        
        config_files = self.global_config.get("CONFIG_FILES", {})
        relative_path = config_files.get(config_key)
        if not relative_path:
            raise ValueError(f"Config file key '{config_key}' not found in CONFIG_FILES")
        
        current_dir = Path(os.getcwd())
        
        # Try current directory
        direct_path = current_dir / relative_path
        if direct_path.exists():
            return str(direct_path)
        
        # Walk up parents looking for the config file
        for parent in current_dir.parents:
            parent_path = parent / relative_path
            if parent_path.exists():
                return str(parent_path)
            # Stop at project root markers
            if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                if parent_path.exists():
                    return str(parent_path)
                break
        
        # Fall back to cwd-relative (original behavior)
        return os.path.join(os.getcwd(), relative_path)

    def get_log_file_path(self, log_key: str) -> str:
        """
        Get the path to a log file from the LOG_FILES section of global config.
        """
        log_files = self.global_config.get("LOG_FILES", {})
        return log_files.get(log_key)

    def load_colour_config(self) -> dict:
        """
        Load the colour configuration from the COLOURS config file.
        """
        colour_config_path = self.get_config_file_path("COLOURS")
        return self.load_config(colour_config_path)

    def load_border_patterns_config(self) -> dict:
        """
        Load the border patterns configuration from the BORDER_PATTERNS config file.
        """
        border_patterns_path = self.get_config_file_path("BORDER_PATTERNS")
        return self.load_config(border_patterns_path)

# Create a global instance
config_loader = ConfigLoader()
global_config = config_loader.global_config



