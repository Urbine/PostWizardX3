# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

import unittest

from core.models.secret_model import GoogleSearch
from core.controllers.auth import GoogleAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
GAuthController = GoogleAuthSecretController(SECRETS_DB_INTERFACE)


class TestGetSecrets(unittest.TestCase):
    """Test cases for get_secrets method."""

    def test_get_secrets_no_entries(self):
        """Test get_secrets when no entries exist in the database."""
        g_secrets = GAuthController.get_secrets()
        if g_secrets is None:
            # if there are no entries in the database or there is no
            # database, the function should return None
            self.assertIsNone(g_secrets)
        else:
            for secret_instance in g_secrets:
                self.assertIsInstance(secret_instance, GoogleSearch)


if __name__ == "__main__":
    unittest.main()
