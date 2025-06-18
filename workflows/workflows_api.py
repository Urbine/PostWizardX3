"""
Workflows API Module

This module consolidates reusable functionality from content selection, embedding assistance,
and gallery selection workflows. It provides a unified interface for accessing common operations
across these workflows.

The module contains a collection of utility functions that handle various aspects of the workflow
processes, including:

1. Data Processing:
   - Parsing assets and content from various sources
   - Filtering published content
   - Identifying missing elements
   - Processing thumbnails and media files

2. Payload Generation:
   - Creating structured payloads for WordPress
   - Building specialized payloads for images and galleries
   - Handling metadata and attributes

3. Content Management:
   - Generating slugs for URLs
   - File synchronization
   - Tag and model management
   - Database querying and filtering

4. Workflow Coordination:
   - Console-based user interaction
   - Session management and logging
   - Classification and tag filtering
   - Social media integration

This API serves as the backbone for the three main workflow assistants in the project:
- Content Selection (mcash_assistant.py)
- Embedding Assistance (embed_assistant.py)
- Gallery Selection (gallery_select.py)
- Data Source Update (update_manager.py) (Logging logic only)

By centralizing these functions, the module promotes code reuse and consistency
across the different workflow implementations.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

import datetime
import logging
import os
import random
import re
import tempfile
import time
import shutil
import sqlite3
import zipfile

from dataclasses import dataclass, fields
from enum import Enum
from sqlite3 import Connection, Cursor, OperationalError
from typing import TypeVar, Any, Generic, Optional
from re import Pattern

# Third-party modules
import pyclip
import requests
import rich.console
import urllib3.exceptions
from rich.console import Console
from selenium import webdriver  # Imported for type annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


# Local implementations
from core import (
    InvalidInput,
    UnsupportedParameter,
    HotFileSyncIntegrityError,
    AssetsNotFoundError,
    UnavailableLoggingDirectory,
    InvalidSQLConfig,
    get_duration,
    generate_random_str,
    parse_client_config,
    content_select_conf,
    helpers,
    wp_auth,
    clean_filename,
    x_auth,
    bot_father,
    split_char,
    UnableToConnectError,
    InvalidDB,
    monger_cash_auth,
    gallery_select_conf,
)

from integrations import (
    wordpress_api,
    x_api,
    botfather_telegram,
    WPEndpoints,
    XEndpoints,
)
from integrations.botfather_telegram import BotFatherCommands, BotFatherEndpoints
from ml_engine import classify_title, classify_description, classify_tags

# Imported for typing purposes
from core.config_mgr import (
    WPAuth,
    ContentSelectConf,
    GallerySelectConf,
    MongerCashAuth,
)

T = TypeVar("T")


class EmbedsMultiSchema(Generic[T]):
    """
    Complementary class dealing with dynamic SQL schema reading for content databases.

    EmbedsMultiSchema provides an interface to the main control flow of the bot that allows
    for direct index probing based on the present schema. This improvement will make it easier
    for the user to implement further functionality and behaviour based on specific fields.
    """

    @dataclass(frozen=True)
    class SchemaRegEx:
        """
        Immutable dataclass containing compiled RegEx patterns for class methods.
        """

        pat_slug: Pattern[str] = re.compile(r"slug", re.IGNORECASE)
        pat_embed: Pattern[str] = re.compile(r"embeds?", re.IGNORECASE)
        pat_thumbnail: Pattern[str] = re.compile(r"thumb(nail)?", re.IGNORECASE)
        pat_categories: Pattern[str] = re.compile(r"categor(ies)?", re.IGNORECASE)
        pat_rating: Pattern[str] = re.compile(r"ratings?", re.IGNORECASE)
        pat_title: Pattern[str] = re.compile(r"title", re.IGNORECASE)
        pat_link: Pattern[str] = re.compile(r"links?", re.IGNORECASE)
        pat_date: Pattern[str] = re.compile(r"date", re.IGNORECASE)
        pat_id: Pattern[str] = re.compile(r"id", re.IGNORECASE)
        pat_duration: Pattern[str] = re.compile(r"duration", re.IGNORECASE)
        pat_prnstars: Pattern[str] = re.compile(r"pornstars?", re.IGNORECASE)
        pat_models: Pattern[str] = re.compile(r"models?", re.IGNORECASE)
        pat_resolution: Pattern[str] = re.compile("resolution", re.IGNORECASE)
        pat_tags: Pattern[str] = re.compile(r"tags?", re.IGNORECASE)
        pat_likes: Pattern[str] = re.compile(r"likes?", re.IGNORECASE)
        pat_url: Pattern[str] = re.compile(r"urls?", re.IGNORECASE)
        pat_description: Pattern[str] = re.compile(r"description", re.IGNORECASE)
        pat_studio: Pattern[str] = re.compile(r"studios?", re.IGNORECASE)
        pat_trailer: Pattern[str] = re.compile(r"trailers?", re.IGNORECASE)
        pat_orientation: Pattern[str] = re.compile(r"orientation", re.IGNORECASE)

        def __iter__(self):
            """
            Yields the attribute values of this object based on its fields.

            This method iterates over the attributes defined by the `fields` function,
            which typically returns a list of Field objects. For each field, it yields the value
            of the corresponding attribute using Python's built-in `getattr` function.
            """
            for field in fields(self):
                yield getattr(self, field.name)

    @staticmethod
    def get_schema(db_cur: sqlite3) -> tuple[str, list[tuple[int, str]]]:
        """
        Get a tuple with the table and its field names.

        :param db_cur: ``sqlite3`` - Active database cursor
        :return: tuple('tablename', [(indx, 'fieldname'), ...])
        """
        query = "SELECT sql FROM sqlite_master"
        try:
            schema: list[tuple[int | str, ...]] = helpers.fetch_data_sql(query, db_cur)
            fst_table, *others = schema

            if others:
                logging.warning(
                    "Detected db with more than one table, fetching the first one by default."
                )

            table_name: str = fst_table[0].split(" ")[2].split("(")[0]
            query: str = "PRAGMA table_info({})".format(table_name)
            schema = helpers.fetch_data_sql(query, db_cur)
            fields_ord = list(map(lambda lstpl: lstpl[0:2], schema))

            return table_name, fields_ord

        except OperationalError:
            logging.critical(
                "db file was not found. Raising InvalidDB exception and quitting..."
            )
            raise InvalidDB

    def __init__(self, db_cur: sqlite3):
        """Initialisation logic for ``EmbedsMultiSchema`` instances.
            Supports data field handling that can carry out error handling without
            explicit logic in the main control flow or functionality using this class.
        :param db_cur: Active database cursor
        """
        schema = EmbedsMultiSchema.get_schema(db_cur)
        self.table_name: str = schema[0]
        self.__fields_indx = schema[1]
        self.__fields: list[Any] = list(map(lambda tpl: tpl[1], self.__fields_indx))
        self.field_count: int = len(self.__fields)
        self.__data: Optional[T] = None

    def load_data_instance(self, data_instance: T) -> None:
        """
        Setter for the private field ``data_instance``.
        :param data_instance: ``T`` - Generic type that ideally can handle __getitem__
        :return: ``None``
        """
        self.__data = data_instance
        return None

    def get_data_instance(self) -> Optional[T]:
        """Retrieve a copy of the data stored in the private field ``self.__data``

        :return: ``T`` | None - Generic Type
        """
        return self.__data

    def get_fields(self, keep_indx: bool = False) -> list[tuple[int, str]] | list[str]:
        """Get the actual database field names or a data structure (tuple) including
            its indexes.

        :param keep_indx: ``bool`` - Flag that, activated, retrieves indexes and column names in a tuple.
        :return:
        """
        if keep_indx:
            return self.__fields_indx
        else:
            return self.__fields

    def __safe_retrieve(self, re_pattern: Pattern[str]) -> Optional[T]:
        """Getter for the private fields ``self.__fields`` and ``self.__data``.
            Typically used in iterations where data access could result in exceptions that could
            cause undesired crashes.

        :param re_pattern: ``Pattern[str]`` - Regular Expression pattern (from local dataclass ``SchemaRegEx``)
        :return: ``T`` | None - Generic type object
        """
        match = helpers.match_list_single(re_pattern, self.__fields)
        if self.__data:
            try:
                return self.__data[match]
            except (IndexError, TypeError):
                return None
        else:
            return match

    def get_slug(self) -> Optional[str | int]:
        """Slug getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``slug`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_slug
        return self.__safe_retrieve(re_pattern)

    def get_embed(self) -> Optional[str | int]:
        """Embed getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``embed`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_embed
        return self.__safe_retrieve(re_pattern)

    def get_thumbnail(self) -> Optional[str | int]:
        """Thumbnail getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``thumbnail`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_thumbnail
        return self.__safe_retrieve(re_pattern)

    def get_categories(self) -> Optional[str | int]:
        """Categories getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``categories`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_categories
        return self.__safe_retrieve(re_pattern)

    def get_rating(self) -> Optional[str | int]:
        """Rating getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``rating`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_rating
        return self.__safe_retrieve(re_pattern)

    def get_title(self) -> Optional[str | int]:
        """Title getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``title`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_title
        return self.__safe_retrieve(re_pattern)

    def get_link(self) -> Optional[str | int]:
        """Link getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``link`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_link
        return self.__safe_retrieve(re_pattern)

    def get_date(self) -> Optional[str | int]:
        """Date getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``date`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_date
        return self.__safe_retrieve(re_pattern)

    def get_id(self) -> Optional[str | int]:
        """ID getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``id`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_id
        return self.__safe_retrieve(re_pattern)

    def get_duration(self) -> Optional[str | int]:
        """Duration getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``Duration`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_duration
        return self.__safe_retrieve(re_pattern)

    def get_pornstars(self) -> Optional[str | int]:
        """Pornstars getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``pornstars`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_prnstars
        return self.__safe_retrieve(re_pattern)

    def get_models(self) -> Optional[str | int]:
        """Models getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``models`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_models
        return self.__safe_retrieve(re_pattern)

    def get_resolution(self) -> Optional[str | int]:
        """Resolution getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``resolution`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_resolution
        return self.__safe_retrieve(re_pattern)

    def get_tags(self) -> Optional[str | int]:
        """Tags getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``tags`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_tags
        return self.__safe_retrieve(re_pattern)

    def get_likes(self) -> Optional[str | int]:
        """Likes getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``likes`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_likes
        return self.__safe_retrieve(re_pattern)

    def get_url(self) -> Optional[str | int]:
        """URL getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``url`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_url
        return self.__safe_retrieve(re_pattern)

    def get_description(self) -> Optional[str | int]:
        """Description getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``description`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_description
        return self.__safe_retrieve(re_pattern)

    def get_studio(self) -> Optional[str | int]:
        """Studio getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``studio`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_studio
        return self.__safe_retrieve(re_pattern)

    def get_trailer(self) -> Optional[str | int]:
        """Trailer getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``trailer`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_trailer
        return self.__safe_retrieve(re_pattern)

    def get_orientation(self) -> Optional[str | int]:
        """Orientation getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``orientation`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_orientation
        return self.__safe_retrieve(re_pattern)


