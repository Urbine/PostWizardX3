"""Tests for delete_secrets method of BraveAuthController."""

import unittest

from core.controllers.auth.brave_auth_controller import BraveAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
BAuthController = BraveAuthSecretController(SECRETS_DB_INTERFACE)


class TestDeleteSecrets(unittest.TestCase):
    """Test cases for delete_secrets method."""

    def test_delete_secrets(self):
        """Test delete_secrets method."""
        self.assertTrue(BAuthController.delete_secrets())


if __name__ == "__main__":
    unittest.main()
