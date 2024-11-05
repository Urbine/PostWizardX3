"""
This module parses a specific type of .txt file
called dumps. Those files contain important video metadata that will be
inserted into a database for later use.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

import os
import re
import sqlite3
import datetime

# Local implementations
from common import helpers


# Fields I need
# 1.  Video title  - OK
# 2.  Video Description - OK
# 3.  Thumbnail - OK
# 4.  Tags - OK
# 5.  Video source - OK
# 6.  Tracking link - OK
# 7.  Date - OK
# 8.  Video type - OK
# 9.  Models - OK
# 10. Site name - OK
# 11. WP-Ready Slug - OK



# Make sure that you get a dump file with all these fields:
# Dump format: Dump with | (Select this one on MongerCash)
# name | description | models | tags | site_name | date | source | thumbnail | tracking
def parse_txt_dump(filename: str, d_name: str, d_conn: sqlite3,
                   d_cur: sqlite3, dirname: str = '', parent: bool = False):
    if dirname:
        path = f"{dirname}/{helpers.clean_filename(filename, 'txt')}"
    else:
        path = f"{helpers.is_parent_dir_required(parent=parent)}{helpers.clean_filename(filename, 'txt')}"

    total_entries = 0
    with open(path,'r', encoding='utf-8') as dump_file:
        for line in dump_file.readlines():
            try:
                dump_line = line.split('|')

                # I am not interested in videos that don't point to a source URL.
                # In some cases, their tags are moved to the source URL field and that breaks the slug construction.
                if dump_line[6] == '' or re.match("http", dump_line[6]) is None:
                    continue

                title = dump_line[0]
                description = dump_line[1]
                model = dump_line[2]
                if model == '':
                    model = None

                tags = dump_line[3]
                if tags == '':
                    tags = None

                # Break down the date and convert it to ISO format to get a date object.
                # dump_line[5] is initially 'Aug 20th, 2024' but I want a datetime.date object.
                date = str(helpers.parse_date_to_iso(dump_line[5], m_abbr=True))

                # The duration comes at the end of source urls.
                pre_duration = dump_line[6].split('/')[-1:][0].split('_')
                if len(pre_duration) >= 2:
                    duration = dump_line[6].split('/')[-1:][0].split('_')[-1:][0].split('.')[0]
                else:
                    duration = None
                source_url = dump_line[6]
                thumbnail_url = dump_line[7]
                tracking_url = dump_line[8].strip('\n')
                site_name = dump_line[4]

                # Pre_slug is taken from the source URL slug without the duration value.
                pre_slug = "-".join(dump_line[6].split('/')[-1:][0].split('_')[:-1])

                if pre_slug == '':
                    post_slug = dump_line[6].split('/')[-1:][0]
                    # Sometimes, the last element contains a file extension
                    # and I don't want that in my url slugs.
                    if re.findall("[.+]", post_slug) is not None:
                        post_slug = dump_line[6].split('/')[-1:][0].split(".")[0]
                else:
                    post_slug = pre_slug

                # This url slug must be ready for WordPress.
                wp_slug = "-".join(site_name.split(" ")).lower() + '-' + post_slug

                all_values = (title,
                              description,
                              model,
                              tags,
                              date,
                              duration,
                              source_url,
                              thumbnail_url,
                              tracking_url,
                              wp_slug)

                d_cur.execute("INSERT INTO videos VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               all_values)
                d_conn.commit()

                total_entries += 1
            except IndexError:
                # This is a pattern.
                # When it reaches the end and there is no more data, Python throws an IndexError.
                d_conn.close()
                break

        return f'{os.path.dirname(os.getcwd())}/{d_name}', total_entries


if __name__ == '__main__':

    # the db names could be gathered via input
    # listed here for convenience
    db_name_suggest = [f'asian-sex-diary-vids-{datetime.date.today()}.db',
                       f'trike-patrol-vids_{datetime.date.today()}.db',
                       f'tuktuk-patrol-vids-{datetime.date.today()}.db']

    db_name = helpers.filename_creation_helper(db_name_suggest, extension='db')

    db_conn = sqlite3.connect(f"{helpers.is_parent_dir_required(parent=True)}{db_name}")
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

    # As you will notice, this list will be useful
    # to get a month number from an abbreviation.

    print("Available .txt files in the parent dir:\n")
    # Gets txt files in the project directory
    txt_files = helpers.search_files_by_ext('txt', '', parent=True)
    for fnum, f in enumerate(txt_files, start=1):
        print(f'{fnum}. {f}')

    file_select = input("\nPick a txt to parse: ")
    try:
        dump_file_name = txt_files[int(file_select) - 1]
    except IndexError:
        raise IndexError(f'There are {len(txt_files)} .txt files in {os.path.dirname(os.getcwd())}\nTry again!')

    parsing = parse_txt_dump(dump_file_name, db_name ,cursor, db_conn, parent=True)

    print(f'{parsing[1]} video entries have been processed from {dump_file_name} and inserted into\n{parsing[0]}')
