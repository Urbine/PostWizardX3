"""
The `Tasks` package guides some workflows in this project, specifically
those concerned with file/database updates and single-responsibility programs
that are meant to be called as modules by the former.

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = "1.0.0"

# ** MongerCash Dump Creation `mcash_dump_create.py` **
from workflows.tasks.mcash_dump_create import parse_partner_name, get_vid_dump_flow

# ** MongerCash Photo Set Scrape `m_cash_scrape.py` **
from workflows.tasks.mcash_scrape import get_set_source_flow

# ** MongerCash TXT dump parser
from workflows.tasks.parse_txt_dump import parse_txt_dump_chain

# ** MongerCash HTML photoset dump parser
from workflows.tasks.sets_source_parse import db_generate

# ** Clean outdated files
from workflows.tasks.clean_outdated_files import clean_outdated

__all__ = [
    "parse_partner_name",
    "get_vid_dump_flow",
    "get_set_source_flow",
    "db_generate",
    "parse_txt_dump_chain",
]
