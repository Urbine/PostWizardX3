"""
Module for handling PostWizard API authentication.

This module provides the PWSecretsController class which manages PostWizard API keys,
including storage, retrieval, and updates through a secrets database interface.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, Union

from core.controllers.interfaces.universal_controller import UniversalSecretController
from core.secrets.secret_repository import SecretsDBInterface
from core.models.secret_model import (
    SecretType,
    PostWizardAPILogin,
    PostWizardAPIToken,
)


class PWSecretsController(UniversalSecretController):
    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(
            secrets_db, [SecretType.PWAPI_PASSWORD, SecretType.PWAPI_TOKEN]
        )

    def store_secrets(self, secret_type: SecretType, user: str, secret: str) -> bool:
        """
        Store PostWizard secrets using the secrets database interface.

        :param secret_type: ``SecretType`` -> The type of secret to store.
        :param user: ``str`` -> The username for the PostWizard.
        :param secret: ``str`` -> The secret value to be stored
        :return: ``bool`` -> True if storage was successful, False otherwise
        """
        return self._universal_db.generic_store_secret(user, secret_type, secret, "")

    def update_secrets(
        self, secret_type: SecretType, user: str, new_secret: str
    ) -> bool:
        """
        Update PostWizard secrets using the secrets database interface.

        :param secret_type: ``SecretType`` -> The type of secret to update.
        :param user: ``str`` -> The username for the PostWizard.
        :param new_secret: ``str`` -> The new secret value to be stored
        :return: ``bool`` -> True if update was successful, False otherwise
        """
        return self._universal_db.generic_update_secret(user, secret_type, new_secret)

    def get_secrets(
        self, secret_type: SecretType
    ) -> Optional[Union[PostWizardAPILogin, PostWizardAPIToken]]:
        """
        Retrieve PostWizard secrets from the secrets database interface.

        :param secret_type: ``SecretType`` -> The type of secret to retrieve
        :return: ``Optional[Union[PostWizardAPILogin, PostWizardAPIToken]]``
        """
        secret_entry = self._universal_db.get_entries_by_secret_type(secret_type)
        if secret_entry is None:
            return None

        for slot in secret_entry:
            self._universal_db.load_data_row(slot)
            if secret_type == SecretType.PWAPI_PASSWORD:
                return PostWizardAPILogin(
                    api_user=self._universal_db.get_name(),
                    api_secret=self._universal_db.decrypt_secret(
                        self._universal_db.get_secret()
                    ),
                )
            else:
                return PostWizardAPIToken(
                    api_user=self._universal_db.get_name(),
                    access_token=self._universal_db.decrypt_secret(
                        self._universal_db.get_secret()
                    ),
                )

        return None

    def delete_secrets(self, secret_type: SecretType) -> bool:
        """
        Delete PostWizard secrets from the secrets database interface.

        :param secret_type: ``SecretType`` -> The type of secret to delete.
        :return: ``bool`` -> True if the secrets were successfully deleted, False otherwise
        """
        return self._universal_db.remove_secret_by_type(secret_type)
