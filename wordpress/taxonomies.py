"""
WordPress Taxonomy classes

This module defines two classes: WPTaxonomyValues and WPTaxonomyMarker.

WPTaxonomyValues:
    Enum class for the WordPress cache taxonomy value representation.

WPTaxonomyMarker:
    Enum class for the WordPress cache taxonomy key markers.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

from enum import Enum


class WPTaxonomyValues(Enum):
    """
    Enum class for the WordPress cache taxonomy value representation.

    A taxonomy value list is a key in the WordPress post data that holds a list of numeric IDs
    for a given taxonomy, such as tags or categories.

    Example:
        "tags": [12, 34, 56]
        "categories": [2, 5]
    """

    TAGS = "tags"
    CATEGORIES = "categories"
    MODELS = "pornstars"
    PHOTOS = "photos_tag"


class WPTaxonomyMarker(Enum):
    """
    Enum class for the WordPress cache taxonomy key markers.

    A taxonomy marker is a prefix or identifier used in the 'class_list' field of a post
    to indicate the type of taxonomy (e.g., tag, category, post type, status).

    Example:
        "tag-python", "category-tutorial", "status-published"

    These markers help extract and group related metadata from posts.
    """

    TAG = "tag"
    CATEGORY = "category"
    POST = "post"
    TYPE = "type"
    STATUS = "status"
    MODELS = "pornstars"
    PHOTOS = "photos_tag"
