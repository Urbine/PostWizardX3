import unittest
from core.models.secret_model import SecretType
from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestGetSecrets(unittest.TestCase):
    def test_get_secrets(self):
        username = "test_username"
        secret_type = SecretType.X_API_KEY
        xauth_list = XAuthController.get_secrets(secret_type, username)
        self.assertIsInstance(xauth_list, list)
        self.assertGreater(len(xauth_list), 0)
        found = False
        for xauth in xauth_list:
            if xauth.x_username == username:
                self.assertEqual(xauth.access_token, "test_access_token_updated")
                self.assertEqual(xauth.api_key, "test_api_key_updated")
                self.assertEqual(xauth.api_secret, "test_api_secret_updated")
                self.assertEqual(xauth.client_id, "test_client_id")
                self.assertEqual(xauth.client_secret, "test_client_secret_updated")
                self.assertEqual(xauth.refresh_token, "test_refresh_token_updated")
                self.assertEqual(xauth.uri_callback, "http://127.0.0.47:8888")
                self.assertEqual(xauth.x_passw, "super_secret_password")
                self.assertEqual(xauth.x_email, "test@example.com")
                found = True
        self.assertTrue(found, "Expected secret not found in the list.")


if __name__ == "__main__":
    unittest.main()
