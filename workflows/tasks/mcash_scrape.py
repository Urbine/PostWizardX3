"""
MongerCash Web Automation Module

This module provides web automation functionality for extracting content from MongerCash.
It contains functions for:

1. Extracting video metadata (titles, descriptions, dates, durations)
2. Extracting media links (source URLs, thumbnails)
3. Retrieving XML export data
4. Automating authentication and site navigation

While originally designed as a comprehensive parser for direct source code extraction,
its primary current use is obtaining the full source code of pages for further
processing by the specialized parser in `tasks.sets_source_parse`.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import datetime

# Third-party modules
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By


# Local module implementations
from core.models.config_model import WebSourcesConf
from core.models.secret_model import SecretType, MongerCashAuth
from core.config.config_factories import web_sources_conf_factory
from core.utils.secret_handler import SecretHandler
from core.utils.strings import match_list_single
from .mcash_dump_create import parse_partner_name


def extract_descriptions(bs4_obj: BeautifulSoup) -> list[str]:
    """Extract  video descriptions from HTML source
    ``<td><textarea class="display-link-text" rows="2">description text</textarea></td>``

    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    #
    text_areas = bs4_obj.find_all(
        "textarea", attrs={"class": "display-link-text", "rows": "2"}
    )
    # All descriptions are located in even positions followed by ``<script>``
    # elements in uneven positions. This is the easiest approach, I guess.
    return [
        txt_area.text
        for num, txt_area in enumerate(text_areas, start=1)
        if num % 2 == 0
    ]


def extract_title(bs4_obj: BeautifulSoup) -> list[str]:
    """Extract a video title from HTML Source
    ``<td class="tab-column col_0 center-align">video title</td>``

    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    vid_title = bs4_obj.find_all("td", attrs={"class": "tab-column col_0 center-align"})
    return [title.text for title in vid_title]


def extract_date(bs4_obj: BeautifulSoup) -> list[str]:
    """Extract post/upload date from HTML Source
    ``<td class="tab-column col_1 center-align">Sep  4, 2024</td>``
    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    #
    vid_date = bs4_obj.find_all("td", attrs={"class": "tab-column col_1 center-align"})
    return [date.text for date in vid_date]


def extract_duration(bs4_obj: BeautifulSoup) -> list[str]:
    """Extract video duration information from HTML Source
    ``<td class="tab-column col_2 center-align">4 Min</td>``

    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    #
    vid_duration = bs4_obj.find_all(
        "td", attrs={"class": "tab-column col_2 center-align"}
    )
    return [duration.text for duration in vid_duration]


# Video thumbnail & source link are together
# <video class="video_holder_14126 table-video-small" controls="" poster="
# https://xyz.com/ttp/video/video_thumbnail.jpg">
# <source src="https://xyz.com/ttp/video/video_file.mp4" type="video/"/>
# </video>


def extract_source(bs4_obj: BeautifulSoup) -> list[str]:
    """Extract video source URL from HTML source
    ``<source src="https://xyz.com/ttp/video/video_file.mp4" type="video/"/>``

    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    video_source = bs4_obj.find_all("source")
    return [source.attrs["src"] for source in video_source]


def extract_thumbnail(bs4_obj: BeautifulSoup) -> list[str]:
    """Extract thumbnail link from HTML Source
    ``<video class="video_holder_14126 table-video-small" controls=""
    poster="https://xyz.com/ttp/video/video_thumbnail.jpg"></video>``

    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    video_thumb = bs4_obj.find_all("video")
    return [thumb.attrs["poster"].strip("\n\t") for thumb in video_thumb]


def combine_vid_elems(bs4_obj: BeautifulSoup) -> list[tuple[str, str, str, str, str]]:
    """Combine all elements in a common data structure with the values returned by other functions.

    :param bs4_obj: `BeautifulSoup``
    :return: ``list[tuple[str, str, str, str, str]]`` `(title, descriptions, date, source, thumbnail)`
    """
    page_vids = zip(
        extract_title(bs4_obj),
        extract_descriptions(bs4_obj),
        extract_date(bs4_obj),
        extract_source(bs4_obj),
        extract_thumbnail(bs4_obj),
    )
    return list(page_vids)


def get_xml_link(bs4_obj: BeautifulSoup) -> list[str]:
    """Get an XML dump file from the HTML source for further parsing
    ``<a href="internal.php?... class="linkcode-view" id="xml_1" target="_blank" title="Export as XML">``

    :param bs4_obj: ``BeautifulSoup``
    :return: ``list[str]``
    """
    a_xml = bs4_obj.find_all("a", attrs={"title": "Export as XML"})
    # There is only one link with this ``title`` attribute
    return [a.attrs["href"] for a in a_xml][0]


def xml_tag_text(bs4_xml: BeautifulSoup, elem_tag: str) -> str:
    """Get tag information from a specific tag from XML source.

    :param bs4_xml: ``BeautifulSoup``
    :param elem_tag: ``str`` tag name
    :return: ``str`` tag information
    """
    title = bs4_xml.find(elem_tag)
    return title.text


def get_set_source_flow(
    webdrv: webdriver,
    web_sources_conf: WebSourcesConf = web_sources_conf_factory(),
    mcash_auth: MongerCashAuth = SecretHandler().get_secret(
        SecretType.MONGERCASH_PASSWORD
    )[0],
    partner_hint: str = None,
) -> tuple[BeautifulSoup, str]:
    """Get the photo set source code for further parsing.
    This source file will be parsed by a specialised parser in this package.

    :param webdrv: ``webdriver`` Chrome/Gecko webdriver instance
    :param web_sources_conf: ``TasksConf`` object with configuration for task modules
    :param mcash_auth: ``MongerCashAuth`` with credentials to access the partner site.
    :param partner_hint: ``str`` pattern to match the correct partner offer
    :return: ``tuple[BeautifulSoup, str]`` (source_code, filename)
    """
    source_html = None
    with webdrv as driver:
        # Go to URL
        driver.get(web_sources_conf.mcash_set_url)

        driver.implicitly_wait(30)

        username_box = driver.find_element(By.ID, "user")
        pass_box = driver.find_element(By.ID, "password")

        username_box.send_keys(mcash_auth.username)
        pass_box.send_keys(mcash_auth.password)

        button_login = driver.find_element(By.ID, "head-login")
        button_login.click()

        website_partner = driver.find_element(By.ID, "link_site")
        website_partner_select = Select(website_partner)
        partner_options = website_partner_select.options

        if partner_hint:
            selection = match_list_single(
                partner_hint, partner_options, ignore_case=True
            )
        else:
            for num, opt in enumerate(partner_options, start=0):
                print(f"{num}. {opt.text}")

            selection = input("Enter a number and select a partner: ")

        website_partner_select.select_by_index(int(selection))
        partner_name = parse_partner_name(partner_options, int(selection))

        apply_changes_xpath = (
            "/html/body/div[1]/div[2]/form/div/div[2]/div/div/div[6]/div/div/input"
        )
        apply_changes_button = driver.find_element(By.XPATH, apply_changes_xpath)
        apply_changes_button.click()

        # Refresh the page to avoid loading status crashes in Chrome
        driver.refresh()

        # Increase videos per page before dumping to XML
        vids_per_page = driver.find_element(By.ID, "page-count-val")

        vid_select = Select(vids_per_page)

        # Selecting `Show All` by default in index 5
        vid_select.select_by_index(5)

        update_submit_button = driver.find_element(By.ID, "pageination-submit")
        update_submit_button.click()

        source_html = BeautifulSoup(driver.page_source, "html.parser")

    return source_html, f"{partner_name}photos-{datetime.date.today()}"
