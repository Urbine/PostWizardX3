import argparse
import sys
import warnings

# Local implementations
import content_select
import helpers
import feed_scrape
import feed_dump_create
import parse_txt_dump
import sets_source_parse


print('Welcome to the media_source local update wizard')

""" *** Steps to update the database from MediaSource ***
1. Get the dump and source files to create the photosets and vid databases. 
2. Call the parsing modules on the text dump and HTML sources. 
3. Clean the file cache and tidy up.

"""
arg_parser = argparse.ArgumentParser(description="media_source local update wizard arguments")

arg_parser.add_argument('temp_dir', type=str,
                        help='Relative or absolute path to your temp directory')

arg_parser.add_argument('--gecko', action='store_true',
                        help='Use the Gecko webdriver for this process.')

arg_parser.add_argument('--headless', action='store_true',
                        help='Browser headless execution.')

args = arg_parser.parse_args()

media_source_hosted_vids = feed_scrape.media_source_hosted_vids
media_source_downloadable_sets = feed_scrape.media_source_downloadable_sets

temp_folder = args.temp_dir
webdriver = helpers.get_webdriver(temp_folder, headless=args.headless, gecko=args.gecko)

username = helpers.get_client_info('client_info.json',
                                   parent=True)['MediaSource']['username']

password = helpers.get_client_info('client_info.json',
                                   parent=True)['MediaSource']['password']


dump_file_name = feed_dump_create.get_vid_dump_flow(media_source_hosted_vids, temp_folder,
                      (username, password), webdriver)

# Test if the file contains characters and it is not empty.
# If the file is empty, it means that something went wrong with the webdriver.
load_dump_file = helpers.load_from_file(f'{temp_folder}/dump_file_name', 'txt')
while len(load_dump_file) == 0:
    warnings.warn('The content of the dump file is empty, retrying...', UserWarning)
    dump_file_name = feed_dump_create.get_vid_dump_flow(media_source_hosted_vids, temp_folder,
                      (username, password), webdriver)
    continue

