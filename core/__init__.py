"""
Common utilities for the project.

This package includes helper functions and custom exceptions.
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"
__version__ = "1.0.0"

# Config_mgr constants
from core.config_mgr import (
    wp_auth,
    monger_cash_auth,
    gallery_select_conf,
    content_select_conf,
    embed_assist_conf,
    tasks_conf,
    x_auth,
    bot_father,
    update_mcash_conf,
    brave_auth,
)


# Custom Exceptions `custom_exceptions.py`
from core.custom_exceptions import (
    InvalidInput,
    NoSuitableArgument,
    UnsupportedParameter,
    RefreshTokenError,
    HotFileSyncIntegrityError,
    AssetsNotFoundError,
    AccessTokenRetrievalError,
    UnavailableLoggingDirectory,
    NoFieldsException,
    InvalidDB,
    BraveAPIValidationError,
    BraveAPIInvalidCountryCode,
    BraveAPIInvalidLanguageCode,
    MissingCacheError,
)


# Project helper functions `helpers.py`
from core.helpers import (
    access_url,
    access_url_bs4,
    clean_console,
    clean_filename,
    clean_file_cache,
    export_request_json,
    fetch_data_sql,
    filename_creation_helper,
    filename_select,
    get_duration,
    generate_random_str,
    sha256_hash_generate,
    str_encode_b64,
    get_token_oauth,
    get_webdriver,
    is_parent_dir_required,
    load_file_path,
    load_from_file,
    load_json_ctx,
    lst_dict_to_csv,
    match_list_elem_date,
    match_list_mult,
    match_list_single,
    parse_date_to_iso,
    parse_client_config,
    remove_if_exists,
    search_files_by_ext,
    split_char,
    write_to_file,
    write_config_file,
)

__all__ = [
    "NoSuitableArgument",
    "UnsupportedParameter",
    "InvalidInput",
    "RefreshTokenError",
    "HotFileSyncIntegrityError",
    "AssetsNotFoundError",
    "AccessTokenRetrievalError",
    "UnavailableLoggingDirectory",
    "NoFieldsException",
    "InvalidDB",
    "BraveAPIValidationError",
    "BraveAPIInvalidCountryCode",
    "BraveAPIInvalidLanguageCode",
    "MissingCacheError",
    "access_url",
    "access_url_bs4",
    "clean_console",
    "clean_filename",
    "clean_file_cache",
    "filename_creation_helper",
    "filename_select",
    "export_request_json",
    "get_duration",
    "generate_random_str",
    "sha256_hash_generate",
    "str_encode_b64",
    "get_token_oauth",
    "get_webdriver",
    "is_parent_dir_required",
    "match_list_elem_date",
    "match_list_mult",
    "match_list_single",
    "load_file_path",
    "load_from_file",
    "load_json_ctx",
    "lst_dict_to_csv",
    "parse_date_to_iso",
    "parse_client_config",
    "remove_if_exists",
    "search_files_by_ext",
    "split_char",
    "update_mcash_conf",
    "write_to_file",
    "write_config_file",
    "wp_auth",
    "monger_cash_auth",
    "gallery_select_conf",
    "content_select_conf",
    "embed_assist_conf",
    "tasks_conf",
    "x_auth",
    "bot_father",
    "brave_auth",
]
