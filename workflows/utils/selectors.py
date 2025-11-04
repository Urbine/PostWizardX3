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
from typing import List, Optional

# Third-party imports
from rich.console import Console


# Local imports
from core.utils.interfaces import WordFilter
from ml_engine import classify_title, classify_description, classify_tags
from wordpress import WordPress
from workflows.utils.checkers import get_tag_ids
from workflows.utils.logging import ConsoleStyle


class SlugGetter:
    """
    Retrieve a slug based on user input from provided options or get a custom one.
    Handles edge cases when no slugs are available or user input is invalid.

    :param console_obj: ``rich.console.Console`` Console object for printing and user interaction
    :param slugs: ``list[str]`` List of available slug options to choose from
    :return: ``str`` The selected slug, either from the provided list or a custom one
    """

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
            return (
                WordFilter(delimiter="-", enforce_unique=True, stopword_removal=True)
                .add_word(self._proposed_slug)
                .filter()
            )


class ContentClassifier:
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

    def __init__(
        self,
        console_obj: Console,
        wordpress_site: WordPress,
        title: str,
        description: str,
        tags: str,
        interactive=False,
        aggregate_all=False,
    ):
        self._console_obj = console_obj
        self._wordpress_site = wordpress_site
        self._title = title
        self._description = description
        self._tags = tags
        self._interactive = interactive
        self._aggregate_all = aggregate_all
        self._prompt_style = ConsoleStyle.TEXT_STYLE_PROMPT.value

        # Deferred assignment
        self._candidates = None
        self._consolidated = None
        self._categ_ints = None
        self._headless_offer = None

    def _print_options(self, option_lst, print_delim: bool = False):
        for opt, classifier in enumerate(option_lst, start=1):
            self._console_obj.print(
                f"{opt}. {classifier.title() if isinstance(classifier, str) else classifier}",
                style=ConsoleStyle.TEXT_STYLE_DEFAULT.value,
            )
        if print_delim:
            self._console_obj.print(f"{'*':=^35}")

    def _prepare_candidates(self) -> None:
        self._candidates = [
            classify_title(self._title if self._title is not None else ""),
            classify_description(
                self._description if self._description is not None else ""
            ),
            classify_tags(self._tags if self._tags is not None else ""),
        ]

    def _consolidate_candidates(self):
        self._consolidated = {categ for categs in self._candidates for categ in categs}
        logging.info(f"Consolidated candidates: {self._consolidated}")

    def _trace_category_num(self, tag_list: List[str]):
        categ_ids: List[int] = get_tag_ids(
            self._wordpress_site, tag_list, preset="categories"
        )
        logging.info(
            f"WordPress API matched category ID: {categ_ids} for category: {tag_list}"
        )
        self._categ_ints = categ_ids

    def _interactive_pick(self) -> None:
        self._prepare_candidates()
        if not self._aggregate_all:
            classifier_str_lst: List[str] = ["Title", "Description", "Tags"]
            classifier_options = [categs for categs in self._candidates if categs]

            option = ""
            self._console_obj.print(
                "\nAvailable Machine Learning classifiers: \n",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )

            self._print_options(classifier_str_lst)
            peek = re.compile("peek", re.IGNORECASE)
            rand = re.compile(r"rando?m?", re.IGNORECASE)
            number = re.compile(r"\d+")
            while not option:
                match self._console_obj.input(
                    f"\n[{self._prompt_style}]Pick your classifier:  (Type in the 'peek' to open all classifiers or 'random' to let me choose for you)[/{self._prompt_style}]\n"
                ):
                    case str() as p if peek.findall(p):
                        self._print_options(classifier_options, print_delim=True)
                        self._print_options(classifier_str_lst)
                        option = self._console_obj.input(
                            f"\n[{self._prompt_style}]Your choice:[/{self._prompt_style}]\n"
                        )
                    case str() as r if rand.findall(r):
                        option = random.choice(classifier_options)
                    case str() as n if number.findall(n):
                        if option_number := int(n) - 1 <= len(classifier_str_lst):
                            option = option_number
                    case _:
                        continue
            try:
                # Here ``option`` can be either ``str`` or ``set[str]``
                categories = (
                    list(self._candidates[int(option) - 1])
                    if isinstance(option, (str, int))
                    else option
                )
            except (IndexError, ValueError):
                self._console_obj.print(
                    "Invalid option! Picking randomly",
                    style=ConsoleStyle.TEXT_STYLE_WARN.value,
                )
                categories = list(random.choice(self._candidates))
                self._consolidated = list(categories)
                logging.info(f"Storing random category candidate: {self._consolidated}")

        self._consolidate_candidates()
        logging.info(f"Suggested categories ML: {self._consolidated}")

        self._console_obj.print(
            " \n** I think these categories are appropriate: **\n",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
        )
        self._print_options(self._consolidated)

        categ_num = re.compile(r"\d+")
        match self._console_obj.input(
            f"[{self._prompt_style}]\nEnter the category number or type in to look for another category within the site: [{self._prompt_style}]\n"
        ):
            case str() as num if categ_num.match(num):
                try:
                    sel_categ = list(self._consolidated)[int(num) - 1]
                    logging.info(f"User selected category: {sel_categ}")
                except (ValueError, IndexError):
                    sel_categ = random.choice(self._consolidated)
                    logging.info(
                        f"User typed in an incorrect option: {num}. Picking random category {sel_categ}"
                    )
            case _ as misc:
                sel_categ = misc
                logging.info(f"User typed in category: {misc}")

        self._trace_category_num([sel_categ])

    def headless_offer(self):
        self._prepare_candidates()
        self._consolidate_candidates()
        self._headless_offer = {
            "Recommended": self._consolidated,
            "All Categories": self._wordpress_site.get_post_categories(),
        }
        return self._headless_offer

    def get_headless_pick(self, final_tag: str):
        self._trace_category_num([final_tag])

    def get(self):
        if self._interactive:
            self._interactive_pick()
            return self._categ_ints
        else:
            return self._headless_offer
