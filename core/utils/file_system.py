"""
File System Utilities
This module contains functions to work with files and directories.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import csv
import datetime
import glob
import importlib.resources
import json
import logging
import os
import random
import shutil
import sqlite3
import stat
import subprocess
from collections import deque
from pathlib import Path
from typing import Optional, Any, List, Dict, Deque, Union


# Local imports
from core.models.file_system import ApplicationPath
from core.utils.parsers import parse_client_config
from core.utils.strings import match_list_single, generate_random_str, clean_filename
from core.exceptions.config_exceptions import ConfigFileNotFound
from core.exceptions.util_exceptions import (
    UnavailableLoggingDirectory,
    UnsupportedPlatform,
)


def clean_file_cache(cache_folder: str | Path, file_ext: str) -> None:
    """The purpose of this function is simple: cleaning remaining temporary files once the job control
    has used them; this is especially useful when dealing with thumbnails.

    :param cache_folder: ``str`` folder used for caching (name only)
    :param file_ext: ``str`` file extension of cached files to be removed
    :return: ``None``
    """
    parent: bool = not os.path.exists(os.path.join(os.getcwd(), cache_folder))
    cache_files: list[str] = search_files_by_ext(
        file_ext, parent=parent, folder=cache_folder
    )

    go_to_folder: str = os.path.join(is_parent_dir_required(parent), cache_folder)
    folders: list[str] = glob.glob(f"{go_to_folder}{os.sep}*")
    if cache_files:
        os.chdir(go_to_folder)
        for file in cache_files:
            os.remove(file)
    elif folders:
        for item in folders:
            try:
                shutil.rmtree(item)
            except NotADirectoryError:
                os.remove(item)
    return None


def filename_creation_helper(suggestions: list[str], extension: str = "") -> str:
    """Takes a list of suggested filenames or creates a custom filename from user input.
    a user can type in just a filename without extension and the function will validate
    it to provide the correct name as needed.

    :param suggestions: list with the suggested filenames
    :param extension: file extension depending on what kind of file you want the user to create.
    :return: Filename either suggested or validated from user input.
    """
    name_suggest = suggestions
    print("Suggested filenames:\n")
    for num, file in enumerate(name_suggest, start=1):
        print(f"{num}. {file}")

    name_select = input(
        "\nPick a number to create your file or else type in a name now: "
    )
    try:
        return name_suggest[int(name_select) - 1]
    except (ValueError, IndexError):
        if len(name_select.split(".")) >= 2:
            return name_select
        elif name_select == "":
            raise RuntimeError("You really need a filename to continue.")
        else:
            return clean_filename(name_select, extension)


def filename_select(extension: str, parent: bool = False, folder: str = "") -> str:
    """Gives you a list of files with a certain extension. If you want to access the file from a parent dir,
    either let the destination function handle it for you or specify it yourself.

    :param folder: where you want to look for files
    :param extension: File extension of the files that interest you.
    :param parent: ``True`` to search in parent dir, default set to ``False``.
    :return: File name without relative path.
    """
    available_files = search_files_by_ext(extension, folder=folder, parent=parent)
    print(f"\nHere are the available {extension} files:")
    for num, file in enumerate(available_files, start=1):
        print(f"{num}. {file}")

    select_file = input(f"\nSelect your {extension} file now: ")
    try:
        return available_files[int(select_file) - 1]
    except IndexError:
        raise RuntimeError(f"This program requires a {extension} file. Exiting...")


def export_request_json(
    filename: str, stream, indent: int = 1, parent: bool = False, target_dir: str = ""
) -> str:
    """This function writes a ``JSON`` file to either your parent or current working dir.

    :param target_dir: (str) folder where the file is to be exported
    :param filename: (str) Filename with or without JSON extension.
    :param stream: (json) Data stream to export to JSON
    :param indent: (int) Indentation spaces. Default 1
    :param parent: (bool) Place file in parent directory if True. Default False.
    :return: (None) print statement for console logging.
    """
    f_name: str = clean_filename(filename, ".json")

    cwd_or_par: str = is_parent_dir_required(parent, relpath=True)

    f_path = (
        os.path.join(cwd_or_par, target_dir)
        if not target_dir
        else os.path.join(target_dir, f_name)
    )

    with open(f_path, "w", encoding="utf-8") as t:
        json.dump(stream, t, ensure_ascii=False, indent=indent)
    return f_path


def lst_dict_to_csv(lst_dic: list[dict[str, Any]], filename: str) -> None:
    """Helper function to dump a dictionary into a ``CSV`` file in current working dir.

    :param lst_dic: ``list[dict[str, Any]]``
    :param filename: ``str`` **(with or without ``.csv`` extension)**
    :return: ``None`` (file in project root)
    """
    clean_file = clean_filename(filename, "csv")
    with open(
        os.path.join(os.getcwd(), clean_file), "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(
            csvfile,
            dialect="excel",
        )
        writer.writerow(lst_dic[0].keys())
        for dic in lst_dic:
            writer.writerow(dic.values())
    return None


def is_parent_dir_required(parent: bool, relpath: bool = False) -> str:
    """
    This function returns a string to be used as a relative path that works
    with other functions to modify the where files are being stored
    or located (either parent or current working directory).

    :param parent: ``bool`` that will be gathered by parent functions.
    :param relpath: ``bool`` - Return parent or cwd as a relative path.
    :return: ``str`` Empty string in case the parent variable is not provided.
    """
    if parent:
        return_dir = os.path.dirname(os.getcwd())
    elif parent is None:
        return ""
    else:
        return_dir = os.getcwd()

    if relpath:
        return os.path.relpath(return_dir)
    else:
        return return_dir


def load_file_path(package: str, filename: str) -> Optional[Path]:
    """Load resources stored within folders in packages.
    Usually, not all systems can locate the required resources due to the package structure of the project.

    :param package: ``str`` package name, for example, if you have a file name in `./models` (being ./ a package itself) you can specify ``package.models`` here.
    :param filename: ``str`` name of the filename you are trying to load.
    :return: ``Path`` object
    """
    try:
        with importlib.resources.path(package, filename) as n_path:
            return n_path
    except ModuleNotFoundError:
        raise FileNotFoundError


def load_json_ctx(
    filename_or_path: str | Path, log_err: bool = False, thread_safe: bool = False
) -> Optional[Union[List[Dict[str, Any]], Deque[Dict[str, Any]]]]:
    """This function makes it possible to assign a JSON file from storage to a variable.

    :param filename_or_path: ``str`` -> Filename or path
    :param log_err: ``True`` if you want to print error information, default ``False``.
    :param thread_safe: ``True`` if you want to return a ``deque`` object, default ``False``
    :return: ``JSON`` object
    """
    if isinstance(filename_or_path, Path):
        json_file_path = filename_or_path
        json_file = os.path.basename(json_file_path)
    else:
        json_file = clean_filename(filename_or_path, "json")
        parent = not os.path.exists(
            os.path.join(is_parent_dir_required(False), json_file)
        )
        parent_or_cwd = is_parent_dir_required(parent)
        json_file_path = os.path.join(parent_or_cwd, json_file)

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            imp_json = json.load(f)

        if thread_safe:
            return deque(imp_json)

        return imp_json
    except FileNotFoundError:
        logging.critical(f"Raised FileNotFoundError: {json_file} not found!")
        if log_err:
            print(f"File {json_file_path} not found! Double-check the filename.")
        raise FileNotFoundError


def load_from_file(filename: str, extension: str, dirname: str = "", parent=False):
    """Loads the content of any file that could be read with the ``file.read()`` built-in function.\n
    Not suitable for files that require special handling by modules or classes.

    :param filename: ``str`` filename
    :param dirname: directory, if there is any.
    :param extension: file extension of the file to be read
    :param parent: Looks for the file in the parent directory if ``True``, default ``False``.
    :return: ``str``
    """
    parent_or_cwd = is_parent_dir_required(parent, relpath=True)
    file = clean_filename(filename, extension)
    if dirname:
        path = os.path.join(dirname, file)
    else:
        path = os.path.join(parent_or_cwd, file)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        return None


def remove_if_exists(fname: str | Path) -> bool:
    """Removes a file only if it exists in either parent or current working directory.

    :param fname: ``str`` | ``Path`` -> File name
    :return: Returns ``None`` if the file does not exist or is removed.
    """
    if os.path.exists(fname):
        os.remove(fname)
        return True
    return False


def search_files_by_ext(
    extension: str,
    folder: str | Path,
    recursive: bool = False,
    parent=False,
    abspaths=False,
) -> list[str]:
    """This function searches for files with the specified extension
    and returns a list with the files in either parent or current working directories.


    :param extension: with or without extension dot
    :param folder: ``str`` folder name
    :param parent: Searches in the parent directory if ``True``. Default ``False``.
    :param recursive: Recursive file search.
    :param abspaths: Return absolute paths intead of basenames
    :return: ``list[str]``
    """
    parent_dir = os.path.dirname(os.getcwd()) if parent else os.getcwd()
    search_files = clean_filename("*", extension)
    if recursive:
        return glob.glob(
            os.path.join(
                os.path.relpath(parent_dir), os.path.join(folder, "*", search_files)
            ),
            recursive=recursive,
        )
    else:
        return [
            os.path.basename(route) if not abspaths else os.path.abspath(route)
            for route in glob.glob(
                os.path.join(parent_dir, os.path.join(folder, search_files))
            )
        ]


def write_to_file(
    filename: str, folder: str, extension: str, stream: Any, create_file: bool = False
) -> None:
    """Write to file initializes a context manager to write a stream of data to a file with
    an extension specified by the user. This helper function reduces the need to repeat the code
    needed for this kind of operation.
    The function uses a relative path and the parent parameter
    will dictate whether the file is located alongside the source file.

    :param filename: -> Self-explanatory. Handles filenames with or without extension.
    :param folder: Destination folder for the file.
    :param extension: File extension that will be enforced for the file type.
    :param stream: stream data or data structure to be writen or converted into a file.
    :param create_file: If ``True``, the file will be created if it does not exist.
    :return: ``None`` -> It creates a file
    """
    mode = "xt" if create_file else "wt+"
    f_name = clean_filename(filename, extension)
    with open(
        f"{os.path.join(os.path.abspath(folder), f_name)}",
        mode,
        encoding="utf-8",
    ) as file:
        file.write(stream)
    print(f"Created file {f_name} in {os.path.abspath(folder)}")
    return None


def write_config_file(
    filename: str,
    package: str,
    section: str,
    option: str,
    value: str,
    safe_write: bool = False,
) -> bool:
    """Modify specific sections, options and values in an .ini configuration file.

    :param filename: ``str`` .ini config filename.
    :param package: ``str`` origin package in the project.
    :param section: ``str`` config section header name.
    :param option: ``str`` config option.
    :param value: ``str`` config option value.
    :param safe_write: ``bool`` - If ``True``, the function will not raise an exception if the file is not found.
    :raises ConfigFileNotFound: If the file is not found and safe_write is ``False``.
    :return: ``None`` (Writes .ini config file)
    """
    try:
        config = parse_client_config(filename, package, env_var=True, safe_parse=True)
        if not config:
            return False

        config.set(section, option, str(value))
        with open(os.environ.get("CONFIG_PATH"), "w") as update:
            config.write(update)
        return True
    except FileNotFoundError as Erno:
        logging.error(f"Raised {Erno!r}: {filename} not found in package {package}!")
        if safe_write:
            logging.info(f"Safe write enabled - Skipping Exception {Erno!r}")
            return False
        else:
            raise ConfigFileNotFound(filename, package)


def goto_project_root(project_root: str, source_path: str) -> Optional[str]:
    """
    Changes working directory to project root in order to account for cases when a file is executed
    as individual script or as a module in a package. If the function cannot identify a matching
    ``project_root`` string in the file path, the current working directory does not change.

    If the function finds a matching ``project_root`` string in the file path, the current working
    directory is changed to the directory containing the project root and returns the path for further
    processing.

    :param project_root: ``str`` -> directory name where this project is located
    :param source_path: ``str`` -> Path of the file where the function is called, typically the ``__file__`` variable.
    :return: ``str`` if the path exists else ``None``
    """
    file_path = source_path.split(os.sep)
    p_dir_indx = match_list_single(project_root, file_path, ignore_case=True)
    if p_dir_indx:
        project_dir = os.sep.join(file_path[: p_dir_indx + 1])
        if os.path.exists(project_dir):
            os.chdir(project_dir)
            return project_dir
    return None


def logging_setup(
    logging_dirname: str | Path,
    path_to_this: str,
) -> None:
    """Initiate the basic logging configuration for flows in the ``automation`` package.

    :param logging_dirname: ``str`` - Local logging direactory
    :param path_to_this: ``str`` - Equivalent to __file__ but passed in as a parameter.
    :return: ``None``
    """
    get_filename = lambda f: os.path.basename(f).split(".")[0]  # noqa: E731
    sample_size = 5
    random_int_id = "".join(
        random.choices([str(num) for num in range(1, 10)], k=sample_size)
    )
    uniq_log_id = f"{random_int_id}{generate_random_str(sample_size)}"

    # This will help users identify their corresponding log per session.
    os.environ["SESSION_ID"] = uniq_log_id
    log_name = (
        f"{get_filename(path_to_this)}-log-{uniq_log_id}-{datetime.date.today()}.log"
    )

    if os.path.exists(logging_dirname):
        log_dir_path = os.path.abspath(logging_dirname)
    elif os.path.exists(
        log_dir_parent := os.path.join(os.path.dirname(os.getcwd()), logging_dirname)
    ):
        log_dir_path = log_dir_parent
    else:
        try:
            os.makedirs(logging_dirname, exist_ok=True)
            log_dir_path = logging_dirname
        except OSError:
            raise UnavailableLoggingDirectory(logging_dirname)

    logging.basicConfig(
        filename=os.path.join(log_dir_path, log_name),
        filemode="w+",
        level=logging.INFO,
        encoding="utf8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )
    return None


def create_store(store_path: Path | str):
    """
    Create a database at a specific path

    :param store_path: ``Path`` or ``str`` -> Database path as a Path object or string.
                    Path objects are preferable unless the string you provide is a well-formed path.
    """
    db_conn = sqlite3.connect(Path(store_path))
    db_curr = db_conn.cursor()
    return db_conn, db_curr


def apply_os_permissions(
    file_path: str | Path, dir_permissions: bool = False, read_only: bool = False
) -> bool:
    """
    Apply Operating System permissions to protect certain artifacts that must be modified only by the
    current user as this prevents other users or threads initiated by others to modify them.
    This function is compatible with systems based on ``POSIX`` and Microsoft Windows.

    :param file_path:
    :param dir_permissions: ``bool`` -> apply permissions suitable for a directory
                            (``POSIX`` -> ``CHMOD 700`` / Default file permissions ``CHMOD 600``)
    :param read_only: ``bool`` -> apply read only permissions to an artifact (``POSIX`` -> ``CHMOD 400`` )
    """
    if os.path.exists(file_path):
        if os.name == "posix":
            if read_only:
                os.chmod(file_path, mode=0o400)
            else:
                # Only the owner can write and read
                chmod_num = 0o700 if dir_permissions else 0o600
                os.chmod(file_path, mode=chmod_num)
        elif os.name == "nt":
            # Remove inherited permissions
            subprocess.run(["icacls", f"{file_path}", "/inheritance:r"], check=True)
            if dir_permissions:
                # Full access to current user
                subprocess.run(
                    ["icacls", f"{file_path}", "/grant", f"{os.getlogin()}:F"],
                    check=True,
                )
            elif read_only:
                subprocess.run(
                    ["icacls", file_path, "/grant:r", f"{os.getlogin()}:R"], check=True
                )
            else:
                # Read and write for current user only
                subprocess.run(
                    ["icacls", f"{file_path}", "/grant:r", f"{os.getlogin()}:R,W"],
                    check=True,
                )

            # Remove other redundant permissions
            subprocess.run(["icacls", f"{file_path}", "/remove:g", "Users"], check=True)
            subprocess.run(
                ["icacls", f"{file_path}", "/remove:g", "Administrators"], check=True
            )
        else:
            raise UnsupportedPlatform("Unable to apply OS permissions to artifacts...")
        return True
    else:
        return False


def create_secure_path(path: str | Path, make_dir: bool = True) -> None:
    """
    Ensures a file or directory exists and secures its permissions.

    :param path: File or directory path.
    :param make_dir: If True and path is a directory (or extensionless), it will be created.
                     If False, path is assumed to be a file and must already exist or be created elsewhere.
    :return: None
    :raises RuntimeError: If the operating system is unsupported.
    """
    client_path = Path(path)
    if make_dir:
        client_path.mkdir(parents=True, exist_ok=True)

    if os.name == "posix":
        # 0o700 == S_IRUSR | S_IWUSR | S_IXUSR
        mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    elif os.name == "nt":
        # Windows seems to only honor the read-only bit via S_IREAD
        # Ensuring write permissions for the owner
        mode = stat.S_IREAD | stat.S_IWRITE
    else:
        raise RuntimeError(f"Unsupported OS: {os.name}")

    os.chmod(client_path, mode)


def exists_ok(app_path: ApplicationPath) -> str:
    """
    Create an application directory if it does not exist.

    :param app_path: ``ApplicationPath`` -> Directory to create
    :return: ``str`` -> Directory path
    """
    if not os.path.exists(app_path.value):
        os.makedirs(app_path.value, exist_ok=True)
    return app_path.value
