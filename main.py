# This code will be used by several files


import json
import urllib
import urllib.request
import urllib.error

from bs4 import BeautifulSoup


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


def get_client_info() -> json:
    with open('client_info.json', 'r', encoding='utf-8') as secrets:
        client_info = json.load(secrets)
    return client_info


if __name__ == '__main__':
    access_url()
    access_url_bs4()
    get_client_info()
