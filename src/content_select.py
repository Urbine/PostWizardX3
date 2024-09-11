import random
import requests
import sqlite3

from main import database_select
from wordpress_api import wp_post_create, upload_thumbnail

print("Choose your Partner and WP databases:\n")
db_connection_dump = sqlite3.connect(database_select(parent=True))
cur_dump = db_connection_dump.cursor()
print('\n')
db_connection_wp = sqlite3.connect(database_select(parent=True))
cur_wp = db_connection_wp.cursor()

# Videos table - db_connection_dump
# CREATE TABLE
#     videos(title,
#     description,
#     model,
#     tags,
#     date,
#     duration,
#     source_url,
#     thumbnail_url,
#     tracking_url,
#     wp_slug)

query = """
SELECT 
title, 
description,  
tags,  
duration, 
source_url,
thumbnail_url,
tracking_url,
wp_slug FROM videos ORDER BY date DESC
"""

def fetch_videos_db(sql_query: str, db_cursor):
    db_cursor.execute(sql_query)
    return db_cursor.fetchall()

def is_published(title: str, db_cursor):
    search_vids = f'SELECT * FROM videos WHERE title="{title}"'
    if not db_cursor.execute(search_vids).fetchall():
        return False
    else:
        return True

def get_banner(banner_lst: list[str]):
    return random.choice(banner_lst)

def fetch_thumbnail(folder: str, slug: str, remote_res: str):
    thumbnail_dir = folder
    remote_data = requests.get(remote_res)
    with open(f"{folder}/{slug}.jpg", 'wb') as img:
        img.write(remote_data.content)
    return remote_data.status_code

def make_payload(vid_slug,
                 status_wp: str,
                 vid_name: str,
                 vid_description: str,
                 banner_tracking_url: str,
                 banner_img: str,
                 partner_name: str) -> dict:
    payload_post = {"slug": f"{vid_slug}",
                     "status": f"{status_wp}",
                     "type": "post",
                     "link": f"https://whoresmen.com/{vid_slug}/",
                     "title": f"{vid_name}",
                     "content": f"<p>{vid_description}</p><figure class=\"wp-block-image size-large\"><a href=\"{banner_tracking_url}\"><img decoding=\"async\" src=\"{banner_img}\" alt=\"{vid_name} | {partner_name} on WhoresMen.com\"/></a></figure>",
                     "excerpt": f"<p>{vid_description}</p>\n",
                     "author": 1,
                     "featured_media": 0}
    return payload_post

