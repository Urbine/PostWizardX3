"""
Workflows Parsing Module

This module contains functions for parsing elements that are of interest to the workflows,
such as asset config files.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import re

# Local imports
from core.exceptions.config_exceptions import AssetsNotFoundError
from core.models.config_model import MCashContentBotConf
from core.utils.parsers import parse_client_config
from core.utils.interfaces import WordFilter


def asset_parser(bot_config: MCashContentBotConf, partner: str):
    """Parse asset images for post payload from the specified file in the
    ``workflows_config.ini`` file.

    :param bot_config: ``ContentSelectConf`` bot config factory function.
    :param partner: ``str`` partner name
    :return: ``list[str]`` asset images or banners.
    """
    assets = parse_client_config(bot_config.assets_conf, "core.config")
    sections = assets.sections()

    wrd_list = (
        WordFilter(delimiter=" ", filter_pattern=r"(?=\W)\S").add_word(partner).split()
    )

    find_me = (  # noqa: E731
        lambda word, section: matchs[0]
        if (matchs := re.findall(word, section, flags=re.IGNORECASE))
        else matchs
    )

    assets_list = []
    for wrd in wrd_list:
        # The main lambda has re.findall with IGNORECASE flag, however
        # list index lookup does take word case into consideration for str comparison.
        wrd_to_lc = wrd.lower()

        # To ensure uniqueness in the hints provided, the count of matches must be 1.
        # If the same word is found more than once, then the match is clearly not unique.
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
        logging.critical("Raised AssetsNotFoundError - Quitting...")
        raise AssetsNotFoundError
