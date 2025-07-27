import unittest
from core.models.secret_model import SecretType
from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestDeleteSecrets(unittest.TestCase):
    def test_delete_secrets(self):
        # Use a valid SecretType for deletion
        secret_type = XAuthController.supported_secret_types
        for secret_type in secret_type:
            self.assertTrue(XAuthController.delete_secrets(secret_type))
        self.assertIsNone(XAuthController.get_secrets(secret_type))


if __name__ == "__main__":
    unittest.main()
