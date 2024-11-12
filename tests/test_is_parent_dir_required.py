import unittest

# Local implementation to be tested
from common import is_parent_dir_required


class TestIsParentDirRequired(unittest.TestCase):
    def test_is_parent_dir_required(self):
        self.assertEqual(is_parent_dir_required(True), '../')
        self.assertEqual(is_parent_dir_required(False), './')


if __name__ == '__main__':
    unittest.main()
