import unittest
from workflows.content_select import clean_partner_tag


class TestCleanPartnerTag(unittest.TestCase):
    def test_clean_partner_tag(self):
        self.assertEqual(clean_partner_tag("Totico's"), "Toticos")
        self.assertEqual(clean_partner_tag("Paradise GF's"), "Paradise GFs")
        self.assertEqual(clean_partner_tag("All Mama's & Papa's"), "All Mamas & Papas")
        self.assertEqual(
            clean_partner_tag("This one does not need anything"),
            "This one does not need anything",
        )
        self.assertEqual(clean_partner_tag("wildlifeclouds"), "wildlifeclouds")


if __name__ == "__main__":
    unittest.main()
