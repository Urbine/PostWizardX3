"""
content_select is the biggest of three bots that streamline the content upload and
integration of content in my WordPress site.

It is able to identify the data sources dynamically and serve as an assistant powered
by several local integrations, being one of those the ``integrations.wordpress_api`` implementation.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

import argparse
import os
from sqlite3 import Connection, Cursor

import pyclip
import random
import re
import requests
import time
import sqlite3
import warnings

from requests.exceptions import ConnectionError, SSLError

# Local implementations
from core import (helpers,
                  InvalidInput,
                  UnsupportedParameter,
                  CONTENT_SEL_CONF,
                  WP_CLIENT_INFO, clean_filename)

from core.config_mgr import WPAuth, ContentSelectConf, GallerySelectConf, EmbedAssistConf
from integrations import wordpress_api
from integrations.url_builder import WPEndpoints
from ml_engine import classify_title, classify_description


def clean_partner_tag(partner_tag: str) -> str:
    """ Clean partner names that could contain apostrophes in them.

    :param partner_tag: ``str`` the conflicting text
    :return: ``str`` cleaned partner tag without the apostrophe.
    """
    # This expression means "not a word and underscore"
    try:
        no_word: list[str] = re.findall(
            r"[\W_]", partner_tag, flags=re.IGNORECASE)
        if no_word[0] == " " and len(no_word) == 1:
            return partner_tag
        elif "'" not in no_word:
            return partner_tag
        else:
            split_char: str = no_word[1] if len(no_word) > 1 else no_word[0]
            return "".join(partner_tag.split(split_char))
    except IndexError:
        return partner_tag


def published(table: str, title: str, field: str, db_cursor: sqlite3) -> bool:
    """In order to come up with a way to know if a certain title has been published,
    I need to try a request and see whether there is any results. This is what the function
    published does, it returns True if there is any result or False if there isn't any.

    The logic is designed to be treated in a natural way ``if not published`` or ``if published.``
    However, with the introduction of the ``JSON`` file filtering, this mechanism that identifies published
    titles has been retired and greatly improved.

    :param table: ``str``` SQL table according to your database schema.
    :param title: ``str`` value you want to look up in the db.
    :param field: ``str`` table field you want to use for the search.
    :param db_cursor: ``sqlite3`` database connection cursor.
    :return: ``boolean`` True if one or more results are retrieved, False if the list is empty.
    """
    search_vids: str = f"SELECT * FROM {table} WHERE {field}='{title}'"
    if db_cursor.execute(search_vids).fetchall():
        return True
    else:
        return False


def published_json(title: str, wp_posts_f: list[dict[str, ...]]) -> bool:
    """This function leverages the power of a local implementation that specialises
    in getting, manipulating, and filtering WordPress API post information in JSON format.
    After getting the posts from the local cache, the function filters each element using
    the ``re`` module to find matches to the title passed in as a parameter. After all that work,
    the function returns a boolean; True if the title was found and that just suggests
    that such a title is already published, or there is a post with the same title.

    Ideally, we can benefit from a different and more accurate filter for this purpose, however,
    it is important for the objectives of this project that all post titles are unique and that, inevitably,
    delimits the purpose and approach of this method. For now, this behaviour of title-only matching is desirable.

    :param title: ``str`` lookup term, in this case a ``title``
    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :return: ``bool`` True if one or more matches is found, False if the result is None.
    """
    post_titles: list[str] = wordpress_api.get_post_titles_local(
        wp_posts_f, yoast=True)

    comp_title: re.Pattern = re.compile(fr'({title})')

    results: list[str] = [
        vid_name for vid_name in post_titles if re.match(comp_title, vid_name)
    ]
    if len(results) >= 1:
        return True
    else:
        return False


def filter_published(all_videos: list[tuple],
                     wp_posts_f: list[dict]) -> list[tuple[str, ...]]:
    """ ``filter_published`` does its filtering work based on the ``published_json`` function.
    Actually, the ``published_json`` is the brain behind this function and the reason why I decided to
    separate brain and body, as it were, is modularity. I want to be able to modify the classification rationale
    without affecting the way in which iterations are performed, unless I intend to do so specifically.
    If this function fails, then I have an easier time to identify the culprit.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles that will be taken into consideration by the ``video_upload_pilot`` (later) for their suggestion and publication.

    :param all_videos: ``List[tuple]`` usually resulting from the SQL database query values.
    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :return: ``list[tuple]`` with the new filtered values.
    """
    # This loop gets the items I am interested in.
    not_published: list[tuple] = []
    for elem in all_videos:
        (title, *fields) = elem
        if published_json(title, wp_posts_f):
            continue
        else:
            not_published.append(elem)
    return not_published


def get_tag_ids(wp_posts_f: list[dict],
                tag_lst: list[str], preset: str) -> list[int]:
    """WordPress uses integers to identify several elements that posts share like models or tags.
    This function is equipped to deal with inconsistencies that are inherent to the way that WP
    handles its tags; for example, some tags can have the same meaning but differ in case.
    Most of my input will be lowercase tags that must be matched to analogous ones differing in case.
    As I want to avoid tag duplicity and URL proliferation in our site, I will use the same IDs for tags
    with a case difference but same in meaning. That's why this function gets a fullmatch with the help of
    the Python RegEx module, and it is instructed to ignore the case of occurrences.

    WordPress handles tag string input the same way; for example, if I write the tag 'mature' into the tags
    textarea in the browser, it maps it to the previously recorded 'Mature' tag, so theoretically and,
    as a matter of fact,'mature' and 'Mature' map to the same tag ID within the WordPress site.

    Another important feature of this function is the implementation of a set comprehension that I later
    coerce into a list. A set will make sure I get unique IDs since any duplicated input in the post payload
    could yield a failed status code or, ultimately, cause problems in post and URL management.
    This is just a preventive measure since, in theory, it is unlikely that we get two matches for the same tag
    simply because I am narrowing the ambiguities down by using pattern matching and telling it to ignore the case.
    Finally, the function will return a reversed list of integers.
    In order words, if you pass ``[foo, bar, python]`` , you will get ``[3, 2, 1]`` instead of ``[1, 2, 3]``.
    This reverse order is not important because you can send tags in any order and
    WordPress will sort them for you automatically, it always does (thankfully).

    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :param tag_lst: ``list[str]`` a list of tags
    :param preset: as this function is used for three terms, the presets supported are
           ``models``,  ``tags``, ``photos`` and ``categories``
    :return: ``list[int]``
    """
    match preset:
        case "models":
            preset = ("pornstars", "pornstars")
        case "tags":
            preset = ("tag", "tags")
        case "photos":
            preset = ("photos_tag", "photos_tag")
        case "categories":
            preset = ("category", "categories")
        case _ as err:
            raise UnsupportedParameter(err)

    tag_tracking: dict[str, int] = wordpress_api.map_wp_class_id(
        wp_posts_f, preset[0], preset[1]
    )
    # I will match them with Regex here to avoid touching the datasource.
    matched_keys: list[str] = [
        wptag
        for wptag in tag_tracking.keys()
        for tag in tag_lst
        if re.fullmatch(tag, wptag, flags=re.IGNORECASE)
    ]
    # The function will return a reversed list of matches.
    return list({tag_tracking[tag] for tag in matched_keys})


def get_model_ids(wp_posts_f: list[dict], model_lst: list[str]) -> list[int]:
    """This function is crucial to obtain the WordPress element ID ``model`` to be able
    to communicate and tell WordPress what we want. It takes in a list of model names and filters
    through the entire WP dataset to locate their ID and return it back to the controlling function.
    None if the value is not found in the dataset.
    This function enforces Title case in matches since models are people and proper names are generally
    in title case, and it is also the case in the data structure that local module ``integrations.wordpress_api`` returns.
    Further testing is necessary to know if this case convention is always enforced, so consistency is key here.

    :param wp_posts_f: ``list[dict]`` WordPress Post Information case file (previously loaded and ready to process)
    :param model_lst: ``list[str]`` models' names
    :return: ``list[int]`` (corresponding IDs)
    """
    model_tracking: dict[str, int] = wordpress_api.map_wp_class_id(
        wp_posts_f, "pornstars", "pornstars"
    )
    return list(
        {
            model_tracking[model.title().strip()]
            for model in model_lst
            if model.title().strip() in model_tracking.keys()
        }
    )


def identify_missing(
        wp_data_dic: dict[str, str | int],
        data_lst: list[str],
        data_ids: list[int],
        ignore_case: bool = False,
):
    """This function is a simple algorithm that identifies when a tag or model must be manually recorded
    on WordPress, and it does that with two main assumptions:
    1) "If I have x tags/models, I must have x integers/IDs"
    2) "If there is a value with no ID, it just means that there is none and has to be created"
    Number 1 is exactly the first test for our values so, most of the time, if our results are consistent,
    this function returns None and no other operations are carried out. It acts exactly like a gatekeeper.
    In case the opposite is true, the function will examine why those IDs are missing and return the culprits (2).
    Our gatekeeper has an option to either enforce the case policy or ignore it, so I generally tell it to be
    lenient with tags (ignore_case = True) and strict with models (ignore_case = False), this is optional though.
    Ignore case was implemented based on the considerations that I have shared so far.

    :param wp_data_dic: ``dict[str, str | int]`` returned by either ``map_wp_model_id`` or ``tag_id_merger_dict``
    from module ``integrations.wordpress_api``
    :param data_lst: ``list[str]`` tags or models
    :param data_ids: ``list[int]`` tag or model IDs.
    :param ignore_case: ``bool`` True, enforce case policy. Default False.
    :return: ``None`` or ``list[str]``
    """
    # Assumes we have x items and x ids
    if len(data_lst) == len(data_ids):
        return None
    else:
        # If we have less or more items on either side, we've got a problem.
        not_found: list[str] = []
        for item in data_lst:
            if ignore_case:
                item: str = item.lower()
                tags: list[str] = [tag.lower() for tag in wp_data_dic.keys()]
                if item not in tags:
                    not_found.append(item)
            else:
                try:
                    wp_data_dic[item]
                except KeyError:
                    not_found.append(item)
        return not_found


def fetch_thumbnail(
        folder: str, slug: str, remote_res: str, thumbnail_name: str = ""
) -> int:
    """This function handles the renaming and fetching of thumbnails that will be uploaded to
    WordPress as media attachments. It dynamically renames the thumbnails by taking in a URL slug to
    conform with SEO best-practices. Returns a status code of 200 if the operation was successful
    (fetching the file from a remote source). It also has the ability to store the image using a
    relative path.

    :param folder: ``str`` thumbnails dir
    :param slug: ``str`` URL slug
    :param remote_res: ``str`` thumbnail download URL
    :param thumbnail_name: ``str`` used in case the user wants to upload different thumbnails
    and wishes to keep the names.
    :return: ``int`` (status code from requests)
    """
    parent: bool = False if os.path.exists(f"./{folder}") else True
    thumbnail_dir: str = f"{helpers.is_parent_dir_required(parent=parent)}{folder}"
    remote_data: requests = requests.get(remote_res)
    if thumbnail_name != "":
        name: str = f"-{thumbnail_name.split('.')[0]}"
    else:
        name: str = thumbnail_name
    with open(f"{thumbnail_dir}/{slug}{name}.jpg", "wb") as img:
        img.write(remote_data.content)
    return remote_data.status_code


def make_payload(
        vid_slug,
        status_wp: str,
        vid_name: str,
        vid_description: str,
        banner_tracking_url: str,
        banner_img: str,
        partner_name: str,
        tag_int_lst: list[int],
        model_int_lst: list[int],
        categs: list[int] | None = None,
        wp_auth: WPAuth = WP_CLIENT_INFO
) -> dict[str, str | int]:
    """Make WordPress ``JSON`` payload with the supplied values.
    This function also injects ``HTML`` code into the payload to display the banner, add ``ALT`` text to it
    and other parameters for the WordPress editor's (Gutenberg) rendering.

    Some elements are not passed as f-strings because the ``WordPress JSON REST API`` has defined a different data types
    for those elements and, sometimes, the response returns a status code of 400
    when those are not followed carefully.

    :param vid_slug: ``str`` slug optimized by the job control function and database parsing algo ( ``tasks`` package).
    :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
    :param vid_name: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param banner_tracking_url: ``str`` Affiliate tracking link to generate leads
    :param banner_img: ``str`` banner image URL that will be injected into the payload.
    :param partner_name: ``str`` The offer you are promoting
    :param tag_int_lst: ``list[int]`` tag ID list
    :param model_int_lst: ``list[int]`` model ID list
    :param categs: ``list[int]`` category numbers to be passed with the post information
    :param wp_auth: ``WPAuth`` Object with the author information.
    :return: ``dict[str, str | int]``
    """
    # Added an author field to the client_info config file.
    author: int = int(wp_auth.author_admin)
    payload_post: dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "link": f"https://whoresmen.com/{vid_slug}/",
        "title": f"{vid_name}",
        "content": f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt="{vid_name} | {partner_name} on WhoresMen.com"/></a></figure>',
        "excerpt": f"<p>{vid_description}</p>\n",
        "author": author,
        "featured_media": 0,
        "tags": tag_int_lst,
        "pornstars": model_int_lst,
    }

    # if the job control passes categories then a new key-value pair will be added with them.
    if categs:
        payload_post["categories"] = categs
    else:
        pass

    return payload_post


def make_payload_simple(
        vid_slug,
        status_wp: str,
        vid_name: str,
        vid_description: str,
        tag_int_lst: list[int],
        model_int_lst: list[int] | None = None,
        categs: list[int] | None = None,
        wp_auth: WPAuth = WP_CLIENT_INFO
) -> dict[str, str | int]:
    """Makes a simple WordPress JSON payload with the supplied values.

    :param vid_slug: ``str`` slug optimized by the job control function and database parsing algo ( ``tasks`` package).
    :param status_wp: ``str`` in this case, it is just the str "draft". It could be "publish" but it requires review.
    :param vid_name: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param tag_int_lst: ``list[int]`` tag ID list
    :param model_int_lst: ``list[int]`` or ``None`` model ID list
    :param categs: ``list[int]`` or ``None`` category integers provided as optional parameter.
    :param wp_auth: ``WPAuth`` object with site configuration information.
    :return: ``dict[str, str | int]``
    """
    # Added an author field to the client_info file.
    author: int = int(wp_auth.author_admin)
    payload_post: dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "title": f"{vid_name}",
        "content": f"<p>{vid_description}",
        "excerpt": f"<p>{vid_description}</p>\n",
        "author": author,
        "featured_media": 0,
        "tags": tag_int_lst,
    }

    if categs:
        payload_post["categories"] = categs
    elif model_int_lst:
        payload_post["pornstars"] = model_int_lst
    else:
        pass
    return payload_post


def make_img_payload(vid_title: str, vid_description: str) -> dict[str, str]:
    """Similar to the make_payload function, this one makes the payload for the video thumbnails,
    it gives them the video description and focus key phrase, which is the video title plus a call to
    action in case that ALT text appears on the image search vertical, and they want to watch the video.

    :param vid_title: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :return: ``dict[str, str]``
    """
    img_payload: dict[str, str] = {
        "alt_text": f"{vid_title} on WhoresMen.com - {vid_description}. Watch now!",
        "caption": f"{vid_title} on WhoresMen.com - {vid_description}. Watch now!",
        "description": f"{vid_title} on WhoresMen.com - {vid_description}. Watch now!",
    }
    return img_payload


def make_slug(
        partner: str, model: str, title: str, content: str, reverse: bool = False
) -> str:
    """This function is a new approach to the generation of slugs inspired by the slug making
    mechanism from gallery_select.py. It takes in strings that will be transformed into URL slugs
    that will help us optimise the permalinks for SEO purposes.

    :param partner: ``str`` video partner/br``and
    :param model:  ``str`` video model
    :param title: ``str`` Video title
    :param content: ``str`` type of content, in this file it is simply `video` but it could be `pics`
                    this parameter tells Google about the main content of the page.
    :param reverse: ``bool``  ``True`` if you want to place the video title in front of the permalink. Default ``False``
    :return: ``str`` formatted string of a WordPress-ready URL slug.
    """
    filter_words: set[str] = {"at", "&", "and"}
    title_sl: str = "-".join(
        [
            word.lower()
            for word in title.lower().split()
            if (
                re.match(r"[\w+]", word, flags=re.IGNORECASE)
                and word.lower() not in filter_words
        )
        ]
    )

    partner_sl: str = "-".join(clean_partner_tag(partner.lower()).split())
    try:
        model_sl: str = "-".join(
            [
                "-".join(name.split(" "))
                for name in [model.lower().strip() for model in model.split(",")]
            ]
        )

        content: str = f"-{content}" if content != "" or None else ""

        if reverse:
            return f"{title_sl}-{partner_sl}-{model_sl}{content}"
        else:
            return f"{partner_sl}-{model_sl}-{title_sl}{content}"
    except AttributeError:
        # Model can be NoneType and crash the program if this is not handled.
        if reverse:
            return f"{title_sl}-{partner_sl}-{content}"
        else:
            return f"{partner_sl}-{title_sl}-{content}"


def hot_file_sync(bot_config: ContentSelectConf |
                              GallerySelectConf | EmbedAssistConf) -> bool:
    """I named this feature "Hot Sync" as it has the ability to modify the data structure we are using as a cached
    datasource and allows for more efficiency in keeping an up-to-date copy of all your posts.
    This function leverages the power of the caching mechanism defined
    in wordpress_api.py that dynamically appends new items in order and keeps track of cached pages with the
    total count of posts at the time of update. hot_file_sync just updates the JSON cache of the WP site and
    reloads the local cache configuration file to validate the changes.

    Hot Sync will write the changes once the new changes are validated and compared with the local config file.
    In other words, if it isn't right, the WP post file remains untouched.

    :param bot_config: ``ContentSelectConf`` or ``GallerySelectConf`` or ``EmbedAssistConf``
    with configuration information.
    :return: ``bool``  ``True`` if everything went well or ``False`` if the validation failed)
    """
    parent = False if os.path.exists(
        f"./{clean_filename(bot_config.wp_cache_config, 'json')}") else True
    if isinstance(bot_config, GallerySelectConf):
        wp_filename: str = helpers.clean_filename(
            bot_config.wp_json_photos, "json")
    else:
        wp_filename: str = helpers.clean_filename(
            bot_config.wp_json_posts, "json")
    sync_changes: list[dict[str, ...]] = wordpress_api.update_json_cache(
        photos=True if isinstance(bot_config, GallerySelectConf) else False)
    # Reload config
    config_json: dict[str, str] = helpers.load_json_ctx(
        bot_config.wp_cache_config)
    if len(sync_changes) == config_json[0][wp_filename]["total_posts"]:
        helpers.export_request_json(
            wp_filename, sync_changes, 1, parent=parent)
        return True
    else:
        return False


def partner_select(
        partner_lst: list[str],
        banner_lsts: list[list[str]],
        db_name: str,
) -> tuple[str, list[str]]:
    """Selects partner and banner list based on their index order.
    As this function is based on index and order of elements, both lists should have the same number of elements.


    :param partner_lst: ``list[str]`` - partner offers
    :param banner_lsts: ``list[list[str]]`` list of banners to select from.
    :param db_name: ``str`` partner database name
    :return: ``tuple[str, list[str]]`` partner_name, banner_list
    """
    print("\n")
    for num, partner in enumerate(partner_lst, start=1):
        print(f"{num}. {partner}")
    try:
        partner_indx = input("\n\nSelect your partner: ")
        partner = partner_lst[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]
    except IndexError:
        partner_indx = input("\n\nSelect your partner again: ")
        partner = partner_lst[int(partner_indx) - 1]
        banners = banner_lsts[int(partner_indx) - 1]
    return partner, banners


def select_guard(db_name: str, partner: str) -> None:
    """This function protects the user by matching the first
    occurrence of the partner's name in the database that the user selected.
    Avoiding issues at this stage is crucial because, if a certain user selects an
    incorrect database, the program will either crash or send incorrect record details to
    WordPress, and that could be a huge issue considering that each partner offering has
    proprietary banners and tracking links.

    :param db_name: ``str`` user-selected database name
    :param partner: ``str`` user-selected partner offering
    :return: ``None`` / If the assertion fails the execution will stop gracefully.
    """
    # Find the split character as I just need to get the first word of the name
    # to match it with partner selected by the user
    match_regex = re.findall(r"[\W_]", db_name)[0]
    try:
        assert re.match(
            db_name.strip().split(match_regex)[0], partner, flags=re.IGNORECASE
        )
    except AssertionError:
        print("\nBe careful! Partner and database must match. Re-run...")
        print(f"You selected {db_name} for partner {partner}.")
        quit()


def content_select_db_match(
        hint_lst: list[str],
        content_hint: str,
        folder: str = "",
        prompt_db: bool = False,
        parent: bool = False,
) -> tuple[Connection, Cursor, str, int]:
    """Give a list of databases, match them with multiple hints and retrieves the most up-to-date filename.
    This is a specialised implementation based on the ``filename_select`` function in the ``core.helpers`` module.

    ``content_select_db_match`` finds a common index where the correct partner offer and database are located
    within two separate lists: the available ``.db`` file list and a list of partner offers.
    In order to accomplish this, the modules in the ``tasks`` package apply a consistent naming convention that
    looks like ``partner-name-date-content-type-in-ISO-format``; those filenames are further analysed by an algorithm
    that matches strings found in a lookup list.

    For more information on how this matching works and the algorithm behind it, refer to the documentation for
    ``match_list_mult`` and ``match_list_elem_date`` in the ``core.helpers`` module.

    :param hint_lst: ``list[str]`` words/patterns to match.
    :param content_hint: ``str`` type of content, typically ``vids`` or ``photos``

    **Note: As part of the above-mentioned naming convention, the files include a content type hint.
    This allows the algorithm to identify video or photo databases, depending on the module
    calling the function. However, this hint can be any word that you use consistently in your filenames.**

    :param prompt_db: ``True`` if you want to prompt the user to select db. Default ``False``.
    :param folder: ``str`` where you want to look for files
    :param parent: ``True`` to search in parent dir, default set to ``False``.
    If you want to access the file from a parent dir,
    either let the destination function handle it for you or specify it yourself.
    :return: ``tuple[Connection, Cursor, str, int]``
             (database connection, database cursor, database name, common index int)
    """
    available_files: list[str] = helpers.search_files_by_ext(
        "db", folder=folder, parent=parent)
    filtered_files: list[str] = helpers.match_list_elem_date(
        hint_lst,
        available_files,
        join_hints=(True, " ", "-"),
        ignore_case=True,
        strict=True,
    )

    relevant_content: list[str] = [
        filtered_files[indx]
        for indx in helpers.match_list_mult(content_hint, filtered_files)
    ]

    if prompt_db:
        print(f"\nHere are the available database files:")
        for num, file in enumerate(relevant_content, start=1):
            print(f"{num}. {file}")
        print("\n")
    else:
        pass
    print("\n")
    for num, file in enumerate(hint_lst, start=1):
        print(f"{num}. {file}")

    try:
        select_partner: str = input(f"\nSelect your partner now: ")
        # I just need the first word to match the db.
        try:
            split_char = re.findall(r"[\W_]",
                                    hint_lst[int(select_partner) - 1])[0]
            clean_hint: str = hint_lst[int(
                select_partner) - 1].split(split_char)[0]
        except IndexError:
            clean_hint: str = hint_lst[int(select_partner) - 1]

        rel_content: int = helpers.match_list_single(
            clean_hint, relevant_content, ignore_case=True
        )

        select_file: int = rel_content

        is_parent: str = (
            helpers.is_parent_dir_required(parent)
            if folder == ""
            else f"{folder}/"
        )
        db_path: str = f"{is_parent}{relevant_content[select_file]}"

        db_new_conn: sqlite3 = sqlite3.connect(db_path)
        db_new_cur: sqlite3 = db_new_conn.cursor()
        return (db_new_conn, db_new_cur,
                relevant_content[int(select_file)], select_file)
    except IndexError or ValueError:
        raise InvalidInput


def video_upload_pilot(
        banner_lsts: list[list[str]],
        wp_auth: WPAuth = WP_CLIENT_INFO,
        wp_endpoints: WPEndpoints = WPEndpoints,
        cs_config: ContentSelectConf = CONTENT_SEL_CONF,
        parent: bool = False,
) -> None:
    """Here is the main coordinating function of this module, the job control that
    uses all previous functions to carry out all the tasks associated with the video upload process in the business.
    In fact, by convention, this function must be called main(), but that name does not really reflect
    the excitement of what it accomplishes and the collaboration with other members of the module plus other modules
    and local implementations. This function is a real pilot and here's a quick breakdown of its workflow:

    **Note: This won't be a detailed description, however, it will give you a better notion of
    how this code accomplishes these tasks.**

    1) Calls hot_file_sync to begin the session with a fresh set of data. \n
    2) Sets up the required files and data structures by using configuration constants. \n
    3) Assigns the video results from fetch_data_sql to a local variable. \n
    4) Assigns the WP API base url to a local variable. \n
    5) Gathers input from the user and then validates. \n
    6) Validates user input and ensures a sensible choice is picked. \n
    7) Calls filter_published to get a set of fresh videos to start the control loop (result assigned to variable). \n
    8) Control loop starts with the enumerate function and the filtered dataset. \n

        8.1) Unpacks values from every tuple. \n
        8.2) Constructs a '-video' slug to make sure it conforms to Google's policies about content main topic. \n
        8.3) Prints relevant metadata about the video for the user. \n
        8.4) Prompts the user with options to either upload the current item, exit or fetch the next element. \n
        8.5) Handles the options according to the control number of the loop and executes the following: \n

            8.5.1) Upload the video:
                => Prepares additional validation with the supplied metadata. \n
                **Function calls:** \n
                --> get_tag_ids/get_model_ids \n
                --> wordpress_api.tag_id_merger_dict \n
                --> wordpress_api.map_wp_model_id \n
                --> identify_missing \n
                --> make_payload \n
                --> fetch_thumbnail \n
                --> wordpress_api.wp_post_create \n
                --> make_img_payload \n
                --> wordpress_api.upload_thumbnail \n
                --> pyclip.copy(source_url) \n
                --> pyclip.copy(title) \n
                --> Prompts the user to continue \n
                --> If the user continues: \n
                    -> pyclip.clear()
                    -> hot_file_sync
                    -> filter_published (assigns it to out-of-loop scope) \n
            8.5.2) The user chooses not to continue
                **Function calls:** \n
                --> pyclip.detect_clipboard()
                --> pyclip.clear()
                --> clean_file_cache \n
                --> *BREAK*
            8.5.3) The user presses enter
                --> *CONTINUE*
            8.6) The loop will continue until the control variable total_elems is 1 since the loop wants to
            tell the user when it is no longer possible for them to fetch more items.
            **When it reaches the point where there is only one element to show, the program will communicate
            that to the user and wait 60 seconds before cleaning cache files and clipboard data.**

    :param banner_lsts: ``list[list[str]]`` banner URLS to make the post payload.
    :param wp_auth: ``WPAuth`` element provided by the ``core.config_mgr`` module.
                     Set by default and bound to change based on the config file.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :param cs_config: ``ContentSelectConf`` Object that contains configuration options for this module.
    :param parent: ``True`` if you want to locate relevant files in the parent directory. Default False
    :return: ``None``
    """
    # Configuration steps
    print("\n==> Warming up... ┌(◎_◎)┘ ")
    hot_file_sync(bot_config=cs_config)
    partners: list[str] = cs_config.partners.split(',')
    wp_posts_f: list[dict[str, ...]] = helpers.load_json_ctx(
        cs_config.wp_json_posts)
    wp_base_url: str = wp_auth.api_base_url
    os.system('clear')
    db_conn, cur_dump, partner_db_name, partner_indx = content_select_db_match(
        partners, cs_config.content_hint, parent=parent
    )
    all_vals: list[tuple[str, ...]] = helpers.fetch_data_sql(
        cs_config.sql_query, cur_dump)
    # Prints out at the end of the uploading session.
    videos_uploaded: int = 0
    partner, banners = partners[partner_indx], banner_lsts[partner_indx]
    select_guard(partner_db_name, partner)
    not_published_yet: list[tuple[str, ...]
    ] = filter_published(all_vals, wp_posts_f)
    # You can keep on getting posts until this variable is equal to one.
    total_elems: int = len(not_published_yet)
    print(f"There are {total_elems} videos to be published...")
    for num, vid in enumerate(not_published_yet):
        (title, *fields) = vid
        description = fields[0]
        models = fields[1]
        tags = fields[2]
        date = fields[3]
        duration = fields[4]
        source_url = fields[5]
        thumbnail_url = fields[6]
        tracking_url = fields[7]
        partner_name = partner
        print(f"\n{' Review this post ':*^30}\n")
        print(title)
        print(description)
        print(f"Duration: {duration}")
        print(f"Tags: {tags}")
        print(f"Models: {models}")
        print(f"Date: {date}")
        print(f"Thumbnail URL: {thumbnail_url}")
        print(f"Source URL: {source_url}")
        # Centralized control flow
        add_post = input(
            "\nAdd post to WP? -> Y/N/ENTER to review next post: ").lower()
        if add_post == ("y" or "yes"):
            add_post = True
        elif add_post == ("n" or "no"):
            pyclip.detect_clipboard()
            pyclip.clear()
            print(f"You have created {videos_uploaded} posts in this session!")
            break
        else:
            if num < total_elems - 1:
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("\nWe have reviewed all posts for this query.")
                print("Try a different SQL query or partner. I am ready when you are. ")
                print(
                    f"You have created {videos_uploaded} posts in this session!")
                break
        if add_post:
            slugs: list[str] = [
                f"{fields[8]}-video",
                make_slug(partner, models, title, "video"),
                make_slug(partner, models, title, "video", reverse=True),
            ]

            print("\n--> Available slugs:\n")

            for n, slug in enumerate(slugs, start=1):
                print(f"{n}. -> {slug}")
            print("--> Enter #4 to provide a custom slug")

            match input("\nSelect your slug: "):
                case "1":
                    wp_slug: str = slugs[0]
                case "2":
                    wp_slug: str = slugs[1]
                case "3":
                    wp_slug: str = slugs[2]
                case "4":
                    wp_slug: str = input("Provide a new slug: ")
                case _:
                    # Smart slug by default (reversed).
                    wp_slug: str = slugs[2]

            tag_prep: list[str] = [tag.strip() for tag in tags.split(",")]
            # Making sure that the partner tag does not have apostrophes
            partner_tag: str = clean_partner_tag(partner.lower())
            tag_prep.append(partner_tag)
            tag_ints: list[int] = get_tag_ids(wp_posts_f, tag_prep, "tags")
            all_tags_wp: dict[str, str] = wordpress_api.tag_id_merger_dict(
                wp_posts_f)
            tag_check: list[str] | None = identify_missing(
                all_tags_wp, tag_prep, tag_ints, ignore_case=True
            )
            if tag_check is None:
                # All tags have been found and mapped to their IDs.
                pass
            else:
                # You've hit a snag.
                for tag in tag_check:
                    print(f"ATTENTION --> Tag: {tag} not on WordPress.")
                    print("--> Copying missing tag to your system clipboard.")
                    print("Paste it into the tags field as soon as possible...\n")
                    pyclip.detect_clipboard()
                    pyclip.copy(tag)

            # Removing trailing spaces in tags and models
            model_prep = (
                [model.strip() for model in models.split(",")]
                if models is not None
                else ["model-not-found"]
            )

            # The would-be `models_ints`
            calling_models: list[int] = get_model_ids(wp_posts_f, model_prep)
            all_models_wp: dict[str, int] = wordpress_api.map_wp_class_id(
                wp_posts_f, "pornstars", "pornstars"
            )
            new_models: list[str] | None = identify_missing(
                all_models_wp, model_prep, calling_models)

            if new_models is None or model_prep[0] == "model-not-found":
                # All model have been found and located
                # or the post does not include a model.
                pass
            else:
                # There's a new girl in town.
                for girl in new_models:
                    print(f"ATTENTION! --> Model: {girl} not on WordPress.")
                    print("--> Copying missing model name to your system clipboard.")
                    print("Paste it into the Pornstars field as soon as possible...\n")
                    pyclip.detect_clipboard()
                    pyclip.copy(girl)

            class_title = classify_title(title)
            class_description = classify_description(description)
            # class_tags = classify_tags(tags)
            class_title.union(class_description)
            # class_title.union(class_tags)
            consolidate_categs = list(class_title)

            print(" \n** I think these categories are appropriate: **\n")
            for num, categ in enumerate(consolidate_categs, start=1):
                print(f"{num}. {categ}")

            match input("\nEnter the category number or type in to look for another category in the site: "):
                case _ as option:
                    try:
                        sel_categ = consolidate_categs[int(option) - 1]
                    except (ValueError or IndexError):
                        sel_categ = option

            categ_ids = get_tag_ids(wp_posts_f, [sel_categ], preset="categories")

            print("\n--> Making payload...")
            payload = make_payload(
                wp_slug,
                wp_auth.default_status,
                title,
                description,
                tracking_url,
                random.choice(banners),
                partner_name,
                tag_ints,
                calling_models,
                categs=categ_ids
            )

            print("--> Fetching thumbnail...")
            pic_format = clean_filename(wp_slug, cs_config.pic_format)
            try:
                fetch_thumbnail(
                    cs_config.thumbnail_dir,
                    wp_slug,
                    thumbnail_url)
                thumbnail_lookup = False if os.path.exists(
                    f"./{cs_config.thumbnail_dir}") else True
                thumbnail_folder: str = f"{helpers.is_parent_dir_required(thumbnail_lookup)}{cs_config.thumbnail_dir}"
                print(
                    f"--> Stored thumbnail {pic_format} in cache folder {thumbnail_folder}"
                )
                print("--> Uploading thumbnail to WordPress Media...")
                print("--> Adding image attributes on WordPress...")
                img_attrs: dict[str, str] = make_img_payload(
                    title, description)
                upload_img: int = wordpress_api.upload_thumbnail(
                    wp_base_url,
                    ["/media"],
                    f"{cs_config.thumbnail_dir}/{pic_format}",
                    img_attrs,
                )

                # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is
                # the case. Each successful upload will prompt the program to
                # clean the thumbnail selectively.
                if upload_img == 500:
                    print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually."
                    )
                    print("--> Proceeding to the next post...\n")
                    continue
                elif upload_img == (200 or 201):
                    os.remove(f"{thumbnail_folder}/{pic_format}")
                else:
                    pass

                print(f"--> WordPress Media upload status code: {upload_img}")
                print("--> Creating post on WordPress")
                push_post = wordpress_api.wp_post_create(
                    [wp_endpoints.posts], payload)
                print(f"--> WordPress status code: {push_post}")
                # Copy important information to the clipboard.
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(source_url)
                pyclip.copy(title)
                print("--> * DONE * Check the post and paste all you need from your clipboard.")
                videos_uploaded += 1
            except SSLError:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("* There was a connection error while processing this post... *")
                if input(
                        "\nDo you want to continue? Y/N/ENTER to exit: ") == ("y" or "yes"):
                    continue
                else:
                    print(
                        f"You have created {videos_uploaded} posts in this session!")
                    break
            if num < total_elems - 1:
                next_post = input(
                    "\nNext post? -> Y/N/ENTER to review next post: ").lower()
                if next_post == ("y" or "yes"):
                    # Clears clipboard after every video.
                    pyclip.clear()
                    print("\n==> Syncing and caching changes... ε= ᕕ(⎚‿⎚)ᕗ")
                    try:
                        sync: bool = hot_file_sync(bot_config=cs_config)
                    except ConnectionError:
                        print("Hot File Sync encountered a ConnectionError.")
                        print(
                            "Going to next post. I will fetch your changes in a next try.")
                        print(
                            "If you want to update again, relaunch the bot or try to add another post and select 'y'")
                        sync: bool = True
                    if sync:
                        continue
                    else:
                        print(
                            """ERROR: WP JSON Sync failed. Look at the files.
                            Maybe you have to rollback your WordPress cache.
                            Run: python3 -m integrations.wordpress_api --posts""")
                elif next_post == ("n" or "no"):
                    # The terminating parts add this function to avoid
                    # tracebacks from pyclip
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    print(
                        f"You have created {videos_uploaded} posts in this session!")
                    break
                else:
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                # Since we ran out of elements the script will end after adding it to WP
                # So that it doesn't clear the clipboard automatically.
                print("\nWe have reviewed all posts for this query.")
                print("Try a different query and run me again.")
                print("\n--> Cleaning thumbnails cache now")
                print(
                    f"You have created {videos_uploaded} posts in this session!")
                print(
                    "Waiting for 60 secs to clear the clipboard before you're done with the last post..."
                )
                time.sleep(60)
                pyclip.detect_clipboard()
                pyclip.clear()
                break
        else:
            pyclip.detect_clipboard()
            pyclip.clear()
            print("\nWe have reviewed all posts for this query.")
            print("Try a different SQL query or partner. I am ready when you are. ")
            print(f"You have created {videos_uploaded} posts in this session!")
            break


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    arg_parser = argparse.ArgumentParser(
        description="Content Select Assistant - Behaviour Tweaks"
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        help="""Define if database and file search happens in the parent directory.
                                        This argument also affects:
                                        1. Thumbnail search
                                        2. HotSync caching
                                        3. Cache cleaning
                                        The default is set to false, so if you execute this file as a module,
                                        you may not want to enable it because this is treated as a package.""",
    )

    args = arg_parser.parse_args()

    banner_tuktuk_1 = "https://mongercash.com/view_banner.php?name=tktkp-728x90.gif&amp;filename=9936_name.gif&amp;type=gif&amp;download=1"
    banner_tuktuk_2 = "https://mongercash.com/view_banner.php?name=tuktuk620x77.jpg&filename=7664_name.jpg&type=jpg&download=1"
    banner_tuktuk_3 = "https://mongercash.com/view_banner.php?name=tktkp-850x80.jpg&amp;filename=9934_name.jpg&amp;type=jpg&amp;download=1"

    banner_asd_1 = "https://mongercash.com/view_banner.php?name=asd-640x90.gif&filename=6377_name.gif&type=gif&download=1"
    banner_asd_2 = "https://mongercash.com/view_banner.php?name=asd-header-970x170.png&filename=6871_name.png&type=png&download=1"
    banner_asd_3 = "https://mongercash.com/view_banner.php?name=asd-channel-footer-950%20x%20250.png&filename=6864_name.png&type=png&download=1"

    banner_trike_1 = "https://mongercash.com/view_banner.php?name=tp-728x90.gif&amp;filename=9924_name.gif&amp;type=gif&amp;download=1"
    banner_trike_2 = "https://mongercash.com/view_banner.php?name=tp-850x80.jpg&filename=9921_name.jpg&type=jpg&download=1"
    banner_trike_3 = "https://mongercash.com/view_banner.php?name=trike%20patrol%20850x80.gif&amp;filename=7675_name.gif&amp;type=gif&amp;download=1"

    banner_euro_1 = "https://mongercash.com/view_banner.php?name=esd-730x90-1.png&filename=12419_name.png&type=png&download=1"
    banner_euro_2 = "https://mongercash.com/view_banner.php?name=esd-1323x270-2.png&filename=12414_name.png&type=png&download=1"
    banner_euro_3 = "https://mongercash.com/view_banner.php?name=esd-876x75-1.png&filename=12416_name.png&type=png&download=1"

    banner_paradise_1 = "https://mongercash.com/view_banner.php?name=1323x270.jpg&filename=8879_name.jpg&type=jpg&download=1"

    banner_toticos_1 = "https://mongercash.com/view_banner.php?name=tot-600x120-2.gif&filename=2605_name.gif&type=gif&download=1"

    banner_lst_asd = [banner_asd_1, banner_asd_2, banner_asd_3]
    banner_lst_tktk = [banner_tuktuk_1, banner_tuktuk_2, banner_tuktuk_3]
    banner_lst_trike = [banner_trike_1, banner_trike_2, banner_trike_3]
    banner_lst_esd = [banner_euro_1, banner_euro_2, banner_euro_3]
    banner_lst_paradise = [banner_paradise_1]
    banner_lst_toticos = [banner_toticos_1]

    banner_lists = [
        banner_lst_asd,
        banner_lst_tktk,
        banner_lst_trike,
        banner_lst_esd,
        banner_lst_paradise,
        banner_lst_toticos,
    ]

    video_upload_pilot(banner_lists, parent=args.parent)