class ConsoleStyle(Enum):
    """
    Store constants for color styles used with console objects from the ``Rich`` library.
    """

    TEXT_STYLE_ATTENTION = "bold yellow"
    TEXT_STYLE_DEFAULT = "green"
    TEXT_STYLE_ACTION = "bold green"
    TEXT_STYLE_PROMPT = "bold cyan"
    TEXT_STYLE_SPECIAL_PROMPT = "bold magenta"
    TEXT_STYLE_WARN = "bold red"


def logging_setup(
    bot_config,
    path_to_this: str,
) -> None:
    """Initiate the basic logging configuration for bots in the ``workflows`` package.

    :param bot_config: ``ContentSelectConf`` | ``GallerySelectConf`` | ``EmbedAssistConf`` | ``UpdateMCash`` - config functions
    :param path_to_this: ``str`` - Equivalent to __file__ but passed in as a parameter.
    :return: ``None``
    """
    get_filename = lambda f: os.path.basename(f).split(".")[0]
    sample_size = 5
    random_int_id = "".join(
        random.choices([str(num) for num in range(1, 10)], k=sample_size)
    )
    uniq_log_id = f"{random_int_id}{generate_random_str(sample_size)}"

    # This will help users identify their corresponding log per session.
    os.environ["SESSION_ID"] = uniq_log_id
    log_name = (
        f"{get_filename(path_to_this)}-log-{uniq_log_id}-{datetime.date.today()}.log"
    )
    log_dirname_cfg = bot_config.logging_dirname

    if os.path.exists(log_dirname_cfg):
        log_dir_path = os.path.abspath(log_dirname_cfg)
    elif os.path.exists(
        log_dir_parent := os.path.join(os.path.dirname(os.getcwd()), log_dirname_cfg)
    ):
        log_dir_path = log_dir_parent
    else:
        try:
            os.mkdir(log_dirname_cfg)
            log_dir_path = log_dirname_cfg
        except OSError:
            raise UnavailableLoggingDirectory(log_dirname_cfg)

    logging.basicConfig(
        filename=os.path.join(log_dir_path, log_name),
        filemode="w+",
        level=logging.INFO,
        encoding="utf8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )
    return None


def clean_partner_tag(partner_tag: str) -> str:
    """Clean partner names that could contain apostrophes in them.

    :param partner_tag: ``str`` the conflicting text
    :return: ``str`` cleaned partner tag without the apostrophe.
    """
    try:
        spl_word: str = split_char(partner_tag)
        if spl_word == " ":
            return partner_tag
        elif "'" not in split_char(partner_tag, char_lst=True):
            return partner_tag
        else:
            # Second special character is the apostrophe, the first one is typically a whitespace
            return "".join(partner_tag.split(spl_word))
    except IndexError:
        return partner_tag


def asset_parser(bot_config: ContentSelectConf, partner: str):
    """Parse asset images for post payload from the specified file in the
    ``workflows_config.ini`` file.

    :param bot_config: ``ContentSelectConf`` bot config factory function.
    :param partner: ``str`` partner name
    :return: ``list[str]`` asset images or banners.
    """
    assets = parse_client_config(bot_config.assets_conf, "core.config")
    sections = assets.sections()

    wrd_list = clean_partner_tag(partner).split(split_char(partner, placeholder=" "))

    find_me = (
        lambda word, section: matchs[0]
        if (matchs := re.findall(word, section, flags=re.IGNORECASE))
        else matchs
    )

    assets_list = []
    for wrd in wrd_list:
        # The main lambda has re.findall with IGNORECASE flag, however
        # list index lookup does take word case into consideration for str comparison.
        wrd_to_lc = wrd.lower()

        # To ensure uniqueness in the hints provided, the count of matches must be 1.
        # If the same word is found more than once, then the match is clearly not unique.
        matches = (
            temp_lst := [find_me(wrd_to_lc, section) for section in sections]
        ).count(wrd_to_lc)
        if matches == 1:
            match_indx = temp_lst.index(wrd_to_lc)
            logging.info(
                f'Asset parsing result: found "{wrd}" in section: {sections[match_indx]}'
            )
            assets_list = list(assets[sections[match_indx]].values())
            break
        else:
            continue

    if assets_list:
        return assets_list
    else:
        logging.critical("Raised AssetsNotFoundError - Quitting...")
        raise AssetsNotFoundError


def published(table: str, title: str, field: str, db_cursor: sqlite3) -> bool:
    """In order to come up with a way to know if a certain title has been published,
    I need to try a request and see whether there is any results. This is what the function
    published does, it returns True if there is any result or False if there isn't any.

    The logic is designed to be treated in a natural way ``if not published`` or ``if published.``
    However, with the introduction of the ``JSON`` file filtering, this mechanism that identifies published
    titles has been retired and greatly improved.

    :param table: ``str``` SQL table according to your database schema.
    :param title: ``str`` value you want to look up in the db.
    :param field: ``str`` table field you want to use for the search.
    :param db_cursor: ``sqlite3`` database connection cursor.
    :return: ``boolean`` True if one or more results are retrieved, False if the list is empty.
    """
    search_vids: str = f"SELECT * FROM {table} WHERE {field}='{title}'"
    if db_cursor.execute(search_vids).fetchall():
        return True
    else:
        return False


def published_json(title: str, wp_posts_f: list[dict]) -> bool:
    """This function leverages the power of a local implementation that specialises
    in getting, manipulating and filtering WordPress API post information in JSON format.
    After getting the posts from the local cache, the function filters each element using
    the ``re`` module to find matches to the title passed in as a parameter. After all that work,
    the function returns a boolean; True if the title was found and that just suggests
    that such a title is already published, or there is a post with the same title.

    Ideally, we can benefit from a different and more accurate filter for this purpose, however,
    it is important for the objectives of this project that all post titles are unique and that, inevitably,
    delimits the purpose and approach of this method. For now, this behaviour of title-only matching is desirable.

    :param title: ``str`` lookup term, in this case a ``title``
    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :return: ``bool`` True if one or more matches is found, False if the result is None.
    """
    post_titles: list[str] = wordpress_api.get_post_titles_local(wp_posts_f, yoast=True)

    comp_title: re.Pattern = re.compile(rf"({title})")

    results: list[str] = [
        vid_name for vid_name in post_titles if re.match(comp_title, vid_name)
    ]
    if len(results) >= 1:
        return True
    else:
        return False


def filter_published(
    all_videos: list[tuple], wp_posts_f: list[dict]
) -> list[tuple[str, ...]]:
    """``filter_published`` does its filtering work based on the ``published_json`` function.
    Actually, the ``published_json`` is the brain behind this function and the reason why I decided to
    separate brain and body, as it were, is modularity. I want to be able to modify the classification rationale
    without affecting the way in which iterations are performed, unless I intend to do so specifically.
    If this function fails, then I have an easier time to identify the culprit.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles that will be taken into consideration by the ``video_upload_pilot`` (later) for their suggestion and publication.

    :param all_videos: ``List[tuple]`` usually resulting from the SQL database query values.
    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :return: ``list[tuple]`` with the new filtered values.
    """
    not_published: list[tuple] = []
    for elem in all_videos:
        (title, *fields) = elem
        if published_json(title, wp_posts_f):
            continue
        else:
            not_published.append(elem)
    return not_published


def get_tag_ids(wp_posts_f: list[dict], tag_lst: list[str], preset: str) -> list[int]:
    """WordPress uses integers to identify several elements that posts share like models or tags.
    This function is equipped to deal with inconsistencies that are inherent to the way that WP
    handles its tags; for example, some tags can have the same meaning but differ in case.
    Most of my input will be lowercase tags that must be matched to analogous ones differing in case.
    As I want to avoid tag duplicity and URL proliferation in our site, I will use the same IDs for tags
    with a case difference but same in meaning. That's why this function gets a fullmatch with the help of
    the Python RegEx module, and it is instructed to ignore the case of occurrences.

    WordPress handles tag string input the same way; for example, if I write the tag 'mature' into the tags
    textarea in the browser, it maps it to the previously recorded 'Mature' tag, so theoretically and,
    as a matter of fact,'mature' and 'Mature' map to the same tag ID within the WordPress site.

    Another important feature of this function is the implementation of a set comprehension that I later
    coerce into a list. A set will make sure I get unique IDs since any duplicated input in the post payload
    could yield a failed status code or, ultimately, cause problems in post and URL management.
    This is just a preventive measure since, in theory, it is unlikely that we get two matches for the same tag
    simply because I am narrowing the ambiguities down by using pattern matching and telling it to ignore the case.
    Finally, the function will return a reversed list of integers.
    In order words, if you pass ``[foo, bar, python]`` , you will get ``[3, 2, 1]`` instead of ``[1, 2, 3]``.
    This reverse order is not important because you can send tags in any order and
    WordPress will sort them for you automatically, it always does (thankfully).

    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :param tag_lst: ``list[str]`` a list of tags
    :param preset: as this function is used for three terms, the presets supported are
           ``models``,  ``tags``, ``photos`` and ``categories``
    :return: ``list[int]``
    """
    match preset:
        case "models":
            preset = ("pornstars", "pornstars")
        case "tags":
            preset = ("tag", "tags")
        case "photos":
            preset = ("photos_tag", "photos_tag")
        case "categories":
            preset = ("category", "categories")
        case _ as err:
            raise UnsupportedParameter(err)

    tag_tracking: dict[str, int] = wordpress_api.map_wp_class_id(
        wp_posts_f, preset[0], preset[1]
    )

    clean_tag = lambda tag: " ".join(tag.split(split_char(tag)))
    tag_join = lambda tag: "".join(map(clean_tag, tag))
    # Result must be: colourful-skies/great -> colourful skies great
    cl_tags = list(map(tag_join, tag_lst))

    # It is crucial that tags don't have any special characters
    # before processing them with ``tag_tracking``.
    matched_keys: list[str] = [
        wptag
        for wptag in tag_tracking.keys()
        for tag in cl_tags
        if re.fullmatch(tag, wptag, flags=re.IGNORECASE)
    ]
    return list({tag_tracking[tag] for tag in matched_keys})


def get_model_ids(wp_posts_f: list[dict], model_lst: list[str]) -> list[int]:
    """This function is crucial to obtain the WordPress element ID ``model`` to be able
    to communicate and tell WordPress what we want. It takes in a list of model names and filters
    through the entire WP dataset to locate their ID and return it back to the controlling function.
    None if the value is not found in the dataset.
    This function enforces Title case in matches since models are people and proper names are generally
    in title case, and it is also the case in the data structure that local module ``integrations.wordpress_api`` returns.
    Further testing is necessary to know if this case convention is always enforced, so consistency is key here.

    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :param model_lst: ``list[str]`` models' names
    :return: ``list[int]`` (corresponding IDs)
    """
    model_tracking: dict[str, int] = wordpress_api.map_wp_class_id(
        wp_posts_f, "pornstars", "pornstars"
    )
    title_strip = lambda model: model.title().strip()
    return list(
        {
            model_tracking[title_strip(model)]
            for model in model_lst
            if title_strip(model) in model_tracking.keys()
        }
    )


def identify_missing(
    wp_data_dic: dict[str, str | int],
    data_lst: list[str],
    data_ids: list[int],
    ignore_case: bool = False,
):
    """This function is a simple algorithm that identifies when a tag or model must be manually recorded
    on WordPress, and it does that with two main assumptions:\n
    1) "If I have x tags/models, I must have x integers/IDs"\n
    2) "If there is a value with no ID, it just means that there is none and has to be created"\n
    Number 1 is exactly the first test for our values so, most of the time, if our results are consistent,
    this function returns None and no other operations are carried out. It acts exactly like a gatekeeper.
    In case the opposite is true, the function will examine why those IDs are missing and return the culprits (2).
    Our gatekeeper has an option to either enforce the case policy or ignore it, so I generally tell it to be
    lenient with tags (ignore_case = True) and strict with models (ignore_case = False), this is optional though.
    Ignore case was implemented based on the considerations that I have shared so far.

    :param wp_data_dic: ``dict[str, str | int]`` returned by either ``map_wp_model_id`` or ``tag_id_merger_dict`` from module ``integrations.wordpress_api``
    :param data_lst: ``list[str]`` tags or models
    :param data_ids: ``list[int]`` tag or model IDs.
    :param ignore_case: ``bool`` True, enforce case policy. Default False.
    :return: ``None`` or ``list[str]``
    """
    if len(data_lst) == len(data_ids):
        return None
    else:
        not_found: list[str] = []
        for item in data_lst:
            if ignore_case:
                item: str = item.lower()
                tags: list[str] = list(map(lambda tag: tag.lower(), wp_data_dic.keys()))
                if item not in tags:
                    not_found.append(item)
            else:
                try:
                    wp_data_dic[item]
                except KeyError:
                    not_found.append(item)
        return not_found


def fetch_thumbnail(
    folder: str, slug: str, remote_res: str, thumbnail_name: str = ""
) -> int:
    """This function handles the renaming and fetching of thumbnails that will be uploaded to
    WordPress as media attachments. It dynamically renames the thumbnails by taking in a URL slug to
    conform with SEO best-practices. Returns a status code of 200 if the operation was successful
    (fetching the file from a remote source). It also has the ability to store the image using a
    relative path.

    :param folder: ``str`` thumbnails dir
    :param slug: ``str`` URL slug
    :param remote_res: ``str`` thumbnail download URL
    :param thumbnail_name: ``str`` in case the user wants to upload different thumbnails and wishes to keep the names.
    :return: ``int`` (status code from requests)
    """
    thumbnail_dir: str = folder
    remote_data: requests = requests.get(remote_res)
    cs_conf = content_select_conf()
    if thumbnail_name != "":
        name: str = f"-{thumbnail_name.split('.')[0]}"
    else:
        name: str = thumbnail_name
    img_name = clean_filename(f"{slug}{name}", cs_conf.pic_fallback)
    with open(os.path.join(thumbnail_dir, img_name), "wb") as img:
        img.write(remote_data.content)

    if cs_conf.imagick:
        helpers.imagick(
            os.path.join(thumbnail_dir, img_name),
            cs_conf.quality,
            cs_conf.pic_format,
        )

    return remote_data.status_code


def fetch_thumbnail_file(
    folder: str,
    remote_res: str,
) -> tuple[str, int]:
    """
    Fetches a thumbnail file from the given remote resource and saves it to the specified folder.

    :param folder: ``str`` thumbnails dir (typically a temporary folder)
    :param remote_res: ``str`` thumbnail download URL
    :return: ``tuple[str, int]`` (file name, status code)
    """
    thumbnail_dir: str = folder
    remote_data: requests = requests.get(remote_res)
    img_name = (spl_str := remote_res).split(split_char(spl_str))[-1]
    with open(os.path.join(thumbnail_dir, img_name), "wb") as img:
        img.write(remote_data.content)
    return os.path.join(os.path.abspath(folder), img_name), remote_data.status_code


def make_payload(
    vid_slug,
    status_wp: str,
    vid_name: str,
    vid_description: str,
    banner_tracking_url: str,
    banner_img: str,
    partner_name: str,
    tag_int_lst: list[int],
    model_int_lst: list[int],
    bot_conf: ContentSelectConf = content_select_conf(),
    categs: Optional[list[int]] = None,
    wpauth: WPAuth = wp_auth(),
) -> dict[str, str | int]:
    """Make WordPress ``JSON`` payload with the supplied values.
    This function also injects ``HTML`` code into the payload to display the banner, add ``ALT`` text to it
    and other parameters for the WordPress editor's (Gutenberg) rendering.

    Some elements are not passed as f-strings because the ``WordPress JSON REST API`` has defined a different data types
    for those elements and, sometimes, the response returns a status code of 400
    when those are not followed carefully.

    :param vid_slug: ``str`` slug optimized by the job control function and database parsing algo ( ``tasks`` package).
    :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
    :param vid_name: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param banner_tracking_url: ``str`` Affiliate tracking link to generate leads
    :param banner_img: ``str`` banner image URL that will be injected into the payload.
    :param partner_name: ``str`` The offer you are promoting
    :param tag_int_lst: ``list[int]`` tag ID list
    :param model_int_lst: ``list[int]`` model ID list
    :param bot_conf: ``ContentSelectConf`` Bot configuration object
    :param categs: ``list[int]`` category numbers to be passed with the post information
    :param wpauth: ``WPAuth`` Object with the author information.
    :return: ``dict[str, str | int]``
    """
    author: int = int(wpauth.author_admin)
    img_attrs: bool = bot_conf.img_attrs
    payload_post: dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "link": f"{wpauth.full_base_url.strip('/')}/{vid_slug}/",
        "title": f"{vid_name}",
        "excerpt": f"<p>{vid_description}</p>\n",
        "content": f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt="{vid_name} | {partner_name} on {bot_conf.site_name}{bot_conf.domain_tld}"/></a></figure>'
        if img_attrs
        else f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt=""/></a></figure>',
        "author": author,
        "featured_media": 0,
        "tags": tag_int_lst,
        "pornstars": model_int_lst,
    }

    if categs:
        payload_post["categories"] = categs

    return payload_post


