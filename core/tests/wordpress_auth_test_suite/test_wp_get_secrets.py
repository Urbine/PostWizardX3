"""Tests for get_secrets method of WPAuthController."""

import unittest

from core.models.secret_model import WPSecrets
from core.controllers.auth.wp_auth_controller import WPAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
WPAuth = WPAuthController(SECRETS_DB_INTERFACE)


class TestWPGetSecrets(unittest.TestCase):
    """Test cases for get_secrets method."""

    def test_get_secrets_no_entries(self):
        """Test get_secrets when no entries exist in the database."""
        wp_secrets = WPAuth.get_secrets()
        if wp_secrets is None:
            # if there are no entries in the database or there is no
            # database, the function should return None
            self.assertIsNone(wp_secrets)
        else:
            for secret_instance in wp_secrets:
                self.assertIsInstance(secret_instance, WPSecrets)


if __name__ == "__main__":
    unittest.main()
