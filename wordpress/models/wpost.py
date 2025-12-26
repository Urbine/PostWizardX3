# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
WPost
This module defines the WPost class, which represents a WordPress post with basic information.
It will be used to store the data of the posts that a running instance has created and that allows other
modules to access the information contained in them for further processing.

Attributes:
    post_id (int): The ID of the post.
    title (str): The title of the post.
    slug (str): The slug of the post.
    content (str): The content of the post.
    ptype (str): The post type of the post.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from dataclasses import dataclass


@dataclass
class WPost:
    post_id: int
    title: str
    slug: str
    content: str
    ptype: str
    author: str
