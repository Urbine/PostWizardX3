"""
Common utilities for the project.

This package includes helper functions and custom exceptions.
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = "1.0.0"

# Custom Exceptions `custom_exceptions.py`
from .custom_exceptions import NoSuitableArgument

# Project helper functions `helpers.py`
from .helpers import access_url
from .helpers import access_url_bs4
from .helpers import clean_filename
from .helpers import clean_path
from .helpers import cwd_or_parent_path
from .helpers import export_request_json
from .helpers import export_to_csv_nt
from .helpers import fetch_data_sql
from .helpers import filename_creation_helper
from .helpers import filename_select
from .helpers import get_client_info
from .helpers import get_dict_key
from .helpers import get_duration
from .helpers import get_from_db
from .helpers import get_project_db
from .helpers import get_token_oauth
from .helpers import get_webdriver
from .helpers import is_parent_dir_required
from .helpers import load_from_file
from .helpers import load_json_ctx
from .helpers import match_list_elem_date
from .helpers import match_list_mult
from .helpers import match_list_single
from .helpers import parse_date_to_iso
from .helpers import remove_if_exists
from .helpers import search_files_by_ext
from .helpers import write_to_file

__all__ = [
    "NoSuitableArgument",
    "access_url",
    "access_url_bs4",
    "clean_filename",
    "clean_path",
    "cwd_or_parent_path",
    "filename_creation_helper",
    "filename_select",
    "export_request_json",
    "export_to_csv_nt",
    "get_client_info",
    "get_dict_key",
    "get_duration",
    "get_from_db",
    "get_project_db",
    "get_token_oauth",
    "get_webdriver",
    "is_parent_dir_required",
    "match_list_elem_date",
    "match_list_mult",
    "load_from_file",
    "load_json_ctx",
    "parse_date_to_iso",
    "remove_if_exists",
    "search_files_by_ext",
    "write_to_file",
]
