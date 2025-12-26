# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
API URL Builder

This module defines the APIUrlBuilder class, which is a subclass of URLBuilder.
It provides methods to construct URLs for specific endpoints, such as retrieving posts and
post meta fields for now.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self

# Local imports
from core.config.config_factories import web_sources_conf_factory
from postwizard_sdk.models import APIUrl, PostType, QueryParams
from postwizard_sdk.builders.interfaces import URLBuilder


class APIUrlBuilder(URLBuilder):
    def __init__(self):
        super().__init__(web_sources_conf_factory().pw_api_base_url.strip("/"))

    def taxonomies_add(self) -> Self:
        return self._plus_path(APIUrl.TAXONOMIES, APIUrl.TAXONOMIES_ADD)

    def taxonomies_check(self) -> Self:
        return self._plus_path(APIUrl.TAXONOMIES, APIUrl.TAXONOMIES_CHECK)

    def taxonomies_link(self, post_id: int) -> Self:
        return (
            self._plus_path(APIUrl.TAXONOMIES, APIUrl.TAXONOMIES_CHECK)
            ._plus_query_param(QueryParams.POST_ID, post_id)
            ._plus_query_param(QueryParams.LINK, str(True).lower())
        )

    def taxonomies_unlink(self, post_id: int) -> Self:
        return (
            self._plus_path(APIUrl.TAXONOMIES, APIUrl.TAXONOMIES_CHECK)
            ._plus_query_param(QueryParams.POST_ID, post_id)
            ._plus_query_param(QueryParams.UNLINK, str(True).lower())
        )

    def taxonomies_remove(self) -> Self:
        return self._plus_path(APIUrl.TAXONOMIES, APIUrl.TAXONOMY_REMOVE)

    def posts(self, post_id: int) -> Self:
        return self._plus_path(APIUrl.POSTS, post_id)

    def posts_dump_by_type(self, post_type: PostType) -> Self:
        return self._plus_path(APIUrl.POSTS, APIUrl.DUMP)._plus_query_param(
            QueryParams.TYPE, post_type
        )

    def post_batch(self) -> Self:
        return self._plus_path(APIUrl.POSTS, APIUrl.BATCH)

    def posts_meta(
        self,
        post_id: int,
        auto_thumb: bool = False,
        retries: int = 5,
        timeout: int = 1,
    ) -> Self:
        builder = self._plus_path(APIUrl.POSTS, "")._plus_path(
            APIUrl.POSTS_META, post_id
        )
        return (
            builder._plus_query_param(QueryParams.AUTO_THUMB, str(auto_thumb).lower())
            ._plus_query_param(QueryParams.RETRIES, retries)
            ._plus_query_param(QueryParams.TIMEOUT, timeout)
            if auto_thumb
            else builder
        )

    def post_meta_dump(self):
        return self._plus_path(APIUrl.POSTS, "")._plus_path(
            APIUrl.POSTS_META, APIUrl.DUMP
        )

    def post_meta_batch(self):
        return self._plus_path(APIUrl.POSTS, "")._plus_path(
            APIUrl.POSTS_META, APIUrl.BATCH
        )

    def login(self) -> Self:
        return self._plus_path(APIUrl.LOGIN, "")
