"""
Config_mgr (Configuration Manager) Module

Centralized configuration management system for handling service authentication and application settings.
This module provides:

1. Immutable dataclass structures for storing configuration parameters
2. Factory functions that load values from configuration files
3. Standardized access to secrets and configuration variables

Key features:
- Immutable dataclasses prevent unexpected modification of configuration values
- Configuration changes are only possible through config file updates
- Centralized error handling for missing configuration values
- Structured access to service credentials and application behavior settings

The immutable design pattern ensures a consistent configuration state throughout
the application lifecycle, eliminating side effects and configuration-related bugs.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import os
from dataclasses import dataclass

from core.helpers import parse_client_config, singleton
from core.custom_exceptions import InvalidConfiguration, ClientInfoSecretsNotFound

CONFIG_PKG = "core.config"
CLIENT_INFO_INI = parse_client_config("client_info", CONFIG_PKG)
WORKFLOWS_CONFIG_INI = parse_client_config("workflows_config", CONFIG_PKG)
TASKS_CONFIG_INI = parse_client_config("tasks_config", CONFIG_PKG)

# Environment variable set the in parse_client_config() function in the helpers.py file.
CONFIG_PATH = os.environ.get("CONFIG_PATH")


@singleton
@dataclass(frozen=True, kw_only=True)
class WPAuth:
    """
    Immutable dataclass responsible for holding WordPress secret structure,
    site information, configuration filenames, and behavioural constants.
    """

    api_base_url: str
    app_password: str
    author_admin: str
    full_base_url: str
    default_status: str
    hostname: str
    user: str
    wp_cache_file: str
    wp_photos_file: str
    wp_posts_file: str

    def __repr__(self):
        return "WPAuth()"


@singleton
@dataclass(frozen=True, kw_only=True)
class MongerCashAuth:
    """
    Immutable dataclass with the MongerCash secret structure.
    """

    username: str
    password: str

    def __repr__(self):
        return "MongerCash(username, password)"


@singleton
@dataclass(frozen=True, kw_only=True)
class YandexAuth:
    """
    Immutable dataclass responsible for ordering Yandex API details.
    """

    client_id: str
    client_secret: str

    def __repr__(self):
        return "YandexAuth(client_id, client_secret)"


@singleton
@dataclass(frozen=True, kw_only=True)
class ContentSelectConf:
    """
    Immutable dataclass responsible for holding content-select
    bot configuration variables and behavioural tweaks.
    """

    assets_conf: str
    content_hint: str
    domain_tld: str
    imagick: bool
    img_attrs: bool
    logging_dirname: str
    partners: str
    pic_fallback: str
    pic_format: str
    quality: int
    site_name: str
    sql_query: str
    telegram_posting_auto: bool
    telegram_posting_enabled: bool
    wp_json_posts: str
    wp_cache_config: str
    x_posting_auto: bool
    x_posting_enabled: bool

    def __repr__(self):
        return "ContentSelectConf()"


@singleton
@dataclass(frozen=True, kw_only=True)
class GallerySelectConf:
    """
    Immutable dataclass responsible for holding gallery-select
    bot configuration variables and behavioural tweaks.
    """

    content_hint: str
    domain_tld: str
    imagick: bool
    img_attrs: bool
    logging_dirname: str
    partners: str
    pic_fallback: str
    pic_format: str
    quality: int
    reverse_slug: bool
    site_name: str
    sql_query: str
    telegram_posting_auto: bool
    telegram_posting_enabled: bool
    wp_json_photos: str
    wp_json_posts: str
    wp_cache_config: str
    x_posting_auto: bool
    x_posting_enabled: bool

    def __repr__(self):
        return "GallerySelectConf()"


@singleton
@dataclass(frozen=True, kw_only=True)
class EmbedAssistConf:
    """
    Immutable dataclass responsible for holding embed-assist
    bot configuration variables and behavioural tweaks.
    """

    content_hint: str
    domain_tld: str
    imagick: bool
    img_attrs: bool
    logging_dirname: str
    partners: str
    pic_fallback: str
    pic_format: str
    quality: int
    site_name: str
    sql_query: str
    telegram_posting_auto: bool
    telegram_posting_enabled: bool
    wp_json_posts: str
    wp_cache_config: str
    x_posting_auto: bool
    x_posting_enabled: bool

    def __repr__(self):
        return "EmbedAssistConf()"


@singleton
@dataclass(frozen=True, kw_only=True)
class TasksConf:
    """
    Immutable dataclass for configuration constants for the ``tasks`` package.
    """

    mcash_dump_url: str
    mcash_set_url: str

    def __repr__(self):
        return "TasksConf()"


@singleton
@dataclass(frozen=True, kw_only=True)
class XAuth:
    """
    Immutable dataclass responsible for structuring X platform secrets
    and API configurable and non-constant parameters.
    """

    access_token: str
    api_key: str
    api_secret: str
    client_id: str
    client_secret: str
    refresh_token: str
    uri_callback: str
    x_username: str
    x_passw: str
    x_email: str

    def __repr__(self):
        return "XAuth(client_id, client_secret)"


@singleton
@dataclass(frozen=True, kw_only=True)
class BotAuth:
    """
    Immutable class in charge of providing secrets for the BotFather
    service for Telegram Bot implementations.
    """

    telegram_chat_id: str
    token: str

    def __repr__(self):
        return "BotAuth()"


@singleton
@dataclass(frozen=True, kw_only=True)
class BraveAuth:
    """
    Immutable data class for the Brave Search API and its modes.
    """

    api_key_search: str

    def __repr__(self):
        return "BraveAuth()"


@singleton
@dataclass(frozen=True, kw_only=True)
class GoogleSearch:
    api_key: str
    cse_id_img: str
    cse_id_web: str

    def __repr__(self):
        return "GoogleSearch()"


@singleton
@dataclass(frozen=True, kw_only=True)
class UpdateMCash:
    """
    Immutable class with behavioral tweaks for
    """

    logging_dirname: str

    def __repr__(self):
        return "UpdateMCash()"


def wp_auth() -> WPAuth:
    """Factory function for dataclass ``WPAuth``

    :return: ``WPAuth``
    """
    try:
        return WPAuth(
            user=CLIENT_INFO_INI["WP_Admin"]["user"],
            app_password=CLIENT_INFO_INI["WP_Admin"]["app_password"],
            author_admin=CLIENT_INFO_INI["WP_Admin"]["author_admin"],
            hostname=CLIENT_INFO_INI["WP_Admin"]["hostname"],
            api_base_url=CLIENT_INFO_INI["WP_Admin"]["api_base_url"],
            full_base_url=CLIENT_INFO_INI["WP_Admin"]["full_base_url"],
            default_status=CLIENT_INFO_INI["WP_Admin"]["default_status"],
            wp_cache_file=CLIENT_INFO_INI["WP_Admin"]["wp_cache_file"],
            wp_posts_file=CLIENT_INFO_INI["WP_Admin"]["wp_posts_file"],
            wp_photos_file=CLIENT_INFO_INI["WP_Admin"]["wp_photos_file"],
        )
    except KeyError:
        raise ClientInfoSecretsNotFound(CONFIG_PATH)


def monger_cash_auth() -> MongerCashAuth:
    """Factory function for dataclass ``MongerCashAuth``

    :return: ``MongerCashAuth``
    """
    try:
        return MongerCashAuth(
            username=CLIENT_INFO_INI["MongerCash"]["username"],
            password=CLIENT_INFO_INI["MongerCash"]["password"],
        )
    except KeyError:
        raise ClientInfoSecretsNotFound(CONFIG_PATH)


def yandex_auth() -> YandexAuth:
    """Factory function for dataclass ``YandexAuth``

    :return: ``YandexAuth``
    """
    try:
        return YandexAuth(
            client_id=CLIENT_INFO_INI["Yandex"]["client_id"],
            client_secret=CLIENT_INFO_INI["Yandex"]["client_secret"],
        )
    except KeyError:
        raise ClientInfoSecretsNotFound(CONFIG_PATH)


def x_auth() -> XAuth:
    """Factory function for dataclass ``XAuth``

    :return: ``XAuth``
    """
    try:
        return XAuth(
            client_id=CLIENT_INFO_INI["x_api"]["client_id"],
            client_secret=CLIENT_INFO_INI["x_api"]["client_id"],
            api_key=CLIENT_INFO_INI["x_api"]["api_key"],
            api_secret=CLIENT_INFO_INI["x_api"]["api_secret"],
            uri_callback=CLIENT_INFO_INI["x_api"]["uri_callback"],
            x_username=CLIENT_INFO_INI["x_api"]["x_username"],
            x_passw=CLIENT_INFO_INI["x_api"]["x_passw"],
            x_email=CLIENT_INFO_INI["x_api"]["x_email"],
            access_token=CLIENT_INFO_INI["x_api"]["access_token"],
            refresh_token=CLIENT_INFO_INI["x_api"]["refresh_token"],
        )
    except KeyError:
        raise ClientInfoSecretsNotFound(CONFIG_PATH)


def bot_father() -> BotAuth:
    """Factory function for dataclass ``BotAuth``.

    :return: ``BotAuth``
    """
    try:
        return BotAuth(
            telegram_chat_id=CLIENT_INFO_INI["telegram_botfather"][
                "telegram_group_channel_id"
            ],
            token=CLIENT_INFO_INI["telegram_botfather"]["bot_token"],
        )
    except KeyError:
        raise ClientInfoSecretsNotFound(CONFIG_PATH)


def brave_auth() -> BraveAuth:
    """Factory function for dataclass ``BraveAuth``.

    :return: ``BraveAuth``
    """
    try:
        return BraveAuth(
            api_key_search=CLIENT_INFO_INI["brave_search_api"]["api_key_search"]
        )
    except KeyError:
        raise ClientInfoSecretsNotFound(CONFIG_PATH)


def content_select_conf() -> ContentSelectConf:
    """Factory function for dataclass ``ContentSelectConf``

    :return: ``ContentSelectConf``
    """
    try:
        return ContentSelectConf(
            wp_json_posts=WORKFLOWS_CONFIG_INI["general_config"]["wp_json_posts"],
            wp_cache_config=WORKFLOWS_CONFIG_INI["general_config"]["wp_cache_config"],
            pic_format=WORKFLOWS_CONFIG_INI["general_config"]["pic_format"],
            pic_fallback=WORKFLOWS_CONFIG_INI["general_config"]["fallback_pic_format"],
            imagick=WORKFLOWS_CONFIG_INI.getboolean(
                "general_config", "imagick_enabled"
            ),
            quality=WORKFLOWS_CONFIG_INI.getint("general_config", "conversion_quality"),
            sql_query=WORKFLOWS_CONFIG_INI["content_select"]["sql_query"],
            content_hint=WORKFLOWS_CONFIG_INI["content_select"]["db_content_hint"],
            assets_conf=WORKFLOWS_CONFIG_INI["content_select"]["assets_conf"],
            partners=WORKFLOWS_CONFIG_INI["content_select"]["partners"],
            site_name=WORKFLOWS_CONFIG_INI["general_config"]["website_name"],
            domain_tld=WORKFLOWS_CONFIG_INI["general_config"]["domain_tld"],
            logging_dirname=WORKFLOWS_CONFIG_INI["general_config"]["logging_dirname"],
            img_attrs=WORKFLOWS_CONFIG_INI.getboolean("general_config", "img_attrs"),
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                "content_select", "x_posting_auto"
            ),
            x_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                "content_select", "x_posting_enabled"
            ),
            telegram_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                "content_select", "telegram_posting_auto"
            ),
            telegram_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                "content_select", "telegram_posting_enabled"
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def gallery_select_conf() -> GallerySelectConf:
    """Factory function for dataclass ``EmbedAssistConf``

    :return: ``EmbedAssistConf``
    """
    try:
        return GallerySelectConf(
            pic_format=WORKFLOWS_CONFIG_INI["general_config"]["pic_format"],
            pic_fallback=WORKFLOWS_CONFIG_INI["general_config"]["fallback_pic_format"],
            imagick=WORKFLOWS_CONFIG_INI.getboolean(
                "general_config", "imagick_enabled"
            ),
            quality=WORKFLOWS_CONFIG_INI.getint("general_config", "conversion_quality"),
            wp_json_photos=WORKFLOWS_CONFIG_INI["gallery_select"]["wp_json_photos"],
            wp_json_posts=WORKFLOWS_CONFIG_INI["general_config"]["wp_json_posts"],
            wp_cache_config=WORKFLOWS_CONFIG_INI["general_config"]["wp_cache_config"],
            content_hint=WORKFLOWS_CONFIG_INI["gallery_select"]["db_content_hint"],
            sql_query=WORKFLOWS_CONFIG_INI["gallery_select"]["sql_query"],
            partners=WORKFLOWS_CONFIG_INI["gallery_select"]["partners"],
            site_name=WORKFLOWS_CONFIG_INI["general_config"]["website_name"],
            domain_tld=WORKFLOWS_CONFIG_INI["general_config"]["domain_tld"],
            logging_dirname=WORKFLOWS_CONFIG_INI["general_config"]["logging_dirname"],
            img_attrs=WORKFLOWS_CONFIG_INI.getboolean("general_config", "img_attrs"),
            reverse_slug=WORKFLOWS_CONFIG_INI.getboolean(
                "gallery_select", "reverse_slug"
            ),
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                "gallery_select", "x_posting_auto"
            ),
            x_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                "gallery_select", "x_posting_enabled"
            ),
            telegram_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                "gallery_select", "telegram_posting_auto"
            ),
            telegram_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                "gallery_select", "telegram_posting_enabled"
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def google_search_conf() -> GoogleSearch:
    """Factory function for dataclass ``GoogleSearch``"""
    try:
        return GoogleSearch(
            api_key=CLIENT_INFO_INI["google_custom_search"]["api_key"],
            cse_id_img=CLIENT_INFO_INI["google_custom_search"]["search_engine_id_img"],
            cse_id_web=CLIENT_INFO_INI["google_custom_search"]["search_engine_id_web"],
        )
    except ValueError:
        raise InvalidConfiguration


def embed_assist_conf() -> EmbedAssistConf:
    """Factory function for dataclass ``EmbedAssistConf``

    :return: ``EmbedAssistConf``
    """
    try:
        return EmbedAssistConf(
            wp_json_posts=WORKFLOWS_CONFIG_INI["general_config"]["wp_json_posts"],
            wp_cache_config=WORKFLOWS_CONFIG_INI["general_config"]["wp_cache_config"],
            pic_format=WORKFLOWS_CONFIG_INI["general_config"]["pic_format"],
            pic_fallback=WORKFLOWS_CONFIG_INI["general_config"]["fallback_pic_format"],
            imagick=WORKFLOWS_CONFIG_INI.getboolean(
                "general_config", "imagick_enabled"
            ),
            quality=WORKFLOWS_CONFIG_INI.getint("general_config", "conversion_quality"),
            sql_query=WORKFLOWS_CONFIG_INI["embed_assist"]["sql_query"],
            content_hint=WORKFLOWS_CONFIG_INI["embed_assist"]["db_content_hint"],
            partners=WORKFLOWS_CONFIG_INI["embed_assist"]["partners"],
            site_name=WORKFLOWS_CONFIG_INI["general_config"]["website_name"],
            domain_tld=WORKFLOWS_CONFIG_INI["general_config"]["domain_tld"],
            logging_dirname=WORKFLOWS_CONFIG_INI["general_config"]["logging_dirname"],
            img_attrs=WORKFLOWS_CONFIG_INI.getboolean("general_config", "img_attrs"),
            x_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                "embed_assist", "x_posting_auto"
            ),
            x_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                "embed_assist", "x_posting_enabled"
            ),
            telegram_posting_auto=WORKFLOWS_CONFIG_INI.getboolean(
                "embed_assist", "telegram_posting_auto"
            ),
            telegram_posting_enabled=WORKFLOWS_CONFIG_INI.getboolean(
                "embed_assist", "telegram_posting_enabled"
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def update_mcash_conf() -> UpdateMCash:
    """Factory function for dataclass ``UpdateMCash``

    :return: ``UpdateMCash``
    """
    return UpdateMCash(
        logging_dirname=WORKFLOWS_CONFIG_INI["general_config"]["logging_dirname"]
    )


def tasks_conf() -> TasksConf:
    """Factory function for dataclass ``TasksConf``

    :return: ``TasksConf``
    """
    return TasksConf(
        mcash_dump_url=TASKS_CONFIG_INI["dump_create_config"]["mcash_dump_url"],
        mcash_set_url=TASKS_CONFIG_INI["dump_create_config"]["mcash_set_url"],
    )
