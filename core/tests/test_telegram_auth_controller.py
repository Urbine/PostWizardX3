# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""Test suite for the Telegram Auth Controller."""

import os
import unittest

# Import the test modules from the test suite
from core.tests.telegram_auth_test_suite import TestTelegramGetSecrets
from core.tests.telegram_auth_test_suite import TestTelegramStoreSecrets
from core.tests.telegram_auth_test_suite import TestTelegramUpdateSecrets
from core.tests.telegram_auth_test_suite import TestTelegramDeleteSecrets
from core.secrets.secrets_factory import secrets_factory
from core.models.config_model import VAULT_DIR, LOCAL_TEST_VAULT_NAME

SECRETS_DB_INTERFACE = secrets_factory(in_memory=True)


def load_tests(loader, suite, pattern):
    """Load the test suite."""
    suite = unittest.TestSuite()

    # Add test cases from each test module
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramGetSecrets))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramStoreSecrets))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramUpdateSecrets))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramDeleteSecrets))
    return suite


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        # Clean up the test database
        os.remove(os.path.join(VAULT_DIR, f"{LOCAL_TEST_VAULT_NAME}.db"))
