import unittest
from core.models.secret_model import (
    SecretType,
    XAPISecrets,
    XClientSecrets,
    XTokens,
    XCredentials,
)
from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestUpdateSecrets(unittest.TestCase):
    def test_update_secrets(self):
        username = "test_username"
        secret_type = SecretType.X_API_SECRET
        new_api_secret = "test_new_api_secret_updated"
        self.assertTrue(
            XAuthController.update_secrets(
                secret_type,
                username,
                new_api_secret,
            )
        )


class TestGetSecretsUpdated(unittest.TestCase):
    def test_get_secrets_updated(self):
        username = "test_username"
        secret_type = SecretType.X_API_KEY
        xauth_list = XAuthController.get_secrets(secret_type, username)
        self.assertIsInstance(xauth_list, list)
        self.assertGreater(len(xauth_list), 0)
        found_api = found_client = found_tokens = found_credentials = False
        for xauth in xauth_list:
            if isinstance(xauth, XAPISecrets):
                self.assertEqual(xauth.api_key, "test_api_key_updated")
                self.assertEqual(xauth.api_secret, "test_api_secret_updated")
                found_api = True
            elif isinstance(xauth, XClientSecrets):
                self.assertEqual(xauth.client_id, "test_client_id")
                self.assertEqual(xauth.client_secret, "test_client_secret_updated")
                found_client = True
            elif isinstance(xauth, XTokens):
                self.assertEqual(xauth.access_token, "test_access_token_updated")
                self.assertEqual(xauth.refresh_token, "test_refresh_token_updated")
                found_tokens = True
            elif isinstance(xauth, XCredentials):
                self.assertEqual(xauth.x_passw, "super_secret_password")
                self.assertEqual(xauth.x_email, "test@example.com")
                found_credentials = True
        self.assertTrue(found_api, "Expected XAPISecrets not found in the list.")
        self.assertTrue(found_client, "Expected XClientSecrets not found in the list.")
        self.assertTrue(found_tokens, "Expected XTokens not found in the list.")
        self.assertTrue(
            found_credentials, "Expected XCredentials not found in the list."
        )


if __name__ == "__main__":
    unittest.main()
