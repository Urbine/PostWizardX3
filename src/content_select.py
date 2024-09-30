"""

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

import os
import pyclip
import random
import re
import requests
import sqlite3
import time

from urllib3.exceptions import MaxRetryError, SSLError

# Local implementations
import helpers
import wordpress_api


# Videos table - db_connection_dump
# CREATE TABLE
#     videos(
#     title,
#     description,
#     model,
#     tags,
#     date,
#     duration,
#     source_url,
#     thumbnail_url,
#     tracking_url,
#     wp_slug
#     )

# sample_query = """
# SELECT
# title,
# description,
# tags,
# duration,
# source_url,
# thumbnail_url,
# tracking_url,
# wp_slug FROM videos ORDER BY date DESC
# """

def fetch_videos_db(sql_query: str, db_cursor):
    db_cursor.execute(sql_query)
    return db_cursor.fetchall()


def published(table: str, title: str, db_cursor) -> bool:
    search_vids = f'SELECT * FROM {table} WHERE title="{title}"'
    if not db_cursor.execute(search_vids).fetchall():
        return False
    else:
        return True


def get_banner(banner_lst: list[str]):
    return random.choice(banner_lst)


def get_model_id(wp_posts_f: list[dict], model: str):
    model_tracking = wordpress_api.map_class_list_id(wp_posts_f,
                                                     'pornstars',
                                                     'pornstars')
    if model in model_tracking.keys():
        return model_tracking[model]
    else:
        return None


def get_tag_ids(wp_posts_f: list[dict], tag_lst: list[str]) -> list[int]:
    tag_tracking = wordpress_api.tag_id_merger_dict(wp_posts_f)
    # I am using a set to enforce uniqueness.
    # Also, I want to match tags that could contain
    # uppercase letters in the dict from WordPress.
    # I will match them with Regex here to avoid touching the datasource.
    matched_keys = [wptag for wptag in tag_tracking.keys()
                    for tag in tag_lst if re.fullmatch(tag, wptag, flags=re.IGNORECASE)]
    # The function will return a reversed list of matches.
    return list({tag_tracking[tag] for tag in matched_keys})


def get_model_ids(wp_posts_f: list[dict], model_lst: list[str]):
    model_tracking = wordpress_api.map_class_list_id(wp_posts_f,'pornstars','pornstars')
    return list({model_tracking[model.title()] for model in model_lst
                 if model.title() in model_tracking.keys()})


def get_dict_key(tag_dic: dict, tag_id: int):
    for tname, tid in tag_dic.items():
        if tag_id == tid:
            return tname
    return None


def identify_missing(wp_data_dic: dict,
                     data_lst: list[str],
                     data_ids: list[int],
                     ignore_case: bool = False):
    # Assumes we have x items and x ids
    if len(data_lst) == len(data_ids):
        return None
    else:
        # If we have less or more items on either side, we've got a problem.
        not_found = []
        for item in data_lst:
            if ignore_case:
                item = item.lower()
                tags = [tag.lower() for tag in wp_data_dic.keys()]
                if item not in tags:
                    not_found.append(item)
            else:
                try:
                    wp_data_dic[item]
                except KeyError:
                    not_found.append(item)
        return not_found


def fetch_thumbnail(folder: str, slug: str, remote_res: str, parent: bool = False):
    thumbnail_dir = f'{helpers.is_parent_dir_required(parent=parent)}{folder}'
    remote_data = requests.get(remote_res)
    with open(f"{thumbnail_dir}/{slug}.jpg", 'wb') as img:
        img.write(remote_data.content)
    return remote_data.status_code


def clean_file_cache(cache_folder: str, file_ext: str, parent=False):
    cache_files = helpers.search_files_by_ext(file_ext,
                                              parent=parent,
                                              folder=cache_folder)
    go_to_folder = helpers.is_parent_dir_required(parent=parent) + cache_folder
    os.chdir(go_to_folder)
    if len(cache_files) > 1:
        for file in cache_files:
            os.remove(file)
    else:
        return None


def make_payload(vid_slug,
                 status_wp: str,
                 vid_name: str,
                 vid_description: str,
                 banner_tracking_url: str,
                 banner_img: str,
                 partner_name: str,
                 tag_int_lst: list[int],
                 model_int_lst: list[int]) -> dict:
    author = helpers.get_client_info('client_info',
                                     parent=True)['WordPress']['user_apps']['wordpress_api.py']['author']
    payload_post = {"slug": f"{vid_slug}",
                    "status": f"{status_wp}",
                    "type": "post",
                    "link": f"https://whoresmen.com/{vid_slug}/",
                    "title": f"{vid_name}",
                    "content": f"<p>{vid_description}</p><figure class=\"wp-block-image size-large\"><a href=\"{banner_tracking_url}\"><img decoding=\"async\" src=\"{banner_img}\" alt=\"{vid_name} | {partner_name} on WhoresMen.com\"/></a></figure>",
                    "excerpt": f"<p>{vid_description}</p>\n",
                    "author": author,
                    "featured_media": 0,
                    "tags": tag_int_lst,
                    "pornstars": model_int_lst}
    return payload_post


