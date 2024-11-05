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

import argparse
import datetime
import os.path
import re

import requests
import sqlite3
import warnings

from collections import namedtuple
from requests.auth import HTTPBasicAuth
from typing import Generator

# Third-party modules
import xlsxwriter

# Local implementations
from common import helpers, NoSuitableArgument

def curl_wp_self_concat(wp_self: str, param_lst: list[str]) -> requests:
    """Makes the GET request based on the curl mechanism as described on the docs.
    curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/users?context=edit
    In other words: curl --user "USERNAME:PASSWORD" https://HOSTNAME/wp-json/wp/v2/REST_PARAMS

    :param wp_self: (str) wp base url
    :param param_lst: (list -> str) list of URl params
    :return: json object
    """
    client_info_file = helpers.get_client_info('client_info.json')
    username_: str = client_info_file['WordPress']['user_apps']['wordpress_api.py']['username']
    app_pass_: str = client_info_file['WordPress']['user_apps']['wordpress_api.py']['app_password']
    wp_self: str = wp_self + "".join(param_lst)
    return requests.get(wp_self, headers={"user": f"{username_}:{app_pass_}"})


def wp_post_create(wp_self: str, param_lst: list[str], payload):
    """Makes the POST request based on the mechanism as described on the docs.
    :param payload: dictionary with the post information.
    :param wp_self: (str) wp base url
    :param param_lst: (list -> str) list of URl params
    :return: json object
    """
    client_info_file = helpers.get_client_info('client_info')
    username_: str = client_info_file['WordPress']['user_apps']['wordpress_api.py']['username']
    app_pass_: str = client_info_file['WordPress']['user_apps']['wordpress_api.py']['app_password']
    auth_wp = HTTPBasicAuth(username_, app_pass_)
    wp_self: str = wp_self + "".join(param_lst)
    return requests.post(wp_self, json=payload, auth=auth_wp).status_code


def create_wp_local_cache(hostname: str,
                          params_dict: dict[str, str],
                          endpoint: str,
                          wp_filen: str,
                          parent: bool = False) -> list[dict]:
    """ Gets all posts from your WP Site.
    It does this by fetching every page with 10 posts each and concatenating the JSON
    responses to return a single list of dict elements.
    :param parent: True if your config file will be located in parent dir. Default False
    :param wp_filen: File name of your new wp_cache_file
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
    print(f"\nCreating WordPress {helpers.clean_filename(wp_filen, 'json')} cache file...\n")
    while True:
        curl_json = curl_wp_self_concat(base_url, params_posts)
        if curl_json.status_code == 400:
            # Assumes that no config file exists.
            local_cache_config(wp_filen, x_wp_totalpages, x_wp_total)
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


def get_tags_num_count(wp_posts_f: list[dict], photos: bool = False) -> dict:
    """Counts the occurrences of tags, however, this function fetches the tag numbers
    not the actual names. This is necessary to match everything at a later routine.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
    :param photos: True if you want to fetch tags for photo post types. Default False.
    :return: dict
    """
    content = "photos_tag" if photos else "tags"
    tags_nums_count: dict = {}
    for dic in wp_posts_f:
        for tag_num in dic[content]:
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


def get_tags_unique(wp_posts_f: list[dict], pattern: str) -> list[str]:
    """ This function will get the unique occurrences in the `['class_list']` key in the
    wp_posts_f, which is a list of all the individual post dicts.
    :param wp_posts_f: list of all the individual post dicts
                      (it must be loaded by using either the json built-ins or the local helpers api)
    :param pattern: the piece of text that will get the match to gather the keywords.
                    For example, the `['class_list']` will have items like `'tag-colourful-skies'`, where the
                    pattern is `tag`.
    :return: set (ensure uniqueness) coerced into list
    """
    tag_class_list = get_from_class_list(wp_posts_f, pattern)
    unique_tags = []
    for tags in tag_class_list:
        try:
            tag_lst = tags.split(',')
            for tag in tag_lst:
                unique_tags.append(tag)
        except AttributeError:
            continue
    return list(set(unique_tags))


def tag_id_merger_dict(wp_posts_f: list[dict]) -> dict:
    """Returns a dictionary {"tag": "tag-id"} from the output from other functions.
    I am created a NamedTuple function with this information too.

    This function could be used to map tags to their corresponding ids within the WordPress site
    and strongly relies on the order in which the tags are extracted and zipped.
    Be warned that this behaviour could be altered by the ordering in values and consistency is not always
    the norm; that is the reason why this function has been replaced by `get_from_class_list` with a smarter algorithm.
    :param wp_posts_f: List of dicts generated by the get_all_posts function.
    :return: dict
    """
    return {tag: t_id for tag, t_id in zip(get_tag_count(wp_posts_f).keys(),
                                           get_tags_num_count(wp_posts_f).keys())}


def tag_id_count_merger(wp_posts_f: list[dict]) -> list:
    """This function makes a list of namedtuples with fields ['title', 'ID', 'count'] .
    Just like the `tag_id_merger_dict`, the function heavily relies on the order of extraction, which could
    be problematic in some cases. It does not mean these functions do not work, however, there are some
    less-error-prone alternatives in this module.
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
    It comes in handy when you don't want to fetch your keywords using the `['class_list']` key in your post dicts.
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
    """ This function makes a {"Tag": ["post slug", ...]} or {"Tag": ["post id", ...]} dictionary.
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
    Associates post ID with a URL. As many functions, it assumes that your WordPress installation has
    the Yoast SEO plug-in in place.
    :param wp_posts_f: Posts json
    :param host_name: (str) your hostname (Optional param = None)
    :return: dict
    """
    # In the case of KeyError, there is at least one post that hasn't been categorized in WordPress.
    # Check the culprit with the following code if this behaviour is not intended:
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


