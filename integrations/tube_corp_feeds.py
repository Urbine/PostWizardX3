"""
Gather information from the VJAV and DesiTube public APIs, parse it and insert it into a SQLite3 database.
Provides interactivity via CLI for users.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import datetime
import os
import sqlite3
import tempfile
import urllib.parse

from dataclasses import dataclass

# Local implementations
import core
from .url_builder import CSVColumns, URLEncode
from core.helpers import remove_if_exists, parse_client_config


@dataclass(frozen=True)
class TubeCorpUrl:
    """
    Builder class for the TubeCorporate Feed intergration.
    """

    vjav_base_url: str = "https://vjav.com/admin/feeds/embed/?source="
    desi_t_url: str = "https://desiporn.tube/admin/feeds/embed/?source="


class TubeDumpURL:
    """
    Builder class for the Tube Corporate URL object.
    """

    def __init__(
        self,
        base_url: str,
        sort_crit: str,
        days: str | int = "",
        url_limit: str | int = 999999999,
        sep: URLEncode = URLEncode.PIPE,
    ) -> None:
        self.base_url = base_url
        self.format = "&feed_format=csv&"
        self.scrshot_f = "screenshot_format=source&"
        self.sort_crit = (
            f"sorting={sort_crit}&"  # rating, popularity, duration, post_date, ID
        )
        self.period = f"days={days}&" if days != "" else days
        self.limit = f"limit={url_limit}"
        self.sep = f"&csv_separator={sep}"
        self.__an_url = (
            self.base_url
            + self.format
            + self.scrshot_f
            + self.sort_crit
            + self.period
            + self.limit
            + self.sep
        )

    def __str__(self):
        return self.__an_url


def construct_tube_dump_url(
    base_url: str,
    sort_crit: str,
    days: str | int = "",
    url_limit: str | int = 999999999,
    sep: URLEncode = URLEncode.PIPE,
    columns: CSVColumns = CSVColumns,
) -> str:
    """
    Construct the API dump url to access the text content to be parsed by function `adult_next_dump_parse`
    once accessed.

    :param base_url: API Base URL (provided in this module as a constant)
    :param sort_crit: Sorting criteria from possible values:

                      1. ``'popularity'``
                      2. ``'rating'``
                      3. ``'duration'``
                      4. ``'post_date'``
                      5. ``'id'`` **(default if no criteria is provided)**

    :param sep: ``CSVSeparator`` Object that contains the dump separation code
    :param days: time period scope in days
    :param url_limit: maximum value of URLs to retrieve.
    :param columns: ``CSVColumns`` object that contains common csv columns.
    :return: ``f-str`` (Formatted str) Video Dump URL
    """
    column_lst = [
        columns.ID_,
        columns.title,
        columns.duration,
        columns.added_time,
        columns.categories,
        columns.rating,
        columns.main_thumbnail,
        columns.embed_code,
        columns.link,
    ]

    csv_columns = f"&csv_columns={str(sep).join(column_lst)}"

    return f"{TubeDumpURL(base_url, sort_crit, days, url_limit, sep)!s}{csv_columns}"


def tube_dump_parse(filename: str, dirname: str, partner: str, sep: str) -> str:
    """
    Parse the text dump based on the parameters that ``construct_vjav_dump_url`` constructed.
    Once the temporary text file is fetched from the origin, this function will record all the values
    into a ``SQLite3`` database.

    :param filename: ``str`` temporary ``CSV`` filename that will be used as the database filename
    :param dirname: ``str`` provide a target path for the database
    :param partner: ``str`` Partner offer name that will be used to construct the video slugs in the database.
    :param sep: ``str`` character separator depending on the separator constant selected at URL build (typically ``'|'``).
    :return: ``f-str`` (Formatted str) with the video count and database name.
    """
    # Sample layout of the text file to be parsed, however, not the actual dump.
    # ID|Title|Description|Website link|Duration|Rating|Publish date,
    # time|Categories|Tags|Models|Embed code|Thumbnail prefix|Main
    # thumbnail|Thumbnails|Preview URL
    c_filename = core.clean_filename(filename, "csv")
    path = os.path.join(os.path.abspath(dirname), c_filename)
    db_name = os.path.join(os.getcwd(), f"{filename}-{datetime.date.today()}.db")
    remove_if_exists(db_name)
    db_conn = sqlite3.connect(db_name)
    db_cur = db_conn.cursor()

    db_create_table = """
    CREATE TABLE embeds(id,
                        title,
                        duration,
                        date,
                        categories,
                        rating,
                        thumbnail,
                        embed_code,
                        web_link,
                        wp_slug)
    """
    db_cur.execute(db_create_table)

    total_entries = 0
    with open(path, "r", encoding="utf-8") as dump_file:
        for line in dump_file.readlines():
            # I don't want to process or count the header of the csv file.
            if total_entries == 0:
                total_entries += 1
            else:
                line_split = line.split(urllib.parse.unquote(sep))
                id_ = line_split[0]
                title = line_split[1]
                duration = line_split[2]
                publish_date = line_split[3].split(" ")[0]
                categories = line_split[4]
                rating = line_split[5]
                main_thumbnail = line_split[6]
                embed_code = line_split[7]
                website_link = line_split[8]

                wp_slug = (
                    f"{website_link.split('/')[-2:][0]}-{partner}-video"
                    if partner != ""
                    else f"{website_link.split('/')[-2:][0]}-video"
                )

                all_values = (
                    id_,
                    title,
                    duration,
                    publish_date,
                    categories,
                    rating,
                    main_thumbnail,
                    embed_code,
                    website_link,
                    wp_slug,
                )

                db_cur.execute(
                    "INSERT INTO embeds values(?,?,?,?,?,?,?,?,?, ?)",
                    all_values,
                )
                db_conn.commit()
                total_entries += 1

    db_cur.close()
    db_conn.close()
    return f"Inserted a total of {total_entries} video entries into {db_name}"


def main(*args, **kwargs):
    task_conf = parse_client_config("tasks_config", "core.config")
    source_id = task_conf["tubecorp_feeds"]["source_id"]
    vjav_url = f"{TubeCorpUrl.vjav_base_url}{source_id}"
    desi_url = f"{TubeCorpUrl.desi_t_url}{source_id}"

    main_url = construct_tube_dump_url(vjav_url, *args, **kwargs)

    temp_dir = tempfile.TemporaryDirectory(dir=".")

    core.write_to_file("vjav-dump", temp_dir.name, "csv", core.access_url_bs4(main_url))

    result = tube_dump_parse("vjav-dump", temp_dir.name, "jav", URLEncode.PIPE)

    print(result)

    main_url = construct_tube_dump_url(desi_url, *args, **kwargs)

    core.write_to_file(
        "desi-tube-dump", temp_dir.name, "csv", core.access_url_bs4(main_url)
    )

    result = tube_dump_parse("desi-tube-dump", temp_dir.name, "", URLEncode.PIPE)

    temp_dir.cleanup()
    print(result)
    print("Cleaned temporary folder...")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Tube Corporate feeds integration - CLI Interface"
    )

    arg_parser.add_argument(
        "-sort",
        type=str,
        help="""Sorting criteria from possible values:
                                  1. popularity
                                  2. rating
                                  3. duration
                                  4. post_date
                                  5. id (default if no criteria is provided)""",
    )

    arg_parser.add_argument("-days", type=int, help="Provide the time period in days")

    arg_parser.add_argument("-limit", type=int, help="amount of urls to process")

    cli_args = arg_parser.parse_args()

    main(cli_args.sort, cli_args.days, url_limit=cli_args.limit)
