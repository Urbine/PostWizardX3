# Accessing MongerCash to get a dump file.

import datetime

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import time

# Local implementations
import helpers


# ==== Functions ====

def get_vid_dump_flow(url_: str,
                      c_info: tuple,
                      webdrv: webdriver,
                      parent: bool = True) -> None:
    # Captures the source outside the context manager.
    source_html = None
    with (webdrv as driver):
        # Go to URL
        print(f"Getting Dump file from MongerCash")
        print("Please wait...\n")
        driver.get(url_)

        # Find element by its ID
        username_box = driver.find_element(By.ID, 'user')
        pass_box = driver.find_element(By.ID, 'password')

        # Authenticate / Send keys
        username_box.send_keys(c_info[0])
        pass_box.send_keys(c_info[1])
        time.sleep(1)

        # Get Button Class
        button_login = driver.find_element(By.ID, 'head-login')

        # Click on the login Button
        button_login.click()
        time.sleep(1)

        # Partner select
        website_partner = driver.find_element(By.XPATH, '//*[@id="link_site"]')
        website_partner_select = Select(website_partner)
        partner_options = website_partner_select.options
        for num, opt in enumerate(partner_options, start=0):
            print(f'{num}. {opt.text}')

        selection = input("\nEnter a number and select a partner: ")
        website_partner_select.select_by_index(int(selection))
        partner_name = '-'.join(partner_options[int(selection)].text.split('-')[:-1][0].lower().split(' '))

        time.sleep(1)
        apply_changes_xpath = '/html/body/div[1]/div[2]/form/div/div[2]/div/div/div[6]/div/div/input'
        apply_changes_button = driver.find_element(By.XPATH, apply_changes_xpath)
        apply_changes_button.click()
        time.sleep(1)

        # Refresh the page to avoid loading status crashes in Chrome
        driver.refresh()

        # Dump format: Dump with | (Select this one on MongerCash)
        # name | description | models | tags | site_name | date | source | thumbnail | tracking

        # Dump type select `Dump with |`
        dump_format = driver.find_element(By.ID, 'dump_format')
        Select(dump_format).select_by_index(2)

        # There are 8 fields, I need 9.
        append_field = driver.find_element(By.ID, 'appendFieldPlus')
        append_field.click()

        # First field: video name
        name_field = driver.find_element(By.ID, 'dp_field_0')
        Select(name_field).select_by_index(1)

        # Second field: video description
        description_field = driver.find_element(By.ID, 'dp_field_1')
        Select(description_field).select_by_index(3)

        # Third field: models
        models_field = driver.find_element(By.ID, 'dp_field_2')
        Select(models_field).select_by_index(10)

        # Fourth field: traffic tags
        tags_field = driver.find_element(By.ID, 'dp_field_3')
        Select(tags_field).select_by_index(6)

        # Fifth field: site name
        site_name_field = driver.find_element(By.ID, 'dp_field_4')
        Select(site_name_field).select_by_index(16)

        # Sixth field: date
        date_field = driver.find_element(By.ID, 'dp_field_5')
        Select(date_field).select_by_index(17)

        # Seventh field: source URL
        source_field = driver.find_element(By.ID, 'dp_field_6')
        Select(source_field).select_by_index(5)

        # Eighth field: thumbnail URL
        source_field = driver.find_element(By.ID, 'dp_field_7')
        Select(source_field).select_by_index(4)

        # Ninth field: tracking URL
        tracking_field = driver.find_element(By.ID, 'dp_field_8')
        Select(tracking_field).select_by_index(18)

        # Update Dump textarea
        dump_update = driver.find_element(By.ID, 'dumpUpdate')
        dump_update.click()
        time.sleep(3)

        # Extract textarea text
        dump_txtarea = driver.find_element(By.CLASS_NAME, 'display-dump-textarea')
        dump_content = dump_txtarea.text

        # Create a name for out dump file.
        dump_name = f'{partner_name}{datetime.date.today()}'

        helpers.write_to_file(dump_name, 'txt', dump_content, parent=parent)

    return None


# ==== Execution space ====

# Configure Chrome's Path and arguments
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = "/opt/google/chrome/google-chrome"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")

# Initialize the webdriver
web_driver = webdriver.Chrome(options=chrome_options)

# TODO: Use JSON notation to store user credentials
#  so that no private information is pushed to GitHub. OK
username = helpers.get_client_info('client_info.json',
                                   parent=True)['MongerCash']['username']

password = helpers.get_client_info('client_info.json',
                                   parent=True)['MongerCash']['password']

if __name__ == '__main__':
    m_cash_vids_dump = 'https://mongercash.com/internal.php?page=adtools&category=3&typeid=23&view=dump'

    get_vid_dump_flow(m_cash_vids_dump,
                      (username, password), web_driver)
