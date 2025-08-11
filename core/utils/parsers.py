"""
Parsing Utilities
This module contains functions to parse configuration files and other data sources.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import importlib.resources
import logging
import os
import re
from calendar import month_abbr, month_name
from configparser import ConfigParser
from datetime import date

from core.utils.strings import clean_filename, split_char, filter_apostrophe
from core.exceptions.config_exceptions import ConfigFileNotFound, SectionsNotFoundError


def parse_client_config(
    ini_file: str, package_name: str, env_var: bool = False, safe_parse: bool = False
) -> ConfigParser | bool:
    """Parse client configuration files that store secrets and other configurations.

    :param ini_file: ``str`` ini filename with or without the extension
    :param package_name: ``str`` package name where the config file is located.
    :param env_var: ``bool`` Save path in an environment path
    :param safe_parse: ``bool`` If ``True``, the function will return ``False`` if the file is not found.
    :return: ``ConfigParser``
    """
    f_ini = clean_filename(ini_file, "ini")
    config = ConfigParser(interpolation=None)
    with importlib.resources.path(package_name, f_ini) as f_path:
        if env_var:
            os.environ["CONFIG_PATH"] = os.path.abspath(f_path)
        elif not os.path.exists(f_path):
            if safe_parse:
                return False
            else:
                raise ConfigFileNotFound(f_ini, package_name)
        config.read(f_path)
    return config


def parse_date_to_iso(
    full_date: str, zero_day: bool = False, m_abbr: bool = False
) -> date:
    """Breaks down the full date string and converts it to ISO format to get a datetime.date object.
    important: Make sure to import 'from calendar import month_abbr, month_name' as it is required.

    :param full_date: date_full is ``'Aug 20th, 2024'`` or ``'August 20th, 2024'``.
    :param zero_day: True if your date already has a zero in days less than 10. Default: False
    :param m_abbr: Set to True if you provide a month abbreviation e.g. ``'Aug'``, default set to ``False``.
    :return: ``date`` object (``ISO`` format)
    """
    # Lists month_abbr and month_name provided by the built-in Calendar
    # library in Python.
    if m_abbr:
        months = list(month_abbr)
    else:
        months = list(month_name)

    letters = re.compile(r"[a-z]")
    year = str(full_date.split(",")[1].strip())

    month_num = str(months.index(full_date.split(",")[0].split(" ")[0]))

    # The date ISO format requires that single numbers are preceded by a 0.

    if int(month_num) <= 9:
        month_num = "0" + str(months.index(full_date.split(",")[0].split(" ")[0]))

    day_nth = str(full_date.split(",")[0].split(" ")[1])
    day = day_nth.strip("".join(letters.findall(day_nth)))

    if zero_day:
        if int(day) <= 9:
            day = day_nth.strip("".join(letters.findall(day_nth)))
    else:
        if int(day) <= 9:
            day = "0" + day_nth.strip("".join(letters.findall(day_nth)))

    return date.fromisoformat(year + month_num + day)


def config_section_parser(config_filename: str, target_hint: str):
    """Parse a configuration file that contains a specific string in one of its sections and retrieve options
    under that section.

    As an example, you have file ``my_config.ini`` and it has two sections ``[pretty_config]`` and ``[ugly_config]``.
    In this case, you need the options in ``[pretty_config]``, however another user could create a configuration file
    with a different arrangement like add spaces or include words to the section name and this makes hardcoding of section
    names difficult, hence this function.
    A user could create a file with the section name ``[config_pretty]`` or ``[not-so-pretty-config]`` and this function
    will be able to retrieve the options from that part of the file as long as it contains the ``target_hint``
    string, in represented in this example as the word ``"pretty"``.

    :param config_filename: ``str`` Source config filename
    :param target_hint: ``str`` string that could be included in a config file section
    :return: ``list[str]`` -> config options.
    """
    config = parse_client_config(config_filename, "core.config")
    sections = config.sections()

    wrd_list = filter_apostrophe(target_hint).split(
        split_char(target_hint, placeholder=" ")
    )

    find_me = (
        lambda word, section: matchs[0]
        if (matchs := re.findall(word, section, flags=re.IGNORECASE))
        else matchs
    )

    option_list = []
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
                f'Section parsing result: found "{wrd}" in section: {sections[match_indx]}'
            )
            option_list = list(config[sections[match_indx]].values())
            break
        else:
            continue

    if option_list:
        return option_list
    else:
        logging.critical("Raised SectionsNotFoundError - Quitting...")
        raise SectionsNotFoundError
