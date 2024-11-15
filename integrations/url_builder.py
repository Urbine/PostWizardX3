"""
Help in the construction of API URLs that other modules need to gather information from a remote source.
Contribute to better organization of the code by providing common elements that some APIs need in this package.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CSVColumns:
    """
    CSV Column fields that can be used together or in isolation depending on the kind of
    result that you want to obtain.
    """
    ID_: str = 'id'
    title: str = 'title'
    description: str = 'description'
    link: str = 'link'
    duration: str = 'duration'
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
class CSVSeparators:
    """
    Encoded separators for the URL params
    """
    pipe_sep: str = "%7C"
    comma_sep: str = "%2C"
    semicolon_sep: str = "%3B"


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
