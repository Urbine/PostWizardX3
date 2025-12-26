# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""Tests for update_secrets method of TelegramAuthController."""

import unittest

from core.controllers.auth.telegram_auth_controller import BotFatherAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
TAuthController = BotFatherAuthController(SECRETS_DB_INTERFACE)


class TestTelegramUpdateSecrets(unittest.TestCase):
    """Test cases for update_secrets method."""

    def test_update_secrets_success(self):
        """Test successful update of Telegram API credentials."""
        chat_id = "test_chat_id"
        botfather_token = "test_botfather_token"
        self.assertTrue(TAuthController.update_secrets(chat_id, botfather_token))


if __name__ == "__main__":
    unittest.main()
