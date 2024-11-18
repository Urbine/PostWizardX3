import argparse
import datetime
import os.path
import sqlite3

# Local implementations
import core
from core.helpers import clean_file_cache
from .url_builder import CSVColumns, CSVSeparators

# Constants

ABJAV_BASE_URL = "https://direct.abjav.com"
ABJAV_CAMPAIGN_ID = 1291575419


def construct_api_dump_url(
        base_url: str,
        campgn_id: str | int,
        sort_crit: str,
        days: str | int = "",
        url_limit: str | int = 999999999,
        sep: CSVSeparators = CSVSeparators.pipe_sep,
        columns: CSVColumns = CSVColumns
) -> str:
    """
    Construct the API dump url to access the text content to be parsed by function `adult_next_dump_parse`
    once accessed.

    :param columns:
    :param base_url: API Base URL (provided in this module as a constant)
    :param campgn_id: Campaign ID (provided in this module as a constant)
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
    params = "/feeds/?link_args="
    campaign_id = f"campaign_id:{campgn_id}"
    format = "&feed_format=csv&"
    # rating, popularity, duration, post_date, ID
    sorting = f"sorting={sort_crit}&"
    limit = f"limit={url_limit}"
    sep_param = f"&csv_separator={sep}&"
    days = f"days={days}&" if days != "" else days

    # Column Fields
    column_lst = [
        columns.ID_,
        columns.title,
        columns.duration,
        columns.added_time,
        columns.categories,
        columns.rating,
        columns.main_thumbnail,
        columns.embed_code,
        columns.link
    ]

    csv_columns = f"csv_columns={str(sep).join(column_lst)}"

    return f"{base_url}{params}{campaign_id}{format}{sorting}{days}{limit}{sep_param}{csv_columns}"


def adult_next_dump_parse(filename: str, dirname: str,
                          partner: str, sep: str) -> str:
    """
    Parse the text dump based on the parameters that ``construct_api_dump_url`` constructed.
    Once the temporary text file is fetched from the origin, this function will record all the values
    into a ``SQLite3`` database.

    :param filename: ``str`` temporary ``CSV`` filename that will be used as the database filename
    :param dirname: ``str`` provide a target path for the database
    :param partner: ``str`` Partner offer name that will be used to construct the video slugs in the database.
    :param sep: ``str`` character separator depending on the separator constant selected at URL build (typically ``'|'``).
    :return: ``f-str`` (Formatted str) with the video count and database name.
    """
    # Sample layout of the text file to be parsed
    # ID|Title|Description|Website link|Duration|Rating|Publish date,
    # time|Categories|Tags|Models|Embed code|Thumbnail prefix|Main
    # thumbnail|Thumbnails|Preview URL
    c_filename = core.clean_filename(filename, 'csv')
    is_parent_dir = False if os.path.exists(
        f'./{dirname}/{c_filename}') else True
    path = f"{core.is_parent_dir_required(is_parent_dir)}{dirname}/{core.clean_filename(filename, 'csv')}"
    db_name = f"{core.is_parent_dir_required(parent=is_parent_dir)}{filename}-{datetime.date.today()}.db"
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
                continue
            else:
                line_split = line.split(sep)
                id_ = line_split[0]
                title = line_split[1]
                duration = line_split[2]
                publish_date = line_split[3].split(" ")[0]
                categories = line_split[4]
                rating = line_split[5]
                main_thumbnail = line_split[6]
                embed_code = line_split[7]
                website_link = line_split[8]

                # Custom db fields

                # As mentioned in other modules, slugs have to contain the
                # content type
                wp_slug = f"{website_link.split('/')[-2:][0]}-{partner}-video"

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
                    wp_slug
                )

                db_cur.execute(
                    "INSERT INTO embeds values(?,?,?,?,?,?,?,?,?,?)",
                    all_values,
                )
                db_conn.commit()
                total_entries += 1

    db_conn.close()
    return f"Inserted a total of {total_entries} video entries into {db_name}"


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='AdultNext integration - CLI Interface')

    arg_parser.add_argument('-sort', type=str,
                            help="""Sorting criteria from possible values:
                                      1. popularity
                                      2. rating
                                      3. duration
                                      4. post_date
                                      5. id (default if no criteria is provided)""")

    arg_parser.add_argument('-days', type=int,
                            help='Provide the time period in days')

    arg_parser.add_argument(
        '-limit',
        type=int,
        help='amount of urls to process')

    cli_args = arg_parser.parse_args()

    # Build the URL
    main_url = construct_api_dump_url(
        ABJAV_BASE_URL, ABJAV_CAMPAIGN_ID, cli_args.sort, days=cli_args.days, url_limit=cli_args.limit
    )

    # Use it to fetch the stream for the `write_to_file` functions.
    core.write_to_file(
        "abjav-dump", "tmp", "csv", core.access_url_bs4(main_url)
    )

    # Parse the temporary csv and generate the database with the data.
    result = adult_next_dump_parse("abjav-dump", "./tmp", 'jav', "|")

    # Clean the temp .csv file in temporary folder
    clean_file_cache('tmp', 'csv')
    print(result)
    print('Cleaned temporary folder...')
