"""
Minimal ConfigLoader for tUilKit: unified path logic, proper indentation, essential methods only.
"""
import os
import json
from pathlib import Path
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface
from tUilKit.interfaces.file_system_interface import FileSystemInterface

class ConfigLoader(ConfigLoaderInterface):
    def __init__(self):
        config_path = self._get_json_path_bootstrap('tUilKit_CONFIG.json')
        self.global_config = self.load_config(config_path)

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
        shared_config_files = self.global_config.get("SHARED_CONFIG_FILES", {})
        if config_key in shared_config_files:
            return self._resolve_path(config_key, search_type="shared", config_key=config_key)
        return self._resolve_path(config_key, search_type="config", config_key=config_key)

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        return self._resolve_path(file, search_type="generic")

    def get_log_file_path(self, log_key: str) -> str:
        return self._resolve_path(log_key, search_type="log")

    def get_test_log_file_path(self, test_log_key: str) -> str:
        return self._resolve_path(test_log_key, search_type="test_log")

    def load_colour_config(self) -> dict:
        colour_config_path = self.get_config_file_path("COLOURS")
        return self.load_config(colour_config_path)

    def load_border_patterns_config(self) -> dict:
        try:
            border_patterns_path = self.get_config_file_path("BORDER_PATTERNS")
            return self.load_config(border_patterns_path)
        except FileNotFoundError as e:
            print(f"ConfigLoader: Warning - {e}. Returning empty border patterns config.")
            return {}

    def _resolve_path(self, file: str, search_type: str = "config", config_key: str = None) -> str:
        current_dir = Path(os.getcwd())
        checked_paths = []
        if search_type == "shared" and config_key:
            shared_config_files = self.global_config.get("SHARED_CONFIG_FILES", {})
            relative_paths = self.global_config.get("RELATIVE_FOLDER_PATHS", {})
            shared_folder = relative_paths.get("SHARED", "config/GLOBAL_SHARED.d/")
            shared_path = shared_config_files[config_key]
            abs_path = os.path.abspath(os.path.join(shared_folder, shared_path))
            cwd_path = os.path.abspath(os.path.join(os.getcwd(), shared_folder, shared_path))
            dev_shared_path = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", shared_folder, shared_path))
            checked_paths.extend([abs_path, cwd_path, dev_shared_path])
            for path in checked_paths:
                if os.path.exists(path):
                    print(f"ConfigLoader: Loaded shared config '{config_key}' from {path}")
                    return path
            print(f"ConfigLoader: Shared config file '{shared_path}' not found. Checked: {checked_paths}")
            raise FileNotFoundError(f"Shared config file '{shared_path}' not found in modular folder '{shared_folder}'. Checked: {checked_paths}")
        if search_type == "config" and config_key:
            config_files = self.global_config.get("CONFIG_FILES", {})
            relative_path = config_files.get(config_key)
            if not relative_path:
                raise ValueError(f"Config file key '{config_key}' not found in CONFIG_FILES or SHARED_CONFIG_FILES")
            direct_path = current_dir / relative_path
            checked_paths.append(str(direct_path))
            if direct_path.exists():
                print(f"ConfigLoader: Loaded config '{config_key}' from {direct_path}")
                return str(direct_path)
            for parent in current_dir.parents:
                parent_path = parent / relative_path
                checked_paths.append(str(parent_path))
                if parent_path.exists():
                    print(f"ConfigLoader: Loaded config '{config_key}' from {parent_path}")
                    return str(parent_path)
                if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                    if parent_path.exists():
                        print(f"ConfigLoader: Loaded config '{config_key}' from {parent_path}")
                        return str(parent_path)
                    break
            fallback_path = os.path.join(os.getcwd(), relative_path)
            checked_paths.append(fallback_path)
            print(f"ConfigLoader: Loaded config '{config_key}' from fallback {fallback_path}")
            return fallback_path
        if search_type == "generic":
            root_path = current_dir / file
            checked_paths.append(str(root_path))
            if root_path.exists():
                return str(root_path)
            config_path = current_dir / "config" / file
            checked_paths.append(str(config_path))
            if config_path.exists():
                return str(config_path)
            for parent in current_dir.parents:
                parent_config = parent / "config" / file
                checked_paths.append(str(parent_config))
                if parent_config.exists():
                    return str(parent_config)
                if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                    if parent_config.exists():
                        return str(parent_config)
                    break
            root_modes = self.global_config.get("ROOT_MODES", {})
            config_root_mode = root_modes.get("CONFIG", "project")
            if config_root_mode == "workspace":
                workspace_root = Path(__file__).resolve().parents[5]
                fallback_config = workspace_root / "config" / file
            elif config_root_mode == "project":
                repo_root = Path(__file__).resolve().parents[4]
                fallback_config = repo_root / "Dev" / "tUilKit" / "config" / file
            else:
                workspace_root = Path(__file__).resolve().parents[5]
                fallback_config = workspace_root / "config" / file
            checked_paths.append(str(fallback_config))
            if fallback_config.exists():
                return str(fallback_config)
            raise FileNotFoundError(f"Config file '{file}' not found in expected locations. Checked: {checked_paths}")
        if search_type in ["log", "test_log"]:
            log_files = self.global_config.get("LOG_FILES", {})
            root_modes = self.global_config.get("ROOT_MODES", {})
            workspace_root = self.global_config.get("WORKSPACE_ROOT_PATH", None)
            log_key = file
            log_path = log_files.get(log_key)
            log_root_mode = root_modes.get("LOGS" if search_type == "log" else "TEST_LOGS", "project")
            if log_root_mode == "workspace" and workspace_root:
                if log_path and not os.path.isabs(log_path):
                    return os.path.join(workspace_root, log_path)
                else:
                    return log_path
            return log_path
        raise ValueError(f"Unknown search_type '{search_type}' for _resolve_path")

    def _get_json_path_bootstrap(self, file: str) -> str:
        """
        Bootstrap config path finder for initial load, avoids self.global_config access.
        """
        checked_paths = []
        current_dir = Path(os.getcwd())
        root_path = current_dir / file
        checked_paths.append(str(root_path))
        if root_path.exists():
            print(f"ConfigLoader: Found config at {root_path}")
            return str(root_path)
        config_path = current_dir / "config" / file
        checked_paths.append(str(config_path))
        if config_path.exists():
            print(f"ConfigLoader: Found config at {config_path}")
            return str(config_path)
        for parent in current_dir.parents:
            parent_config = parent / "config" / file
            checked_paths.append(str(parent_config))
            if parent_config.exists():
                print(f"ConfigLoader: Found config at {parent_config}")
                return str(parent_config)
            if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                if parent_config.exists():
                    print(f"ConfigLoader: Found config at {parent_config}")
                    return str(parent_config)
                break
        # Bootstrap: use environment variable or default for root mode
        config_root_mode = os.environ.get("CONFIG_ROOT_MODE", "project")
        if config_root_mode == "workspace":
            workspace_root = Path(__file__).resolve().parents[5]
            fallback_config = workspace_root / "config" / file
            checked_paths.append(str(fallback_config))
        elif config_root_mode == "project":
            repo_root = Path(__file__).resolve().parents[4]
            fallback_config = repo_root / "Dev" / "tUilKit" / "config" / file
            checked_paths.append(str(fallback_config))
        else:
            # For 'auto', 'manual', etc., default to workspace root
            workspace_root = Path(__file__).resolve().parents[5]
            fallback_config = workspace_root / "config" / file
            checked_paths.append(str(fallback_config))
        if fallback_config.exists():
            print(f"ConfigLoader: Found config at {fallback_config}")
            return str(fallback_config)

        # Explicit fallback for test/dev environments
        explicit_fallback = Path(__file__).resolve().parents[4] / "Dev" / "tUilKit" / "config" / file
        checked_paths.append(str(explicit_fallback))
        if explicit_fallback.exists():
            print(f"ConfigLoader: Found config at {explicit_fallback}")
            return str(explicit_fallback)

        # Absolute path fallback using workspace root
        workspace_root_abs = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", "config", file))
        checked_paths.append(workspace_root_abs)
        if os.path.exists(workspace_root_abs):
            print(f"ConfigLoader: Found config at {workspace_root_abs}")
            return workspace_root_abs

        print(f"ConfigLoader: Checked paths for config: {checked_paths}")
        raise FileNotFoundError(f"Config file '{file}' not found in expected locations. Checked: {checked_paths}")
