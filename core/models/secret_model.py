"""
Secret configuration model

This module defines the representation of all the secrets managed in the application.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class SecretType(Enum):
    """
    Enum class representing the different types of secrets stored in the database.
    """

    BRAVE_API_KEY = "brave_api_key"
    GOOGLE_API_KEY = "google_api_key"
    MONGERCASH_PASSWORD = "mongercash_password"
    YANDEX_CLIENT_SECRET = "yandex_client_secret"
    TELEGRAM_ACCESS_TOKEN = "telegram_access_token"
    PWAPI_PASSWORD = "pwapi_password"
    PWAPI_TOKEN = "pwapi_token"
    WP_APP_PASSWORD = "wp_app_password"
    X_CLIENT_SECRET = "x_client_secret"
    X_ACCESS_TOKEN = "x_access_token"
    X_API_KEY = "x_api_key"
    X_API_SECRET = "x_api_secret"
    X_REFRESH_TOKEN = "x_refresh_token"
    X_PASSWORD = "x_password"
    X_USERNAME = "x_username"


@dataclass(frozen=True, kw_only=True)
class WPSecrets:
    """
    Immutable dataclass responsible for holding WordPress secret structure,
    site information, configuration filenames, and behavioural constants.
    """

    app_password: Optional[str]
    hostname: Optional[str]
    user: Optional[str]

    def __repr__(self):
        return "WPAuth()"


@dataclass(frozen=True, kw_only=True)
class XAuth:
    """
    Immutable dataclass responsible for holding X platform secret structure.
    It acts as a common base class for different credentials and tokens.
    It stores the URI callback and the type of secret stored in the database.

    :param username: ``Optional[str]`` -> Optional username field for subclasses.
    :param uri_callback: ``str`` -> The URI callback for the X platform.
    :param secret_type: ``SecretType`` -> The type of secret stored in the database.
    """

    uri_callback = "http://127.0.0.47:8888"
    username: Optional[str]
    secret_type: SecretType | List[SecretType]

    def __repr__(self):
        return "XAuth()"


@dataclass(frozen=True, kw_only=True)
class XCredentials(XAuth):
    """
    Immutable dataclass responsible for holding X platform credentials.
    It stores the username, password, and email for the X platform.

    :param x_passw: ``str`` -> The password for the X platform.
    :param x_email: ``str`` -> The email address associated with the X platform account.
    """

    x_passw: str
    x_email: str

    def __repr__(self):
        return "XCredentials()"


@dataclass(frozen=True, kw_only=True)
class XAPISecrets(XAuth):
    """
    Immutable dataclass responsible for holding X platform API secrets.
    It stores the API key and API secret for the X platform.

    :param api_key: ``str`` -> The API key for the X platform.
    :param api_secret: ``str`` -> The API secret for the X platform.
    """

    api_key: str
    api_secret: str

    def __repr__(self):
        return "XAPISecrets()"


@dataclass(frozen=True, kw_only=True)
class XClientSecrets(XAuth):
    """
    Immutable dataclass responsible for holding X platform client secrets.
    It stores the client ID and client secret for the X platform.

    :param client_id: ``str`` -> The client ID for the X platform.
    :param client_secret: ``str`` -> The client secret for the X platform.
    """

    client_id: str
    client_secret: str

    def __repr__(self):
        return "XClientSecrets()"


@dataclass(frozen=True, kw_only=True)
class XTokens(XAuth):
    """
    Immutable dataclass responsible for holding X platform tokens.
    It stores the access token and refresh token for the X platform.

    :param access_token: ``str`` -> The access token for the X platform.
    :param refresh_token: ``str`` -> The refresh token for the X platform.
    """

    access_token: str
    refresh_token: str

    def __repr__(self):
        return "XTokens()"


@dataclass(frozen=True, kw_only=True)
class BotAuth:
    """
    Immutable class in charge of providing secrets for the BotFather
    service for Telegram Bot implementations.

    :param telegram_chat_id: ``str`` -> The Telegram chat ID for the BotFather service.
    :param token: ``str`` -> The token for the BotFather service.
    """

    telegram_chat_id: Optional[str]
    token: Optional[str]

    def __repr__(self):
        return "BotAuth()"


@dataclass(frozen=True, kw_only=True)
class BraveAuth:
    """
    Immutable data class for the Brave Search API and its modes.

    :param api_key_search: ``str`` -> The API key for the Brave Search API.
    """

    api_key_search: Optional[str]

    def __repr__(self):
        return "BraveAuth()"


@dataclass(frozen=True, kw_only=True)
class GoogleSearch:
    """
    Immutable data class for the Google Custom Search API.
    It holds the API key and the Custom Search Engine ID (CSE ID)

    :param api_key: ``str`` -> The API key for the Google Custom Search API.
    :param cse_id: ``str`` -> The Custom Search Engine ID (CSE ID) for the Google Custom Search API.
    """

    api_key: Optional[str]
    cse_id: Optional[str]

    def __repr__(self):
        return "GoogleSearch()"


@dataclass(frozen=True, kw_only=True)
class MongerCashAuth:
    """
    Immutable dataclass with the MongerCash secret structure.
    """

    username: str
    password: str

    def __repr__(self):
        return "MongerCash(username, password)"


@dataclass(frozen=True, kw_only=True)
class YandexAuth:
    """
    Immutable dataclass responsible for ordering Yandex API details.
    """

    client_id: str
    client_secret: str

    def __repr__(self):
        return "YandexAuth(client_id, client_secret)"


@dataclass(frozen=True, kw_only=True)
class PostWizardAPILogin:
    """
    Immutable dataclass responsible for holding PostWizard API secrets.
    It stores the API key and API secret for the PostWizard API.

    :param api_key: ``str`` -> The API key for the PostWizard API.
    :param api_secret: ``str`` -> The API secret for the PostWizard API.
    """

    api_user: str
    api_secret: str


@dataclass(frozen=True, kw_only=True)
class PostWizardAPIToken:
    """
    Immutable dataclass responsible for holding PostDirector API tokens.
    It stores the access token and refresh token for the PostDirector API.

    :param access_token: ``str`` -> The access token for the PostDirector API.
    :param refresh_token: ``str`` -> The refresh token for the PostDirector API.
    """

    api_user: str
    access_token: str
