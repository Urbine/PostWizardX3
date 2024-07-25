# This code will be used by several files in this project.

import json
import os
import requests
import urllib
import urllib.request
import urllib.error

from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session

# This way OAuthlib won't enforce HTTPS connections.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def get_client_info() -> json:
    with open('client_info.json', 'r', encoding='utf-8') as secrets:
        client_info = json.load(secrets)
    return client_info


def get_token_oauth(client_id_, uri_callback_, client_secret_, auth_url_, token_url_) -> None:
    oauth_session = OAuth2Session(client_id_, redirect_uri=uri_callback_, )
    authorization_url, state = oauth_session.authorization_url(auth_url_)
    print(f'Please go to {authorization_url} and authorize access.')
    authorization_response = input('Enter the full callback URL: ')
    token = oauth_session.fetch_token(
        token_url_,
        authorization_response=authorization_response,
        client_secret=client_secret_)
    with open('token.json', 'w', encoding='utf-8') as t:
        json.dump(token, t, ensure_ascii=False, indent=4)
    return print("Token stored in project root. Ready to use!")


def access_url_bs4(url_to_bs4) -> BeautifulSoup:
    # type(str) -> BeautifulSoup object
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_to_bs4, None, headers)
    page = urllib.request.urlopen(request)
    return BeautifulSoup(page, 'html.parser')


def access_url(url_raw):
    # type(str) -> BeautifulSoup object
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url_raw, None, headers)
    page = urllib.request.urlopen(request)
    return page


def import_token_json() -> json:
    with open('token.json', 'r', encoding='utf-8') as t:
        imp_tokn = json.load(t)
    return imp_tokn


if __name__ == '__main__':
    access_url()
    access_url_bs4()
    get_client_info()
    get_token_oauth()
    import_token_json()