def make_payload_simple(
    vid_slug,
    status_wp: str,
    vid_name: str,
    vid_description: str,
    tag_int_lst: list[int],
    model_int_lst: Optional[list[int]] = None,
    categs: Optional[list[int]] = None,
    wp_auth: WPAuth = wp_auth(),
) -> dict[str, str | int]:
    """Makes a simple WordPress JSON payload with the supplied values.

    :param vid_slug: ``str`` slug optimized by the job control function and database parsing algo ( ``tasks`` package).
    :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
    :param vid_name: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param tag_int_lst: ``list[int]`` tag ID list
    :param model_int_lst: ``list[int]`` or ``None`` model ID list
    :param categs: ``list[int]`` or ``None`` category integers provided as optional parameter.
    :param wp_auth: ``WPAuth`` object with site configuration information.
    :return: ``dict[str, str | int]``
    """
    author: int = int(wp_auth.author_admin)
    payload_post: dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "title": f"{vid_name}",
        "content": f"<p>{vid_description}",
        "excerpt": f"<p>{vid_description}</p>\n",
        "author": author,
        "featured_media": 0,
        "tags": tag_int_lst,
    }

    if categs:
        payload_post["categories"] = categs
    elif model_int_lst:
        payload_post["pornstars"] = model_int_lst

    return payload_post


def make_img_payload(
    vid_title: str,
    vid_description: str,
    bot_config: ContentSelectConf = content_select_conf(),
    flat_payload: bool | tuple[str, str, str] = False,
) -> dict[str, str]:
    """Similar to the make_payload function, this one makes the payload for the video thumbnails,
    it gives them the video description and focus key phrase, which is the video title plus a call to
    action in case that a certain ALT text appears on the image search vertical, and they want to watch the video.

    :param vid_title: ``str`` The title of the video.
    :param vid_description: ``str`` The description of the video.
    :param bot_config: ``ContentSelectConf`` Uses general configuration options to customise payloads.
    :param flat_payload: ``bool | tuple[str, str, str]``, optional
        When ``False`` (default), the payload is generated automatically.
        If a tuple of (`alt_text`, `caption`, `description`) is provided, it is used to create the payload.
    :return: ``dict[str, str]`` A dictionary with the image payload.
    """

    # In case that the description is the same as the title, the program will send
    # a different payload to avoid keyword over-optimization.
    flat_attrs_dict = {
        "alt_text": "",
        "caption": "",
        "description": "",
    }

    if vid_title == vid_description and not flat_payload:
        img_payload: dict[str, str] = {
            "alt_text": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld}",
            "caption": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld}",
            "description": f"{vid_title} {bot_config.site_name}{bot_config.domain_tld}",
        }
    elif not bot_config.img_attrs:
        img_payload = flat_attrs_dict
    elif not flat_payload:
        img_payload: dict[str, str] = {
            "alt_text": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld} - {vid_description}",
            "caption": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld} - {vid_description}",
            "description": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld} - {vid_description}",
        }
    else:
        flat_attrs_dict["alt_text"] = flat_payload[0]
        flat_attrs_dict["caption"] = flat_payload[1]
        flat_attrs_dict["description"] = flat_payload[2]
        img_payload = flat_attrs_dict

    return img_payload


