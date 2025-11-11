"""
Workflows File Handling module

This module is responsible for handling file operations, such as fetching thumbnails and
fetching zip files from the internet.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import shutil
import time
import zipfile
from typing import Tuple, List, Dict

# Third-party imports
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# Local imports
from core.config.config_factories import image_config_factory
from core.models.secret_model import MongerCashAuth, SecretType
from core.utils.data_access import WebDriverFactory
from core.utils.file_system import search_files_by_ext
from core.utils.interfaces import WordFilter
from core.utils.secret_handler import SecretHandler
from core.utils.strings import clean_filename
from core.utils.system_shell import imagick
from wordpress import WordPress
from workflows.builders import WorkflowMediaPayload


def fetch_thumbnail(
    folder: str, slug: str, remote_res: str, thumbnail_name: str = ""
) -> int:
    """This function handles the renaming and fetching of thumbnails that will be uploaded to
    WordPress as media attachments. It dynamically renames the thumbnails by taking in a URL slug to
    conform with SEO best-practices. Returns a status code of 200 if the operation was successful
    (fetching the file from a remote source). It also has the ability to store the image using a
    relative path.

    :param folder: ``str`` thumbnails dir
    :param slug: ``str`` URL slug
    :param remote_res: ``str`` thumbnail download URL
    :param thumbnail_name: ``str`` in case the user wants to upload different thumbnails and wishes to keep the names.
    :return: ``int`` (status code from requests)
    """
    thumbnail_dir: str = folder
    remote_data = requests.get(remote_res)
    cs_conf = image_config_factory()
    if thumbnail_name != "":
        name: str = f"-{thumbnail_name.split('.')[0]}"
    else:
        name: str = thumbnail_name
    img_name = clean_filename(f"{slug}{name}", cs_conf.pic_fallback)
    with open(os.path.join(thumbnail_dir, img_name), "wb") as img:
        img.write(remote_data.content)

    if cs_conf.imagick:
        imagick(
            os.path.join(thumbnail_dir, img_name),
            cs_conf.img_conversion_quality,
            cs_conf.pic_format,
        )

    return remote_data.status_code


def fetch_thumbnail_file(
    folder: str,
    remote_res: str,
) -> Tuple[str, int]:
    """
    Fetches a thumbnail file from the given remote resource and saves it to the specified folder.

    :param folder: ``str`` thumbnails dir (typically a temporary folder)
    :param remote_res: ``str`` thumbnail download URL
    :return: ``tuple[str, int]`` (file name, status code)
    """
    thumbnail_dir: str = folder
    remote_data = requests.get(remote_res)
    img_name = WordFilter(delimiter=" ").add_word(remote_res).split()[-1]
    with open(os.path.join(thumbnail_dir, img_name), "wb") as img:
        img.write(remote_data.content)
    return os.path.join(os.path.abspath(folder), img_name), remote_data.status_code


def fetch_zip(
    dwn_dir: str,
    remote_res: str,
    parent: bool = False,
    gecko: bool = False,
    headless: bool = False,
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
    webdriver = WebDriverFactory(dwn_dir, headless=headless, gecko=gecko)
    webdrv = webdriver.get_instance()

    webdrv_user_sel = "Gecko" if gecko else "Chrome"
    logging.info(
        f"User selected webdriver {webdrv_user_sel} -> Headless? {str(headless)}"
    )
    logging.info(f"Using {dwn_dir} for downloads as per function params")

    mongercash_auth: MongerCashAuth = SecretHandler().get_secret(
        SecretType.MONGERCASH_PASSWORD
    )[0]
    username: str = mongercash_auth.username
    password: str = mongercash_auth.password
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

    time.sleep(5)
    zip_set = search_files_by_ext(
        "zip", parent=parent, folder=os.path.relpath(dwn_dir)
    )[0]
    print(f"--> Fetched file {zip_set}")
    logging.info(f"--> Fetched archive file {zip_set}")
    return None


def extract_zip(zip_path: str, extr_dir: str) -> None:
    """Locate and extract a .zip archive in different locations.
    For example, you can locate the .zip archive from a temporary location and extract it
    somewhere else.

    :param zip_path: ``str`` where to locate the zip archive.
    :param extr_dir: ``str`` where to extract the contents of the archive
    :return: ``None``
    """
    get_zip: List[str] = search_files_by_ext("zip", folder=os.path.relpath(zip_path))
    try:
        with zipfile.ZipFile(
            zip_loc := os.path.join(zip_path, get_zip[0]), "r"
        ) as zipf:
            zipf.extractall(path=os.path.abspath(extr_dir))
        print(
            f"--> Extracted files from {os.path.basename(zip_loc)} in folder {os.path.relpath(extr_dir)}"
        )
        logging.info(f"Extracted {zip_loc}")
        print("--> Tidying up...")
        try:
            # Some archives have a separate set of redundant files in that folder.
            # I don't want them.
            shutil.rmtree(junk_folder := os.path.join(extr_dir, "__MACOSX"))
            logging.info(f"Junk folder {junk_folder} detected and cleaned.")
        except (FileNotFoundError, NotImplementedError) as e:
            logging.warning(f"Caught {e!r} - Handled")
        finally:
            logging.info(f"Cleaning remaining archive in {zip_path}")
            os.remove(zip_loc)
    except (IndexError, zipfile.BadZipfile) as e:
        logging.error(f"Something went wrong with the archive extraction -> {e!r}")
        return None


def upload_image_set(
    ext: str,
    folder: str,
    title: str,
    wordpress_site: WordPress,
) -> None:
    """Upload a set of images to the WordPress Media endpoint.

    :param ext: ``str`` image file extension to look for.
    :param folder:  ``str`` Your thumbnails folder, just the name is necessary.
    :param title: ``str`` gallery name
    :param wordpress_site: ``WordPress`` instance
    :return: ``None``
    """
    thumbnails: List[str] = search_files_by_ext(ext, folder=folder)
    if len(thumbnails) == 0:
        # Assumes the thumbnails are contained in a directory
        # This could be caused by the archive extraction
        logging.info("Thumbnails contained in directory - Running recursive search")
        files: List[str] = search_files_by_ext(".jpg", recursive=True, folder=folder)

        get_parent_dir = lambda dr: os.path.split(os.path.split(dr)[-2:][0])[1]  # noqa: E731

        thumbnails: List[str] = [
            os.path.join(get_parent_dir(path), os.path.basename(path)) for path in files
        ]

    if len(thumbnails) != 0:
        logging.info(
            prnt_imgs
            := f"--> Uploading set with {len(thumbnails)} images to WordPress Media..."
        )
        print(prnt_imgs)
        print("--> Adding image attributes on WordPress...")
        thumbnails.sort()

    # Prepare the image new name so that separators are replaced by hyphens.
    # E.g. this_is_a_cool_pic.jpg => this-is-a-cool-pic.jpg

    for number, image in enumerate(thumbnails, start=1):
        img_attrs: Dict[str, str] = WorkflowMediaPayload().gallery_payload_factory(
            title, number
        )

        img_file = (
            WordFilter(delimiter="-")
            .add_word(os.path.splitext(os.path.basename(image))[0])
            .filter()
        )

        os.renames(
            os.path.join(folder, os.path.basename(image)),
            img_new := os.path.join(
                folder, clean_filename(os.path.basename(img_file), ext)
            ),
        )

        status_code: int = wordpress_site.upload_image(img_new, img_attrs)

        img_now = os.path.basename(img_new)
        if status_code == 200 or status_code == 201:
            logging.info(f"Removing --> {img_now}")
            os.remove(img_new)

        logging.info(
            img_seq := f"* Image {number} | {img_now} --> Status code: {status_code}"
        )
        print(img_seq)
    try:
        # Check if I have paths instead of filenames
        if len(thumbnails[0].split(os.sep)) > 1:
            try:
                shutil.rmtree(
                    remove_dir
                    := f"{os.path.join(os.path.abspath(folder), thumbnails[0].split(os.sep)[0])}"
                )
                logging.info(f"Removed dir -> {remove_dir}")
            except NotImplementedError:
                logging.info(
                    "Incompatible platform - Directory cleaning relies on tempdir logic for now"
                )
    except (IndexError, AttributeError):
        pass
