"""
Workflows Filtering module

This module is responsible for filtering data related to posts, provide information about
published posts and missing taxonomies.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import re

from typing import List, Tuple, Dict, Union

# Local imports
from core.utils.strings import split_char
from wordpress import WordPress
from wordpress.models.taxonomies import WPTaxonomyMarker, WPTaxonomyValues
from workflows.interfaces import EmbedsMultiSchema


def published_json(
    title: str, wordpress_site: WordPress, yoast_support: bool = False
) -> bool:
    """This function leverages the power of a local implementation that specialises
    in getting, manipulating and filtering WordPress API post information in JSON format.
    After getting the posts from the local cache, the function filters each element using
    the ``re`` module to find matches to the title passed in as a parameter. After all that work,
    the function returns a boolean; True if the title was found and that just suggests
    that such a title is already published, or there is a post with the same title.

    Ideally, we can benefit from a different and more accurate filter for this purpose, however,
    it is important for the objectives of this project that all post titles are unique and that, inevitably,
    delimits the purpose and approach of this method. For now, this behaviour of title-only matching is desirable.

    :param title: ``str`` lookup term, in this case a ``title``
    :param wordpress_site: ``WordPress`` class instance responsible for managing all the
                             WordPress site data.
    :param yoast_support: ``bool`` Enable Yoast SEO support for parsing.
    :return: ``bool`` True if one or more matches is found, False if the result is None.
    """
    post_titles: List[str] = wordpress_site.get_post_titles_local(
        yoast_support=yoast_support
    )

    results: List[str] = [vid_name for vid_name in post_titles if title in post_titles]
    if len(results) >= 1:
        return True
    else:
        return False


def filter_published(
    all_videos: List[Tuple[str, ...]], wordpress_site: WordPress
) -> List[Tuple[str, ...]]:
    """``filter_published`` does its filtering work based on the ``published_json`` function.
    Actually, the ``published_json`` is the brain behind this function and the reason why I decided to
    separate brain and body, as it were, is modularity. I want to be able to modify the classification rationale
    without affecting the way in which iterations are performed, unless I intend to do so specifically.
    If this function fails, then I have an easier time to identify the culprit.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles that will be taken into consideration by the ``video_upload_pilot`` (later) for their suggestion and publication.

    :param all_videos: ``List[tuple]`` usually resulting from the SQL database query values.
    :param wordpress_site: ``WordPress`` class instance responsible for managing all the
                             WordPress site data.
    :return: ``list[tuple]`` with the new filtered values.
    """
    not_published: List[Tuple[str, ...]] = []
    word_regex = re.compile(r"^(?!https?)\w+\b")
    for elem in all_videos:
        for item in elem:
            try:
                if word_regex.match(item):
                    if published_json(item, wordpress_site):
                        break
                    else:
                        not_published.append(elem)
                        break
            except TypeError:
                continue
    return not_published


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
    # match_regex = re.findall(r"[\W_]+", db_name)[0]
    spl_dbname = lambda db: db.strip().split(split_char(db))  # noqa: E731
    try:
        assert re.match(spl_dbname(db_name)[0], partner, flags=re.IGNORECASE)
    except AssertionError:
        logging.critical(
            f"Select guard detected issues for db_name: {db_name} partner: {partner} split: {spl_dbname(db_name)}"
        )
        print("\nBe careful! Partner and database must match. Re-run...")
        print(f"The program selected {db_name} for partner {partner}.")
        exit(0)


def identify_missing(
    wp_data_dic: Dict[str, Union[str, int]],
    data_lst: List[str],
    data_ids: List[int],
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

    :param wp_data_dic: ``Dict[str, str | int]`` returned by either ``map_wp_model_id`` or ``tag_id_merger_dict`` from an instace of ``WordPress``
    :param data_lst: ``List[str]`` tags or models
    :param data_ids: ``List[int]`` tag or model IDs.
    :param ignore_case: ``bool`` -> ``True``, enforce case policy. Default ``False``.
    :return: ``None`` or ``List[str]``
    """
    if len(data_lst) == len(data_ids):
        return None
    else:
        not_found: List[str] = []
        for item in data_lst:
            if ignore_case:
                item: str = item.lower()
                tags: List[str] = list(map(lambda tag: tag.lower(), wp_data_dic.keys()))
                if item not in tags:
                    not_found.append(item)
            else:
                try:
                    wp_data_dic[item]
                except KeyError:
                    not_found.append(item)
        return not_found


def filter_published_embeds(
    wordpress_site: WordPress, videos: List[Tuple[str, ...]], db_cur
) -> List[Tuple[str, ...]]:
    """filter_published does its filtering work based on the published_json function.
    It is based on a similar version from module `content_select`, however, this one is adapted to embedded videos
    and a different db schema.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles.

    :param videos: ``list[tuple[str, ...]]`` usually resulting from the SQL database query values.
    :param wordpress_site: ``WordPress`` instance responsible for managing all the
                             WordPress site data.
    :param db_cur: ``sqlite3`` - Active database cursor
    :return: ``list[tuple[str, ...]]`` with the new filtered values.
    """
    db_interface = EmbedsMultiSchema(db_cur)
    post_titles: List[str] = wordpress_site.get_post_titles_local(yoast_support=True)

    not_published: List[Tuple] = []
    for elem in videos:
        db_interface.load_data_instance(elem)
        vid_title = db_interface.get_title()
        if vid_title in post_titles:
            continue
        else:
            not_published.append(elem)
    return not_published


def filter_relevant(
    all_galleries: List[Tuple[str, ...]],
    wordpress_posts_site: WordPress,
    wordpress_photos_site: WordPress,
) -> List[Tuple[str, ...]]:
    """Filter relevant galleries by using a simple algorithm to identify the models in
    each photo set and returning matches to the user. It is an experimental feature because it
    does not always work, specially when some image sets use the full name of the model and that
    makes it difficult for this simple algorithm to work.
    This could be reimplemented in a different (more efficient) manner, however,
    I do not believe it is a critical feature.

    :param all_galleries: ``list[tuple[str, ...]`` typically returned by a database query response.
    :param wordpress_posts_site: ``WordPress`` instance
    :param wordpress_photos_site: ``WordPress`` instance
    :return: ``list[tuple[str, ...]]`` Image sets related to models present in the WP site.
    """
    models_set: set[str] = set(
        wordpress_posts_site.map_wp_class_id(
            WPTaxonomyMarker.MODELS, WPTaxonomyValues.MODELS
        ).keys()
    )
    not_published_yet = []
    for elem in all_galleries:
        (title, *fields) = elem
        model_in_set = False
        title_split = title.split(" ")
        for word in title_split:
            if word not in models_set:
                continue
            else:
                model_in_set = True
                break

        if not published_json(title, wordpress_photos_site, False) and model_in_set:
            not_published_yet.append(elem)
        else:
            continue
    return not_published_yet
