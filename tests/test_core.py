import copy, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch
from rooz.calendar_service import *
from rooz.config import Config, validate as validate_config, DEFAULTS
from rooz.events import Repository, validate as validate_data
from rooz.i18n import Localizer, PAIRS, JMONTHS, GMONTHS, HMONTHS, WEEKDAYS, SHORT_WEEK
from rooz.formatting import dates
from rooz.position import place
from rooz import autostart

ROOT = Path(__file__).resolve().parents[1]


class CalendarTests(unittest.TestCase):
    def test_independent_official_every_day(self):
        fixture = json.loads((ROOT / "tests/fixtures/official-1405-days.json").read_text())
        self.assertEqual(365, len(fixture["days"]))
        previous = None
        for r in fixture["days"]:
            d = date.fromisoformat(r["gregorian_date"])
            self.assertEqual(r["jalali_date"], jalali(d).isoformat())
            self.assertEqual(d, gregorian(*map(int, r["jalali_date"].split("-"))))
            if previous:
                self.assertEqual(previous + timedelta(days=1), d)
            previous = d
        self.assertEqual(date(2026, 3, 21), gregorian(1405, 1, 1))
        self.assertEqual(date(2026, 10, 10), gregorian(1405, 7, 18))

    def test_roundtrip_entire_supported_range(self):
        start = gregorian(1350, 1, 1)
        end = gregorian(1450, 12, month_length(1450, 12))
        n = (end - start).days
        for i in range(n + 1):
            d = start + timedelta(days=i)
            j = jalali(d)
            self.assertEqual(d, gregorian(j.year, j.month, j.day))

    def test_official_leap_flags_full_range(self):
        obj = json.loads((ROOT / "tests/fixtures/official-leap-years-1350-1450.json").read_text())
        self.assertEqual(list(range(1350, 1451)), [r["jalali_year"] for r in obj["years"]])
        for r in obj["years"]:
            self.assertEqual(r["is_leap"], month_length(r["jalali_year"], 12) == 30)

    def test_boundaries_leaps(self):
        self.assertEqual(30, month_length(1403, 12))
        self.assertEqual(29, month_length(1404, 12))
        self.assertEqual(date(2025, 3, 20), gregorian(1403, 12, 30))
        self.assertEqual(date(2025, 3, 21), gregorian(1404, 1, 1))
        self.assertEqual(date(2027, 3, 20), gregorian(1405, 12, 29))
        self.assertEqual(date(2027, 3, 21), gregorian(1406, 1, 1))
        self.assertEqual((1350, 1), shift_month(1350, 1, -1))
        self.assertEqual((1450, 12), shift_month(1450, 12, 1))
        self.assertEqual((1406, 1), shift_month(1405, 12, 1))
        with self.assertRaises(ValueError):
            gregorian(1349, 1, 1)

    def test_grids_all_weekdays_and_six_rows(self):
        first_weekdays = set()
        has_six = False
        for y in range(1400, 1410):
            for m in range(1, 13):
                cells = month_cells(y, m)
                self.assertEqual(month_length(y, m), len(cells))
                self.assertEqual(len(cells), len({c.day for c in cells}))
                first_weekdays.add(cells[0].day.weekday())
                has_six |= cells[-1].row == 5
                for c in cells:
                    self.assertEqual({5: 6, 6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 0}[c.day.weekday()], c.column)
        self.assertEqual(set(range(7)), first_weekdays)
        self.assertTrue(has_six)
        cells = month_cells(1405, 7)
        self.assertEqual((0, 2), (cells[0].row, cells[0].column))
        self.assertEqual(4, cells[-1].row)

    def test_clock_midnight_jumps_and_timezone(self):
        instants = [
            datetime(2026, 10, 10, 20, 29, tzinfo=timezone.utc),
            datetime(2026, 10, 10, 20, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 9, 12, tzinfo=timezone.utc),
            datetime(2026, 10, 12, 12, tzinfo=timezone.utc),
        ]
        c = Clock(now=lambda: instants.pop(0))
        self.assertTrue(c.reconcile())
        self.assertEqual(date(2026, 10, 10), c.day)
        self.assertTrue(c.reconcile())
        self.assertEqual(date(2026, 10, 11), c.day)
        self.assertTrue(c.reconcile())
        self.assertEqual(date(2026, 10, 9), c.day)
        self.assertTrue(c.reconcile())
        frozen = Clock(now=lambda: datetime(2026, 10, 10, 12, tzinfo=timezone.utc))
        self.assertTrue(frozen.reconcile())
        self.assertFalse(frozen.reconcile())
        self.assertEqual(
            date(2026, 10, 11), civil_day("Asia/Tehran", datetime(2026, 10, 10, 22, tzinfo=timezone.utc))
        )
        self.assertEqual(
            timedelta(hours=4, minutes=30), datetime(2021, 7, 1, tzinfo=ZoneInfo("Asia/Tehran")).utcoffset()
        )
        self.assertEqual(
            timedelta(hours=3, minutes=30), datetime(2026, 7, 1, tzinfo=ZoneInfo("Asia/Tehran")).utcoffset()
        )


class EventTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository(user=Path("/nonexistent"))
        self.data = json.loads((ROOT / "data/calendars/1405.json").read_text())

    def test_annual_complete_and_source_mapping(self):
        report = validate_data(self.data)
        self.assertEqual((365, 305, 26), (report["days"], report["events"], report["holiday_dates"]))
        fixture = json.loads((ROOT / "tests/fixtures/official-1405-days.json").read_text())
        self.assertEqual(fixture["days"], self.data["days"])
        self.assertEqual(set(range(282)), {e["source_row"] for e in self.data["events"]})
        self.assertEqual(189, self.data["verification"]["main_occasion_cells"])
        self.assertEqual(93, self.data["verification"]["appendix_occasion_cells"])
        for r in fixture["days"]:
            self.assertEqual(r["hijri_date"], self.repo.hijri(date.fromisoformat(r["gregorian_date"])))

    def test_official_holiday_fixture(self):
        expected = [
            "01-01",
            "01-02",
            "01-03",
            "01-04",
            "01-12",
            "01-13",
            "01-25",
            "03-06",
            "03-14",
            "03-15",
            "04-03",
            "04-04",
            "05-13",
            "05-21",
            "05-22",
            "05-30",
            "06-08",
            "08-22",
            "10-02",
            "10-16",
            "11-04",
            "11-22",
            "12-09",
            "12-19",
            "12-20",
            "12-29",
        ]
        actual = {
            jalali(date.fromisoformat(e["gregorian_date"])).isoformat()[5:]
            for e in self.data["events"]
            if e["is_public_holiday"]
        }
        self.assertEqual(set(expected), actual)
        self.assertEqual("1447-10-01", self.repo.hijri(date(2026, 3, 21)))
        self.assertEqual("1448-03-17", self.repo.hijri(gregorian(1405, 6, 8)))
        es = self.repo.events(date(2026, 3, 21))
        self.assertEqual({"آغاز نوروز", "عید سعید فطر"}, {e["title"]["fa"] for e in es})
        self.assertEqual(2, sum(e["is_public_holiday"] for e in self.repo.events(gregorian(1405, 3, 14))))

    def test_lunar_continuity(self):
        previous = None
        for record in self.data["days"]:
            y, m, d = map(int, record["hijri_date"].split("-"))
            if previous:
                py, pm, pd = previous
                if (py, pm) == (y, m):
                    self.assertEqual(pd + 1, d)
                else:
                    self.assertIn(pd, (29, 30))
                    self.assertEqual(1, d)
                    self.assertEqual(pm % 12 + 1, m)
                    self.assertEqual(py + (pm == 12), y)
            previous = y, m, d

    def test_fridays_filters_countdown_and_coverage(self):
        fri = gregorian(1405, 7, 17)
        thu = gregorian(1405, 7, 16)
        self.assertEqual(4, fri.weekday())
        self.assertFalse(self.repo.holiday(fri))
        self.assertFalse(self.repo.holiday(thu))
        today = gregorian(1405, 7, 18)
        self.assertEqual((gregorian(1405, 8, 22), 34), self.repo.next_holiday(today))
        holiday = date(2026, 3, 21)
        self.assertEqual((holiday, 0), self.repo.next_holiday(holiday))
        self.assertEqual(
            [], self.repo.visible(holiday, {"visible_categories": [], "show_public_holidays": False})
        )
        self.assertTrue(self.repo.holiday(holiday))
        self.assertIsNone(self.repo.next_holiday(gregorian(1406, 1, 1)))
        self.assertFalse(self.repo.known(gregorian(1406, 1, 1)))
        self.assertIsNone(self.repo.hijri(gregorian(1406, 1, 1)))
        self.assertTrue(self.repo.known(today))
        self.assertEqual([], self.repo.events(today))

    def test_validation_negative_cases(self):
        for edit in (
            lambda d: d["days"].pop(),
            lambda d: d["days"].append(d["days"][0]),
            lambda d: d["events"][0].update(is_public_holiday="true"),
            lambda d: d["events"][0].update(source_id="unknown"),
            lambda d: d["days"][0].update(hijri_date="1447-13-01"),
            lambda d: d["events"].append(d["events"][0]),
        ):
            obj = copy.deepcopy(self.data)
            edit(obj)
            with self.assertRaises(ValueError):
                validate_data(obj)

    def test_invalid_user_package_and_untrusted_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text("{bad")
            r = Repository(user=tmp)
            self.assertTrue(r.errors)
            self.assertTrue(r.known(date(2026, 3, 21)))
            p.unlink()
            obj = copy.deepcopy(self.data)
            obj["solar_year"] = 1406
            for d in obj["days"]:
                d["gregorian_date"] = (
                    date.fromisoformat(d["gregorian_date"]) + timedelta(days=365)
                ).isoformat()
                d["jalali_date"] = d["jalali_date"].replace("1405", "1406")
            for e in obj["events"]:
                e["gregorian_date"] = (
                    date.fromisoformat(e["gregorian_date"]) + timedelta(days=365)
                ).isoformat()
            p.write_text(json.dumps(obj))
            r = Repository(user=tmp)
            self.assertFalse(r.known(date(2027, 3, 21)))
            self.assertIsNone(r.hijri(date(2027, 3, 21)))


