"""
Module for handling Yandex API authentication.

This module provides the YandexAuthController class which manages Yandex API keys,
including storage, retrieval, and updates through a secrets database interface.
The controller acts as an intermediary between the application and the secrets
storage, providing a clean API for managing Yandex authentication credentials.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

from typing import List, Optional

# Local implementations
from core.controllers.interfaces.universal_controller import UniversalSecretController
from core.models.secret_model import SecretType, YandexAuth
from core.secrets.secret_repository import SecretsDBInterface


class YandexAuthController(UniversalSecretController):
    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.YANDEX_CLIENT_SECRET])

    def store_secrets(self, client_id: str, api_key: str) -> bool:
        """
        Store Yandex API keys in the secrets database.

        :param client_id: ``str`` -> A string representing the Yandex client ID to be stored.
        :param api_key: ``str`` -> A string representing the Yandex API key to be stored.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully stored.
        """
        store_secret = self._universal_db.generic_store_secret(
            client_id, SecretType.YANDEX_CLIENT_SECRET, api_key
        )
        if store_secret:
            return True

        return False

    def update_secrets(self, client_id: str, api_key: str) -> bool:
        """
        Update Yandex API keys in the secrets database.

        :param api_key: A string representing the Yandex API key to be updated.
        :return: ``bool`` -> A boolean indicating whether the API key was successfully updated.
        """
        update_secret = self._universal_db.generic_update_secret(
            client_id, SecretType.YANDEX_CLIENT_SECRET, api_key
        )
        if update_secret:
            return True

        return False

    def get_secrets(self) -> Optional[List[YandexAuth]]:
        """
        Retrieve Yandex API keys from the secrets database.

        :return: ``List[YandexAuth]`` -> A list of YandexAuth objects containing the retrieved API keys.
        """
        secret_by_type = self._universal_db.get_entries_by_secret_type(
            SecretType.YANDEX_CLIENT_SECRET
        )
        if not secret_by_type:
            return None
        yandex_instances = []
        for secret in secret_by_type:
            self._universal_db.load_data_row(secret)
            yandex_instances.append(
                YandexAuth(
                    client_id=self._universal_db.get_name(),
                    client_secret=self._universal_db.decrypt_secret(
                        self._universal_db.get_secret()
                    ),
                )
            )
        return yandex_instances

    def delete_secrets(self, *args) -> bool:
        """
        Delete Yandex API keys from the secrets database.

        :return: ``bool`` -> A boolean indicating whether the API key was successfully deleted.
        """
        delete_secret = self._universal_db.remove_secret_by_type(
            SecretType.YANDEX_CLIENT_SECRET
        )
        if delete_secret:
            return True

        return False
