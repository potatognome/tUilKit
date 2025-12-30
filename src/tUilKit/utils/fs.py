# Lib/site-packages/tUilKit/utils/fs.py
"""
Contains functions for managing files, folders and path names.
Provides implementation of FileSystemInterface with logging support using colour keys.
"""

import shutil
import os
from tUilKit.interfaces.file_system_interface import FileSystemInterface

class FileSystem(FileSystemInterface):
    def __init__(self, logger, log_files=None):
        """
        Initializes the FileSystem with a logger and optional log_files dict.
        """
        super().__init__(logger, log_files)
        # Define log categories for selective logging
        self.LOG_KEYS = {
            "default": ["MASTER", "SESSION"],
            "error": ["ERROR", "SESSION", "MASTER"],
            "fs": ["MASTER", "SESSION", "FS"]
        }

    def _get_log_files(self, category="default"):
        """
        Returns a list of log file paths for the given category or categories.
        category can be str or list of str.
        """
        if isinstance(category, str):
            categories = [category]
        elif isinstance(category, list):
            categories = category
        else:
            categories = ["default"]
        all_files = []
        for cat in categories:
            keys = self.LOG_KEYS.get(cat, self.LOG_KEYS["default"])
            all_files.extend([self.log_files.get(key) for key in keys if self.log_files.get(key)])
        return list(set(all_files))  # unique

    def validate_and_create_folder(self, folder_path: str, log: bool = True, log_to: str = "both", category="fs") -> bool:
        """
        Validates and creates a folder if it does not exist.
        Logs the action using colour keys: !try for attempt, !create for action, !path for the path, !pass for success.
        """
        log_files = self._get_log_files(category)
        if not os.path.exists(folder_path):
            if self.logger and log:
                self.logger.colour_log("!try", "Attempting to", "!create", "create folder:", "!path", folder_path, log_files=log_files, log_to=log_to, end="..... ")
            try:
                os.makedirs(folder_path, exist_ok=True)
                if self.logger and log:
                    self.logger.colour_log("!pass", "DONE!", log_files=log_files, log_to=log_to, time_stamp=False)
            except Exception as e:
                if self.logger and log:
                    self.logger.log_exception("!error", "Could not create folder: ", e, log_files=self._get_log_files("error"), log_to=log_to)
                return False
        return True

    def remove_empty_folders(self, path: str, log: bool = True, category="fs") -> None:
        """
        Recursively removes empty folders under the given path.
        Logs each removal using !pass and !path colour keys.
        """
        log_files = self._get_log_files(category)
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)  
                    except Exception as e:
                        if self.logger and log:
                            self.logger.log_exception("!error", "Could not remove folder: ", e, log_files=self._get_log_files("error"))
                    if self.logger and log:
                        self.logger.colour_log("!pass", "Removed empty folder:", "!path", dir_path, log_files=log_files)

    def get_all_files(self, folder: str) -> list[str]:
        """
        Returns a list of all files (not directories) in the specified folder.
        """
        return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    def validate_extension(self, fullfilepath: str, extension: str) -> str:
        """
        Ensures the filepath has the specified extension.
        If not, appends it.
        """
        base, ext = os.path.splitext(fullfilepath)
        if ext.lower() != extension.lower():
            fullfilepath += extension
        return fullfilepath

    def no_overwrite(self, fullfilepath: str, max_count=None, log: bool = True, category="fs") -> str:
        """
        Guarantees that a newly generated file will not overwrite an existing file.
        Generates a non-overwriting filename by appending a counter in parentheses.
        If max_count is reached, returns the oldest file.
        Logs using !warn for max count, !done for success, with !path and !file keys.
        Use if you are not using version control and want to avoid overwriting files.
        """
        log_files = self._get_log_files(category)
        base, ext = os.path.splitext(fullfilepath)
        counter = 1
        new_fullfilepath = fullfilepath
        oldest_file = fullfilepath
        oldest_timestamp = os.path.getmtime(fullfilepath) if os.path.exists(fullfilepath) else float('inf')
        
        while os.path.exists(new_fullfilepath):
            new_fullfilepath = f"{base}({counter}){ext}"
            if os.path.exists(new_fullfilepath):
                file_timestamp = os.path.getmtime(new_fullfilepath)
                if file_timestamp < oldest_timestamp:
                    oldest_timestamp = file_timestamp
                    oldest_file = new_fullfilepath
            counter += 1
            if max_count and counter > max_count:
                if self.logger and log:
                    self.logger.colour_log(
                        "!warn",
                        "Max count reached, returning oldest file:",
                        "!path", os.path.dirname(oldest_file),
                        "!file", os.path.basename(oldest_file),
                        log_files=log_files
                    )
                return oldest_file
        if self.logger and log:
            self.logger.colour_log(
                "!done",
                "No-overwrite filename generated:",
                "!path", os.path.dirname(new_fullfilepath),
                "!file", os.path.basename(new_fullfilepath),
                log_files=log_files
            )
        return new_fullfilepath

    def backup_and_replace(self, full_pathname: str, backup_full_pathname: str, log: bool = True, category="fs") -> str:
        """
        Backs up the file and replaces it with an empty file.
        Logs using !done for success, !path and !file for paths.
        """
        log_files = self._get_log_files(category)
        if full_pathname and backup_full_pathname:
            if os.path.exists(full_pathname):
                shutil.copy2(full_pathname, backup_full_pathname)
                if self.logger and log:
                    self.logger.colour_log("!done", "Backup created:", "!path", os.path.dirname(backup_full_pathname), "!file", os.path.basename(backup_full_pathname), log_files=log_files)
                try:
                    with open(full_pathname, 'w') as file:
                        file.write('')
                    if self.logger and log:
                        self.logger.colour_log("!done", "File replaced:", "!path", os.path.dirname(full_pathname), "!file", os.path.basename(full_pathname), log_files=log_files)
                except Exception as e:
                    if self.logger and log:
                        self.logger.log_exception("!error", "Generated Exception ", e, log_files=self._get_log_files("error"))
        return full_pathname

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes a filename by replacing invalid characters with safe alternatives.
        """
        invalid_chars = {
            ':' : '-',
            '\\' : '',
            '/' : '',
            '?' : '',
            '*' : '',
            '<' : '',
            '>' : '',
            '|' : '',
        }
        new_filename = filename
        for char, replacement in invalid_chars.items():
            new_filename = new_filename.replace(char, replacement)
        return new_filename
