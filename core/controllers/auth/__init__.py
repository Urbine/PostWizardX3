"""
Subpackage for authentication controllers.

The controllers in this subpackage manage authentication credentials for different
services. Each controller provides methods to store, retrieve, and update
authentication information in a secrets database interface.

The controllers are:

- `BraveAuthController`: Manages Brave API keys.
- `GoogleAuthController`: Manages Google API keys and Custom Search Engine (CSE) IDs.
- `BotFatherAuthController`: Manages Telegram BotFather API keys.
- `WPAuthController`: Manages WordPress application passwords.
- `XAuthController`: Manages X (Twitter) API credentials.

"""

from .brave_auth_controller import BraveAuthSecretController
from .google_auth_controller import GoogleAuthSecretController
from .telegram_auth_controller import BotFatherAuthController
from .wp_auth_controller import WPAuthController
from .x_auth_controller import XAuthController
from .mongercash_auth_controller import MongerCashAuthController
from .yandex_auth_controller import YandexAuthController

__all__ = [
    "BraveAuthSecretController",
    "GoogleAuthSecretController",
    "BotFatherAuthController",
    "WPAuthController",
    "XAuthController",
    "MongerCashAuthController",
    "YandexAuthController",
]
