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

    no_sp_chars = lambda w: "".join(re.findall(r"\w+", w))

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


def transform_mcash_hosted_link(link: str) -> str:
    """
    Transform MCash hosted link to video link slug

    :param link: ``str`` -> MCash hosted link
    :return: ``str`` -> video link slug
    """
    partners = ["asd", "ttp", "toticos", "pgfs", "esd"]
    decompose = link.split("/")
    slug = decompose[-1]
    partner_id = partner if (partner := decompose[-3]) in partners else ""
    new_slug = slug.split("_")
    if partner_id:
        new_slug.insert(-1, partner_id)
    slugify = "-".join(new_slug)
    return slugify
