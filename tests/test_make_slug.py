from unittest import TestCase
from workflows.content_select import make_slug


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
