"""
Config_mgr (Configuration Manager) module

Store and load the secrets necessary for interaction with other services.
Load important configuration variables that affect the project's behaviour.

This module was implemented in order to resolve issues reading directly
from the data structures that store those secrets and configs.

For example, several IndexError were raised due to relative references to files
in module operations.

"""
import importlib.resources
from dataclasses import dataclass
from core.helpers import clean_filename
from core.custom_exceptions import ConfigFileNotFound
from configparser import ConfigParser
import os


@dataclass(frozen=True)
class WPAuth:
    user: str
    app_password: str
    author_admin: str
    hostname: str
    api_base_url: str
    full_base_url: str
    default_status: str


@dataclass(frozen=True)
class MongerCashAuth:
    username: str
    password: str


@dataclass(frozen=True)
class YandexAuth:
    client_id: str
    client_secret: str


@dataclass(frozen=True)
class ContentSelectConf:
    thumbnail_dir: str
    wp_json_posts: str
    wp_cache_config: str
    pic_format: str
    sql_query: str
    content_hint: str
    partners: str


@dataclass(frozen=True)
class GallerySelectConf:
    thumbnails_dir: str
    temp_dir: str
    pic_format: str
    wp_json_photos: str
    wp_json_posts: str
    wp_cache_config: str
    content_hint: str
    partners: str


@dataclass()
class EmbedAssistConf:
    thumbnail_dir: str
    wp_json_posts: str
    wp_cache_config: str
    pic_format: str
    sql_query: str
    content_hint: str
    partners: str


def parse_client_config(ini_file: str, package_name: str) -> ConfigParser:
    """Parse a client configuration files that store secrets and other configurations.

    :param ini_file: ``str`` ini filename with or without the extension
    :param package_name: ``str`` package name where the config file is located.
    :return: ``ConfigParser``
    """
    f_ini = clean_filename(ini_file, "ini")
    config = ConfigParser()
    with importlib.resources.path(package_name, f_ini) as f_path:
        if os.path.exists(f_path):
            config.read(f_path)
        else:
            raise ConfigFileNotFound(str(f_path))
    return config


# client_info.ini
client_info = parse_client_config('client_info', 'core.config')

WP_CLIENT_INFO = WPAuth(
    user=client_info['WP_Admin']['user'],
    app_password=client_info['WP_Admin']['app_password'],
    author_admin=client_info['WP_Admin']['author_admin'],
    hostname=client_info['WP_Admin']['hostname'],
    api_base_url=client_info['WP_Admin']['api_base_url'],
    full_base_url=client_info['WP_Admin']['full_base_url'],
    default_status=client_info['WP_Admin']['default_status']
)

MONGER_CASH_INFO = MongerCashAuth(
    username=client_info['MongerCash']['username'],
    password=client_info['MongerCash']['password'],
)

YANDEX_INFO = YandexAuth(
    client_id=client_info['Yandex']['client_id'],
    client_secret=client_info['Yandex']['client_secret'],
)

# workflows_config.ini
workflows_config = parse_client_config('workflows_config', 'core.config')

CONTENT_SEL_CONF = ContentSelectConf(
    thumbnail_dir=workflows_config['content_select']['thumbnails_folder'],
    wp_json_posts=workflows_config['content_select']['wp_json_posts'],
    wp_cache_config=workflows_config['content_select']['wp_cache_config'],
    pic_format=workflows_config['content_select']['pic_format'],
    sql_query=workflows_config['content_select']['sql_query'],
    content_hint=workflows_config['content_select']['db_content_hint'],
    partners=workflows_config['content_select']['partners']
)

GALLERY_SEL_CONF = GallerySelectConf(
    thumbnails_dir=workflows_config['gallery_select']['thumbnails_folder'],
    temp_dir=workflows_config['gallery_select']['tmp_folder'],
    pic_format=workflows_config['gallery_select']['pic_format'],
    wp_json_photos=workflows_config['gallery_select']['wp_json_photos'],
    wp_json_posts=workflows_config['gallery_select']['wp_json_posts'],
    wp_cache_config=workflows_config['gallery_select']['wp_cache_config'],
    content_hint=workflows_config['gallery_select']['db_content_hint'],
    partners=workflows_config['gallery_select']['partners']
)

EMBED_ASSIST_CONF = EmbedAssistConf(
    thumbnail_dir=workflows_config['embed_assist']['thumbnails_folder'],
    wp_json_posts=workflows_config['embed_assist']['wp_json_posts'],
    wp_cache_config=workflows_config['embed_assist']['wp_cache_config'],
    pic_format=workflows_config['embed_assist']['pic_format'],
    sql_query=workflows_config['embed_assist']['sql_query'],
    content_hint=workflows_config['embed_assist']['db_content_hint'],
    partners=workflows_config['embed_assist']['partners']
)