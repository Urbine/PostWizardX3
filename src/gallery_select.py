"""
This module is a photo gallery upload assistant.
Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__  = "yohamg@programmer.net"

# Std Library
import re
import shutil
import sqlite3
import time
import zipfile
from sqlite3 import OperationalError
from urllib3.exceptions import MaxRetryError, SSLError

# Third-party modules
import pyclip
from selenium import webdriver
from selenium.webdriver.common.by import By

# Local implementations
import content_select
import helpers
import wordpress_api

def fetch_zip(dwn_dir: str, remote_res: str, parent=False):
    download_dir = f'{helpers.cwd_or_parent_path(parent=parent)}/{dwn_dir}'
    options = webdriver.FirefoxOptions()
    options.set_preference("browser.download.folderList",2)
    options.set_preference("browser.download.manager.showWhenStarting",False)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk","application/octet-stream")
    options.enable_downloads = True
    webdrv = webdriver.Firefox(options=options)
    username = helpers.get_client_info('client_info.json',
                                       parent=True)['MongerCash']['username']

    password = helpers.get_client_info('client_info.json',
                                       parent=True)['MongerCash']['password']
    with webdrv as driver:
            # Go to URL
            print("--> Getting files from MongerCash")
            print("--> Authenticating...")
            driver.get(remote_res)

            # Find element by its ID
            username_box = driver.find_element(By.ID, 'user')
            pass_box = driver.find_element(By.ID, 'password')

            # Authenticate / Send keys
            username_box.send_keys(username)
            pass_box.send_keys(password)

            # Get Button Class
            button_login = driver.find_element(By.ID, 'head-login')

            # Click on the login Button
            button_login.click()
            print("--> Downloading...")
    print(f"--> Fetched file {helpers.search_files_by_ext('zip', parent=True, folder='tmp')[0]}")
    return None

def extract_zip(zip_path: str, extr_dir: str):
    get_zip = helpers.search_files_by_ext('zip', folder=zip_path)
    try:
        with zipfile.ZipFile(f'{zip_path}/{get_zip[0]}', 'r') as zipf:
            zipf.extractall(path=extr_dir)
        print(f"--> Extracted files from {get_zip[0]} in folder {extr_dir}")
        print(f"--> Tidying up...")
        shutil.rmtree(f'{extr_dir}/__MACOSX')
        helpers.if_exists_remove(f'{zip_path}/{get_zip[0]}')
    except IndexError or zipfile.BadZipfile:
        helpers.if_exists_remove(f'{zip_path}/{get_zip[0]}')
        return None

def make_gallery_payload(gal_title: str, iternum:int):
    img_payload = {"alt_text": f"Photo {iternum} from {gal_title}",
                   "caption": f"Photo {iternum} from {gal_title}",
                   "description": f"Photo {iternum} from {gal_title}"}
    return img_payload

def search_db_like(cur: sqlite3, table: str, field: str, query: str):
    qry = f'SELECT * FROM {table} WHERE {field} like "{query}%"'
    return cur.execute(qry).fetchall()


def get_from_db(cur: sqlite3, field: str, table: str):
    qry = f'SELECT {field} from {table}'
    try:
        return cur.execute(qry).fetchall()
    except OperationalError:
        return None

def get_model_set(db_cursor: sqlite3, table: str):
    models = get_from_db(db_cursor, 'models', table)
    new_lst = [model[0].strip(',') for model in models
               if model[0] is not None]
    return {elem for model in new_lst for elem in
            (model.split(',') if re.findall('[,+]', model) else [model])}

def make_photos_payload(status_wp: str, set_name: str, partner_name: str) -> dict:
    filter_words = {'on', 'in', 'at', '&', 'and'}
    no_partner_name = [word for word in set_name.split(" ")
                       if word not in set(partner_name.split(" "))]

    wp_pre_slug = "-".join([word.lower() for word in no_partner_name
               if re.match(r"[\w+]", word, flags=re.IGNORECASE) and word.lower() not in filter_words])
    # '-pics' tells Google the main content of the page.
    final_slug = f'{"-".join(partner_name.lower().split(" "))}-{wp_pre_slug}-pics'
    author = helpers.get_client_info('client_info',
                                     parent=True)['WordPress']['user_apps']['wordpress_api.py']['author']
    payload_post = {"slug": final_slug,
                    "status": f"{status_wp}",
                    "type": "photos",
                    "link": f"https://whoresmen.com/{final_slug}/",
                    "title": f"{set_name}",
                    "author": author,
                    "featured_media": 0}
    return payload_post


def gallery_upload_pilot(cur_prtner: sqlite3,
                         cur_wp_po: sqlite3,
                         cur_wp_ph: sqlite3,
                         partners: list[str],
                         db_name_prtner: str):
    partners = partners
    # Lists unique models whose videos where already published on the site.
    models_set = get_model_set(cur_wp_po, 'videos')
    all_galleries = get_from_db(cur_prtner, '*', 'sets')
    wp_base_url = "https://whoresmen.com/wp-json/wp/v2"
    # Start a new session with a clear thumbnail cache.
    # This is in case you run the program after a traceback or end execution early.
    content_select.clean_thumbnails_cache('thumbnails/', parent=True)
    # Prints out at the end of the uploading session.
    galleries_uploaded = 0
    print('\n')
    for num, partner in enumerate(partners, start=1):
        print(f"{num}. {partner}")
    try:
        partner_indx = input("\n\nSelect your partner: ")
        partner = partners[int(partner_indx) - 1]
    except IndexError:
        partner_indx = input("\n\nSelect your partner again: ")
        partner = partners[int(partner_indx) - 1]

    if re.match(db_name_prtner.split('_')[0],
                partner, flags=re.IGNORECASE):
        pass
    else:
        raise RuntimeError("Be careful! Partner and database must match. Try again...")

    # Relevancy algorithm.
    not_published_yet = []
    for elem in all_galleries:
        (title, *fields) = elem
        model_in_set = False
        title_split = title.split(" ")
        for word in title_split:
            if word not in models_set:
                continue
            else:
                model_in_set = True
                break

        if (not content_select.published('sets', title, cur_wp_ph)
            and model_in_set):
            not_published_yet.append(elem)
        else:
            continue
    # You can keep on getting sets until this variable is equal to one.
    total_elems = len(not_published_yet)
    print(f"\nThere are {total_elems} to be published...")
    for num, photo in enumerate(not_published_yet):
        (title, *fields) = photo
        # if not published(title, cursor_wp):
        title = title
        date = fields[0]
        download_url = fields[1]
        partner_name = partner
        print(f"\n{' Review this photo set ':*^30}\n")
        print(title)
        print(f"Date: {date}")
        print(f"Download URL: \n{download_url}")
        # Centralized control flow
        add_post = input('\nAdd set to WP? -> Y/N/ENTER to review next set: ').lower()
        if add_post == ('y' or 'yes'):
            add_post = True
        elif add_post == ('n' or 'no'):
            pyclip.detect_clipboard()
            pyclip.clear()
            print("\n--> Cleaning thumbnails cache now")
            content_select.clean_thumbnails_cache('thumbnails/', parent=True)
            print(f'You have created {galleries_uploaded} sets in this session!')
            break
        else:
            if num < total_elems - 1:
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("\nWe have reviewed all sets for this query.")
                print("Try a different SQL query or partner. I am ready when you are. ")
                print("\n--> Cleaning thumbnails cache now")
                content_select.clean_thumbnails_cache('thumbnails/', parent=True)
                print(f'You have created {galleries_uploaded} sets in this session!')
                break
        if add_post:
            print('\n--> Making payload...')
            payload = make_photos_payload('draft', title, partner_name)

            try:
                fetch_zip('/tmp', download_url, parent=True)
                extract_zip('../tmp', '../thumbnails')

                print("--> Creating set on WordPress")
                push_post = wordpress_api.wp_post_create(wp_base_url, ['/photos'], payload)
                print(f'--> WordPress status code: {push_post}')
                print("--> Adding image attributes on WordPress...")
                img_attrs = make_gallery_payload(title)
                thumbnails = helpers.search_files_by_ext('jpg', parent=True, folder='thumbnails')
                print(f"--> Uploading set with {len(thumbnails)} images to WordPress Media...")
                print("--> Adding image attributes on WordPress...")
                for number, image in enumerate(thumbnails, start=1):
                    img_attrs = make_gallery_payload(title, number)
                    status_code = wordpress_api.upload_thumbnail(wp_base_url, ['/media'],
                                              f"../thumbnails/{image}", img_attrs)
                    print(f"* Image {number} --> Status code: {status_code}")
                # Copy important information to the clipboard.
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(title)
                print("--> Check the set and paste your focus phrase on WP.")
                galleries_uploaded += 1
            except MaxRetryError or SSLError:
                pyclip.detect_clipboard()
                pyclip.clear()
                content_select.clean_thumbnails_cache('thumbnails/', parent=True)
                print("* There was a connection error while processing this set... *")
                if input("\nDo you want to continue? Y/N/ENTER to exit: ") == ('y' or 'yes'):
                    continue
                else:
                    print("\n--> Cleaning thumbnails cache now")
                    content_select.clean_thumbnails_cache('thumbnails/', parent=True)
                    print(f'You have created {galleries_uploaded} set in this session!')
                    break
            if num < total_elems - 1:
                next_post = input("\nNext set? -> Y/N/ENTER to review next set: ").lower()
                if next_post == ('y' or 'yes'):
                    # Clears clipboard after every video.
                    content_select.clean_thumbnails_cache('thumbnails/', parent=True)
                    pyclip.clear()
                    continue
                elif next_post == ('n' or 'no'):
                    # The terminating parts add this function to avoid tracebacks from pyclip
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    print("\n--> Cleaning thumbnails cache now")
                    content_select.clean_thumbnails_cache('thumbnails/', parent=True)
                    print(f'You have created {galleries_uploaded} sets in this session!')
                    break
                else:
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                # Since we ran out of elements the script will end after adding it to WP
                # So that it doesn't clear the clipboard automatically.
                print("\nWe have reviewed all sets for this query.")
                print("Try a different query and run me again.")
                print("\n--> Cleaning thumbnails cache now")
                content_select.clean_thumbnails_cache('thumbnails/', parent=True)
                print(f'You have created {galleries_uploaded} sets in this session!')
                print("Waiting for 60 secs to clear the clipboard before you're done with the last set...")
                time.sleep(60)
                pyclip.detect_clipboard()
                pyclip.clear()
                break
        else:
            pyclip.detect_clipboard()
            pyclip.clear()
            print("\nWe have reviewed all sets for this query.")
            print("Try a different SQL query or partner. I am ready when you are. ")
            print("\n--> Cleaning thumbnails cache now")
            content_select.clean_thumbnails_cache('thumbnails/', parent=True)
            print(f'You have created {galleries_uploaded} sets in this session!')
            break


print(' *** Select your partner photo set DB: ***')
db_name_partner = helpers.filename_select('db', parent = True)
db_partner = sqlite3.connect(f'{helpers.is_parent_dir_required(parent=True)}{db_name_partner}')
cur_partner = db_partner.cursor()

print('\n *** Select your WP All Posts DB: ***')
db_wp_1 = helpers.filename_select('db', parent = True)
db_wp_posts = sqlite3.connect(f'{helpers.is_parent_dir_required(parent=True)}{db_wp_1}')
cur_wp_posts = db_wp_posts.cursor()

print('\n *** Select your WP Photos DB: ***')
db_wp_2 = helpers.filename_select('db', parent = True)
db_wp_photos = sqlite3.connect(f'{helpers.is_parent_dir_required(parent=True)}{db_wp_2}')
cur_wp_photos = db_wp_photos.cursor()

partnerz = ['Asian Sex Diary', 'Tuktuk Patrol', 'Trike Patrol']

gallery_upload_pilot(cur_partner, cur_wp_posts, cur_wp_photos, partnerz, db_name_partner)


