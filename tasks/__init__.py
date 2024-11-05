"""
The `Tasks` package guides some workflows in this project, specifically
those concerned with file/database updates and single-responsibility programs
that are meant to be called as modules by the former.

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = '1.0.0'

# ** MediaSource Dump Creation `feed_dump_create.py` **

# Functions
from tasks.feed_dump_create import get_partner_name
from tasks.feed_dump_create import get_vid_dump_flow

# Constants
from tasks.feed_dump_create import FEED_DUMP_URL
from tasks.feed_dump_create import MEDIA_SOURCE_USERNAME
from tasks.feed_dump_create import MEDIA_SOURCE_PASSWD

# ** MediaSource Photo Set Scrape `media_source_scrape.py` **
from tasks.feed_scrape import get_page_source_flow

# Contants
from tasks.feed_scrape import FEED_SETS_URL
from tasks.feed_scrape import MEDIA_SOURCE_HOSTED_URL

# ** MediaSource TXT dump parser
from tasks.parse_txt_dump import parse_txt_dump

# ** MediaSource HTML photoset dump parser
from tasks.sets_source_parse import db_generate

__all__ = ['get_partner_name',
           'get_vid_dump_flow',
           'get_page_source_flow',
           'db_generate',
           'parse_txt_dump',
           'FEED_DUMP_URL',
           'MEDIA_SOURCE_HOSTED_URL',
           'MEDIA_SOURCE_USERNAME',
           'MEDIA_SOURCE_PASSWD',
           'FEED_SETS_URL']