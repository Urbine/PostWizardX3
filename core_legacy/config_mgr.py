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
from typing import Optional

# Local implementations
from core.helpers import parse_client_config, singleton
from core.custom_exceptions import InvalidConfiguration, ClientInfoSecretsNotFound

CONFIG_PKG = "core.config"
CLIENT_INFO_INI = parse_client_config("client_info", CONFIG_PKG)
WORKFLOWS_CONFIG_INI = parse_client_config("workflows_config", CONFIG_PKG)

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
class ai_services:
    llm_provider: str
    llm_model_tag: str
    llm_serve_host: str
    llm_serve_port: str


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


def ai_services_conf() -> Optional[ai_services]:
    """Factory function for dataclass ``ai_services``"""
    try:
        return ai_services(
            llm_provider=WORKFLOWS_CONFIG_INI["general_config"]["llm_provider"],
            llm_model_tag=WORKFLOWS_CONFIG_INI["general_config"]["llm_model_tag"],
            llm_serve_host=WORKFLOWS_CONFIG_INI["general_config"]["llm_host"],
            llm_serve_port=WORKFLOWS_CONFIG_INI["general_config"]["llm_port"],
        )
    except ValueError:
        return None
