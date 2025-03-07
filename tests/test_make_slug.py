from unittest import TestCase
from workflows.content_select import make_slug


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
