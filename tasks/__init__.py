"""
The `Tasks` package guides some workflows in this project, specifically
those concerned with file/database updates and single-responsibility programs
that are meant to be called as modules by the former.

"""
__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = '1.0.0'

# ** MongerCash Dump Creation `mcash_dump_create.py` **

from tasks.mcash_dump_create import parse_partner_name
from tasks.mcash_dump_create import get_vid_dump_flow

# ** MongerCash Photo Set Scrape `m_cash_scrape.py` **
from tasks.mcash_scrape import get_set_source_flow
# ** MongerCash TXT dump parser
from tasks.parse_txt_dump import parse_txt_dump
# ** MongerCash HTML photoset dump parser
from tasks.sets_source_parse import db_generate

__all__ = ['parse_partner_name',
           'get_vid_dump_flow',
           'get_set_source_flow',
           'db_generate',
           'parse_txt_dump']
