"""
System Shell Utilities

This module contains functions to work with processes inside a system shell.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
import subprocess
from pathlib import Path

from core.utils.strings import clean_filename


def imagick(img_path: Path | str, quality: int, target: str) -> None:
    """Convert images to a target file format via the ImageMagick library
    installed in the system.

    The ``convert`` command is deprecated in ImageMagick 7 (IMv7).
    Therefore, ``magick`` or ``magick convert`` are the modern way.
    This means that, if this command does not work in your platform, you need to either
    modify this to ``convert`` instead of the modern command or just update your IM version.
    However, if you work with PNG files with transparent background, don't use an older version
    of IM.That said, it won't look good, but it depends on what you need.

    :param img_path: ``Path`` - Image URI
    :param quality: ``int`` image quality (0 to 100)
    :param target: ``str`` target file format
    :return: ``None``
    """
    if os.path.exists(img_path):
        img = os.path.split(img_path)
        get_file = lambda dirpath: clean_filename(dirpath[1], target)
        subprocess.Popen(
            f"magick {img} -quality {quality} {os.path.join(img[0], get_file(img))}",
            shell=True,
        ).wait()
    else:
        raise FileNotFoundError(f"File {img_path} was not found!")
    return None


def clean_console() -> None:
    """Clear console text in POSIX (Unix/Linux/macOS) or Windows.

    :return: ``None``
    :raise: ``NotImplementedError`` as an edge case
    """
    if os.name == "posix":
        os.system("clear")
    elif os.name == "nt":
        os.system("cls")
    else:
        raise NotImplementedError
