# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Module for handling Brave API authentication.

This module provides the BraveAuthController class which manages Brave API keys,
including storage, retrieval, and updates through a secrets database interface.
The controller acts as an intermediary between the application and the secrets
storage, providing a clean API for managing Brave authentication credentials.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, List
from core.models.secret_model import BraveAuth, SecretType
from core.secrets.secret_repository import SecretsDBInterface
from core.controllers.interfaces import UniversalSecretController


class BraveAuthSecretController(UniversalSecretController):
    """
    Controller for handling Brave API authentication.

    This class provides methods to manage Brave API keys, including storage,
    retrieval, and updates through a secrets database interface.
    """

    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.BRAVE_API_KEY])

    def get_secrets(self) -> Optional[List[BraveAuth]]:
        """
        Retrieve Brave API keys from the secrets database.

        :return: ``List[BraveAuth]`` -> A list of BraveAuth objects containing the retrieved API keys.
        """
        entries = self._universal_db.get_entries_by_secret_type(
            SecretType.BRAVE_API_KEY
        )
        if not entries:
            return None

        result = []
        for entry in entries:
            self._universal_db.load_data_row(entry)
            api_key = self._universal_db.get_secret()
            if api_key:
                result.append(
                    BraveAuth(api_key_search=self._universal_db.decrypt_secret(api_key))
                )

        return result

    def store_secrets(self, api_key: str) -> bool:
        """
        Store Brave API keys in the secrets database.

        :param api_key: ``str`` -> A string representing the Brave API key to be stored.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully stored.
        """
        return self._universal_db.generic_store_secret(
            "BraveAPI", SecretType.BRAVE_API_KEY, api_key
        )

    def update_secrets(self, api_key: str) -> bool:
        """
        Update Brave API keys in the secrets database.

        :param api_key: A string representing the Brave API key to be updated.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully updated.
        """
        return self._universal_db.generic_update_secret(
            "BraveAPI", SecretType.BRAVE_API_KEY, api_key
        )

    def delete_secrets(self) -> bool:
        """
        Delete Brave API keys from the secrets database.

        :return: ``bool`` -> A boolean indicating whether the API key was successfully deleted.
        """
        return self._universal_db.remove_secret_by_type(SecretType.BRAVE_API_KEY)
