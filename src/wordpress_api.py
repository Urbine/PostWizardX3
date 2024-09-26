# This the first attempt at connecting the WordPress API to gather information
# to streamline analytics and other processes.
import json
import re
from collections import namedtuple
import helpers
import os
import pprint

import requests
import sqlite3
import time
import xlsxwriter
from requests.auth import HTTPBasicAuth


# curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/users?context=edit
# In other words: curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/REST_PARAMS

def curl_wp_self_concat(wp_self: str, param_lst: list[str]) -> list[dict]:
    """
    Makes the GET request based on the curl mechanism as described on the docs.
    :param wp_self: (str) wp base url
    :param param_lst: (list -> str) list of URl params
    :return: json object
    """
    client_info_file = helpers.get_client_info('client_info.json', parent=True)
    username_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["username"]
    app_pass_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["app_password"]
    wp_self: str = wp_self + "".join(param_lst)
    return requests.get(wp_self, headers={"user": f"{username_}:{app_pass_}"}).json()


def wp_post_create(wp_self: str, param_lst: list[str], payload):
    """
    Makes the GET request based on the curl mechanism as described on the docs.
    :param payload: dictionary with the post information.
    :param wp_self: (str) wp base url
    :param param_lst: (list -> str) list of URl params
    :return: json object
    """
    client_info_file = helpers.get_client_info('client_info.json', parent=True)
    username_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["username"]
    app_pass_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["app_password"]
    auth_wp = HTTPBasicAuth(username_, app_pass_)
    wp_self: str = wp_self + "".join(param_lst)
    return requests.post(wp_self, json=payload, auth=auth_wp).status_code


def get_all_posts(hostname: str, params_dict: dict) -> list[dict]:
    """
    :param hostname: hostname of your WP site.
    :param params_dict: dictionary with the rest parameters in the URL.
    :return: list[dict]
    """
    # Accumulation of dict elements for concatenation.
    result_dict: list[dict] = []
    base_url: str = f"https://{hostname}/wp-json/wp/v2"
    # List of parameters that I intend to concatenate to the base URL.
    # /posts/page=1
    page_num: int = 1
    params_posts: list[str] = [params_dict["posts"]["posts_url"]]
    page_num_param: bool = False
    print("\nWorking on it...\n")
    while True:
        curl_json: list[dict] = curl_wp_self_concat(base_url, params_posts,)
        try:
            if curl_json["data"]["status"] == 400:
                print(f"\n{'DONE':=^30}\n")
                return result_dict
        except TypeError:
            print(f"Processing page #{page_num}")
            page_num += 1
            if page_num_param is False:
                params_posts.append(params_dict["posts"]["page"])
                params_posts.append(str(page_num))
                page_num_param = True
            else:
                params_posts[-1] = str(page_num)
            for item in curl_json:
                result_dict.append(item)


# Tags and its IDs are repeated and must be isolated
# to count for the unique elements in each dictionary and merge them.

# This assumes that Yoast is running in your WordPress installation.
def get_tag_count(wp_posts_f: list[dict]) -> dict:
    """
    Counts every occurrence of a tag in the entire posts json file.
    :param wp_posts_f: file with the posts information from WordPress.
    :return: (dict)
    """
    tags_count: dict = {}
    for dic in wp_posts_f:
        for kw in dic['yoast_head_json']['schema']['@graph'][0]['keywords']:
            if kw in tags_count.keys():
                tags_count[kw] = tags_count[kw] + 1
                continue
            else:
                tags_count[kw] = 1
                continue
    return tags_count


def get_tags_num_count(wp_posts_f: list[dict]) -> dict:
    """
    Counts the occurrences of tags, however, this function fetches the tag numbers
    not the actual names. This is necessary to match everything at a later routine.
    :param wp_posts_f: Posts json
    :return: dict
    """
    tags_nums_count: dict = {}
    for dic in wp_posts_f:
        for tag_num in dic["tags"]:
            if tag_num in tags_nums_count.keys():
                tags_nums_count[tag_num] = tags_nums_count[tag_num] + 1
                continue
            else:
                tags_nums_count[tag_num] = 1
                continue
    return tags_nums_count

def get_slugs(wp_posts_f: list[dict]) -> list[str]:
    return [url['slug'] for url in wp_posts_f]

# TODO: Code reuse, map unique keys and count or aggregate info.

# Ideally, I want an ordered data structure that combines tag name, id, and count.
# I am creating a NamedTuple with this information. However, I want to leave this
# dictionary function, just in case.

