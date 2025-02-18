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
    Builder dataclass for encoded separators for URL params.
    """

    PIPE: str = "%7C"
    COMMA: str = "%2C"
    SEMICOLON: str = "%3B"
    SPACE: str = "%20"


@dataclass(frozen=True)
class AdultNextUrl:
    """
    Builder class for the AdultNext API integration
    """

    abjav_base_url: str = "https://direct.abjav.com"


dataclass(frozen=True)


class TubeCorpUrl:
    """
    Builder class for the TubeCorporate Feed intergration.
    """

    vjav_base_url: str = "https://vjav.com/admin/feeds/embed/?source="
    desi_t_url: str = "https://desiporn.tube/admin/feeds/embed/?source="


@dataclass(frozen=True)
class WPEndpoints:
    """
    Builder dataclass for the WordPress API Endpoints.
    """

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
    """
    Builder dataclass for the X API scopes.
    """

    READ: str = "tweet.read"
    WRITE: str = "tweet.write"
    OFFLINE: str = "offline.access"
    MEDIA: str = "media.write"
    USREAD: str = "users.read"


@dataclass(frozen=True)
class XEndpoints:
    """
    Builder dataclass for the X API Endpoints.
    """

    token_url: str = "https://api.x.com/2/oauth2/token"
    authorise_url: str = "https://x.com/i/oauth2/authorize?"
    tweets: str = "https://api.x.com/2/tweets"


@dataclass(frozen=True)
class BotFatherCommands:
    """
    Builder dataclass for the BotFather REST API Commands.
    """

    api_url: str = "https://api.telegram.org/bot"
    get_me: str = "/getMe"
    send_message = "/sendMessage"


@dataclass(frozen=True)
class BotFatherEndpoints:
    """
    Builder dataclass for the BotFather REST API Command Endpoints.
    """

    chat_id: str = "?chat_id="
    text: str = "&text="
    parse_mode = "&parse_mode="
    parse_mode_mdv2: str = "MarkdownV2"
    prefer_large_media = "prefer_large_media="
