"""
Workflows database utils module

This module is responsible for database selection, management and common operations.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import re
import sqlite3
from sqlite3 import OperationalError, Connection, Cursor
from typing import Optional, List, Tuple

# Third-party imports
from rich.console import Console

# Local imports
from core.exceptions.util_exceptions import InvalidInput
from core.utils.file_system import search_files_by_ext, is_parent_dir_required
from core.utils.strings import (
    match_list_elem_date,
    match_list_mult,
    split_char,
    match_list_single,
)


def search_db_like(
    cur: sqlite3, table: str, field: str, query: str
) -> Optional[List[Tuple[...]]]:
    """Perform a ``SQL`` database search with the ``like``  parameter in a SQLite3 database.

    :param cur: ``sqlite3`` db cursor object
    :param table: ``str`` table in the db schema
    :param field: ``str`` field you want to match with ``like``
    :param query: ``str`` database query in ``SQL``
    :return: ``list[tuple[...]]`` or ``None``
    """
    qry: str = f'SELECT * FROM {table} WHERE {field} like "{query}%"'
    return cur.execute(qry).fetchall()


def get_from_db(cur: sqlite3, field: str, table: str) -> Optional[List[Tuple[...]]]:
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


def content_select_db_match(
    hint_lst: List[str],
    content_hint: str,
    dir: str = "",
    prompt_db: bool = False,
    parent: bool = False,
) -> Tuple[Connection, Cursor, str, int]:
    """Give a list of databases, match them with multiple hints, and retrieves the most up-to-date filename.
    This is a specialised implementation based on the ``filename_select`` function in the ``core.utils.file_system`` module.

    ``content_select_db_match`` finds a common index where the correct partner offer and database are located
    within two separate lists: the available ``.db`` file list and a list of partner offers.
    In order to accomplish this, the modules in the ``tasks`` package apply a consistent naming convention that
    looks like ``partner-name-content-type-date-in-ISO-format``; those filenames are further analysed by an algorithm
    that matches strings found in a lookup list.

    For more information on how this matching works and the algorithm behind it, refer to the documentation for
    ``match_list_mult`` and ``match_list_elem_date`` in the ``core.utils.strings`` module.

    **Note: As part of the above-mentioned naming convention, the files include a content type hint.
    This allows the algorithm to identify video or photo databases, depending on the module
    calling the function. However, this hint can be any word that you use consistently in your filenames.
    Also, if you want to access the file in the parent dir, either let the destination function handle it for you
    or specify it yourself. Everytime Python runs the file as a module or runs it on an interpreter outside your
    virtual environment, relative paths prove inefficient. However, this issue has been largely solved by using
    package notation with standard library and local implementations.**

    :param hint_lst: ``list[str]`` words/patterns to match.
    :param content_hint: ``str`` type of content, typically ``vids`` or ``photos``
    :param prompt_db: ``True`` if you want to prompt the user to select db. Default ``False``.
    :param dir: ``str`` where you want to look for relevant files
    :param parent: ``True`` to search in parent dir, default set to ``False``.
    :return: ``tuple[Connection, Cursor, str, int]`` (database connection, database cursor, database name, common index int)
    """

    console = Console()

    available_files: List[str] = search_files_by_ext("db", folder=dir, parent=parent)
    filtered_files: List[str] = match_list_elem_date(
        hint_lst,
        available_files,
        join_hints=(True, " ", "-"),
        ignore_case=True,
        strict=True,
    )

    relevant_content: List[str] = [
        filtered_files[indx] for indx in match_list_mult(content_hint, filtered_files)
    ]

    # Replacing the line below with the one above
    # relevant_content: list[str] = list(
    #     map(
    #         lambda indx: filtered_files[indx],
    #         match_list_mult(content_hint, filtered_files),
    #     )
    # )

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
        clean_hint: List[str] = hint_lst[(int(select_partner) - 1)].split(spl_char)

        select_file: int = 0
        for hint in clean_hint:
            rel_content: int = match_list_single(
                hint, relevant_content, ignore_case=True
            )
            if hint:
                if rel_content:
                    select_file = rel_content
                    break
            else:
                continue

        is_parent: str = (
            is_parent_dir_required(parent) if dir == "" else os.path.abspath(dir)
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


def get_model_set(db_cursor: sqlite3, table: str) -> set[str]:
    """Query the database and isolate the values of a single column to aggregate them
    in a set of str. In this case, the function isolates the ``models`` field from a
    table that the user specifies.

    :param db_cursor: ``sqlite3`` database cursor
    :param table: ``str`` table you want to consult.
    :return: ``set[str]``
    """
    models: List[Tuple[str]] = get_from_db(db_cursor, "models", table)
    new_lst: List[str] = [
        model[0].strip(",") for model in models if model[0] is not None
    ]
    return {
        elem
        for model in new_lst
        for elem in (model.split(",") if re.findall(r",+", model) else [model])
    }
