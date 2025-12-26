# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Module for handling Telegram BotFather API authentication.

This module provides the BotFatherAuthController class which manages Telegram BotFather API keys,
including storage, retrieval, and updates through a secrets database interface.
The controller acts as an intermediary between the application and the secrets
storage, providing a clean API for managing Telegram BotFather authentication credentials.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, List
from core.models.secret_model import BotAuth, SecretType
from core.secrets.secret_repository import SecretsDBInterface
from core.controllers.interfaces import UniversalSecretController


class BotFatherAuthController(UniversalSecretController):
    """
    Controller for handling BotFather authentication.

    This class provides methods for storing, retrieving, and updating
    BotFather authentication credentials through a secrets database interface.
    """

    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.TELEGRAM_ACCESS_TOKEN])

    def get_secrets(self) -> Optional[List[BotAuth]]:
        """
        Retrieve BotFather API keys from the secrets database.

        :return: ``List[BotAuth]`` -> A list of BotAuth objects containing the retrieved API keys.
        """
        secrets = self._universal_db.get_entries_by_secret_type(
            SecretType.TELEGRAM_ACCESS_TOKEN,
        )
        if not secrets:
            return None

        result = []
        for entry in secrets:
            chat_id = entry[1]
            token = self._universal_db.decrypt_secret(entry[2])
            if token:
                result.append(BotAuth(telegram_chat_id=chat_id, token=token))
        return result

    def store_secrets(self, telegram_chat_id: str, telegram_token: str) -> bool:
        """
        Store BotFather API keys in the secrets database.

        :param telegram_chat_id: ``str`` -> A string representing the Telegram chat ID to be stored.
        :param telegram_token: ``str`` -> A string representing the BotFather API key to be stored.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully stored.
        """
        return self._universal_db.generic_store_secret(
            telegram_chat_id,
            SecretType.TELEGRAM_ACCESS_TOKEN,
            telegram_token,
        )

    def update_secrets(self, chat_id: str, new_token: str) -> bool:
        """
        Update BotFather API keys in the secrets database.

        :param chat_id: ``str`` -> A string representing the Telegram chat ID to be updated.
        :param new_token: ``str`` -> A string representing the new BotFather API key to be updated.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully updated.
        """
        return self._universal_db.generic_update_secret(
            chat_id, SecretType.TELEGRAM_ACCESS_TOKEN, new_token
        )

    def delete_secrets(self, chat_id: str) -> bool:
        """
        Delete BotFather API keys from the secrets database.

        :param chat_id: ``str`` -> A string representing the Telegram chat ID to be deleted.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully deleted.
        """
        return self._universal_db.remove_secret_by_name(chat_id)
