"""
Common utilities for the project.

This package includes helper functions and custom exceptions.
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = "1.0.0"

# Config_mgr constants
from core.config_mgr import wp_auth
from core.config_mgr import monger_cash_auth
from core.config_mgr import gallery_select_conf
from core.config_mgr import content_select_conf
from core.config_mgr import embed_assist_conf
from core.config_mgr import tasks_conf
from core.config_mgr import x_auth

# Custom Exceptions `custom_exceptions.py`
from core.custom_exceptions import InvalidInput
from core.custom_exceptions import NoSuitableArgument
from core.custom_exceptions import UnsupportedParameter

# Project helper functions `helpers.py`
from core.helpers import access_url
from core.helpers import access_url_bs4
from core.helpers import clean_filename
from core.helpers import clean_file_cache
from core.helpers import clean_path
from core.helpers import cwd_or_parent_path
from core.helpers import export_client_info
from core.helpers import export_request_json
from core.helpers import export_to_csv_nt
from core.helpers import fetch_data_sql
from core.helpers import filename_creation_helper
from core.helpers import filename_select
from core.helpers import get_client_info
from core.helpers import get_dict_key
from core.helpers import get_duration
from core.helpers import get_from_db
from core.helpers import get_project_db
from core.helpers import generate_random_str
from core.helpers import get_token_oauth
from core.helpers import get_webdriver
from core.helpers import is_parent_dir_required
from core.helpers import load_file_path
from core.helpers import load_from_file
from core.helpers import load_json_ctx
from core.helpers import match_list_elem_date
from core.helpers import match_list_mult
from core.helpers import match_list_single
from core.helpers import parse_date_to_iso
from core.helpers import remove_if_exists
from core.helpers import search_files_by_ext
from core.helpers import write_to_file

__all__ = [
    "NoSuitableArgument",
    "UnsupportedParameter",
    "InvalidInput",
    "access_url",
    "access_url_bs4",
    "clean_filename",
    "clean_file_cache",
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
    "generate_random_str",
    "get_token_oauth",
    "get_webdriver",
    "is_parent_dir_required",
    "match_list_elem_date",
    "match_list_mult",
    "load_file_path",
    "load_from_file",
    "load_json_ctx",
    "parse_date_to_iso",
    "remove_if_exists",
    "search_files_by_ext",
    "write_to_file",
    "wp_auth",
    "monger_cash_auth",
    "gallery_select_conf",
    "content_select_conf",
    "embed_assist_conf",
    "tasks_conf",
    "x_auth",
]
