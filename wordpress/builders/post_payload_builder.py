# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
SimplePostPayloadBuilder class

This class is a builder for a simple WordPress post payload.
Specialised payload builders in this module should subclass it
and develop any specialization on top of it.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self, List

from wordpress.interfaces import SimplePayloadBuilder
from wordpress.models import PayloadItem


class PostPayloadBuilder(SimplePayloadBuilder):
    """
    A builder for a simple WordPress post payload.
    It extends the ``SimplePayloadBuilder`` class and provides methods to add
    specific fields to the payload.
    """

    def __init__(self):
        super().__init__()

    def slug(self, slug: str) -> Self:
        """
        Add a slug to the payload.

        :param slug:  ``str`` -> The slug to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.SLUG, slug)
        return self

    def status(self, status: str) -> Self:
        """
        Add a status to the payload.

        :param status:  ``str`` -> The status to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.STATUS, status)
        return self

    def type(self, post_type: str) -> Self:
        """
        Add a post type to the payload.

        :param post_type:  ``str`` -> The post type to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.TYPE, post_type)
        return self

    def title(self, title: str) -> Self:
        """
        Add a title to the payload.

        :param title:  ``str`` -> The title to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.TITLE, title)
        return self

    def content(self, content: str) -> Self:
        """
        Add a content to the payload.

        :param content:  ``str`` -> The content to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.CONTENT, content)
        return self

    def excerpt(self, excerpt: str) -> Self:
        """
        Add an excerpt to the payload.

        :param excerpt:  ``str`` -> The excerpt to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.EXCERPT, excerpt)
        return self

    def featured_media(self, featured_media: int) -> Self:
        """
        Add a featured media to the payload.

        :param featured_media:  ``int`` -> The featured media to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.FEATURED_MEDIA, featured_media)
        return self

    def tags(self, tags: List[int]) -> Self:
        """
        Add a tags list to the payload.

        :param tags:  ``list[int]`` -> The numeric tags to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.TAGS, tags)
        return self

    def categories(self, categories: List[int]) -> Self:
        """
        Add a categories list to the payload.

        :param categories:  ``list[int]`` -> The numeric categories to be added to the payload.
        :return: ``SimplePayloadBuilder`` -> The builder for chaining.
        """
        self._plus(PayloadItem.CATEGORIES, categories)
        return self
