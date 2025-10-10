"""
Client Schema

This module defines the PostMetaKey and PostKey classes, which are used to represent
the keys of the PostMeta and Post objects in the PostWizard Server API.

This module also defines the PostType, Ethnicity, Orientation, and HairColor classes,
which are used to represent the values of the PostMetaKey and PostKey objects in a
consistent manner, although all values provided are validated in the server side.

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


class Ethnicity(Enum):
    ASIAN = "asian"
    MIXED = "mixed"
    MIDDLE_EASTERN = "middle eastern"
    EBONY = "ebony"
    LATINO = "latino"
    WHITE = "white"
    INDIAN = "indian"


class Orientation(Enum):
    STRAIGHT = "straight"
    TRANS = "trans"


class HairColor(Enum):
    BLONDE = "blonde"
    BROWN = "brown"
    BLACK = "black"
    RED = "red"
    OTHER = "other"


class Production(Enum):
    PROFESSIONAL = "professional"
    HOMEMADE = "homemade"


class ToggleField(Enum):
    ON = "on"
    OFF = "off"


class Taxonomy(Enum):
    MODEL = "pornstars"
    TAG = "post_tag"
    CATEGORY = "category"


class TaxonomyMeta(Enum):
    TAXONOMY = "taxonomy"
    TAXONOMY_NAME = "taxonomy_name"
    TAXONOMY_DESCRIPTION = "taxonomy_description"


class TaxonomyInfo(Enum):
    TERM = "term"
    SLUG = "slug"
