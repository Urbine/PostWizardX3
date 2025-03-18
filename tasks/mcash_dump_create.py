"""
Video dump file creation with web automation

The main responsibility of this program is the collection of video information from our content partner:
`MongerCash`; it generates a ``.txt`` file with all information specific to a partner offer.
This is the first step in the data collection process.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import datetime
import tempfile
import time
from tempfile import TemporaryDirectory
from typing import Optional

# Third-party Libraries
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By


# Local implementations
import core
from core import monger_cash_auth, tasks_conf
from core.config_mgr import MongerCashAuth, TasksConf


def parse_partner_name(partner_options: list[WebElement], select_num: int) -> str:
    """Parse, obtain, and contruct the full partner name from the option matched by the
    ``partner_hint`` parameter in the main driver function. It will join it so that it can be used a filename.

    :param partner_options: ``list[WebElement]`` with all the partner options on the site.
    :param select_num: ``int`` index of the partner offer used by the automation sequence.
    :return: ``str`` partner name joined by `-` (hyphens)
    """
    return "-".join(
        partner_options[select_num].text.split("-")[:-1][0].lower().split(" ")
    )


def get_vid_dump_flow(
    webdrv,
    mcash_info: MongerCashAuth = monger_cash_auth(),
    task_conf: TasksConf = tasks_conf(),
    partner_hint: Optional[str] = None,
    temp_dir_p: str = "",
) -> tuple[TemporaryDirectory[str], str] | str:
    """Get the text file and match the options with the hint provided to get a video dump file
    specific to a partner offer.

    :param temp_dir_p: ``str`` - path of your temporary directory
    :param mcash_info: ``MongerCashAuth`` object with necessary credentials for authentication. (Default)
    :param task_conf: ``TasksConf`` object with configuration information like `download_folder`
    :param webdrv: ``webdriver`` Chrome/Gecko webdriver that interfaces with Selenium.
    :param parent: ``bool`` True to tell the ``write_to_file`` function to write in the parent directory.
    :param partner_hint: ``str`` pattern to match the partner with available options.
    :return: ``str`` new dump filename
    """
    source_html = None
    with webdrv as driver:
        # Go to URL
        driver.minimize_window()
        driver.get(task_conf.mcash_dump_url)
        driver.implicitly_wait(30)

        username_box = driver.find_element(By.ID, "user")
        pass_box = driver.find_element(By.ID, "password")

        username_box.send_keys(mcash_info.username)
        pass_box.send_keys(mcash_info.password)

        button_login = driver.find_element(By.ID, "head-login")
        button_login.click()

        website_partner = driver.find_element(By.ID, "link_site")
        website_partner_select = Select(website_partner)
        partner_options = website_partner_select.options
        if partner_hint:
            selection = core.match_list_single(
                partner_hint, partner_options, ignore_case=True
            )
        else:
            for num, opt in enumerate(partner_options, start=0):
                print(f"{num}. {opt.text}")

            selection = input("\nEnter a number and select a partner: ")

        website_partner_select.select_by_index(int(selection))
        partner_name = parse_partner_name(partner_options, int(selection))

        apply_changes_xpath = (
            "/html/body/div[1]/div[2]/form/div/div[2]/div/div/div[6]/div/div/input"
        )
        apply_changes_button = driver.find_element(By.XPATH, apply_changes_xpath)
        apply_changes_button.click()

        # Refresh the page to avoid loading status crashes in Chrome
        driver.refresh()

        # Dump format: Dump with | (Select this one on MongerCash)
        # name | description | models | tags | site_name | date | source | thumbnail | tracking

        # Dump type select `Dump with |`
        dump_format = driver.find_element(By.ID, "dump_format")
        Select(dump_format).select_by_index(2)

        # There are 8 fields, I need 9.
        append_field = driver.find_element(By.ID, "appendFieldPlus")
        append_field.click()

        # First field: video name
        name_field = driver.find_element(By.ID, "dp_field_0")
        Select(name_field).select_by_index(1)

        # Second field: video description
        description_field = driver.find_element(By.ID, "dp_field_1")
        Select(description_field).select_by_index(3)

        # Third field: models
        models_field = driver.find_element(By.ID, "dp_field_2")
        Select(models_field).select_by_index(10)

        # Fourth field: traffic tags
        tags_field = driver.find_element(By.ID, "dp_field_3")
        Select(tags_field).select_by_index(6)

        # Fifth field: site name
        site_name_field = driver.find_element(By.ID, "dp_field_4")
        Select(site_name_field).select_by_index(16)

        # Sixth field: date
        date_field = driver.find_element(By.ID, "dp_field_5")
        Select(date_field).select_by_index(17)

        # Seventh field: source URL
        source_field = driver.find_element(By.ID, "dp_field_6")
        Select(source_field).select_by_index(5)

        # Eighth field: thumbnail URL
        source_field = driver.find_element(By.ID, "dp_field_7")
        Select(source_field).select_by_index(4)

        # Ninth field: tracking URL
        tracking_field = driver.find_element(By.ID, "dp_field_8")
        Select(tracking_field).select_by_index(18)

        # Update Dump textarea
        dump_update = driver.find_element(By.ID, "dumpUpdate")
        dump_update.click()

        # Extract textarea text
        dump_txtarea = driver.find_element(By.CLASS_NAME, "display-dump-textarea")

        while not dump_txtarea.text:
            continue

        dump_content = dump_txtarea.text

        # Create a name for out dump file.
        dump_name = f"{partner_name}vids-{datetime.date.today()}"

        if temp_dir_p == "":
            temp_dir = tempfile.TemporaryDirectory(dir=".")
            core.write_to_file(dump_name, temp_dir.name, "txt", dump_content)
            return temp_dir, dump_name
        else:
            core.write_to_file(dump_name, temp_dir_p, "txt", dump_content)
            return dump_name
