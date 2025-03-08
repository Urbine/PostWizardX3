"""
This module stores the helper functions that collaborate with other local implementations.

The file also adds bits of reusable business logic from other modules.
Helpers must have a reusable implementation of commonly-used code.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import base64
import csv
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
import string
import subprocess
import urllib
import urllib.request
import urllib.error

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

# Local implmentations
from core.custom_exceptions import ConfigFileNotFound

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


def clean_filename(filename: str, extension: str = None) -> str:
    """This function handles filenames with and without extension
    and avoids breaking functions that work with filenames and paths.
    Here you can pass filenames with or without extension and enforce a file type
    without expecting a user to pass in a correct ``filename.extension`` every time.

    In case that you don't pass an extension, the function will return the filename without
    any modifications. I call that a 'trust' mode.

    :param filename: ``str`` -> self-explanatory
    :param extension: ``str`` -> self-explanatory
    :return: ``str`` (New filename)
    """
    # This has some applications to avoid additional logic or error handling
    # in other functions.
    # TODO: Fix clean_filename('com.example', 'com') and
    # clean_filename('plares.co', '.uk')

    if filename == "":
        return filename
    elif not isinstance(filename, str):
        raise TypeError("Filename must be a string.")
    elif not isinstance(extension, str):
        raise TypeError("Extension must be a string.")
    else:
        pass

    if re.findall("[.+]", extension):
        if re.findall(extension.split(".")[0], filename):
            return filename.split(".")[0] + extension
        else:
            return filename + extension
    elif extension is None:
        # This is a kind of "trust" mode.
        return filename
    elif filename == extension:
        # If filename and extension are the same, I simply give it back:
        return filename + "." + extension
    elif re.findall(extension, filename):
        if re.findall("[.+]", filename):
            return filename.split(".")[0] + "." + extension
        else:
            return filename + "." + extension
    else:
        return filename + "." + extension


def clean_file_cache(cache_folder: str, file_ext: str) -> None:
    """The purpose of this function is simple: cleaning remaining temporary files once the job control
    has used them; this is specially useful when dealing with thumbnails.

    :param cache_folder: ``str`` folder used for caching (name only)
    :param file_ext: ``str`` file extension of cached files to be removed
    :return: ``None``
    """
    parent: bool = not os.path.exists(f"./{cache_folder}")
    cache_files: list[str] = search_files_by_ext(
        file_ext, parent=parent, folder=cache_folder
    )

    go_to_folder: str = is_parent_dir_required(parent) + cache_folder
    folders: list[str] = glob.glob(f"{go_to_folder}/*")
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
            finally:
                continue
    return None


def clean_path(folder: str, prefix: bool = False) -> str:
    """Prefix or suffix a slash to construct a path.
    It can be useful when it is not possible to use a formatted string.
    The majority of path joins do not require this function and other built-in functions
    can do this as well (e.g. ``os.path.join``).

    :param folder: folder string
    :param prefix: ``True`` if you need to prefix the folder with a ``'/'``. Default ``False``.
    :return: concatenated string
    """
    if folder == "":
        return folder
    elif not isinstance(folder, str):
        raise TypeError("Filename must be a string.")
    else:
        pass

    if prefix:
        return "/" + folder + "/"
    else:
        return folder + "/"


def cwd_or_parent_path(parent: bool = False) -> str:
    """This function gets an absolute path that works with other functions to point out
    where files are being stored (parent or current working directory).

    :param parent: ``bool`` that will be gathered by parent functions.
    :return: ``str`` absolute path string, not a path object.
    """
    if parent:
        return os.path.dirname(os.getcwd())
    else:
        return os.getcwd()


def export_client_info() -> Optional[dict[str, dict[str, str]]]:
    """Help dataclasses set a ``default_factory`` field for the client info function.
    **Note: No longer used due to core.config_mgr implementation.**

    :return: ``dict[str, dict[str, str]`` Client info loaded ``JSON``
    """
    info = get_client_info("client_info")
    return info


def fetch_data_sql(sql_query: str, db_cursor: sqlite3) -> list[tuple[str | int, ...]]:
    """Fetch videos takes a SQL query in string format and returns the data
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
    except ValueError or IndexError:
        if len(name_select.split(".")) >= 2:
            return name_select
        elif name_select == "":
            raise RuntimeError("You really need a database name to continue.")
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
    filename: str, stream, indent: int = 1, parent: bool = False, folder: str = ""
) -> str:
    """This function writes a ``JSON`` file to either your parent or current working dir.

    :param folder: (str) folder where the file is to be exported
    :param filename: (str) Filename with or without JSON extension.
    :param stream: (json) Data stream to export to JSON
    :param indent: (int) Indentation spaces. Default 1
    :param parent: (bool) Place file in parent directory if True. Default False.
    :return: (None) print statement for console logging.
    """
    is_parent: str = is_parent_dir_required(parent)
    f_name: str = clean_filename(filename, ".json")
    dest_dir = is_parent + f"/{folder}" if folder != "" else is_parent

    cwd_or_par = cwd_or_parent_path(parent)
    f_path = cwd_or_par + f"/{folder}" if folder != "" else cwd_or_par

    with open(f"{dest_dir}{f_name}", "w", encoding="utf-8") as t:
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
    authorization_url, state = oauth_session.authorization_url(auth_url_)
    print(f"Please go to {authorization_url} and authorize access.")
    authorization_response = uri_callback_
    token = oauth_session.fetch_token(
        token_url_,
        authorization_response=authorization_response,
        client_secret=client_secret_,
    )
    return token