def unpack_tpl_excel(tupled_list) -> Generator[str, None, None]:
    """ This function was created to write the tuple (by typecast) contents of
    another function into an .xlsx file cell appropriately.
    It was created to address an unwanted behaviour in this line specifically:
    tuple(map_tags_posts(wp_posts_f, idd='y').values()) in the `create_tag_report_excel` function.
    :param tupled_list: list of tuples
    :return: Generator with a YieldType of str
    """
    for item in tupled_list:
        yield "".join(str(item)).strip("[']")


def get_post_models(wp_posts_f: list[dict]) -> list[str]:
    """ This function is based on the same principle as `get unique tags`, however, this is a
        domain specific implementation that is no longer in operation and has been replaced by function
        `get_from_class_list`
    :param wp_posts_f:
    :return: list of model items joined by a comma individually.
             This behaviour is desired because some videos have more than one model item associated with it,
             making it easier for other functions to process these individually and find unique occurrences.
    """
    models = [[" ".join(cls_lst.split('-')[1:]).title() for cls_lst in elem['class_list']
               if re.match("pornstars", cls_lst)] for elem in wp_posts_f]
    return [",".join(model) if len(model) != 0 else None for model in models]


#
def get_post_category(wp_posts_f: list[dict]) -> list[str]:
    """ It assumes that each post has only one category, so that's why I am not joining
        them with commas within the return list comprehension.
        This is a domain specific implementation for categories.
        If you have more than one category, you can use the `get_from_class_list` with 'category'
        as the pattern parameter.
    :param wp_posts_f:
    :return: list of str
    """
    categories = [[" ".join(cls_lst.split('-')[1:]).title() for cls_lst in elem['class_list']
                   if re.match("category", cls_lst)] for elem in wp_posts_f]
    return [category[0] for category in categories]


def get_from_class_list(wp_posts_f: list[dict], pattern: str) -> list[str]:
    """ Gets keywords from a post dictionary that WordPress prefixes with a specific pattern.
    For example, the value `tag-colourful-skies` will be matched via a pattern, in this case `tag`,
    and cleaned for further processing, so the result is a cleaned keyword in title case (`Colourful Skies`).
    :param wp_posts_f: list of post dictionaries (previously loaded in the program)
    :param pattern: pattern prefix
    :return: list of str individually joined by a comma as different posts have a unique
             keyword combination.
    """
    class_list = [[" ".join(cls_lst.split('-')[1:]).title() for cls_lst in elem['class_list']
                   if re.match(pattern, cls_lst)] for elem in wp_posts_f]
    return [",".join(item) if len(item) != 0 else None for item in class_list]


