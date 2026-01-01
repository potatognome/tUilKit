# Lib/site-packages/tUilKit/utils/output.py 
"""
Contains functions for log files and displaying text output in the terminal using ANSI sequences to colour code output.
"""
import re
from datetime import datetime
import sys
import os
from abc import ABC, abstractmethod

# Add the base directory of the project to the system path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..\\'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.dict.DICT_COLOURS import RGB
from tUilKit.dict.DICT_CODES import ESCAPES, COMMANDS
from tUilKit.interfaces.logger_interface import LoggerInterface
from tUilKit.interfaces.colour_interface import ColourInterface
from tUilKit.config.config import ConfigLoader

# ANSI ESCAPE CODE PREFIXES for colour coding f-strings
SET_FG_COLOUR = ESCAPES['OCTAL'] + COMMANDS['FGC']
SET_BG_COLOUR = ESCAPES['OCTAL'] + COMMANDS['BGC']
ANSI_RESET = ESCAPES['OCTAL'] + COMMANDS['RESET']

config_loader = ConfigLoader()

LOG_FILES = config_loader.global_config.get("LOG_FILES", {})

class ColourManager(ColourInterface):
    def __init__(self, colour_config: dict):
        self.ANSI_FG_COLOUR_SET = {}
        self.ANSI_BG_COLOUR_SET = {}
        for key, value in colour_config['COLOUR_KEY'].items():
            if '|' in value:
                fg, bg = value.split('|', 1)
            else:
                fg = value
                bg = 'BLACK'
            if fg in RGB:
                self.ANSI_FG_COLOUR_SET[key] = f"\033[38;2;{RGB[fg]}"
            if bg in RGB:
                self.ANSI_BG_COLOUR_SET[key] = f"\033[48;2;{RGB[bg]}"
        self.ANSI_FG_COLOUR_SET['RESET'] = ANSI_RESET

    def get_fg_colour(self, colour_code: str) -> str:
        return self.ANSI_FG_COLOUR_SET.get(colour_code, "\033[38;2;190;190;190m")

    def get_bg_colour(self, colour_code: str) -> str:
        return self.ANSI_BG_COLOUR_SET.get(colour_code, "\033[48;2;0;0;0m")

    def strip_ansi(self, fstring: str) -> str:
        import re
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub('', fstring)

    def colour_fstr(self, *args, bg=None, separator=" ") -> str:
        """
        Usage:
            colour_fstr("RED", "Some text", "GREEN", "Other text", bg="YELLOW")
        If bg is provided, applies the background colour to the whole string.
        Now supports per-key background: keys with fg|bg in config set both fg and bg.
        """
        result = ""
        FG_RESET = "\033[38;2;190;190;190m"
        BG_RESET = "\033[49m"
        current_fg = FG_RESET
        current_bg = ""
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                arg = ', '.join(map(str, arg))
            else:
                arg = str(arg)
            if arg in self.ANSI_FG_COLOUR_SET:
                current_fg = self.ANSI_FG_COLOUR_SET[arg]
                current_bg = self.ANSI_BG_COLOUR_SET.get(arg, "")
            elif arg.startswith('BG_'):
                current_bg = self.get_bg_colour(arg[3:])
            else:
                result += f"{current_bg}{current_fg}{arg}"
                if i != len(args) - 1:
                    result += separator
        result += FG_RESET + BG_RESET
        return result

    def colour_path(self, path: str) -> str:
        """
        Returns a colour-formatted string for a file path using COLOUR_KEYs:
        DRIVE, BASEFOLDER, MIDFOLDER, THISFOLDER, FILE.
        If only one folder, uses DRIVE and BASEFOLDER.
        If two folders, uses DRIVE, BASEFOLDER, THISFOLDER.
        If more, uses DRIVE, BASEFOLDER, MIDFOLDER(s), THISFOLDER.
        # Exposed for external use in tUilKit: Use when displaying full pathnames with color coding.
        """
        import os
        drive, tail = os.path.splitdrive(path)
        folders, filename = os.path.split(tail)
        folders = folders.strip(os.sep)
        folder_parts = folders.split(os.sep) if folders else []
        n = len(folder_parts)

        parts = []
        if drive:
            parts.append(("DRIVE", drive + os.sep))
        if n == 1 and folder_parts:
            parts.append(("BASEFOLDER", folder_parts[0] + os.sep))
        elif n == 2:
            parts.append(("BASEFOLDER", folder_parts[0] + os.sep))
            parts.append(("THISFOLDER", folder_parts[1] + os.sep))
        elif n > 2:
            parts.append(("BASEFOLDER", folder_parts[0] + os.sep))
            for mid in folder_parts[1:-1]:
                parts.append(("MIDFOLDER", mid + os.sep))
            parts.append(("THISFOLDER", folder_parts[-1] + os.sep))
        if filename:
            parts.append(("FILE", filename))

        colour_args = []
        for key, value in parts:
            colour_args.extend([f"!{key.lower()}", value])
        return self.colour_fstr(*colour_args, separator="")

    def interpret_codes(self, text: str) -> str:
        import re
        def replace_code(match):
            code = match.group(1)
            return self.ANSI_FG_COLOUR_SET.get(code, f"{{{code}}}")  # if not found, leave as {code}
        return re.sub(r'\{(\w+)\}', replace_code, text)


