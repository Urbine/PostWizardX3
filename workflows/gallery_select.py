"""
This module is a photo gallery upload assistant.
Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

# Std Library
import argparse
import os.path
import re
import shutil
import sqlite3
import tempfile
import time
import zipfile
from sqlite3 import OperationalError
from requests import ConnectionError

# Third-party modules
from rich.console import Console
import pyclip
from selenium import webdriver  # Imported for type annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# Local implementations
import core
from workflows.content_select import (
    hot_file_sync,
    filter_published,
    get_tag_ids,
    select_guard,
    published_json,
    content_select_db_match,
)
from core.helpers import clean_file_cache

from core import helpers, monger_cash_auth, gallery_select_conf, wp_auth

# Imported for typing purposes
from core.config_mgr import MongerCashAuth, WPAuth, GallerySelectConf
from integrations import wordpress_api, WPEndpoints


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

    :param dwn_dir: ``str``  Download directory. Typically, a temporary location.
    :param remote_res: ``str`` Archive download URL. It must be a direct link (automatic download)
    :param parent: ``bool``  ``True`` if your download dir is in MONGER_CASH_INFOa parent directory. Default ``False``
    :param gecko: ``bool`` ``True`` if you want to use Gecko (Firefox) webdriver instead of Chrome. Default ``False``
    :param headless: ``bool`` ``True`` if you want headless execution. Default ``False``.
    Note about ``headless`` mode: In this function, I have performed testing of a headless retrieval of the .zip
    archive, however, ``headless`` mode seems incompatible for this process. I am leaving the parameter to explore the
    execution in other platforms like Microsoft Windows as this function has been tested in Linux Fedora for the most
    part.
    :param m_cash_auth: ``MongerCashAuth`` object with authentication information to access MongerCash.
    :return: ``None``
    """
    webdrv: webdriver = helpers.get_webdriver(dwn_dir, gecko=gecko, headless=headless)
    username: str = m_cash_auth.username
    password: str = m_cash_auth.password
    with webdrv as driver:
        # Go to URL
        print("--> Getting files from MongerCash")
        print("--> Authenticating...")
        driver.get(remote_res)

        # Find element by its ID
        username_box: WebElement = driver.find_element(By.ID, "user")
        pass_box: WebElement = driver.find_element(By.ID, "password")

        # Authenticate / Send keys
        username_box.send_keys(username)
        pass_box.send_keys(password)

        # Get Button Class
        button_login: WebElement = driver.find_element(By.ID, "head-login")

        # Click on the login Button
        button_login.click()
        print("--> Downloading...")

        if not gecko:
            # Chrome exits after authenticating and before completing pending downloads.
            # On the other hand, Gecko does not need additional time.
            time.sleep(15)
        else:
            pass

    time.sleep(5)
    print(
        f"--> Fetched file {helpers.search_files_by_ext('zip', parent=parent, folder=os.path.relpath(dwn_dir))[0]}"
    )
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
        with zipfile.ZipFile(f"{os.path.abspath(zip_path)}/{get_zip[0]}", "r") as zipf:
            zipf.extractall(path=os.path.abspath(extr_dir))
        print(
            f"--> Extracted files from {get_zip[0]} in folder {os.path.relpath(extr_dir)}"
        )
        print(f"--> Tidying up...")
        try:
            # Some archives have a separate set of redundant files in that folder.
            # I don't want them.
            shutil.rmtree(f"{extr_dir}/__MACOSX")
        except FileNotFoundError:
            # Sometimes, this can blow up if that directory is not there.
            pass
        finally:
            # We always have to clean up.
            clean_file_cache(os.path.relpath(zip_path), ".zip")
    except (IndexError, zipfile.BadZipfile):
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
        # This happens when the table or field does not exist.
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
    wp_auth: WPAuth = wp_auth(),
) -> dict[str, str | int]:
    """Construct the photos payload that will be sent with all the parameters for the
    WordPress REST API request to create a ``photos`` post.
    In addition, this function makes the permalink that I will be using for the post.

    :param status_wp: ``str`` typically ``draft`` but it can be ``publish``, however, all posts need review.
    :param set_name: ``str`` photo gallery name.
    :param partner_name: ``str`` partner offer that I am promoting
    :param tags: ``list[int]`` tag IDs that will be sent to WordPress for classification and integration.
    :param reverse_slug: ``bool`` ``True`` if you want to reverse the permalink (slug) construction.
    :param wp_auth: ``WPAuth`` Object with the author information.
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
            f'{wp_pre_slug}-{"-".join(partner_name.lower().split(" "))}-pics'
        )
    else:
        final_slug: str = (
            f'{"-".join(partner_name.lower().split(" "))}-{wp_pre_slug}-pics'
        )

    # Added an author field to the client_info config file.
    author: int = int(wp_auth.author_admin)

    payload_post: dict[str, str | int] = {
        "slug": final_slug,
        "status": f"{status_wp}",
        "type": "photos",
        "link": f"{wp_auth.full_base_url}/{final_slug}/",
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
    :param wp_params: ``WPAuth``object with the base URL of the WP site.
    :return: ``None``
    """
    # Making sure folder is accessible.
    thumbnails: list[str] = helpers.search_files_by_ext(
        ext, folder=os.path.relpath(folder)
    )
    if len(thumbnails) == 0:
        # Assumes the thumbnails are contained in a directory
        # This could be caused by the archive extraction
        files: list[str] = helpers.search_files_by_ext(
            "jpg", recursive=True, folder=os.path.relpath(folder)
        )
        thumbnails: list[str] = ["/".join(path.split("/")[-2:]) for path in files]

    if len(thumbnails) != 0:
        print(f"--> Uploading set with {len(thumbnails)} images to WordPress Media...")
        print("--> Adding image attributes on WordPress...")
        thumbnails.sort()
    else:
        pass

    for number, image in enumerate(thumbnails, start=1):
        img_attrs: dict[str, str] = make_gallery_payload(title, number)
        status_code: int = wordpress_api.upload_thumbnail(
            wp_params.api_base_url,
            ["/media"],
            f"{os.path.abspath(folder)}/{image}",
            img_attrs,
        )
        # If upload is successful, the thumbnail is no longer useful.
        if status_code == (200 or 201):
            os.remove(f"{os.path.abspath(folder)}/{image}")
        else:
            pass
        print(f"* Image {number} | {image} --> Status code: {status_code}")
    try:
        # Check if I have paths instead of filenames
        if len(thumbnails[0].split("/")) > 1:
            # Get rid of the folder.
            shutil.rmtree(f"{os.path.abspath(folder)}/{thumbnails[0].split('/')[0]}")
        else:
            pass
    except (IndexError, AttributeError):
        # If slicing/splitting fails with IndexError or AttributeError, it does
        # not crash the program.
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
    # Relevancy algorithm.
    # Lists unique models whose videos where already published on the site.
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
    :param headless: ``bool`` ``True`` will enable the ``headless`` of the webdriver.
    For more information on this refer to the ``fetch_zip`` documentation on this module.
    :param parent: ``bool`` ``True`` if you are operating in the parent directory. Default ``False``
    :param wp_admin_auth: ``WPAuth`` object with information about you WP site.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :param gallery_sel_conf: ``GallerySelectConf`` object with configuration options for this module.
    :return: ``None``
    """
    # Configuring the required files
    console = Console()
    with console.status(
        "[bold green] Warming up... [blink]┌(◎_◎)┘[/blink] [/bold green]\n",
        spinner="aesthetic",
    ):
        hot_file_sync(bot_config=gallery_sel_conf)
    wp_photos_f = helpers.load_json_ctx(gallery_sel_conf.wp_json_photos)
    wp_posts_f = helpers.load_json_ctx(gallery_sel_conf.wp_json_posts)
    partners: list[str] = gallery_sel_conf.partners.split(",")
    db_conn, cur_partner, db_name_partner, partner_indx = content_select_db_match(
        partners, gallery_sel_conf.content_hint, parent=parent
    )
    all_galleries: list[tuple[str, ...]] = core.fetch_data_sql(
        gallery_sel_conf.sql_query, cur_partner
    )
    # Prints out at the end of the uploading session.
    galleries_uploaded: int = 0
    partner_: str = partners[partner_indx]
    # Gatekeeper function
    select_guard(db_name_partner, partner_)
    if relevancy_on:
        not_published_yet = filter_relevant(all_galleries, wp_posts_f, wp_photos_f)
    else:
        # In theory, this will work sometimes since I modify some of the
        # gallery names to reflect the queries we rank for on Google.
        not_published_yet = filter_published(all_galleries, wp_photos_f)
    # You can keep on getting sets until this variable is equal to one.
    total_elems: int = len(not_published_yet)
    console.print(
        f"There are {total_elems} sets to be published...",
        style="bold yellow",
        justify="center",
    )
    # Create temporary directories
    temp_dir = tempfile.TemporaryDirectory(dir=".")
    thumbnails_dir = tempfile.TemporaryDirectory(prefix="thumbs", dir=".")
    for num, photo in enumerate(not_published_yet):
        (title, *fields) = photo
        title: str = title
        date: str = fields[0]
        download_url: str = fields[1]
        partner_name: str = partner_
        console.print(f"\n{'Review this photo set ':*^30}\n", style="green")
        console.print(title, style="green")
        console.print(f"Date: {date}", style="green")
        console.print(f"Download URL: \n{download_url}", style="green")
        # Centralized control flow
        add_post: str | bool = console.input(
            "[bold yellow]\nAdd set to WP? -> Y/N/ENTER to review next set: [/bold yellow]"
        ).lower()
        if add_post == ("y" or "yes"):
            add_post: bool = True
        elif add_post == ("n" or "no"):
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                f"You have created {galleries_uploaded} sets in this session!",
                style="bold red",
            )
            break
        else:
            if num < total_elems - 1:
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
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

            try:
                fetch_zip(
                    temp_dir.name,
                    download_url,
                    parent=parent,
                    gecko=gecko,
                    headless=headless,
                )
                extract_zip(temp_dir.name, thumbnails_dir.name)

                console.print("--> Creating set on WordPress", style="bold green")
                upload_image_set("*", thumbnails_dir.name, title)

                push_post = wordpress_api.wp_post_create([wp_endpoints.photos], payload)
                console.print(
                    f"--> WordPress status code: {push_post}", style="bold green"
                )

                # Copy important information to the clipboard.
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                # This is the main tag for galleries
                pyclip.copy(partner_.lower())
                pyclip.copy(title)
                console.print(
                    "--> Check the set and paste your focus phrase on WP.",
                    style="bold magenta",
                )
                galleries_uploaded += 1
            except ConnectionError:
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this set... *",
                    style="bold red",
                )
                if console.input(
                    "[bold yellow]\nDo you want to continue? Y/N/ENTER to exit: [/bold yellow]"
                ) == ("y" or "yes"):
                    continue
                else:
                    console.print(
                        f"You have created {galleries_uploaded} set in this session!",
                        style="bold yellow",
                    )
                    temp_dir.cleanup()
                    thumbnails_dir.cleanup()
                    break
            if num < total_elems - 1:
                next_post = console.input(
                    "[bold yellow]\nNext set? -> Y/N/ENTER to review next set: [/bold yellow]"
                ).lower()
                if next_post == ("y" or "yes"):
                    # Clears clipboard after every video.
                    pyclip.clear()
                    with console.status(
                        "[bold magenta] Syncing and caching changes... [blink]ε= ᕕ(⎚‿⎚)ᕗ[blink][/bold magenta]\n",
                        spinner="aesthetic",
                    ):
                        hot_file_sync(bot_config=gallery_sel_conf)
                        not_published_yet = filter_published(all_galleries, wp_photos_f)
                        continue
                elif next_post == ("n" or "no"):
                    # The terminating parts add this function to avoid
                    # tracebacks from pyclip
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    console.print(
                        f"You have created {galleries_uploaded} sets in this session!",
                        style="bold yellow",
                    )
                    temp_dir.cleanup()
                    thumbnails_dir.cleanup()
                    break
                else:
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                # Since we ran out of elements the script will end after adding it to WP
                # So that it doesn't clear the clipboard automatically.
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
                console.print(
                    "Waiting for 60 secs to clear the clipboard before you're done with the last set...",
                    style="bold cyan",
                )
                time.sleep(60)
                pyclip.detect_clipboard()
                pyclip.clear()

                break
        else:
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
            break


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

    args = arg_parser.parse_args()

    gallery_upload_pilot(
        relevancy_on=args.relevancy,
        gecko=args.gecko,
        parent=args.parent,
    )
