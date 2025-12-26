# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Module for handling WordPress API authentication.

This module provides the WPAuthController class which manages WordPress application
passwords, including storage, retrieval, and updates through a secrets database
interface. The controller handles authentication credentials for WordPress sites,
supporting multiple WordPress instances with different hostnames and users.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, List
from core.models.secret_model import WPSecrets, SecretType
from core.secrets.secret_repository import SecretsDBInterface
from core.controllers.interfaces import UniversalSecretController


class WPAuthController(UniversalSecretController):
    """
    Controller for handling WordPress authentication.

    This class provides methods to manage WordPress application passwords, including
    storage, retrieval, and updates through a secrets database interface.
    """

    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.WP_APP_PASSWORD])

    def get_secrets(self) -> Optional[List[WPSecrets]]:
        """
        Retrieve WordPress application passwords from the secrets database interface.

        :return: ``List[WPSecrets]`` -> A list of WPSecrets objects containing the retrieved application passwords.
        """
        entries = self._universal_db.get_entries_by_secret_type(
            SecretType.WP_APP_PASSWORD
        )
        if not entries:
            return None

        result = []
        for entry in entries:
            self._universal_db.load_data_row(entry)
            name = self._universal_db.get_name()
            app_password = self._universal_db.get_secret()
            metadata = self._universal_db.get_metadata()
            if app_password:
                result.append(
                    WPSecrets(
                        hostname=name,
                        app_password=self._universal_db.decrypt_secret(app_password),
                        user=metadata,
                    )
                )

        return result

    def store_secrets(self, hostname: str, app_password: str, username: str) -> bool:
        """
        Store WordPress application passwords in the secrets database interface.

        :param hostname: ``str`` -> The hostname of the WordPress site.
        :param app_password: ``str`` -> The application password for the WordPress site.
        :param username: ``str`` -> The username associated with the application password.
        :return: ``bool`` -> A boolean indicating whether the application password was successfully stored.
        """
        return self._universal_db.generic_store_secret(
            hostname, SecretType.WP_APP_PASSWORD, app_password, username
        )

    def update_secrets(self, hostname: str, new_app_password: str) -> bool:
        """
        Update the application password for a WordPress site in the secrets database interface.

        :param hostname: ``str`` -> The hostname of the WordPress site.
        :param new_app_password: ``str`` -> The new application password for the WordPress site.
        :return: ``bool`` -> A boolean indicating whether the application password was successfully updated.
        """
        return self._universal_db.generic_update_secret(
            hostname, SecretType.WP_APP_PASSWORD, new_app_password
        )

    def delete_secrets(self, hostname: str) -> bool:
        """
        Delete the application password for a WordPress site from the secrets database interface.

        :param hostname: ``str`` -> The hostname of the WordPress site.
        :return: ``bool`` -> A boolean indicating whether the application password was successfully deleted.
        """
        return self._universal_db.remove_secret_by_name(hostname)
