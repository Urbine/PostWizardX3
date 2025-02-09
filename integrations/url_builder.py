"""
Help in the construction of API URLs that other modules need to gather information from a remote source.
Contribute to better organization of the code by providing common elements that some APIs need in this package.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from dataclasses import dataclass
from enum import Enum


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
    Encoded separators for URL params
    """

    PIPE: str = "%7C"
    COMMA: str = "%2C"
    SEMICOLON: str = "%3B"
    SPACE: str = "%20"


@dataclass(frozen=True)
class WPEndpoints:
    users: str = "/users?"
    posts: str = "/posts"
    photos: str = "/photos"
    per_page: str = "?per_page="
    page: str = "?page="
    fields_base: str = "?_fields="
    # fields are comma-separated in the URL after the
    # fields_base value.
    field_author: str = "author"
    field_id: str = "id"
    field_except: str = "excerpt"
    field_title: str = "title"
    field_link: str = "link"
    categories: str = "/categories"
    media: str = "/media"


@dataclass(frozen=True)
class XScope:
    READ: str = "tweet.read"
    WRITE: str = "tweet.write"
    OFFLINE: str = "offline.access"
    MEDIA: str = "media.write"
    USREAD: str = "users.read"


@dataclass(frozen=True)
class XEndpoints:
    token_url: str = "https://api.x.com/2/oauth2/token"
    authorise_url: str = "https://x.com/i/oauth2/authorize?"
    tweets: str = "https://api.x.com/2/tweets"
