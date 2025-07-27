import unittest

from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestStoreCredentials(unittest.TestCase):
    def test_store_credentials(self):
        email_addr = "test@example.com"
        password = "super_secret_password"
        username = "test_username"
        self.assertTrue(
            XAuthController.store_credentials(username, email_addr, password)
        )


if __name__ == "__main__":
    unittest.main()
