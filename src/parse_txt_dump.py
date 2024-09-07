from datetime import date, datetime
from calendar import month_abbr, day_name
import re
import sqlite3
import os

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

db_name = "asian_sex_diary_dump.db"

db_conn = sqlite3.connect(f"../{db_name}")
cursor = db_conn.cursor()
cursor.execute("""
CREATE TABLE 
    videos(title, 
    description, 
    model, 
    tags, 
    date, 
    duration, 
    source_url, 
    thumbnail_url, 
    tracking_url, 
    wp_slug)
""")

sum = 0
months = [m for m in month_abbr]
with open('../asd_dump.txt', 'r', encoding='utf-8') as dump_file:
    for line in dump_file.readlines():
        try:
            dump_line = line.split('|')
            title = dump_line[0]
            description = dump_line[1]
            model = dump_line[2]
            if model == '':
                model = None
            tags = dump_line[3]
            # Break down the date to iso format to get a date object.
            # dump_line[5] is initially 'Aug 20th, 2024'
            year_date = str(dump_line[5].split(",")[1].strip())
            month_date_num = str(months.index(dump_line[5].split(",")[0].split(" ")[0]))
            # the date ISO format requires that single numbers are preceded by a 0.
            if int(month_date_num) <= 9:
                month_date_num = '0' + str(months.index(dump_line[5].split(",")[0].split(" ")[0]))
            
            day_nth = str(dump_line[5].split(",")[0].split(" ")[1])
            day_date = day_nth.strip("".join(re.findall("[a-z]", day_nth)))
            if int(day_date) <= 9:
                day_date = '0' + day_nth.strip("".join(re.findall("[a-z]", day_nth)))
            date = date.fromisoformat(year_date + month_date_num + day_date)

            # the duration comes at the end of urls
            duration = dump_line[6].split('/')[-1:][0].split('_')[-1:][0].split('.')[0]
            source_url = dump_line[6]
            thumbnail_url = dump_line[7]
            tracking_url = dump_line[8].strip('\n')
            site_name = dump_line[4]
            pre_slug = "-".join(dump_line[6].split('/')[-1:][0].split('_')[:-1])
            wp_slug = "-".join(site_name.split(" ")).lower() + '-' + pre_slug
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
            db_conn.close()
            break

db_path = f'{os.path.dirname(os.getcwd())}/{db_name}'
print(f'{sum} videos entries have been processed and inserted into\n{db_path}')
