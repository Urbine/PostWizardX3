# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Rest endpoints

This module provides a class-based interface to interact with the PostWizard REST API,
enabling retrieval and management of post meta fields and posts.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from enum import Enum


class APIUrl(Enum):
    API_VERSION = "v1"
    POSTS = "posts"
    POSTS_META = "meta"
    DUMP = "dump"
    BATCH = "batch"
    LOGIN = "auth/login"
    TAXONOMIES = "taxonomies"
    TAXONOMIES_CHECK = "check"
    TAXONOMIES_ADD = "add"
    TAXONOMY_REMOVE = "remove"


class QueryParams(Enum):
    TYPE = "type"
    LINK = "link"
    UNLINK = "unlink"
    POST_ID = "id"
    AUTO_THUMB = "autothumb"
    RETRIES = "retries"
    TIMEOUT = "timeout"
