"""
This module connects to the WordPress API to gather information
and streamline data analysis and other processes.
It specialises in the handling and filtering of WordPress Post information,
managing local caching and reporting of an active site.

It was created with the notion of the perfect assistant to keep a site clean and
derive insights based on multiple data extraction methods developed here.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
 
"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

import datetime
import pprint
import re

import requests
import sqlite3
from collections import namedtuple

from requests.auth import HTTPBasicAuth

# Third-party modules
import xlsxwriter

# Local implementations
import helpers


def curl_wp_self_concat(wp_self: str, param_lst: list[str]) -> requests:
    """Makes the GET request based on the curl mechanism as described on the docs.
    curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/users?context=edit
    In other words: curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/REST_PARAMS

    :param wp_self: (str) wp base url
    :param param_lst: (list -> str) list of URl params
    :return: json object
    """
    client_info_file = helpers.get_client_info('client_info.json', parent=True)
    username_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["username"]
    app_pass_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["app_password"]
    wp_self: str = wp_self + "".join(param_lst)
    return requests.get(wp_self, headers={"user": f"{username_}:{app_pass_}"})


def wp_post_create(wp_self: str, param_lst: list[str], payload):
    """Makes the POST request based on the mechanism as described on the docs.
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


def create_wp_local_cache(hostname: str,
                          params_dict: dict[str, str],
                          endpoint: str,
                          wp_filename: str,
                          parent: bool = False) -> list[dict]:
    """ Gets all posts from your WP Site.
    It does this by fetching every page with 10 posts each and concatenating the JSON
    responses to return a single list of dict elements.
    :param parent: True if your config file will be located in parent dir. Default False
    :param wp_filename: File name of your new wp_cache_file
    :param endpoint: endpoint key within the params dict.
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
    x_wp_total = 0
    x_wp_totalpages = 0
    params_posts: list[str] = [params_dict["posts"][endpoint]]
    page_num_param: bool = False
    print(f"\nCreating WordPress {helpers.clean_filename(wp_filename, 'json')} cache file...\n")
    while True:
        curl_json = curl_wp_self_concat(base_url, params_posts)
        if curl_json.status_code == 400:
            # Assumes that no config file exists.
            local_cache_config(wp_filename,
                               x_wp_totalpages,
                               x_wp_total,
                               parent=parent)
            print(f"\n{'DONE':=^30}\n")
            return result_dict
        else:
            print(f"--> Processing page #{page_num}")
            page_num += 1
            if page_num_param is False:
                headers = curl_json.headers
                x_wp_total += int(headers['x-wp-total'])
                x_wp_totalpages += int(headers['x-wp-totalpages'])
                params_posts.append(params_dict['posts']['page'])
                params_posts.append(str(page_num))
                page_num_param = True
            else:
                params_posts[-1] = str(page_num)
            for item in curl_json.json():
                result_dict.append(item)


# Note:
# Tags and its IDs are repeated and must be isolated
# to count for the unique elements in each dictionary and merge them.


def get_tags_num_count(wp_posts_f: list[dict]) -> dict:
    """Counts the occurrences of tags, however, this function fetches the tag numbers
    not the actual names. This is necessary to match everything at a later routine.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
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
    """ As its name describes, this function gets the slugs from the
    WP post file or dict.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
    :return: list[str]
    """
    return [url['slug'] for url in wp_posts_f]


def tag_id_merger_dict(wp_posts_f: list[dict]) -> dict:
    """Returns a dictionary {"tag": "tag-id"} from the output from other functions.
    I am created a NamedTuple with this information. However, I want to leave this
    dictionary function, just in case.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
    :return: dict
    """
    return {tag: t_id for tag, t_id in zip(get_tag_count(wp_posts_f).keys(),
                                           get_tags_num_count(wp_posts_f).keys())}


# TODO: Code reuse, map unique keys and count or aggregate info.

# Note:
# Ideally, I want an ordered data structure that combines tag name, id, and count.


