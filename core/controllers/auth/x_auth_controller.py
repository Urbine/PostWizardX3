# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Module for handling X (Twitter) API authentication.

This module provides the XAuthController class which manages X API credentials,
including API keys, tokens, and client secrets. It handles storage, retrieval,
and updates of authentication credentials through a secrets database interface.
The controller supports both OAuth 1.0a and OAuth 2.0 authentication flows for
X API access.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, List
import logging

from core.models.secret_model import (
    SecretType,
    XAuth,
    XAPISecrets,
    XClientSecrets,
    XTokens,
    XCredentials,
)
from core.secrets.secret_repository import SecretsDBInterface
from core.controllers.interfaces import UniversalSecretController


class XAuthController(UniversalSecretController):
    """
    Controller for handling X (Twitter) API authentication.

    This class manages X API credentials, including API keys, tokens, and client secrets.
    It handles storage, retrieval, and updates of authentication credentials through a secrets database interface.
    """

    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(
            secrets_db,
            [
                SecretType.X_API_KEY,
                SecretType.X_API_SECRET,
                SecretType.X_CLIENT_SECRET,
                SecretType.X_ACCESS_TOKEN,
                SecretType.X_REFRESH_TOKEN,
                SecretType.X_PASSWORD,
            ],
        )

    def store_secrets(
        self,
        secret_type: SecretType,
        username: str,
        secret_param_one: str,
        secret_param_two: str,
    ) -> bool:
        """
        Store X platform secrets using the secrets database interface.

        :param secret_type: ``SecretType`` -> The type of secret to store.
        :param username: ``str`` -> The username for the X platform.
        :param secret_param_one: ``str`` -> The first parameter for the secret.
        :param secret_param_two: ``str`` -> The second parameter for the secret.
        :return: ``bool`` -> True if storage was successful, False otherwise
        """
        match secret_type:
            case SecretType.X_API_KEY | SecretType.X_API_SECRET:
                return self.store_api_secrets(
                    username, secret_param_one, secret_param_two
                )
            case SecretType.X_CLIENT_SECRET:
                return self.store_client_id_secret(
                    username, secret_param_one, secret_param_two
                )
            case SecretType.X_ACCESS_TOKEN | SecretType.X_REFRESH_TOKEN:
                return self.store_token_secret(
                    username, secret_param_one, secret_param_two
                )
            case SecretType.X_PASSWORD:
                return self.store_credentials(
                    username, secret_param_one, secret_param_two
                )
            case _:
                logging.error(
                    f"Invalid secret provided: {secret_type} args: {username}, {secret_param_one}, {secret_param_two}."
                )
                return False

    def update_secrets(
        self, secret_type: SecretType, username: str, new_secret: str
    ) -> bool:
        """
        Update X platform secrets using the secrets database interface.

        :param secret_type: ``SecretType`` -> The type of secret to update.
        :param username: ``str`` -> The username for the X platform.
        :param new_secret: ``str`` -> The new secret value to be stored
        :return: ``bool`` -> True if update was successful, False otherwise
        """
        if secret_type not in self.supported_secret_types:
            return False
        return self._universal_db.generic_update_secret(
            username, secret_type, new_secret
        )

    def store_client_id_secret(
        self, username: str, client_id: str, client_secret: str
    ) -> bool:
        """
        Store X platform client ID and client secret using the secrets database interface.
        This function stores the client ID and client secret for the X platform.
        It uses the client ID for the secret entry to ensure uniqueness.
        The secrets are stored in the database with the type X_CLIENT_SECRET.

        :param username: ``str`` -> The username for the X platform.
        :param client_id: ``str`` -> The client ID for the X platform.
        :param client_secret: ``str`` -> The client secret for the X platform.
        :return: ``bool`` -> True if both the client ID and client secret were added successfully.
        """
        return self._universal_db.generic_store_secret(
            client_id, SecretType.X_CLIENT_SECRET, client_secret, metadata=username
        )

    def store_api_secrets(self, username: str, api_secret: str, api_key: str) -> bool:
        """
        Store X API secrets using the secrets database interface.
        This function stores the API secret and API key for the X platform.
        It uses the client ID for the secret entry to ensure uniqueness.
        The secrets are stored in the database with the type X_API_SECRET and X_API_KEY.

        :param username: ``str`` -> Random string that identifies the stored secret
        :param api_secret: ``str`` -> The API secret for the X platform.
        :param api_key: ``str`` -> The API key for the X platform.
        :return: ``bool`` -> ``True`` if both the API secret and API key were added successfully.
        """
        api_secret_stored = self._universal_db.generic_store_secret(
            username, SecretType.X_API_SECRET, api_secret
        )
        api_key_stored = self._universal_db.generic_store_secret(
            username, SecretType.X_API_KEY, api_key
        )
        return api_secret_stored and api_key_stored

    def store_credentials(self, username: str, email_addr: str, password: str) -> bool:
        """
        Store X platform credentials (email and password) using the secrets database interface.

        :param email_addr: ``str`` -> The email address associated with the X platform account.
        :param password: ``str`` -> The password for the X platform account.
        :param username: ``str`` -> The username for the X platform account.
        :return: ``bool`` -> True if the credentials were added successfully.
        """
        return self._universal_db.generic_store_secret(
            username, SecretType.X_PASSWORD, password, email_addr
        )

    def store_token_secret(
        self, username: str, access_token: str, refresh_token: str
    ) -> bool:
        """
        Store X platform access token and refresh token using the secrets database interface.

        :param username: ``str`` -> The username for the X platform account.
        :param access_token: ``str`` -> The access token for the X platform.
        :param refresh_token: ``str`` -> The refresh token for the X platform.
        :return: ``bool`` -> True if both the access token and refresh token were added successfully.
        """
        access_stored = self._universal_db.generic_store_secret(
            username,
            SecretType.X_ACCESS_TOKEN,
            access_token,
        )
        refresh_stored = self._universal_db.generic_store_secret(
            username,
            SecretType.X_REFRESH_TOKEN,
            refresh_token,
        )
        return access_stored and refresh_stored

    def get_secrets(self, secret_type: SecretType) -> Optional[List[XAuth]]:
        """
        Get X platform secrets from the secrets database interface.
        This function retrieves the X platform secrets for a given username.

        It fetches the API key, API secret, client ID, client secret, credentials (email and password),
        access token, and refresh token from the database.
        If returns a list of XAuth instances containing the retrieved secrets.

        :param secret_type: ``SecretType`` -> The type of secret to retrieve.
        :param username: ``str`` -> The username for which to retrieve the X platform secrets.
        :return: ``XAuth`` -> An instance of XAuth containing the retrieved secrets.
        """
        x_user_secrets = self._universal_db.retrieve_like_entry("secret_type", "x_%")
        decrypt = lambda secret: self._universal_db.decrypt_secret(secret)  # noqa: E731

        instances = []
        api_secrets = {}
        token_secrets = {}
        if x_user_secrets:
            for entry in x_user_secrets:
                self._universal_db.load_data_row(entry)
                match self._universal_db.get_secret_type():
                    case SecretType.X_API_KEY.value:
                        api_secrets["api_key"] = decrypt(
                            self._universal_db.get_secret()
                        )
                        api_secrets["username"] = self._universal_db.get_name()
                        api_secrets["secret_type"] = [
                            SecretType.X_API_KEY,
                            SecretType.X_API_SECRET,
                        ]
                    case SecretType.X_API_SECRET.value:
                        api_secrets["api_secret"] = decrypt(
                            self._universal_db.get_secret()
                        )
                        api_secrets["username"] = self._universal_db.get_name()
                        api_secrets["secret_type"] = [
                            SecretType.X_API_KEY,
                            SecretType.X_API_SECRET,
                        ]
                    case SecretType.X_CLIENT_SECRET.value:
                        instances.append(
                            XClientSecrets(
                                client_id=self._universal_db.get_name(),
                                client_secret=decrypt(self._universal_db.get_secret()),
                                username=self._universal_db.get_metadata(),
                                secret_type=SecretType.X_CLIENT_SECRET,
                            )
                        )
                    case SecretType.X_PASSWORD.value:
                        instances.append(
                            XCredentials(
                                x_passw=decrypt(self._universal_db.get_secret()),
                                username=self._universal_db.get_name(),
                                x_email=self._universal_db.get_metadata(),
                                secret_type=SecretType.X_PASSWORD,
                            )
                        )
                    case SecretType.X_ACCESS_TOKEN.value:
                        token_secrets["access_token"] = decrypt(
                            self._universal_db.get_secret()
                        )
                        token_secrets["username"] = self._universal_db.get_name()
                        token_secrets["secret_type"] = [
                            SecretType.X_ACCESS_TOKEN,
                            SecretType.X_REFRESH_TOKEN,
                        ]
                    case SecretType.X_REFRESH_TOKEN.value:
                        token_secrets["refresh_token"] = decrypt(
                            self._universal_db.get_secret()
                        )
                        token_secrets["username"] = self._universal_db.get_name()
                        token_secrets["secret_type"] = [
                            SecretType.X_ACCESS_TOKEN,
                            SecretType.X_REFRESH_TOKEN,
                        ]
                    case _:
                        continue
        else:
            logging.info("X platform secrets were not found")
            return None

        try:
            if len(api_secrets) == 2:
                instances.append(XAPISecrets(**api_secrets))
            elif len(token_secrets) == 2:
                instances.append(XTokens(**token_secrets))
        except TypeError as TypeErr:
            logging.debug(f"Raised {TypeErr!r} Reason: {TypeErr.__cause__}")
        pass

        return [
            instance for instance in instances if secret_type == instance.secret_type
        ]

    def delete_secrets(self, secret_type: SecretType) -> bool:
        """
        Delete X platform secrets using the secrets database interface.

        :param secret_type: ``SecretType`` -> The secret type for the X platform.
        :return: ``bool`` -> True if all the secrets were deleted successfully.
        """
        user_entries = self._universal_db.retrieve_like_entry("secret_type", "x_%")
        deleted = True
        for entry in user_entries:
            self._universal_db.load_data_row(entry)
            if (
                current_secret := self._universal_db.get_secret_type()
            ) == secret_type.value:
                deleted &= self._universal_db.remove_secret_by_type(current_secret)
        return deleted
