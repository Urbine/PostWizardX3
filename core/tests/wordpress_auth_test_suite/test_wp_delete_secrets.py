# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""Tests for delete_secrets method of WPAuthController."""

import unittest

from core.controllers.auth.wp_auth_controller import WPAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
WPAuth = WPAuthController(SECRETS_DB_INTERFACE)


class TestWPDeleteSecrets(unittest.TestCase):
    """Test cases for delete_secrets method."""

    def test_delete_secrets(self):
        """Test delete_secrets method."""
        test_hostname = "example.com"
        self.assertTrue(WPAuth.delete_secrets(test_hostname))


if __name__ == "__main__":
    unittest.main()
