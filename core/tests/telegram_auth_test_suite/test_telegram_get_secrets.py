"""Tests for get_secrets method of TelegramAuthController."""

import unittest

from core.models.secret_model import BotAuth
from core.controllers.auth.telegram_auth_controller import BotFatherAuthController
from core.secrets.secrets_factory import secrets_factory

SECRETS_DB_INTERFACE = secrets_factory(test_mode=True)
TAuthController = BotFatherAuthController(SECRETS_DB_INTERFACE)


class TestTelegramGetSecrets(unittest.TestCase):
    """Test cases for get_secrets method."""

    def test_get_secrets_no_entries(self):
        """Test get_secrets when no entries exist in the database."""
        t_secrets = TAuthController.get_secrets()
        if t_secrets is None:
            # if there are no entries in the database or there is no
            # database, the function should return None
            self.assertIsNone(t_secrets)
        else:
            for secret_instance in t_secrets:
                self.assertIsInstance(secret_instance, BotAuth)


if __name__ == "__main__":
    unittest.main()
