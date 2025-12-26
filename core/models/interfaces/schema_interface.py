# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
SchemaInterface

This module defines the SchemaInterface class, which is a complementary class dealing with
dynamic SQL schema reading and query creation for embedded content databases.
SchemaInterface is a type of lightweight implementation of a local Object-Relational Mapping (ORM) system.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import sqlite3

from typing import TypeVar, Generic, Optional, Any
from pathlib import Path
from re import Pattern

# Local implementations

from core.exceptions.data_access_exceptions import InvalidDB
from core.utils.strings import match_list_single
from core.utils.data_access import fetch_data_sql

T = TypeVar("T")


class SchemaInterface(Generic[T]):
    """
    Complementary class dealing with dynamic SQL schema reading for content databases.

    SchemaInterface provides an interface to the main control flow of programs that allows
    for direct index probing based on the present schema. This will make it easier
    for the user to implement further functionality and behaviour based on specific fields.

    **Note:** Subclasses must implement a class called ``SchemaRegEx``. It is a dataclass with
    compiled regex patterns that you will use. If you fail to implement this class, your implementation
    will raise a ``TypeError`` exception. This requirement has been imposed to enforce encapsulation.

    For example::

        @dataclass
        class SchemaRegEx:
            pattern_id: Pattern[str] = re.compile("id")

    """

    def __init__(
        self,
        db_path: str | Path,
        table_number: int = 0,
        thread_safe: bool = True,
        in_memory: bool = False,
    ):
        """
        Initialisation logic for ``SchemaInterface`` instances.
        Supports data field handling that can carry out error handling without
        explicit logic in the main control flow or functionality using this class.

        :param db_path: ``str | Path`` - Path to the SQLite database file.
        :param table_number: ``int`` - If your database has more than one table, you can specify an index.
        :param thread_safe: ``bool`` - If True, will create a new database connection for each operation if you operate in different threads.
        :param in_memory: ``bool`` - If True, will use an in-memory database
        """
        self.__db_path = db_path if not in_memory else ":memory:"
        try:
            self.__conn: sqlite3.Connection = sqlite3.connect(self.__db_path)
        except sqlite3.OperationalError:
            logging.critical(
                f"db file was not found at {db_path}. Raising InvalidDB exception and quitting..."
            )
            raise InvalidDB(db_path)
        self.__cursor: sqlite3.Cursor = self.__conn.cursor()
        self.__schema = SchemaInterface.get_schema(
            self.__cursor, table_number=table_number
        )
        self.__table_name: str = self.__schema[0]
        self.__fields_indx = self.__schema[1]
        self.__fields: list[Any] = list(map(lambda tpl: tpl[1], self.__fields_indx))
        self.__field_count: int = len(self.__fields)
        self.__data: Optional[T] = None
        self.__query = ""
        self.thread_safe = thread_safe

    def renew_db_conn(self) -> None:
        """
        Close and re-open the database connection.
        This function is called whenever a database operation is required, and
        it is necessary to ensure all changes are carried out in the same execution thread.
        """
        if self.thread_safe:
            self.__conn = sqlite3.Connection(self.__db_path)
            self.__cursor = self.__conn.cursor()
        return None

    def clean_resources(self) -> None:
        """
        Close the database cursor and connection to free up resources.
        """
        if self.thread_safe:
            self.__cursor.close()
            self.__conn.close()
        return None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, "SchemaRegEx"):
            raise TypeError(
                f"{cls.__name__} must define an inner dataclass 'SchemaRegEx' refer to docstring for details"
            )

    @staticmethod
    def get_schema(
        db_cur: sqlite3, table_number: int
    ) -> tuple[str, list[tuple[int, str]]]:
        """
        Get a tuple with the table and its field names.

        :param db_cur: ``sqlite3`` - Active database cursor
        :param table_number: ``int`` - If your database has more than one table, you can specify an index.
        :return: tuple('tablename', [(indx, 'fieldname'), ...])
        """
        query = "SELECT sql FROM sqlite_master"
        try:
            schema: list[tuple[int | str, ...]] = fetch_data_sql(query, db_cur)
            fst_table, *others = schema

            target_table = fst_table
            if others and table_number != 0:
                target_table = others[table_number]
            elif not others and table_number == 0:
                logging.info(
                    "Detected db with more than one table, fetching the first one by default."
                )
            table_name: str = str(target_table).split(" ")[2].split("(")[0]
            query: str = "PRAGMA table_info({})".format(table_name)
            schema = fetch_data_sql(query, db_cur)
            fields_ord = list(map(lambda lstpl: lstpl[0:2], schema))

            return table_name, fields_ord

        except sqlite3.OperationalError:
            logging.critical(
                "db file was not found. Raising InvalidDB exception and quitting..."
            )
            raise InvalidDB

    def load_data_row(self, data_instance: T) -> None:
        """
        Setter for the private field ``data_instance``.
        This field represents a row of data while looping over a database result set.

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

    def _safe_retrieve_iter(self, re_pattern: Pattern[str]) -> Optional[T]:
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

    def _safe_insert(self, *args, exclude_id: bool = True) -> bool:
        """
        Insert a new row into the database table.

        :param args: ``tuple`` - Values to be inserted into the table.
        :return: ``bool`` - True if the insert was successful, False otherwise.
        """
        self.renew_db_conn()
        placeholders = "?," * len(*args)
        fields = self.__fields[int(exclude_id) : len(*args) + 1]
        try:
            self.__query = "INSERT INTO {} ({}) VALUES ({})".format(
                self.__table_name, ",".join(fields), placeholders.strip(",")
            )
            self.__cursor.execute(self.__query, args[0])
            self.__conn.commit()
            self.clean_resources()
            return True
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as SQLErr:
            self.__conn.rollback()
            logging.error(f"Caught {SQLErr!r}")
            logging.debug(f"Query: {self.__query}")
            return False

    def _safe_update(
        self,
        predicate: str = "",
        /,
        **kwargs,
    ) -> bool:
        """
        Update a row in the database table.

        :param predicate: ``str`` - SQL WHERE clause to filter which rows to update.
        :param args: ``tuple`` - Values to be used in the WHERE clause.
        :param kwargs: ``dict`` - Key-value pairs representing the fields to be updated and their new values.
        :return: ``bool`` - True if the update was successful, False otherwise.
        """
        self.renew_db_conn()
        try:
            fields = []
            for field, _ in kwargs.items():
                fields.append("{} = :{}".format(field, field))
            predicate = " WHERE " + predicate if predicate else ""
            self.__query = (
                "UPDATE {} SET {}".format(
                    self.__table_name,
                    ",".join(fields).strip(","),
                )
                + predicate
            )
            self.__cursor.execute(self.__query, kwargs)
            self.__conn.commit()
            self.clean_resources()
            return True
        except sqlite3.OperationalError as SQLErr:
            self.__conn.rollback()
            logging.error(f"Caught {SQLErr!r} Cause: {SQLErr.__cause__}")
            logging.debug(f"Query: {self.__query}")
            return False

    def _safe_select(
        self, *args, predicate: str = "", fetch_one: bool = False
    ) -> tuple[T] | list[tuple[T]] | bool:
        """
        Select rows from the database table based on the provided fields and predicate.

        :param args: ``tuple`` - Fields to be selected from the table.
        :param predicate: ``str`` - SQL WHERE clause to filter which rows to select.
        :param fetch_one: ``bool`` - If True, fetches a single row; otherwise, fetches all matching rows.
        :return: ``tuple[T]`` | ``list[tuple[T]]`` | ``bool`` - Returns a tuple of the selected rows, a list of tuples, or False if an error occurs.
        """
        self.renew_db_conn()
        try:
            predicate = " WHERE " + predicate if predicate else ""
            self.__query = (
                "SELECT {} FROM {}".format(",".join(args).strip(","), self.__table_name)
                + predicate
            )
            results = self.__cursor.execute(self.__query)
            results = results.fetchone() if fetch_one else results.fetchall()
            self.clean_resources()
            return results
        except sqlite3.OperationalError as SQLErr:
            self.__conn.rollback()
            logging.error(f"Caught {SQLErr!r}")
            logging.debug(f"Query: {self.__query}")
            return False

    def _safe_select_all(
        self, predicate: str = "", fetch_one: bool = False
    ) -> tuple[T] | list[tuple[T]] | bool:
        """
        Select all rows from the database table with an optional predicate.

        :param predicate: ``str`` - SQL WHERE clause to filter which rows to select.
        :param fetch_one: ``bool`` - If True, fetches a single row; otherwise, fetches all matching rows.
        :return: ``tuple[T]`` | ``list[tuple[T]]`` | ``bool`` - Returns a tuple of the selected rows, a list of tuples, or False if an error occurs.
        """
        self.renew_db_conn()
        try:
            predicate = " WHERE " + predicate if predicate else ""
            self.__query = "SELECT * FROM {}".format(self.__table_name) + predicate
            results = self.__cursor.execute(self.__query)
            results = results.fetchone() if fetch_one else results.fetchall()
            self.clean_resources()
            return results
        except sqlite3.OperationalError as SQLErr:
            self.__conn.rollback()
            logging.error(f"Caught {SQLErr!r} Cause: {SQLErr.__cause__}")
            logging.debug(f"Query: {self.__query}")
            return False

    def _safe_retrieve_like_entry(
        self, field: str, like: str, fetch_one: bool = False
    ) -> tuple[str | int] | bool:
        """
        Retrieve a secret entry from the database based on a predicate.

        :param field: ``str`` -> Field to search for
        :param like: ``str`` -> String to search for
        :param fetch_one: ``bool`` -> If True, fetches a single row; otherwise, fetches all matching rows
        :return: ``tuple[str | int]`` | ``bool`` -> A tuple containing the secret entries or False if not found
        """
        like = f"like '{like}'"
        return self._safe_select_all(f"{field} {like}", fetch_one=fetch_one)

    def _safe_delete(self, predicate: str = "") -> bool:
        """
        Delete rows from the database table based on the provided predicate.

        :param predicate: ``str`` - SQL WHERE clause to filter which rows to delete.
        :return: ``bool`` - True if delete was successful, False otherwise.
        """
        self.renew_db_conn()
        try:
            predicate = " WHERE " + predicate if predicate else ""
            self.__query = "DELETE FROM {}".format(self.__table_name) + predicate
            self.__cursor.execute(self.__query)
            self.__conn.commit()
            self.clean_resources()
            return True
        except sqlite3.OperationalError as SQLErr:
            self.__conn.rollback()
            logging.error(f"Caught {SQLErr!r} Cause: {SQLErr.__cause__}")
            logging.debug(f"Query: {self.__query}")
            return False