def tag_id_count_merger(wp_posts_f: list[dict]) -> list:
    """This function makes a list of namedtuples with fields ['title', 'ID', 'count'] .
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
    :return: List[namedTuple, ...]
   """
    tag_id_merger = zip(get_tag_count(wp_posts_f).keys(),
                        get_tags_num_count(wp_posts_f).keys(), get_tag_count(wp_posts_f).values())
    Tag_ID_Count = namedtuple("WP_Tags", ['title', 'ID', 'count'])
    cooked = [Tag_ID_Count(title, ids, count) for title, ids, count in tag_id_merger]
    return cooked


def get_tag_id_pairs(wp_posts_f: list[dict]) -> dict:
    """ This function makes a {"tag": ["post id", ...]} dictionary.
    Again, this function assumes that you have the Yoast SEO plugin in your installation.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
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


def get_post_titles_local(wp_posts_f: list[dict], yoast: bool = False) -> list[str]:
    """ Gets a list of all post titles from wp_posts_f. This function is different to others
    because it can extract data from the Yoast SEO plugin element, however, it does work
    without it by giving you the rendered title instead.
    To activate the "Yoast" mode, just set the optional parameter to True.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
    :param yoast: optional Yoast mode parameter.
    :return: list[str]
    """
    all_titles = []
    for post in wp_posts_f:
        if yoast:
            all_titles.append(" ".join(post['yoast_head_json']['title'].split(" ")[:-2]))
        else:
            all_titles.append(post['title']['rendered'])
    return all_titles


def get_tag_count(wp_posts_f: list[dict]) -> dict:
    """Counts every occurrence of a tag in the entire posts json file.
    This function assumes that the Yoast SEO plugin is running in your WordPress installation.
    Why? Because some information is easier to extract from the Yoast head JSON key.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
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


def map_posts_by_id(wp_posts_f: list[dict], host_name=None) -> dict:
    """Maps post ID to a slug. In WordPress, every post and even field has an ID.
    In this case, this function just maps the slug with the post ID.
    If you set host_name to True, the function will give you the hostname + post slug
    in every iteration, otherwise it will give you the slug only by default.
    :param wp_posts_f: Posts json
    :param host_name: (str) your hostname/WP site base URL (Optional param = None)
    :return: dict
    """
    u_pack = zip([idd['id'] for idd in wp_posts_f],
                 [url['slug'] for url in wp_posts_f])
    if host_name is not None:
        # if the user specifies a hostname with another TLD, .com will not be used!
        # clean_filename has a "trust" mode.
        return {idd: f"{helpers.clean_filename(host_name, 'com')}/" + url
                for idd, url in u_pack}
    else:
        return {idd: url for idd, url in u_pack}