def get_post_descriptions(wp_posts_f: list[dict], yoast: bool = False) -> list[str]:
    """ As the name indicates, it extracts the WordPress descriptions or commonly called `excerpts` from the
        list of post dictionaries (wp_post_f). It allows for Yoast SEO integration since excerpts can contain
        unwanted HTML entities.
    :param wp_posts_f: list of dict
    :param yoast: True if you want to match Yoast descriptions. Default False.
    :return: list of str (post excerpts)
    """
    if yoast:
        return [item['yoast_head_json']['description'] for item in wp_posts_f]
    else:
        return [item['excerpt']['rendered'].strip('\n').strip('<p>').strip('</p>')
                for item in wp_posts_f]


def map_wp_class_id(wp_posts_f: list[dict], match_word: str, key_wp: str) -> dict:
    """
    This function parses the wp_posts or wp_photos JSON files to locate and map tags or other
    keywords (e.g. models) that WordPress includes in the `class_list` key.
    `map_wp_class_id` is used extensively to match tags, model, photo tag, and category items with the
    intention to pair them with an ID within the WordPress site.
    A way to fully understand why we need a match and a key parameter is the following:
    `tag-colourful-skies` have an associated integer value of 123. `map_wp_class_id` has to identify the
    keyword and its numeric value contained in different lists; match_word deals with the former by applying
    pattern matching on `tag-colourful-skies` to extract the keyword in title case without the prefix.
    On the other hand, key_wp obtains its numeric value 123, so that both can be paired in a key-value structure (dict).

    Examples of matching parameters (str):

    -> models:
        match_word = `'pornstars'`
        key_wp = `'pornstars'`
    -> tags:
        match_word = `'tag'`
        key_wp = `'tags'`
    -> photo tags:
        match_word = `'photo_tag'`
        key_wp = `'photo_tag'`
    -> categories:
        match_word = `'category'`
        key_wp = `'categories'`

    :param wp_posts_f: the wp_posts or wp_photos files previously loaded in the program.
    :param match_word: the prefix of the keywords that you want to match.
    :param key_wp: dict key where the numeric values are located.
    :return: dict {keyword: associated numeric value}
    """
    result_dict = {}
    for elem in wp_posts_f:
        kw = [" ".join(item.split('-')[1:]).title() for item in elem['class_list']
              if re.findall(match_word, item)]
        model_ids = elem[key_wp]
        for item in zip(kw, model_ids):
            (name, wp_id) = item
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
    # Tag & Tag ID Fields, Videos Tagged, Video IDs.
    tag_plus_tid = workbook.add_worksheet(name="Tag Fields & Videos Tagged")

    tag_plus_tid.set_column('A:C', 20)
    tag_plus_tid.set_column('D:E', 90)
    tag_plus_tid.write_row('A1', ("Tag", "Tag ID", "Videos Tagged", "Tagged IDs"))
    tag_plus_tid.write_column('A2', tuple(tag_id_merger_dict(wp_posts_f).keys()))
    tag_plus_tid.write_column('B2', tuple(tag_id_merger_dict(wp_posts_f).values()))
    tag_plus_tid.write_column('C2', tuple(get_tags_num_count(wp_posts_f).values()))
    tag_plus_tid.write_column('D2', unpack_tpl_excel(map_tags_posts(wp_posts_f, idd=True).values()))

    # Post ID & Post Slug on WordPress
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
                               yoast: bool = False) -> None:
    """ Creates a SQLite db based on the wp_post_f that will be used by other modules to
        compare information in a different format. Sometimes, titles and descriptions can't be matched by
        the built-in RegEx module in Python due to character sets or encodings present in different pieces of
        information extracted from WordPress. This is where, by having a db, we can conduct simple comparison
        operations without pattern matching.
    :param db_name: self-explanatory
    :param wp_posts_f: As detailed in several places, this is a list of dicts comprised of post dicts.
    :param parent: True if you want to place your database in the parent directory. Default False
    :param photosets: True if you want to build a photoset db. Default False
    :param yoast: True if you have Yoast SEO plugin and want to increase accuracy, which is useful
                  when fiels have unwanted HTML entities. Default False
    :return: None (Database file in working or parent directory)
    """
    db_name = helpers.clean_filename(db_name, '.db')
    db_full_name = f"{helpers.is_parent_dir_required(parent=parent)}{db_name}"
    # SQLite3 can't overwrite an existing db with the same table.
    helpers.remove_if_exists(db_full_name)
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