def video_upload_pilot(videos: list[tuple], banner_lsts: list[list[str]], cursor_wp):
    all_vals = videos
    wp_base_url = "https://whoresmen.com/wp-json/wp/v2"
    partners = ["Asian Sex Diary", "TukTuk Patrol", "Trike Patrol"]
    videos_uploaded = 0
    print('\n')
    for num, partner in enumerate(partners, start=1):
        print(f"{num}. {partner}")
    try:
        partner_indx = input("\n\nSelect your partner: ")
        partner = partners[int(partner_indx)-1]
        banners = banner_lsts[int(partner_indx)-1]
    except IndexError:
        partner_indx = input("\n\nSelect your partner again: ")
        partner = partners[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]

    for vid in all_vals:
        (title, *fields) = vid
        if not is_published(title,cursor_wp):
            description = fields[0]
            models = fields[1]
            tags = fields[2]
            date = fields[3]
            duration = fields[4]
            source_url = fields[5]
            thumbnail_url = fields[6]
            tracking_url = fields[7]
            wp_slug = fields[8] + '-video'
            partner_name = partner
            print("\nReview this post:\n")
            print(title)
            print(description)
            print(f"Duration: {duration}")
            print(f"Tags: {tags}")
            print(f"Models: {models}")
            print(f"Date: {date}")
            print(f"Source URL: {source_url}")
            if input('\nAdd post to WP? -> Y/N: ').lower() == ('y' or 'yes'):
                print('\n--> Making payload...')
                payload = make_payload(wp_slug, "draft", title,
                                       description, tracking_url, get_banner(banners), partner_name)

                print("--> Fetching thumbnail...")
                img_name = fetch_thumbnail('../thumbnails', wp_slug, thumbnail_url)

                print(f"--> Stored thumbnail {wp_slug}.jpg in cache folder ../thumbnails")
                print("--> Creating post on WordPress")
                push_post = wp_post_create(wp_base_url,['/posts'], payload)
                print(f'--> WordPress status code: {push_post}')
                print("--> Uploading thumbnail to WordPress Media...")
                img_attrs = {"alt_text": f"{title} - {description}. Watch it now on WhoresMen.com",
                            "caption": f"{title} - {description}. Watch it now on WhoresMen.com",
                            "description": f"{title} - {description}. Watch it now on WhoresMen.com"}
                upload_img = upload_thumbnail(wp_base_url,['/media'],
                                              f"../thumbnails/{wp_slug}.jpg", img_attrs)
                print(f'\n--> WordPress Media upload status code: {upload_img}')
                print("--> Check the post and copy all you need from above.")
                videos_uploaded += 1
                if input("\nNext post? -> Y/N: ").lower() == ('y' or 'yes'):
                    continue
                else:
                    print("Exiting...")
                    print(f'You have created {videos_uploaded} posts in this session!')
                    break
            elif input("\nReview another post? -> Y/N: ").lower() == ('y' or 'yes'):
                    continue
            else:
                print("Exiting...")
                print(f'You have uploaded {videos_uploaded} videos in this session!')
                break
        else:
            continue

banner_tuktuk_1 = "https://mongercash.com/view_banner.php?name=tktkp-728x90.gif&amp;filename=9936_name.gif&amp;type=gif&amp;download=1"
banner_tuktuk_2 = "https://mongercash.com/view_banner.php?name=tktkp-960x75.gif&amp;filename=9935_name.gif&amp;type=gif&amp;download=1"
banner_tuktuk_3 = "https://mongercash.com/view_banner.php?name=tktkp-850x80.jpg&amp;filename=9934_name.jpg&amp;type=jpg&amp;download=1"
banner_asd_1 = "https://mongercash.com/view_banner.php?name=asd638x60.gif&amp;filename=7654_name.gif&amp;type=gif&amp;download=1"
banner_asd_2 = "https://mongercash.com/view_banner.php?name=asd850x80.gif&amp;filename=7655_name.gif&amp;type=gif&amp;download=1"
banner_asd_3 = "https://mongercash.com/view_banner.php?name=asd-728x90.gif&amp;filename=9876_name.gif&amp;type=gif&amp;download=1"
banner_trike_1 = "https://mongercash.com/view_banner.php?name=tp-728x90.gif&amp;filename=9924_name.gif&amp;type=gif&amp;download=1"
banner_trike_2 = "https://mongercash.com/view_banner.php?name=tp-770x76.gif&amp;filename=9926_name.gif&amp;type=gif&amp;download=1"
banner_trike_3 = "https://mongercash.com/view_banner.php?name=trike%20patrol%20850x80.gif&amp;filename=7675_name.gif&amp;type=gif&amp;download=1"

banner_lst_asd = [banner_asd_1, banner_asd_2, banner_asd_3]
banner_lst_tktk = [banner_tuktuk_1, banner_tuktuk_2, banner_tuktuk_3]
banner_lst_trike = [banner_trike_1, banner_trike_2, banner_trike_3]
banner_lists = [banner_lst_asd, banner_lst_tktk, banner_lst_trike]

ideal_q = 'SELECT * FROM videos WHERE date>="2024" OR date>="2023"'

video_upload_pilot(fetch_videos_db(ideal_q, cur_dump), banner_lists, cur_wp)

