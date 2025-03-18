"""
Config_mgr (Configuration Manager) module

Store and load the secrets necessary for interaction with other services.
Load important configuration variables that affect the project's behaviour.

This module was implemented in order to resolve issues reading directly
from the data structures that store those secrets and configs.

For example, several IndexError were raised due to relative references to files
in module operations.

Note that you can't assign values to instances of the dataclasses in this file (from other modules)
as they are immutable. The only way to modify any of the parameters in this file is by means of a config file.
This avoids side effects or unexpected behaviour.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from dataclasses import dataclass

from core.helpers import parse_client_config
from core.custom_exceptions import InvalidConfiguration


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class MongerCashAuth:
    """
    Immutable dataclass with the MongerCash secret structure.
    """

    username: str
    password: str

    def __repr__(self):
        return "MongerCash(username, password)"


@dataclass(frozen=True)
class YandexAuth:
    """
    Immutable dataclass responsible for ordering Yandex API details.
    """

    client_id: str
    client_secret: str

    def __repr__(self):
        return "YandexAuth(client_id, client_secret)"


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class TasksConf:
    """
    Immutable dataclass for configuration constants for the ``tasks`` package.
    """

    mcash_dump_url: str
    mcash_set_url: str

    def __repr__(self):
        return "TasksConf()"


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class BotAuth:
    """
    Immutable class in charge of providing secrets for the BotFather
    service for Telegram Bot implementations.
    """

    telegram_chat_id: str
    token: str

    def __repr__(self):
        return "BotAuth()"


@dataclass(frozen=True)
class UpdateMCash:
    """
    Immutable class with behavioral tweaks for
    """

    logging_dirname: str

    def __repr__(self):
        return "UpdateMCash()"


# client_info.ini
client_info = parse_client_config("client_info", "core.config")


def wp_auth() -> WPAuth:
    """Factory function for dataclass ``WPAuth``

    :return: ``WPAuth``
    """
    return WPAuth(
        user=client_info["WP_Admin"]["user"],
        app_password=client_info["WP_Admin"]["app_password"],
        author_admin=client_info["WP_Admin"]["author_admin"],
        hostname=client_info["WP_Admin"]["hostname"],
        api_base_url=client_info["WP_Admin"]["api_base_url"],
        full_base_url=client_info["WP_Admin"]["full_base_url"],
        default_status=client_info["WP_Admin"]["default_status"],
        wp_cache_file=client_info["WP_Admin"]["wp_cache_file"],
        wp_posts_file=client_info["WP_Admin"]["wp_posts_file"],
        wp_photos_file=client_info["WP_Admin"]["wp_photos_file"],
    )


def monger_cash_auth() -> MongerCashAuth:
    """Factory function for dataclass ``MongerCashAuth``

    :return: ``MongerCashAuth``
    """
    return MongerCashAuth(
        username=client_info["MongerCash"]["username"],
        password=client_info["MongerCash"]["password"],
    )


def yandex_auth() -> YandexAuth:
    """Factory function for dataclass ``YandexAuth``

    :return: ``YandexAuth``
    """
    return YandexAuth(
        client_id=client_info["Yandex"]["client_id"],
        client_secret=client_info["Yandex"]["client_secret"],
    )


def x_auth() -> XAuth:
    """Factory function for dataclass ``XAuth``

    :return: ``XAuth``
    """
    return XAuth(
        client_id=client_info["x_api"]["client_id"],
        client_secret=client_info["x_api"]["client_id"],
        api_key=client_info["x_api"]["api_key"],
        api_secret=client_info["x_api"]["api_secret"],
        uri_callback=client_info["x_api"]["uri_callback"],
        x_username=client_info["x_api"]["x_username"],
        x_passw=client_info["x_api"]["x_passw"],
        x_email=client_info["x_api"]["x_email"],
        access_token=client_info["x_api"]["access_token"],
        refresh_token=client_info["x_api"]["refresh_token"],
    )


def bot_father() -> BotAuth:
    """Factory function for dataclass ``BotAuth``.

    :return: ``BotAuth``
    """
    return BotAuth(
        telegram_chat_id=client_info["telegram_botfather"]["telegram_group_channel_id"],
        token=client_info["telegram_botfather"]["bot_token"],
    )


# workflows_config.ini
workflows_config = parse_client_config("workflows_config", "core.config")


def content_select_conf() -> ContentSelectConf:
    """Factory function for dataclass ``ContentSelectConf``

    :return: ``ContentSelectConf``
    """
    try:
        return ContentSelectConf(
            wp_json_posts=workflows_config["general_config"]["wp_json_posts"],
            wp_cache_config=workflows_config["general_config"]["wp_cache_config"],
            pic_format=workflows_config["general_config"]["pic_format"],
            pic_fallback=workflows_config["general_config"]["fallback_pic_format"],
            imagick=workflows_config.getboolean("general_config", "imagick_enabled"),
            quality=workflows_config.getint("general_config", "conversion_quality"),
            sql_query=workflows_config["content_select"]["sql_query"],
            content_hint=workflows_config["content_select"]["db_content_hint"],
            assets_conf=workflows_config["content_select"]["assets_conf"],
            partners=workflows_config["content_select"]["partners"],
            site_name=workflows_config["general_config"]["website_name"],
            domain_tld=workflows_config["general_config"]["domain_tld"],
            logging_dirname=workflows_config["general_config"]["logging_dirname"],
            img_attrs=workflows_config.getboolean("general_config", "img_attrs"),
            x_posting_auto=workflows_config.getboolean(
                "content_select", "x_posting_auto"
            ),
            x_posting_enabled=workflows_config.getboolean(
                "content_select", "x_posting_enabled"
            ),
            telegram_posting_auto=workflows_config.getboolean(
                "content_select", "telegram_posting_auto"
            ),
            telegram_posting_enabled=workflows_config.getboolean(
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
            pic_format=workflows_config["general_config"]["pic_format"],
            pic_fallback=workflows_config["general_config"]["fallback_pic_format"],
            imagick=workflows_config.getboolean("general_config", "imagick_enabled"),
            quality=workflows_config.getint("general_config", "conversion_quality"),
            wp_json_photos=workflows_config["gallery_select"]["wp_json_photos"],
            wp_json_posts=workflows_config["general_config"]["wp_json_posts"],
            wp_cache_config=workflows_config["general_config"]["wp_cache_config"],
            content_hint=workflows_config["gallery_select"]["db_content_hint"],
            sql_query=workflows_config["gallery_select"]["sql_query"],
            partners=workflows_config["gallery_select"]["partners"],
            site_name=workflows_config["general_config"]["website_name"],
            domain_tld=workflows_config["general_config"]["domain_tld"],
            logging_dirname=workflows_config["general_config"]["logging_dirname"],
            img_attrs=workflows_config.getboolean("general_config", "img_attrs"),
            reverse_slug=workflows_config.getboolean("gallery_select", "reverse_slug"),
            x_posting_auto=workflows_config.getboolean(
                "gallery_select", "x_posting_auto"
            ),
            x_posting_enabled=workflows_config.getboolean(
                "gallery_select", "x_posting_enabled"
            ),
            telegram_posting_auto=workflows_config.getboolean(
                "gallery_select", "telegram_posting_auto"
            ),
            telegram_posting_enabled=workflows_config.getboolean(
                "gallery_select", "telegram_posting_enabled"
            ),
        )
    except ValueError:
        raise InvalidConfiguration


def embed_assist_conf() -> EmbedAssistConf:
    """Factory function for dataclass ``EmbedAssistConf``

    :return: ``EmbedAssistConf``
    """
    try:
        return EmbedAssistConf(
            wp_json_posts=workflows_config["general_config"]["wp_json_posts"],
            wp_cache_config=workflows_config["general_config"]["wp_cache_config"],
            pic_format=workflows_config["general_config"]["pic_format"],
            pic_fallback=workflows_config["general_config"]["fallback_pic_format"],
            imagick=workflows_config.getboolean("general_config", "imagick_enabled"),
            quality=workflows_config.getint("general_config", "conversion_quality"),
            sql_query=workflows_config["embed_assist"]["sql_query"],
            content_hint=workflows_config["embed_assist"]["db_content_hint"],
            partners=workflows_config["embed_assist"]["partners"],
            site_name=workflows_config["general_config"]["website_name"],
            domain_tld=workflows_config["general_config"]["domain_tld"],
            logging_dirname=workflows_config["general_config"]["logging_dirname"],
            img_attrs=workflows_config.getboolean("general_config", "img_attrs"),
            x_posting_auto=workflows_config.getboolean(
                "embed_assist", "x_posting_auto"
            ),
            x_posting_enabled=workflows_config.getboolean(
                "embed_assist", "x_posting_enabled"
            ),
            telegram_posting_auto=workflows_config.getboolean(
                "embed_assist", "telegram_posting_auto"
            ),
            telegram_posting_enabled=workflows_config.getboolean(
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
        logging_dirname=workflows_config["general_config"]["logging_dirname"]
    )


# tasks_config.ini
tasks_config = parse_client_config("tasks_config", "core.config")


def tasks_conf() -> TasksConf:
    """Factory function for dataclass ``TasksConf``

    :return: ``TasksConf``
    """
    return TasksConf(
        mcash_dump_url=tasks_config["dump_create_config"]["mcash_dump_url"],
        mcash_set_url=tasks_config["dump_create_config"]["mcash_set_url"],
    )
