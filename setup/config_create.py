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
"""
TASKS_CONF_INI = """[dump_create_config]
mcash_dump_url = https://mongercash.com/internal.php?page=adtools&category=3&typeid=23&view=dump
mcash_set_url = https://mongercash.com/internal.php?page=adtools&category=3&typeid=4
"""

WORKFLOWS_CONF_INI = """[general_config]
# Consider whether or not ImageMagick is enabled before using next-gen image formats.
pic_format = .webp
# Make sure to capitalise "True" and "False" to avoid IncorrectConfiguration exceptions.
imagick_enabled = False
conversion_quality = 80
# Fallback image format if ImageMagick is not enabled or not found.
# This is usually the source format of the thumbnails or images you download and plan to utilise on WP.
fallback_pic_format = .jpg
website_name = <YOUR_SITE_DISPLAY_NAME>
domain_tld = <TLD>
wp_json_posts = wp_posts.json
wp_cache_config = wp_cache_config.json

[content_select]
pic_format = .jpg
# Alternative queries:
# SELECT * FROM videos WHERE date>='2024' OR date>='2023'
# SELECT * FROM videos WHERE date>='2022' AND duration!='trailer'
sql_query = SELECT * FROM videos WHERE duration!='trailer' ORDER BY date DESC
db_content_hint = vids
x_posting_auto = False
x_posting_enabled = False
assets_conf = assets.ini
# Comma separated partners
partners= Asian Sex Diary,TukTuk Patrol,Trike Patrol,Euro Sex Diary,Paradise GF's,Totico's

[gallery_select]
# The format and files can include or exclude the extension as the functions in this
# project are equipped to deal with that.
wp_json_photos = wp_photos.json
db_content_hint = photos
sql_query = SELECT * FROM sets
x_posting_auto = False
x_posting_enabled = False
# Comma separated partners
partners= Asian Sex Diary,Tuktuk Patrol,Trike Patrol,Euro Sex Diary

[embed_assist]
sql_query = SELECT * FROM embeds ORDER BY date DESC
db_content_hint = dump
x_posting_auto = False
x_posting_enabled = False
# Comma separated partners
partners= abjav,vjav,Desi Tube
"""

if __name__ == "__main__":
    print("Welcome to the configuration create module.")
    print("This module will generate the configuration templates for the utilities.")
    print(
        "Review the changes and modify the fields as needed once the files are generated.\n"
    )

    core.write_to_file("client_info", "core/config", "ini", CLIENT_INFO_INI)
    core.write_to_file("tasks_config", "core/config", "ini", TASKS_CONF_INI)
    core.write_to_file("workflows_config", "core/config", "ini", WORKFLOWS_CONF_INI)
