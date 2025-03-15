"""
Photo set HTML Source Parser module

This module parses source code to collect metadata and links to create a photo set database
from MongerCash.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

# Standard Library
import datetime
import os
import re
import sqlite3


# Third-party library
from bs4 import BeautifulSoup

# Local implementation
from core import helpers, remove_if_exists


def parse_titles(soup_html: BeautifulSoup) -> list[str]:
    """Parses all photo set titles from the source file or ``BeautifulSoup``
    element provided.

    :param soup_html: ``BeautifulSoup`` object
    :return: ``list[str]``
    """
    titles = soup_html.find_all("td", attrs={"class": "tab-column left-align col_0"})
    return list(map(lambda td: td.text, titles))


def parse_dates(soup_html: BeautifulSoup) -> list[datetime.date]:
    """Parses all photo set dates from the source file or BeautifulSoup
    element provided and returns a list of datetime.date objects.

    :param soup_html: ``BeautifulSoup`` object
    :return: ``list[datetime.date]``
    """
    dates = soup_html.find_all("td", attrs={"class": "tab-column col_1 center-align"})

    def parse_date(td):
        return helpers.parse_date_to_iso(td.text.strip(), zero_day=True, m_abbr=False)

    return list(map(parse_date, dates))


def parse_links(soup_html: BeautifulSoup) -> list[str]:
    """Parses all photo set links from the source file or ``BeautifulSoup``
    element provided. Returns perfectly formed links that will be used to
    download the sets.

    :param soup_html: ``BeautifulSoup`` object
    :return: list[str]
    """
    base_url = "https://mongercash.com/"
    ziptool_links = soup_html.find_all("a")

    def make_link(td):
        return f"{base_url}{td.attrs['href']}"

    def match_ziptool(td):
        return bool(re.match("zip_tool", td.attrs["href"]))

    return list(map(make_link, filter(match_ziptool, ziptool_links)))


def db_generate(
    soup_html: BeautifulSoup, db_suggest: list[str] | str, parent: bool = False
) -> tuple[str, int]:
    """As its name describes, it puts all the information that previous
    functions returned into a SQLite db.

    :param soup_html: ``BeautifulSoup`` object
    :param db_suggest: List with name suggestions for your db files or string.
    :param parent: ``bool`` ``True`` if you want to generate the database in your parent dir. Default ``False``
    :return: ``tuple[str, int]`` (db_path, total_entries)
    """
    set_titles = parse_titles(soup_html)
    set_dates = parse_dates(soup_html)
    set_links = parse_links(soup_html)

    if isinstance(db_suggest, list):
        d_name = helpers.filename_creation_helper(db_suggest, extension="db")
    else:
        d_name = helpers.clean_filename(db_suggest, "db")

    db_path = os.path.join(helpers.is_parent_dir_required(parent), d_name)
    remove_if_exists(db_path)
    db_conn = sqlite3.connect(db_path)
    cursor = db_conn.cursor()
    cursor.execute("CREATE TABLE sets(title, date, link)")
    # Sum of entered into the db.
    total_photosets = 0
    all_values = zip(set_titles, set_dates, set_links)
    for vals in all_values:
        cursor.execute("INSERT INTO sets VALUES(?, ?, ?)", vals)
        db_conn.commit()
        total_photosets += 1

    cursor.close()
    db_conn.close()
    db_path = os.path.join(helpers.is_parent_dir_required(parent), d_name)

    return db_path, total_photosets
