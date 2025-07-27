"""Tests for store_secrets method of GoogleAuthController."""

import unittest

from core.controllers.auth import GoogleAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
GAuthController = GoogleAuthSecretController(SECRETS_DB_INTERFACE)


class TestStoreSecrets(unittest.TestCase):
    """Test cases for store_secrets method."""

    def test_store_secrets_success(self):
        """Test successful storage of secrets."""
        self.assertTrue(GAuthController.store_secrets("test_api_key", "test_cse_id"))


if __name__ == "__main__":
    unittest.main()
