# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

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


def transform_mcash_hosted_link(link: str) -> Optional[str]:
    """
    Transform MCash hosted link to video link slug

    :param link: ``str`` -> MCash hosted link
    :return: ``str`` -> video link slug
    """
    try:
        partners = ["asd", "ttp", "toticos", "pgfs", "esd"]
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


def mask_mcash_tracking_link(tracking_link: str, base_url: str):
    """
    Masks a tracking link behind a new base URL.

    :param tracking_link: ``str`` -> Tracking link to transform.
    :param base_url: ``str`` -> Base URL to use for the new tracking link.
    :return: ``str`` -> New tracking link.
    """
    tracking_link_re = re.compile(r"(https?://join.+)")
    partner_list = [
        "asiansexdiary",
        "tuktukpatrol",
        "trikepatrol",
        "eurosexdiary",
        "toticos",
        "paradisegfs",
        "helloladyboy",
    ]
    partner_abbr = ["asd", "ttp", "tk", "esd", "tot", "pgfs", "hlb"]
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
        "https://vjav.com/embed",
        "https://desi-porntube.com/embed",
        "https://desi-porn.tube/embed",
        "https://www.pornhub.com/embed",
        "https://videovjav.com/embed",
        "https://abjav.tube/embed",
        "https://www.xvideos.com/embedframe",
        "https://fh.video/embed",
        "https://embed.redtube.com",
    ]
    link_masks = [
        "/jav",
        "/desi-porn",
        "/desi-tube",
        "/pornhb",
        "/jav-video",
        "/jav-tube",
        "/xvid",
        "/fap",
        "/rtube",
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
