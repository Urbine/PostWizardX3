from core.utils.decorators import singleton
from core.config.config_factories import (
    ai_config_factory,
    general_config_factory,
    image_config_factory,
    social_config_factory,
)

from core.exceptions.data_access_exceptions import (
    InvalidDB,
    InvalidSQLConfig,
    UnableToConnectError,
)
from core.exceptions.config_exceptions import (
    SectionsNotFoundError,
    ClientSecretsNotFound,
    InvalidAIConfig,
)
from core.exceptions.util_exceptions import (
    NoSuitableArgument,
    InvalidInput,
    UnsupportedParameter,
    UnavailableLoggingDirectory,
    UnsupportedPlatform,
    InvalidOperationMode,
)

from core.utils.helpers import (
    get_dict_key,
    get_duration,
)
from core.utils.data_access import (
    access_url_bs4,
    access_url,
    fetch_data_sql,
    get_token_oauth,
    get_webdriver,
)
from core.utils.parsers import parse_client_config, parse_date_to_iso
from core.utils.file_system import (
    clean_file_cache,
    filename_creation_helper,
    filename_select,
    export_request_json,
    lst_dict_to_csv,
    is_parent_dir_required,
    load_file_path,
    load_json_ctx,
    load_from_file,
    remove_if_exists,
    search_files_by_ext,
    write_to_file,
    goto_project_root,
    logging_setup,
    create_store,
    apply_os_permissions,
)
from core.utils.system_shell import clean_console
from core.utils.strings import (
    clean_filename,
    match_list_single,
    match_list_mult,
    match_list_elem_date,
    str_encode_b64,
    sha256_hash_generate,
    generate_random_str,
    split_char,
)

__all__ = [
    "ai_config_factory",
    "general_config_factory",
    "get_dict_key",
    "get_duration",
    "image_config_factory",
    "social_config_factory",
]
