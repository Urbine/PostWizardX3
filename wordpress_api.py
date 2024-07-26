# This the first attempt at connecting the WordPress API to gather information
# to streamline analytics and other processes.

from collections import namedtuple
import pprint
import requests

from main import (get_client_info,
                  export_request_json,
                  import_request_json,
                  export_to_csv)


# curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/users?context=edit
# In other words: curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/ENDPOINT

def curl_wp_self_concat(wp_self, param_lst):
    """
    :param wp_self: (str) wp base url
    :param param_lst: (list -> str) list of URl params
    :return: json object
    """
    username_ = get_client_info()["WordPress"]["user_apps"]["wordpress_api.py"]["username"]
    app_pass_ = get_client_info()["WordPress"]["user_apps"]["wordpress_api.py"]["app_password"]
    wp_self = wp_self + "".join(param_lst)
    return requests.get(wp_self, headers={"user": f"{username_}:{app_pass_}"}).json()

# Tags and its IDs are repeated and must be isolated
# to count for the unique elements in each dictionary and merge them.

def get_tag_count(wp_posts_f) -> dict:
    """
    :param wp_posts_f: file with the posts information from WordPress.
    :return: (dict)
    """
    tags_count = {}
    for dic in wp_posts_f:
        for kw in dic['yoast_head_json']['schema']['@graph'][0]['keywords']:
            if kw in tags_count.keys():
                tags_count[kw] = tags_count[kw] + 1
                continue
            else:
                tags_count[kw] = 1
                continue
    return tags_count


def get_tags_num_count(wp_posts_f) -> dict:
    tags_nums_count = {}
    for dic in wp_posts_f:
        for tag_num in dic["tags"]:
            if tag_num in tags_nums_count.keys():
                tags_nums_count[tag_num] = tags_nums_count[tag_num] + 1
                continue
            else:
                tags_nums_count[tag_num] = 1
                continue
    return tags_nums_count

# Ideally, I want an ordered data structure that combines tag name, id, and count.
# I am creating a NamedTuple with this information. However, I want to leave this
# dictionary function, just in case.

def tag_id_merger_dict(wp_posts_f):
    return {tag: t_id for tag, t_id in zip(get_tag_count(wp_posts_f).keys(),
                                           get_tags_num_count(wp_posts_f).keys())}

def tag_master_merger_ntpl(wp_posts_f):
    tag_id_merger = zip(get_tag_count(wp_posts_f).keys(),
                    get_tags_num_count(wp_posts_f).keys(), get_tag_count(wp_posts_f).values())
    WP_Tags = namedtuple("WP_Tags", ['title', 'ID', 'count'])
    cooked = [WP_Tags(title, ids, count) for title, ids, count in tag_id_merger]
    return cooked

# I want hostname as input()
hostname = 'whoresmen.com'
base_url = f"https://{hostname}/wp-json/wp/v2"

endpoints = {
    "users": "/users?",
    "posts": {
        "posts_url": "/posts",
        "per_page": "?per_page="
    }}

# List of parameters that I intend to concatenate to the base URL.
params_posts_per_page = [endpoints["posts"]["posts_url"],
                         endpoints["posts"]["per_page"], "100"]

# Concatenate and get json
if input("Want to fetch a new copy of the json file? Y/N: ").lower() == ("y" or "yes"):
    curl_clone = curl_wp_self_concat(base_url, params_posts_per_page)
    # Caching a copy of the request for analysis and performance gain.
    export_request_json("wp_posts", curl_clone, 1)
else:
    print("Okay, using local file from now on!")
    pass

# Loading local cache
imported_json = import_request_json("wp_posts")


# ==== Post data structure ====
# title: imported_json[0]['title']['rendered']
# description: imported_json[0]['content']['rendered']
# tags text and category : imported_json[0]['class_list'] (prefixed with "tag-" and "category-")
# slug: imported_json[0]['slug']
# tag numbers: imported_json[0]['tags']
# link: imported_json[0]['link']
# id: imported_json[0]['id']
# yoast json: imported_json[0]['yoast_head_json'] (can get info without overhead)
# yoast tags without prefix: imported_json[0]['yoast_head_json']['schema']['@graph'][0]['keywords']
# yoast category: imported_json[0]['yoast_head_json']['schema']['@graph'][0]['articleSection']

# tag_id_merger = zip(get_tag_count(imported_json).keys(),
#                     get_tags_num_count(imported_json).keys(), get_tag_count(imported_json).values())

th = tag_master_merger_ntpl(imported_json)

export_to_csv(th, "sample", ["Title", "Tag ID", "# of Taggings"])

