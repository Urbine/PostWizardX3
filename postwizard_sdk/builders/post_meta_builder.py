# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
PostMetaPayload Builder

This module defines the PostMetaPayload class, which is a subclass of PayloadBuilder.
It is used to build a payload for a WordPress PostMeta request, which is a type of Post request
that is consumed in JSON format by the PostWizard Server API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self, Union

# Local imports
from postwizard_sdk.models.client_schema import (
    Ethnicity,
    HairColor,
    ToggleField,
    Production,
    Orientation,
)
from postwizard_sdk.models import PostMetaKey
from postwizard_sdk.builders.interfaces import NestedPayloadBuilder


class PostMetaNestedPayload(NestedPayloadBuilder):
    def __init__(self):
        super().__init__()

    def post_id(self, post_id: int) -> Self:
        return self._plus(PostMetaKey.ID, post_id)

    def embed_code(self, embed_code: str) -> Self:
        return self._plus(PostMetaKey.EMBED_CODE, embed_code)

    def hours(self, hours: int) -> Self:
        return self._plus(PostMetaKey.HOURS, hours)

    def minutes(self, minutes: int) -> Self:
        return self._plus(PostMetaKey.MINUTES, minutes)

    def seconds(self, seconds: int) -> Self:
        return self._plus(PostMetaKey.SECONDS, seconds)

    def production(self, production: Production) -> Self:
        return self._plus(PostMetaKey.PRODUCTION, production.value)

    def video_url(self, video_url: str) -> Self:
        return self._plus(PostMetaKey.VIDEOURL, video_url)

    def duration(self, duration: int) -> Self:
        return self._plus(PostMetaKey.DURATION, duration)

    def yoast_focuskw(self, yoast_focuskw: str) -> Self:
        return self._plus(PostMetaKey.YOAST_FOCUSKW, yoast_focuskw)

    def yoast_metadesc(self, yoast_metadesc: str) -> Self:
        return self._plus(PostMetaKey.YOAST_METADESC, yoast_metadesc)

    def thumbnail(self, thumbnail: str) -> Self:
        return self._plus(PostMetaKey.THUMBNAIL, thumbnail)

    def orientation(self, orientation: Orientation) -> Self:
        return self._plus(PostMetaKey.ORIENTATION, orientation.value)

    def ethnicity(self, ethnicity: Ethnicity) -> Self:
        return self._plus(PostMetaKey.ETHNICITY, ethnicity.value)

    def hair_color(self, hair_color: HairColor) -> Self:
        return self._plus(PostMetaKey.HAIRCOLOR, hair_color.value)

    def partner(self, partner: str) -> Self:
        return self._plus(PostMetaKey.PARTNER, partner)

    def hd(self, hd: ToggleField) -> Self:
        return self._plus(PostMetaKey.HD, True if hd == ToggleField.ON else False)

    def add(self, key: PostMetaKey, value: Union[str, int, bool]) -> Self:
        return self._plus(key, value)
