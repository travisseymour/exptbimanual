"""
This file is part of the exptbimanual source code.
Copyright (C) 2025 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from rich import print
import os
import sys
from pathlib import Path
from fastnumbers import isfloat
from loguru import logger as log
import platform
import warnings
from functools import wraps

"""
Miscellaneous utilities
"""

OS = platform.system()


def frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


if frozen():
    log.level("INFO")


def addroot(currpath):
    main_file_location = Path(__file__).parent.absolute()
    return str(Path(main_file_location, currpath))


def ospath(path_str: str) -> str:
    if OS == "Windows":
        return str(Path(path_str).absolute())
    else:
        return path_str



def is_numeric(value) -> bool:
    return isfloat(value)

def ignore_warnings(f):
    # https://stackoverflow.com/questions/879173
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response

    return inner



# Function to determine the available display server
def set_qt_platform():
    # Check if the operating system is Linux
    if platform.system() == 'Linux':
        if 'WAYLAND_DISPLAY' in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'wayland'
            print("Using Wayland as the display server.")
        else:
            os.environ['QT_QPA_PLATFORM'] = 'xcb'
            print("Using X11 (xcb) as the display server.")
    elif platform.system() == 'Windows':
        # Windows typically does not require setting this
        pass
    elif platform.system() == 'Darwin':  # macOS
        # macOS typically does not require setting this
        pass
    else:
        # Optionally handle other operating systems or set a default
        os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Default to X11 for non-Linux







def normalize_invisible_chars(text: str) -> str:
    replacements = {
        "\u2029": "\n",  # paragraph separator
        "\u2028": "\n",  # line separator
        "\u00a0": " ",  # non-breaking space
        "\u200b": "",  # zero-width space
        "\u200c": "",  # zero-width non-joiner
        "\u200d": "",  # zero-width joiner
    }
    for src, target in replacements.items():
        text = text.replace(src, target)
    return text




def stop_if_not_linux(app_name: str):
    if OS != 'Linux':
        log.error(f'{app_name} Only Works on Linux Operating Systems, not "{OS}"')
        sys.exit()