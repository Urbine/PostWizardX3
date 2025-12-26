# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""Tests for delete_secrets method of TelegramAuthController."""

import unittest

from core.controllers.auth.telegram_auth_controller import BotFatherAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
TAuthController = BotFatherAuthController(SECRETS_DB_INTERFACE)


class TestTelegramDeleteSecrets(unittest.TestCase):
    """Test cases for delete_secrets method."""

    def test_delete_secrets(self):
        """Test delete_secrets method."""
        chat_id = "test_chat_id"
        self.assertTrue(TAuthController.delete_secrets(chat_id))


if __name__ == "__main__":
    unittest.main()