def is_parent_dir_required(parent: bool) -> str:
    """
    This function returns a string to be used as a relative path that works
    with other functions to modify the where files are being stored
    or located (either parent or current working directory).

    :param parent: ``bool`` that will be gathered by parent functions.
    :return: ``str`` Empty string in case the parent variable is not provided.
    """
    if parent:
        return "../"
    elif parent is None:
        return ""
    else:
        return "./"


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
    parent = not os.path.exists(f"./{f_name}")
    in_parent = is_parent_dir_required(parent)

    try:
        with open(f"{in_parent}{f_name}", "r", encoding="utf-8") as secrets:
            client_info = json.load(secrets)
        return dict(client_info)
    except FileNotFoundError as Errno:
        if logg_err:
            print(Errno)
        else:
            pass
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
    is_parent = is_parent_dir_required(parent=parent)
    db_filename = filename_select("db", parent=parent, folder=folder)
    db_path = (
        f"{is_parent}{folder}/{db_filename}"
        if folder != ""
        else f"{is_parent}{db_filename}"
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
        gecko_options.set_preference("browser.download.dir", download_folder)
        gecko_options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/octet-stream"
        )
        gecko_options.enable_downloads = True

        if headless:
            gecko_options.add_argument("--headless")
        elif no_imgs:
            gecko_options.set_preference("permissions.default.image", 2)
        else:
            pass

        return webdriver.Firefox(options=gecko_options)

    else:
        # Configure Chrome's Path and arguments
        # Binary paths should be detected automatically, however, I want to make
        # sure it uses google-chrome stable in posix and not nightly or dev releases.
        chrome_options = webdriver.ChromeOptions()
        if os.name == "posix":
            chrome_options.binary_location = "/opt/google/chrome/google-chrome"
        else:
            pass

        # Does not let Chrome limit my resource usage
        chrome_options.add_argument("--disable-dev-shm-usage")

        prefs = {
            # Replace with your folder path
            "download.default_directory": f"{download_folder}",
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
        else:
            pass

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
           ``join_hints = (True, ' ', '-')
           # This will result in 'foo-bar' and 'moo-woo' as the new hints.``\n
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
        else:
            pass

        matches = match_list_mult(hint, lookup_list, ignore_case=ignore_case)

        get_match_items = [lookup_list[indx] for indx in matches]

        if reverse:
            for match in get_match_items:
                main_matches.append(match)
        else:
            pass

        date_regex = re.compile(r"(\d{2,4}-\d{1,2}-\d{1,2})")

        extract_dates = [
            date.fromisoformat(re.findall(date_regex, match)[0])
            for match in get_match_items
            if re.findall(date_regex, match)
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


def load_json_ctx(filename: str, log_err: bool = False):
    """This function makes it possible to assign a JSON file from storage to a variable.

    :param log_err: ``True`` if you want to print error information, default ``False``.
    :param filename: ``str``
    :return: ``JSON`` object
    """
    json_file = clean_filename(filename, "json")
    parent = not os.path.exists(f"./{json_file}")
    parent_or_cwd = is_parent_dir_required(parent)
    try:
        with open(
            json_file := f"{parent_or_cwd}{json_file}", "r", encoding="utf-8"
        ) as f:
            imp_json = json.load(f)
        return imp_json
    except FileNotFoundError:
        logging.critical(f"Raised FileNotFoundError: {json_file} not found!")
        if log_err:
            print(
                f"File {parent_or_cwd}{json_file} not found! Double-check the filename."
            )
        return None


def load_from_file(filename: str, extension: str, dirname: str = "", parent=False):
    """Loads the content of any file that could be read with the ``file.read()`` built-in function.\n
    Not suitable for files that require special handling by modules or classes.

    :param filename: ``str`` filename
    :param dirname: directory, if there is any.
    :param extension: file extension of the file to be read
    :param parent: Looks for the file in the parent directory if ``True``, default ``False``.
    :return: ``str``
    """
    parent_or_cwd = is_parent_dir_required(parent)
    file = clean_filename(filename, extension)
    if dirname:
        path = f"{dirname}/{file}"
    else:
        path = f"{parent_or_cwd}{file}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        return None


def remove_if_exists(fname: str):
    """Removes a file only if it exists in either parent or current working directory.

    :param fname: File name
    :return: Returns ``None`` if the file does not exist or is removed.
    """
    if os.path.exists(fname):
        os.remove(fname)
    else:
        return None


def parse_client_config(ini_file: str, package_name: str) -> ConfigParser:
    """Parse a client configuration files that store secrets and other configurations.

    :param ini_file: ``str`` ini filename with or without the extension
    :param package_name: ``str`` package name where the config file is located.
    :return: ``ConfigParser``
    """
    f_ini = clean_filename(ini_file, "ini")
    config = ConfigParser(interpolation=None)
    try:
        with importlib.resources.path(package_name, f_ini) as f_path:
            os.environ["CLIENT_INFO_PATH"] = str(f_path)
            config.read(f_path)
    except ModuleNotFoundError:
        raise ConfigFileNotFound(f_ini, package_name)
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

    year = str(full_date.split(",")[1].strip())

    month_num = str(months.index(full_date.split(",")[0].split(" ")[0]))

    # The date ISO format requires that single numbers are preceded by a 0.

    if int(month_num) <= 9:
        month_num = "0" + str(months.index(full_date.split(",")[0].split(" ")[0]))

    day_nth = str(full_date.split(",")[0].split(" ")[1])
    day = day_nth.strip("".join(re.findall("[a-z]", day_nth)))

    if zero_day:
        if int(day) <= 9:
            day = day_nth.strip("".join(re.findall("[a-z]", day_nth)))
    else:
        if int(day) <= 9:
            day = "0" + day_nth.strip("".join(re.findall("[a-z]", day_nth)))

    return date.fromisoformat(year + month_num + day)


def search_files_by_ext(
    extension: str, folder: str, recursive: bool = False, parent=False
) -> list[str]:
    """This function searches for files with the specified extension
    and returns a list with the files in either parent or current working directories.

    :param recursive: Recursive file search.
    :param extension: with or without extension dot
    :param parent: Searches in the parent directory if ``True``. Default ``False``.
    :param folder: ``str`` folder name
    :return: ``list[str]``
    """
    search_files = clean_filename("*", extension)
    if recursive:
        return glob.glob(
            is_parent_dir_required(parent) + f"{folder}/*/{search_files}",
            recursive=recursive,
        )
    else:
        return [
            route.split("/")[-1:][0]
            for route in glob.glob(
                is_parent_dir_required(parent) + f"{folder}/{search_files}"
            )
        ]


def write_to_file(filename: str, folder: str, extension: str, stream: Any) -> None:
    """Write to file initializes a context manager to write a stream of data to a file with
    an extension specified by the user. This helper function reduces the need to repeat the code
    needed for this kind of operation.
    The function uses a relative path and the parent parameter
    will dictate whether the file is located alongside the source file.

    :param filename: -> Self-explanatory. Handles filenames with or without extension.
    :param folder: Destination folder for the file.
    :param extension: File extension that will be enforced for the file type.
    :param stream: stream data or data structure to be writen or converted into a file.
    :return: ``None`` -> It creates a file
    """
    f_name = clean_filename(filename, extension)
    with open(
        f"{os.path.abspath(folder)}/{f_name}",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(str(stream))
    print(f"Created file {f_name} in {os.path.abspath(folder)}")
    return None


def write_config_file(
    filename: str, package: str, section: str, option: str, value: str
) -> None:
    """Modify specific sections, options and values in an .ini configuration file.

    :param filename: ``str`` .ini config filename.
    :param package: ``str`` origin package in the project.
    :param section: ``str`` config section header name.
    :param option: ``str`` config option.
    :param value: ``str`` config option value.
    :return: ``None`` (Writes .ini config file)
    """
    config = parse_client_config(filename, package)
    config.set(section, option, str(value))
    with open(os.environ.get("CLIENT_INFO_PATH"), "w") as update:
        config.write(update)
    return None


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
            f"magick {img} -quality {quality} {img[0]}/{get_file(img)}", shell=True
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
    """Generate random string of ASCII characters based on a sample size ``k``.

    :param k: ``int`` Number of letters per random string or "sample size"
    :return: ``str``
    """
    letters = string.ascii_letters
    random_string = "".join(random.choices(letters, k=k))
    return random_string


def split_char(
    raw_str: Optional[str], placeholder: str = "-1", char_lst: bool = False
) -> str | list[str]:
    """
    Identify the split character dynamically in order that str.split() knows what
    the correct separator is. In this project, the most relevant separators are ``,`` and
    ``;`` as whitespaces are not as important. However, if the only non-alphanumeric character of
    the string is a whitespace, the function has to return it. Additional parameters
    help with complementary logic and graceful error handling.

    By design, this implementation assumes that, if there are more separators, the first one
    in the match list may not be relevant for the purpose; therefore, it discards all
    whitespaces and focuses on other special characters. This is so because it is common to
    separate words with a whitespace at first and then use another separator, one that is really
    meant to be a separator; for example, in the case ``colorful skies; great landscape;...`` whitespace
    is not the real separator.

    :param raw_str: ``str`` with or without separators
    :param placeholder: ``str`` - Return this character if there is no separator. Default: ``"-1"``
    :param char_lst: ``bool`` - Return a list of unique separators instead of a single one.
    :return: ``str`` | ``list[str]``
    """
    try:
        chars = re.findall(r"[\W_]+", raw_str)
    except TypeError:
        return placeholder

    if chars:
        if len(chars) == 1:
            return chars[0]
        else:
            ch_lst = list(set(chars))
            if char_lst:
                return ch_lst
            else:
                try:
                    filtered = list(filter(lambda ch: ch != " ", ch_lst))
                    return filtered[0]
                except IndexError:
                    return placeholder
    elif char_lst:
        return list(raw_str)
    else:
        return placeholder
