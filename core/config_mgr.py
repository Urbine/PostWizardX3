"""
Config_mgr (Configuration Manager) module

Store and load the secrets necessary for interaction with other services.
Load important configuration variables that affect the project's behaviour.

This module was implemented in order to resolve issues reading directly
from the data structures that store those secrets and configs.

For example, several IndexError were raised due to relative references to files
in module operations.

"""

from dataclasses import dataclass
from core.helpers import parse_client_config


@dataclass(frozen=True)
class WPAuth:
    user: str
    app_password: str
    author_admin: str
    hostname: str
    api_base_url: str
    full_base_url: str
    default_status: str
    wp_cache_file: str
    wp_posts_file: str
    wp_photos_file: str


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
    sql_query: str
    content_hint: str
    partners: str


@dataclass(frozen=True)
class EmbedAssistConf:
    thumbnail_dir: str
    wp_json_posts: str
    wp_cache_config: str
    pic_format: str
    sql_query: str
    content_hint: str
    partners: str


# client_info.ini
client_info = parse_client_config('client_info', 'core.config')

WP_CLIENT_INFO = WPAuth(
    user=client_info['WP_Admin']['user'],
    app_password=client_info['WP_Admin']['app_password'],
    author_admin=client_info['WP_Admin']['author_admin'],
    hostname=client_info['WP_Admin']['hostname'],
    api_base_url=client_info['WP_Admin']['api_base_url'],
    full_base_url=client_info['WP_Admin']['full_base_url'],
    default_status=client_info['WP_Admin']['default_status'],
    wp_cache_file=client_info['WP_Admin']['wp_cache_file'],
    wp_posts_file=client_info['WP_Admin']['wp_posts_file'],
    wp_photos_file=client_info['WP_Admin']['wp_photos_file'],
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
    sql_query=workflows_config['gallery_select']['sql_query'],
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
