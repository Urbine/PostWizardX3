"""Tests for update_secrets method of WPAuthController."""

import unittest

from core.controllers.auth.wp_auth_controller import WPAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
WPAuth = WPAuthController(SECRETS_DB_INTERFACE)


class TestWPUpdateSecrets(unittest.TestCase):
    """Test cases for update_secrets method."""

    def test_update_secrets_success(self):
        """Test successful update of WordPress application password."""
        test_hostname = "example.com"
        new_app_password = "new_test_wp_app_password"
        self.assertTrue(WPAuth.update_secrets(test_hostname, new_app_password))


if __name__ == "__main__":
    unittest.main()
