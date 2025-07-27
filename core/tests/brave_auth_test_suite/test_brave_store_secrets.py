"""Tests for store_secrets method of BraveAuthController."""

import unittest

from core.controllers.auth.brave_auth_controller import BraveAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
BAuthController = BraveAuthSecretController(SECRETS_DB_INTERFACE)


class TestStoreSecrets(unittest.TestCase):
    """Test cases for store_secrets method."""

    def test_store_secrets_success(self):
        """Test successful storage of Brave API key."""
        self.assertTrue(BAuthController.store_secrets("test_brave_api_key"))


if __name__ == "__main__":
    unittest.main()
