"""
Data Access Utilities
This module contains functions to access data from the web and databases.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
import sqlite3
import urllib
from sqlite3 import Connection, Cursor
from typing import Any, Optional, Dict

from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session
from selenium import webdriver

# Local imports
from core.utils.file_system import is_parent_dir_required, filename_select


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


def fetch_data_sql(
    sql_query: str, db_cursor: sqlite3.Cursor
) -> Optional[list[tuple[str | int, ...]]]:
    """Takes a SQL query in string format and returns the data
    in a list of tuples. In case there is no data, the function returns None.

    :param sql_query: SQL Query string.
    :param db_cursor: Database connection cursor.
    :return: ``list[tuple]``
    """
    db_cursor.execute(sql_query)
    return db_cursor.fetchall()


def get_token_oauth(
    client_id_: str,
    uri_callback_: str,
    client_secret_: str,
    auth_url_: str,
    token_url_: str,
) -> Dict[str, str]:
    """Uses the OAuth2Session module from requests_oauthlib to obtain an
    authentication token for compatible APIs. All parameters are self-explanatory.

    :param client_id_: ``str``
    :param uri_callback_: ``str``
    :param client_secret_: ``str``
    :param auth_url_: ``str``
    :param token_url_: ``str``
    :return: ``JSON`` object
    """
    # This way OAuthlib won't enforce HTTPS connections (Optional)
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

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
