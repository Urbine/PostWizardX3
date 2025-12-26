# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

import unittest

# Local implementation to be tested
from core import is_parent_dir_required


class TestIsParentDirRequired(unittest.TestCase):
    def test_is_parent_dir_required(self):
        self.assertEqual(is_parent_dir_required(True, relpath=True), "..")
        self.assertEqual(is_parent_dir_required(False, relpath=True), ".")


if __name__ == "__main__":
    unittest.main()
