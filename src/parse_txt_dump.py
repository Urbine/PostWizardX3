from calendar import month_abbr
from datetime import date
import helpers
import os
import re
import sqlite3

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

# the db names could be gathered via input
# listed here for convenience
db_name_suggest = ["asian_sex_diary_dump.db",
                   "trike_patrol_dump.db",
                   "tuktuk_patrol_dump.db"]

print('Suggested database names:\n')
for num,db in enumerate(db_name_suggest, start=1):
    print(f'{num}. {db}')

db_name_select = input('\nPick a number to create your database or else type in a name now: ')
try:
    db_name = db_name_suggest[int(db_name_select)-1]
except ValueError or IndexError:
    if len(db_name_select.split(".")) >= 2:
        db_name = db_name_select
    elif db_name_select == '':
        raise RuntimeError("You really need a database name to continue.")
    else:
        db_name = db_name_select + '.db'

db_conn = sqlite3.connect(f"../{db_name}")
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

# This variable will count the video entries that will be inserted into the db
sum = 0

# As you will notice, this list will be useful
# to get a month number from an abbreviation.
months = [m for m in month_abbr]

print("Available .txt files in the parent dir:\n")
# Gets txt files in the project directory
txt_files = helpers.search_files_by_ext('txt', parent=True)
for fnum, f in enumerate(txt_files, start=1) :
    print(f'{fnum}. {f}')

file_select = input("\nPick a txt to parse: ")
try:
    dump_file_name = txt_files[int(file_select)-1]
except IndexError:
    raise IndexError(f'There are {len(txt_files)} .txt files in {os.path.dirname(os.getcwd())}\nTry again!')

# Make sure that you get a dump file with all these fields:
# Dump format: Dump with | (Select this one on MongerCash)
# name | description | models | tags | site_name | date | source | thumbnail | tracking

with (open(f'../{dump_file_name}', 'r', encoding='utf-8') as dump_file):
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
            year_date = str(dump_line[5].split(",")[1].strip())
            month_date_num = str(months.index(dump_line[5].split(",")[0].split(" ")[0]))

            # The date ISO format requires that single numbers are preceded by a 0.
            if int(month_date_num) <= 9:
                month_date_num = '0' + str(months.index(dump_line[5].split(",")[0].split(" ")[0]))
            
            day_nth = str(dump_line[5].split(",")[0].split(" ")[1])
            day_date = day_nth.strip("".join(re.findall("[a-z]", day_nth)))

            if int(day_date) <= 9:
                day_date = '0' + day_nth.strip("".join(re.findall("[a-z]", day_nth)))
            date = date.fromisoformat(year_date + month_date_num + day_date)

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

            cursor.execute("INSERT INTO videos VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        all_values)
            db_conn.commit()

            sum = sum + 1
        except IndexError:
            # This is a pattern.
            # When it reaches the end and there is no more data, Python throws an IndexError.
            db_conn.close()
            break

db_path = f'{os.path.dirname(os.getcwd())}/{db_name}'
print(f'{sum} video entries have been processed from {dump_file_name} and inserted into\n{db_path}')

