from bs4 import BeautifulSoup
from main import get_client_info
import re
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pprint
import xml

import time

# Configure Chrome's Path and arguments
chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = "/opt/google/chrome/google-chrome"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")

# Initialize the webdriver
web_driver = webdriver.Chrome(options=chrome_options)

username = get_client_info()['WordPress']['wp_admin']['username']
password = get_client_info()['WordPress']['wp_admin']['password']

wp_admin_videos = 'https://whoresmen.com/wp-admin/edit.php'

with web_driver as driver:
    # Go to URL
    url = wp_admin_videos
    driver.get(url)

    # Find element by its ID
    username_box = driver.find_element(By.ID, 'user_login')
    pass_box = driver.find_element(By.ID, 'user_pass')
    math_challenge_label = driver.find_element(By.XPATH, '//*[@id="loginform"]/div[2]/label')
    math_challenge_box = driver.find_element(By.ID, 'jetpack_protect_answer')

    # Some steps to bypass the WP Math Challenge dynamically
    x = [num for num in math_challenge_label.text if num != ' ']
    length = len(x)
    sum = "".join(x[0:length-1])

    # Authenticate / Send keys
    username_box.send_keys(username)
    pass_box.send_keys(password)
    math_challenge_box.send_keys(eval(sum))
    time.sleep(3)

    # Get Button Class
    button_login = driver.find_element(By.ID, 'wp-submit')

    # Click on the login Button
    button_login.click()
    time.sleep(3)

    # A successful authentication redirects the user
    # to the main page, so we need to get the wp_admin_videos url again.
    driver.get(wp_admin_videos)

    # Find the 'Add video' button
    add_video = driver.find_element(By.XPATH, '//*[@id="wpbody-content"]/div[3]/a')
    add_video.click()
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

pprint.pprint(soup)