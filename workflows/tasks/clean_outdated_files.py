"""
File Cleanup Utility

This module provides functionality to clean outdated files based on a standardized
naming convention: <filename>-<date-in-ISO-format>. It helps maintain storage efficiency
by automatically identifying and removing old files that match specific patterns.

Key features:
1. Date-based file identification and cleanup
2. Configurable through command-line arguments
3. Support for multiple file hints/patterns
4. Optional silent mode for automated workflows
5. Invertible cleaning logic to target today's files instead of older ones

The module works with files that follow a consistent naming pattern where the date
is embedded in ISO format. It provides a command-line interface that allows customization
of the cleaning behaviour, including target folder, file extensions, and matching patterns.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import os

# Local implementations
from core.utils.strings import match_list_elem_date
from core.utils.file_system import search_files_by_ext


def clean_outdated(
    hints_: list[str],
    file_lst: list[str],
    folder: str,
    silent: bool = False,
    invert_clean: bool = False,
) -> None:
    """Match and identify outdated files, and report to the user which files are
    being deleted.

    :param hints_: ``list[str]`` possible filename hints of the files to be deleted.
    :param file_lst: ``list[str]`` file list filtered by extension (externally)
    :param folder: ``str`` folder that will be examined by the function.
    :param silent: ``bool`` suppresses the debugging output.
    :param invert_clean: ``bool`` Cleans files matching today's date.
    :return: ``None``
    """
    reverse = True if not invert_clean else False
    os.chdir(folder)
    outdated = match_list_elem_date(
        hints_, file_lst, ignore_case=True, strict=True, reverse=reverse
    )
    for file in outdated:
        file_path = os.path.abspath(file)

        if os.path.exists(file_path):
            if not silent:
                print(f"Removing {file_path}")
            os.remove(file_path)
        else:
            if not silent:
                print(f"File {file_path} not found")

    if not silent:
        if len(outdated) != 0:
            print(f"{'DONE':=^35}")
        else:
            print("Nothing to clean...")

    return None


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Clean local outdated files")

    arg_parser.add_argument(
        "--folder",
        action="store",
        type=str,
        help="Relative or absolute path to your directory",
    )

    arg_parser.add_argument(
        "--ext",
        action="store",
        type=str,
        help="extension",
    )

    arg_parser.add_argument(
        "--hints",
        type=str,
        nargs="+",
        help="""This parameter receives the first word of the partner offer for matching.
                Pass in multiple values separated by space.""",
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        default=False,
        help="Set if you want to remove the specific files in the parent dir.",
    )

    arg_parser.add_argument(
        "--invert",
        action="store_true",
        default=False,
        help="Clean today's matching files and leaves outdated ones untouched.",
    )

    arg_parser.add_argument(
        "--silent",
        action="store_true",
        default=False,
        help="Omit console output from file operations.",
    )
    args = arg_parser.parse_args()

    hints = list(args.hints)

    # Filter the files to be deleted by their file extension.
    files = search_files_by_ext(args.ext, args.folder, parent=args.parent)

    clean_outdated(
        hints, files, args.folder, invert_clean=args.invert, silent=args.silent
    )
