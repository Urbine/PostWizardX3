"""
Common utilities for the project.

This package includes helper functions and custom exceptions.
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = "1.0.0"

# Auth dataclass constants
from common.config_mgr import WP_CLIENT_INFO
from common.config_mgr import MONGER_CASH_INFO

# Custom Exceptions `custom_exceptions.py`
from common.custom_exceptions import InvalidInput
from common.custom_exceptions import NoSuitableArgument

# Project helper functions `helpers.py`
from common.helpers import access_url
from common.helpers import access_url_bs4
from common.helpers import clean_filename
from common.helpers import clean_path
from common.helpers import cwd_or_parent_path
from common.helpers import export_client_info
from common.helpers import export_request_json
from common.helpers import export_to_csv_nt
from common.helpers import fetch_data_sql
from common.helpers import filename_creation_helper
from common.helpers import filename_select
from common.helpers import get_client_info
from common.helpers import get_dict_key
from common.helpers import get_duration
from common.helpers import get_from_db
from common.helpers import get_project_db
from common.helpers import get_token_oauth
from common.helpers import get_webdriver
from common.helpers import is_parent_dir_required
from common.helpers import load_from_file
from common.helpers import load_json_ctx
from common.helpers import match_list_elem_date
from common.helpers import match_list_mult
from common.helpers import match_list_single
from common.helpers import parse_client_config
from common.helpers import parse_date_to_iso
from common.helpers import remove_if_exists
from common.helpers import search_files_by_ext
from common.helpers import write_to_file

__all__ = [
    "NoSuitableArgument",
    "InvalidInput",
    "access_url",
    "access_url_bs4",
    "clean_filename",
    "clean_path",
    "cwd_or_parent_path",
    "filename_creation_helper",
    "filename_select",
    "export_client_info",
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
    "parse_client_config",
    "parse_date_to_iso",
    "remove_if_exists",
    "search_files_by_ext",
    "write_to_file",
    "WP_CLIENT_INFO",
    "MONGER_CASH_INFO"
]