def make_slug(
    partner: str,
    model: Optional[str],
    title: str,
    content: str,
    studio: Optional[str] = "",
    reverse: bool = False,
    partner_out: bool = False,
) -> str:
    """This function is a new approach to the generation of slugs inspired by the slug-making
    mechanism from gallery_select.py. It takes in strings that will be transformed into URL slugs
    that will help us optimise the permalinks for SEO purposes.

    :param partner: ``str`` video partner
    :param model:  ``str`` video model
    :param title: ``str`` Video title
    :param content: ``str`` type of content, in this file it is simply `video` but it could be `pics` this parameter tells Google about the main content of the page.
    :param studio: ``str`` - Optional component in slugs for compatible schemas.
    :param reverse: ``bool``  ``True`` if you want to place the video title in front of the permalink. Default ``False``
    :param partner_out: ``bool`` ``True`` if you want to build slugs without the partner name. Default ``False``.
    :return: ``str`` formatted string of a WordPress-ready URL slug.
    """
    join_wrds = lambda wrd: "-".join(map(lambda w: w.lower(), re.findall(r"\w+", wrd)))
    build_slug = lambda lst: "-".join(filter(lambda e_str: e_str != "", lst))

    # Punctuation marks are filtered in ``title_cleaned``.
    filter_words: list[str] = [
        "at",
        "&",
        "and",
        "but",
        "it",
        "so",
        "very",
        "amp;",
        "",
        "&amp",
    ]

    title_cleaned: list[str] = [
        "".join(wrd).lower()
        for word in title.lower().split()
        if (wrd := re.findall(r"\w+", word, flags=re.IGNORECASE))
    ]

    title_sl: str = "-".join(
        list(filter(lambda w: w not in filter_words, title_cleaned))
    )

    partner_sl: str = "-".join(clean_partner_tag(partner.lower()).split())
    content_sl: str = join_wrds(content)
    studio_sl: str = join_wrds(studio) if studio is not None else ""

    model_sl: str = ""
    if model:
        model_delim = split_char(model, placeholder=" ")
        model_sl = "-".join(
            "-".join(map(join_wrds, name.split(" ")))
            for name in map(
                lambda m: m.lower().strip(),
                model.split(model_delim if model_delim != " " else "."),
            )
        )

    # Build slug segments according to flags
    segments: list[str]
    if reverse:
        # reverse has precedence over every other flag
        segments = [title_sl, partner_sl]
        if model_sl:
            segments.append(model_sl)
        if studio_sl:
            segments.append(studio_sl)
        segments.append(content_sl)
    elif partner_out:
        # partner name omitted
        segments = [title_sl]
        if model_sl:
            segments.append(model_sl)
        elif studio_sl:
            segments.append(studio_sl)
        segments.append(content_sl)
    else:
        # default behaviour
        segments = [partner_sl]
        if model_sl:
            segments.append(model_sl)
        segments.append(title_sl)
        if studio_sl:
            segments.append(studio_sl)
        segments.append(content_sl)

    return build_slug(segments)


def hot_file_sync(
    bot_config,
) -> bool:
    """I named this feature "Hot Sync" as it can modify the data structure we are using as a cached
    datasource and allows for more efficiency in keeping an up-to-date copy of all your posts.
    This function leverages the power of the caching mechanism defined
    in wordpress_api.py that dynamically appends new items in order and keeps track of cached pages with the
    total count of posts at the time of update. ``hot_file_sync`` just updates the JSON cache of the WP site and
    reloads the local cache configuration file to validate the changes.

    Hot Sync will write the changes once the new ones are validated and compared with the local config file.
    In other words, if it isn't right, the WP post file remains untouched.

    :param bot_config: ``ContentSelectConf`` or ``GallerySelectConf`` or ``EmbedAssistConf`` with configuration information.
    :return: ``bool`` - ``True`` if everything went well or raise ``HotFileSyncIntegrityError`` if the validation failed
    """
    parent = (
        False
        if os.path.exists(f"./{clean_filename(bot_config.wp_cache_config, 'json')}")
        else True
    )
    if photos := hasattr(bot_config, "wp_json_photos"):
        wp_filename: str = helpers.clean_filename(bot_config.wp_json_photos, "json")
    else:
        wp_filename: str = helpers.clean_filename(bot_config.wp_json_posts, "json")

    sync_changes: list[dict[...]] = wordpress_api.update_json_cache(photos=photos)

    # Reload config
    config_json: list[dict[...]] = helpers.load_json_ctx(bot_config.wp_cache_config)
    if len(sync_changes) == config_json[0][wp_filename]["total_posts"]:
        helpers.export_request_json(wp_filename, sync_changes, 1, parent=parent)
        logging.info(
            f"Exporting new WordPress cache config: {bot_config.wp_cache_config}"
        )
        logging.info("HotFileSync Successful")
        return True
    else:
        logging.critical("Raised HotFileSyncIntegrityError - Quitting...")
        raise HotFileSyncIntegrityError


def partner_select(
    partner_lst: list[str],
    banner_lsts: list[list[str]],
) -> tuple[str, list[str]]:
    """Selects partner and banner list based on their index order.
    As this function is based on index and order of elements, both lists should have the same number of elements.
    **Note: No longer in use since there are better implementations now**

    :param partner_lst: ``list[str]`` - partner offers
    :param banner_lsts: ``list[list[str]]`` list of banners to select from.
    :return: ``tuple[str, list[str]]`` partner_name, banner_list
    """
    print("\n")
    for num, partner in enumerate(partner_lst, start=1):
        print(f"{num}. {partner}")
    try:
        partner_indx = input("\n\nSelect your partner: ")
        partner = partner_lst[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]
    except IndexError:
        partner_indx = input("\n\nSelect your partner again: ")
        partner = partner_lst[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]
    return partner, banners


def select_guard(db_name: str, partner: str) -> None:
    """This function protects the user by matching the first
    occurrence of the partner's name in the database that the user selected.
    Avoiding issues at this stage is crucial because, if a certain user selects an
    incorrect database, the program will either crash or send incorrect record details to
    WordPress, and that could be a huge issue considering that each partner offering has
    proprietary banners and tracking links.

    It is important to note that this function was designed at a time when the user had to
    manually select a database. However, with functions like ``content_select_db_match`` , the
    program will obtain the most appropriate database automatically. Despite the latter, ``select_guard``
    has been kept in place to alert the user of any errors that may arise and still serve the purpose
    that led to its creation.

    :param db_name: ``str`` user-selected database name
    :param partner: ``str`` user-selected partner offering
    :return: ``None`` If the assertion fails the execution will stop gracefully.
    """
    # Find the split character as I just need to get the first word of the name
    # to match it with partner selected by the user
    # match_regex = re.findall(r"[\W_]+", db_name)[0]
    spl_dbname = lambda db: db.strip().split(split_char(db))
    try:
        assert re.match(spl_dbname(db_name)[0], partner, flags=re.IGNORECASE)
    except AssertionError:
        logging.critical(
            f"Select guard detected issues for db_name: {db_name} partner: {partner} split: {spl_dbname(db_name)}"
        )
        print("\nBe careful! Partner and database must match. Re-run...")
        print(f"The program selected {db_name} for partner {partner}.")
        exit(0)


def content_select_db_match(
    hint_lst: list[str],
    content_hint: str,
    folder: str = "",
    prompt_db: bool = False,
    parent: bool = False,
) -> tuple[Connection, Cursor, str, int]:
    """Give a list of databases, match them with multiple hints, and retrieves the most up-to-date filename.
    This is a specialised implementation based on the ``filename_select`` function in the ``core.helpers`` module.

    ``content_select_db_match`` finds a common index where the correct partner offer and database are located
    within two separate lists: the available ``.db`` file list and a list of partner offers.
    In order to accomplish this, the modules in the ``tasks`` package apply a consistent naming convention that
    looks like ``partner-name-content-type-date-in-ISO-format``; those filenames are further analysed by an algorithm
    that matches strings found in a lookup list.

    For more information on how this matching works and the algorithm behind it, refer to the documentation for
    ``match_list_mult`` and ``match_list_elem_date`` in the ``core.helpers`` module.

    **Note: As part of the above-mentioned naming convention, the files include a content type hint.
    This allows the algorithm to identify video or photo databases, depending on the module
    calling the function. However, this hint can be any word that you use consistently in your filenames.
    Also, if you want to access the file from a parent dir, either let the destination function handle it for you
    or specify it yourself. Everytime Python runs the file as a module or runs it on an interpreter outside your
    virtual environment, relative paths prove inefficient. However, this issue has been largely solved by using
    package notation with standard library and local implementations.**

    :param hint_lst: ``list[str]`` words/patterns to match.
    :param content_hint: ``str`` type of content, typically ``vids`` or ``photos``
    :param prompt_db: ``True`` if you want to prompt the user to select db. Default ``False``.
    :param folder: ``str`` where you want to look for files
    :param parent: ``True`` to search in parent dir, default set to ``False``.
    :return: ``tuple[Connection, Cursor, str, int]`` (database connection, database cursor, database name, common index int)
    """

    console = Console()

    available_files: list[str] = helpers.search_files_by_ext(
        "db", folder=folder, parent=parent
    )
    filtered_files: list[str] = helpers.match_list_elem_date(
        hint_lst,
        available_files,
        join_hints=(True, " ", "-"),
        ignore_case=True,
        strict=True,
    )

    relevant_content: list[str] = list(
        map(
            lambda indx: filtered_files[indx],
            helpers.match_list_mult(content_hint, filtered_files),
        )
    )

    if prompt_db:
        print("\nHere are the available database files:")
        for num, file in enumerate(relevant_content, start=1):
            print(f"{num}. {file}")
        print("\n")

    console.print(
        f"Session ID: {os.environ.get('SESSION_ID')}",
        style="bold yellow",
        justify="left",
    )
    print("\n")
    for num, file in enumerate(hint_lst, start=1):
        console.print(f"{num}. {file}", style="bold green")

    try:
        select_partner: str = console.input(
            "[bold yellow]\nSelect your partner now: [bold yellow]\n",
        )
        spl_char = split_char(hint_lst[(int(select_partner) - 1)])
        clean_hint: list[str] = hint_lst[(int(select_partner) - 1)].split(spl_char)

        select_file: int = 0
        for hint in clean_hint:
            rel_content: int = helpers.match_list_single(
                hint, relevant_content, ignore_case=True
            )
            if hint:
                if rel_content:
                    select_file = rel_content
                    break
            else:
                continue

        is_parent: str = (
            helpers.is_parent_dir_required(parent)
            if folder == ""
            else os.path.abspath(folder)
        )
        db_path: str = os.path.join(is_parent, relevant_content[int(select_file)])

        db_new_conn: sqlite3 = sqlite3.connect(db_path)
        db_new_cur: sqlite3 = db_new_conn.cursor()
        return (
            db_new_conn,
            db_new_cur,
            relevant_content[int(select_file)],
            select_file,
        )
    except (IndexError, ValueError, TypeError) as e:
        logging.critical(f"Encountered {e!r}. Debugging info: {relevant_content}")
        raise InvalidInput