class Logger(LoggerInterface):
    def __init__(self, colour_manager: ColourManager, log_files=None):
        self.Colour_Mgr = colour_manager
        self.log_files = log_files or LOG_FILES.copy()
        self._log_queue = []
        # Load log categories from config, with fallback defaults
        self.LOG_KEYS = config_loader.global_config.get("LOG_CATEGORIES", {
            "default": ["MASTER", "SESSION"],
            "error": ["ERROR", "SESSION", "MASTER"],
            "fs": ["MASTER", "SESSION", "FS"],
            "init": ["INIT", "SESSION", "MASTER"]
        })
        # Clean the session log on initialization to ensure it only contains the current execution
        self._clean_session_log()

    def _clean_session_log(self):
        """
        Clears the session log file to ensure it only contains logs from the current execution.
        """
        session_log = self.log_files.get("SESSION")
        if session_log:
            try:
                # Ensure the log directory exists
                log_dir = os.path.dirname(session_log)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                # Clear the session log file
                with open(session_log, 'w', encoding='utf-8') as log:
                    log.write("")  # Clear the file
            except Exception as e:
                # If we can't clear the session log, log to terminal only (avoid recursion)
                print(f"Warning: Could not clear session log {session_log}: {e}")

    def _get_log_files(self, category):
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

    @staticmethod
    def split_time_string(time_string: str) -> tuple[str, str]:
        parts = time_string.strip().split()
        if len(parts) >= 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return "", ""

    def log_message(self, message: str, log_files = None, end: str = "\n", log_to: str = "both", time_stamp: bool = True):
        """
        log_files: list of str or str or None
        log_to: "both", "file", "term", "queue"
        time_stamp: if True, prepend date and time to the message
        """
        if isinstance(log_files, str):
            log_files = [log_files]
        elif log_files is None:
            log_files = []
        
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            message = f"{date} {time} {message}"
        
        if log_to in ("file", "both") and log_files:
            for log_file in log_files:
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    # Queue the message if the log folder doesn't exist
                    self._log_queue.append((message, log_file, end))
                    if log_to == "file":
                        continue
                else:
                    self.flush_log_queue(log_file)
                    if not os.path.exists(log_file):
                        self._log_queue.append((f"Log file created: {log_file}", log_file, "\n"))
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(self.Colour_Mgr.strip_ansi(message) + end)
        
        if log_to in ("term", "both"):
            print(message, end=end)
        
        if log_to == "queue" and log_files:
            for log_file in log_files:
                self._log_queue.append((message, log_file, end))

    def flush_log_queue(self, log_file: str):
        log_dir = os.path.dirname(log_file)
        if os.path.exists(log_dir):
            with open(log_file, 'a', encoding='utf-8') as log:
                for msg, lf, end in self._log_queue:
                    if lf == log_file:
                        log.write(self.Colour_Mgr.strip_ansi(msg) + end)
            # Remove flushed messages
            self._log_queue = [item for item in self._log_queue if item[1] != log_file]

    def colour_log(self, *args, category="default", spacer=0, log_files=None, end="\n", log_to="both", time_stamp=True):
        # Exposed for external use in tUilKit: Use to replace print(f"") with colored, timestamped logging.
        category_files = self._get_log_files(category)
        if log_files is None:
            effective_log_files = category_files
        else:
            if isinstance(log_files, str):
                log_files = [log_files]
            effective_log_files = list(set(category_files + log_files))
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = ("!date", date, "!time", time)
        else:
            prefix = ()
        if spacer > 0:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, f"{' ' * spacer}", *args)
        else:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, *args)
        # Pass time_stamp=False so log_message does not add its own (uncoloured) timestamp
        self.log_message(coloured_message, log_files=effective_log_files, end=end, log_to=log_to, time_stamp=False)

    def colour_log_text(self, message: str, log_files=None, log_to="both", time_stamp=True):
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = f"{date} {time} "
        else:
            prefix = ""
        coloured_message = prefix + self.Colour_Mgr.interpret_codes(message)
        self.log_message(coloured_message, log_files=log_files, log_to=log_to, time_stamp=False)

    def log_exception(self, description: str, exception: Exception, category="error", log_files=None, log_to: str = "both") -> None:
        # Exposed for external use in tUilKit: Use for logging exceptions with colored formatting.
        category_files = self._get_log_files(category)
        if log_files is None:
            effective_log_files = category_files
        else:
            if isinstance(log_files, str):
                log_files = [log_files]
            effective_log_files = list(set(category_files + log_files))
        self.colour_log("", log_files=effective_log_files, time_stamp=False, log_to=log_to)
        self.colour_log("", log_files=effective_log_files, time_stamp=False, log_to=log_to)
        self.colour_log("!error", "UNEXPECTED ERROR:", "!info", description, "!error", str(exception), log_files=effective_log_files, log_to=log_to)

    def log_done(self, log_files = None, end: str = "\n", log_to: str = "both", time_stamp=True):
        self.colour_log("!done", "Done!", category="default", log_files=log_files, end=end, log_to=log_to, time_stamp=time_stamp)

    def log_column_list(self, df, filename, log_files=None, log_to: str = "both"):
        self.colour_log(
            "!path", os.path.dirname(filename), "/",
            "!file", os.path.basename(filename),
            ": ",
            "!info", "Columns:",
            "!output", df.columns.tolist(),
            category="default",
            log_files=log_files,
            log_to=log_to)

    def print_rainbow_row(self, pattern="X-O-", spacer=0, log_files=None, end="\n", log_to="both"):
        bright_colours = [
            'RED', 'CRIMSON', 'ORANGE', 'CORAL', 'GOLD',
            'YELLOW', 'CHARTREUSE', 'GREEN', 'CYAN',
            'BLUE', 'INDIGO', 'VIOLET', 'MAGENTA'
        ]
        self.log_message(f"{' ' * spacer}", log_files=log_files, end="", log_to=log_to, time_stamp=False)
        rainbow_colours = bright_colours + bright_colours[::-1][1:-1]
        for colour in rainbow_colours:
            self.log_message(self.Colour_Mgr.colour_fstr(colour, pattern), log_files=log_files, end="", log_to=log_to, time_stamp=False)
        self.log_message(self.Colour_Mgr.colour_fstr("RED", f"{pattern}"[0]), log_files=log_files, end=end, log_to=log_to, time_stamp=False)

    def print_top_border(self, pattern, length, index=0, log_files=None, border_colour='!proc', log_to: str = "both"):
        top = pattern['TOP'][index] * (length // len(pattern['TOP'][index]))
        self.colour_log(border_colour, f" {top}", category="default", log_files=log_files, log_to=log_to)

    def print_text_line(self, text, pattern, length, index=0, log_files=None, border_colour='!proc', text_colour='!proc', log_to: str = "both"):
        left = pattern['LEFT'][index]
        right = pattern['RIGHT'][index]
        inner_text_length = len(left) + len(text) + len(right)
        trailing_space_length = length - inner_text_length - 2
        text_line_args = [border_colour, left, text_colour, text, f"{' ' * trailing_space_length}", border_colour, right]
        self.colour_log(*text_line_args, category="default", log_files=log_files, log_to=log_to)

    def print_bottom_border(self, pattern, length, index=0, log_files=None, border_colour='!proc', log_to: str = "both"):
        bottom = pattern['BOTTOM'][index] * (length // len(pattern['BOTTOM'][index]))
        self.colour_log(border_colour, f" {bottom}", category="default", log_files=log_files, log_to=log_to)

    def apply_border(self, text, pattern, total_length=None, index=0, log_files=None, border_colour='!proc', text_colour='!proc', log_to: str = "both"):
        # Exposed for external use in tUilKit: Use for highlighting header text in the terminal with borders.
        inner_text_length = len(pattern['LEFT'][index]) + len(text) + len(pattern['RIGHT'][index])
        if total_length and total_length > inner_text_length:
            length = total_length
        else:
            length = inner_text_length
        self.print_top_border(pattern, length, index, log_files=log_files, border_colour=border_colour, log_to=log_to)
        self.print_text_line(text, pattern, length, index, log_files=log_files, border_colour=border_colour, text_colour=text_colour, log_to=log_to)
        self.print_bottom_border(pattern, length, index, log_files=log_files, border_colour=border_colour, log_to=log_to)
