"""
Utility Helper Functions

This module provides reusable utility functions that support various operations across the project.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, Tuple


def get_duration(seconds: int | float) -> Tuple[int | float, int | float, int | float]:
    """Takes the number of seconds and calculates its duration in hours, minutes, and seconds.

    :param seconds: ``int``
    :return: ``tuple[int, int, int]`` *hours, minutes, seconds*
    """
    hours, remainder = divmod(seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute
    return hours, minutes, seconds


def get_dict_key(source_dic: dict, value: int) -> Optional[str | int]:
    """This function retrieves the key from a dictionary if the value is associated with one.

    :param source_dic: key lookup ``dict``
    :param value: value to query
    :return: ``str`` or ``int`` or ``None`` / *depending on the results and datatype of the key.*
    """
    for tname, tid in source_dic.items():
        if value == tid:
            return tname
    return None
