# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Post Payload Client Schema enumeration

This module defines the schema for the payload used to create a post in WordPress.
This enumeration of possible values is not exhaustive, and it can be extended.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from enum import Enum


class PayloadItem(Enum):
    SLUG = "slug"
    STATUS = "status"
    TYPE = "type"
    TITLE = "title"
    EXCERPT = "excerpt"
    CONTENT = "content"
    FEATURED_MEDIA = "featured_media"
    TAGS = "tags"
    PORNSTARS = "pornstars"
    CATEGORIES = "categories"


class ImagePayloadItem(Enum):
    ALT_TEXT = "alt_text"
    CAPTION = "caption"
    DESCRIPTION = "description"
    PHOTOS_TAG = "photos_tag"
    TYPE = "photos"
