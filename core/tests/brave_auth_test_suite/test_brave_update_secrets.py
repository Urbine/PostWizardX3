"""Tests for update_secrets method of BraveAuthController."""

import unittest

from core.controllers.auth.brave_auth_controller import BraveAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
BAuthController = BraveAuthSecretController(SECRETS_DB_INTERFACE)


class TestUpdateSecrets(unittest.TestCase):
    """Test cases for update_secrets method."""

    def test_update_secrets_success(self):
        """Test successful update of Brave API key."""
        new_api_key = "new_test_brave_api_key"
        self.assertTrue(BAuthController.update_secrets(new_api_key))


if __name__ == "__main__":
    unittest.main()
