# Lib/site-packages/tUilKit/interfaces/config_loader_interface.py
"""
    This module defines the ConfigLoaderInterface, which provides an abstract interface for
    loading JSON configuration files and ensuring the existence of specified folders.
"""
 
from abc import ABC, abstractmethod

class ConfigLoaderInterface(ABC):
    @abstractmethod
    def load_config(self, json_file_path: str) -> dict:
        pass

    @abstractmethod
    def get_json_path(self, file: str, cwd: bool = False) -> str:
        pass

    @abstractmethod
    def ensure_folders_exist(self, file_system) -> None:
        """Create all folders specified in the configuration using the provided file system."""
        pass
