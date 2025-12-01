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
colour_config = config_loader.load_config(config_loader.get_json_path('COLOURS.json'))
ANSI_FG_COLOUR_SET = {key: f"{ESCAPES['OCTAL']}{COMMANDS['FGC']}{RGB[value]}" for key, value in colour_config['COLOUR_KEY'].items()}


class ColourManager(ColourInterface):
    def __init__(self, colour_config: dict):
        # Foreground colour codes
        self.ANSI_FG_COLOUR_SET = {
            key: f"\033[38;2;{RGB[value]}" for key, value in colour_config['COLOUR_KEY'].items() if value in RGB
        }
        # Background colour codes
        self.ANSI_BG_COLOUR_SET = {
            key: f"\033[48;2;{RGB[value]}" for key, value in colour_config['COLOUR_KEY'].items() if value in RGB
        }

    def get_fg_colour(self, colour_code: str) -> str:
        return self.ANSI_FG_COLOUR_SET.get(colour_code, "\033[38;2;190;190;190m")

    def get_bg_colour(self, colour_code: str) -> str:
        return self.ANSI_BG_COLOUR_SET.get(colour_code, "\033[48;2;0;0;0m")

    def strip_ansi(self, fstring: str) -> str:
        import re
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub('', fstring)

    def colour_fstr(self, *args, bg=None) -> str:
        """
        Usage:
            colour_fstr("RED", "Some text", "GREEN", "Other text", bg="YELLOW")
        If bg is provided, applies the background colour to the whole string.
        """
        result = ""
        FG_RESET = "\033[38;2;190;190;190m"
        BG_RESET = "\033[49m"
        current_colour = FG_RESET
        bg_colour = self.get_bg_colour(bg) if bg else ""
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                arg = ', '.join(map(str, arg))
            if arg in self.ANSI_FG_COLOUR_SET:
                current_colour = self.get_fg_colour(arg)
            else:
                result += f"{bg_colour}{current_colour}{arg}"
                if i != len(args) - 1:
                    result += " "
        result += FG_RESET + BG_RESET
        return result

    def colour_path(self, path: str) -> str:
        """
        Returns a colour-formatted string for a file path using COLOUR_KEYs:
        DRIVE, BASEFOLDER, MIDFOLDER, THISFOLDER, FILE.
        If only one folder, uses DRIVE and BASEFOLDER.
        If two folders, uses DRIVE, BASEFOLDER, THISFOLDER.
        If more, uses DRIVE, BASEFOLDER, MIDFOLDER(s), THISFOLDER.
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
            colour_args.extend([key, value])
        return self.colour_fstr(*colour_args)


class Logger(LoggerInterface):
    def __init__(self, colour_manager: ColourManager):
        self.Colour_Mgr = colour_manager
        self._log_queue = []

    @staticmethod
    def split_time_string(time_string: str) -> tuple[str, str]:
        parts = time_string.strip().split()
        if len(parts) >= 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return "", ""

    def log_message(self, message: str, log_file = None, end: str = "\n", log_to: str = "both", time_stamp: bool = True):
        """
        log_to: DEFAULT="both", 'file', 'term', 'queue'
        time_stamp: if True, prepend date and time to the message
        """
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            message = f"{date} {time} {message}"
        if log_to in ("file", "both") and log_file:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                # Queue the message if the log folder doesn't exist
                self._log_queue.append((message, log_file, end))
                if log_to == "file":
                    return
            else:
                self.flush_log_queue(log_file)
                with open(log_file, 'a') as log:
                    log.write(self.Colour_Mgr.strip_ansi(message) + end)
        if log_to in ("term", "both"):
            print(message, end=end)
        if log_to == "queue" and log_file:
            self._log_queue.append((message, log_file, end))

    def flush_log_queue(self, log_file: str):
        log_dir = os.path.dirname(log_file)
        if os.path.exists(log_dir):
            with open(log_file, 'a') as log:
                for msg, lf, end in self._log_queue:
                    if lf == log_file:
                        log.write(self.Colour_Mgr.strip_ansi(msg) + end)
            # Remove flushed messages
            self._log_queue = [item for item in self._log_queue if item[1] != log_file]

    def colour_log(self, *args, spacer=0, log_file=None, end="\n", log_to="both", time_stamp=True):
        if time_stamp:
            date, time = self.split_time_string(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            prefix = ("DATE", date, "TIME", time)
        else:
            prefix = ()
        if spacer > 0:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, f"{' ' * spacer}", *args)
        else:
            coloured_message = self.Colour_Mgr.colour_fstr(*prefix, *args)
        # Pass time_stamp=False so log_message does not add its own (uncoloured) timestamp
        self.log_message(coloured_message, log_file=log_file, end=end, log_to=log_to, time_stamp=False)

    def log_exception(self, description: str, exception: Exception, log_file = None, log_to: str = "both") -> None:
        self.colour_log("", log_file=log_file, time_stamp=False, log_to=log_to)
        self.colour_log("ERROR", "UNEXPECTED ERROR:", "INFO", description, "ERROR", str(exception), log_file=log_file, log_to=log_to)

    def log_done(self, log_file = None, end: str = "\n", log_to: str = "both", time_stamp=True):
        self.colour_log("DONE", "Done!", log_file=log_file, end=end, log_to=log_to, time_stamp=time_stamp)

    def log_column_list(self, df, filename, log_file=None, log_to: str = "both"):
        self.colour_log(
            "PATH", os.path.dirname(filename), "/",
            "FILE", os.path.basename(filename),
            ": ",
            "INFO", "Columns:",
            "OUTPUT", df.columns.tolist(),
            log_file=log_file,
            log_to=log_to)

    def print_rainbow_row(self, pattern="X-O-", spacer=0, log_file=None, end="\n", log_to="both"):
        bright_colours = [
            'RED', 'CRIMSON', 'ORANGE', 'CORAL', 'GOLD',
            'YELLOW', 'CHARTREUSE', 'GREEN', 'CYAN',
            'BLUE', 'INDIGO', 'VIOLET', 'MAGENTA'
        ]
        self.log_message(f"{' ' * spacer}", log_file=log_file, end="", log_to=log_to, time_stamp=False)
        rainbow_colours = bright_colours + bright_colours[::-1][1:-1]
        for colour in rainbow_colours:
            self.log_message(self.Colour_Mgr.colour_fstr(colour, pattern), log_file=log_file, end="", log_to=log_to, time_stamp=False)
        self.log_message(self.Colour_Mgr.colour_fstr("RED", f"{pattern}"[0]), log_file=log_file, end=end, log_to=log_to, time_stamp=False)

    def print_top_border(self, pattern, length, index=0, log_file=None, border_colour='CANARY', log_to: str = "both"):
        top = pattern['TOP'][index] * (length // len(pattern['TOP'][index]))
        self.colour_log(border_colour, f" {top}", log_file=log_file, log_to=log_to)

    def print_text_line(self, text, pattern, length, index=0, log_file=None, border_colour='GREEN', text_colour='RESET', log_to: str = "both"):
        left = pattern['LEFT'][index]
        right = pattern['RIGHT'][index]
        inner_text_length = len(left) + len(text) + len(right)
        trailing_space_length = length - inner_text_length - 2
        text_line_args = [border_colour, left, text_colour, text, f"{' ' * trailing_space_length}", border_colour, right]
        self.colour_log(*text_line_args, log_file=log_file, log_to=log_to)

    def print_bottom_border(self, pattern, length, index=0, log_file=None, border_colour='BLUE', log_to: str = "both"):
        bottom = pattern['BOTTOM'][index] * (length // len(pattern['BOTTOM'][index]))
        self.colour_log(border_colour, f" {bottom}", log_file=log_file, log_to=log_to)

    def apply_border(self, text, pattern, total_length=None, index=0, log_file=None, border_colour='RESET', text_colour='GREEN', log_to: str = "both"):
        inner_text_length = len(pattern['LEFT'][index]) + len(text) + len(pattern['RIGHT'][index])
        if total_length and total_length > inner_text_length:
            length = total_length
        else:
            length = inner_text_length
        self.print_top_border(pattern, length, index, log_file=log_file, border_colour=border_colour, log_to=log_to)
        self.print_text_line(text, pattern, length, index, log_file=log_file, border_colour=border_colour, text_colour=text_colour, log_to=log_to)
        self.print_bottom_border(pattern, length, index, log_file=log_file, border_colour=border_colour, log_to=log_to)
