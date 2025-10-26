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

    def print_slugs(slug_list: List[str]) -> str:
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

    def slug_getter_persist(slug_list: List[str]) -> Optional[str]:
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
        return None

    return slug_getter_persist(slugs)


class SlugGetter:
    def __init__(
        self,
        console_obj: Console,
        slugs: List[str],
        interactive: bool = True,
        proposed_slug: Optional[str] = None,
    ):
        self._prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value
        self._user_attention_style = ConsoleStyle.TEXT_STYLE_ATTENTION.value
        self._slug_entry_style = ConsoleStyle.TEXT_STYLE_ACTION.value
        self._console = console_obj
        self._slug_list = slugs
        self._interactive = interactive
        self._proposed_slug = proposed_slug

    def _print_slugs(self) -> str:
        self._console.print(
            "\n--> Available slugs:\n", style=self._user_attention_style
        )

        for n, slug in enumerate(self._slug_list, start=1):
            self._console.print(f"{n}. -> {slug}", style=self._slug_entry_style)
        self._console.print(
            "--> Provide a custom slug or pick a slug number",
            style=self._user_attention_style,
        )

        slug_option = self._console.input(
            f"[{self._prompt_style}]\nSelect your slug: [/{self._prompt_style}]\n"
        )
        return slug_option

    def _slug_getter_loop(self) -> Optional[str]:
        user_slug = ""
        while not user_slug:
            if len(self._slug_list) != 0:
                user_slug = self._print_slugs()
                if re.match(r"^\d+$", user_slug):
                    try:
                        return self._slug_list[int(user_slug) - 1]
                    except (IndexError, ValueError):
                        self._console.print(
                            "Invalid option! Choosing random slug...",
                            style=ConsoleStyle.TEXT_STYLE_WARN.value,
                        )
                        user_slug = random.choice(self._slug_list)
                        logging.info(f"Chose random slug: {user_slug} automatically")
                        return user_slug
                elif re.match(r"^\w+", user_slug):
                    logging.info(f"User-provided slug: {user_slug} used")
                    self._console.print(
                        f"Using custom slug: {user_slug}",
                        style=self._user_attention_style,
                    )
                    return user_slug
            else:
                logging.critical("No slugs were provided in controlling function.")
                self._console.print(
                    " -> Provide a custom slug for the post now: \n",
                    style=self._prompt_style,
                )
                user_slug = input()
                if user_slug:
                    return user_slug
                else:
                    continue
        return None

    def get(self) -> Optional[str]:
        if self._interactive:
            return self._slug_getter_loop()
        else:
            logging.info(f"User-proposed slug: {self._proposed_slug} used")
            return self._proposed_slug


def pick_classifier(
    console_obj: Console,
    wordpress_site: WordPress,
    title: str,
    description: str,
    tags: str,
    interactive=False,
) -> List[int]:
    """
    Picks a classifier for content selection based on user input and automatically assigns relevant categories.

    If interactive mode is enabled, the user can choose a classifier from the list of available classifiers.
    If interactive mode is disabled, the function will automatically aggregate all classifiers and return a
    set of unique categories to choose from. In both cases, the user will be able to provide a custom category
    by typing it in the console.

    :raises ValueError: If an invalid option is chosen by the user.
    :param console_obj: The rich.console.Console object to print output.
    :param wordpress_site: An instance of the WordPress class.
    :param title: The title of the content being selected.
    :param description: A short description of the content.
    :param tags: The relevant tags for the content.
    :param interactive: Whether to use interactive mode or not.
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
        classify_title(title if title is not None else ""),
        classify_description(description if description is not None else ""),
        classify_tags(tags if tags is not None else ""),
    ]

    if interactive:
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
                "Invalid option! Picking randomly",
                style=ConsoleStyle.TEXT_STYLE_WARN.value,
            )
            categories = list(random.choice(classifiers))

        consolidate_categs = list(categories)
    else:
        consolidate_categs = {categ for categs in classifiers for categ in categs}

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
                sel_categ = list(consolidate_categs)[int(num) - 1]
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
