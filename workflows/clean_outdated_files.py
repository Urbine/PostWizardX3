"""
Clean outdated files based on the named convention <filename>-<date-in-ISO-format>
Accepts CLI arguments to fine-tune its cleaning behaviour and scope.

"""

# Std Library
import argparse
import os

# Local implementations
import common


def clean_outdated(hints_: list[str],
                   file_lst: list[str], folder: str) -> None:
    """ Match and identify outdated files, and report to the user which files are
        being deleted.
    :param hints_: ``list[str]`` possible filename hints of the files to be deleted.
    :param file_lst: ``list[str]`` file list filtered by extension (externally)
    :param folder: ``str`` folder that will be examined by the function.
    :return: ``None``
    """
    os.chdir(folder)
    outdated = common.match_list_elem_date(
        hints_, file_lst, ignore_case=True, strict=True, reverse=True
    )
    for file in outdated:
        print(f'Removing {os.path.abspath(file)}')
        os.remove(file)

    if len(outdated) != 0:
        print(f"{'DONE':=^35}")
    else:
        print('Nothing to clean...')

    return None


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description="Clean local outdated files")

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
        nargs='+',
        help="""This parameter receives the first word of the partner offer for matching.
                Pass in multiple values separated by space.""",
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        default=False,
        help="Set if you want to remove the specific files in the parent dir.",
    )

    args = arg_parser.parse_args()

    hints = list(args.hints)

    # Filter the files to be deleted by extension.
    files = common.search_files_by_ext(
        args.ext, args.folder, parent=args.parent)

    clean_outdated(hints, files, args.folder)
