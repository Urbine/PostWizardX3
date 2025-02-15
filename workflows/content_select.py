"""
content_select is the biggest out of three bots that streamline the content upload and
integration of content in my WordPress site.

It is able to identify the data sources dynamically and serve as an assistant powered
by several local integrations, being one of those the ``integrations.wordpress_api`` implementation.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import datetime
import logging
import os
import random
import re
import readline  # Imported to enable Standard Input manipulation. Don't remove!
import tempfile
import time
import sqlite3
import warnings

from sqlite3 import Connection, Cursor

# Third-party modules
import pyclip
import requests
from requests.exceptions import SSLError, ConnectionError
from rich.console import Console

# Local implementations
from core import (
    InvalidInput,
    UnsupportedParameter,
    HotFileSyncIntegrityError,
    AssetsNotFoundError,
    UnavailableLoggingDirectory,
    get_duration,
    generate_random_str,
    parse_client_config,
    content_select_conf,
    helpers,
    wp_auth,
    clean_filename,
    x_auth,
    bot_father,
)

from integrations import wordpress_api, x_api, botfather_telegram
from integrations.url_builder import (
    WPEndpoints,
    XEndpoints,
    BotFatherCommands,
    BotFatherEndpoints,
)
from ml_engine import classify_title, classify_description, classify_tags

# Imported for typing purposes
from core.config_mgr import (
    WPAuth,
    ContentSelectConf,
    GallerySelectConf,
    EmbedAssistConf,
    UpdateMCash,
)


def logging_setup(
    bot_config: ContentSelectConf | GallerySelectConf | EmbedAssistConf | UpdateMCash,
    path_to_this: str,
) -> None:
    """Initiate the basic logging configuration for bots in the ``workflows`` package.

    :param bot_config: ``ContentSelectConf`` | ``GallerySelectConf`` | ``EmbedAssistConf`` | ``UpdateMCash`` - config functions
    :param path_to_this: ``str`` - Equivalent to __file__ but passed in as a parameter.
    :return: ``None``
    """
    get_filename = lambda f: os.path.basename(f).split(".")[0]
    random_int_id = "".join(random.choices([str(num) for num in range(1, 10)], k=5))
    uniq_log_id = f"{random_int_id}{generate_random_str(5)}"

    # This will help users identify their corresponding log per session.
    os.environ["SESSION_ID"] = uniq_log_id
    log_name = (
        f"{get_filename(path_to_this)}-log-{uniq_log_id}-{datetime.date.today()}.log"
    )
    log_dirname_cfg = bot_config.logging_dirname

    if os.path.exists(log_dirname_cfg):
        log_dir_path = os.path.abspath(log_dirname_cfg)
    elif os.path.exists(log_dir_parent := f"../{log_dirname_cfg}"):
        log_dir_path = log_dir_parent
    else:
        try:
            os.mkdir(log_dirname_cfg)
            log_dir_path = log_dirname_cfg
        except OSError:
            raise UnavailableLoggingDirectory(log_dirname_cfg)

    logging.basicConfig(
        filename=f"{log_dir_path}/{log_name}",
        filemode="w+",
        level=logging.INFO,
        encoding="utf8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )
    return None


def clean_partner_tag(partner_tag: str) -> str:
    """Clean partner names that could contain apostrophes in them.

    :param partner_tag: ``str`` the conflicting text
    :return: ``str`` cleaned partner tag without the apostrophe.
    """
    try:
        no_word: list[str] = re.findall(r"[\W_]+", partner_tag, flags=re.IGNORECASE)
        if no_word[0] == " " and len(no_word) == 1:
            return partner_tag
        elif "'" not in no_word:
            return partner_tag
        else:
            # Second special character is the apostrophe, the first one is typically a whitespace
            split_char: str = no_word[1] if len(no_word) > 1 else no_word[0]
            return "".join(partner_tag.split(split_char))
    except IndexError:
        return partner_tag


def asset_parser(bot_config: ContentSelectConf, partner: str):
    """Parse asset images for post payload building from the specified file in the
    ``workflows_config.ini`` file.

    :param bot_config: ``ContentSelectConf`` bot config factory function.
    :param partner: ``str`` partner name
    :return: ``list[str]`` asset images or banners.
    """
    assets = parse_client_config(bot_config.assets_conf, "core.config")
    sections = assets.sections()

    spl_char = lambda tag: chars[0] if (chars := re.findall(r"[\W_]+", tag)) else " "
    wrd_list = clean_partner_tag(partner).split(spl_char(partner))

    find_me = (
        lambda word, section: matches[0]
        if (matches := re.findall(word, section, flags=re.IGNORECASE))
        else matches
    )

    assets_list = []
    for wrd in wrd_list:
        # The main lambda has re.findall with IGNORECASE flag, however
        # list index lookup does take word case into consideration for str comparison.
        wrd_to_lc = wrd.lower()

        # To ensure uniqueness in the hints provided, the count of matches must be 1.
        # If the same word is found more than once, then the match is not unique.
        matches = (
            temp_lst := [find_me(wrd_to_lc, section) for section in sections]
        ).count(wrd_to_lc)
        if matches == 1:
            match_indx = temp_lst.index(wrd_to_lc)
            logging.info(
                f'Asset parsing result: found "{wrd}" in section: {sections[match_indx]}'
            )
            assets_list = list(assets[sections[match_indx]].values())
            break
        else:
            continue

    if assets_list:
        return assets_list
    else:
        logging.critical(f"Raised AssetsNotFoundError - Quitting...")
        raise AssetsNotFoundError


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
    post_titles: list[str] = wordpress_api.get_post_titles_local(wp_posts_f, yoast=True)

    comp_title: re.Pattern = re.compile(rf"({title})")

    results: list[str] = [
        vid_name for vid_name in post_titles if re.match(comp_title, vid_name)
    ]
    if len(results) >= 1:
        return True
    else:
        return False


def filter_published(
    all_videos: list[tuple], wp_posts_f: list[dict]
) -> list[tuple[str, ...]]:
    """``filter_published`` does its filtering work based on the ``published_json`` function.
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
    not_published: list[tuple] = []
    for elem in all_videos:
        (title, *fields) = elem
        if published_json(title, wp_posts_f):
            continue
        else:
            not_published.append(elem)
    return not_published


