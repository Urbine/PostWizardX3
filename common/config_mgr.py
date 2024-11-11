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

from .helpers import parse_client_config


@dataclass()
class WPAuth:
    user: str
    app_password: str
    author: str


@dataclass()
class MongerCashAuth:
    username: str
    password: str


@dataclass()
class YandexAuth:
    client_id: str
    client_secret: str


# client_info.ini
client_info = parse_client_config("./config/client_info")

WP_CLIENT_INFO = WPAuth(
    user=client_info["WP_Admin"]["user"],
    app_password=client_info["WP_Admin"]["app_password"],
    author=client_info["WP_Admin"]["author"],
)

MONGER_CASH_INFO = MongerCashAuth(
    username=client_info["MongerCash"]["username"],
    password=client_info["MongerCash"]["password"],
)


YANDEX_INFO = YandexAuth(
    client_id=client_info["Yandex"]["client_id"],
    client_secret=client_info["Yandex"]["client_secret"],
)
