# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Test Suite for core.clean_filename Function

This module contains test cases for the clean_filename function, which handles
file naming conventions and extension management. The test suite verifies various
edge cases and expected behaviors for filename formatting:

1. Preserving existing properly formatted filenames
2. Adding extensions to filenames without them
3. Handling dot prefixes in extensions
4. Working with package-style naming conventions
5. Ensuring consistent extension format regardless of input style

These tests ensure the function correctly maintains or appends file extensions
based on the provided parameters.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

import unittest

# Local implementation to be tested
from core.utils.strings import clean_filename


class TestCleanFilename(unittest.TestCase):
    def test_clean_filename(self):
        # Possible cases
        self.assertEqual(clean_filename("sample.json", "json"), "sample.json")
        self.assertEqual(clean_filename("sample", "json"), "sample.json")
        self.assertEqual(clean_filename("sample", ".json"), "sample.json")
        self.assertEqual(clean_filename("wp_posts.json", ".json"), "wp_posts.json")
        self.assertEqual(
            clean_filename("com.thispackage.anything", ""), "com.thispackage.anything"
        )
        self.assertEqual(
            clean_filename("com.thispackage.anything", "java"),
            "com.thispackage.anything.java",
        )
        self.assertEqual(
            clean_filename("com.thispackage.anything", ".java"),
            "com.thispackage.anything.java",
        )


if __name__ == "__main__":
    unittest.main()
