"""
Client Schema

This module defines the PostMetaKey and PostKey classes, which are used to represent
the keys of the PostMeta and Post objects in the PostWizard Server API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from enum import Enum


class PostMetaKey(Enum):
    HD = "hd"
    ID = "postID"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    EMBED_CODE = "embedCode"
    PARTNER = "partner"
    ORIENTATION = "orientation"
    ETHNICITY = "ethnicity"
    HAIRCOLOR = "hairColor"
    THUMBNAIL = "thumbURL"
    PRODUCTION = "production"
    VIDEOURL = "videoURL"
    DURATION = "duration"
    YOAST_FOCUSKW = "yoastFocusKw"
    YOAST_METADESC = "yoastMetaDesc"


class PostKey(Enum):
    ID = "postID"
    AUTHOR = "author"
    CONTENT = "content"
    TITLE = "title"
    SLUG = "slug"
    STATUS = "status"
    TYPE = "type"


class PostType(Enum):
    POST = "post"
    ATTACHMENT = "attachment"
    PHOTOS = "photos"
    ALL = "all"