def map_tags_post_urls(wp_posts_f: list[dict], host_name=None) -> dict:
    """This function makes a {"Tag": ["post slug", ...]} dictionary.
    For example, {"some_tag": ["a-post-somewhere-in-wp", ...]}

    If you set host_name to True, the slugs will be 'wpsite.com/a-post-somewhere-in-wp'
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
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
    return [",".join(model) if len(model) != 0 else None for model in models]


# It assumes that each post has only one category, so that's why I am not join
# them with commas with a list comprehension.
def get_post_category(wp_posts_f: list[dict]):
    categories = [[" ".join(cls_lst.split('-')[1:]).title() for cls_lst in elem['class_list']
                   if re.match("category", cls_lst)] for elem in wp_posts_f]
    return [category[0] for category in categories]


def get_post_descriptions(wp_posts_f: list[dict], yoast: bool = False):
    if yoast:
        return [item['yoast_head_json']['description'] for item in wp_posts_f]
    else:
        return [item['excerpt']['rendered'].strip('\n').strip('<p>').strip('</p>')
                for item in wp_posts_f]


def map_wp_model_id(wp_posts_f: list[dict], match_word: str, key_wp: str) -> dict:
    result_dict = {}
    for elem in wp_posts_f:
        kw = [" ".join(model.split('-')[1:]).title() for model in elem['class_list']
              if re.findall(match_word, model)]
        model_ids = elem[key_wp]
        for model in zip(kw, model_ids):
            (name, wp_id) = model
            if name not in result_dict.keys():
                result_dict[name] = wp_id
            else:
                continue
    return result_dict


# CSV output is possible, not very effective, though.
# export_to_csv_nt(tag_master_merger_ntpl(imported_json),
# "sample", ["Title", "Tag ID", "# of Taggings"])


def create_tag_report_excel(wp_posts_f: list[dict],
                            workbook_name: str, parent: bool = False) -> None:
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


def update_published_titles_db(db_name: str,
                               wp_posts_f: list[dict],
                               parent: bool = False,
                               photosets: bool = False,
                               yoast: bool = False):
    db_name = helpers.clean_filename(db_name, '.db')
    db_full_name = f"{helpers.is_parent_dir_required(parent=parent)}{db_name}"
    # SQLite3 can't overwrite an existing db with the same table.
    helpers.if_exists_remove(db_full_name)
    db = sqlite3.connect(db_full_name)
    cur = db.cursor()
    if photosets:
        cur.execute('CREATE TABLE sets(title, model, wp_slug)')
        vid_slugs = get_slugs(wp_posts_f)
        vid_titles = get_post_titles_local(wp_posts_f, yoast=yoast)
        for title, slug in zip(vid_titles, vid_slugs):
            model = title.split(" ")[0]
            cur.execute('INSERT INTO sets VALUES (?, ?, ?)',
                        (title.title(), model, slug))
            db.commit()
    else:
        cur.execute('CREATE TABLE videos(title, models, wp_slug)')
        vid_slugs = get_slugs(wp_posts_f)
        vid_titles = get_post_titles_local(wp_posts_f)
        vid_models = get_post_models(wp_posts_f)
        for title, models, slug in zip(vid_titles, vid_models, vid_slugs):
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
    try:
        image_json = request.json()
        return requests.post(wp_self + "/" + str(image_json['id']),
                             json=payload, auth=auth_wp).status_code
    except KeyError:
        return request.status_code


def local_cache_config(wp_filename: str,
                       wp_curr_page: int,
                       total_posts: int,
                       parent: bool = False) -> str:
    wp_cache_filename = 'wp_cache_config.json'
    wp_filename = helpers.clean_filename(wp_filename, '.json')
    locate_conf = helpers.search_files_by_ext('.json', '', parent=parent)
    create_new = [{
        wp_filename: {
            'cached_pages': wp_curr_page,
            'total_posts': total_posts,
            'last_updated': str(datetime.date.today())
        }
    }]
    if wp_cache_filename in locate_conf:
        existing_file = helpers.load_json_ctx(wp_cache_filename, parent=parent)
        for item in existing_file:
            item.update({wp_filename: {
                'cached_pages': wp_curr_page,
                'total_posts': total_posts,
                'last_updated': str(datetime.date.today())
            }})

        return helpers.export_request_json(wp_cache_filename,
                                           existing_file,
                                           indent=2,
                                           parent=parent)
    else:
        return helpers.export_request_json(wp_cache_filename,
                                           create_new,
                                           indent=2,
                                           parent=parent)


def update_json_cache(hostname: str,
                      params_dict: dict,
                      endpoint: str,
                      config_dict: list[dict],
                      wp_filename: str,
                      parent: bool = False) -> list[dict]:
    """ Updates the local wp cache files for processing.
    It does this by fetching the last page cached and calculating the
    difference between the total elements variable from the HTTP request and
    the reported items in the local configuration file.
    :param parent: True if the config and cache files are in the parent dir.
    :param wp_filename: Where you stored your cached WordPress post data.
    :param config_dict: Configuration file in JSON format (loaded as dict) .
    :param endpoint: Endpoint key within the params dict.
    :param hostname: Hostname of your WP site.
    :param params_dict: Dictionary with the rest parameters in the URL.
    :return: list[dict]
    """
    config = config_dict
    base_url: str = f"https://{hostname}/wp-json/wp/v2"
    # List of parameters that I intend to concatenate to the base URL.
    # /posts/page=1
    params_posts: list[str] = [params_dict["posts"][endpoint]]
    x_wp_total = 0
    x_wp_totalpages = 0
    clean_fname = helpers.clean_filename(wp_filename, '.json')
    # The loop will add 1 to page num when the first request is successful.
    page_num = [dic[clean_fname]['cached_pages'] for dic in config
                if clean_fname in dic.keys()][0] - 2
    result_dict = helpers.load_json_ctx(wp_filename, parent=parent)
    total_elems = len(result_dict)
    recent_posts: list[dict] = []
    page_num_param: bool = False
    while True:
        curl_json = curl_wp_self_concat(base_url, params_posts)
        if curl_json.status_code == 400:
            diff = x_wp_total - total_elems
            if diff == 0:
                pass
            else:
                add_list = recent_posts[:diff]
                add_list.reverse()
                for recent in add_list:
                    result_dict.insert(0, recent)
            local_cache_config(wp_filename,
                               page_num,
                               x_wp_total,
                               parent=parent)
            return result_dict
        else:
            page_num += 1
            if page_num_param is False:
                headers = curl_json.headers
                x_wp_total += int(headers['x-wp-total'])
                x_wp_totalpages += int(headers['x-wp-totalpages'])
                params_posts.append(params_dict['posts']['page'])
                params_posts.append(str(page_num))
                page_num_param = True
            else:
                params_posts[-1] = str(page_num)
            for item in curl_json.json():
                if item not in result_dict:
                    recent_posts.append(item)
                else:
                    continue

def upgrade_wp_local_cache(hostname: str,
                           params_dict: dict,
                           endpoint: str,
                           wp_filename: str,
                           wp_db_name: str,
                           cached: bool = False,
                           parent: bool = False) -> None:
    l_config = helpers.load_json_ctx('wp_cache_config.json', parent=parent)
    if cached:
        updated_local_cache = update_json_cache(hostname,
                                                params_dict,
                                                endpoint,
                                                l_config,
                                                wp_filename,
                                                parent=True)

    else:
        updated_local_cache = create_wp_local_cache(hostname,
                                                    params_dict,
                                                    endpoint,
                                                    wp_filename,
                                                    parent=True)

    helpers.export_request_json(wp_filename, updated_local_cache, 1, parent=parent)
    local_json: list[dict] = helpers.load_json_ctx(wp_filename, parent=True)
    update_published_titles_db(wp_db_name, local_json, parent=True, yoast=True)
    return None


# I want hostname as input()
hstname: str = 'whoresmen.com'
b_url: str = f"https://{hstname}/wp-json/wp/v2"

# It is possible to add more REST parameters.
rest_params: dict = {
    "users": "/users?",
    "posts": {
        "posts_url": "/posts",
        "photos": "/photos",
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


if __name__ == '__main__':
    if input("Do you want to update your WP Posts JSON file? Y/N: ").lower() == ("y" or "yes"):
        # Modify the params parameter if needed.
        upgrade_wp_local_cache(hstname,
                               rest_params,
                               'posts_url',
                               'wp_posts',
                               'WP_all_post_titles',
                               cached=True,
                               parent=True)

        upgrade_wp_local_cache(hstname,
                               rest_params,
                               'photos',
                               'wp_photos',
                               'WP_all_photo_sets',
                               cached=False,
                               parent=True)

    else:
        print("Okay, using cached files from now on!\n")
        pass

    # Loading local cache
    imported_json: list[dict] = helpers.load_json_ctx("wp_posts", parent=True)
    # wp_post_len: int = len(imported_json)

    # Create the report here. Make sure to uncomment the following:
    # create_tag_report_excel(imported_json, "tag_report_excel", parent=True)

    # categories = get_all_categories(hstname, rest_params)
    # export_request_json('wp_categories', categories, parent=True)

    # pprint.pprint(map_class_list_id(imported_json, 'category', 'categories'))
    # pprint.pprint(map_wp_model_id(imported_json, 'pornstars', 'pornstars'))

    # print(get_post_descriptions(imported_json, yoast=True))

    # ==== WP Posts json data structure ====
    # title: imported_json[0]['title']['rendered']
    # description: imported_json[0]['content']['rendered']
    # tags text, category, and models: imported_json[0]['class_list'] (prefixed with "tag-" and "category-")
    # slug: imported_json[0]['slug']
    # tag numbers: imported_json[0]['tags'] OK
    # link: imported_json[0]['link']
    # id: imported_json[0]['id']
    # yoast json: imported_json[0]['yoast_head_json'] (can get info without overhead)
    # yoast tags without prefix: imported_json[0]['yoast_head_json']['schema']['@graph'][0]['keywords'] OK
    # yoast category: imported_json[0]['yoast_head_json']['schema']['@graph'][0]['articleSection']
    # =============================