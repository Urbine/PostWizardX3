# Accessing MongerCash to get Hosted Videos and links
from main import get_client_info
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pprint

# Configure Chrome's Path and argument
chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = "/opt/google/chrome/google-chrome"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")

# Initialize the webdriver
web_driver = webdriver.Chrome(options=chrome_options)

m_cash_hosted_vids = 'https://mongercash.com/internal.php?page=adtools&category=3&typeid=23'

# TODO: Use JSON notation to store user credentials
#  so that no private information is pushed to GitHub.
username = get_client_info()['MongerCash']['username']
password = get_client_info()['MongerCash']['password']

# TODO: Get all text areas and video titles.
# TODO: Set up page progression with webdriver navigation.
# TODO: Select a specific partner and apply changes by using webdriver.

# Run Selenium with a Context Manager
with web_driver as driver:
    # Go to URL
    url = m_cash_hosted_vids
    driver.get(url)


    # Find element by its ID
    username_box = driver.find_element(By.ID, 'user')
    pass_box = driver.find_element(By.ID, 'password')

    # Authenticate / Send keys
    username_box.send_keys(username)
    pass_box.send_keys(password)
    time.sleep(1)

    # Get Button Class
    button_login = driver.find_element(By.ID, 'head-login')

    # Click The Button
    button_login.click()
    time.sleep(3)
    print(driver.page_source)