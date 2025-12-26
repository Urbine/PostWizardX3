# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

import unittest

from core.controllers.auth import XAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
XAuthController = XAuthController(SECRETS_DB_INTERFACE)


class TestStoreClientIDSecret(unittest.TestCase):
    def test_store_client_id_secret(self):
        username = "test_username"
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        self.assertTrue(
            XAuthController.store_client_id_secret(username, client_id, client_secret)
        )


if __name__ == "__main__":
    unittest.main()