def x_post_creator(
    description: str, post_url: str, post_text: Optional[str] = None
) -> int:
    """Create a post with a random action call for the X platform.
    Depending on your bot configuration, you can pass in your own post text and
    override the random call to action. If you just don't feel like typing and
    want to post without the randon text, the default value is an empty string.

    Set the ``x_posting_auto`` option in ``workflows_config.ini`` to ``False`` ,
    so that you get to type when you interact with the bots.

    :param description: ``str`` Video description
    :param post_url: ``str`` Video post url on WordPress
    :param post_text: ``str`` in certain circumstances
    :return: ``int`` POST request status code.
    """
    cs_conf = content_select_conf()
    site_name = cs_conf.site_name
    calls_to_action = [
        f"Watch more on {site_name}:",
        f"Take a quick look on {site_name}:",
        f"Watch the action for free on {site_name}:",
        f"Don't miss out. Watch now on {site_name}:",
        f"Don't miss out. Watch more on {site_name}:",
        f"Watch for free on {site_name}:",
        "Click below to watch for free:",
        "You won't need another video after this one:",
        f"{site_name} has it all for free:",
        f"All the Good stuff. Only on {site_name}:"
        "I bet you haven't watched this one:"
        "Well, you asked for it:",
        "I can't believe this is free:",
        "Specially for you:",
        f"Check out {site_name} today:",
        "Watch today for free:",
        "You're missing out on the action:",
        "When you thought you've watch it all:",
        f"Brought to you by {site_name}:",
        "Watch now:",
        "Watch free:Click to watch full video:",
        "Don't miss out:",
    ]
    # Env variable "X_TOKEN" is assigned in function ``x_api.refresh_flow()``
    bearer_token = os.environ.get("X_TOKEN")

    if post_text or post_text == "":
        post_text = f"{description} {post_text} {post_url}"
    else:
        post_text = f"{description} | {random.choice(calls_to_action)} {post_url}"

    request = x_api.post_x(post_text, bearer_token, XEndpoints())
    logging.info(f"Sent to X -> {post_text}")
    logging.info(f"X post metadata -> {request.json()}")
    return request.status_code


def telegram_send_message(
    description: str,
    post_url: str,
    bot_config,
    msg_text: str = "",
) -> int:
    """Set up a message template for the Telegram BotFather function ``send_message()``
    Parameters are self-explanatory.

    :param description: ``str``
    :param msg_text: ``str``
    :param post_url: ``str``
    :param bot_config: ``ContentSelectConf`` | ``EmbedAssistConf`` | ``GallerySelectConf``
    :return: ``int``
    """
    site_name = bot_config.site_name
    calls_to_action = [
        f"Watch more on {site_name}:",
        f"Take a quick look on {site_name}:",
        f"Watch the action for free on {site_name}:",
        f"Don't miss out. Watch now on {site_name}:",
        f"Don't miss out. Watch more on {site_name}:",
        f"Watch for free on {site_name}:",
        "Click below to watch for free:",
        "You won't need another video after this one:",
        f"{site_name} has it all for free:",
        f"All the Good stuff. Only on {site_name}:"
        "I bet you haven't watched this one:"
        "Well, you asked for it:",
        "I can't believe this is free:",
        "Specially for you:",
        f"Check out {site_name} today:",
        "Watch today for free:",
        "You're missing out on the action:",
        "When you thought you've watch it all:",
        f"Brought to you by {site_name}:",
        "Watch now:",
        "Watch free:Click to watch full video:",
        "Don't miss out:",
    ]
    auto_mode = bot_config.telegram_posting_auto
    if auto_mode:
        msg_text = random.choice(calls_to_action)

    message = (
        f"{description} | {msg_text} {post_url}"
        if auto_mode
        else f"{description} {msg_text} {post_url}"
    )
    req = botfather_telegram.send_message(
        bot_father(), BotFatherCommands(), BotFatherEndpoints(), message
    )
    logging.info(f"Sent to Telegram -> {message}")
    logging.info(f"BotFather post metadata -> {req.json()}")
    return req.status_code


def wp_publish_checker(post_slug: str, cs_conf) -> Optional[bool]:
    """Check for the publication a post in real time by using iteration of the Hot File Sync
    algorithm. It will detect that you have effectively hit the publish button, so that functionality
    that directly depends on the post being online can take it from there.

    The function assigns environment variable ``"LATEST_POST"`` since objects
    present in this application do not usually work with fully qualified links because it is
    not necessary. This mechanism has also proven effective for manipulating pieces of information during runtime.

    :param post_slug: ``str`` self-explanatory
    :param cs_conf: ``ContentSelectConf`` | ``EmbedAssistConf`` | ``GallerySelectConf`` - Config objects
    :return: ``None`` | ``True``
    """
    retries = 0
    retry_offset = 5
    start_check = time.time()
    hot_sync = hot_file_sync(cs_conf)
    while hot_sync:
        posts_file = (
            cs_conf.wp_json_photos
            if hasattr(cs_conf, "wp_json_photos")
            else cs_conf.wp_json_posts
        )
        wp_postf = helpers.load_json_ctx(posts_file)
        slugs = wordpress_api.get_slugs(wp_postf)
        if post_slug in slugs:
            os.environ["LATEST_POST"] = wp_postf[0]["link"]
            end_check = time.time()
            h, mins, secs = get_duration(end_check - start_check)
            logging.info(
                f"wp_publish_checker took -> hours: {h} mins: {mins} secs: {secs} in {retries} retries"
            )
            return True

        time.sleep(retry_offset)

        if retry_offset != 0:
            retry_offset -= 1
        else:
            retry_offset = 5

        retries += 1
        # Safeguard mechanism
        try:
            hot_sync = hot_file_sync(cs_conf)
        except KeyboardInterrupt:
            while not hot_sync:
                continue
            raise KeyboardInterrupt
    return None


