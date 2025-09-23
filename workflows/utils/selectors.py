"""
Workflows Selectors Module

This module contains functions for facilitating element selection from lists and other data structures
where user input is required.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import random
import re
from typing import List, Tuple, Optional

# Third-party imports
from rich.console import Console

# Local imports
from ml_engine import classify_title, classify_description, classify_tags
from wordpress import WordPress
from workflows.utils.checkers import get_tag_ids
from workflows.utils.logging import ConsoleStyle


def partner_select(
    partner_lst: List[str],
    banner_lsts: List[List[str]],
) -> Tuple[str, List[str]]:
    """Selects partner and banner list based on their index order.
    As this function is based on index and order of elements, both lists should have the same number of elements.
    **Note: No longer in use since there are better implementations now**

    :param partner_lst: ``List[str]`` - partner offers
    :param banner_lsts: ``List[list[str]]`` list of banners to select from.
    :return: ``tuple[str, List[str]]`` partner_name, banner_list
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


def slug_getter(console_obj: Console, slugs: List[str]) -> Optional[str]:
    """
    Retrieve a slug based on user input from provided options or get a custom one.
    Handles edge cases when no slugs are available or user input is invalid.

    :param console_obj: ``rich.console.Console`` Console object for printing and user interaction
    :param slugs: ``list[str]`` List of available slug options to choose from
    :return: ``str`` The selected slug, either from the provided list or a custom one
    """
    prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
    user_attention_style = ConsoleStyle.TEXT_STYLE_ATTENTION.value
    slug_entry_style = ConsoleStyle.TEXT_STYLE_ACTION.value

    def print_slugs(slug_list: List[str]):
        console_obj.print("\n--> Available slugs:\n", style=user_attention_style)

        for n, slug in enumerate(slug_list, start=1):
            console_obj.print(f"{n}. -> {slug}", style=slug_entry_style)
        console_obj.print(
            "--> Provide a custom slug or pick a slug number",
            style=user_attention_style,
        )

        slug_option = console_obj.input(
            f"[{prompt_style}]\nSelect your slug: [/{prompt_style}]\n"
        )
        return slug_option

    def slug_getter_persist(slug_list: List[str]) -> str:
        user_slug = ""
        while not user_slug:
            if len(slug_list) != 0:
                user_slug = print_slugs(slug_list)
                if re.match(r"^\d+$", user_slug):
                    try:
                        return slug_list[int(user_slug) - 1]
                    except (IndexError, ValueError):
                        console_obj.print(
                            "Invalid option! Choosing random slug...",
                            style=ConsoleStyle.TEXT_STYLE_WARN.value,
                        )
                        user_slug = random.choice(slug_list)
                        logging.info(f"Chose random slug: {user_slug} automatically")
                        return user_slug
                elif re.match(r"^\w+", user_slug):
                    logging.info(f"User-provided slug: {user_slug} used")
                    console_obj.print(
                        f"Using custom slug: {user_slug}", style=user_attention_style
                    )
                    return user_slug
            else:
                logging.critical("No slugs were provided in controlling function.")
                console_obj.print(
                    " -> Provide a custom slug for the post now: \n", style=prompt_style
                )
                user_slug = input()
                if user_slug:
                    return user_slug
                else:
                    continue

    return slug_getter_persist(slugs)


def pick_classifier(
    console_obj: Console,
    wordpress_site: WordPress,
    title: str,
    description: str,
    tags: str,
) -> List[int]:
    """
    Picks a classifier for content selection based on user input and automatically assigns relevant categories.

    :raises ValueError: If an invalid option is chosen by the user.
    :param console_obj: The rich.console.Console object to print output.
    :param wordpress_site: An instance of the WordPress class.
    :param title: The title of the content being selected.
    :param description: A short description of the content.
    :param tags: The relevant tags for the content.
    :return: None
    """

    def print_options(option_lst, print_delim: bool = False):
        for opt, classifier in enumerate(option_lst, start=1):
            console_obj.print(
                f"{opt}. {classifier.title() if isinstance(classifier, str) else classifier}",
                style=ConsoleStyle.TEXT_STYLE_DEFAULT.value,
            )
        if print_delim:
            console_obj.print(f"{'*':=^35}")

    prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
    classifiers = [
        classify_title(title),
        classify_description(description),
        classify_tags(tags),
    ]

    classifier_str_lst: List[str] = list(locals().keys())[2:5]
    classifier_options = [categs for categs in classifiers if categs]

    option = ""
    console_obj.print(
        "\nAvailable Machine Learning classifiers: \n",
        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
    )

    print_options(classifier_str_lst)
    peek = re.compile("peek", re.IGNORECASE)
    rand = re.compile(r"rando?m?", re.IGNORECASE)
    number = re.compile(r"\d+")
    while not option:
        match console_obj.input(
            f"\n[{prompt_style}]Pick your classifier:  (Type in the 'peek' to open all classifiers or 'random' to let me choose for you)[/{prompt_style}]\n"
        ):
            case str() as p if peek.findall(p):
                print_options(classifier_options, print_delim=True)
                print_options(classifier_str_lst)
                option = console_obj.input(
                    f"\n[{prompt_style}]Your choice:[/{prompt_style}]\n"
                )
            case str() as r if rand.findall(r):
                option = random.choice(classifier_options)
            case str() as n if number.findall(n):
                if option_number := int(n) <= len(classifier_str_lst) + 1:
                    option = option_number + 1
            case _:
                continue
    try:
        # Here ``option`` can be either ``str`` or ``set[str]``
        categories = (
            list(classifiers[int(option) - 1])
            if isinstance(option, (str, int))
            else option
        )
    except (IndexError, ValueError):
        console_obj.print(
            "Invalid option! Picking randomly", style=ConsoleStyle.TEXT_STYLE_WARN.value
        )
        categories = list(random.choice(classifiers))

    consolidate_categs = list(categories)
    logging.info(f"Suggested categories ML: {consolidate_categs}")

    console_obj.print(
        " \n** I think these categories are appropriate: **\n",
        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
    )
    print_options(consolidate_categs)

    categ_num = re.compile(r"\d+")
    match console_obj.input(
        f"[{prompt_style}]\nEnter the category number or type in to look for another category within the site: [{prompt_style}]\n"
    ):
        case str() as num if categ_num.match(num):
            try:
                sel_categ = consolidate_categs[int(num) - 1]
                logging.info(f"User selected category: {sel_categ}")
            except (ValueError, IndexError):
                sel_categ = random.choice(consolidate_categs)
                logging.info(
                    f"User typed in an incorrect option: {num}. Picking random category {sel_categ}"
                )
        case _ as misc:
            sel_categ = misc
            logging.info(f"User typed in category: {misc}")

    categ_ids: List[int] = get_tag_ids(wordpress_site, [sel_categ], preset="categories")
    logging.info(
        f"WordPress API matched category ID: {categ_ids} for category: {sel_categ}"
    )
    return categ_ids
