import argparse
import sqlite3
import sys
import warnings

# Local implementations
import content_select
import helpers
import mcash_scrape
import mcash_dump_create
import parse_txt_dump
import sets_source_parse


print('Welcome to the mcash local update wizard')

""" *** Steps to update the database from MongerCash ***
(if I were to do it manually)
1. Get the dump and source files to create the photosets and vid databases. 
2. Call the parsing modules on the text dump and HTML sources. 
3. Clean the file cache and tidy up.

Workflow:


"""

# TODO: Make a function to clean old .db files by extracting the last datetime object from the name.
arg_parser = argparse.ArgumentParser(description="mcash local update wizard arguments")

arg_parser.add_argument('temp_dir', type=str,
                        help='Relative or absolute path to your temp directory')

arg_parser.add_argument('--parent', action='store_true',
                        help='Set if you want the resulting files to be located in the parent dir.')

arg_parser.add_argument('--gecko', action='store_true',
                        help='Use the Gecko webdriver for this process.')

arg_parser.add_argument('--headless', action='store_true',
                        help='Browser headless execution.')

arg_parser.add_argument('--silent', action='store_true',
                        help='Ignore user warnings')

args = arg_parser.parse_args()

if args.silent:
    warnings.filterwarnings('ignore')
else:
    pass

m_cash_hosted_vids = mcash_scrape.m_cash_hosted_vids
m_cash_downloadable_sets = mcash_scrape.m_cash_downloadable_sets

temp_dir = args.temp_dir
webdriver = helpers.get_webdriver(temp_dir, headless=args.headless, gecko=args.gecko)

username = helpers.get_client_info('client_info.json',
                                   parent=True)['MongerCash']['username']

password = helpers.get_client_info('client_info.json',
                                   parent=True)['MongerCash']['password']

# Fetching

dump_file_name = mcash_dump_create.get_vid_dump_flow(m_cash_hosted_vids, temp_dir,
                      (username, password), webdriver)

# Test if the file contains characters and it is not empty.
# If the file is empty, it means that something went wrong with the webdriver.
load_dump_file = helpers.load_from_file(f'{temp_dir}/dump_file_name', 'txt')
while len(load_dump_file) == 0:
    warnings.warn('The content of the dump file is empty, retrying...', UserWarning)
    dump_file_name = mcash_dump_create.get_vid_dump_flow(m_cash_hosted_vids, temp_dir,
                      (username, password), webdriver)
    load_dump_file = helpers.load_from_file(f'{temp_dir}/dump_file_name', 'txt')
    continue

photoset_source = mcash_scrape.get_page_source_flow(m_cash_downloadable_sets,
                                                    (username, password), webdriver)

# Just like the text dump, the source code could be empty and I need to test it.
while len(photoset_source[0]) == 0:
    warnings.warn('The source file is empty, retrying...', UserWarning)
    photoset_source = mcash_scrape.get_page_source_flow(m_cash_downloadable_sets,
                                                        (username, password), webdriver)
    continue

# Parsing video txt dump:
db_name_suggest = parse_txt_dump.db_name_suggest
db_name = helpers.filename_creation_helper(db_name_suggest, extension='db')
db_conn = sqlite3.connect(f"{helpers.is_parent_dir_required(parent=args.parent)}{db_name}")
cursor = db_conn.cursor()
cursor.execute("""
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
""")

parsing = parse_txt_dump.parse_txt_dump(dump_file_name, db_name,
                                        db_conn, cursor, parent=args.parent)
warnings.warn(f'{parsing[1]} video entries have been processed from {dump_file_name} and inserted into\n{parsing[0]}',
              UserWarning)

parsing_photos = sets_source_parse.db_generate(photoset_source[0],
                                               sets_source_parse.db_name_suggest, parent=args.parent)
warnings.warn(f'{parsing_photos[1]} photo set entries have been processed and inserted into\n{parsing_photos[0]}',
              UserWarning)

# Tidy up
warnings.warn(f'Cleaning temporary directory {temp_dir}', UserWarning)
content_select.clean_file_cache(temp_dir,'*', parent=None)