def tag_id_merger_dict(wp_posts_f: list[dict]) -> dict:
    """
    Returns a dictionary {"tag": "tag-id"} from the output from other functions.
    :param wp_posts_f:
    :return: dict
    """
    return {tag: t_id for tag, t_id in zip(get_tag_count(wp_posts_f).keys(),
                                           get_tags_num_count(wp_posts_f).keys())}


def tag_id_count_merger(wp_posts_f: list[dict]) -> list:
    """
       This function makes a list of namedtuples with fields ['title', 'ID', 'count'] .
       :param wp_posts_f: WP Posts Json
       :return: List[namedTuple, ...]
       """
    tag_id_merger = zip(get_tag_count(wp_posts_f).keys(),
                        get_tags_num_count(wp_posts_f).keys(), get_tag_count(wp_posts_f).values())
    Tag_ID_Count = namedtuple("WP_Tags", ['title', 'ID', 'count'])
    cooked = [Tag_ID_Count(title, ids, count) for title, ids, count in tag_id_merger]
    return cooked


def get_tag_id_pairs(wp_posts_f: list[dict]) -> dict:
    """
    This function makes a {"tag": ["post id", ...]} dictionary.
    :param wp_posts_f: WP Posts Json
    :return: dict
    """
    unique_tags = get_tag_count(wp_posts_f).keys()
    tags_c: dict = {kw: [] for kw in unique_tags}
    for dic in wp_posts_f:
        for kw in dic['yoast_head_json']['schema']['@graph'][0]['keywords']:
            if kw in tags_c.keys():
                tags_c[kw].append(dic['id'])
                continue
    return tags_c


def get_post_titles_local(wp_posts_f: list[dict]):
    all_titles = []
    for post in wp_posts_f:
        all_titles.append(post['title']['rendered'])
    return all_titles


def map_posts_by_id(wp_posts_f: list[dict], host_name=None) -> dict:
    """
    Associates post ID with a url.
    :param wp_posts_f: Posts json
    :param host_name: (str) your hostname (Optional param = None)
    :return: dict
    """
    u_pack = zip([idd['id'] for idd in wp_posts_f],
                 [url['slug'] for url in wp_posts_f])
    if host_name is not None:
        return {idd: f"{host_name}/" + url for idd, url in u_pack}
    else:
        return {idd: url for idd, url in u_pack}


def map_tags_post_urls(wp_posts_f: list[dict], host_name=None) -> dict:
    """
    This function makes a {"Tag": ["post slug", ...]} dictionary.
    :param wp_posts_f: WP Posts Json
    :param host_name Optional set to None, hostname str if you want it as output.
    :return: dict
    """
    mapped_ids = map_posts_by_id(wp_posts_f, host_name)
    unique_tags = get_tag_count(wp_posts_f).keys()
    tags_c = {kw: [] for kw in unique_tags}
    for dic in wp_posts_f:
        for kw in dic['yoast_head_json']['schema']['@graph'][0]['keywords']:
            if kw in tags_c.keys():
                tags_c[kw].append(mapped_ids[dic['id']])
                continue
    return tags_c


def map_tags_posts(wp_posts_f: list[dict], host_name=None, idd=None) -> dict:
    """
    This function makes a {"Tag": ["post slug", ...]} or {"Tag": ["post id", ...]} dictionary.
    :param wp_posts_f: WP Posts json
    :param host_name Optional set to None, hostname str if you want it as output.
    :param idd (Bool) You can set this one to True if you want the post ids
            instead of the slugs.
    :return: dict
    """
    mapped_ids: dict = map_posts_by_id(wp_posts_f, host_name)
    unique_tags = get_tag_count(wp_posts_f).keys()
    tags_c: dict = {kw: [] for kw in unique_tags}
    for dic in wp_posts_f:
        for kw in dic['yoast_head_json']['schema']['@graph'][0]['keywords']:
            if kw in tags_c.keys():
                if idd is True:
                    tags_c[kw].append(dic['id'])
                    continue
                else:
                    tags_c[kw].append(mapped_ids[dic['id']])
                    continue
    return tags_c


def map_postsid_category(wp_posts_f: list[dict], host_name=None) -> dict:
    """
    Associates post ID with a url.
    :param wp_posts_f: Posts json
    :param host_name: (str) your hostname (Optional param = None)
    :return: dict
    """
    # In the case of KeyError, there is at least one post that hasn't been categorized in WordPress.
    # Check the culprit with the following code:
    # try:
    #     for url in imported_json:
    #         print(url['yoast_head_json']['schema']['@graph'][0]['articleSection'])
    # except KeyError:
    #     pprint.pprint(url)
    u_pack = zip([idd['id'] for idd in wp_posts_f],
                 [url['yoast_head_json']['schema']['@graph'][0]['articleSection'] for url in wp_posts_f])
    if host_name is not None:
        return {idd: f"{host_name}/" + url for idd, url in u_pack}
    else:
        return {idd: cat for idd, cat in u_pack}


