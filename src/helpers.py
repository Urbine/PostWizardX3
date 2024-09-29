"""
This module stores the helper functions that collaborate
with other local implementations.
This file also adds bits of reusable business logic from other modules.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__  = "yohamg@programmer.net"

import csv
import glob
import json
import os
import re
import urllib
import urllib.request
import urllib.error

from datetime import date

from bs4 import BeautifulSoup
from calendar import month_abbr, month_name
from requests_oauthlib import OAuth2Session

# This way OAuthlib won't enforce HTTPS connections.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def access_url_bs4(url_to_bs4: str) -> BeautifulSoup:
    """Accesses a URL and returns a BeautifulSoup object that's ready to parse.
    :param url_to_bs4: (str) URL
    :return: bs4.BeautifulSoup object
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_to_bs4, None, headers)
    page = urllib.request.urlopen(request)
    return BeautifulSoup(page, 'html.parser')

def access_url(url_raw: str):
    """ Accesses a URL and returns a http.client.HTTPResponse object
    :param url_raw: (str) URL
    :return: http.client.HTTPResponse object
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_raw, None, headers)
    page = urllib.request.urlopen(request)
    return page

def clean_filename(filename: str, extension: str=None) -> str:
    """This function handles filenames with and without extension
    and avoids breaking functions that work with filenames and paths.
    Here you can pass filenames with or without extension and enforce a file type
    without expecting a user to pass in a correct filename.extension every time.

    In case that you don't pass an extension, the function will return the filename without
    any modifications. I call that a 'trust' mode.

    :param filename: str -> self-explanatory
    :param extension: str -> self-explanatory
    :return: str (New filename)
    """
    # This has some applications to avoid additional logic or error handling
    # in other functions.
    # TODO: Fix clean_filename('com.example', 'com') and clean_filename('plares.co', '.uk')

    if filename == '':
        return filename
    elif not isinstance(filename, str):
        raise TypeError("Filename must be a string.")
    elif not isinstance(extension, str):
        raise TypeError("Extension must be a string.")
    else:
        pass

    if re.findall("[.+]", extension):
        if re.findall(extension.split('.')[0], filename):
            return filename.split('.')[0] + extension
        else:
            return filename + extension
    elif extension is None:
        # This is a kind of "trust" mode.
        return filename
    elif re.findall(extension, filename):
        if re.findall("[.+]", filename):
            return filename.split('.')[0] + '.' + extension
        else:
            return filename + '.' + extension
    else:
        return filename + '.' + extension


def clean_path(folder: str, prefix: bool = False):
    if folder == '':
        return folder
    elif not isinstance(folder, str):
        raise TypeError("Filename must be a string.")
    else:
        pass

    if prefix:
        return '/' + folder + '/'
    else:
        return folder + '/'


def cwd_or_parent_path(parent: bool=False) -> str:
    """This function gets an absolute path that works with other functions to point out
    where files are being stored (parent or current working directory).
    :param parent: bool that will be gathered by parent functions.
    :return: str: absolute path string, not a path object.
    """
    if parent:
        return os.path.dirname(os.getcwd())
    else:
        return os.getcwd()

def filename_creation_helper(suggestions: list[str], extension: str='') -> str:
    """Takes a list of suggested filenames or creates a custom filename from user input.
    a user can type in just a filename without extension and the function will validate
    it to provide the correct name as needed.
    :param suggestions: list with the suggested filenames
    :param extension: file extension depending on what kind of file you want the user to create.
    :return: Filename either suggested or validated from user input.
    """
    name_suggest = suggestions
    print('Suggested filenames:\n')
    for num, file in enumerate(name_suggest, start=1):
        print(f'{num}. {file}')

    name_select = input('\nPick a number to create your file or else type in a name now: ')
    try:
        return name_suggest[int(name_select) - 1]
    except ValueError or IndexError:
        if len(name_select.split(".")) >= 2:
            return name_select
        elif name_select == '':
            raise RuntimeError("You really need a database name to continue.")
        else:
            return clean_filename(name_select, extension)

def filename_select(extension: str, parent: bool=False) -> str:
    """
    Gives you a list of files with a certain extension.
    :param extension: File extension of the files that interest you.
    :param parent: Bool, True to search in parent dir, default set to False.
    :return: File name without relative path.
    If you want to access the file from a parent dir,
    either let the destination function handle it for you or specify it yourself.
    """
    available_files = search_files_by_ext(extension, folder='', parent=parent)
    print(f'\nHere are the available {extension} files:')
    for num, file in enumerate(available_files, start=1):
        print(f'{num}. {file}')

    select_file = input(f'\nSelect your {extension} file now: ')
    try:
        return available_files[int(select_file) - 1]
    except IndexError:
        raise RuntimeError(f'This program requires a {extension} file. Exiting...')

def export_request_json(filename: str,
                        stream,
                        indent: int = 1,
                        parent: bool=False) -> str:
    """ This function writes a JSON file to either your parent or current working dir
    :param filename: (str) Filename with or without JSON extension.
    :param stream: (json) Data stream to export to JSON
    :param indent: (int) Indentation spaces. Default 1
    :param parent: (bool) Place file in parent directory if True. Default False.
    :return: (None) print statement for console logging.
    """
    f_name = clean_filename(filename,'.json')
    filename = is_parent_dir_required(parent) + f_name
    f_path = cwd_or_parent_path(parent)

    with open(f'{filename}', 'w', encoding='utf-8') as t:
        json.dump(stream, t, ensure_ascii=False, indent=indent)
    return f_path


def export_to_csv_nt(nmedtpl_lst: list, filename: str, top_row_lst: list[str]) -> None:
    """Helper function to dump a list of NamedTuples into a CSV file in current working dir.
    :param nmedtpl_lst: list[namedtuple]
    :param filename: name (without csv extension)
    :param top_row_lst: list[str]
    :return: None (file in project root)
    """
    with open(filename + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', )
        writer.writerow(top_row_lst)
        for tag in nmedtpl_lst:
            try:
                writer.writerow([getattr(tag, f) for f in tag._fields])
            except IndexError:
                continue
    return None

def get_token_oauth(client_id_: str,
                    uri_callback_: str,
                    client_secret_: str,
                    auth_url_: str,
                    token_url_: str) -> json:
    """ Uses the OAuth2Session module from requests_oauthlib to obtain an
    authentication token for compatible APIs. All parameters are self-explanatory.
    :param client_id_: (str)
    :param uri_callback_: (str)
    :param client_secret_: (str)
    :param auth_url_: (str)
    :param token_url_: (str)
    :return: json object
    """
    oauth_session = OAuth2Session(client_id_, redirect_uri=uri_callback_, )
    authorization_url, state = oauth_session.authorization_url(auth_url_)
    print(f'Please go to {authorization_url} and authorize access.')
    authorization_response = input('Enter the full callback URL: ')
    token = oauth_session.fetch_token(
        token_url_,
        authorization_response=authorization_response,
        client_secret=client_secret_)
    return token

def is_parent_dir_required(parent: bool) -> str:
    """
    This function returns a string to be used as a relative path that works
    with other functions to modify the where files are being stored
    or located (either parent or current working directory).
    :param parent: bool that will be gathered by parent functions.
    :return: str. Empty string in case the parent variable is not provided.
    """
    if parent:
        return '../'
    elif parent is None:
        return ''
    else:
        return './'


def if_exists_remove(fname: str, parent: bool = False):
    """Removes a file only if it exists in either parent or current working directory.
    :param parent: Set to 'True' if you need to look for your file in the parent dir.
    :param fname: File name
    :return: Returns none if the file does not exist
    """
    if os.path.exists(fname):
        os.remove(fname)
    else:
        return None


def get_client_info(filename: str, parent: bool=False):
    """
    :return: json object
    """
    f_name = clean_filename(filename, '.json')
    in_parent = is_parent_dir_required(parent)

    try:
        with open(f'{in_parent}{f_name}', 'r', encoding='utf-8') as secrets:
            client_info = json.load(secrets)
        return client_info
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        return None

def load_json_ctx(filename: str, parent: bool=False, log_err: bool = False):
    """ This function makes it possible to assign a JSON file from storage to a variable.
    :param logerr: True if you want to print error information, default False.
    :param parent: Looks for the JSON file in the parent directory if True, default False.
    :param filename: (str) filename
    :return: json object
    """
    parent_or_cwd = is_parent_dir_required(parent)
    json_file = clean_filename(filename, 'json')

    try:
        with open(f"{parent_or_cwd}{json_file}", 'r', encoding='utf-8') as f:
            imp_json = json.load(f)
        return imp_json
    except FileNotFoundError:
        if log_err:
            print(f"File {parent_or_cwd}{json_file} not found! Double-check the filename.")
        return None

def load_from_file(filename: str, extension: str, parent=False):
    """ Loads the content of any file that could be read with the file.read()
    Not suitable for files that require special handling by modules or classes.
    :param extension: file extension of the file to be read
    :param parent: Looks for the file in the parent directory if True, default False.
    :param filename: (str) filename
    :return: str
    """
    parent_or_cwd = is_parent_dir_required(parent)
    file = clean_filename(filename, extension)

    try:
        with open(f"{parent_or_cwd}{file}", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        return None

def parse_date_to_iso(full_date: str, m_abbr: bool=False) -> date:
    """Breaks down the full date string and converts it to ISO format to get a datetime.date object.
    important: Make sure to import 'from calendar import month_abbr, month_name' as it is required.
    :param full_date: date_full is 'Aug 20th, 2024' or 'August 20th, 2024'.
    :param m_abbr: Set to True if you provide a month abbreviation e.g. 'Aug', default set to False ().
    :return: date object (ISO format)
    """
    # Lists month_abbr and month_name provided by the built-in Calendar library in Python.
    if m_abbr:
        months = [m for m in month_abbr]
    else:
        months = [m for m in month_name]

    year = str(full_date.split(",")[1].strip())
    month_num = str(months.index(full_date.split(",")[0].split(" ")[0]))

    # The date ISO format requires that single numbers are preceded by a 0.
    if int(month_num) <= 9:
        month_num = '0' + str(months.index(full_date.split(",")[0].split(" ")[0]))

    day_nth = str(full_date.split(",")[0].split(" ")[1])
    day = day_nth.strip("".join(re.findall("[a-z]", day_nth)))

    if int(day) <= 9:
        day_date = '0' + day_nth.strip("".join(re.findall("[a-z]", day_nth)))

    return date.fromisoformat(year + month_num + day)

def search_files_by_ext(extension: str, folder:str, parent: bool = False) -> list[str]:
    """This function searches for files with the specified extension
    and returns a list with the files in either parent or current working directories.
    :param extension: with or without dot
    :param parent: Searches in the parent directory if True, default False.
    :param folder: str folder name
    :return: list[str]
    """
    # uses the clean_filename function to receive extension with or without dot.
    search_files = clean_filename('*', extension)
    clean_folder = clean_path(folder)
    return [route.split('/')[-1:][0]
            for route in glob.glob(is_parent_dir_required(parent)+ f'/{clean_folder}{search_files}')]

def write_to_file(filename: str, extension: str, stream, parent: bool=False) -> None:
    """

    :param filename:
    :param extension:
    :param stream:
    :param parent:
    :return:
    """
    f_name = clean_filename(filename, extension)
    with open(f'{is_parent_dir_required(parent=parent)}{f_name}', 'w', encoding='utf-8') as file:
        file.write(str(stream))
    print(f'Created file {f_name} in {cwd_or_parent_path(parent=parent)}')
    return None

