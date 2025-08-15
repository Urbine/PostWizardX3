"""
Module for the WordPress API Endpoints constants.

This module provides a class-based interface to interact with the WordPress REST API,
enabling retrieval, creation, and management of posts, tags, categories, and media.
It supports local caching of API data, efficient synchronization, and various utilities
for filtering, mapping, and reporting on WordPress site content.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

from enum import Enum


class WPEndpoints(Enum):
    """
    Enum class for the WordPress API Endpoints constants.
    """

    USERS = "/users?"
    POSTS = "/posts"
    PER_PAGE = "?per_page="
    PAGE = "?page="
    PHOTOS = "/photos"
    FIELDS_BASE = "?_fields="
    # fields are comma-separated in the URL after the
    # fields_base value.
    FIELD_AUTHOR = "author"
    FIELD_ID = "id"
    FIELD_EXCERPT = "excerpt"
    FIELD_TITLE = "title"
    FIELD_LINK = "link"
    CATEGORIES = "/categories"
    MEDIA = "/media"
    TAGS = "/tags"