def unpack_tpl_excel(tupled_list) -> None:
    """
    This function was created to write the tuple (by typecast) contents of
    another function into an .xlsx file cell appropriately.
    :param tupled_list: list of tuples
    :return: None
    """
    # tuple(map_tags_posts(wp_posts_f, idd='y').values())
    for item in tupled_list:
        yield "".join(str(item)).strip("[']")

def get_post_models(wp_posts_f: list[dict]):
    models = [[" ".join(cls_lst.split('-')[1:]).title() for cls_lst in elem['class_list']
             if re.match("pornstars", cls_lst)] for elem in wp_posts_f]
    return [",".join(model) if len(model)!=0 else None for model in models]

# =========== REPORTS ===========

# This will generate a new .xlsx file in project root.
# CSV output is possible, not very effective, though.
# export_to_csv_nt(tag_master_merger_ntpl(imported_json),
# "sample", ["Title", "Tag ID", "# of Taggings"])
# create_tag_report_excel(imported_json, "tag_report_excel", parent=True)
def create_tag_report_excel(wp_posts_f: list[dict], workbook_name: str, parent: bool = False) -> None:
    """
    As its name points out this function writes the tagging information
    into an Excel .xlsx file
    :param parent: Place the workbook in the parent directory if True, default False.
    :param wp_posts_f: WP Posts json
    :param workbook_name: (str) the workbook name with or without extension.
    :return: None
    """
    workbook_fname = helpers.clean_filename(workbook_name, '.xlsx')
    dir_prefix = helpers.is_parent_dir_required(parent)

    workbook = xlsxwriter.Workbook(f'{dir_prefix}{workbook_fname}')
    # Tag & Tag ID Fields & Videos Tagged
    tag_plus_tid = workbook.add_worksheet(name="Tag Fields & Videos Tagged")

    tag_plus_tid.set_column('A:C', 20)
    tag_plus_tid.set_column('D:E', 90)
    tag_plus_tid.write_row('A1', ("Tag", "Tag ID", "Videos Tagged", "Tagged IDs"))
    tag_plus_tid.write_column('A2', tuple(tag_id_merger_dict(wp_posts_f).keys()))
    tag_plus_tid.write_column('B2', tuple(tag_id_merger_dict(wp_posts_f).values()))
    tag_plus_tid.write_column('C2', tuple(get_tags_num_count(wp_posts_f).values()))
    tag_plus_tid.write_column('D2', unpack_tpl_excel(map_tags_posts(wp_posts_f, idd=True).values()))

    post_id_slug = workbook.add_worksheet(name="Post id & Post Slug")
    post_id_slug.set_column('A:A', 20)
    post_id_slug.set_column('B:B', 80)
    post_id_slug.set_column('C:C', 40)
    post_id_slug.write_row('A1', ("Post ID", "Post Slug", "Post Category"))
    post_id_slug.write_column('A2', tuple(map_posts_by_id(wp_posts_f).keys()))
    post_id_slug.write_column('B2', tuple(map_posts_by_id(wp_posts_f).values()))
    post_id_slug.write_column('C2', unpack_tpl_excel(map_postsid_category(wp_posts_f).values()))

    workbook.close()

    print(f"\nFind the new .xlsx file in \n{helpers.cwd_or_parent_path(parent=parent)}\n")
    return None


def update_published_titles_db(db_name: str, wp_posts_f: list[dict], parent=False):
    db_name = helpers.clean_filename(db_name, '.db')
    db_full_name = f"{helpers.is_parent_dir_required(parent=parent)}{db_name}"
    # SQLite can't overwrite an existing db with the same table.
    helpers.if_exists_remove(db_full_name)
    db = sqlite3.connect(f'{db_full_name}')
    cur = db.cursor()
    cur.execute('CREATE TABLE videos(title, models, wp_slug)')
    vid_slugs = get_slugs(wp_posts_f)
    vid_titles = get_post_titles_local(wp_posts_f)
    vid_models = get_post_models(wp_posts_f)
    for title, models ,slug in zip(vid_titles, vid_models, vid_slugs):
        cur.execute('INSERT INTO videos VALUES (?, ?, ?)',
                    (title, models, slug))
        db.commit()
    db.close()

