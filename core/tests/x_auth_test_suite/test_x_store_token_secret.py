import unittest

from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestStoreTokenSecret(unittest.TestCase):
    def test_store_token_secret(self):
        username = "test_username"
        access_token = "test_access_token"
        refresh_token = "test_refresh_token"
        self.assertTrue(
            XAuthController.store_token_secret(username, access_token, refresh_token)
        )


if __name__ == "__main__":
    unittest.main()
