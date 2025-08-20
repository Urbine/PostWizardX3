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
    LOGIN = "auth/login"
