"""
This module is a photo gallery upload assistant.
Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import logging
import os.path
import re
import shutil
import sqlite3
import tempfile
import time
import zipfile

from sqlite3 import OperationalError

# Third-party modules
import pyclip
from rich.console import Console
from selenium import webdriver  # Imported for type annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from requests.exceptions import ConnectionError, SSLError

# Local implementations
import core
from workflows.content_select import (
    hot_file_sync,
    filter_published,
    get_tag_ids,
    select_guard,
    published_json,
    content_select_db_match,
    wp_publish_checker,
    x_post_creator,
    telegram_send_message,
    logging_setup,
)

from core import helpers, monger_cash_auth, gallery_select_conf, wp_auth, x_auth

# Imported for typing purposes
from core.config_mgr import MongerCashAuth, WPAuth, GallerySelectConf
from integrations import wordpress_api, x_api, WPEndpoints, XEndpoints


def fetch_zip(
    dwn_dir: str,
    remote_res: str,
    parent: bool = False,
    gecko: bool = False,
    headless: bool = False,
    m_cash_auth: MongerCashAuth = monger_cash_auth(),
) -> None:
    """Fetch a .zip archive from the internet by following set of authentication and retrieval
    steps via automated execution of a browser instance (webdriver).

    **Note about "headless" mode: In this function, I have performed testing for a headless retrieval of the .zip
    archive, however, "headless" mode seems incompatible for this process. I am leaving the parameter to explore the
    execution in other platforms like Microsoft Windows as this function has been tested in Linux for the most
    part.**

    *Take into consideration that function fetch_zip() downloads files and Chrome does not usually wait
    until current downloads finish before closing running browser instances; fixes have been applied here to correct that behaviour.*

    *Headless mode does not show users why a certain iteration of the program failed and, due to the many factors, including but not limited to,
    internet connection speeds, the browser instance may require user collaboration to ensure the file has been
    downloaded and the former could then be closed either automatically or explicitly.*
    **For this reason, refrain from using headless mode with this module.**

    :param dwn_dir: ``str``  Download directory. Typically, a temporary location.
    :param remote_res: ``str`` Archive download URL. It must be a direct link (automatic download)
    :param parent: ``bool``  ``True`` if your download dir is in a parent directory. Default ``False``
    :param gecko: ``bool`` ``True`` if you want to use Gecko (Firefox) webdriver instead of Chrome. Default ``False``
    :param headless: ``bool`` ``True`` if you want headless execution. Default ``False``.
    :param m_cash_auth: ``MongerCashAuth`` object with authentication information to access MongerCash.
    :return: ``None``
    """
    webdrv: webdriver = helpers.get_webdriver(dwn_dir, headless=headless, gecko=gecko)

    webdrv_user_sel = "Gecko" if gecko else "Chrome"
    logging.info(
        f"User selected webdriver {webdrv_user_sel} -> Headless? {str(headless)}"
    )
    logging.info(f"Using {dwn_dir} for downloads as per function params")

    username: str = m_cash_auth.username
    password: str = m_cash_auth.password
    with webdrv as driver:
        # Go to URL
        print("--> Getting files from MongerCash")
        print("--> Authenticating...")
        driver.get(remote_res)
        driver.implicitly_wait(30)

        username_box: WebElement = driver.find_element(By.ID, "user")
        pass_box: WebElement = driver.find_element(By.ID, "password")

        username_box.send_keys(username)
        pass_box.send_keys(password)

        button_login: WebElement = driver.find_element(By.ID, "head-login")

        button_login.click()
        print("--> Downloading...")

        if not gecko:
            # Chrome exits after authenticating and before completing pending downloads.
            # On the other hand, Gecko does not need additional time.
            time.sleep(15)
        else:
            pass

    time.sleep(5)
    zip_set = helpers.search_files_by_ext(
        "zip", parent=parent, folder=os.path.relpath(dwn_dir)
    )[0]
    print(f"--> Fetched file {zip_set}")
    logging.info(f"--> Fetched archive file {zip_set}")
    return None


def extract_zip(zip_path: str, extr_dir: str):
    """Locate and extract a .zip archive in different locations.
    For example, you can locate the .zip archive from a temporary location and extract it
    somewhere else.

    :param zip_path: ``str`` where to locate the zip archive.
    :param extr_dir: ``str`` where to extract the contents of the archive
    :return: ``None``
    """
    get_zip: list[str] = helpers.search_files_by_ext(
        "zip", folder=os.path.relpath(zip_path)
    )
    try:
        with zipfile.ZipFile(
            zip_path := f"{os.path.abspath(zip_path)}/{get_zip[0]}", "r"
        ) as zipf:
            zipf.extractall(path=os.path.abspath(extr_dir))
        print(
            f"--> Extracted files from {get_zip[0]} in folder {os.path.relpath(extr_dir)}"
        )
        logging.info(f"Extracted {zip_path}")
        print(f"--> Tidying up...")
        try:
            # Some archives have a separate set of redundant files in that folder.
            # I don't want them.
            shutil.rmtree(junk_folder := f"{extr_dir}/__MACOSX")
            logging.info(f"Junk folder {junk_folder} detected and cleaned.")
        except (FileNotFoundError, NotImplementedError) as e:
            logging.warning(f"Caught {str(e)} - Handled")
            pass
        finally:
            logging.info(f"Cleaning remaining archive in {zip_path}")
            core.clean_file_cache(os.path.relpath(zip_path), ".zip")
    except (IndexError, zipfile.BadZipfile) as e:
        logging.error(f"Something went wrong with the archive extraction -> {str(e)}")
        return None


def make_gallery_payload(gal_title: str, iternum: int):
    """Make the image gallery payload that will be sent with the PUT/POST request
    to the WordPress media endpoint.

    :param gal_title: ``str`` Gallery title/name
    :param iternum: ``str`` short for "iteration number" and it allows for image numbering in the payload.
    :return: ``dict[str, str]``
    """
    img_payload: dict[str, str] = {
        "alt_text": f"Photo {iternum} from {gal_title}",
        "caption": f"Photo {iternum} from {gal_title}",
        "description": f"Photo {iternum} from {gal_title}",
    }
    return img_payload


def search_db_like(
    cur: sqlite3, table: str, field: str, query: str
) -> list[tuple[...]] | None:
    """Perform a ``SQL`` database search with the ``like``  parameter in a SQLite3 database.

    :param cur: ``sqlite3`` db cursor object
    :param table: ``str`` table in the db schema
    :param field: ``str`` field you want to match with ``like``
    :param query: ``str`` database query in ``SQL``
    :return: ``list[tuple[...]]`` or ``None``
    """
    qry: str = f'SELECT * FROM {table} WHERE {field} like "{query}%"'
    return cur.execute(qry).fetchall()


def get_from_db(cur: sqlite3, field: str, table: str) -> list[tuple[...]] | None:
    """Get a specific field or all ( ``*`` ) from a SQLite3 database.

    :param cur: ``sqlite3`` database cursor
    :param field: ``str`` field that you want to consult.
    :param table: ``str`` table in you db schema
    :return: ``list[tuple[...]]``  or ``None``
    """
    qry: str = f"SELECT {field} from {table}"
    try:
        return cur.execute(qry).fetchall()
    except OperationalError:
        return None


def get_model_set(db_cursor: sqlite3, table: str) -> set[str]:
    """Query the database and isolate the values of a single column to aggregate them
    in a set of str. In this case, the function isolates the ``models`` field from a
    table that the user specifies.

    :param db_cursor: ``sqlite3`` database cursor
    :param table: ``str`` table you want to consult.
    :return: ``set[str]``
    """
    models: list[tuple[str]] = get_from_db(db_cursor, "models", table)
    new_lst: list[str] = [
        model[0].strip(",") for model in models if model[0] is not None
    ]
    return {
        elem
        for model in new_lst
        for elem in (model.split(",") if re.findall(r",+", model) else [model])
    }


def make_photos_payload(
    status_wp: str,
    set_name: str,
    partner_name: str,
    tags: list[int],
    reverse_slug: bool = False,
    wpauth: WPAuth = wp_auth(),
) -> dict[str, str | int]:
    """Construct the photos payload that will be sent with all the parameters for the
    WordPress REST API request to create a ``photos`` post.
    In addition, this function makes the permalink that I will be using for the post.

    :param status_wp: ``str`` typically ``draft`` but it can be ``publish``, however, all posts need review.
    :param set_name: ``str`` photo gallery name.
    :param partner_name: ``str`` partner offer that I am promoting
    :param tags: ``list[int]`` tag IDs that will be sent to WordPress for classification and integration.
    :param reverse_slug: ``bool`` ``True`` if you want to reverse the permalink (slug) construction.
    :param wpauth: ``WPAuth`` Object with the author information.
    :return: ``dict[str, str | int]``
    """
    filter_words: set[str] = {"on", "in", "at", "&", "and"}

    no_partner_name: list[str] = list(
        filter(lambda w: w not in set(partner_name.split(" ")), set_name.split(" "))
    )

    # no_partner_name: list[str] = [
    #     word for word in set_name.split(" ") if word not in set(partner_name.split(" "))
    # ]

    wp_pre_slug: str = "-".join(
        [
            word.lower()
            for word in no_partner_name
            if re.match(r"\w+", word, flags=re.IGNORECASE)
            and word.lower() not in filter_words
        ]
    )

    if reverse_slug:
        # '-pics' tells Google the main content of the page.
        final_slug: str = (
            f"{wp_pre_slug}-{'-'.join(partner_name.lower().split(' '))}-pics"
        )
    else:
        final_slug: str = (
            f"{'-'.join(partner_name.lower().split(' '))}-{wp_pre_slug}-pics"
        )
    # Setting Env variable since the slug is needed outside this function.
    os.environ["SET_SLUG"] = final_slug

    author: int = int(wpauth.author_admin)

    payload_post: dict[str, str | int] = {
        "slug": final_slug,
        "status": f"{status_wp}",
        "type": "photos",
        "link": f"{wpauth.full_base_url}/{final_slug}/",
        "title": f"{set_name}",
        "author": author,
        "featured_media": 0,
        "photos_tag": tags,
    }
    return payload_post


def upload_image_set(
    ext: str, folder: str, title: str, wp_params: WPAuth = wp_auth()
) -> None:
    """Upload a set of images to the WordPress Media endpoint.

    :param ext: ``str`` image file extension to look for.
    :param folder:  ``str`` Your thumbnails folder, just the name is necessary.
    :param title: ``str`` gallery name
    :param wp_params: ``WPAuth`` object with the base URL of the WP site.
    :return: ``None``
    """
    thumbnails: list[str] = helpers.search_files_by_ext(
        ext, folder=os.path.relpath(folder)
    )
    if len(thumbnails) == 0:
        # Assumes the thumbnails are contained in a directory
        # This could be caused by the archive extraction
        logging.info("Thumbnails contained in directory - Running recursive search")
        files: list[str] = helpers.search_files_by_ext(
            "jpg", recursive=True, folder=os.path.relpath(folder)
        )
        thumbnails: list[str] = ["/".join(path.split("/")[-2:]) for path in files]

    if len(thumbnails) != 0:
        logging.info(
            prnt_imgs
            := f"--> Uploading set with {len(thumbnails)} images to WordPress Media..."
        )
        print(prnt_imgs)
        print("--> Adding image attributes on WordPress...")
        thumbnails.sort()
    else:
        pass

    # Prepare the image new name so that separators are replaced by hyphens.
    # E.g. this_is_a_cool_pic.jpg => this-is-a-cool-pic.jpg
    split_char = (
        lambda name: chars[0] if (chars := re.findall(r"[\W_]+", name)) else " "
    )
    new_name_img = lambda name: "-".join(name.split(split_char(name)))

    for number, image in enumerate(thumbnails, start=1):
        img_attrs: dict[str, str] = make_gallery_payload(title, number)
        new_img = os.path.abspath(f"{folder}/{new_name_img(image)}")
        os.renames(os.path.abspath(f"{folder}/{image}"), new_img)
        status_code: int = wordpress_api.upload_thumbnail(
            wp_params.api_base_url,
            ["/media"],
            f"{new_img}",
            img_attrs,
        )

        if status_code == (200 or 201):
            logging.info(f"Removing --> {new_img}")
            os.remove(new_img)
        else:
            pass
        logging.info(
            img_seq
            := f"* Image {number} | {new_name_img(image)} --> Status code: {status_code}"
        )
        print(img_seq)
    try:
        # Check if I have paths instead of filenames
        if len(thumbnails[0].split("/")) > 1:
            try:
                shutil.rmtree(
                    remove_dir
                    := f"{os.path.abspath(folder)}/{thumbnails[0].split('/')[0]}"
                )
                logging.info(f"Removed dir -> {remove_dir}")
            except NotImplementedError:
                logging.info(
                    "Incompatible platform - Directory cleaning relies on tempdir logic for now"
                )
                pass
        else:
            pass
    except (IndexError, AttributeError):
        pass
    finally:
        return None


def filter_relevant(
    all_galleries: list[tuple[str, ...]],
    wp_posts_f: list[dict[str, ...]],
    wp_photos_f: list[dict[str, ...]],
) -> list[tuple[str, ...]]:
    """Filter relevant galleries by using a simple algorithm to identify the models in
    each photo set and returning matches to the user. It is an experimental feature because it
    does not always work, specially when some image sets use the full name of the model and that
    makes it difficult for this simple algorithm to work.
    This could be reimplemented in a different (more efficient) manner, however,
    I do not believe it is a critical feature.

    :param all_galleries: ``list[tuple[str, ...]`` typically returned by a database query response.
    :param wp_posts_f: ``list[dict[str, ...]]`` WordPress Posts data structure
    :param wp_photos_f:  ``list[dict[str, ...]]`` WordPress Photos data structure
    :return: ``list[tuple[str, ...]]`` Image sets related to models present in the WP site.
    """
    models_set: set[str] = set(
        wordpress_api.map_wp_class_id(wp_posts_f, "pornstars", "pornstars").keys()
    )
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

        if not published_json(title, wp_photos_f) and model_in_set:
            not_published_yet.append(elem)
        else:
            continue
    return not_published_yet


def gallery_upload_pilot(
    relevancy_on: bool = False,
    gecko: bool = False,
    headless: bool = False,
    parent: bool = False,
    wp_admin_auth: WPAuth = wp_auth(),
    wp_endpoints: WPEndpoints = WPEndpoints,
    gallery_sel_conf: GallerySelectConf = gallery_select_conf(),
) -> None:
    """Control the entire execution of the gallery upload process.
    This ``gallery_upload_pilot`` function is a modification of ``video_upload_pilot``
    in the ``workflows.content_select`` module in the same package.
    It includes modifications that are necessary to deal with extra steps and automation:

    Note: the function calls specialized units that have been implemented for each responsibility,
    ``gallery_upload_pilot`` is just a job control that puts it all together, just like other like it in this package.

    1. Fetch a ``.zip`` archive with a download link provided by the database
    2. Locate, extract that .zip file into a temporary location, and dispose of the archive file.
    3. Upload a set of images to WordPress with appropriate metadata and clean successful uploads from the disk simultaneously.
    4. Build the payloads to create a post in WordPress once the image set has been successfully uploaded.

    If you want to know more about the flow control involved in this function, refer to the documentation
    for ``video_upload_pilot`` in the ``workflows.content_select`` module as there is a more detailed
    breakdown of the process.

    :param relevancy_on: ``bool`` ``True`` to enable the relevancy algorithm (experimental). Default ``False``
    :param gecko: ``bool`` ``True`` if you want to use the Gecko webdriver. Default ``False`` (Chrome)
    :param headless: ``bool`` ``True`` will enable the ``headless`` of the webdriver. For more information on this refer to the ``fetch_zip`` documentation on this module.
    :param parent: ``bool`` ``True`` if you are operating in the parent directory. Default ``False``
    :param wp_admin_auth: ``WPAuth`` object with information about you WP site.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :param gallery_sel_conf: ``GallerySelectConf`` object with configuration options for this module.
    :return: ``None``
    """
    time_start = time.time()
    logging_setup(gallery_sel_conf, __file__)
    logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}")

    console = Console()
    os.system("clear")
    with console.status(
        "[bold green] Warming up... [blink]┌(◎_◎)┘[/blink] [/bold green]\n",
        spinner="aesthetic",
    ):
        hot_file_sync(bot_config=gallery_sel_conf)
        x_api.refresh_flow(x_auth(), XEndpoints())

    wp_photos_f = helpers.load_json_ctx(gallery_sel_conf.wp_json_photos)
    logging.info(f"Reading WordPress Posts cache: {gallery_sel_conf.wp_json_posts}")

    wp_posts_f = helpers.load_json_ctx(gallery_sel_conf.wp_json_posts)
    logging.info(f"Reading WordPress Photos cache: {gallery_sel_conf.wp_json_posts}")

    partners: list[str] = gallery_sel_conf.partners.split(",")
    logging.info(f"Loading partners variable: {partners}")

    db_conn, cur_partner, db_name_partner, partner_indx = content_select_db_match(
        partners, gallery_sel_conf.content_hint, parent=parent
    )
    logging.info(
        f"Matched {db_name_partner} for {partners[partner_indx]} index {partner_indx}"
    )
    all_galleries: list[tuple[str, ...]] = core.fetch_data_sql(
        gallery_sel_conf.sql_query, cur_partner
    )
    logging.info(f"{len(all_galleries)} elements found in database {db_name_partner}")
    # Prints out at the end of the uploading session.
    galleries_uploaded: int = 0

    partner_: str = partners[partner_indx]
    # Gatekeeper function
    select_guard(db_name_partner, partner_)
    logging.info("Select guard cleared...")

    if relevancy_on:
        logging.info("Relevancy algorithm on...")
        not_published_yet = filter_relevant(all_galleries, wp_posts_f, wp_photos_f)
    else:
        # In theory, this will work "sometimes" since I modify some of the
        # gallery names to reflect the queries we rank for on Google.
        # I don't use it as it is still experimental.
        logging.info("Relevancy algorithm off...")
        not_published_yet = filter_published(all_galleries, wp_photos_f)

    # You can keep on getting sets until this variable is equal to one.
    total_elems: int = len(not_published_yet)
    logging.info(f"Detected {total_elems} to be published")
    os.system("clear")
    # Environment variable set in logging_setup() - content_select.py
    console.print(
        f"Session ID: {os.environ.get('SESSION_ID')}",
        style="bold yellow",
        justify="left",
    )
    console.print(
        f"There are {total_elems} sets to be published...",
        style="bold red",
        justify="center",
    )
    time.sleep(2)
    temp_dir = tempfile.TemporaryDirectory(dir=".")
    logging.info(f"Created {temp_dir.name} for temporary file download & extraction")
    thumbnails_dir = tempfile.TemporaryDirectory(prefix="thumbs", dir=".")
    logging.info(f"Created {thumbnails_dir.name} for thumbnail temporary storage")

    for num, photo in enumerate(not_published_yet):
        (title, *fields) = photo
        logging.info(f"Displaying on iteration {num} data: {photo}")
        title: str = title
        date: str = fields[0]
        download_url: str = fields[1]
        partner_name: str = partner_
        os.system("clear")
        console.print(
            f"Session ID: {os.environ.get('SESSION_ID')}",
            style="bold yellow",
            justify="left",
        )
        console.print(f"\n{'Review this photo set ':*^30}\n", style="green")
        console.print(title, style="green")
        console.print(f"Date: {date}", style="green")
        console.print(f"Download URL: \n{download_url}", style="green")
        add_post: str | bool = console.input(
            "[bold yellow]\nAdd set to WP? -> Y/N/ENTER to review next set: [/bold yellow]\n"
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {num} for processing")
            add_post: bool = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further interaction with the bot")
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                f"You have created {galleries_uploaded} sets in this session!",
                style="bold red",
            )
            temp_dir.cleanup()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            logging.info(
                f"User created {galleries_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
            )
            logging.info("Cleaning clipboard and temporary directories. Quitting...")
            logging.shutdown()
            break
        else:
            if num < total_elems - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "\nWe have reviewed all sets for this query.", style="bold red"
                )
                console.print(
                    "Try a different SQL query or partner. I am ready when you are. ",
                    style="bold red",
                )
                console.print(
                    f"You have created {galleries_uploaded} sets in this session!",
                    style="bold red",
                )
                temp_dir.cleanup()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                logging.info(
                    f"User created {galleries_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                )
                logging.info(
                    "Cleaning clipboard and temporary directories. Quitting..."
                )
                logging.shutdown()
                break
        if add_post:
            console.print("\n--> Making payload...", style="bold green")
            tag_list: list[int] = get_tag_ids(wp_photos_f, [partner_name], "photos")
            payload: dict[str, str | int] = make_photos_payload(
                wp_admin_auth.default_status,
                title,
                partner_name,
                tag_list,
                reverse_slug=True,
            )

            logging.info(f"Generated payload: {payload}")

            try:
                fetch_zip(
                    temp_dir.name,
                    download_url,
                    parent=parent,
                    gecko=gecko,
                    headless=headless,
                )
                extract_zip(temp_dir.name, thumbnails_dir.name)
                upload_image_set("*", thumbnails_dir.name, title)

                logging.info(f"WP Slug - Selected: {os.environ.get('SET_SLUG')}")

                console.print("--> Creating set on WordPress", style="bold green")
                push_post = wordpress_api.wp_post_create([wp_endpoints.photos], payload)
                logging.info(wp_push_msg := f"WordPress post push status: {push_post}")
                console.print(wp_push_msg, style="bold green")

                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                # This is the main tag for galleries
                pyclip.copy(partner_.lower())
                pyclip.copy(title)
                console.print(
                    "--> Check the set and paste your focus phrase on WP.",
                    style="bold magenta",
                )
                if (
                    gallery_sel_conf.x_posting_enabled
                    or gallery_sel_conf.telegram_posting_enabled
                ):
                    status_msg = "Checking WP status and preparing for social sharing."
                    with console.status(
                        f"[bold green]{status_msg} [blink]ε= ᕕ(⎚‿⎚)ᕗ[blink] [/bold green]\n",
                        spinner="earth",
                    ):
                        is_published = wp_publish_checker(
                            os.environ.get("SET_SLUG"), gallery_sel_conf
                        )
                    if is_published:
                        if gallery_sel_conf.x_posting_enabled:
                            logging.info("X Posting - Enabled in workflows config")
                            if gallery_sel_conf.x_posting_auto:
                                logging.info("X Posting Automatic detected in config")
                                # Environment "LATEST_POST" variable assigned in wp_publish_checker()
                                x_post_create = x_post_creator(
                                    title, os.environ.get("LATEST_POST")
                                )
                            else:
                                post_text = console.input(
                                    "[bold yellow]Enter your additional X post text here or press enter to use default configs: [bold yellow]\n"
                                )
                                logging.info(
                                    f"User entered custom post text: {post_text}"
                                )
                                x_post_create = x_post_creator(
                                    title,
                                    os.environ.get("LATEST_POST"),
                                    post_text=post_text,
                                )

                                # Copy custom post text for the following prompt
                                pyclip.detect_clipboard()
                                pyclip.copy(post_text)

                            if x_post_create == 201:
                                console.print(
                                    "--> Post has been published on WP and shared on X.\n",
                                    style="bold yellow",
                                )
                            else:
                                console.print(
                                    f"--> There was an error while trying to share on X.\n Status: {x_post_create}",
                                    style="bold red",
                                )
                            logging.info(f"X post status code: {x_post_create}")

                        if gallery_sel_conf.telegram_posting_enabled:
                            logging.info(
                                "Telegram Posting - Enabled in workflows config"
                            )
                            if gallery_sel_conf.telegram_posting_auto:
                                logging.info(
                                    "Telegram Posting Automatic detected in config"
                                )
                                telegram_msg = telegram_send_message(
                                    title,
                                    os.environ.get("LATEST_POST"),
                                    gallery_sel_conf,
                                )
                            else:
                                post_text = console.input(
                                    "[bold yellow]Enter your additional Telegram message here or press enter to use default configs: [bold yellow]\n"
                                )
                                telegram_msg = telegram_send_message(
                                    title,
                                    os.environ.get("LATEST_POST"),
                                    gallery_sel_conf,
                                    msg_text=post_text,
                                )

                            if telegram_msg == 200:
                                console.print(
                                    # Env variable assigned in botfather_telegram.send_message()
                                    f"--> Message sent to Telegram {os.environ.get('T_CHAT_ID')}",
                                    style="bold yellow",
                                )
                            else:
                                console.print(
                                    f"--> There was an error while trying to communicate with Telegram.\n Status: {telegram_msg}",
                                    style="bold red",
                                )
                            logging.info(
                                f"Telegram message status code: {telegram_msg}"
                            )
                else:
                    pass
                galleries_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {str(e)} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this set... *",
                    style="bold red",
                )
                if console.input(
                    "[bold yellow]\nDo you want to continue? Y/ENTER to exit: [/bold yellow]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {str(e)}")
                    continue
                else:
                    logging.info(f"User declined after catching {str(e)}")
                    console.print(
                        f"You have created {galleries_uploaded} set in this session!",
                        style="bold yellow",
                    )
                    temp_dir.cleanup()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    logging.info(
                        f"User created {galleries_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                    )
                    logging.info(
                        "Cleaning clipboard and temporary directories. Quitting..."
                    )
                    logging.shutdown()
                    break
            if num < total_elems - 1:
                next_post = console.input(
                    "[bold yellow]\nNext set? -> N/ENTER to review next set: [/bold yellow]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    console.print(
                        f"You have created {galleries_uploaded} sets in this session!",
                        style="bold yellow",
                    )
                    temp_dir.cleanup()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    logging.info(
                        f"User created {galleries_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                    )
                    logging.info(
                        "Cleaning clipboard and temporary directories. Quitting..."
                    )
                    logging.shutdown()
                    break
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                console.print(
                    "\nWe have reviewed all sets for this query.", style="bold red"
                )
                console.print(
                    "Try a different query and run me again.", style="bold red"
                )
                console.print(
                    f"You have created {galleries_uploaded} sets in this session!",
                    style="bold yellow",
                )
                temp_dir.cleanup()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                logging.info(
                    f"User created {galleries_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                )
                logging.info(
                    "Cleaning clipboard and temporary directories. Quitting..."
                )
                logging.shutdown()
        else:
            logging.info(f"List exhausted. State: num={num} total_elems={total_elems}")
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                "\nWe have reviewed all sets for this query.", style="bold red"
            )
            console.print(
                "Try a different SQL query or partner. I am ready when you are. ",
                style="bold red",
            )
            console.print(
                f"You have created {galleries_uploaded} sets in this session!",
                style="bold yellow",
            )
            temp_dir.cleanup()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            logging.info(
                f"User created {galleries_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
            )
            logging.info("Cleaning clipboard and temporary directories. Quitting...")
            logging.shutdown()
            break


def main(*args, **kwargs):
    try:
        gallery_upload_pilot(*args, **kwargs)
    except KeyboardInterrupt:
        logging.critical(f"KeyboardInterrupt exception detected")
        logging.info("Cleaning clipboard and temporary directories. Quitting...")
        print("Goodbye! ಠ‿↼")
        pyclip.detect_clipboard()
        pyclip.clear()
        logging.shutdown()
        # When quit is called, temp dirs will be automatically cleaned.
        quit()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Gallery Select Assistant - Behaviour Tweaks"
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        default=False,
        help="""Define if database and file search happens in the parent directory.
                                            This argument also affects:
                                            1. Thumbnail search
                                            2. HotSync caching
                                            3. Cache cleaning
                                            The default is set to false, so if you execute this file as a module,
                                            you may not want to enable it because this is treated as a package.
                                            If you are experiencing issues with the location of your thumbnails and relative
                                            references, this is a good place to start.""",
    )

    arg_parser.add_argument(
        "--gecko",
        action="store_true",
        help="Use the gecko webdriver for the browser automation steps.",
    )

    arg_parser.add_argument(
        "--relevancy",
        action="store_true",
        help="Activate relevancy algorithm (experimental)",
    )

    arg_parser.add_argument(
        "--headless",
        action="store_true",
        help="Enable headless webdriver execution. Compatibility is experimental with this module.",
    )

    args_cli = arg_parser.parse_args()

    main(
        relevancy_on=args_cli.relevancy,
        gecko=args_cli.gecko,
        parent=args_cli.parent,
    )