def upload_thumbnail(wp_self: str, param_lst: list[str], file_path: str, payload: dict):
    client_info_file = helpers.get_client_info('client_info.json', parent=True)
    username_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["username"]
    app_pass_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["app_password"]
    auth_wp = HTTPBasicAuth(username_, app_pass_)
    headers = {"Content-Disposition": f"attachment; filename={file_path}"}
    wp_self: str = wp_self + "".join(param_lst)
    with open(file_path, 'rb') as thumb:
        request = requests.post(wp_self, files={'file': thumb}, auth=auth_wp)
    image_json = request.json()
    return requests.post(wp_self + "/" + str(image_json['id']), json=payload, auth=auth_wp).status_code

# TODO: get_all_categories reuses some code and it does not work as expected.
def get_all_categories(hostname: str, params_dict: dict) -> list[dict]:
    """
    :param hostname: hostname of your WP site.
    :param params_dict: dictionary with the rest parameters in the URL.
    :return: list[dict]
    """
    # Accumulation of dict elements for concatenation.
    result_dict: list[dict] = []
    base_url: str = f"https://{hostname}/wp-json/wp/v2"
    # List of parameters that I intend to concatenate to the base URL.
    # /posts/page=1
    page_num: int = 1
    params_posts: list[str] = [params_dict["posts"]["categories"]]
    page_num_param: bool = False
    print("\nWorking on it...\n")
    while True:
        curl_json: list[dict] = curl_wp_self_concat(base_url, params_posts)
        try:
            if curl_json["data"]["status"] == 400:
                print(f"\n{'DONE':=^30}\n")
                return result_dict
        except TypeError:
            print(f"Processing page #{page_num}")
            page_num += 1
            if page_num_param is False:
                params_posts.append(params_dict["posts"]["page"])
                params_posts.append(str(page_num))
                page_num_param = True
            else:
                params_posts[-1] = str(page_num)
            for item in curl_json:
                result_dict.append(item)

# I want hostname as input()
hstname: str = 'whoresmen.com'
b_url: str = f"https://{hstname}/wp-json/wp/v2"

# It is possible to add more REST parameters.
rest_params: dict = {
    "users": "/users?",
    "posts": {
        "posts_url": "/posts",
        "per_page": "?per_page=",
        "page": "?page=",
        "fields": {"fields_base": "?_fields=",
                   # fields are comma-separated in the URL after the fields_base value.
                   "fields": ["author", "id", "excerpt", "title", "link"]
                   },
        "categories": "/categories"
    },
    "media": "/media",
}

if input("Want to fetch a new copy of the WP Posts JSON file? Y/N: ").lower() == ("y" or "yes"):
    # Modify the params parameter if needed.
    all_posts: list[dict] = get_all_posts(hstname, rest_params)
    # Caching a copy of the request for analysis and performance gain.
    helpers.export_request_json("wp_posts", all_posts, 1, parent=True)
    recent_json: list[dict] = helpers.import_request_json("wp_posts", parent=True)
    update_published_titles_db('WP_all_post_titles', recent_json, parent=True)
else:
    print("Okay, using cached file from now on!\n")
    pass

# Loading local cache
imported_json: list[dict] = helpers.import_request_json("wp_posts", parent=True)

# for num, p in enumerate(posts, start=1) :
#     print(f'{num}. {p}')


# Create the report here. Make sure to uncomment the following:
# create_tag_report_excel(imported_json, "tag_report_excel", parent=True)

# categories = get_all_categories(hstname, rest_params)
# export_request_json('wp_categories', categories, parent=True)

# --> Tests
# create_wp = wp_post_create(b_url, [rest_params['posts']['posts_url']], json_post)
# get_post_titles_local(imported_json)

# ==== WP Posts json data structure ====
# title: imported_json[0]['title']['rendered']
# description: imported_json[0]['content']['rendered']
# tags text and category : imported_json[0]['class_list'] (prefixed with "tag-" and "category-")
# slug: imported_json[0]['slug']
# tag numbers: imported_json[0]['tags'] OK
# link: imported_json[0]['link']
# id: imported_json[0]['id']
# yoast json: imported_json[0]['yoast_head_json'] (can get info without overhead)
# yoast tags without prefix: imported_json[0]['yoast_head_json']['schema']['@graph'][0]['keywords'] OK
# yoast category: imported_json[0]['yoast_head_json']['schema']['@graph'][0]['articleSection']
# =============================
