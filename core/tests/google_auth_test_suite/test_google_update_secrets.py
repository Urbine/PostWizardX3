"""Tests for update_secrets method of GoogleAuthController."""

import unittest


from core.controllers.auth import GoogleAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
GAuthController = GoogleAuthSecretController(SECRETS_DB_INTERFACE)


class TestUpdateSecrets(unittest.TestCase):
    """Test cases for update_secrets method."""

    def test_update_secrets_success(self):
        """Test successful update of secrets."""
        new_api_key = "new_test_api_key"
        cse_id = "test_cse_id"
        self.assertTrue(GAuthController.update_secrets(cse_id, new_api_key))


if __name__ == "__main__":
    unittest.main()
