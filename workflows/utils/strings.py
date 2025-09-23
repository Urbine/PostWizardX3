"""
Workflows String Utilities Module

This module provides utilities to deal with string manipulation and filtering.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import re
from typing import Optional, List

from core.utils.strings import split_char
from workflows.exceptions import IncompatibleLinkException


def clean_partner_tag(partner_tag: str) -> str:
    """Clean partner names that could contain apostrophes in them.

    :param partner_tag: ``str`` the conflicting text
    :return: ``str`` cleaned partner tag without the apostrophe.
    """
    try:
        spl_word: str = split_char(partner_tag)
        if spl_word == " ":
            return partner_tag
        elif "'" not in split_char(partner_tag, char_lst=True):
            return partner_tag
        else:
            # Second special character is the apostrophe, the first one is typically a whitespace
            return "".join(partner_tag.split(spl_word))
    except IndexError:
        return partner_tag


def filter_tags(
    tgs: str, filter_lst: Optional[List[str]] = None
) -> Optional[List[str]]:
    """Remove redundant words found in tags and return a clear list of unique filtered tags.

    :param tgs: ``list[str]`` tags to be filtered
    :param filter_lst: ``list[str]`` lookup list of words to be removed
    :return: ``list[str]``
    """
    if tgs is None:
        return None

    no_sp_chars = lambda w: "".join(re.findall(r"\w+", w))  # noqa: E731

    # Split with a whitespace separator is not necessary at this point:
    t_split = tgs.split(spl if (spl := split_char(tgs)) != " " else "-1")

    new_set = set({})
    for tg in t_split:
        temp_lst = []
        sublist = tg.split(" ")
        for word in sublist:
            if filter_lst is None:
                temp_lst.append(no_sp_chars(word))
            elif word not in filter_lst:
                temp_lst.append(no_sp_chars(word))
            elif temp_lst:
                continue
        new_set.add(" ".join(temp_lst))
    return list(new_set)


def transform_media_source_hosted_link(link: str) -> Optional[str]:
    """
    Transform MediaSource hosted link to video link slug

    :param link: ``str`` -> MediaSource hosted link
    :return: ``str`` -> video link slug
    """
    try:
        partners = ["pa", "pb", "pe", "pf", "pd"]
        decompose = link.split("/")
        slug = decompose[-1]
        partner_id = partner if (partner := decompose[-3]) in partners else ""
        new_slug = slug.split("_")
        if partner_id:
            new_slug.insert(-1, partner_id)
        slugify = "-".join(new_slug)
        return slugify
    except IndexError:
        return None


def mask_media_source_tracking_link(tracking_link: str, base_url: str):
    """
    Masks a tracking link behind a new base URL.

    :param tracking_link: ``str`` -> Tracking link to transform.
    :param base_url: ``str`` -> Base URL to use for the new tracking link.
    :return: ``str`` -> New tracking link.
    """
    tracking_link_re = re.compile(r"(https?://join.+)")
    partner_list = [
        "partner_a",
        "partner_b",
        "partner_c",
        "partner_d",
        "partner_e",
        "partner_f",
        "partner_g",
    ]
    partner_abbr = ["pa", "pb", "pc", "pd", "pe", "pf", "pg"]
    if tracking_link_re.match(tracking_link):
        tracking_str = tracking_link.split("/")[-1]
        get_partner_name = tracking_link.split(".")[1]
        if get_partner_name in partner_list:
            partner_indx = partner_list.index(get_partner_name)
            return f"{base_url.strip('/')}/{partner_abbr[partner_indx]}/{tracking_str}"
    return None


def transform_partner_iframe(embed_iframe: str, base_url: str) -> str:
    """
    Transform partner iframe code to masked embedded links.
    Raises an exception if the link is not compatible with the masking algorithm.

    :param embed_iframe: ``str`` -> Embed iframe code to transform.
    :param base_url: ``str`` -> Base URL to use for the new embedded link.
    :return: ``str`` -> New embedded link.
    """
    partner_link_list = [
        "https://example-feed-a.com/embed",
        "https://example-feed-b.com/embed",
        "https://partner-three.example.com/embed",
        "https://partner-four.example.com/embed",
        "https://partner-five.example.com/embed",
        "https://partner-six.example.com/embed",
        "https://partner-seven.example.com/embedframe",
        "https://partner-eight.example.com/embed",
        "https://partner-nine.example.com/embed",
    ]
    link_masks = [
        "/partner-one",
        "/partner-two",
        "/partner-three",
        "/partner-four",
        "/partner-five",
        "/partner-six",
        "/partner-seven",
        "/partner-eight",
        "/partner-nine",
    ]
    decomposed_frame = embed_iframe.split('"')
    link_regex = re.compile(r"https?://.+\.\w+(?:/embed(?:frame)?)?(?=/)", re.MULTILINE)
    for item in decomposed_frame:
        match = link_regex.match(item)
        if match and match.group(0) in partner_link_list:
            curr_indx = partner_link_list.index(match.group(0))
            new_embed_link = (
                f"{base_url}{link_masks[curr_indx]}{link_regex.split(item)[1]}"
            )
            frame_index = decomposed_frame.index(item)
            decomposed_frame[frame_index] = new_embed_link
        elif match and match.group(0) not in partner_link_list:
            raise IncompatibleLinkException(item)
    return '"'.join(decomposed_frame)
