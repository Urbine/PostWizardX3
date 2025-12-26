# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Module for handling MongerCash API authentication.

This module provides the MongerCashAuthController class which manages MongerCash API keys,
including storage, retrieval, and updates through a secrets database interface.
The controller acts as an intermediary between the application and the secrets
storage, providing a clean API for managing MongerCash authentication credentials.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

from typing import Optional, List

# Local implementations
from core.controllers.interfaces import UniversalSecretController
from core.models.secret_model import SecretType, MongerCashAuth
from core.secrets.secret_repository import SecretsDBInterface


class MongerCashAuthController(UniversalSecretController):
    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.MONGERCASH_PASSWORD])
        self.secrets_db = secrets_db

    def store_secrets(self, username: str, password: str) -> bool:
        """
        Store MongerCash secrets in the secrets database interface.

        :param username: ``str`` -> The username for the MongerCash account.
        :param password: ``str`` -> The password for the MongerCash account.
        :return: ``bool`` -> True if the secrets were successfully stored, False otherwise
        """
        store_secret = self._universal_db.generic_store_secret(
            username, SecretType.MONGERCASH_PASSWORD, password
        )
        if store_secret:
            return True

        return False

    def update_secrets(self, password: str, new_password: str) -> bool:
        """
        Update MongerCash secrets using the secrets database interface.

        :param password: ``str`` -> The current password for the MongerCash account.
        :param new_password: ``str`` -> The new password for the MongerCash account.
        :return: ``bool`` -> True if the secrets were successfully updated, False otherwise
        """
        username = self.get_secrets()[0].username
        update_secret = self._universal_db.generic_update_secret(
            username, SecretType.MONGERCASH_PASSWORD, new_password
        )
        return update_secret

    def get_secrets(self) -> Optional[List[MongerCashAuth]]:
        """
        Retrieve MongerCash secrets from the secrets database interface.

        :return: ``Optional[Union[MongerCashAuth, List[MongerCashAuth]]]``
        """
        secrets = self._universal_db.get_entries_by_secret_type(
            SecretType.MONGERCASH_PASSWORD,
        )
        mcash_instances = []
        if not secrets:
            return None
        else:
            for secret in secrets:
                self._universal_db.load_data_row(secret)
                mcash_instances.append(
                    MongerCashAuth(
                        username=self._universal_db.get_name(),
                        password=self._universal_db.decrypt_secret(
                            self._universal_db.get_secret()
                        ),
                    )
                )
        return mcash_instances

    def delete_secrets(self) -> bool:
        """
        Delete MongerCash secrets from the secrets database interface.

        :return: ``bool`` -> True if the secrets were successfully deleted, False otherwise
        """
        delete_secret = self._universal_db.remove_secret_by_type(
            SecretType.MONGERCASH_PASSWORD
        )
        if delete_secret:
            return True

        return False
