import unittest

# Local implementation to be tested
from core import clean_filename


class TestCleanFilename(unittest.TestCase):
    def test_clean_filename(self):
        # Possible cases
        self.assertEqual(clean_filename('sample.json', 'json'), 'sample.json')
        self.assertEqual(clean_filename('sample', 'json'), 'sample.json')
        self.assertEqual(clean_filename('sample', '.json'), 'sample.json')


if __name__ == '__main__':
    unittest.main()
