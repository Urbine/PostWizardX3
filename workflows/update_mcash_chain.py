import argparse
import sqlite3
import warnings


# Local implementations
from common import (
    is_parent_dir_required,
    get_webdriver,
    load_from_file,
    clean_filename,
    MONGER_CASH_INFO,
)

from tasks.mcash_dump_create import M_CASH_DUMP_URL, get_vid_dump_flow

from tasks.mcash_scrape import M_CASH_SETS_URL, get_page_source_flow

from tasks.parse_txt_dump import parse_txt_dump
from tasks.sets_source_parse import db_generate
from workflows.content_select import clean_file_cache

print("Welcome to the MongerCash local update wizard")

""" *** Steps to update the database from MongerCash ***
(if I were to do it manually)
1. Get the dump and source files to create the photosets and vid databases.
2. Call the parsing modules on the text dump and HTML sources.
3. Clean the file cache and tidy up.
4. Clean outdated files.
"""

# TODO: Make a function to clean old .db files by extracting the last
# datetime object from the name.
arg_parser = argparse.ArgumentParser(description="mcash local update wizard arguments")

arg_parser.add_argument(
    "temp_dir", type=str, help="Relative or absolute path to your temp directory"
)

arg_parser.add_argument(
    "--hint",
    type=str,
    help="This parameter receives the first word of the partner offer for matching",
)

arg_parser.add_argument(
    "--parent",
    action="store_true",
    help="Set if you want the resulting files to be located in the parent dir.",
)

arg_parser.add_argument(
    "--gecko", action="store_true", help="Use the Gecko webdriver for this process."
)

arg_parser.add_argument(
    "--headless", action="store_true", help="Browser headless execution."
)

arg_parser.add_argument("--silent", action="store_true", help="Ignore user warnings")

args = arg_parser.parse_args()

if args.silent:
    warnings.filterwarnings("ignore")
else:
    pass

m_cash_downloadable_sets = M_CASH_SETS_URL
m_cash_vids_dump = M_CASH_DUMP_URL

temp_dir = args.temp_dir
webdriver = get_webdriver(temp_dir, headless=args.headless, gecko=args.gecko)

username = MONGER_CASH_INFO.username

password = MONGER_CASH_INFO.password

# Fetching

dump_file_name = get_vid_dump_flow(
    m_cash_vids_dump,
    temp_dir,
    (username, password),
    webdriver,
    parent=None,
    partner_hint=args.hint,
)

# Test if the file contains characters and it is not empty.
# If the file is empty, it means that something went wrong with the webdriver.
load_dump_file = load_from_file(dump_file_name, "txt", dirname=temp_dir, parent=None)
while len(load_dump_file) == 0:
    warnings.warn("The content of the dump file is empty, retrying...", UserWarning)
    dump_file_name = get_vid_dump_flow(
        m_cash_vids_dump,
        temp_dir,
        (username, password),
        webdriver,
        parent=None,
        partner_hint=args.hint,
    )
    load_dump_file = load_from_file(
        dump_file_name, "txt", dirname=temp_dir, parent=None
    )
    continue

# webdriver gets a second assignment to avoid connection pool issues.
webdriver = get_webdriver(temp_dir, headless=args.headless, gecko=args.gecko)
photoset_source = get_page_source_flow(
    m_cash_downloadable_sets, (username, password), webdriver, partner_hint=args.hint
)

# Just like the text dump, the source code could be empty and I need to
# test it.
while len(photoset_source[0]) == 0:
    warnings.warn("The source file is empty, retrying...", UserWarning)
    photoset_source = get_page_source_flow(
        m_cash_downloadable_sets, (username, password), webdriver
    )
    continue

# Parsing video txt dump:

db_name = clean_filename(dump_file_name, "db")
db_conn = sqlite3.connect(f"{is_parent_dir_required(parent=args.parent)}{db_name}")
cursor = db_conn.cursor()
cursor.execute(
    """
CREATE TABLE
    videos(
    title,
    description,
    model,
    tags,
    date,
    duration,
    source_url,
    thumbnail_url,
    tracking_url,
    wp_slug
    )
"""
)

parsing = parse_txt_dump(
    dump_file_name, db_name, db_conn, cursor, dirname=temp_dir, parent=args.parent
)
print(
    f"{parsing[1]} video entries have been processed from {dump_file_name} and inserted into\n{parsing[0]}\n"
)

parsing_photos = db_generate(photoset_source[0], photoset_source[1], parent=args.parent)
print(
    f"{parsing_photos[1]} photo set entries have been processed and inserted into\n{parsing_photos[0]}\n"
)

# Tidy up
print(f"Cleaning temporary directory {temp_dir}")
clean_file_cache(temp_dir, "*")
