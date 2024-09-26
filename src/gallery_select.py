# Modules in this project
import os
from operator import is_not
from pprint import pprint
from sqlite3 import OperationalError

import content_select
import helpers
import mcash_scrape
import wordpress_api

# Libraries
import requests
import time
import shutil
import sqlite3

from selenium import webdriver
from selenium.webdriver.common.by import By
from zipfile import ZipFile

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
    print("** DONE **")
    return None

def extract_zip(zip_path: str, extr_dir: str):
    get_zip = helpers.search_files_by_ext('zip', folder=zip_path)
    try:
        with ZipFile(f'{zip_path}/{get_zip[0]}', 'r') as zipf:
            zipf.extractall(path=extr_dir)
        shutil.rmtree(f'{extr_dir}/__MACOSX')
        helpers.if_exists_remove(f'{zip_path}/{get_zip[0]}')
    except IndexError:
        return None

def make_gallery_payload(gal_title: str):
    img_payload = {"alt_text": f"{gal_title}",
                   "caption": f"{gal_title}",
                   "description": f"{gal_title}"}
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

def get_model_set(db_cursor: sqlite3):
    models = get_from_db(cur_wp, 'models','videos')
    new_set = {model[0].strip(',') for model in models
               if model[0] is not None}
    return new_set

# db_name_phset = helpers.filename_select('db', parent = True)
# db_phset = sqlite3.connect(db_name_phset)
# cur_phset = db_phset.cursor()

def gallery_upload_pilot():

db_name_wp = helpers.filename_select('db', parent = True)
db_wp = sqlite3.connect(f'{helpers.is_parent_dir_required(parent=True)}{db_name_wp}')
cur_wp = db_wp.cursor()

def get_phtoto_sets():
    ...



zip_file = "http://mongercash.com/zip_tool/MzAwMTc2NC4xLjE2LjQ2LjAuMTQxNjguMC4wLjA/NATS_Content_LaizaandMayaOnAsianSexDiarySet1.zip"
# fetch_zip('/tmp', zip_file, parent=True)
# extract_zip('../tmp', '../thumbnails')


