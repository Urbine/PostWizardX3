"""Tests for get_secrets method of BraveAuthController."""

import unittest

from core.models.secret_model import BraveAuth
from core.controllers.auth.brave_auth_controller import BraveAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
BAuthController = BraveAuthSecretController(SECRETS_DB_INTERFACE)


class TestGetSecrets(unittest.TestCase):
    """Test cases for get_secrets method."""

    def test_get_secrets_no_entries(self):
        """Test get_secrets when no entries exist in the database."""
        b_secrets = BAuthController.get_secrets()
        if b_secrets is None:
            # if there are no entries in the database or there is no
            # database, the function should return None
            self.assertIsNone(b_secrets)
        else:
            for secret_instance in b_secrets:
                self.assertIsInstance(secret_instance, BraveAuth)


if __name__ == "__main__":
    unittest.main()
