# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Post Builder

This module defines the PostInfoPayload class, which is a subclass of PayloadBuilder.
It is used to build a payload for a WordPress Post request, which is a type of Post request
that is consumed in JSON format by the PostWizard Server API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self, Union
from postwizard_sdk.builders.interfaces import NestedPayloadBuilder
from postwizard_sdk.models import PostKey


class PostInfoNestedPayload(NestedPayloadBuilder):
    def __init__(self):
        super().__init__()

    def post_id(self, post_id: int) -> Self:
        return self._plus(PostKey.ID, post_id)

    def author(self, author: str) -> Self:
        return self._plus(PostKey.AUTHOR, author)

    def content(self, content: str) -> Self:
        return self._plus(PostKey.CONTENT, content)

    def title(self, title: str) -> Self:
        return self._plus(PostKey.TITLE, title)

    def slug(self, slug: str) -> Self:
        return self._plus(PostKey.SLUG, slug)

    def status(self, status: str) -> Self:
        return self._plus(PostKey.STATUS, status)

    def post_type(self, post_type: str) -> Self:
        return self._plus(PostKey.TYPE, post_type)

    def add(self, key: PostKey, value: Union[str, int, bool]) -> Self:
        return self._plus(key, value)