def upload_thumbnail(wp_self: str, param_lst: list[str], file_path: str, payload: dict) -> int:
    """ Uploads video thumbnail or any other image as a WordPress media attachment.
    :param wp_self: This is the base URL from your WP site (where your site is hosted)
    :param param_lst: Typically the '/media' endpoint. In this module, you can get this endpoint from the global
                      rest_params dict. It takes a list because the function will join all the parameters to complete
                      the post request.

    :param file_path: This can be an absolute or relative path to your image attachment.
    :param payload: dictionary with image attributes like ALT text, Description and Caption.
    :return: Integer number that represents the status code of the request.
             In this function, we deal with a possible `KeyError` exception, which is raised by different factors:
             1. Upload Failure: successful connection with the REST API, incorrect parameters.
             2. Incorrect file/MIME Type: WordPress API supports JPEG, PNG, GIF, ICO, BMP, TIFF, WEbP with their
                corresponding extensions by default.
                The supported file/MIME types can be extended via custom functions or plugins.
            3. Defective file: Let's say that you have a `.jpg` that was not downloaded correctly and, therefore,
               rendering its contents is not possible.
            5. Server/gateway errors: It is possible that your server is experiencing a high workload or
               something that could be causing 500 error codes.

            In all scenarios, the image was not uploaded and the dict contains debugging output that is not
            associated with the `['id']` key of the JSON response file, thus raising a `KeyError` exception.
            The function returns the request status code for further handling and debugging.
    """
    client_info_file = helpers.get_client_info('client_info.json')
    username_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["username"]
    app_pass_: str = client_info_file["WordPress"]["user_apps"]["wordpress_api.py"]["app_password"]
    auth_wp = HTTPBasicAuth(username_, app_pass_)
    # headers = {"Content-Disposition": f"attachment; filename={file_path}"}
    wp_self: str = wp_self + "".join(param_lst)
    with open(file_path, 'rb') as thumb:
        request = requests.post(wp_self, files={'file': thumb}, auth=auth_wp)
    try:
        image_json = request.json()
        return requests.post(wp_self + "/" + str(image_json['id']),
                             json=payload, auth=auth_wp).status_code
    except KeyError:
        return request.status_code