def get_tag_ids(wp_posts_f: list[dict], tag_lst: list[str], preset: str) -> list[int]:
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

    spl_char = lambda tag: chars[0] if (chars := re.findall(r"[\W_]+", tag)) else " "
    clean_tag = lambda tag: " ".join(tag.split(spl_char(tag)))
    tag_join = lambda tag: "".join(map(clean_tag, tag))
    # Result must be: colourful-skies/great -> colourful skies great
    cl_tags = list(map(tag_join, tag_lst))

    # It is crucial that tags don't have any special characters
    # before processing them with ``tag_tracking``.
    matched_keys: list[str] = [
        wptag
        for wptag in tag_tracking.keys()
        for tag in cl_tags
        if re.fullmatch(tag, wptag, flags=re.IGNORECASE)
    ]
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
    title_strip = lambda model: model.title().strip()
    return list(
        {
            model_tracking[title_strip(model)]
            for model in model_lst
            if title_strip(model) in model_tracking.keys()
        }
    )


def identify_missing(
    wp_data_dic: dict[str, str | int],
    data_lst: list[str],
    data_ids: list[int],
    ignore_case: bool = False,
):
    """This function is a simple algorithm that identifies when a tag or model must be manually recorded
    on WordPress, and it does that with two main assumptions:\n
    1) "If I have x tags/models, I must have x integers/IDs"\n
    2) "If there is a value with no ID, it just means that there is none and has to be created"\n
    Number 1 is exactly the first test for our values so, most of the time, if our results are consistent,
    this function returns None and no other operations are carried out. It acts exactly like a gatekeeper.
    In case the opposite is true, the function will examine why those IDs are missing and return the culprits (2).
    Our gatekeeper has an option to either enforce the case policy or ignore it, so I generally tell it to be
    lenient with tags (ignore_case = True) and strict with models (ignore_case = False), this is optional though.
    Ignore case was implemented based on the considerations that I have shared so far.

    :param wp_data_dic: ``dict[str, str | int]`` returned by either ``map_wp_model_id`` or ``tag_id_merger_dict`` from module ``integrations.wordpress_api``
    :param data_lst: ``list[str]`` tags or models
    :param data_ids: ``list[int]`` tag or model IDs.
    :param ignore_case: ``bool`` True, enforce case policy. Default False.
    :return: ``None`` or ``list[str]``
    """
    if len(data_lst) == len(data_ids):
        return None
    else:
        not_found: list[str] = []
        for item in data_lst:
            if ignore_case:
                item: str = item.lower()
                tags: list[str] = list(map(lambda tag: tag.lower(), wp_data_dic.keys()))
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
    :param thumbnail_name: ``str`` in case the user wants to upload different thumbnails and wishes to keep the names.
    :return: ``int`` (status code from requests)
    """
    thumbnail_dir: str = folder
    remote_data: requests = requests.get(remote_res)
    cs_conf = content_select_conf()
    if thumbnail_name != "":
        name: str = f"-{thumbnail_name.split('.')[0]}"
    else:
        name: str = thumbnail_name
    img_name = clean_filename(f"{slug}{name}", cs_conf.pic_fallback)
    with open(f"{thumbnail_dir}/{img_name}", "wb") as img:
        img.write(remote_data.content)

    if cs_conf.imagick:
        helpers.imagick(
            f"{thumbnail_dir}/{slug}{name}.{cs_conf.pic_fallback}",
            cs_conf.quality,
            cs_conf.pic_format,
        )
    else:
        pass

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
    bot_conf: ContentSelectConf = content_select_conf(),
    categs: list[int] | None = None,
    wpauth: WPAuth = wp_auth(),
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
    :param bot_conf: ``ContentSelectConf`` Bot configuration object
    :param categs: ``list[int]`` category numbers to be passed with the post information
    :param wpauth: ``WPAuth`` Object with the author information.
    :return: ``dict[str, str | int]``
    """
    author: int = int(wpauth.author_admin)
    payload_post: dict = {
        "slug": f"{vid_slug}",
        "status": f"{status_wp}",
        "type": "post",
        "link": f"{wpauth.full_base_url.strip('/')}/{vid_slug}/",
        "title": f"{vid_name}",
        "content": f'<p>{vid_description}</p><figure class="wp-block-image size-large"><a href="{banner_tracking_url}"><img decoding="async" src="{banner_img}" alt="{vid_name} | {partner_name} on {bot_conf.site_name}{bot_conf.domain_tld}"/></a></figure>',
        "excerpt": f"<p>{vid_description}</p>\n",
        "author": author,
        "featured_media": 0,
        "tags": tag_int_lst,
        "pornstars": model_int_lst,
    }

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
    wp_auth: WPAuth = wp_auth(),
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


