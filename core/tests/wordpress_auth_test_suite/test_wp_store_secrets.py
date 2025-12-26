# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""Tests for store_secrets method of WPAuthController."""

import unittest

from core.controllers.auth.wp_auth_controller import WPAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
WPAuth = WPAuthController(SECRETS_DB_INTERFACE)


class TestWPStoreSecrets(unittest.TestCase):
    """Test cases for store_secrets method."""

    def test_store_secrets_success(self):
        """Test successful storage of WordPress application password."""
        hostname = "example.com"
        app_password = "test_wp_app_password"
        username = "testuser"
        self.assertTrue(WPAuth.store_secrets(hostname, app_password, username))


if __name__ == "__main__":
    unittest.main()
