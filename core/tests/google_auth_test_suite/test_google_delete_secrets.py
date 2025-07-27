import unittest

from core.controllers.auth import GoogleAuthSecretController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
GAuthController = GoogleAuthSecretController(SECRETS_DB_INTERFACE)


class TestDeleteSecrets(unittest.TestCase):
    """Test cases for get_secrets method."""

    def test_delete_secrets(self):
        """Test delete_secrets method."""
        self.assertTrue(GAuthController.delete_secrets())


if __name__ == "__main__":
    unittest.main()
