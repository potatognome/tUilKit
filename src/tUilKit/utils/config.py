
"""
Minimal ConfigLoader for tUilKit: delegates all path logic to ConfigPathResolver, essential methods only.
"""
import os
import json
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface
from tUilKit.interfaces.file_system_interface import FileSystemInterface
from tUilKit.utils.config_path_resolver import ConfigPathResolver

class ConfigLoader(ConfigLoaderInterface):
    def __init__(self):
        config_path = self._bootstrap_config_path('tUilKit_CONFIG.json')
        self.global_config = self.load_config(config_path)
        root_modes = self.global_config.get("ROOT_MODES", {})
        self.path_resolver = ConfigPathResolver(
            config_root_mode=root_modes.get("CONFIG", "project"),
            workspace_root_path=self.global_config.get("WORKSPACE_ROOT_PATH"),
            project_root_path=self.global_config.get("PROJECT_ROOT_PATH"),
            relative_folder_paths=self.global_config.get("RELATIVE_FOLDER_PATHS", {})
        )

    def load_config(self, json_file_path: str) -> dict:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def ensure_folders_exist(self, file_system: FileSystemInterface):
        log_files = self.global_config.get("LOG_FILES", {})
        for log_path in log_files.values():
            folder = os.path.dirname(log_path)
            if folder:
                file_system.validate_and_create_folder(folder, category="fs")

    def get_config_file_path(self, config_key: str) -> str:
        shared_config_files = self.global_config.get("SHARED_CONFIG_FILES", {})
        relative_paths = self.global_config.get("RELATIVE_FOLDER_PATHS", {})
        shared_folder = relative_paths.get("SHARED", "config/GLOBAL_SHARED.d/")
        if config_key in shared_config_files:
            path = self.path_resolver.resolve_shared_config_path(config_key, shared_config_files, shared_folder)
            if path:
                return path
            raise FileNotFoundError(f"Shared config file '{config_key}' not found.")
        config_files = self.global_config.get("CONFIG_FILES", {})
        relative_path = config_files.get(config_key)
        if not relative_path:
            raise ValueError(f"Config file key '{config_key}' not found.")
        path = self.path_resolver.resolve_config_path(relative_path)
        if path:
            return path
        raise FileNotFoundError(f"Config file '{config_key}' not found.")

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        path = self.path_resolver.resolve_config_path(file)
        if path:
            return path
        raise FileNotFoundError(f"Config file '{file}' not found.")

    def get_log_file_path(self, log_key: str) -> str:
        log_files = self.global_config.get("LOG_FILES", {})
        return log_files.get(log_key)

    def get_test_log_file_path(self, test_log_key: str) -> str:
        test_log_files = self.global_config.get("TEST_LOG_FILES", {})
        return test_log_files.get(test_log_key)

    def load_colour_config(self) -> dict:
        colour_config_path = self.get_config_file_path("COLOURS")
        return self.load_config(colour_config_path)

    def load_border_patterns_config(self) -> dict:
        try:
            border_patterns_path = self.get_config_file_path("BORDER_PATTERNS")
            return self.load_config(border_patterns_path)
        except FileNotFoundError:
            # Minimal error handling, no print
            return {}

    def _bootstrap_config_path(self, file: str) -> str:
        # Minimal bootstrap logic for initial config load
        import os
        from pathlib import Path
        current_dir = Path(os.getcwd())
        root_path = current_dir / file
        if root_path.exists():
            return str(root_path)
        config_path = current_dir / "config" / file
        if config_path.exists():
            return str(config_path)
        for parent in current_dir.parents:
            parent_config = parent / "config" / file
            if parent_config.exists():
                return str(parent_config)
        fallback_abs = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", "config", file))
        if os.path.exists(fallback_abs):
            return fallback_abs
        raise FileNotFoundError(f"Config file '{file}' not found in expected locations.")