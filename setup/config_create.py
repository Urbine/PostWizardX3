"""
Configuration Generator for WebMaster SEO Tools

This module generates the initial configuration templates required for the webmaster_seo_tools package.
It creates the following configuration files in the core/config directory:

1. `client_info.ini` - Stores authentication credentials and API endpoints for various services:
   - WordPress admin access and API configuration
   - MongerCash authentication
   - Yandex API credentials
   - X (Twitter) API credentials
   - Telegram bot configuration

2. `tasks_conf.ini` - Contains settings for specific task operations:
   - MongerCash dump and set URLs
   - Campaign IDs for various services
   - Feed source configurations

3. `workflows_config.ini` - Defines workflow behavior and preferences:
   - Image processing settings (format, quality, attributes)
   - Content selection parameters and SQL queries
   - Gallery selection configuration
   - Embed assistance settings
   - Social media integration options

When executed as a script, this module creates the config directory structure
and populates it with template files that can be customized for your specific
implementation requirements.

Usage:
    python3 config_create.py

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os

# Locally implemented modules
import core

# Create the client_info.ini that store secrets and move it to the core package.
CLIENT_INFO_INI = """[WP_Admin]
user = <admin or another username>
app_password = <the app password you generated on WordPress>
author_admin = 1
hostname = <mysite.xyz>
api_base_url = https://mysite.xyz/wp-json/wp/v2
full_base_url = https://mysite.xyz
default_status = draft
wp_cache_file = wp_cache_config.json
wp_posts_file = wp_posts.json
wp_photos_file = wp_photos.json

[MongerCash]
username = <mcash_username>
password = <mcash_password>

[Yandex]
client_id = 
client_secret = 

[x_api]
uri_callback =
x_username = 
x_passw =
x_email =
api_key = 
api_secret =  
client_id = 
client_secret =  
access_token = <added automatically after app authorization>
refresh_token = <added automatically after app authorization>

[telegram_botfather]
telegram_group_channel_id = @<chat_id>
bot_token = 

[brave_search_api]
api_key_search = 

[google_custom_search]
api_key = 
# Generated one with image search, no safesearch filtering
# Both ids can be equal if you use a custom search engine that supports image search.
search_engine_id_img =
search_engine_id_web =


"""
TASKS_CONF_INI = """[dump_create_config]
mcash_dump_url = https://mongercash.com/internal.php?page=adtools&category=3&typeid=23&view=dump
mcash_set_url = https://mongercash.com/internal.php?page=adtools&category=3&typeid=4

[adult_next]
abjav_campaig_id =

[tubecorp_feeds]
source_id = 

[fhouse_api]
# Found in the dump data like "utm_campaign=xx.xxx"
fhouse_camp_utm = 
"""

WORKFLOWS_CONF_INI = """[general_config]
pic_format = .webp
imagick_enabled = False
conversion_quality = 80
fallback_pic_format = .jpg
website_name = <YOUR_SITE_DISPLAY_NAME>
domain_tld = <TLD>
wp_json_posts = wp_posts.json
wp_cache_config = wp_cache_config.json
# Only the directory name
logging_dirname = logs
# Tweak this option if you want to remove image attributes
# This is useful to de-optimise images for SEO
img_attrs = False

[content_select]
pic_format = .jpg
# Alternative queries:
# SELECT * FROM videos WHERE date>='2024' OR date>='2023'
# SELECT * FROM videos WHERE date>='2022' AND duration!='trailer'
sql_query = SELECT * FROM videos WHERE duration!='trailer' ORDER BY date DESC
# Based on the file that integrations generate
# Usually partner-dbContentHint-date
db_content_hint = vids
x_posting_auto = False
x_posting_enabled = False
telegram_posting_auto = False
telegram_posting_enabled = False
assets_conf = assets.ini
# Comma separated partners
partners= <partners>

[gallery_select]
# The format and files can include or exclude the extension as the functions in this
# project are equipped to deal with that.
wp_json_photos = wp_photos.json
db_content_hint = photos
sql_query = SELECT * FROM sets
reverse_slug = True
x_posting_auto = False
x_posting_enabled = False
telegram_posting_auto = False
telegram_posting_enabled = False
# Comma separated partners
partners= <partners>

[embed_assist]
sql_query = SELECT * FROM embeds ORDER BY date DESC
db_content_hint = dump
x_posting_auto = False
x_posting_enabled = False
telegram_posting_auto = False
telegram_posting_enabled = False
# Comma separated partners
partners= <partners>

[update_mcash_chain]
logging_dirname = logs
"""

if __name__ == "__main__":
    print("Welcome to the configuration create module.")
    print("This module will generate configuration templates for the utilities.")
    print(
        "Review the changes and modify the fields as needed once the files are generated.\n"
    )

    if os.path.exists(cfg_path := os.path.join(os.getcwd(), "core", "config")):
        os.makedirs(cfg_path, exist_ok=True)

    core.write_to_file(
        "client_info", os.path.join("core", "config"), "ini", CLIENT_INFO_INI
    )
    core.write_to_file(
        "tasks_config", os.path.join("core", "config"), "ini", TASKS_CONF_INI
    )
    core.write_to_file(
        "workflows_config", os.path.join("core", "config"), "ini", WORKFLOWS_CONF_INI
    )