def local_cache_config(wp_filen: str, wp_curr_page: int, total_posts: int) -> str:
    """ Creates a new config file and locates existing local cache configuration files to update its contents
        with new information about cached pages, post quantity, and date of update.
    :param wp_filen: Name of the current WordPress Post/Photo file to link the file
                        with its corresponding configuration
    :param wp_curr_page: Last cached page
    :param total_posts: self-explanatory, obtained from another function.
    :return: Function with a return type of str.
    """
    wp_cache_filename = 'wp_cache_config.json'
    wp_filen = helpers.clean_filename(wp_filen, '.json')
    parent = False if os.path.exists(f'./{wp_cache_filename}') else True
    locate_conf = helpers.search_files_by_ext('.json', '', parent=parent)
    create_new = [{
        wp_filen: {
            'cached_pages': wp_curr_page,
            'total_posts': total_posts,
            'last_updated': str(datetime.date.today())
        }
    }]
    if wp_cache_filename in locate_conf:
        existing_file = helpers.load_json_ctx(wp_cache_filename)
        for item in existing_file:
            item.update({wp_filen: {
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


def update_json_cache(hostname: str, params_dict: dict, endpoint: str, config_dict: list[dict], wp_filen: str) -> list[dict]:
    """ Updates the local wp cache files for processing.
    It does this by fetching the last page cached and calculating the
    difference between the total elements variable from the HTTP request and
    the reported items in the local configuration file.
    :param wp_filen: Where you stored your cached WordPress post data.
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
    clean_fname = helpers.clean_filename(wp_filen, '.json')
    # The loop will add 1 to page num when the first request is successful.
    page_num = [dic[clean_fname]['cached_pages'] for dic in config
                if clean_fname in dic.keys()][0] - 2
    result_dict = helpers.load_json_ctx(wp_filen)
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
            local_cache_config(wp_filen, page_num, x_wp_total)
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
                           parent: bool = False,
                           yoast: bool = False) -> None:
    """ Updates both the WP post information JSON file (posts and photos) and creates a SQLite database
        using the cached files.
    :param hostname: Base url (WP Self)
    :param params_dict: Dictionary of parameters (rest_params) that helping functions will parse and use.
    :param endpoint: params_dict key that describes the type of post that you want to cache, just the key str.
    :param wp_filename: Desired filename for your cached file.
    :param wp_db_name: Desired filename for your cached database.
    :param cached: Update db and config files with cached data.
           If set to `True`, the cache and config files will be rebuilt.
    :param parent: True if you want to place both your config and post info JSON files in the parent dir.
                   Default False
    :param yoast: Enable the Yoast SEO metadata for the published titles db. Default False.
    :return: None (Creates and modifies files in either parent or current working directories)
             -> Note: This function will create the file that most functions in this module will use: wp_posts_f
             make sure to load the appropriate file with the JSON built-in functions or the local helpers API.
             For example: `imported_json: list[dict] = helpers.load_json_ctx("wp_posts", parent=True)`
    """
    l_config = helpers.load_json_ctx('wp_cache_config.json')
    if cached:
        updated_local_cache = update_json_cache(hostname, params_dict, endpoint, l_config, wp_filename)

    else:
        updated_local_cache = create_wp_local_cache(hostname,
                                                    params_dict,
                                                    endpoint,
                                                    wp_filename,
                                                    parent=parent)

    helpers.export_request_json(wp_filename, updated_local_cache, 1, parent=parent)
    local_json: list[dict] = helpers.load_json_ctx(wp_filename)
    update_published_titles_db(wp_db_name, local_json, parent=parent, yoast=yoast)
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

    # Suppress RuntimeWarnings during import
    warnings.filterwarnings("ignore", category=RuntimeWarning,
                            message=".*found in sys.modules after import of package.*")

    args_parser = argparse.ArgumentParser(description='WordPress API Local Module')

    args_parser.add_argument('--cached', action='store_true',
                      help="""Select this flag if you already have a cached copy of your JSON file.
                      In case you need to recreate your config files, database or JSON files use do not set this flag. 
                      Using this flag will allow you to recreate the config and database with cached data.""")


    args_parser.add_argument('--parent', action='store_true',
                      help='Place the output of these functions in the relative parent directory.')

    args_parser.add_argument('--posts', action='store_true',
                             help='Update the wp_posts local cache or associated files (db/config).')

    args_parser.add_argument('--photos', action='store_true',
                             help='Update the wp_photos local cache or associated files (db/config).')

    args = args_parser.parse_args()

    # Standardizing db names for consistency
    DB_NAME_POSTS = f'wp-posts-{datetime.date.today()}'
    DB_NAME_PHOTOS = f'wp-photos-{datetime.date.today()}'

    CACHE_NAME_POSTS = 'wp_posts'
    CACHE_NAME_PHOTOS = 'wp_photos'

    if args.posts:
        endpoint_key = 'posts_url'
        wp_filename = CACHE_NAME_POSTS
        wp_db_name = DB_NAME_POSTS

    elif args.photos:
        endpoint_key = 'photos'
        wp_filename = CACHE_NAME_PHOTOS
        wp_db_name = DB_NAME_PHOTOS

    else:
        program_name = __file__.split('/')[-1:][0]
        raise NoSuitableArgument(f"No arguments have been provided. Run {program_name} --help for options.")

    upgrade_wp_local_cache(hstname,
                           rest_params,
                           endpoint_key,
                           wp_filename,
                           wp_db_name,
                           cached=args.cached,
                           parent=args.parent,
                           yoast=True)

    # Loading local cache
    # imported_json: list[dict] = helpers.load_json_ctx("wp_posts", parent=True)
    # wp_post_len: int = len(imported_json)

    # Create the report here. Make sure to uncomment the following:
    # create_tag_report_excel(imported_json, "tag_report_excel", parent=True)

    # categories = get_all_categories(hstname, rest_params)
    # export_request_json('wp_categories', categories, parent=True)

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
