"""
Core Utilities Package

This module provides essential utilities, helpers, and exception handling for the project.
It centralizes core functionality used across different parts of the application.

Key components:
- Custom exceptions for standardized error handling
- Helper functions for common operations (file I/O, string manipulation, network requests)
- Configuration management via the config_mgr module
- Authentication handlers for various services (WordPress, MongoDB, X/Twitter)
- Data transformation and processing utilities

The module is designed with a focus on reusability, maintainability, and consistent
error handling patterns to ensure reliable operation across the entire application.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
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
    google_search_conf,
)


# Custom Exceptions `custom_exceptions.py`
from core.custom_exceptions import (
    UnableToConnectError,
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
    ClientInfoSecretsNotFound,
    InvalidSQLConfig,
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
    singleton,
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
    "ClientInfoSecretsNotFound",
    "UnableToConnectError",
    "InvalidSQLConfig",
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
    "singleton",
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
    "google_search_conf",
]
