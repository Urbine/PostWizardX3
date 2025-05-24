"""
Partner Tag Cleaning Tests Module

This module contains unit tests for the clean_partner_tag function from the workflows_api module.
The clean_partner_tag function is responsible for processing partner tags by removing possessive
apostrophes to ensure consistent URL generation and taxonomy across the website.

The test suite verifies that the function correctly handles:
1. Single possessive apostrophes in words
2. Apostrophes in different word positions
3. Multiple possessive forms in a single tag
4. Strings without apostrophes
5. Single words without apostrophes

These tests ensure that the partner tag cleaning functionality works reliably across
various inputs, which is important for maintaining consistent URL patterns and taxonomy
organization in the WordPress content management system.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

import unittest
from workflows.workflows_api import clean_partner_tag


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
