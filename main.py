# This code will be used by several files in this project.

import csv
import json
import os

import urllib
import urllib.request
import urllib.error

from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session

# This way OAuthlib won't enforce HTTPS connections.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def get_client_info() -> json:
    """
    :return: json object
    """
    try:
        with open('client_info.json', 'r', encoding='utf-8') as secrets:
            client_info = json.load(secrets)
        return client_info
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        print("Don't add the .json extension to the function.")
        return None


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


def import_request_json(filename) -> list:
    """
    :param filename: (str) filename without JSON extension
    :return: json object
    """
    try:
        with open(f"{filename}.json", 'r', encoding='utf-8') as f:
            imp_json = json.load(f)
        return imp_json
    except FileNotFoundError:
        print("File not found! Double-check the filename.")
        print("Don't add the .json extension to the function.")
        return None


def export_request_json(filename, stream, indent) -> None:
    """
    :param filename: (str) Filename without JSON extension.
    :param stream: (json) Data stream to export to JSON
    :param indent: (int) Indentation spaces
    :return: (None) print statement for console logging.
    """
    with open(f'{filename}.json', 'w', encoding='utf-8') as t:
        json.dump(stream, t, ensure_ascii=False, indent=indent)
    return print("The file has been stored in project root. Ready to use!")


def export_to_csv(nmedtpl_lst, filename, top_row_lst) -> None:
    """
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


if __name__ == '__main__':
    access_url()
    access_url_bs4()
    get_client_info()
    get_token_oauth()
    import_request_json()
    export_request_json()
