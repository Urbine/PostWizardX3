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


def is_config_enabled(config_file_key):
    if config_file_key.title() == "True" or config_file_key.title() == "False":
        return eval(config_file_key.title())
    else:
        raise InvalidConfiguration(config_file_key)


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

    def __repr__(self):
        return "WPAuth()"


@dataclass(frozen=True)
class MongerCashAuth:
    username: str
    password: str

    def __repr__(self):
        return "MongerCash(username, password)"


@dataclass(frozen=True)
class YandexAuth:
    client_id: str
    client_secret: str

    def __repr__(self):
        return "YandexAuth(client_id, client_secret)"


@dataclass(frozen=True)
class ContentSelectConf:
    wp_json_posts: str
    wp_cache_config: str
    pic_format: str
    imagick: bool
    sql_query: str
    content_hint: str
    partners: str

    def __repr__(self):
        return "ContentSelectConf()"


@dataclass(frozen=True)
class GallerySelectConf:
    pic_format: str
    imagick: bool
    wp_json_photos: str
    wp_json_posts: str
    wp_cache_config: str
    sql_query: str
    content_hint: str
    partners: str

    def __repr__(self):
        return "GallerySelectConf()"


@dataclass(frozen=True)
class EmbedAssistConf:
    wp_json_posts: str
    wp_cache_config: str
    pic_format: str
    imagick: bool
    sql_query: str
    content_hint: str
    partners: str

    def __repr__(self):
        return "EmbedAssistConf()"


@dataclass(frozen=True)
class TasksConf:
    mcash_dump_url: str
    mcash_set_url: str

    def __repr__(self):
        return "TasksConf()"


@dataclass(frozen=True)
class XAuth:
    uri_callback: str
    x_username: str
    x_passw: str
    x_email: str
    client_id: str
    client_secret: str
    api_key: str
    api_secret: str

    def __repr__(self):
        return "XAuth(client_id, client_secret)"


# client_info.ini
client_info = parse_client_config("client_info", "core.config")


def wp_auth() -> WPAuth:
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
    return MongerCashAuth(
        username=client_info["MongerCash"]["username"],
        password=client_info["MongerCash"]["password"],
    )


def yandex_auth() -> YandexAuth:
    return YandexAuth(
        client_id=client_info["Yandex"]["client_id"],
        client_secret=client_info["Yandex"]["client_secret"],
    )


def x_auth():
    return XAuth(
        client_id=client_info["x_api"]["client_id"],
        client_secret=client_info["x_api"]["client_id"],
        api_key=client_info["x_api"]["api_key"],
        api_secret=client_info["x_api"]["api_secret"],
        uri_callback=client_info["x_api"]["uri_callback"],
        x_username=client_info["x_api"]["x_username"],
        x_passw=client_info["x_api"]["x_passw"],
        x_email=client_info["x_api"]["x_email"],
    )


# workflows_config.ini
workflows_config = parse_client_config("workflows_config", "core.config")


def content_select_conf() -> ContentSelectConf:
    return ContentSelectConf(
        wp_json_posts=workflows_config["content_select"]["wp_json_posts"],
        wp_cache_config=workflows_config["content_select"]["wp_cache_config"],
        pic_format=workflows_config["general_config"]["pic_format"],
        imagick=is_config_enabled(
            workflows_config["general_config"]["imagick_enabled"]
        ),
        sql_query=workflows_config["content_select"]["sql_query"],
        content_hint=workflows_config["content_select"]["db_content_hint"],
        partners=workflows_config["content_select"]["partners"],
    )


def gallery_select_conf() -> GallerySelectConf:
    return GallerySelectConf(
        pic_format=workflows_config["general_config"]["pic_format"],
        imagick=is_config_enabled(
            workflows_config["general_config"]["imagick_enabled"]
        ),
        wp_json_photos=workflows_config["gallery_select"]["wp_json_photos"],
        wp_json_posts=workflows_config["gallery_select"]["wp_json_posts"],
        wp_cache_config=workflows_config["gallery_select"]["wp_cache_config"],
        content_hint=workflows_config["gallery_select"]["db_content_hint"],
        sql_query=workflows_config["gallery_select"]["sql_query"],
        partners=workflows_config["gallery_select"]["partners"],
    )


def embed_assist_conf() -> EmbedAssistConf:
    return EmbedAssistConf(
        wp_json_posts=workflows_config["embed_assist"]["wp_json_posts"],
        wp_cache_config=workflows_config["embed_assist"]["wp_cache_config"],
        pic_format=workflows_config["general_config"]["pic_format"],
        imagick=is_config_enabled(
            workflows_config["general_config"]["imagick_enabled"]
        ),
        sql_query=workflows_config["embed_assist"]["sql_query"],
        content_hint=workflows_config["embed_assist"]["db_content_hint"],
        partners=workflows_config["embed_assist"]["partners"],
    )


# tasks_config.ini
tasks_config = parse_client_config("tasks_config", "core.config")


def tasks_conf() -> TasksConf:
    return TasksConf(
        mcash_dump_url=tasks_config["dump_create_config"]["mcash_dump_url"],
        mcash_set_url=tasks_config["dump_create_config"]["mcash_set_url"],
    )