def make_img_payload(vid_title: str, vid_description: str):
    img_payload = {"alt_text": f"{vid_title} on WhoresMen.com - {vid_description}. Watch now!",
                   "caption": f"{vid_title} on WhoresMen.com - {vid_description}. Watch now!",
                   "description": f"{vid_title} on WhoresMen.com - {vid_description}. Watch now!"}
    return img_payload


def video_upload_pilot(videos: list[tuple],
                       partners: list[str],
                       banner_lsts: list[list[str]],
                       partner_db_name: str,
                       cursor_wp: sqlite3,
                       wp_posts_f: list[dict]):
    all_vals = videos
    wp_base_url = "https://whoresmen.com/wp-json/wp/v2"
    # Start a new session with a clear thumbnail cache.
    # This is in case you run the program after a traceback or end execution early.
    clean_file_cache('thumbnails/', '.jpg', parent=True)
    # Prints out at the end of the uploading session.
    videos_uploaded = 0
    print('\n')
    for num, partner in enumerate(partners, start=1):
        print(f"{num}. {partner}")
    try:
        partner_indx = input("\n\nSelect your partner: ")
        partner = partners[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]
    except IndexError:
        partner_indx = input("\n\nSelect your partner again: ")
        partner = partners[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]

    if re.match(partner_db_name.split('_')[0],
                partner, flags=re.IGNORECASE):
        pass
    else:
        raise RuntimeError("Be careful! Partner and database must match. Try again...")

    # This loop gets the items I am interested in.
    not_published_yet = []
    for elem in all_vals:
        (title, *fields) = elem
        if not published('videos', title, cursor_wp):
            not_published_yet.append(elem)
        else:
            continue
    # You can keep on getting posts until this variable is equal to one.
    total_elems = len(not_published_yet)
    print(f"\nThere are {total_elems} videos to be published...")
    for num, vid in enumerate(not_published_yet):
        (title, *fields) = vid
        # if not published(title, cursor_wp):
        description = fields[0]
        models = fields[1]
        tags = fields[2]
        date = fields[3]
        duration = fields[4]
        source_url = fields[5]
        thumbnail_url = fields[6]
        tracking_url = fields[7]
        # Tells Google the main content of the page.
        wp_slug = fields[8] + '-video'
        partner_name = partner
        print(f"\n{' Review this post ':*^30}\n")
        print(title)
        print(description)
        print(f"Duration: {duration}")
        print(f"Tags: {tags}")
        print(f"Models: {models}")
        print(f"Date: {date}")
        print(f"Thumbnail URL: {thumbnail_url}")
        print(f"Source URL: {source_url}")
        # Centralized control flow
        add_post = input('\nAdd post to WP? -> Y/N/ENTER to review next post: ').lower()
        if add_post == ('y' or 'yes'):
            add_post = True
        elif add_post == ('n' or 'no'):
            pyclip.detect_clipboard()
            pyclip.clear()
            print("\n--> Cleaning thumbnails cache now")
            clean_file_cache('thumbnails', '.jpg', parent=True)
            print(f'You have created {videos_uploaded} posts in this session!')
            break
        else:
            if num < total_elems - 1:
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("\nWe have reviewed all posts for this query.")
                print("Try a different SQL query or partner. I am ready when you are. ")
                print("\n--> Cleaning thumbnails cache now")
                clean_file_cache('thumbnails', '.jpg', parent=True)
                print(f'You have created {videos_uploaded} posts in this session!')
                break
        if add_post:
            print('\n--> Making payload...')
            tag_prep = tags.split(',')
            tag_prep.append(partner.lower())
            tag_ints = get_tag_ids(wp_posts_f, tag_prep)
            all_tags_wp = wordpress_api.tag_id_merger_dict(wp_posts_f)
            tag_check = identify_missing(all_tags_wp, tag_prep,
                                         tag_ints, ignore_case=True)
            if tag_check is None:
                # All tags have been found and mapped to their IDs.
                pass
            else:
                # You've hit a snag.
                for tag in tag_check:
                    print(f'ATTENTION --> Tag: {tag} not on WordPress.')
                    print('--> Copying missing tag to your system clipboard.')
                    print("Paste it into the tags field as soon as possible...")
                    pyclip.detect_clipboard()
                    pyclip.copy(tag)

            model_prep = models.split(',')
            # The would-be 'models_ints'
            calling_models = get_model_ids(wp_posts_f, model_prep)
            all_models_wp = wordpress_api.map_class_list_id(wp_posts_f,
                                                            'pornstars', 'pornstars')
            new_models = identify_missing(all_models_wp, model_prep, calling_models)

            if new_models is None:
                # All model have been found and located.
                pass
            else:
                # There's a new girl in town.
                for girl in new_models:
                    print(f'ATTENTION --> Model: {girl} not on WordPress.')
                    print('--> Copying missing model name to your system clipboard.')
                    print("If you add this one, you won't see me here again. <3")
                    pyclip.detect_clipboard()
                    pyclip.copy(girl)

            payload = make_payload(wp_slug,
                                   "draft",
                                   title,
                                   description,
                                   tracking_url,
                                   get_banner(banners),
                                   partner_name,
                                   tag_ints,
                                   calling_models)

            print("--> Fetching thumbnail...")
            try:
                fetch_thumbnail('thumbnails', wp_slug, thumbnail_url, parent=True)
                print(f"--> Stored thumbnail {wp_slug}.jpg in cache folder ../thumbnails")
                print("--> Creating post on WordPress")
                push_post = wordpress_api.wp_post_create(wp_base_url, ['/posts'], payload)
                print(f'--> WordPress status code: {push_post}')
                print("--> Uploading thumbnail to WordPress Media...")
                print("--> Adding image attributes on WordPress...")
                img_attrs = make_img_payload(title, description)
                upload_img = wordpress_api.upload_thumbnail(wp_base_url, ['/media'],
                                                            f"../thumbnails/{wp_slug}.jpg", img_attrs)
                print(f'\n--> WordPress Media upload status code: {upload_img}')
                # Copy important information to the clipboard.
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(source_url)
                pyclip.copy(title)
                print("--> Check the post and paste all you need from your clipboard.")
                videos_uploaded += 1
            except MaxRetryError or SSLError:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("* There was a connection error while processing this post... *")
                if input("\nDo you want to continue? Y/N/ENTER to exit: ") == ('y' or 'yes'):
                    continue
                else:
                    print("\n--> Cleaning thumbnails cache now")
                    clean_file_cache('thumbnails', '.jpg', parent=True)
                    print(f'You have created {videos_uploaded} posts in this session!')
                    break
            if num < total_elems - 1:
                next_post = input("\nNext post? -> Y/N/ENTER to review next post: ").lower()
                if next_post == ('y' or 'yes'):
                    # Clears clipboard after every video.
                    pyclip.clear()
                    continue
                elif next_post == ('n' or 'no'):
                    # The terminating parts add this function to avoid tracebacks from pyclip
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    print("\n--> Cleaning thumbnails cache now")
                    clean_file_cache('thumbnails', '.jpg', parent=True)
                    print(f'You have created {videos_uploaded} posts in this session!')
                    break
                else:
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                # Since we ran out of elements the script will end after adding it to WP
                # So that it doesn't clear the clipboard automatically.
                print("\nWe have reviewed all posts for this query.")
                print("Try a different query and run me again.")
                print("\n--> Cleaning thumbnails cache now")
                clean_file_cache('thumbnails', 'jpg', parent=True)
                print(f'You have created {videos_uploaded} posts in this session!')
                print("Waiting for 60 secs to clear the clipboard before you're done with the last post...")
                time.sleep(60)
                pyclip.detect_clipboard()
                pyclip.clear()
                break
        else:
            pyclip.detect_clipboard()
            pyclip.clear()
            print("\nWe have reviewed all posts for this query.")
            print("Try a different SQL query or partner. I am ready when you are. ")
            print("\n--> Cleaning thumbnails cache now")
            clean_file_cache('thumbnails', '.jpg', parent=True)
            print(f'You have created {videos_uploaded} posts in this session!')
            break


if __name__ == '__main__':
    print("Choose your Partner and WP databases:")
    parent_wd = helpers.is_parent_dir_required(parent=True)
    db_dump_name = helpers.filename_select('db', parent=True)
    db_connection_dump = sqlite3.connect(f'{parent_wd}{db_dump_name}')
    cur_dump = db_connection_dump.cursor()

    db_wp_name = helpers.filename_select('db', parent=True)
    db_connection_wp = sqlite3.connect(f'{parent_wd}{db_wp_name}')
    cur_wp = db_connection_wp.cursor()

    client_info = helpers.get_client_info('client_info', parent=True)

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

    # Alternative query: SELECT * FROM videos WHERE date>="2024" OR date>="2023"
    ideal_q = 'SELECT * FROM videos WHERE date>="2023" AND duration!="trailer"'

    partnerz = ["Asian Sex Diary", "TukTuk Patrol", "Trike Patrol"]

    imported_json = helpers.load_json_ctx("wp_posts", parent=True)

    video_upload_pilot(fetch_videos_db(ideal_q, cur_dump),
                       partnerz, banner_lists, db_dump_name, cur_wp, imported_json)
