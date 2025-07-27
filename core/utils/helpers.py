"""
Utility Helper Functions Collection

This module provides reusable utility functions that support various operations across the project.
It contains implementations for common tasks including:

- URL access and web scraping (access_url, access_url_bs4)
- File handling and manipulation (clean_filename, load_from_file, write_to_file)
- Data processing and conversion (parse_date_to_iso, export_to_csv, lst_dict_to_csv)
- Authentication and security (get_token_oauth, sha256_hash_generate, str_encode_b64)
- Database operations (fetch_data_sql, get_from_db, get_project_db)
- Web automation (get_webdriver)
- Path and filename management (filename_creation_helper, search_files_by_ext)
- Data matching and filtering (match_list_single, match_list_mult, match_list_elem_date)
- Configuration handling (parse_client_config, write_config_file)
- System utilities (clean_console, get_duration, generate_random_str)

Each function is designed to be reusable across different modules and workflows in the project,
promoting code consistency and reducing duplication.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import base64
import csv
import datetime
import glob
import hashlib
import importlib.resources
import json
import logging
import os
import random
import re
import shutil
import sqlite3
import stat
import string
import subprocess
import urllib
import urllib.error
import urllib.request


from calendar import month_abbr, month_name
from configparser import ConfigParser
from datetime import date
from pathlib import Path
from re import Pattern
from sqlite3 import OperationalError, Connection, Cursor
from typing import AnyStr, Any, Optional

# Third-party modules
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session
from selenium import webdriver

# Local implementations
from core import SectionsNotFoundError, UnavailableLoggingDirectory, UnsupportedPlatform
from core.exceptions.config_exceptions import ConfigFileNotFound

# This way OAuthlib won't enforce HTTPS connections.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def access_url_bs4(url_to_bs4: str) -> BeautifulSoup:
    """Accesses a URL and returns a BeautifulSoup object that's ready to parse.

    :param url_to_bs4: ``str`` URL
    :return: ``bs4.BeautifulSoup`` object
    """
    user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
    headers = {
        "User-Agent": user_agent,
    }
    request = urllib.request.Request(url_to_bs4, None, headers)
    page = urllib.request.urlopen(request)
    return BeautifulSoup(page, "html.parser")


def access_url(url_raw: str) -> Any:
    """Accesses a URL and returns a http.client.HTTPResponse object

    :param url_raw: ``str`` URL
    :return: ``http.client.HTTPResponse`` object
    """
    user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
    headers = {
        "User-Agent": user_agent,
    }
    request = urllib.request.Request(url_raw, None, headers)
    page = urllib.request.urlopen(request)
    return page


def clean_filename(filename: str, extension: str = "") -> str:
    """This function handles filenames with and without extension
    and avoids breaking functions that work with filenames and paths
    without expecting a user to pass in a correct ``filename.extension`` every time.

    In case that you don't pass an extension, the function will return the filename without
    any modifications, like a "trust" mode.

    :param filename: ``str`` -> self-explanatory
    :param extension: ``str`` -> self-explanatory. Default ``""`` (Empty str)
    :return: ``str`` (New filename)
    """
    if extension == "":
        return filename
    elif not isinstance(filename, str):
        raise TypeError(f"Filename must be a string, not {type(filename)}!")
    elif not isinstance(extension, str):
        raise TypeError(f"Extension must be a string, not {type(filename)}!")

    no_dot = lambda fname: re.findall(r"\w+", fname)[0]

    if "." in split_char(filename, char_lst=True):
        return (
            ".".join(
                filter(lambda lst: no_dot(extension) not in lst, filename.split("."))
            )
            + f".{no_dot(extension)}"
        )
    else:
        return f"{filename}.{no_dot(extension)}"


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


def export_client_info() -> Optional[dict[str, dict[str, str]]]:
    """Help dataclasses set a ``default_factory`` field for the client info function.
    **Note: No longer used due to core.config_mgr implementation.**

    :return: ``dict[str, dict[str, str]`` Client info loaded ``JSON``
    """
    info = get_client_info("client_info")
    return info


def fetch_data_sql(
    sql_query: str, db_cursor: sqlite3
) -> Optional[list[tuple[str | int, ...]]]:
    """Takes a SQL query in string format and returns the data
    in a list of tuples. In case there is no data, the function returns None.

    :param sql_query: SQL Query string.
    :param db_cursor: Database connection cursor.
    :return: ``list[tuple]``
    """
    db_cursor.execute(sql_query)
    return db_cursor.fetchall()


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
    if not target_dir:
        is_parent: str = is_parent_dir_required(parent, relpath=True)
        f_name: str = clean_filename(filename, ".json")
        dest_dir = (
            os.path.join(is_parent, target_dir) if target_dir != "" else is_parent
        )

        cwd_or_par = is_parent_dir_required(parent)
        f_path = (
            os.path.join(cwd_or_par, target_dir) if target_dir != "" else cwd_or_par
        )
    else:
        f_path = os.path.join(target_dir, filename)

    with open(f_path, "w", encoding="utf-8") as t:
        json.dump(stream, t, ensure_ascii=False, indent=indent)
    return f_path


def export_to_csv_nt(nmedtpl_lst: list, filename: str, top_row_lst: list[str]) -> None:
    """Helper function to dump a list of NamedTuples into a ``CSV`` file in current working dir.

    :param nmedtpl_lst: ``list[namedtuple]``
    :param filename: name **(with or without ``.csv`` extension)**
    :param top_row_lst: ``list[str]``
    :return: ``None`` (file in project root)
    """
    clean_file = clean_filename(filename, "csv")
    with open(clean_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(
            csvfile,
            dialect="excel",
        )
        writer.writerow(top_row_lst)
        for tag in nmedtpl_lst:
            try:
                writer.writerow([getattr(tag, f) for f in tag._fields])
            except IndexError:
                continue
    return None


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


def get_token_oauth(
    client_id_: str,
    uri_callback_: str,
    client_secret_: str,
    auth_url_: str,
    token_url_: str,
) -> json:
    """Uses the OAuth2Session module from requests_oauthlib to obtain an
    authentication token for compatible APIs. All parameters are self-explanatory.

    :param client_id_: ``str``
    :param uri_callback_: ``str``
    :param client_secret_: ``str``
    :param auth_url_: ``str``
    :param token_url_: ``str``
    :return: ``JSON`` object
    """
    oauth_session = OAuth2Session(
        client_id_,
        redirect_uri=uri_callback_,
    )
    authorization_url, _ = oauth_session.authorization_url(auth_url_)
    print(f"Please go to {authorization_url} and authorize access.")
    authorization_response = uri_callback_
    token = oauth_session.fetch_token(
        token_url_,
        authorization_response=authorization_response,
        client_secret=client_secret_,
    )
    return token


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


def get_client_info(
    filename: str, logg_err: bool = False
) -> Optional[dict[str, [str, str]]]:
    """This function handles API secrets in a way that completely eliminates the need
    to use them inside the code. It can be any ``JSON`` file that you create for that purpose and,
    most importantly, placed in **``.gitignore``** to avoid pushing sensitive info to *GitHub* or *GitLab*.

    :param filename: ``JSON`` file where you store your secrets.
    :param logg_err: ``True`` if you want to print the ``FileNotFoundError`` exception.
    :return: ``dict[str, [str,str]]`` loaded dictionary from filename ``json.load`` or ``None`` if the file is not found.
    """
    f_name = clean_filename(filename, "json")
    parent = not os.path.exists(
        os.path.join(is_parent_dir_required(False, relpath=True), f_name)
    )
    in_parent = is_parent_dir_required(parent, relpath=True)

    try:
        with open(os.path.join(in_parent, f_name), "r", encoding="utf-8") as secrets:
            client_info = json.load(secrets)
        return dict(client_info)
    except FileNotFoundError as Errno:
        if logg_err:
            print(Errno)

        return None


def get_duration(seconds: int | float) -> tuple[int | float, int | float, int | float]:
    """Takes the number of seconds and calculates its duration in hours, minutes, and seconds.

    :param seconds: ``int``
    :return: ``tuple[int, int, int]`` *hours, minutes, seconds*
    """
    hours, remainder = divmod(seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute
    return hours, minutes, seconds


def get_dict_key(source_dic: dict, value: int) -> Optional[str | int]:
    """This function retrieves the key from a dictionary if the value is associated with one.

    :param source_dic: key lookup ``dict``
    :param value: value to query
    :return: ``str`` or ``int`` or ``None`` / *depending on the results and datatype of the key.*
    """
    for tname, tid in source_dic.items():
        if value == tid:
            return tname
    return None


def get_from_db(
    cur: sqlite3, field: str, table: str
) -> Optional[list[tuple[str, ...]]]:
    """This function gets a field from a table in a ``SQLite3`` database.

    :param cur: database cursor
    :param field: database column/field
    :param table: database table
    :return: ``list[tuple] | None`` List of tuples with the values or None in case of operational error.
    """
    qry = f"SELECT {field} from {table}"
    try:
        return cur.execute(qry).fetchall()
    except OperationalError:
        return None


def get_project_db(
    parent: bool = False, folder: str = ""
) -> tuple[Connection, Cursor, str]:
    """Look for databases in the project files either from a child directory or root.

    :param parent: ``True`` if you are looking for databases from a child directory. Default ``False``.
    :param folder: specific folder to look for databases.
    :return: ``SQLite3`` db connection, db cursor, and db name in Tuple.
    """
    is_parent = is_parent_dir_required(parent=parent, relpath=True)
    db_filename = filename_select("db", parent=parent, folder=folder)
    db_path = (
        os.path.join(is_parent, folder, db_filename)
        if folder != ""
        else os.path.join(is_parent, db_filename)
    )
    db_new_conn = sqlite3.connect(db_path)
    db_new_cur = db_new_conn.cursor()
    return db_new_conn, db_new_cur, db_filename


def get_webdriver(
    download_folder: str,
    headless: bool = False,
    gecko: bool = False,
    no_imgs: bool = False,
) -> webdriver:
    """Get a webdriver with customisable settings via parameters.

    :param no_imgs: ``bool`` - Disable image loading for scraping performance gain
    :param download_folder: self-explanatory. Works with relative or absolute paths
    :param headless: ``True`` to enable headless webdriver execution. Default ``False``.
    :param gecko: True to obtain a gecko webdriver instance. Default Chrome Webdriver ``gecko=False``.
    :return: Selenium ``webdriver`` instance.
    """
    if gecko:
        # Configure the Firefox (Gecko) Driver
        gecko_options = webdriver.FirefoxOptions()
        gecko_options.set_preference("browser.download.folderList", 2)
        gecko_options.set_preference("browser.download.manager.showWhenStarting", False)
        gecko_options.set_preference(
            "browser.download.dir", f"{os.path.abspath(download_folder)}"
        )
        gecko_options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/octet-stream"
        )
        gecko_options.enable_downloads = True

        if headless:
            gecko_options.add_argument("--headless")
        elif no_imgs:
            gecko_options.set_preference("permissions.default.image", 2)

        return webdriver.Firefox(options=gecko_options)

    else:
        # Configure Chrome's Path and arguments
        # Binary paths should be detected automatically, however, I want to make
        # sure it uses google-chrome stable in posix and not nightly or dev releases.
        chrome_options = webdriver.ChromeOptions()
        if os.name == "posix":
            chrome_binary_location = (
                f"{os.path.join('opt', 'google', 'chrome', 'google-chrome')}"
            )
            if os.path.exists(chrome_binary_location):
                chrome_options.binary_location = chrome_binary_location
        # Does not let Chrome limit my resource usage
        chrome_options.add_argument("--disable-dev-shm-usage")

        prefs = {
            # Replace with your folder path
            "download.default_directory": f"{os.path.abspath(download_folder)}",
            # Automatically download without the prompt
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,  # Overwrite if the file exists
            "safebrowsing.enabled": True,  # Ignore security warnings
        }

        # ``prefs`` above are experimental options
        chrome_options.add_experimental_option("prefs", prefs)

        if headless:
            chrome_options.add_argument("--headless")
        elif no_imgs:
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")

        return webdriver.Chrome(options=chrome_options)


def match_list_single(
    hint: str | Pattern[str], items: list, ignore_case: bool = False
) -> Optional[int]:
    """Matches a single occurrence of a ``hint`` and returns its ``index`` position.

    :param hint: ``str`` pattern or word
    :param items: where to look for occurrences (list of ``str`` or ``WebElement``)
    :param ignore_case: ``True`` to disable the ``re.IGNORECASE`` flag in the Python Regex match. Default ``False``.
    :return: ``int`` or ``None`` if there is no match.
    """
    ignore_case = re.IGNORECASE if ignore_case else 0
    for item in items[:]:
        if isinstance(item, str) or isinstance(item, Pattern):
            # Item must be kept intact in case I want to look for it in the list.
            # In this case it doesn't matter, however, re.match looks for
            # matches in `inter`
            inter = item
        else:
            # in case I am passing a list of WebElement items.
            inter = item.text

        if re.findall(hint, inter, flags=ignore_case):
            return items.index(item)
        else:
            continue
    return None


def match_list_mult(
    hint: str, list_lookup: list[str], ignore_case: bool = False
) -> list[int]:
    """Matches a ``str`` within a list and returns the indexes where such matches occurred.

    :param hint: ``str`` pattern
    :param list_lookup: the list likely to contain the match.
    :param ignore_case: ``True`` to enable the ``re.IGNORECASE`` flag for matches. Default ``False``
    :return: ``list[int]`` list of matching index positions.
    """
    ignore_case = re.IGNORECASE if ignore_case else 0
    return [
        num
        for num, elem in enumerate(list_lookup)
        if re.findall(hint, elem, flags=ignore_case)
    ]


def match_list_elem_date(
    l_hints: list[str],
    lookup_list: list[str],
    ignore_case: bool = False,
    join_hints: tuple[bool, str, str] = (False, "", ""),
    strict: bool = False,
    reverse: bool = False,
) -> list[str]:
    """Finds matches, within a list of strings, and compares the dates in each of the strings to return the items
    that are associated with the latest dates; therefore, leaving out strings with the same name that do not contain
    a relevant date (strict mode). This project adopted a filename convention that places filenames, joined with
    hyphens ('-'), with a date string in ISO format to keep track of updates in files generated by other modules.
    One of our helper functions in this module returns a list of files by extension
    ``search_files_by_ext`` and I needed a way of getting the most relevant files, so that other modules can
    incorporate further functionality that can effectively select from the available filenames and work with an
    updated copy of such. This algorithm also implements a simple ``reverse`` mode, that outputs the lookup list without
    the matches; in other words, it excludes the matches if you don't want to use them in your functionality.

    For example, I have to match strings with the hints ``['foo', 'bar']`` within a list
    ``['foo-2024-11-04', 'foo-2024-11-02', 'bar-2024-10-29', 'bar-2024-09-20']`` the function will find multiple occurrences
    of the hints and for each hint in the list do the following:

    1. manipulate the hint with split and join if needed (in case there is a known pattern in place)
    2. extract dates using regular expressions and compare them to find the string related to the latest date
    3. match other strings that do not contain dates (strict mode off).

    :param l_hints: list of patterns or str that you want to match.
    :param lookup_list: list of strings to process and look for matches
    :param ignore_case: ``True`` if you want to enable the ``re.IGNORECASE`` flag in the matching process. Default ``False``
    :param join_hints: (optional) Tuple of three values:\n
           1. ``bool`` value to tell the function whether to use the values that you provided.\n
           2. `split` character because, if you want to join, you need to split in this case.\n
           3. `join` character to join your hints.\n
           -> Here is an example with the `join_hints` parameter:\n
           ``hints = ['foo bar', 'moo woo']``\n
           ``lookup_list = [foo-bar-2024-11-09, foo-bar-2024-11-02, moo-woo-2024-10-27, moo-woo-2024-10-29]``\n
           ``join_hints = (True, ' ', '-')``\n
           # This will result in 'foo-bar' and 'moo-woo' as the new hints.\n
           From here the function will extract the date and store the item the *"most up-to-date"* filename,
           leaving out older and irrelevant filenames.
           In this example, the output will be ``[foo-bar-2024-11-09, moo-woo-2024-10-29]``
    :param strict: ``True`` if you only want to match strings with "date".
           **Note that, if this is active, other strings that do not follow the convention will be left out.**
           Default ``False``.
    :param reverse: ``True`` to return a ``lookup_list`` without the matches.
    :return: ``list[str]``
    """
    up_to_date: list[str] = []
    main_matches: list[str] = []
    for hint in l_hints:
        if join_hints[0]:
            spl_hint = hint.split(join_hints[1])
            hint = join_hints[2].join(spl_hint)

        matches = match_list_mult(hint, lookup_list, ignore_case=ignore_case)

        get_match_items = [lookup_list[indx] for indx in matches]

        if reverse:
            for match in get_match_items:
                main_matches.append(match)

        date_regex = re.compile(r"(\d{2,4}-\d{1,2}-\d{1,2})")

        extract_dates = [
            date.fromisoformat(date_regex.findall(match)[0])
            for match in get_match_items
            if date_regex.findall(match)
        ]

        if extract_dates:
            max_date_items = match_list_mult(str(max(extract_dates)), get_match_items)
            for indx in max_date_items:
                up_to_date.append(get_match_items[indx])
        elif not strict:
            # If there are no dates in the item, I still want to know about it.
            # BUT only if strict mode is disabled.
            for m_item in get_match_items:
                up_to_date.append(m_item)
        else:
            continue
    if reverse:
        return [match for match in main_matches if match not in up_to_date]
    else:
        return up_to_date


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
    filename_or_path: str | Path, log_err: bool = False
) -> Optional[list[dict[...]]]:
    """This function makes it possible to assign a JSON file from storage to a variable.

    :param log_err: ``True`` if you want to print error information, default ``False``.
    :param filename_or_path: ``str`` -> Filename or path
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


def parse_client_config(
    ini_file: str, package_name: str, env_var: bool = False, safe_parse: bool = False
) -> ConfigParser | bool:
    """Parse client configuration files that store secrets and other configurations.

    :param ini_file: ``str`` ini filename with or without the extension
    :param package_name: ``str`` package name where the config file is located.
    :param env_var: ``bool`` Save path in an environment path
    :param safe_parse: ``bool`` If ``True``, the function will return ``False`` if the file is not found.
    :return: ``ConfigParser``
    """
    f_ini = clean_filename(ini_file, "ini")
    config = ConfigParser(interpolation=None)
    with importlib.resources.path(package_name, f_ini) as f_path:
        if env_var:
            os.environ["CONFIG_PATH"] = os.path.abspath(f_path)
        elif not os.path.exists(f_path):
            if safe_parse:
                return False
            else:
                raise ConfigFileNotFound(f_ini, package_name)
        config.read(f_path)
    return config


def parse_date_to_iso(
    full_date: str, zero_day: bool = False, m_abbr: bool = False
) -> date:
    """Breaks down the full date string and converts it to ISO format to get a datetime.date object.
    important: Make sure to import 'from calendar import month_abbr, month_name' as it is required.

    :param full_date: date_full is ``'Aug 20th, 2024'`` or ``'August 20th, 2024'``.
    :param zero_day: True if your date already has a zero in days less than 10. Default: False
    :param m_abbr: Set to True if you provide a month abbreviation e.g. ``'Aug'``, default set to ``False``.
    :return: ``date`` object (``ISO`` format)
    """
    # Lists month_abbr and month_name provided by the built-in Calendar
    # library in Python.
    if m_abbr:
        months = list(month_abbr)
    else:
        months = list(month_name)

    letters = re.compile(r"[a-z]")
    year = str(full_date.split(",")[1].strip())

    month_num = str(months.index(full_date.split(",")[0].split(" ")[0]))

    # The date ISO format requires that single numbers are preceded by a 0.

    if int(month_num) <= 9:
        month_num = "0" + str(months.index(full_date.split(",")[0].split(" ")[0]))

    day_nth = str(full_date.split(",")[0].split(" ")[1])
    day = day_nth.strip("".join(letters.findall(day_nth)))

    if zero_day:
        if int(day) <= 9:
            day = day_nth.strip("".join(letters.findall(day_nth)))
    else:
        if int(day) <= 9:
            day = "0" + day_nth.strip("".join(letters.findall(day_nth)))

    return date.fromisoformat(year + month_num + day)


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


def load_file_package_scope(package: str, filename: str) -> AnyStr:
    """Load file when the program is executed as a module.

    :param package: package name
    :param filename: filename
    :return: AnyStr
    """
    with importlib.resources.path(package, filename) as file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


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


def str_encode_b64(encode_str: str) -> str:
    """Encode any string by using the Base64 algorithm.

    :param encode_str: ``str`` to encode
    :return:
    """
    encode_bytes = encode_str.encode("ascii")
    b64_bytes = base64.b64encode(encode_bytes)
    return b64_bytes.decode("ascii")


def sha256_hash_generate(r_str: str) -> str:
    """Generate SHA256 hash from random string.

    :param r_str: ``str`` random string
    :return: ``str`` SHA256 hash string
    """
    return hashlib.sha256(r_str.encode()).hexdigest()


def generate_random_str(k: int) -> str:
    """Generate a random string of ASCII characters based on a sample size ``k``.

    :param k: ``int`` Number of letters per random string or "sample size"
    :return: ``str``
    """
    letters = string.ascii_letters
    random_string = "".join(random.choices(letters, k=k))
    return random_string


def split_char(
    spl_str: Optional[str],
    placeholder: str = "-1",
    char_lst: bool = False,
    char_lst_raw: bool = False,
) -> str | list[str]:
    """
    Identify the split character dynamically in order that str.split() knows what
    the correct separator is. In this project, the most relevant separators are ``, `` and
    ``;``, in contrast, whitespaces are not as important. That said, if the only non-alphanumeric character of
    the string is whitespace, the function has to return it. Additional parameters
    help with complementary logic and graceful error handling across modules.

    By design, this implementation assumes that, if there are multiple separators or the first one
    in the match list is whitespace, the former may repeat itself or the latter may not be relevant for the purpose;
    therefore, the logic discards all whitespaces and focuses on other special characters that occur the most if there
    are more multiple matches. This is so because it is common to separate words with a whitespace at first and then
    use another separator, one that is really meant to be a separator; for example, in the case
    ``colorful skies; great landscape; ...`` whitespace is not the real separator.

    :param spl_str: ``str`` with or without separators
    :param placeholder: ``str`` - Return this character if there is no separator as it can't be empty. Default: ``"-1"``
    :param char_lst: ``bool`` - Return a list of unique separators instead of a single one or ``raw_str`` in a ``list[str]``.
    :param char_lst_raw: ``bool`` - If active, the function will return the char_lst without any modifications for debugging.
    :return: ``str`` | ``list[str]``
    """
    try:
        chars = re.findall(r"[^0-9a-z]", spl_str, re.IGNORECASE)
    except TypeError:  # if ``spl_str`` is ``None``
        return placeholder

    lst_strip = lambda chls: list(map(lambda s: s.strip(), chls))

    if chars:
        if len(chars) == 1:
            return chars[0]
        else:
            ch_lst = lst_strip(chars)
            if char_lst:
                return ch_lst
            elif char_lst_raw:
                return chars
            else:
                try:
                    filtered = list(filter(lambda ch: ch != " " and ch != "", ch_lst))
                    # It makes sense to identify which character occurs more frequently.
                    return max(filtered, key=filtered.count)
                except ValueError:
                    return placeholder
    elif char_lst:
        return list(spl_str)
    else:
        return placeholder


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


def filter_apostrophe(apost_str: str) -> str:
    """Clean words that could contain apostrophes in them.

    :param apost_str: ``str`` the conflicting text
    :return: ``str`` -> ``apost_str`` without apostrophe
    """
    return "".join(apost_str.split(split_char(apost_str)))


def goto_project_root(project_root: str, source_path: str) -> Optional[str]:
    """
    Changes working directory to project root in order to account for cases when a file is executed
    as individual script or as a module in a package. If the function cannot identify a matching
    ``project_root`` string in the file path, the current working directory does not change.

    :param project_root: ``str`` -> directory name where this project is located
    :param source_path: ``str`` -> Path of the file where the function is called, typically the ``__file__`` variable.
    :return: ``str`` if the path exists else ``None``
    """
    file_path = source_path.split(os.sep)
    p_dir_indx = match_list_single(project_root, file_path)
    if p_dir_indx:
        project_dir = os.sep.join(file_path[: p_dir_indx + 1])
        if os.path.exists(project_dir):
            os.chdir(project_dir)
    return None


def config_section_parser(config_filename: str, target_hint: str):
    """Parse a configuration file that contains a specific string in one of its sections and retrieve options
    under that section.

    As an example, you have file ``my_config.ini`` and it has two sections ``[pretty_config]`` and ``[ugly_config]``.
    In this case, you need the options in ``[pretty_config]``, however another user could create a configuration file
    with a different arrangement like add spaces or include words to the section name and this makes hardcoding of section
    names difficult, hence this function.
    A user could create a file with the section name ``[config_pretty]`` or ``[not-so-pretty-config]`` and this function
    will be able to retrieve the options from that part of the file as long as it contains the ``target_hint``
    string, in represented in this example as the word ``"pretty"``.

    :param config_filename: ``str`` Source config filename
    :param target_hint: ``str`` string that could be included in a config file section
    :return: ``list[str]`` -> config options.
    """
    config = parse_client_config(config_filename, "core.config")
    sections = config.sections()

    wrd_list = filter_apostrophe(target_hint).split(
        split_char(target_hint, placeholder=" ")
    )

    find_me = (
        lambda word, section: matchs[0]
        if (matchs := re.findall(word, section, flags=re.IGNORECASE))
        else matchs
    )

    option_list = []
    for wrd in wrd_list:
        # The main lambda has re.findall with IGNORECASE flag, however
        # list index lookup does take word case into consideration for str comparison.
        wrd_to_lc = wrd.lower()

        # To ensure uniqueness in the hints provided, the count of matches must be 1.
        # If the same word is found more than once, then the match is clearly not unique.
        matches = (
            temp_lst := [find_me(wrd_to_lc, section) for section in sections]
        ).count(wrd_to_lc)
        if matches == 1:
            match_indx = temp_lst.index(wrd_to_lc)
            logging.info(
                f'Section parsing result: found "{wrd}" in section: {sections[match_indx]}'
            )
            option_list = list(config[sections[match_indx]].values())
            break
        else:
            continue

    if option_list:
        return option_list
    else:
        logging.critical("Raised SectionsNotFoundError - Quitting...")
        raise SectionsNotFoundError


def logging_setup(
    logging_dirname: str | Path,
    path_to_this: str,
) -> None:
    """Initiate the basic logging configuration for bots in the ``workflows`` package.

    :param logging_dirname: ``str`` - Local logging direactory
    :param path_to_this: ``str`` - Equivalent to __file__ but passed in as a parameter.
    :return: ``None``
    """
    get_filename = lambda f: os.path.basename(f).split(".")[0]
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
