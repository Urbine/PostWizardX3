"""Test suite for the XAuthController class."""

import os
import unittest

from core.secrets import VAULT_DIR, LOCAL_TEST_VAULT_NAME
from core.tests.x_auth_test_suite import (
    TestStoreClientIDSecret,
    TestStoreAPISecrets,
    TestStoreCredentials,
    TestStoreTokenSecret,
    TestUpdateSecrets,
    TestDeleteSecrets,
)

if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(TestStoreClientIDSecret)
    )
    test_suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(TestStoreTokenSecret)
    )
    test_suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(TestStoreCredentials)
    )
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestStoreAPISecrets))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUpdateSecrets))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDeleteSecrets))
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
