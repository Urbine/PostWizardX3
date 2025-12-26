# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Module for handling Google API authentication.

This module provides the GoogleAuthController class which manages Google API keys
and Custom Search Engine IDs, including storage, retrieval, and updates through
a secrets database interface. The controller facilitates authentication for
Google Custom Search API operations, managing credentials securely.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, List
from core.models.secret_model import GoogleSearch, SecretType
from core.secrets.secret_repository import SecretsDBInterface
from core.controllers.interfaces import UniversalSecretController


class GoogleAuthSecretController(UniversalSecretController):
    """
    Controller for Google API authentication.

    Manages Google API keys and Custom Search Engine IDs, including storage,
    retrieval, and updates through a secrets database interface. Facilitates
    authentication for Google Custom Search API operations, managing credentials
    securely.
    """

    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(secrets_db, [SecretType.GOOGLE_API_KEY])

    def get_secrets(self) -> Optional[List[GoogleSearch]]:
        """
        Retrieve Google API keys and Custom Search Engine IDs from the secrets database.

        :return: ``List[GoogleSearch]`` -> A list of GoogleSearch objects containing the retrieved API keys and CSE IDs.
        """
        api_entries = self._universal_db.get_entries_by_secret_type(
            SecretType.GOOGLE_API_KEY
        )
        if not api_entries:
            return None

        result = []
        for entry in api_entries:
            self._universal_db.load_data_row(entry)
            cse_id = self._universal_db.get_name()
            api_key = self._universal_db.get_secret()
            if api_key:
                result.append(
                    GoogleSearch(
                        api_key=self._universal_db.decrypt_secret(api_key),
                        cse_id=cse_id,
                    )
                )

        return result

    def store_secrets(self, google_api_key: str, google_cse_id: str) -> bool:
        """
        Store Google API keys and Custom Search Engine IDs in the secrets database.

        :param google_api_key: ``str`` -> A string representing the Google API key to be stored.
        :param google_cse_id: ``str`` -> A string representing the Custom Search Engine ID to be stored.
        :return: ``bool`` -> A boolean indicating whether the API key and CSE ID were successfully stored.
        """
        return self._universal_db.generic_store_secret(
            google_cse_id, SecretType.GOOGLE_API_KEY, google_api_key
        )

    def update_secrets(self, cse_id: str, new_api_key: str) -> bool:
        """ "
        Update Google API keys and Custom Search Engine IDs in the secrets database.

        :param new_api_key: ``str`` -> A string representing the new Google API key to be updated.
        :param cse_id: ``str`` -> A string representing the Custom Search Engine ID to be updated.
        :return: ``bool`` -> A boolean indicating whether the API key and CSE ID were successfully updated.
        """
        return self._universal_db.generic_update_secret(
            cse_id, SecretType.GOOGLE_API_KEY, new_api_key
        )

    def delete_secrets(self) -> bool:
        """
        Delete Google API keys and Custom Search Engine IDs from the secrets database.

        :return: ``bool`` -> A boolean indicating whether the API key and CSE ID were successfully deleted.
        """
        return self._universal_db.remove_secret_by_type(SecretType.GOOGLE_API_KEY)
