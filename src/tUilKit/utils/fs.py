# Lib/site-packages/tUilKit/utils/fs.py
"""
Contains functions for managing files, folders and path names.
""" 
import shutil
import os
from tUilKit.interfaces.file_system_interface import FileSystemInterface

class FileSystem(FileSystemInterface):
    def __init__(self, logger):
        self.logger = logger

    def validate_and_create_folder(self, folder_path: str, log_file = None, log: bool = True, log_to: str = "both") -> bool:
        if not os.path.exists(folder_path):
            if self.logger and log:
                self.logger.colour_log("CMD", f"Attempting to create folder: {folder_path}", log_file=log_file, log_to=log_to)
            try:
                os.makedirs(folder_path, exist_ok=True)
                if self.logger and log:
                    self.logger.colour_log("DONE", f"Created folder: {folder_path}", log_file=log_file, log_to=log_to)
            except Exception as e:
                if self.logger and log:
                    self.logger.log_exception("Could not create folder: ", e, log_file=log_file, log_to=log_to)
                exit(1)
        return True

    def remove_empty_folders(self, path: str, log_file = None, log: bool = True) -> None:
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    if self.logger and log:
                        self.logger.colour_log("DONE", f"Removed empty folder: {dir_path}", log_file=log_file)

    def get_all_files(self, folder: str) -> list[str]:
        return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    def validate_extension(self, fullfilepath: str, extension: str) -> str:
        base, ext = os.path.splitext(fullfilepath)
        if ext.lower() != extension.lower():
            fullfilepath += extension
        return fullfilepath

    def no_overwrite(self, fullfilepath: str, max_count=None, log_file=None, log: bool = True) -> str:
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
                        "WARN",
                        f"Max count reached, returning oldest file: {os.path.dirname(oldest_file)}/{os.path.basename(oldest_file)}",
                        log_file=log_file
                    )
                return oldest_file
        if self.logger and log:
            self.logger.colour_log(
                "DONE",
                f"No-overwrite filename generated: {os.path.dirname(new_fullfilepath)}/{os.path.basename(new_fullfilepath)}",
                log_file=log_file
            )
        return new_fullfilepath

    def backup_and_replace(self, full_pathname: str, backup_full_pathname: str, log_file=None, log: bool = True) -> str:
        if full_pathname and backup_full_pathname:
            if os.path.exists(full_pathname):
                shutil.copy2(full_pathname, backup_full_pathname)
                if self.logger and log:
                    self.logger.colour_log("DONE", f"Backup created: {backup_full_pathname}", log_file=log_file)
                try:
                    with open(full_pathname, 'w') as file:
                        file.write('')
                    if self.logger and log:
                        self.logger.colour_log("DONE", f"File replaced: {full_pathname}", log_file=log_file)
                except Exception as e:
                    if self.logger and log:
                        self.logger.log_exception("Generated Exception ", e, log_file=log_file)
        return full_pathname

    def sanitize_filename(self, filename: str) -> str:
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