def make_img_payload(
    vid_title: str,
    vid_description: str,
    bot_config: ContentSelectConf = content_select_conf(),
) -> dict[str, str]:
    """Similar to the make_payload function, this one makes the payload for the video thumbnails,
    it gives them the video description and focus key phrase, which is the video title plus a call to
    action in case that ALT text appears on the image search vertical, and they want to watch the video.

    :param vid_title: ``str`` self-explanatory
    :param vid_description: ``str`` self-explanatory
    :param bot_config: ``ContentSelectConf`` Uses general configuration options to customise payloads.
    :return: ``dict[str, str]``
    """
    # In case that the description is the same as the title, the program will send
    # a different payload to avoid keyword over-optimization.
    if vid_title == vid_description:
        img_payload: dict[str, str] = {
            "alt_text": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld}",
            "caption": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld}",
            "description": f"{vid_title} {bot_config.site_name}{bot_config.domain_tld}",
        }
    else:
        img_payload: dict[str, str] = {
            "alt_text": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld} - {vid_description}",
            "caption": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld} - {vid_description}",
            "description": f"{vid_title} on {bot_config.site_name}{bot_config.domain_tld} - {vid_description}",
        }
    return img_payload


def make_slug(
    partner: str,
    model: str | None,
    title: str,
    content: str,
    reverse: bool = False,
    partner_out: bool = False,
) -> str:
    """This function is a new approach to the generation of slugs inspired by the slug making
    mechanism from gallery_select.py. It takes in strings that will be transformed into URL slugs
    that will help us optimise the permalinks for SEO purposes.

    :param partner: ``str`` video partner
    :param model:  ``str`` video model
    :param title: ``str`` Video title
    :param content: ``str`` type of content, in this file it is simply `video` but it could be `pics` this parameter tells Google about the main content of the page.
    :param reverse: ``bool``  ``True`` if you want to place the video title in front of the permalink. Default ``False``
    :param partner_out: ``bool`` ``True`` if you want to build slugs without the partner name. Default ``False``.
    :return: ``str`` formatted string of a WordPress-ready URL slug.
    """
    filter_words: set[str] = {"at", "&", "and", "!", ",", "-", ""}
    title_sl: str = "-".join(
        [
            word.lower()
            for word in title.lower().split()
            if (
                re.match(r"[\w]+", word, flags=re.IGNORECASE)
                and word.lower() not in filter_words
            )
        ]
    )

    partner_sl: str = "-".join(clean_partner_tag(partner.lower()).split())
    try:
        model_sl: str = "-".join(
            [
                "-".join(name.split(" "))
                for name in list(map(lambda m: m.lower().strip(), model.split(",")))
            ]
        )

        content: str = f"-{content}" if content != "" or None else ""
        if reverse:
            return f"{title_sl}-{partner_sl}-{model_sl}{content}"
        elif partner_out:
            return f"{title_sl}-{model_sl}{content}"
        else:
            return f"{partner_sl}-{model_sl}-{title_sl}{content}"
    except AttributeError:
        # Model can be NoneType and crash the program if this is not handled.
        if reverse:
            return f"{title_sl}-{partner_sl}-{content}"
        elif partner_out:
            return f"{title_sl}-{content}"
        else:
            return f"{partner_sl}-{title_sl}-{content}"


def hot_file_sync(
    bot_config: ContentSelectConf | GallerySelectConf | EmbedAssistConf,
) -> bool:
    """I named this feature "Hot Sync" as it has the ability to modify the data structure we are using as a cached
    datasource and allows for more efficiency in keeping an up-to-date copy of all your posts.
    This function leverages the power of the caching mechanism defined
    in wordpress_api.py that dynamically appends new items in order and keeps track of cached pages with the
    total count of posts at the time of update. ``hot_file_sync`` just updates the JSON cache of the WP site and
    reloads the local cache configuration file to validate the changes.

    Hot Sync will write the changes once the new ones are validated and compared with the local config file.
    In other words, if it isn't right, the WP post file remains untouched.

    :param bot_config: ``ContentSelectConf`` or ``GallerySelectConf`` or ``EmbedAssistConf`` with configuration information.
    :return: ``bool`` - ``True`` if everything went well or raise ``HotFileSyncIntegrityError`` if the validation failed)
    """
    parent = (
        False
        if os.path.exists(f"./{clean_filename(bot_config.wp_cache_config, 'json')}")
        else True
    )
    if isinstance(bot_config, GallerySelectConf):
        wp_filename: str = helpers.clean_filename(bot_config.wp_json_photos, "json")
    else:
        wp_filename: str = helpers.clean_filename(bot_config.wp_json_posts, "json")

    sync_changes: list[dict[str, ...]] = wordpress_api.update_json_cache(
        photos=True if isinstance(bot_config, GallerySelectConf) else False
    )

    # Reload config
    config_json: dict[str, str] = helpers.load_json_ctx(bot_config.wp_cache_config)
    if len(sync_changes) == config_json[0][wp_filename]["total_posts"]:
        helpers.export_request_json(wp_filename, sync_changes, 1, parent=parent)
        logging.info(
            f"Exporting new WordPress cache config: {bot_config.wp_cache_config}"
        )
        logging.info("HotFileSync Successful")
        return True
    else:
        logging.critical("Raised HotFileSyncIntegrityError - Quitting...")
        raise HotFileSyncIntegrityError


