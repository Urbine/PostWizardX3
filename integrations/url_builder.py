# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Help in the construction of API URLs that other modules need to gather information from a remote source.
Contribute to better organization of the code by providing common elements that some APIs need in this package.

The classes in this document are not documented in detail as their integration implementation contains further
clarification on their values and how they are used in context.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from dataclasses import dataclass


@dataclass(frozen=True)
class CSVColumns:
    """
    CSV Column fields that can be used together or in isolation depending on the kind of
    result that you want to obtain.
    """

    ID_: str = "id"
    title: str = "title"
    description: str = "description"
    link: str = "link"
    duration: str = "duration"
    rating: str = "rating"
    added_time: str = "post_date"
    categories: str = "categories"
    tags: str = "tags"
    model: str = "models"
    embed_code: str = "embed"
    # Attaches to main to fetch thumbnail.
    thumbnail_prefix: str = "screenshots_prefix"
    main_thumbnail: str = (
        "main_screenshot"  # Thumbnail ID obtained from removing the img extension
    )
    thumbnails: str = "screenshots"
    video_thumbnail_url: str = "preview_url"


@dataclass(frozen=True)
class URLEncode:
    """
    Builder dataclass for encoded (hex - ASCII 124) separators for URL params.
    """

    PIPE: str = "%7C"
    COMMA: str = "%2C"
    SEMICOLON: str = "%3B"
    SPACE: str = "%20"
