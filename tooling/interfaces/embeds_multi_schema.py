"""
EmbedsMultiSchema

Complementary class dealing with dynamic SQL schema reading for content databases.

EmbedsMultiSchema provides an interface to the main control flow of the bot that allows
for direct index probing based on the present schema. This improvement will make it easier
for the user to implement further functionality and behaviour based on specific fields with the
content databases.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import re
import sqlite3
from dataclasses import dataclass, fields
from re import Pattern
from sqlite3 import OperationalError
from typing import TypeVar, Generic, Any, Optional

# Local implementations
from core.utils.strings import match_list_single
from core.utils.data_access import fetch_data_sql
from core.exceptions.data_access_exceptions import InvalidDB

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
            schema: list[tuple[int | str, ...]] = fetch_data_sql(
                query, db_cur
            )
            fst_table, *others = schema

            if others:
                logging.warning(
                    "Detected db with more than one table, fetching the first one by default."
                )

            table_name: str = fst_table[0].split(" ")[2].split("(")[0]
            query: str = "PRAGMA table_info({})".format(table_name)
            schema = fetch_data_sql(query, db_cur)
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
        match = match_list_single(re_pattern, self.__fields)
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
