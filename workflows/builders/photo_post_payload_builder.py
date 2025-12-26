# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
PhotoPostPayloadBuilder class

This class is a builder for a simple WordPress photo post payload
specific for the workflows in this package.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


from typing import Self, List, Dict, Union
import os

from workflows.builders import WorkflowSlugBuilder
from wordpress.builders import PostPayloadBuilder

from wordpress.models import ImagePayloadItem


class PhotoPostPayloadBuilder(PostPayloadBuilder):
    def __init__(self):
        super().__init__()

    def tags(self, tags: list[int]) -> Self:
        self._plus(ImagePayloadItem.PHOTOS_TAG, tags)
        return self

    def photos_payload_factory(
        self,
        status_wp: str,
        set_name: str,
        partner_name: str,
        tags: List[int],
        reverse_slug: bool = False,
    ) -> Dict[str, Union[str, int]]:
        """
        Factory method for class ``WorkflowPostPayloadBuilder`` to make WordPress ``JSON`` payload with the supplied values.
        for photo gallery posts.

        :param status_wp: ``str`` typically ``draft`` but it can be ``publish``, however, all posts need review.
        :param set_name: ``str`` photo gallery name.
        :param partner_name: ``str`` partner offer that I am promoting
        :param tags: ``list[int]`` tag IDs that will be sent to WordPress for classification and integration.
        :param reverse_slug: ``bool`` ``True`` if you want to reverse the permalink (slug) construction by placing the partner name first.
        :return: ``dict[str, str | int]``
        """
        if reverse_slug:
            # '-pics' tells Google the main content of the page.
            final_slug: str = (
                WorkflowSlugBuilder(enforce_unique=True, stopword_removal=True)
                .title(set_name)
                .partner(partner_name)
                .content_type("pics")
                .build()
            )
        else:
            final_slug: str = (
                WorkflowSlugBuilder(enforce_unique=True, stopword_removal=True)
                .partner(partner_name)
                .title(set_name)
                .content_type("pics")
                .build()
            )

        # Setting Env variable since the slug is needed outside this function.
        os.environ["SET_SLUG"] = final_slug

        post_payload = (
            self.slug(final_slug)
            .status(status_wp)
            .type("photos")
            .title(set_name)
            .featured_media(0)
            .tags(tags)
        )
        return post_payload.build(mutable=True)
