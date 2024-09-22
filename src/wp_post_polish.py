from bs4 import BeautifulSoup

import helpers
import re
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pprint

import time

# Configure Chrome binary Path and arguments
chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = "/opt/google/chrome/google-chrome"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")


# Initialize the webdriver
web_driver = webdriver.Chrome(options=chrome_options)

# Get login credential from the JSON file in the project root
username = helpers.get_client_info('client_info.json',parent=True)['WordPress']['wp_admin']['username']
password = helpers.get_client_info('client_info.json',parent=True)['WordPress']['wp_admin']['password']

wp_admin_params = {
    'video_posts': '/edit.php',
    'new_post': '/post-new.php'
}

wp_admin = 'https://whoresmen.com/wp-admin'

with web_driver as driver:
    # Go to URL
    url = wp_admin
    driver.get(url)

    # Find login elements -> Beginning of the procedure.
    username_box = driver.find_element(By.ID, 'user_login')
    pass_box = driver.find_element(By.ID, 'user_pass')
    math_challenge_label = driver.find_element(By.XPATH, '//*[@id="loginform"]/div[2]/label')
    math_challenge_box = driver.find_element(By.ID, 'jetpack_protect_answer')

    # WP Math Challenge handling
    x = [num for num in math_challenge_label.text if num != ' ']
    length = len(x)
    sum = "".join(x[0:length-1])

    # Authenticate / Solve math challenge
    username_box.send_keys(username)
    pass_box.send_keys(password)
    math_challenge_box.send_keys(eval(sum))
    time.sleep(3)

    # Get Login Button
    button_login = driver.find_element(By.ID, 'wp-submit')
    button_login.click()
    time.sleep(3)

    # A successful authentication redirects the user to the main page
    # so I need to get the wp_admin url again with the relevant route.
    driver.get(wp_admin + wp_admin_params['new_post'])

    print('Find the Add video button\n')
    # Find the 'Add video' button
    # add_video = driver.find_element(By.XPATH, '//*[@id="wpbody-content"]/div[3]/a')
    # add_video.click()
    time.sleep(10)

    print("Find the 'Add title' field and introduce text")
    # Find the 'Add title' field and introduce text
    add_title_css = ".wp-block-post-title"
    add_title = driver.find_element(By.CSS_SELECTOR, add_title_css)
    add_title.send_keys('Test post from Python')

    print("Find the editor block")
    # Find the editor block
    # editor_block_xpath = "/html[1]/body[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/div[4]/div[2]/p[1]"
    # editor_block = driver.find_element(By.XPATH, editor_block_xpath)
    # editor_block.click()
    # editor_block.send_keys('This is a post generated with Selenium Webdriver and Python.')

    print("==== Yoast SEO Fields ====")
    # ==== Yoast SEO Fields ====
    focus_keyphrase = driver.find_element(By.XPATH, "//input[@id='focus-keyword-input-metabox']")
    focus_keyphrase.click()
    focus_keyphrase.send_keys('Python')

    # TODO: Get the progress <div> element to measure SEO Meta description and slug length
    post_slug = driver.find_element(By.XPATH, "//input[@id='yoast-google-preview-slug-metabox']")
    post_slug.click()
    post_slug.clear()
    post_slug.send_keys('this-post-is-a-test-from-python')

    post_slug.send_keys('This is a sample meta description from Selenium Webdriver')

    meta_description_elem = '<div data-contents="true"><div class="" data-block="true" data-editor="bnml3" data-offset-key="a84pc-0-0"><div data-offset-key="a84pc-0-0" class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr"><span data-offset-key="a84pc-0-0"><span data-text="true">this is a meta description</span></span></div></div></div>'
    post_meta_description_xpath = "//div[@id='yoast-google-preview-description-metabox']"
    post_meta_description = driver.find_element(By.XPATH, post_meta_description_xpath)
    post_meta_description.send_keys(meta_description_elem)

    print("Video information fields")
    # Video information fields
    # The featured field is set to 'No' by default.

    # Sets 'High-definition (HD)' to 'Yes'
    hd_radius_css = ".rwmb-field:nth-child(5) label:nth-child(2) > .rwmb-radio"
    driver.find_element(By.CSS_SELECTOR, hd_radius_css).click()

    # # Sets Production to 'Professional'
    # production_radius_xpath = "//input[@value='professional']"
    driver.find_element(By.NAME, 'production').click()

    # # Sets 'Orientation' to 'Straight'
    # orientation_radius_xpath = "//input[@value='straight']"
    driver.find_element(By.NAME, 'video_orientation').click()

    print("File source field")
    # File source field
    sample_file = 'https://hosted.mongercash.com/ttp/video/alina_kim_trailer.mp4'
    file_source_field = driver.find_element(By.XPATH, "//input[@id='video_url']")
    file_source_field.click()
    file_source_field.send_keys(sample_file)

    print("Duration fields")
    # Duration fields
    # hours_select_field = driver.find_element(By.XPATH, "//select[@id='hours']")
    # select_hours = Select(hours_select_field)
    # select_hours.select_by_index(0)

    minutes_select_field = driver.find_element(By.XPATH, "//select[@id='minute']")
    select_minutes = Select(minutes_select_field)
    select_minutes.select_by_value('04')

    # seconds_select_field = driver.find_element(By.XPATH, "//select[@id='second']")
    # select_seconds = Select(seconds_select_field)
    # select_seconds.select_by_index('00')

    print("Pornstar information fields")
    # Pornstar information fields
    # Setting ethnicity only
    ethnicity_select_field = driver.find_element(By.XPATH, "//select[@id='ethnicity']")
    ethnicity_select = Select(ethnicity_select_field)
    ethnicity_select.select_by_value('Asian')

    print("Thumbnails and trailer fields")
    # Thumbnails and trailer fields
    # Setting thumbnail only
    sample_thumbnail = 'https://hosted.mongercash.com/ttp/video/alina_kim_trailer.jpg'
    main_thumbnail_field = driver.find_element(By.XPATH, "//input[@id='thumb']")
    main_thumbnail_field.click()
    main_thumbnail_field.send_keys()

    # Let's give autosaving some secs.
    time.sleep(5)

    print("Locate 'Save draft' button and click on it.")
    # Locate 'Save draft' button and click on it.
    save_draft_xpath = "//button[@aria-label='Save draft']"
    save_draft = driver.find_element(By.XPATH, save_draft_xpath)
    save_draft.click()