class SettingsTests(unittest.TestCase):
    def test_atomic_save_and_bad_config_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.json"
            p.write_text("{bad")
            c = Config(p)
            self.assertTrue(c.warning)
            self.assertEqual(1, len(list(Path(tmp).glob("config.bad-*.json"))))
            c.value["language"] = "en"
            c.save()
            self.assertEqual("en", Config(p).value["language"])
            self.assertEqual([], list(Path(tmp).glob(".rooz-*")))

    def test_bounds_types_schema(self):
        c = validate_config(
            {
                "language": "xx",
                "digits": "latin",
                "window": {"locked": "true", "position": [-200, 30]},
                "appearance": {"widget_scale": 20, "text_scale": False, "accent_color": "oops"},
            }
        )
        self.assertEqual("fa", c["language"])
        self.assertEqual("latin", c["digits"])
        self.assertFalse(c["window"]["locked"])
        self.assertEqual(1.6, c["appearance"]["widget_scale"])
        self.assertEqual(1, c["appearance"]["text_scale"])
        self.assertEqual([-200, 30], c["window"]["position"])
        self.assertEqual("#5FE3AF", c["appearance"]["accent_color"])
        self.assertEqual(1, validate_config({"schema_version": 0})["schema_version"])
        with self.assertRaises(ValueError):
            validate_config({"schema_version": 999})

    def test_autostart_opt_in_out(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"XDG_CONFIG_HOME": tmp}):
            self.assertFalse(autostart.enabled())
            exe = Path(tmp) / "rooz"
            exe.touch()
            autostart.set_enabled(True, str(exe))
            self.assertTrue(autostart.enabled())
            self.assertIn("Exec=/usr/bin/rooz --widget", autostart.path().read_text())
            autostart.set_enabled(False)
            self.assertFalse(autostart.enabled())
            self.assertFalse(autostart.path().exists())
            with self.assertRaises(ValueError):
                autostart.set_enabled(True, "/nonexistent")

    def test_negative_monitor_position(self):
        self.assertEqual((-344, 24), place((-1920, 0, 1920, 1080), (320, 208)))
        self.assertEqual((-1920, 0), place((-1920, 0, 1920, 1080), (320, 208), [-9999, -9999]))
        self.assertEqual((-320, 872), place((-1920, 0, 1920, 1080), (320, 208), [5000, 5000]))