def partner_select(
    partner_lst: list[str],
    banner_lsts: list[list[str]],
    db_name: str,
) -> tuple[str, list[str]]:
    """Selects partner and banner list based on their index order.
    As this function is based on index and order of elements, both lists should have the same number of elements.
    **Note: No longer in use since there are better implementations now**

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

    It is important to note that this function was designed at a time when the user had to
    manually select a database. However, with functions like ``content_select_db_match`` , the
    program will obtain the most appropriate database automatically. Despite the latter, ``select_guard``
    has been kept in place to alert the user of any errors that may arise and still serve the purpose
    that led to its creation.

    :param db_name: ``str`` user-selected database name
    :param partner: ``str`` user-selected partner offering
    :return: ``None`` If the assertion fails the execution will stop gracefully.
    """
    # Find the split character as I just need to get the first word of the name
    # to match it with partner selected by the user
    match_regex = re.findall(r"[\W_]+", db_name)[0]
    spl_dbname = lambda db: db.strip().split(match_regex)
    try:
        assert re.match(spl_dbname(db_name)[0], partner, flags=re.IGNORECASE)
    except AssertionError:
        logging.critical(
            f"Select guard detected issues for db_name: {db_name} partner: {partner} split: {match_regex}"
        )
        print("\nBe careful! Partner and database must match. Re-run...")
        print(f"The program selected {db_name} for partner {partner}.")
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
    looks like ``partner-name-content-type-date-in-ISO-format``; those filenames are further analysed by an algorithm
    that matches strings found in a lookup list.

    For more information on how this matching works and the algorithm behind it, refer to the documentation for
    ``match_list_mult`` and ``match_list_elem_date`` in the ``core.helpers`` module.

    **Note: As part of the above-mentioned naming convention, the files include a content type hint.
    This allows the algorithm to identify video or photo databases, depending on the module
    calling the function. However, this hint can be any word that you use consistently in your filenames.
    Also, if you want to access the file from a parent dir, either let the destination function handle it for you
    or specify it yourself. Everytime Python runs the file as a module or runs it on an interpreter outside your
    virtual environment, relative paths prove inefficient. However, this issue has been largely solved by using
    package notation with standard library and local implementations.**

    :param hint_lst: ``list[str]`` words/patterns to match.
    :param content_hint: ``str`` type of content, typically ``vids`` or ``photos``
    :param prompt_db: ``True`` if you want to prompt the user to select db. Default ``False``.
    :param folder: ``str`` where you want to look for files
    :param parent: ``True`` to search in parent dir, default set to ``False``.
    :return: ``tuple[Connection, Cursor, str, int]`` (database connection, database cursor, database name, common index int)
    """

    console = Console()

    available_files: list[str] = helpers.search_files_by_ext(
        "db", folder=folder, parent=parent
    )
    filtered_files: list[str] = helpers.match_list_elem_date(
        hint_lst,
        available_files,
        join_hints=(True, " ", "-"),
        ignore_case=True,
        strict=True,
    )

    relevant_content: list[str] = list(
        map(
            lambda indx: filtered_files[indx],
            helpers.match_list_mult(content_hint, filtered_files),
        )
    )

    if prompt_db:
        print(f"\nHere are the available database files:")
        for num, file in enumerate(relevant_content, start=1):
            print(f"{num}. {file}")
        print("\n")
    else:
        pass
    print("\n")
    for num, file in enumerate(hint_lst, start=1):
        console.print(f"{num}. {file}", style="bold green")

    try:
        select_partner: str = console.input(
            f"[bold yellow]\nSelect your partner now: [bold yellow]\n",
        )
        # I just need the first word to match the db.
        try:
            split_char = re.findall(r"[\W_]+", hint_lst[int(select_partner) - 1])[0]

            clean_hint: str = hint_lst[int(select_partner) - 1].split(split_char)[0]

        except IndexError:
            clean_hint: str = hint_lst[int(select_partner) - 1]

        rel_content: int = helpers.match_list_single(
            clean_hint, relevant_content, ignore_case=True
        )

        select_file: int = rel_content

        is_parent: str = (
            helpers.is_parent_dir_required(parent) if folder == "" else f"{folder}/"
        )
        db_path: str = f"{is_parent}{relevant_content[select_file]}"

        db_new_conn: sqlite3 = sqlite3.connect(db_path)
        db_new_cur: sqlite3 = db_new_conn.cursor()
        return (
            db_new_conn,
            db_new_cur,
            relevant_content[int(select_file)],
            select_file,
        )
    except (IndexError, ValueError):
        raise InvalidInput


def x_post_creator(description: str, post_url: str, post_text: str = "") -> int:
    """Create a post with a random action call for the X platform.
    Depending on your bot configuration, you can pass in your own post text and
    override the random call to action. If you just don't feel like typing and
    want to post without the randon text, the default value is an empty string.

    Set the ``x_posting_auto`` option in ``workflows_config.ini`` to ``False`` ,
    so that you get to type when you interact with the bots.

    :param description: ``str`` Video description
    :param post_url: ``str`` Video post url on WordPress
    :param post_text: ``str`` in certain circumstances
    :return: ``int`` POST request status code.
    """
    cs_conf = content_select_conf()
    site_name = cs_conf.site_name
    calls_to_action = [
        f"Watch more on {site_name}:",
        f"Take a quick look on {site_name}:",
        f"Watch the action for free on {site_name}:",
        f"Don't miss out. Watch now on {site_name}:",
        f"Don't miss out. Watch more on {site_name}:",
        f"Watch for free on {site_name}:",
        "Click below to watch for free:",
        "You won't need another video after this one:",
        f"{site_name} has it all for free:",
        f"All the Good stuff. Only on {site_name}:"
        "I bet you haven't watched this one:"
        "Well, you asked for it:",
        "I can't believe this is free:",
        f"Specially for you:",
        f"Check out {site_name} today:",
        "Watch today for free:",
        "You're missing out on the action:",
        "When you thought you've watch it all:",
        f"Brought to you by {site_name}:",
        "Watch now:",
        "Watch free:Click to watch full video:",
        "Don't miss out:",
    ]
    # Env variable "X_TOKEN" is assigned in function ``x_api.refresh_flow()``
    bearer_token = os.environ.get("X_TOKEN")
    if not post_text:
        post_text = f"{description} | {random.choice(calls_to_action)} {post_url}"
    else:
        post_text = f"{description} {post_text} {post_url}"
    request = x_api.post_x(post_text, bearer_token, XEndpoints())
    logging.info(f"Sent to X -> {post_text}")
    logging.info(f"X post metadata -> {request.json()}")
    return request.status_code


def telegram_send_message(
    description: str,
    post_url: str,
    bot_config: ContentSelectConf | EmbedAssistConf | GallerySelectConf,
    msg_text: str = "",
) -> int:
    """Set up a message template for the Telegram BotFather function ``send_message()``
    Parameters are self-explanatory.

    :param description: ``str``
    :param msg_text: ``str``
    :param post_url: ``str``
    :param bot_config: ``ContentSelectConf`` | ``EmbedAssistConf`` | ``GallerySelectConf``
    :return: ``int``
    """
    site_name = bot_config.site_name
    calls_to_action = [
        f"Watch more on {site_name}:",
        f"Take a quick look on {site_name}:",
        f"Watch the action for free on {site_name}:",
        f"Don't miss out. Watch now on {site_name}:",
        f"Don't miss out. Watch more on {site_name}:",
        f"Watch for free on {site_name}:",
        "Click below to watch for free:",
        "You won't need another video after this one:",
        f"{site_name} has it all for free:",
        f"All the Good stuff. Only on {site_name}:"
        "I bet you haven't watched this one:"
        "Well, you asked for it:",
        "I can't believe this is free:",
        f"Specially for you:",
        f"Check out {site_name} today:",
        "Watch today for free:",
        "You're missing out on the action:",
        "When you thought you've watch it all:",
        f"Brought to you by {site_name}:",
        "Watch now:",
        "Watch free:Click to watch full video:",
        "Don't miss out:",
    ]
    auto_mode = bot_config.telegram_posting_auto
    if auto_mode:
        msg_text = random.choice(calls_to_action)
    else:
        pass
    message = (
        f"{description} | {msg_text} {post_url}"
        if auto_mode
        else f"{description} {msg_text} {post_url}"
    )
    req = botfather_telegram.send_message(
        bot_father(), BotFatherCommands(), BotFatherEndpoints(), message
    )
    logging.info(f"Sent to Telegram -> {message}")
    logging.info(f"BotFather post metadata -> {req.json()}")
    return req.status_code


def wp_publish_checker(
    post_slug: str, cs_conf: ContentSelectConf | EmbedAssistConf | GallerySelectConf
) -> bool | None:
    """Check for the publication a post in real time by using iteration of the Hot File Sync
    algorithm. It will detect that you have effectively hit the publish button, so that functionality
    that directly depends on the post being online can take it from there.

    The function assigns environment variable ``"LATEST_POST"`` since objects
    present in this application do not usually work with fully qualified links because it is
    not necessary. This mechanism has also proven effective for manipulating pieces of information during runtime.

    :param post_slug: ``str`` self-explanatory
    :param cs_conf: ``ContentSelectConf`` | ``EmbedAssistConf`` | ``GallerySelectConf`` - Config objects
    :return: ``None`` | ``True``
    """
    retries = 0
    retry_offset = 1
    start_check = time.time()
    hot_sync = hot_file_sync(cs_conf)
    while hot_sync:
        posts_file = (
            cs_conf.wp_json_photos
            if isinstance(cs_conf, GallerySelectConf)
            else cs_conf.wp_json_posts
        )
        wp_postf = helpers.load_json_ctx(posts_file)
        slugs = wordpress_api.get_slugs(wp_postf)
        if post_slug in slugs:
            os.environ["LATEST_POST"] = wp_postf[0]["link"]
            end_check = time.time()
            h, min, secs = get_duration(end_check - start_check)
            logging.info(
                f"wp_publish_checker took -> hours: {h} mins: {min} secs: {secs} in {retries} retries"
            )
            return True

        time.sleep(retry_offset)
        retry_offset += 2
        retries += 1
        hot_sync = hot_file_sync(cs_conf)


def video_upload_pilot(
    wp_auth: WPAuth = wp_auth(),
    wp_endpoints: WPEndpoints = WPEndpoints,
    cs_config: ContentSelectConf = content_select_conf(),
    parent: bool = False,
) -> None:
    """Coordinate execution of all functions that interact with the video upload process.
    In other words, this function gives continuity to what ``workflows.update_mcash_chain`` does with
    the data processing and normalisation. Of course, that is just one way to put it since all other
    members in the module undertake a fraction of work, thus, each output is received and made meaningful here.

    :param wp_auth: ``WPAuth`` element provided by the ``core.config_mgr`` module. Set by default and bound to change based on the config file.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :param cs_config: ``ContentSelectConf`` Object that contains configuration options for this module.
    :param parent: ``True`` if you want to locate relevant files in the parent directory. Default False
    :return: ``None``
    """
    time_start = time.time()

    logging_setup(cs_config, __file__)
    logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}")

    console = Console()
    os.system("clear")
    with console.status(
        "[bold green] Warming up... [blink]┌(◎_◎)┘[/blink] [/bold green]\n",
        spinner="aesthetic",
    ):
        hot_file_sync(bot_config=cs_config)
        x_api.refresh_flow(x_auth(), XEndpoints())

    partners: list[str] = cs_config.partners.split(",")
    logging.info(f"Loading partners variable: {partners}")

    wp_posts_f: list[dict[str, ...]] = helpers.load_json_ctx(cs_config.wp_json_posts)
    logging.info(f"Reading WordPress Post cache: {cs_config.wp_json_posts}")

    wp_base_url: str = wp_auth.api_base_url
    logging.info(f"Using {wp_base_url} as WordPress API base url")

    db_conn, cur_dump, partner_db_name, partner_indx = content_select_db_match(
        partners, cs_config.content_hint, parent=parent
    )
    logging.info(
        f"Matched {partner_db_name} for {partners[partner_indx]} index {partner_indx}"
    )

    all_vals: list[tuple[str, ...]] = helpers.fetch_data_sql(
        cs_config.sql_query, cur_dump
    )
    logging.info(f"{len(all_vals)} elements found in database {partner_db_name}")

    # Prints out at the end of the uploading session.
    videos_uploaded: int = 0
    partner = partners[partner_indx]
    banners = asset_parser(cs_config, partner)

    select_guard(partner_db_name, partner)
    logging.info("Select guard cleared...")

    not_published_yet: list[tuple[str, ...]] = filter_published(all_vals, wp_posts_f)

    # You can keep on getting posts until this variable is equal to one.
    total_elems: int = len(not_published_yet)
    logging.info(f"Detected {total_elems} to be published for {partner}")

    os.system("clear")
    # Environment variable set in logging_setup()
    console.print(
        f"Session ID: {os.environ.get('SESSION_ID')}",
        style="bold yellow",
        justify="left",
    )
    console.print(
        f"\nThere are {total_elems} {partner} videos to be published...",
        style="bold red",
        justify="center",
    )
    time.sleep(2)

    thumbnails_dir = tempfile.TemporaryDirectory(prefix="thumbs", dir=".")
    logging.info(f"Created {thumbnails_dir.name} for thumbnail temporary storage")

    for num, vid in enumerate(not_published_yet):
        (title, *fields) = vid
        logging.info(f"Displaying on iteration {num} data: {vid}")
        description = fields[0]
        models = fields[1]
        tags = fields[2]
        date = fields[3]
        duration = fields[4]
        source_url = fields[5]
        thumbnail_url = fields[6]
        tracking_url = fields[7]
        partner_name = partner
        os.system("clear")
        console.print(
            f"Session ID: {os.environ.get('SESSION_ID')}",
            style="bold yellow",
            justify="left",
        )
        console.print(
            f"\n{' Review this post ':*^30}\n", style="bold yellow", justify="center"
        )
        console.print(title, style="green")
        console.print(description, style="green")
        console.print(f"Duration: {duration}", style="green")
        console.print(f"Tags: {tags}", style="green")
        console.print(f"Models: {models}", style="green")
        console.print(f"Date: {date}", style="green")
        console.print(f"Thumbnail URL: {thumbnail_url}", style="green")
        console.print(f"Source URL: {source_url}", style="green")
        # Centralized control flow
        add_post = console.input(
            "\n[bold cyan]Add post to WP? -> Y/N/ENTER to review next post: [/bold cyan]\n",
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {num} for processing")
            add_post = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further activity with the bot")
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                f"You have created {videos_uploaded} posts in this session!",
                style="bold yellow",
            )
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = get_duration(time_end - time_start)
            logging.info(
                f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
            )
            logging.info("Cleaning clipboard and temporary directories. Quitting...")
            logging.shutdown()
            break
        else:
            if num < total_elems - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "\nWe have reviewed all posts for this query.", style="bold red"
                )
                console.print(
                    "Try a different SQL query or partner. I am ready when you are. ",
                    style="bold red",
                )
                console.print(
                    f"You have created {videos_uploaded} posts in this session!",
                    style="bold yellow",
                )
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = get_duration(time_end - time_start)
                logging.info(
                    f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                )
                logging.info(
                    "Cleaning clipboard and temporary directories. Quitting..."
                )
                logging.shutdown()
                break

        # In rare occasions, the ``tags`` is None and the real tags are placed in the ``models`` variable
        # this special handling prevents crashes
        if tags:
            pass
        else:
            tags, models = models, tags

        if add_post:
            slugs: list[str] = [
                f"{fields[8]}-video",
                make_slug(partner, models, title, "video"),
                make_slug(partner, models, title, "video", reverse=True),
                make_slug(partner, models, title, "video", partner_out=True),
            ]

            console.print("\n--> Available slugs:\n", style="bold yellow")

            for n, slug in enumerate(slugs, start=1):
                console.print(f"{n}. -> {slug}", style="bold green")
            console.print("--> Enter #5 to provide a custom slug", style="bold yellow")

            match console.input("[bold magenta]\nSelect your slug: [/bold magenta]\n"):
                case "1":
                    wp_slug: str = slugs[0]
                case "2":
                    wp_slug: str = slugs[1]
                case "3":
                    wp_slug: str = slugs[2]
                case "4":
                    wp_slug: str = slugs[3]
                case "5":
                    # Copy the default slug for editing
                    pyclip.copy(slugs[3])
                    console.print("Provide a new slug: ", style="bold ")
                    wp_slug: str = input()
                case _:
                    # TODO: Add ``default_slug`` option to config file.
                    # Smart slug by default (partner_out).
                    wp_slug: str = slugs[3]

            logging.info(f"WP Slug - Selected: {wp_slug}")
            tag_prep: list[str] = [tag.strip() for tag in tags.split(",")]

            # Making sure that the partner tag does not have apostrophes
            partner_tag: str = clean_partner_tag(partner.lower())
            tag_prep.append(partner_tag)
            tag_ints: list[int] = get_tag_ids(wp_posts_f, tag_prep, "tags")
            all_tags_wp: dict[str, str] = wordpress_api.tag_id_merger_dict(wp_posts_f)
            tag_check: list[str] | None = identify_missing(
                all_tags_wp, tag_prep, tag_ints, ignore_case=True
            )
            if tag_check is None:
                # All tags have been found and mapped to their IDs.
                pass
            else:
                for tag in tag_check:
                    console.print(
                        f"ATTENTION --> Tag: {tag} not on WordPress.", style="bold red"
                    )
                    console.print(
                        "--> Copying missing tag to your system clipboard.",
                        style="bold yellow",
                    )
                    console.print(
                        "Paste it into the tags field as soon as possible...\n",
                        style="bold yellow",
                    )
                    logging.warning(f"Missing tag detected: {tag}")
                    pyclip.detect_clipboard()
                    pyclip.copy(tag)

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
                all_models_wp, model_prep, calling_models
            )

            if new_models is None or model_prep[0] == "model-not-found":
                # Maybe the post does not include a model.
                pass
            else:
                for girl in new_models:
                    console.print(
                        f"ATTENTION! --> Model: {girl} not on WordPress.",
                        style="bold red",
                    )
                    console.print(
                        "--> Copying missing model name to your system clipboard.",
                        style="bold yellow",
                    )
                    console.print(
                        "Paste it into the Pornstars field as soon as possible...\n",
                        style="bold yellow",
                    )
                    logging.warning(f"Missing model: {girl}")
                    pyclip.detect_clipboard()
                    pyclip.copy(girl)

            # NaiveBayes/MaxEnt classification for titles, descriptions, and tags
            class_title = classify_title(title)
            class_description = classify_description(description)
            class_tags = classify_tags(tags)
            class_title.union(class_description)
            class_title.union(class_tags)
            consolidate_categs = list(class_title)
            logging.info(f"Suggested categories ML: {consolidate_categs}")

            console.print(
                " \n** I think these categories are appropriate: **\n",
                style="bold yellow",
            )
            for num, categ in enumerate(consolidate_categs, start=1):
                console.print(f"{num}. {categ}", style="green")

            match console.input(
                "[bold yellow]\nEnter the category number or type in to look for another category in the site: [bold yellow]\n"
            ):
                case _ as option:
                    try:
                        sel_categ = consolidate_categs[int(option) - 1]
                        logging.info(f"User selected category: {sel_categ}")
                    except ValueError or IndexError:
                        sel_categ = option
                        logging.info(f"User typed in category: {option}")

            categ_ids = get_tag_ids(wp_posts_f, [sel_categ], preset="categories")

            console.print("\n--> Making payload...", style="bold green")
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
                categs=categ_ids,
            )
            logging.info(f"Generated payload: {payload}")
            console.print("--> Fetching thumbnail...", style="bold green")

            # Check whether ImageMagick conversion has been enabled in config.
            pic_format = (
                cs_config.pic_format if cs_config.imagick else cs_config.pic_fallback
            )
            thumbnail = clean_filename(wp_slug, pic_format)
            logging.info(f"Thumbnail name: {thumbnail}")

            try:
                fetch_thumbnail(thumbnails_dir.name, wp_slug, thumbnail_url)
                console.print(
                    f"--> Stored thumbnail {thumbnail} in cache folder {os.path.relpath(thumbnails_dir.name)}",
                    style="bold green",
                )
                console.print(
                    "--> Uploading thumbnail to WordPress Media...", style="bold green"
                )
                console.print(
                    "--> Adding image attributes on WordPress...", style="bold green"
                )
                img_attrs: dict[str, str] = make_img_payload(title, description)
                upload_img: int = wordpress_api.upload_thumbnail(
                    wp_base_url,
                    [wp_endpoints.media],
                    f"{thumbnails_dir.name}/{thumbnail}",
                    img_attrs,
                )
                logging.info(f"Image Attrs: {img_attrs}")

                # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is
                # the case. More information in integrations.wordpress_api.upload_thumbnail docs

                if upload_img == 500:
                    logging.warning(
                        f"Defective thumbnail - Bot abandoned current flow."
                    )
                    console.print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually.",
                        style="bold red",
                    )
                    console.print(
                        "--> Proceeding to the next post...\n", style="bold green"
                    )
                    continue
                elif upload_img == (200 or 201):
                    os.remove(removed_img := f"{thumbnails_dir.name}/{thumbnail}")
                    logging.info(f"Uploaded and removed: {removed_img}")
                else:
                    pass

                console.print(
                    f"--> WordPress Media upload status code: {upload_img}",
                    style="bold green",
                )
                console.print("--> Creating post on WordPress", style="bold green")
                push_post = wordpress_api.wp_post_create([wp_endpoints.posts], payload)
                logging.info(f"WordPress post push status: {push_post}")
                console.print(
                    f"--> WordPress status code: {push_post}", style="bold green"
                )

                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(source_url)
                pyclip.copy(title)
                console.print(
                    "--> Check the post and paste all you need from your clipboard.",
                    style="bold green",
                )
                if cs_config.x_posting_enabled or cs_config.telegram_posting_enabled:
                    status_msg = "Checking WP status and preparing for social sharing."
                    with console.status(
                        f"[bold green]{status_msg} [blink]ε= ᕕ(⎚‿⎚)ᕗ[blink] [/bold green]\n",
                        spinner="earth",
                    ):
                        is_published = wp_publish_checker(wp_slug, cs_config)
                    if is_published:
                        if cs_config.x_posting_enabled:
                            logging.info("X Posting - Enabled in workflows config")
                            if cs_config.x_posting_auto:
                                logging.info("X Posting Automatic detected in config")
                                # Environment "LATEST_POST" variable assigned in wp_publish_checker()
                                x_post_create = x_post_creator(
                                    description, os.environ.get("LATEST_POST")
                                )
                            else:
                                post_text = console.input(
                                    "[bold yellow]Enter your additional X post text here or press enter to use default configs: [bold yellow]\n"
                                )
                                logging.info(
                                    f"User entered custom post text: {post_text}"
                                )
                                x_post_create = x_post_creator(
                                    description,
                                    os.environ.get("LATEST_POST"),
                                    post_text=post_text,
                                )

                                # Copy custom post text for the following prompt
                                pyclip.detect_clipboard()
                                pyclip.copy(post_text)

                            if x_post_create == 201:
                                console.print(
                                    "--> Post has been published on WP and shared on X.\n",
                                    style="bold yellow",
                                )
                            else:
                                console.print(
                                    f"--> There was an error while trying to share on X.\n Status: {x_post_create}",
                                    style="bold red",
                                )
                            logging.info(f"X post status code: {x_post_create}")

                        if cs_config.telegram_posting_enabled:
                            logging.info(
                                "Telegram Posting - Enabled in workflows config"
                            )
                            if cs_config.telegram_posting_auto:
                                logging.info(
                                    "Telegram Posting Automatic detected in config"
                                )
                                telegram_msg = telegram_send_message(
                                    description,
                                    os.environ.get("LATEST_POST"),
                                    cs_config,
                                )
                            else:
                                post_text = console.input(
                                    "[bold yellow]Enter your additional Telegram message here or press enter to use default configs: [bold yellow]\n"
                                )
                                telegram_msg = telegram_send_message(
                                    description,
                                    os.environ.get("LATEST_POST"),
                                    cs_config,
                                    msg_text=post_text,
                                )

                            if telegram_msg == 200:
                                console.print(
                                    # Env variable assigned in botfather_telegram.send_message()
                                    f"--> Message sent to Telegram {os.environ.get('T_CHAT_ID')}",
                                    style="bold yellow",
                                )
                            else:
                                console.print(
                                    f"--> There was an error while trying to communicate with Telegram.\n Status: {telegram_msg}",
                                    style="bold red",
                                )
                            logging.info(
                                f"Telegram message status code: {telegram_msg}"
                            )
                else:
                    pass
                videos_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {str(e)} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this post... *",
                    style="bold red",
                )
                if console.input(
                    "\n[bold green] Do you want to continue? Y/ENTER to exit: [bold green]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {str(e)}")
                    continue
                else:
                    logging.info(f"User declined after catching {str(e)}")
                    console.print(
                        f"You have created {videos_uploaded} posts in this session!",
                        style="bold yellow",
                    )
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    logging.info(
                        f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                    )
                    logging.info(
                        "Cleaning clipboard and temporary directories. Quitting..."
                    )
                    logging.shutdown()
                    break
            if num < total_elems - 1:
                next_post = console.input(
                    "[bold cyan]\nNext post? -> N/ENTER to review next post: [/bold cyan]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    logging.info("User declined further activity with the bot")
                    # The terminating parts add this function to avoid
                    # tracebacks from pyclip and enable cross-platform support.
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    console.print(
                        f"You have created {videos_uploaded} posts in this session!",
                        style="bold yellow",
                    )
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = get_duration(time_end - time_start)
                    logging.info(
                        f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                    )
                    logging.info(
                        "Cleaning clipboard and temporary directories. Quitting..."
                    )
                    logging.shutdown()
                    break
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                console.print(
                    "\nWe have reviewed all posts for this query.", style="bold red"
                )
                console.print(
                    "Try a different query and run me again.", style="bold red"
                )
                thumbnails_dir.cleanup()
                console.print(
                    f"You have created {videos_uploaded} posts in this session!",
                    style="bold yellow",
                )
                time_end = time.time()
                h, mins, secs = get_duration(time_end - time_start)
                logging.info(
                    f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                )
                logging.info(
                    "Cleaning clipboard and temporary directories. Quitting..."
                )
                logging.shutdown()
        else:
            logging.info(f"List exhausted. State: num={num} total_elems={total_elems}")
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                "\nWe have reviewed all posts for this query.", style="bold red"
            )
            console.print(
                "Try a different SQL query or partner. I am ready when you are. ",
                style="bold red",
            )
            console.print(
                f"You have created {videos_uploaded} posts in this session!",
                style="bold yellow",
            )
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = get_duration(time_end - time_start)
            logging.info(
                f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
            )
            logging.info("Cleaning clipboard and temporary directories. Quitting...")
            logging.shutdown()
            break


def main(**kwargs):
    try:
        video_upload_pilot(**kwargs)
    except KeyboardInterrupt:
        logging.critical(f"KeyboardInterrupt exception detected")
        logging.info("Cleaning clipboard and temporary directories. Quitting...")
        print("Goodbye! ಠ‿↼")
        pyclip.detect_clipboard()
        pyclip.clear()
        # When quit is called, temp dirs will be automatically cleaned.
        logging.shutdown()
        quit()


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

    args_cli = arg_parser.parse_args()

    main(parent=args_cli.parent)
