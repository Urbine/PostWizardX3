# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""Tests for store_secrets method of TelegramAuthController."""

import unittest

from core.controllers.auth import BotFatherAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
TAuthController = BotFatherAuthController(SECRETS_DB_INTERFACE)


class TestTelegramStoreSecrets(unittest.TestCase):
    """Test cases for store_secrets method."""

    def test_store_secrets_success(self):
        """Test successful storage of Telegram API credentials."""
        chat_id = "test_chat_id"
        botfather_token = "test_botfather_token"
        self.assertTrue(TAuthController.store_secrets(chat_id, botfather_token))


if __name__ == "__main__":
    unittest.main()
