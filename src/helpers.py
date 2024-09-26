# This code will be used by several files in this project.

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
    """
    :param url_to_bs4: (str) URL
    :return: bs4.BeautifulSoup object
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_to_bs4, None, headers)
    page = urllib.request.urlopen(request)
    return BeautifulSoup(page, 'html.parser')

def access_url(url_raw: str):
    """
    :param url_raw: (str) URL
    :return: http.client.HTTPResponse object
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_raw, None, headers)
    page = urllib.request.urlopen(request)
    return page

def clean_filename(filename: str, extension: str=None) -> str:
    """
    This function gets a clear filename and handles filenames with and
    without extension and avoid breaking functions that work with filenames.
    :param filename: str -> self-explanatory
    :param extension: str -> self-explanatory
    :return: str (New filename)
    """
    if filename is None:
        raise RuntimeError(f'You need a filename to continue.')

    if re.findall("[.+]", extension):
        pass
    # This is a kind of "trust" mode.
    elif extension is None:
        return filename
    else:
        extension = '.' + extension

    if len(filename.split(".")) >= 2:
        # The user entered a value which included an extension.
        # and the extension must match what I need.
        return filename.split(".")[0] + extension
    else:
        return filename + extension

def cwd_or_parent_path(parent: bool=False) -> str:
    """
    This function gets a text that works with other functions to point out
    where files are being stored (parent directory or current directory).
    :param parent: bool that will be gathered by parent functions.
    :return: str
    """
    if parent:
        return os.path.dirname(os.getcwd())
    else:
        return os.getcwd()

def db_creation_helper(db_suggestions: list[str]) -> str:
    """
    Takes a list of suggested names or creates a custom .db file.
    :param db_suggestions: list with the suggested db names
    :return: db name either suggested or customised
    """
    db_name_suggest = db_suggestions
    print('Suggested database names:\n')
    for num, db in enumerate(db_name_suggest, start=1):
        print(f'{num}. {db}')

    db_name_select = input('\nPick a number to create your database or else type in a name now: ')
    try:
        return db_name_suggest[int(db_name_select) - 1]
    except ValueError or IndexError:
        if len(db_name_select.split(".")) >= 2:
            return db_name_select
        elif db_name_select == '':
            raise RuntimeError("You really need a database name to continue.")
        else:
            return db_name_select + '.db'

def filename_select(extension: str, parent: bool=False) -> str:
    """
    Gives you a list of files with a certain extension.
    :param extension: File extension of the files that interest you.
    :param parent: Bool, True to search in parent dir, default set to False.
    :return: File name without relative path.
    If you want to access the file from a parent dir,
    either let the destination function handle it for you or specify it yourself.
    """
    available_files = search_files_by_ext(extension, parent=parent)
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
                        parent: bool=False) -> None:
    """
    :param filename: (str) Filename without JSON extension.
    :param stream: (json) Data stream to export to JSON
    :param indent: (int) Indentation spaces. Default 1
    :param parent: (bool) Place file in parent directory if True, default False.
    :return: (None) print statement for console logging.
    """
    f_name = clean_filename(filename,'.json')
    filename = is_parent_dir_required(parent) + f_name
    f_path = cwd_or_parent_path(parent)

    with open(f'{filename}', 'w', encoding='utf-8') as t:
        json.dump(stream, t, ensure_ascii=False, indent=indent)
    return print(f"The JSON file has been stored in {f_path}. Ready to use!\n")


def export_to_csv_nt(nmedtpl_lst: list, filename: str, top_row_lst: list[str]) -> None:
    """
    Helper function to dump the list of NamedTuples into a CSV file in project dir.
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
    """
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

def if_exists_remove(fname: str):
    """
    Removes a file if it exists.
    :param fname: File name
    :return: Returns none if the file does not exist
    """
    if os.path.exists(fname):
        os.remove(fname)
    else:
        return None

def is_parent_dir_required(parent: bool) -> str:
    """
    This function gets a text that works with other functions to modify the
    where files are being stored (parent directory or current directory).
    :param parent: bool that will be gathered by parent functions.
    :return: str. Empty string in case the parent variable is not provided.
    """
    if parent:
        return '../'
    elif parent is None:
        return ''
    else:
        return './'

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

def import_request_json(filename: str, parent: bool=False) -> list:
    """
    :param parent: Looks for the JSON file in the parent directory if True, default False.
    :param filename: (str) filename
    :return: json object
    """
    parent_or_cwd = is_parent_dir_required(parent)
    json_file = clean_filename(filename, '.json')

    try:
        with open(f"{parent_or_cwd}{json_file}", 'r', encoding='utf-8') as f:
            imp_json = json.load(f)
        return imp_json
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        return None

def load_from_file(filename: str, extension: str, parent=False) -> str:
    """
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
    """
    Break down the date and convert it to ISO format to get a datetime.date object.
    important: 'from calendar import month_abbr, month_name' is required.
    :param full_date: date_full is 'Aug 20th, 2024' or 'August 20th, 2024'.
    :param m_abbr: Set to True if you provide a month abbreviation, default set to False ().
    :return: date object (ISO format)
    """
    # Lists month_abbr and month_name provided by the Calendar library in Python.
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

def search_files_by_ext(extension: str, parent: bool = False, folder:str = '') -> list[str]:
    """
    This function returns a list of the .extension files in either parent
    or current directories.
    :param extension: with or without dot
    :param parent: Searches in the parent directory if True, default False.
    :param folder: str folder name followed by '/'
    :return: list[str]
    """
    # uses the clean_filename function to receive extension with or without dot.
    search_files = clean_filename('*', extension)
    return [route.split('/')[-1:][0]
            for route in glob.glob(is_parent_dir_required(parent)+ f'/{folder}/{search_files}')]

def write_to_file(filename: str, extension: str, stream, parent: bool=False) -> None:
    f_name = clean_filename(filename, extension)
    with open(f'{is_parent_dir_required(parent=parent)}{f_name}', 'w', encoding='utf-8') as file:
        file.write(str(stream))
    print(f'Created file {f_name} in {cwd_or_parent_path(parent=parent)}')
    return None

