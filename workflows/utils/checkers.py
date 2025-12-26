# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Workflow Checkers module

This module is responsible for checking WordPress taxonomy elements, match them
with their numerical values and return them to the calling workflow.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import asyncio
import logging
import re
import time
from collections import deque
from typing import List, Dict, Optional, Literal

import aiohttp

# Third-party imports
import pyclip
from rich.console import Console

# Local imports
from core.exceptions.util_exceptions import UnsupportedParameter
from core.utils.interfaces import WordFilter
from postwizard_sdk.builders.taxonomy_builder import TaxonomyNestedPayload
from postwizard_sdk.models.client_schema import Taxonomy
from postwizard_sdk.utils.auth import PostWizardAuth
from wordpress import WordPress
from wordpress.models.taxonomies import WPTaxonomyMarker, WPTaxonomyValues
from workflows.utils.filtering import identify_missing
from workflows.utils.logging import ConsoleStyle
from postwizard_sdk.utils.operations import add_taxonomy


def get_model_ids(wordpress_site: WordPress, model_lst: List[str]) -> List[int]:
    """This function is crucial to obtain the WordPress element ID ``model`` to be able
    to communicate and tell WordPress what we want. It takes in a list of model names and filters
    through the entire WP dataset to locate their ID and return it back to the controlling function.
    None if the value is not found in the dataset.
    This function enforces Title case in matches since models are people and proper names are generally
    in title case, and it is also the case in the data structure that local module ``integrations.wordpress_api`` returns.
    Further testing is necessary to know if this case convention is always enforced, so consistency is key here.

    :param wordpress_site: ``WordPress`` class instance responsible for managing all the
                             WordPress site data.
    :param model_lst: ``List[str]`` models' names
    :return: ``List[int]`` (corresponding IDs)
    """
    model_tracking: Dict[str, int] = wordpress_site.map_wp_class_id(
        WPTaxonomyMarker.MODELS, WPTaxonomyValues.MODELS
    )
    title_strip = lambda model: model.title().strip()  # noqa: E731
    return list(
        {
            model_tracking[title_strip(model)]
            for model in model_lst
            if title_strip(model) in model_tracking.keys()
        }
    )


