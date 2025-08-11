"""
Unit Tests for the Slug Generation Function

This module contains test cases for the `make_slug` function from the
workflows.mcash_assistant module. The function transforms various inputs
(like title, models, description, suffix) into URL-friendly slugs.

The test cases verify that:
1. Special characters are properly handled (apostrophes, spaces)
2. Different input formats for models are correctly processed (semicolon vs comma separation)
3. Stopwords are appropriately removed from descriptions
4. Optional parameters like studio are properly incorporated
5. All parts are correctly joined with hyphens

These tests ensure that slugs are generated consistently and according to
the expected format for web publishing purposes.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

from unittest import TestCase
from tools.workflows_api import make_slug


class TestMakeSlug(TestCase):
    def test_make_slug(self):
        self.assertEqual(
            make_slug(
                "totico's",
                "Hannah X;Didi Dexter;Sarah O'Connor",
                "She's insane and does not dissemble it",
                "-vid",
            ),
            "toticos-hannah-x-didi-dexter-sarah-o-connor-shes-insane-does-not-dissemble-vid",
        )
        self.assertEqual(
            make_slug(
                "Test Patrol",
                "Hannah X,Didi Dexter,Sarah O'Connor",
                "She's insane and I ain't loving it",
                "-vid",
            ),
            "test-patrol-hannah-x-didi-dexter-sarah-o-connor-shes-insane-i-aint-loving-vid",
        )
        self.assertEqual(
            make_slug(
                "Netherlands",
                "Su Rye",
                "she's not so inclined",
                "-vid",
                studio="SapphoFilms - By Nikoletta Garian - Real Stoic",
            ),
            "netherlands-su-rye-shes-not-inclined-sapphofilms-by-nikoletta-garian-real-stoic-vid",
        )
