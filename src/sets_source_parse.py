"""
This module parses source code and creates a photo set database
from MongerCash.
Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__  = "yohamg@programmer.net"

# Std Library
import os
import re
import sqlite3
from datetime import datetime

# Third-party library
from bs4 import BeautifulSoup

# Local implementation
import helpers

def parse_titles(soup_html: BeautifulSoup) -> list[str]:
    """ Parses all photo set titles from the source file or BeautifulSoup
    element provided.
    :param soup_html: BeautifulSoup object
    :return: list[str]
    """
    titles = soup_html.find_all('td',
                                attrs={'class': 'tab-column left-align col_0'})
    return [td.text for td in titles]

def parse_dates(soup_html: BeautifulSoup) -> list[datetime.date]:
    """ Parses all photo set dates from the source file or BeautifulSoup
    element provided and returns a list of datetime.date objects.
    :param soup_html: BeautifulSoup object
    :return: list[datetime.date]
    """
    dates = soup_html.find_all('td',
                               attrs={'class': 'tab-column col_1 center-align'})
    return [helpers.parse_date_to_iso(td.text.strip(), zero_day=True, m_abbr=False)
            for td in dates]

def parse_links(soup_html: BeautifulSoup) -> list[str]:
    """Parses all photo set links from the source file or BeautifulSoup
    element provided. Returns perfectly formed links that will be used to
    download the sets.
    :param soup_html: BeautifulSoup object
    :return: list[str]
    """
    base_url = 'https://mongercash.com/'
    ziptool_links = soup_html.find_all('a')
    return [f"{base_url}{td.attrs['href']}" for td in ziptool_links
            if re.match('zip_tool', td.attrs['href'])]

def db_generate(soup_html: BeautifulSoup, db_suggest: list[str]):
    """ As its name describes, it puts all the information that previous
    functions returned into a SQLite db.
    :param soup_html: BeautifulSoup object
    :param db_suggest: List with name suggestions for your db files.
    :return:
    """
    set_titles = parse_titles(soup_html)
    set_dates = parse_dates(soup_html)
    set_links = parse_links(soup_html)
    db_name = helpers.filename_creation_helper(db_suggest, extension = 'db')
    db_conn = sqlite3.connect(f"{helpers.is_parent_dir_required(parent=True)}{db_name}")
    cursor = db_conn.cursor()
    cursor.execute("CREATE TABLE sets(title, date, link)")
    # Sum of entered into the db.
    sum = 0
    all_values = zip(set_titles, set_dates, set_links)
    for vals in all_values:
        cursor.execute("INSERT INTO sets VALUES(?, ?, ?)", vals)
        db_conn.commit()
        sum += 1
    db_conn.close()
    db_path = f'{os.path.dirname(os.getcwd())}/{db_name}'
    clean_fname = helpers.clean_filename(html_filename,"html")
    print(f'\n{sum} photo set entries have been processed from {clean_fname} and inserted into\n{db_path}')

html_filename = helpers.filename_select('html', parent=True)
source = helpers.load_from_file(html_filename,
                                'html', parent=True)

soup = BeautifulSoup(source,'html.parser')

db_name_suggest = ["asian_sex_diary_photo_sets.db",
                       "trike_patrol_photo_sets.db",
                       "tuktuk_patrol_photo_sets.db"]

db_generate(soup, db_name_suggest)