def model_checker(
    wordpress_site: WordPress,
    model_prep: List[str],
    add_missing: bool = False,
    retries: int = 3,
    interactive=True,
) -> Optional[List[int]]:
    """
    Share missing model checking behaviour accross modules.
    Console logging is expected with this function.

    :param wordpress_site: ``WordPress`` class instance
    :param model_prep: ``list[str]`` - Model tag list without delimiters
    :param add_missing: ``bool`` - Whether to add missing models to the WordPress site via PostWizard
    :param retries: ``int`` - Number of retries to attempt when adding a missing model via PostWizard
    :param interactive: ``bool`` - Whether to interact with the user when adding a missing model
    :return: ``list[int]`` - List of model integer ids in the WordPress site.
    """
    if not model_prep:
        # Maybe the post does not include a model.
        return None
    else:
        console = Console()
        calling_models: List[int] = get_model_ids(wordpress_site, model_prep)
        all_models_wp: Dict[str, int] = wordpress_site.map_wp_class_id(
            WPTaxonomyMarker.MODELS, WPTaxonomyValues.MODELS
        )
        new_models: Optional[List[str]] = identify_missing(
            all_models_wp, model_prep, calling_models
        )

    if new_models is None:
        return calling_models
    else:
        for girl in new_models:
            if not add_missing:
                if interactive:
                    console.print(
                        f"ATTENTION! --> Model: {girl} not on WordPress.",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                    console.print(
                        "--> Copying missing model name to your system clipboard.",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                    console.print(
                        "Paste it into the Pornstars field as soon as possible...\n",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                logging.warning(f"Missing model: {girl}")
                pyclip.detect_clipboard()
                pyclip.copy(girl)
            else:
                new_model = TaxonomyNestedPayload()
                if girl:
                    if interactive:
                        console.print(
                            f'Adding new model: "{girl}" to WordPress...',
                            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                        )
                    new_model.term(girl).taxonomy_name(Taxonomy.MODEL)
                    retry_count = 0
                    while True:
                        resulting_term_id = add_taxonomy(new_model)
                        if resulting_term_id != -1:
                            calling_models.append(resulting_term_id)
                            logging.info(
                                f'Called PostWizard to add model: "{girl}" - Resulting in {resulting_term_id} - Success...'
                            )
                            break
                        else:
                            time.sleep(1)
                            PostWizardAuth.reset_auth()
                            retry_count += 1
                            logging.warning(
                                f"Failed to add model: {girl} - Retrying ({retry_count}/{retries})..."
                            )
                            if retry_count >= retries:
                                console.print(
                                    f"Failed to add model: {girl} - Max retries reached ({retry_count}/{retries})...",
                                    style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                                )
                                break
                    new_model.clear()
    return calling_models


def tag_checker_print(
    console_obj: Console,
    wordpress_site: WordPress,
    tag_prep: List[str],
    add_missing: bool = False,
    interactive: bool = True,
    photo_tags: bool = False,
) -> List[int]:
    """
    Checks the tags in the given WordPress posts and identifies any missing tags, printing
    messages for missing tags as necessary and copying those to the system clipboard.

    :param console_obj: ``rich.console.Console`` The console object used for styled text output
    :param wordpress_site: ``WordPress`` An instance of the WordPress class
    :param tag_prep: ``list[str]`` A list of prepared tags to be checked
    :param add_missing: ``bool`` - Whether to add missing tags to the WordPress site via PostWizard
    :param interactive: ``bool`` - Whether to print messages for the user to the console
    :param photo_tags: ``bool`` - Whether to process the tags for a photo set
    :return: ``list[int]`` A list of tag IDs corresponding to the provided tags
    """
    tag_ints: List[int] = get_tag_ids(
        wordpress_site, tag_prep, "tags" if not photo_tags else "photos"
    )
    all_tags_wp: Dict[str, int] = wordpress_site.tag_id_merger_dict()
    tag_check: Optional[List[str]] = identify_missing(
        all_tags_wp, tag_prep, tag_ints, ignore_case=True
    )

    if tag_check is None:
        # All tags have been found and mapped to their IDs.
        pass
    else:
        for tag in tag_check:
            if not add_missing:
                if interactive:
                    console_obj.print(
                        f"ATTENTION --> Tag: {tag} not on WordPress.",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                    console_obj.print(
                        "--> Copying missing tag to your system clipboard.",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                    console_obj.print(
                        "Paste it into the tags field as soon as possible...\n",
                        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                    )
                    pyclip.detect_clipboard()
                    pyclip.copy(tag)
                logging.warning(f"Missing tag detected: {tag}")
            else:
                new_tag = TaxonomyNestedPayload()
                if tag:
                    if interactive:
                        console_obj.print(
                            f'Adding new tag: "{tag}" to WordPress...',
                            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
                        )
                    new_tag.term(tag).taxonomy_name(Taxonomy.TAG)
                    resulting_term_id = add_taxonomy(new_tag)
                    if resulting_term_id != -1:
                        tag_ints.append(resulting_term_id)
                    logging.info(
                        f'Called PostWizard to add tag: "{tag}" - Resulting in Term ID: {resulting_term_id}'
                    )
                    new_tag.clear()
    return tag_ints


def get_tag_ids(
    wordpress_site: WordPress,
    tag_lst: List[str],
    preset: Literal["models", "tags", "categories", "photos"],
) -> List[int]:
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

    :param wordpress_site: ``WordPress`` class instance responsible for managing all the
                             WordPress site data.
    :param tag_lst: ``List[str]`` a list of tags
    :param preset: ``str`` the preset to use for the mapping of tags
    :return: ``List[int]``
    """
    match preset:
        case "models":
            taxonomies = (WPTaxonomyMarker.MODELS, WPTaxonomyValues.MODELS)
        case "tags":
            taxonomies = (WPTaxonomyMarker.TAG, WPTaxonomyValues.TAGS)
        case "photos":
            taxonomies = (WPTaxonomyMarker.PHOTOS, WPTaxonomyValues.PHOTOS)
        case "categories":
            taxonomies = (WPTaxonomyMarker.CATEGORY, WPTaxonomyValues.CATEGORIES)
        case _ as err:
            raise UnsupportedParameter(err)

    tag_tracking: Dict[str, int] = wordpress_site.map_wp_class_id(
        taxonomies[0], taxonomies[1]
    )

    clean_tag = lambda tag: WordFilter(delimiter=" ").add_word(tag).filter()  # noqa: E731
    # Result must be: colourful-skies/great -> colourful skies great
    cl_tags = list(map(clean_tag, tag_lst))

    # It is crucial that tags don't have any special characters
    # before processing them with ``tag_tracking``.
    matched_keys: List[str] = [
        wptag
        for wptag in tag_tracking.keys()
        for tag in cl_tags
        if re.fullmatch(tag, wptag, flags=re.IGNORECASE)
        if tag
    ]
    return list({tag_tracking[tag] for tag in matched_keys})


def link_testing_massive(post_links):
    failed_links = deque()
    semaphore = asyncio.Semaphore(10)
    d_lock = asyncio.Lock()

    async def mutate_deque(item):
        async with d_lock:
            failed_links.append(item)

    async def test_link(session, link):
        async with semaphore:
            try:
                async with session.get(link) as response:
                    if response.status >= 400:
                        await mutate_deque(link)
            except Exception as e:
                print(f"Got Exceptions: {e!r}")

    async def run_all():
        async with aiohttp.ClientSession(
            headers={
                "keep-alive": "True",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
            },
            timeout=aiohttp.ClientTimeout(30),
            connector=aiohttp.TCPConnector(
                ssl=False, ssl_shutdown_timeout=10.0, force_close=True
            ),
        ) as session:
            tasks = [
                test_link(session, link) for link in post_links if link is not None
            ]
            await asyncio.gather(*tasks)

    asyncio.run(run_all())
    return list(failed_links)
