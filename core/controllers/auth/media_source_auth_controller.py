"""
Module for handling MediaSource API authentication.

This module provides the MediaSourceAuthController class which manages MediaSource API keys,
including storage, retrieval, and updates through a secrets database interface.
The controller acts as an intermediary between the application and the secrets
storage, providing a clean API for managing MediaSource authentication credentials.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

from typing import Optional, List

# Local implementations
from core.controllers.interfaces import UniversalSecretController
from core.models.secret_model import SecretType, MediaSourceAuth
from core.secrets.secret_repository import SecretsDBInterface


class MediaSourceAuthController(UniversalSecretController):
    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.MEDIA_SOURCE_PASSWORD])
        self.secrets_db = secrets_db

    def store_secrets(self, username: str, password: str) -> bool:
        """
        Store MediaSource secrets in the secrets database interface.

        :param username: ``str`` -> The username for the MediaSource account.
        :param password: ``str`` -> The password for the MediaSource account.
        :return: ``bool`` -> True if the secrets were successfully stored, False otherwise
        """
        store_secret = self._universal_db.generic_store_secret(
            username, SecretType.MEDIA_SOURCE_PASSWORD, password
        )
        if store_secret:
            return True

        return False

    def update_secrets(self, password: str, new_password: str) -> bool:
        """
        Update MediaSource secrets using the secrets database interface.

        :param password: ``str`` -> The current password for the MediaSource account.
        :param new_password: ``str`` -> The new password for the MediaSource account.
        :return: ``bool`` -> True if the secrets were successfully updated, False otherwise
        """
        username = self.get_secrets()[0].username
        update_secret = self._universal_db.generic_update_secret(
            username, SecretType.MEDIA_SOURCE_PASSWORD, new_password
        )

    def get_secrets(self) -> Optional[List[MediaSourceAuth]]:
        """
        Retrieve MediaSource secrets from the secrets database interface.

        :return: ``Optional[Union[MediaSourceAuth, List[MediaSourceAuth]]]``
        """
        secrets = self._universal_db.get_entries_by_secret_type(
            SecretType.MEDIA_SOURCE_PASSWORD,
        )
        media_source_instances = []
        if not secrets:
            return None
        else:
            for secret in secrets:
                self._universal_db.load_data_row(secret)
                media_source_instances.append(
                    MediaSourceAuth(
                        username=self._universal_db.get_name(),
                        password=self._universal_db.decrypt_secret(
                            self._universal_db.get_secret()
                        ),
                    )
                )
        return media_source_instances

    def delete_secrets(self) -> bool:
        """
        Delete MediaSource secrets from the secrets database interface.

        :return: ``bool`` -> True if the secrets were successfully deleted, False otherwise
        """
        delete_secret = self._universal_db.remove_secret_by_type(
            SecretType.MEDIA_SOURCE_PASSWORD
        )
        if delete_secret:
            return True

        return False