def social_sharing_controller(
    console_obj: rich.console.Console,
    description: str,
    wp_slug: str,
    cs_config,
) -> None:
    """Share WordPress posts to social media platforms based on the settings in the workflow config.
    It is able to identify whether X or Telegram workflows have been enabled and post content accordingly.

    :param console_obj: ``rich.console.Console`` Console object used to provide user feedback
    :param description: ``str`` description/caption that will be shared
    :param wp_slug: ``str`` WordPress slug used to identify the published post
    :param cs_config: ``ContentSelectConf`` | ``GallerySelectConf`` | ``EmbedAssistConf`` workflow config object
    :return: ``None``
    """
    if cs_config.x_posting_enabled or cs_config.telegram_posting_enabled:
        status_msg = "Checking WP status and preparing for social sharing."
        status_style = ConsoleStyle.TEXT_STYLE_ACTION.value
        user_input = ConsoleStyle.TEXT_STYLE_ATTENTION.value
        with console_obj.status(
            f"[{status_style}]{status_msg} [blink]ε= ᕕ(⎚‿⎚)ᕗ[blink] [/{status_style}]\n",
            spinner="earth",
        ):
            is_published = wp_publish_checker(wp_slug, cs_config)
        if is_published:
            logging.info(
                f"Post {wp_slug} has been published. Exceptions after this might be caused by social plugins."
            )
            if cs_config.x_posting_enabled:
                logging.info("X Posting - Enabled in workflows config")
                if cs_config.x_posting_auto:
                    logging.info("X Posting Automatic detected in config")
                    # Environment "LATEST_POST" variable assigned in wp_publish_checker()
                    x_post_create = x_post_creator(
                        description, os.environ.get("LATEST_POST")
                    )
                else:
                    post_text = console_obj.input(
                        f"[{user_input}]Enter your additional X post text here or press enter to use default configs: [{user_input}]\n"
                    )
                    logging.info(f"User entered custom post text: {post_text}")
                    x_post_create = x_post_creator(
                        description,
                        os.environ.get("LATEST_POST"),
                        post_text=post_text,
                    )

                    # Copy custom post text for the following prompt
                    pyclip.detect_clipboard()
                    pyclip.copy(post_text)

                if x_post_create == 201:
                    console_obj.print(
                        "--> Post has been published on WP and shared on X.\n",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                else:
                    console_obj.print(
                        f"--> There was an error while trying to share on X.\n Status: {x_post_create}",
                        style=ConsoleStyle.TEXT_STYLE_WARN.value,
                    )
                logging.info(f"X post status code: {x_post_create}")

            if cs_config.telegram_posting_enabled:
                logging.info("Telegram Posting - Enabled in workflows config")
                if cs_config.telegram_posting_auto:
                    logging.info("Telegram Posting Automatic detected in config")
                    telegram_msg = telegram_send_message(
                        description,
                        os.environ.get("LATEST_POST"),
                        cs_config,
                    )
                else:
                    post_text = console_obj.input(
                        f"[{user_input}]Enter your additional Telegram message here or press enter to use default configs: [{user_input}]\n"
                    )
                    telegram_msg = telegram_send_message(
                        description,
                        os.environ.get("LATEST_POST"),
                        cs_config,
                        msg_text=post_text,
                    )

                if telegram_msg == 200:
                    console_obj.print(
                        # Env variable assigned in botfather_telegram.send_message()
                        f"--> Message sent to Telegram {os.environ.get('T_CHAT_ID')}",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                else:
                    console_obj.print(
                        f"--> There was an error while trying to communicate with Telegram.\n Status: {telegram_msg}",
                        style=ConsoleStyle.TEXT_STYLE_WARN.value,
                    )
                logging.info(f"Telegram message status code: {telegram_msg}")


def model_checker(
    wp_posts_f: list[dict[...]], model_prep: list[str]
) -> Optional[list[int]]:
    """
    Share missing model checking behaviour accross modules.
    Console logging is expected with this function.

    :param wp_posts_f: ``list[dict[str, ...]]`` - WP Posts file, typically provided by the pilot function.
    :param model_prep: ``list[str]`` - Model tag list without delimiters
    :return: ``list[int]`` - List of model integer ids in the WordPress site.
    """
    if not model_prep:
        # Maybe the post does not include a model.
        return None
    else:
        console = Console()
        calling_models: list[int] = get_model_ids(wp_posts_f, model_prep)
        all_models_wp: dict[str, int] = wordpress_api.map_wp_class_id(
            wp_posts_f, "pornstars", "pornstars"
        )
        new_models: Optional[list[str]] = identify_missing(
            all_models_wp, model_prep, calling_models
        )

    if new_models is None:
        return calling_models
    else:
        for girl in new_models:
            console.print(
                f"ATTENTION! --> Model: {girl} not on WordPress.",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
            console.print(
                "--> Copying missing model name to your system clipboard.",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
            console.print(
                "Paste it into the Pornstars field as soon as possible...\n",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
            logging.warning(f"Missing model: {girl}")
            pyclip.detect_clipboard()
            pyclip.copy(girl)

    return calling_models


def terminate_loop_logging(
    console_obj: rich.console.Console,
    iter_num: int,
    total_elems: int,
    done_count: int,
    time_elapsed: tuple[int | float, int | float, int | float],
    exhausted: bool,
    sets: bool = False,
) -> None:
    """Terminate the sequence of the loop by logging messages to the screen and the logs.

    :param time_elapsed: ``tuple[int, int, int]`` | Time measurement variables that report elapsed execution time for logging.
    :param console_obj: ``rich.console.Console``  | Console object used in order to log information to the console.
    :param iter_num: ``int``    | Iteration number in main loop for logging purposes
    :param total_elems: ``int`` | Total elements that the main loop had to process
    :param done_count: ``int``  | Total of video elements that were pushed to the WordPress site.
    :param exhausted: ``bool``  | Flag that controls console logging depending on whether elements are exhausted.
    :param sets: ``bool``       | Flag that controls console logging depending on whether elements are sets.
    :return: ``None``
    """
    # The terminating parts add this function to avoid
    # tracebacks from pyclip and enable cross-platform support.
    pyclip.detect_clipboard()
    pyclip.clear()
    if exhausted:
        logging.info(f"List exhausted. State: num={iter_num} total_elems={total_elems}")
        console_obj.print(
            "\nWe have reviewed all posts for this query.",
            style=ConsoleStyle.TEXT_STYLE_WARN.value,
        )
        console_obj.print(
            "Try a different SQL query or partner. I am ready when you are. ",
            style=ConsoleStyle.TEXT_STYLE_WARN.value,
        )
    elif not sets:
        console_obj.print(
            f"You have created {done_count} posts in this session!",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
        )
    else:
        console_obj.print(
            f"You have created {done_count} sets in this session!",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
        )
    h, mins, secs = time_elapsed
    logging.info(
        f"User created {done_count} {'posts' if not sets else 'sets'} in hours: {h} mins: {mins} secs: {secs}"
    )
    logging.info("Cleaning clipboard and temporary directories. Quitting...")
    logging.shutdown()
    exit(0)


def pilot_warm_up(
    cs_config,
    wp_auth: WPAuth,
    parent: bool = False,
):
    """
    Performs initialization operations for processing content selection, database operations,
    and WordPress post-handling with the provided configuration and authentication.

    :param cs_config: ``ContentSelectConf | GallerySelectConf | EmbedAssistConf`` Configuration
                     object specifying details for content selection, including database and partner
                     information.
    :param wp_auth: ``WPAuth`` Authentication object for WordPress API access.
    :param parent: ``bool`` optional. Flag indicating whether to use parent-level matching for
                  database content selection. Defaults to False.
    :return: ``None``
    :raises: ``UnableToConnectError`` Raised when the connection to the server fails after exceeding
            the maximum number of retries.
    """
    try:
        logging_setup(cs_config, __file__)
        logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}")

        console = Console()

        helpers.clean_console()

        status_style = ConsoleStyle.TEXT_STYLE_ACTION.value
        with console.status(
            f"[{status_style}] Warming up... [blink]┌(◎ _ ◎)┘[/blink] [/{status_style}]\n",
            spinner="aesthetic",
        ):
            hot_file_sync(bot_config=cs_config)
            x_api.refresh_flow(x_auth(), XEndpoints())

        partners: list[str] = list(
            map(lambda p: p.strip(), cs_config.partners.split(","))
        )
        logging.info(f"Loading partners variable: {partners}")

        wp_posts_f: list[dict[...]] = helpers.load_json_ctx(cs_config.wp_json_posts)
        logging.info(f"Reading WordPress Post cache: {cs_config.wp_json_posts}")

        wp_base_url: str = wp_auth.api_base_url
        logging.info(f"Using {wp_base_url} as WordPress API base url")

        _, cur_dump, partner_db_name, partner_indx = content_select_db_match(
            partners, cs_config.content_hint, parent=parent
        )

        partner = partners[partner_indx]
        select_guard(partner_db_name, partner)
        logging.info("Select guard cleared...")

        logging.info(f"Matched {partner_db_name} for {partner} index {partner_indx}")

        try:
            all_vals: list[tuple[str, ...]] = helpers.fetch_data_sql(
                cs_config.sql_query, cur_dump
            )
        except sqlite3.OperationalError as oerr:
            logging.error(
                f"Error while fetching data from SQL: {oerr!r} likely a configuration issue for partner {partner}."
            )
            raise InvalidSQLConfig(partner=partner)

        logging.info(f"{len(all_vals)} elements found in database {partner_db_name}")

        thumbnails_dir = tempfile.TemporaryDirectory(prefix="thumbs", dir=".")
        logging.info(f"Created {thumbnails_dir.name} for thumbnail temporary storage")

        not_published: list[tuple[str, ...]] = filter_published(all_vals, wp_posts_f)

        if cs_config.__class__.__name__ == "EmbedAssistConf":
            return console, partner, not_published, wp_posts_f, thumbnails_dir, cur_dump
        elif cs_config.__class__.__name__ == "ContentSelectConf":
            return console, partner, not_published, wp_posts_f, thumbnails_dir
        else:
            wp_photos_f = helpers.load_json_ctx(cs_config.wp_json_photos)
            logging.info(
                f"Reading WordPress Photo Posts cache: {cs_config.wp_json_posts}"
            )
            return (
                console,
                partner,
                not_published,
                all_vals,
                wp_posts_f,
                wp_photos_f,
                thumbnails_dir,
            )

    except urllib3.exceptions.MaxRetryError:
        raise UnableToConnectError


def iter_session_print(
    console_obj: rich.console.Console,
    video_count: int,
    elem_num: int = 0,
    partner: Optional[str] = None,
) -> None:
    """Print session information and element statistics to the console using Rich library styling.

    When partner is provided, prints the total count of videos to be published for that partner.
    Otherwise, prints the current element number and count in an iteration session. Uses environment
    variables set in logging_setup() to display session ID.

    :param console_obj: ``rich.console.Console`` Console object used for styled printing
    :param video_count: ``int`` Total count of videos or current count in session
    :param elem_num: ``int`` Current element number being processed, defaults to 0
    :param partner: ``Optional[str]`` Partner name to display with video count, defaults to None
    :return: ``None``
    """

    console_obj.print(
        f"Session ID: {os.environ.get('SESSION_ID')}",
        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
        justify="left",
    )
    if partner:
        console_obj.print(
            f"\nThere are {video_count} {partner} videos to be published...",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="center",
        )
    else:
        console_obj.print(
            f"Element #{elem_num + 1}",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="left",
        )
        console_obj.print(
            f"Count: {video_count}",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="left",
        )
        console_obj.print(
            f"\n{' Review this element ':*^30}\n",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="center",
        )


def slug_getter(console_obj: rich.console.Console, slugs: list[str]) -> str:
    """
    Retrieve a slug based on user input from provided options or get a custom one.
    Handles edge cases when no slugs are available or user input is invalid.

    :param console_obj: ``rich.console.Console`` Console object for printing and user interaction
    :param slugs: ``list[str]`` List of available slug options to choose from
    :return: ``str`` The selected slug, either from the provided list or a custom one
    """
    prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
    user_attention_style = ConsoleStyle.TEXT_STYLE_ATTENTION.value
    slug_entry_style = ConsoleStyle.TEXT_STYLE_ACTION.value

    def slug_getter_persist() -> str:
        user_slug = ""
        while not slug:
            console_obj.print(
                "Provide a new slug for your post now: ", style=prompt_style
            )
            user_slug: str = input()
        return user_slug

    if not slugs:
        logging.critical("No slugs were provided in controlling function.")
        new_slug = slug_getter_persist()
        return new_slug

    console_obj.print("\n--> Available slugs:\n", style=user_attention_style)

    for n, slug in enumerate(slugs, start=1):
        console_obj.print(f"{n}. -> {slug}", style=slug_entry_style)
    console_obj.print(
        "--> Press ENTER to provide a custom slug", style=user_attention_style
    )

    slug_option = console_obj.input(
        f"[{prompt_style}]\nSelect your slug: [/{prompt_style}]\n"
    )

    if slug_option != "":
        try:
            return slugs[int(slug_option) - 1]
        except (IndexError, ValueError):
            console_obj.print(
                "Invalid option! Choosing random slug...",
                style=ConsoleStyle.TEXT_STYLE_WARN.value,
            )
            new_slug = random.choice(slugs)
            logging.info(f"Chose random slug: {new_slug} automatically")
            return new_slug
    else:
        custom_slug = slug_getter_persist()
        logging.info(f"User provided slug: {custom_slug} automatically")
        return custom_slug


def tag_checker_print(
    console_obj: rich.console.Console, wp_posts_f: list[dict], tag_prep: list[str]
) -> list[int]:
    """
    Checks the tags in the given WordPress posts and identifies any missing tags, printing
    messages for missing tags as necessary and copying those to the system clipboard.

    :param console_obj: ``rich.console.Console`` The console object used for styled text output
    :param wp_posts_f: ``list[dict]`` A list of WordPress post data, where each post is a dictionary
    :param tag_prep: ``list[str]`` A list of prepared tags to be checked
    :return: ``list[int]`` A list of tag IDs corresponding to the provided tags
    """
    tag_ints: list[int] = get_tag_ids(wp_posts_f, tag_prep, "tags")
    all_tags_wp: dict[str, str] = wordpress_api.tag_id_merger_dict(wp_posts_f)
    tag_check: Optional[list[str]] = identify_missing(
        all_tags_wp, tag_prep, tag_ints, ignore_case=True
    )

    if tag_check is None:
        # All tags have been found and mapped to their IDs.
        pass
    else:
        for tag in tag_check:
            console_obj.print(
                f"ATTENTION --> Tag: {tag} not on WordPress.",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
            console_obj.print(
                "--> Copying missing tag to your system clipboard.",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
            console_obj.print(
                "Paste it into the tags field as soon as possible...\n",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
            logging.warning(f"Missing tag detected: {tag}")
            pyclip.detect_clipboard()
            pyclip.copy(tag)
    return tag_ints


def pick_classifier(
    console_obj: rich.console.Console,
    wp_posts_f: list[dict],
    title: str,
    description: str,
    tags: str,
) -> list[int]:
    """
    Picks a classifier for content selection based on user input and automatically assigns relevant categories.

    :raises ValueError: If an invalid option is chosen by the user.
    :param console_obj: The rich.console.Console object to print output.
    :param wp_posts_f: A list of dictionaries representing WordPress posts.
    :param title: The title of the content being selected.
    :param description: A short description of the content.
    :param tags: The relevant tags for the content.
    :return: None
    """

    def print_options(option_lst, print_delim: bool = False):
        for opt, classifier in enumerate(option_lst, start=1):
            console_obj.print(
                f"{opt}. {classifier.title() if isinstance(classifier, str) else classifier}",
                style=ConsoleStyle.TEXT_STYLE_DEFAULT.value,
            )
        if print_delim:
            console_obj.print(f"{'*':=^35}")

    prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
    classifiers = [
        classify_title(title),
        classify_description(description),
        classify_tags(tags),
    ]

    classifier_str_lst: list[str] = list(locals().keys())[2:5]
    classifier_options = [categs for categs in classifiers if categs]

    option = ""
    console_obj.print(
        "\nAvailable Machine Learning classifiers: \n",
        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
    )

    print_options(classifier_str_lst)
    peek = re.compile("peek", re.IGNORECASE)
    rand = re.compile(r"rando?m?", re.IGNORECASE)
    while not option:
        match console_obj.input(
            f"\n[{prompt_style}]Pick your classifier:  (Type in the 'peek' to open all classifiers or 'random' to let me choose for you)[/{prompt_style}]\n"
        ):
            case str() as p if peek.findall(p):
                print_options(classifier_options, print_delim=True)
                print_options(classifier_str_lst)
                option = console_obj.input(
                    f"\n[{prompt_style}]Your choice:[/{prompt_style}]\n"
                )
            case str() as r if rand.findall(r):
                option = random.choice(classifier_options)
            case _:
                continue
    try:
        # Here ``option`` can be either ``str`` or ``set[str]``
        categories = (
            list(classifiers[int(option) - 1]) if isinstance(option, str) else option
        )
    except (IndexError, ValueError):
        console_obj.print(
            "Invalid option! Picking randomly", style=ConsoleStyle.TEXT_STYLE_WARN.value
        )
        categories = list(random.choice(classifiers))

    consolidate_categs = list(categories)
    logging.info(f"Suggested categories ML: {consolidate_categs}")

    console_obj.print(
        " \n** I think these categories are appropriate: **\n",
        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
    )
    print_options(consolidate_categs)

    categ_num = re.compile(r"\d")
    match console_obj.input(
        f"[{prompt_style}]\nEnter the category number or type in to look for another category within the site: [{prompt_style}]\n"
    ):
        case str() as num if categ_num.match(num):
            try:
                sel_categ = consolidate_categs[int(num) - 1]
                logging.info(f"User selected category: {sel_categ}")
            except (ValueError, IndexError):
                sel_categ = random.choice(consolidate_categs)
                logging.info(
                    f"User typed in an incorrect option: {num}. Picking random category {sel_categ}"
                )
        case _ as misc:
            sel_categ = misc
            logging.info(f"User typed in category: {misc}")

    categ_ids: list[int] = get_tag_ids(wp_posts_f, [sel_categ], preset="categories")
    logging.info(
        f"WordPress API matched category ID: {categ_ids} for category: {sel_categ}"
    )
    return categ_ids


def filter_tags(
    tgs: str, filter_lst: Optional[list[str]] = None
) -> Optional[list[str]]:
    """Remove redundant words found in tags and return a clear list of unique filtered tags.

    :param tgs: ``list[str]`` tags to be filtered
    :param filter_lst: ``list[str]`` lookup list of words to be removed
    :return: ``list[str]``
    """
    if tgs is None:
        return None

    no_sp_chars = lambda w: "".join(re.findall(r"\w+", w))

    # Split with a whitespace separator is not necessary at this point:
    t_split = tgs.split(spl if (spl := helpers.split_char(tgs)) != " " else "-1")

    new_set = set({})
    for tg in t_split:
        temp_lst = []
        sublist = tg.split(" ")
        for word in sublist:
            if filter_lst is None:
                temp_lst.append(no_sp_chars(word))
            elif word not in filter_lst:
                temp_lst.append(no_sp_chars(word))
            elif temp_lst:
                continue
        new_set.add(" ".join(temp_lst))
    return list(new_set)


def filter_published_embeds(
    wp_posts_f: list[dict[...]], videos: list[tuple[str, ...]], db_cur: sqlite3
) -> list[tuple[str, ...]]:
    """filter_published does its filtering work based on the published_json function.
    It is based on a similar version from module `content_select`, however, this one is adapted to embedded videos
    and a different db schema.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles.

    :param videos: ``list[tuple[str, ...]]`` usually resulting from the SQL database query values.
    :param wp_posts_f: ``list[dict[str, ...]]`` WordPress Post Information case file (previously loaded and ready to process)
    :param db_cur: ``sqlite3`` - Active database cursor
    :return: ``list[tuple[str, ...]]`` with the new filtered values.
    """
    db_interface = EmbedsMultiSchema(db_cur)
    post_titles: list[str] = wordpress_api.get_post_titles_local(wp_posts_f, yoast=True)

    not_published: list[tuple] = []
    for elem in videos:
        db_interface.load_data_instance(elem)
        vid_title = db_interface.get_title()
        if vid_title in post_titles:
            continue
        else:
            not_published.append(elem)
    return not_published


def fetch_zip(
    dwn_dir: str,
    remote_res: str,
    parent: bool = False,
    gecko: bool = False,
    headless: bool = False,
    m_cash_auth: MongerCashAuth = monger_cash_auth(),
) -> None:
    """Fetch a .zip archive from the internet by following set of authentication and retrieval
    steps via automated execution of a browser instance (webdriver).

    **Note about "headless" mode: In this function, I have performed testing for a headless retrieval of the .zip
    archive, however, "headless" mode seems incompatible for this process. I am leaving the parameter to explore the
    execution in other platforms like Microsoft Windows as this function has been tested in Linux for the most
    part.**

    *Take into consideration that function fetch_zip() downloads files and Chrome does not usually wait
    until current downloads finish before closing running browser instances; fixes have been applied here to correct that behaviour.*

    *Headless mode does not show users why a certain iteration of the program failed and, due to the many factors, including but not limited to,
    internet connection speeds, the browser instance may require user collaboration to ensure the file has been
    downloaded and the former could then be closed either automatically or explicitly.*
    **For this reason, refrain from using headless mode with this module.**

    :param dwn_dir: ``str``  Download directory. Typically, a temporary location.
    :param remote_res: ``str`` Archive download URL. It must be a direct link (automatic download)
    :param parent: ``bool``  ``True`` if your download dir is in a parent directory. Default ``False``
    :param gecko: ``bool`` ``True`` if you want to use Gecko (Firefox) webdriver instead of Chrome. Default ``False``
    :param headless: ``bool`` ``True`` if you want headless execution. Default ``False``.
    :param m_cash_auth: ``MongerCashAuth`` object with authentication information to access MongerCash.
    :return: ``None``
    """
    webdrv: webdriver = helpers.get_webdriver(dwn_dir, headless=headless, gecko=gecko)

    webdrv_user_sel = "Gecko" if gecko else "Chrome"
    logging.info(
        f"User selected webdriver {webdrv_user_sel} -> Headless? {str(headless)}"
    )
    logging.info(f"Using {dwn_dir} for downloads as per function params")

    username: str = m_cash_auth.username
    password: str = m_cash_auth.password
    with webdrv as driver:
        # Go to URL
        print("--> Getting files from MongerCash")
        print("--> Authenticating...")
        driver.get(remote_res)
        driver.implicitly_wait(30)

        username_box: WebElement = driver.find_element(By.ID, "user")
        pass_box: WebElement = driver.find_element(By.ID, "password")

        username_box.send_keys(username)
        pass_box.send_keys(password)

        button_login: WebElement = driver.find_element(By.ID, "head-login")

        button_login.click()
        print("--> Downloading...")

        if not gecko:
            # Chrome exits after authenticating and before completing pending downloads.
            # On the other hand, Gecko does not need additional time.
            time.sleep(15)

    time.sleep(5)
    zip_set = helpers.search_files_by_ext(
        "zip", parent=parent, folder=os.path.relpath(dwn_dir)
    )[0]
    print(f"--> Fetched file {zip_set}")
    logging.info(f"--> Fetched archive file {zip_set}")
    return None


def extract_zip(zip_path: str, extr_dir: str) -> None:
    """Locate and extract a .zip archive in different locations.
    For example, you can locate the .zip archive from a temporary location and extract it
    somewhere else.

    :param zip_path: ``str`` where to locate the zip archive.
    :param extr_dir: ``str`` where to extract the contents of the archive
    :return: ``None``
    """
    get_zip: list[str] = helpers.search_files_by_ext(
        "zip", folder=os.path.relpath(zip_path)
    )
    try:
        with zipfile.ZipFile(
            zip_loc := os.path.join(zip_path, get_zip[0]), "r"
        ) as zipf:
            zipf.extractall(path=os.path.abspath(extr_dir))
        print(
            f"--> Extracted files from {os.path.basename(zip_loc)} in folder {os.path.relpath(extr_dir)}"
        )
        logging.info(f"Extracted {zip_loc}")
        print("--> Tidying up...")
        try:
            # Some archives have a separate set of redundant files in that folder.
            # I don't want them.
            shutil.rmtree(junk_folder := os.path.join(extr_dir, "__MACOSX"))
            logging.info(f"Junk folder {junk_folder} detected and cleaned.")
        except (FileNotFoundError, NotImplementedError) as e:
            logging.warning(f"Caught {e!r} - Handled")
        finally:
            logging.info(f"Cleaning remaining archive in {zip_path}")
            os.remove(zip_loc)
    except (IndexError, zipfile.BadZipfile) as e:
        logging.error(f"Something went wrong with the archive extraction -> {e!r}")
        return None


def make_gallery_payload(
    gal_title: str,
    iternum: int,
    gallery_sel_conf: GallerySelectConf = gallery_select_conf(),
):
    """Make the image gallery payload that will be sent with the PUT/POST request
    to the WordPress media endpoint.

    :param gal_title: ``str`` Gallery title/name
    :param iternum: ``str`` short for "iteration number" and it allows for image numbering in the payload.
    :param gallery_sel_conf: ``GallerySelectConf`` - Bot configuration object
    :return: ``dict[str, str]``
    """
    img_attrs: bool = gallery_sel_conf.img_attrs
    img_payload: dict[str, str] = {
        "alt_text": f"Photo {iternum} from {gal_title}" if img_attrs else "",
        "caption": f"Photo {iternum} from {gal_title}" if img_attrs else "",
        "description": f"Photo {iternum} from {gal_title}" if img_attrs else "",
    }
    return img_payload


def search_db_like(
    cur: sqlite3, table: str, field: str, query: str
) -> Optional[list[tuple[...]]]:
    """Perform a ``SQL`` database search with the ``like``  parameter in a SQLite3 database.

    :param cur: ``sqlite3`` db cursor object
    :param table: ``str`` table in the db schema
    :param field: ``str`` field you want to match with ``like``
    :param query: ``str`` database query in ``SQL``
    :return: ``list[tuple[...]]`` or ``None``
    """
    qry: str = f'SELECT * FROM {table} WHERE {field} like "{query}%"'
    return cur.execute(qry).fetchall()


def get_from_db(cur: sqlite3, field: str, table: str) -> Optional[list[tuple[...]]]:
    """Get a specific field or all ( ``*`` ) from a SQLite3 database.

    :param cur: ``sqlite3`` database cursor
    :param field: ``str`` field that you want to consult.
    :param table: ``str`` table in you db schema
    :return: ``list[tuple[...]]``  or ``None``
    """
    qry: str = f"SELECT {field} from {table}"
    try:
        return cur.execute(qry).fetchall()
    except OperationalError:
        return None


def get_model_set(db_cursor: sqlite3, table: str) -> set[str]:
    """Query the database and isolate the values of a single column to aggregate them
    in a set of str. In this case, the function isolates the ``models`` field from a
    table that the user specifies.

    :param db_cursor: ``sqlite3`` database cursor
    :param table: ``str`` table you want to consult.
    :return: ``set[str]``
    """
    models: list[tuple[str]] = get_from_db(db_cursor, "models", table)
    new_lst: list[str] = [
        model[0].strip(",") for model in models if model[0] is not None
    ]
    return {
        elem
        for model in new_lst
        for elem in (model.split(",") if re.findall(r",+", model) else [model])
    }


def make_photos_post_payload(
    status_wp: str,
    set_name: str,
    partner_name: str,
    tags: list[int],
    reverse_slug: bool = False,
    wpauth: WPAuth = wp_auth(),
) -> dict[str, str | int]:
    """Construct the photos payload that will be sent with all the parameters for the
    WordPress REST API request to create a ``photos`` post.
    In addition, this function makes the permalink that I will be using for the post.

    :param status_wp: ``str`` typically ``draft`` but it can be ``publish``, however, all posts need review.
    :param set_name: ``str`` photo gallery name.
    :param partner_name: ``str`` partner offer that I am promoting
    :param tags: ``list[int]`` tag IDs that will be sent to WordPress for classification and integration.
    :param reverse_slug: ``bool`` ``True`` if you want to reverse the permalink (slug) construction.
    :param wpauth: ``WPAuth`` Object with the author information.
    :return: ``dict[str, str | int]``
    """
    filter_words: set[str] = {"on", "in", "at", "&", "and"}

    no_partner_name: list[str] = list(
        filter(lambda w: w not in set(partner_name.split(" ")), set_name.split(" "))
    )

    # no_partner_name: list[str] = [
    #     word for word in set_name.split(" ") if word not in set(partner_name.split(" "))
    # ]

    wp_pre_slug: str = "-".join(
        [
            word.lower()
            for word in no_partner_name
            if re.match(r"\w+", word, flags=re.IGNORECASE)
            and word.lower() not in filter_words
        ]
    )

    if reverse_slug:
        # '-pics' tells Google the main content of the page.
        final_slug: str = (
            f"{wp_pre_slug}-{'-'.join(partner_name.lower().split(' '))}-pics"
        )
    else:
        final_slug: str = (
            f"{'-'.join(partner_name.lower().split(' '))}-{wp_pre_slug}-pics"
        )
    # Setting Env variable since the slug is needed outside this function.
    os.environ["SET_SLUG"] = final_slug

    author: int = int(wpauth.author_admin)

    payload_post: dict[str, str | int] = {
        "slug": final_slug,
        "status": f"{status_wp}",
        "type": "photos",
        "link": f"{wpauth.full_base_url}/{final_slug}/",
        "title": f"{set_name}",
        "author": author,
        "featured_media": 0,
        "photos_tag": tags,
    }
    return payload_post


def upload_image_set(
    ext: str,
    folder: str,
    title: str,
    wp_params: WPAuth = wp_auth(),
    wp_endpoints: WPEndpoints = WPEndpoints(),
) -> None:
    """Upload a set of images to the WordPress Media endpoint.

    :param ext: ``str`` image file extension to look for.
    :param folder:  ``str`` Your thumbnails folder, just the name is necessary.
    :param title: ``str`` gallery name
    :param wp_params: ``WPAuth`` object with the base URL of the WP site.
    :return: ``None``
    """
    thumbnails: list[str] = helpers.search_files_by_ext(ext, folder=folder)
    if len(thumbnails) == 0:
        # Assumes the thumbnails are contained in a directory
        # This could be caused by the archive extraction
        logging.info("Thumbnails contained in directory - Running recursive search")
        files: list[str] = helpers.search_files_by_ext(
            ".jpg", recursive=True, folder=folder
        )

        get_parent_dir = lambda dr: os.path.split(os.path.split(dr)[-2:][0])[1]

        thumbnails: list[str] = [
            os.path.join(get_parent_dir(path), os.path.basename(path)) for path in files
        ]

    if len(thumbnails) != 0:
        logging.info(
            prnt_imgs
            := f"--> Uploading set with {len(thumbnails)} images to WordPress Media..."
        )
        print(prnt_imgs)
        print("--> Adding image attributes on WordPress...")
        thumbnails.sort()

    # Prepare the image new name so that separators are replaced by hyphens.
    # E.g. this_is_a_cool_pic.jpg => this-is-a-cool-pic.jpg
    new_name_img = lambda name: "-".join(
        f"{os.path.basename(name)!s}".split(helpers.split_char(name))
    )

    for number, image in enumerate(thumbnails, start=1):
        img_attrs: dict[str, str] = make_gallery_payload(title, number)
        img_file = "-".join(
            new_name_img(image).split(helpers.split_char(image, placeholder=" "))
        )
        os.renames(
            os.path.join(folder, os.path.basename(image)),
            img_new := os.path.join(folder, os.path.basename(img_file)),
        )
        status_code: int = wordpress_api.upload_thumbnail(
            wp_params.api_base_url,
            [wp_endpoints.media],
            img_new,
            img_attrs,
        )

        img_now = os.path.basename(img_new)
        if status_code == (200 or 201):
            logging.info(f"Removing --> {img_now}")
            os.remove(img_new)

        logging.info(
            img_seq := f"* Image {number} | {img_now} --> Status code: {status_code}"
        )
        print(img_seq)
    try:
        # Check if I have paths instead of filenames
        if len(thumbnails[0].split(os.sep)) > 1:
            try:
                shutil.rmtree(
                    remove_dir
                    := f"{os.path.join(os.path.abspath(folder), thumbnails[0].split(os.sep)[0])}"
                )
                logging.info(f"Removed dir -> {remove_dir}")
            except NotImplementedError:
                logging.info(
                    "Incompatible platform - Directory cleaning relies on tempdir logic for now"
                )
    except (IndexError, AttributeError):
        pass


def filter_relevant(
    all_galleries: list[tuple[str, ...]],
    wp_posts_f: list[dict[...]],
    wp_photos_f: list[dict[...]],
) -> list[tuple[str, ...]]:
    """Filter relevant galleries by using a simple algorithm to identify the models in
    each photo set and returning matches to the user. It is an experimental feature because it
    does not always work, specially when some image sets use the full name of the model and that
    makes it difficult for this simple algorithm to work.
    This could be reimplemented in a different (more efficient) manner, however,
    I do not believe it is a critical feature.

    :param all_galleries: ``list[tuple[str, ...]`` typically returned by a database query response.
    :param wp_posts_f: ``list[dict[...]]`` WordPress Posts data structure
    :param wp_photos_f:  ``list[dict[...]]`` WordPress Photos data structure
    :return: ``list[tuple[str, ...]]`` Image sets related to models present in the WP site.
    """
    models_set: set[str] = set(
        wordpress_api.map_wp_class_id(wp_posts_f, "pornstars", "pornstars").keys()
    )
    not_published_yet = []
    for elem in all_galleries:
        (title, *fields) = elem
        model_in_set = False
        title_split = title.split(" ")
        for word in title_split:
            if word not in models_set:
                continue
            else:
                model_in_set = True
                break

        if not published_json(title, wp_photos_f) and model_in_set:
            not_published_yet.append(elem)
        else:
            continue
    return not_published_yet
