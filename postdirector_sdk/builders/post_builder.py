"""
Post Builder

This module defines the PostInfoPayload class, which is a subclass of PayloadBuilder.
It is used to build a payload for a WordPress Post request, which is a type of Post request
that is consumed in JSON format by the PostDirector Server API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Union, Self, Mapping

from .payload_builder import PayloadBuilder
from postdirector_sdk.models.client_schema import PostKey


class PostInfoPayload(PayloadBuilder):
    def __init__(self):
        super().__init__()

    def _plus(self, key: PostKey, value: Union[str, int]) -> Self:
        if key.value in self._payload:
            self._payload[key.value].update(value)
        else:
            self._payload[key.value] = value
        return self

    def build(self) -> Mapping[str, Union[str, int, bool]]:
        return super().build()

    def clear(self):
        return super().clear()

    def post_id(self, post_id: int):
        return self._plus(PostKey.ID, post_id)

    def author(self, author: str):
        return self._plus(PostKey.AUTHOR, author)

    def content(self, content: str):
        return self._plus(PostKey.CONTENT, content)

    def title(self, title: str):
        return self._plus(PostKey.TITLE, title)

    def slug(self, slug: str):
        return self._plus(PostKey.SLUG, slug)

    def status(self, status: str):
        return self._plus(PostKey.STATUS, status)

    def post_type(self, post_type: str):
        return self._plus(PostKey.TYPE, post_type)
