import unittest
import datetime

# To be tested
from core import parse_date_to_iso


class TestParseDateToISO(unittest.TestCase):
    def test_parse_date_to_iso(self):
        self.assertEqual(
            parse_date_to_iso("Aug 13th, 2024", m_abbr=True), datetime.date(2024, 8, 13)
        )

        self.assertEqual(
            parse_date_to_iso("August 13th, 2024"), datetime.date(2024, 8, 13)
        )  # m_abbr = False / zero_day = False (Default)

        self.assertEqual(
            parse_date_to_iso("Aug 01st, 2024", m_abbr=True, zero_day=True),
            datetime.date(2024, 8, 1),
        )

        self.assertEqual(
            parse_date_to_iso("Aug 13th, 2024", m_abbr=True), datetime.date(2024, 8, 13)
        )

        self.assertEqual(
            parse_date_to_iso("January 31st, 2024", zero_day=True),
            datetime.date(2024, 1, 31),
        )

        self.assertEqual(
            parse_date_to_iso("May 31st, 2017"), datetime.date(2017, 5, 31)
        )


if __name__ == "__main__":
    unittest.main()
