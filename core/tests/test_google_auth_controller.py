"""Test suite for the Google Auth Controller."""

import os
import unittest

# Import the test modules from the test suite
from core.tests.google_auth_test_suite import TestGetSecrets
from core.tests.google_auth_test_suite import TestStoreSecrets
from core.tests.google_auth_test_suite import TestUpdateSecrets
from core.secrets.secrets_factory import secrets_factory
from core.secrets import VAULT_DIR, LOCAL_TEST_VAULT_NAME

SECRETS_DB_INTERFACE = secrets_factory(in_memory=True)


def load_tests(loader, suite, pattern):
    """Load the test suite."""
    suite = unittest.TestSuite()

    # Add test cases from each test module
    suite.addTests(loader.loadTestsFromTestCase(TestGetSecrets))
    suite.addTests(loader.loadTestsFromTestCase(TestStoreSecrets))
    suite.addTests(loader.loadTestsFromTestCase(TestUpdateSecrets))
    return suite


if __name__ == "__main__":
    unittest.main()
