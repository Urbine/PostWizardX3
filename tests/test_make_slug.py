# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Unit Tests for the Slug Generation Function

This module contains test cases for the `make_slug` function from the
workflows.media_source_assistant module. The function transforms various inputs
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
                "partner's",
                "Jane Doe;Ann Smith;Sarah Lee",
                "She's calm and does not worry",
                "-vid",
            ),
            "partners-jane-doe-ann-smith-sarah-lee-shes-calm-does-not-worry-vid",
        )
        self.assertEqual(
            make_slug(
                "Test Patrol",
                "Jane Doe,Ann Smith,Sarah Lee",
                "She's happy and I'm loving it",
                "-vid",
            ),
            "test-patrol-jane-doe-ann-smith-sarah-lee-shes-happy-im-loving-vid",
        )
        self.assertEqual(
            make_slug(
                "Netherlands",
                "Jane Roe",
                "she's not indifferent",
                "-vid",
                studio="SampleFilms - By Sample Director - Real Stoic",
            ),
            "netherlands-jane-roe-shes-not-indifferent-samplefilms-by-sample-director-real-stoic-vid",
        )
