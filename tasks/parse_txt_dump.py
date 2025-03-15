"""
TXT Dump parser module

This module parses a specific type of .txt file called `dump`.
Those files contain important video metadata that will be inserted into a database for processing and structure.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
import re
import sqlite3

# Local implementations
from core import helpers


# Make sure that you get a dump file with all these fields:
# Dump format: Dump with | (Select this one on MongerCash)
# name | description | models | tags | site_name | date | source | thumbnail | tracking
def parse_txt_dump_chain(
    filename: str,
    d_name: str,
    d_conn: sqlite3,
    d_cur: sqlite3,
    dirname: str = "",
    parent: bool = False,
) -> tuple[str, int]:
    """Parse the ``.txt`` file provided, organize and insert the values into a ``sqlite3`` database.

    :param filename: ``str`` name of the file to be parsed
    :param d_name: ``str`` Desired name for the resulting database
    :param d_conn: ``sqlite3`` db connection object
    :param d_cur:  ``sqlite3`` db cursor of your connection object
    :param dirname: ``str`` Where to find the `dump` file in your system.
    :param parent: ``bool`` look for the file in the parent directory
    :return: ``tuple[str, int]`` (abs_path_db, total_entries_in_db)
    """
    cl_fname = helpers.clean_filename(filename, "txt")
    if dirname:
        path = os.path.join(dirname, cl_fname)
    else:
        path = os.path.join(helpers.is_parent_dir_required(parent), cl_fname)

    total_entries = 0
    with open(path, "r", encoding="utf-8") as dump_file:
        for line in dump_file.readlines():
            try:
                dump_line = line.split("|")

                # I am not interested in videos that don't point to a source URL.
                # In some cases, their tags are moved to the source URL field
                # and that breaks the slug construction.
                if dump_line[6] == "" or re.match("http", dump_line[6]) is None:
                    continue

                title = dump_line[0]
                description = dump_line[1]
                model = dump_line[2]
                if model == "":
                    model = None

                tags = dump_line[3]
                if tags == "":
                    tags = None

                date = str(helpers.parse_date_to_iso(dump_line[5], m_abbr=True))

                # The duration comes at the end of source urls.
                pre_duration = dump_line[6].split("/")[-1:][0].split("_")
                if len(pre_duration) >= 2:
                    duration = (
                        dump_line[6].split("/")[-1:][0].split("_")[-1:][0].split(".")[0]
                    )
                else:
                    duration = None
                source_url = dump_line[6]
                thumbnail_url = dump_line[7]
                tracking_url = dump_line[8].strip("\n")
                site_name = dump_line[4]

                # Pre_slug is taken from the source URL slug without the
                # duration value.
                pre_slug = "-".join(dump_line[6].split("/")[-1:][0].split("_")[:-1])

                if pre_slug == "":
                    post_slug = dump_line[6].split("/")[-1:][0]
                    # Sometimes, the last element contains a file extension
                    # and I don't want that in my url slugs.
                    if re.findall("[.+]", post_slug) is not None:
                        post_slug = dump_line[6].split("/")[-1:][0].split(".")[0]
                else:
                    post_slug = pre_slug

                wp_slug = "-".join(site_name.split(" ")).lower() + "-" + post_slug

                all_values = (
                    title,
                    description,
                    model,
                    tags,
                    date,
                    duration,
                    source_url,
                    thumbnail_url,
                    tracking_url,
                    wp_slug,
                )

                d_cur.execute(
                    "INSERT INTO videos VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    all_values,
                )
                d_conn.commit()

                total_entries += 1
            except IndexError:
                # This is a pattern.
                # When it reaches the end and there is no more data, Python
                # throws an IndexError in this function.
                d_cur.close()
                d_conn.close()
                break

        return f"{os.path.abspath(d_name)}", total_entries