class LocalizationTests(unittest.TestCase):
    def test_catalog_and_digits_independent(self):
        self.assertTrue(all(len(v) == 2 and all(isinstance(s, str) and s for s in v) for v in PAIRS.values()))
        for catalog, count in [(JMONTHS, 12), (GMONTHS, 12), (HMONTHS, 12), (WEEKDAYS, 7), (SHORT_WEEK, 7)]:
            for lang in ("fa", "en"):
                self.assertEqual(count, len(catalog[lang]))
        cfg = copy.deepcopy(DEFAULTS)
        cfg["language"] = "en"
        loc = Localizer(cfg)
        self.assertEqual("Today", loc.t("today"))
        self.assertEqual("۱۴۰۵", loc.n(1405))
        cfg["digits"] = "latin"
        self.assertEqual("1405", loc.n(1405))
        cfg["language"] = "fa"
        self.assertEqual("امروز", loc.t("today"))
        self.assertEqual("1405", loc.n(1405))

    def test_english_count_plurals(self):
        cfg = copy.deepcopy(DEFAULTS)
        cfg.update(language="en", digits="latin")
        loc = Localizer(cfg)
        self.assertEqual("1 more event", loc.more(1))
        self.assertEqual("2 more events", loc.more(2))
        self.assertEqual("1 day to public holiday", loc.remaining(1))
        self.assertEqual("0 days to public holiday", loc.remaining(0))

    def test_clipboard_and_fallback(self):
        cfg = copy.deepcopy(DEFAULTS)
        loc = Localizer(cfg)
        repo = Repository(user="/nonexistent")
        self.assertEqual("۱۸ مهر ۱۴۰۵", dates(date(2026, 10, 10), loc, repo)[0])
        cfg["digits"] = "latin"
        self.assertEqual("18 مهر 1405", dates(date(2026, 10, 10), loc, repo)[0])
        self.assertEqual("2026-10-10", date(2026, 10, 10).isoformat())
        cfg["language"] = "en"
        self.assertIn(
            "English translation unavailable", loc.event_title({"title": {"fa": "مثال", "en": None}})
        )

    def test_headless_commands(self):
        env = {**os.environ, "DISPLAY": "", "WAYLAND_DISPLAY": "", "PYTHONPATH": str(ROOT / "src")}
        for arg in ("--version", "--check-data"):
            result = subprocess.run(
                [sys.executable, "-m", "rooz", arg], env=env, capture_output=True, text=True
            )
            self.assertEqual(0, result.returncode, result.stderr)
        result = subprocess.run(
            [sys.executable, "-m", "rooz", "--widget"], env=env, capture_output=True, text=True
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("graphical display", result.stderr)


if __name__ == "__main__":
    unittest.main()
