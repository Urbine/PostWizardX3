# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

import unittest
from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestStoreAPISecrets(unittest.TestCase):
    def test_store_api_secrets(self):
        username = "test_username"
        api_secret = "test_api_secret"
        api_key = "test_api_key"
        self.assertTrue(
            XAuthController.store_api_secrets(username, api_secret, api_key)
        )


if __name__ == "__main__":
    unittest.main()