"""
Minimal ConfigLoader for tUilKit: unified path logic, proper indentation, essential methods only.
"""
import os
import json
from pathlib import Path
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface
from tUilKit.interfaces.file_system_interface import FileSystemInterface

class ConfigLoader(ConfigLoaderInterface):
    def __init__(self):
        config_path = self._get_json_path_bootstrap('tUilKit_CONFIG.json')
        self.global_config = self.load_config(config_path)

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
        shared_config_files = self.global_config.get("SHARED_CONFIG_FILES", {})
        if config_key in shared_config_files:
            return self._resolve_path(config_key, search_type="shared", config_key=config_key)
        return self._resolve_path(config_key, search_type="config", config_key=config_key)

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        return self._resolve_path(file, search_type="generic")

    def get_log_file_path(self, log_key: str) -> str:
        return self._resolve_path(log_key, search_type="log")

    def get_test_log_file_path(self, test_log_key: str) -> str:
        return self._resolve_path(test_log_key, search_type="test_log")

    def load_colour_config(self) -> dict:
        colour_config_path = self.get_config_file_path("COLOURS")
        return self.load_config(colour_config_path)

    def load_border_patterns_config(self) -> dict:
        try:
            border_patterns_path = self.get_config_file_path("BORDER_PATTERNS")
            return self.load_config(border_patterns_path)
        except FileNotFoundError as e:
            print(f"ConfigLoader: Warning - {e}. Returning empty border patterns config.")
            return {}

    def _resolve_path(self, file: str, search_type: str = "config", config_key: str = None) -> str:
        current_dir = Path(os.getcwd())
        checked_paths = []
        if search_type == "shared" and config_key:
            shared_config_files = self.global_config.get("SHARED_CONFIG_FILES", {})
            relative_paths = self.global_config.get("RELATIVE_FOLDER_PATHS", {})
            shared_folder = relative_paths.get("SHARED", "config/GLOBAL_SHARED.d/")
            shared_path = shared_config_files[config_key]
            abs_path = os.path.abspath(os.path.join(shared_folder, shared_path))
            cwd_path = os.path.abspath(os.path.join(os.getcwd(), shared_folder, shared_path))
            dev_shared_path = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", shared_folder, shared_path))
            checked_paths.extend([abs_path, cwd_path, dev_shared_path])
            for path in checked_paths:
                if os.path.exists(path):
                    print(f"ConfigLoader: Loaded shared config '{config_key}' from {path}")
                    return path
            print(f"ConfigLoader: Shared config file '{shared_path}' not found. Checked: {checked_paths}")
            raise FileNotFoundError(f"Shared config file '{shared_path}' not found in modular folder '{shared_folder}'. Checked: {checked_paths}")
        if search_type == "config" and config_key:
            config_files = self.global_config.get("CONFIG_FILES", {})
            relative_path = config_files.get(config_key)
            if not relative_path:
                raise ValueError(f"Config file key '{config_key}' not found in CONFIG_FILES or SHARED_CONFIG_FILES")
            direct_path = current_dir / relative_path
            checked_paths.append(str(direct_path))
            if direct_path.exists():
                print(f"ConfigLoader: Loaded config '{config_key}' from {direct_path}")
                return str(direct_path)
            for parent in current_dir.parents:
                parent_path = parent / relative_path
                checked_paths.append(str(parent_path))
                if parent_path.exists():
                    print(f"ConfigLoader: Loaded config '{config_key}' from {parent_path}")
                    return str(parent_path)
                if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                    if parent_path.exists():
                        print(f"ConfigLoader: Loaded config '{config_key}' from {parent_path}")
                        return str(parent_path)
                    break
            fallback_path = os.path.join(os.getcwd(), relative_path)
            checked_paths.append(fallback_path)
            print(f"ConfigLoader: Loaded config '{config_key}' from fallback {fallback_path}")
            return fallback_path
        if search_type == "generic":
            root_path = current_dir / file
            checked_paths.append(str(root_path))
            if root_path.exists():
                return str(root_path)
            config_path = current_dir / "config" / file
            checked_paths.append(str(config_path))
            if config_path.exists():
                return str(config_path)
            for parent in current_dir.parents:
                parent_config = parent / "config" / file
                checked_paths.append(str(parent_config))
                if parent_config.exists():
                    return str(parent_config)
                if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                    if parent_config.exists():
                        return str(parent_config)
                        break
                # Clean region: no stray function definitions, only valid code
            config_root_mode = root_modes.get("CONFIG", "project")
            if config_root_mode == "workspace":
                workspace_root = Path(__file__).resolve().parents[5]
                fallback_config = workspace_root / "config" / file
            elif config_root_mode == "project":
                repo_root = Path(__file__).resolve().parents[4]
                fallback_config = repo_root / "Dev" / "tUilKit" / "config" / file
            else:
                workspace_root = Path(__file__).resolve().parents[5]
                fallback_config = workspace_root / "config" / file
            checked_paths.append(str(fallback_config))
            if fallback_config.exists():
                return str(fallback_config)
            raise FileNotFoundError(f"Config file '{file}' not found in expected locations. Checked: {checked_paths}")
        if search_type in ["log", "test_log"]:
            log_files = self.global_config.get("LOG_FILES", {})
            root_modes = self.global_config.get("ROOT_MODES", {})
            workspace_root = self.global_config.get("WORKSPACE_ROOT_PATH", None)
            log_key = file
            log_path = log_files.get(log_key)
            log_root_mode = root_modes.get("LOGS" if search_type == "log" else "TEST_LOGS", "project")
            if log_root_mode == "workspace" and workspace_root:
                if log_path and not os.path.isabs(log_path):
                    return os.path.join(workspace_root, log_path)
                else:
                    return log_path
            return log_path
        raise ValueError(f"Unknown search_type '{search_type}' for _resolve_path")


    def _get_json_path_bootstrap(self, file: str) -> str:
        """
        Bootstrap config path finder for initial load, avoids self.global_config access.
        """
        import os
        from pathlib import Path

        checked_paths = []
        current_dir = Path(os.getcwd())
        root_path = current_dir / file
        checked_paths.append(str(root_path))
        if root_path.exists():
            print(f"ConfigLoader: Found config at {root_path}")
            return str(root_path)
        config_path = current_dir / "config" / file
        checked_paths.append(str(config_path))
        if config_path.exists():
            print(f"ConfigLoader: Found config at {config_path}")
            return str(config_path)
        for parent in current_dir.parents:
            parent_config = parent / "config" / file
            checked_paths.append(str(parent_config))
            if parent_config.exists():
                print(f"ConfigLoader: Found config at {parent_config}")
                return str(parent_config)
            if (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                if parent_config.exists():
                    print(f"ConfigLoader: Found config at {parent_config}")
                    return str(parent_config)
                break
        # Bootstrap: use environment variable or default for root mode
        config_root_mode = os.environ.get("CONFIG_ROOT_MODE", "project")
        if config_root_mode == "workspace":
            workspace_root = Path(__file__).resolve().parents[5]
            fallback_config = workspace_root / "config" / file
            checked_paths.append(str(fallback_config))
        elif config_root_mode == "project":
            repo_root = Path(__file__).resolve().parents[4]
            fallback_config = repo_root / "Dev" / "tUilKit" / "config" / file
            checked_paths.append(str(fallback_config))
        else:
            # For 'auto', 'manual', etc., default to workspace root
            workspace_root = Path(__file__).resolve().parents[5]
            fallback_config = workspace_root / "config" / file
            checked_paths.append(str(fallback_config))
        if fallback_config.exists():
            print(f"ConfigLoader: Found config at {fallback_config}")
            return str(fallback_config)

        # Explicit fallback for test/dev environments
        explicit_fallback = Path(__file__).resolve().parents[4] / "Dev" / "tUilKit" / "config" / file
        checked_paths.append(str(explicit_fallback))
        if explicit_fallback.exists():
            print(f"ConfigLoader: Found config at {explicit_fallback}")
            return str(explicit_fallback)

        # Absolute path fallback using workspace root
        workspace_root_abs = os.path.abspath(os.path.join(os.getcwd(), "Dev", "tUilKit", "config", file))
        checked_paths.append(workspace_root_abs)
        if os.path.exists(workspace_root_abs):
            print(f"ConfigLoader: Found config at {workspace_root_abs}")
            return workspace_root_abs

        print(f"ConfigLoader: Checked paths for config: {checked_paths}")
        raise FileNotFoundError(f"Config file '{file}' not found in expected locations. Checked: {checked_paths}")

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        return self._resolve_path(file, search_type="generic")

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
        shared_config_files = self.global_config.get("SHARED_CONFIG_FILES", {})
        if config_key in shared_config_files:
            return self._resolve_path(config_key, search_type="shared", config_key=config_key)
        return self._resolve_path(config_key, search_type="config", config_key=config_key)

    def get_log_file_path(self, log_key: str) -> str:
        return self._resolve_path(log_key, search_type="log")

    def get_test_log_file_path(self, test_log_key: str) -> str:
        return self._resolve_path(test_log_key, search_type="test_log")

    def load_colour_config(self) -> dict:
        colour_config_path = self.get_config_file_path("COLOURS")
        return self.load_config(colour_config_path)

    # Remove duplicate method definition (already defined above with error handling)
