# This code will be used by several files in this project.

import csv
import glob
import json
import os
import re
import urllib
import urllib.request
import urllib.error

from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session

# This way OAuthlib won't enforce HTTPS connections.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

def cwd_or_parent_path(parent: bool) -> str:
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

def get_client_info(filename: str, parent: bool) -> json:
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
        print("Don't add the .json extension to the function.")
        return None

def search_files_by_ext(extension: str, parent=False, folder='') -> list[str]:
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
            for route in glob.glob(is_parent_dir_required(parent)+ f'/{folder}{search_files}')]


def get_token_oauth(client_id_, uri_callback_, client_secret_, auth_url_, token_url_) -> json:
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


def access_url_bs4(url_to_bs4) -> BeautifulSoup:
    """
    :param url_to_bs4: (str) URL
    :return: bs4.BeautifulSoup object
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_to_bs4, None, headers)
    page = urllib.request.urlopen(request)
    return BeautifulSoup(page, 'html.parser')


def access_url(url_raw):
    """
    :param url_raw: (str) URL
    :return: http.client.HTTPResponse object
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_raw, None, headers)
    page = urllib.request.urlopen(request)
    return page


def import_request_json(filename, parent=False) -> list:
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


def export_request_json(filename, stream, indent=1, parent=False) -> None:
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


def export_to_csv_nt(nmedtpl_lst, filename, top_row_lst) -> None:
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


def database_select(parent=False) -> str:
    available_dbs = search_files_by_ext('db', parent=parent)
    print('\nHere are the available .db files:')
    for num, db in enumerate(available_dbs, start=1):
        print(f'{num}. {db}')

    select_db = input('\nSelect your database now: ')
    try:
        return is_parent_dir_required(parent=parent) + available_dbs[int(select_db) - 1]
    except IndexError:
        raise RuntimeError('This program requires a database. Exiting...')

# Removing this as it is not necessary.
# if __name__ == '__main__':
#     access_url()
#     access_url_bs4()
#     clean_filename()
#     cwd_or_parent_path()
#     database_select()
#     export_request_json()
#     get_client_info()
#     get_token_oauth()
#     import_request_json()
#     is_parent_dir_required()
#     search_files_by_ext()

