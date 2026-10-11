import copy
import tempfile
import unittest
from datetime import date
from pathlib import Path

from rooz.config import DEFAULTS, Config, validate
from rooz.events import Repository
from rooz.formatting import dates, full_date
from rooz.i18n import Localizer


class DateFormatTests(unittest.TestCase):
    def setUp(self):
        self.cfg = copy.deepcopy(DEFAULTS)
        self.loc = Localizer(self.cfg)
        self.repo = Repository(user="/nonexistent")

    def test_numeric_dates_are_year_month_day_in_both_languages_and_digit_styles(self):
        expected = ["1405/1/1", "2026/3/21", "1447/10/1"]
        self.cfg["calendar"]["prefer_numerical_dates"] = True
        for language in ("fa", "en"):
            for digits in ("persian", "latin"):
                with self.subTest(language=language, digits=digits):
                    self.cfg.update(language=language, digits=digits)
                    self.assertEqual(
                        [self.loc.n(value) for value in expected],
                        dates(date(2026, 3, 21), self.loc, self.repo),
                    )

    def test_live_preference_applies_to_hover_and_explicit_copy_override(self):
        day = date(2026, 10, 10)
        self.cfg.update(language="en", digits="latin")
        self.assertIn("18 Mehr 1405", full_date(day, self.loc, self.repo))
        self.assertEqual("2026/10/10", dates(day, self.loc, self.repo, numerical=True)[1])
        self.assertIn("18 Mehr 1405", full_date(day, self.loc, self.repo))
        self.cfg["calendar"]["prefer_numerical_dates"] = True
        tooltip = full_date(day, self.loc, self.repo)
        self.assertIn("Saturday\n1405/7/18\n2026/10/10\n1448/4/28", tooltip)
        self.assertNotIn("October", tooltip)
        self.assertEqual("18 Mehr 1405", dates(day, self.loc, self.repo, numerical=False)[0])

    def test_unavailable_hijri_stays_unavailable_in_numeric_mode(self):
        self.cfg.update(language="en", digits="latin")
        self.assertEqual(
            ["1406/1/1", "2027/3/21", "Hijri unavailable"],
            dates(date(2027, 3, 21), self.loc, self.repo, numerical=True),
        )

    def test_preference_persists_and_old_or_invalid_configs_keep_text_default(self):
        self.assertFalse(validate({})["calendar"]["prefer_numerical_dates"])
        self.assertFalse(
            validate({"calendar": {"prefer_numerical_dates": "true"}})["calendar"]["prefer_numerical_dates"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config(Path(tmp) / "config.json")
            cfg.value["calendar"]["prefer_numerical_dates"] = True
            cfg.save()
            self.assertTrue(Config(cfg.path).value["calendar"]["prefer_numerical_dates"])


if __name__ == "__main__":
    unittest.main()
