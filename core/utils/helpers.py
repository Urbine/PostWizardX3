# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Utility Helper Functions

This module provides reusable utility functions that support various operations across the project.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Tuple


def get_duration(seconds: int | float) -> Tuple[int | float, int | float, int | float]:
    """Takes the number of seconds and calculates its duration in hours, minutes, and seconds.

    :param seconds: ``int``
    :return: ``tuple[int, int, int]`` *hours, minutes, seconds*
    """
    hours, remainder = divmod(seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute
    return hours, minutes, seconds
