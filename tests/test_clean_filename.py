import unittest

# Local implementation to be tested
from core import clean_filename


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
