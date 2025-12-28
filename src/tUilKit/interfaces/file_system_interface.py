# Lib/site-packages/tUilKit/interfaces/file_system_interface.py
"""
    This module defines the FileSystemInterface, which provides an abstract interface for
    file system operations such as folder creation, removal of empty folders, and file listing.
""" 

from abc import ABC, abstractmethod

class FileSystemInterface(ABC):
    @abstractmethod
    def validate_and_create_folder(self, folder_path: str, log_files = None) -> bool:
        pass

    @abstractmethod
    def remove_empty_folders(self, path: str, log_files = None) -> None:
        pass

    @abstractmethod
    def get_all_files(self, folder: str) -> list[str]:
        pass
