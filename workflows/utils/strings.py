"""
Workflows String Utilities Module

This module provides utilities to deal with string manipulation and filtering.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import re
from typing import Optional

from workflows.exceptions import IncompatibleLinkException


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
