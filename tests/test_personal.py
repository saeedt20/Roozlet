import copy
import os
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from rooz.calendar_service import gregorian, month_length
from rooz.config import DEFAULTS, validate
from rooz.events import Repository
from rooz.i18n import Localizer
from rooz.personal import PersonalError, PersonalStore, ReminderEngine, wall_instant
from rooz.search import normalize, parse_date, search


class PersonalTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.path = Path(self.home.name) / "data/personal.sqlite3"
        self.store = PersonalStore(self.path)
        self.day = date(2026, 10, 12)

    def tearDown(self):
        self.store.close()
        self.home.cleanup()

    def test_private_transactional_persistence_and_unicode(self):
        key = self.store.save("  یادداشت شخصی  ", "متن چندخطی\n<script>literal</script>", self.day)
        self.store.close()
        self.store = PersonalStore(self.path)
        item = self.store.get(key)
        self.assertEqual("یادداشت شخصی", item["title"])
        self.assertEqual("متن چندخطی\n<script>literal</script>", item["body"])
        self.assertEqual(0o600, self.path.stat().st_mode & 0o777)
        self.assertEqual(0o700, self.path.parent.stat().st_mode & 0o777)
        self.assertEqual(key, self.store.on(self.day)[0].item["id"])

    def test_invalid_values_and_failed_write_leave_original(self):
        key = self.store.save("Original", "body", self.day)
        for overrides in ({"title": ""}, {"body": "X" * 10001}, {"kind": "bad"},
                          {"repeat": "bad"}, {"reminder_time": "24:00"}, {"title": "bad\x00"}):
            args = dict(title="new", body="new", day=self.day, item_id=key)
            args.update(overrides)
            with self.assertRaises(PersonalError):
                self.store.save(**args)
            self.assertEqual("Original", self.store.get(key)["title"])
        self.store.connection.execute("PRAGMA query_only = ON")
        with self.assertRaises(PersonalError):
            self.store.save("Replacement", "new", self.day, item_id=key)
        self.assertEqual("Original", self.store.get(key)["title"])

    def test_soft_delete_undo_and_update_identity(self):
        key = self.store.save("Original", "", self.day)
        self.store.save("Changed", "note", self.day, item_id=key)
        self.assertEqual(1, len(self.store.items()))
        self.store.set_deleted(key)
        self.assertEqual([], self.store.on(self.day))
        self.assertEqual(1, len(self.store.items(include_deleted=True)))
        self.store.set_deleted(key, False)
        self.assertEqual("Changed", self.store.get(key)["title"])

    def test_annual_esfand_leap_and_per_occurrence_completion(self):
        leap_year = next(y for y in range(1400, 1405) if month_length(y, 12) == 30)
        anchor = gregorian(leap_year, 12, 30)
        key = self.store.save("Birthday", "", anchor, "birthday", "annual", True)
        non_leap = next(y for y in range(leap_year + 1, 1410) if month_length(y, 12) == 29)
        anniversary = gregorian(non_leap, 12, 29)
        self.assertEqual(key, self.store.on(anniversary)[0].item["id"])
        self.store.set_state(key, anniversary, "done")
        self.assertTrue(self.store.on(anniversary)[0].done)
        next_day = gregorian(non_leap + 1, 12, month_length(non_leap + 1, 12))
        self.assertFalse(self.store.on(next_day)[0].done)
        self.assertEqual(next_day, self.store.entries(anniversary)[0].day)
        self.assertEqual([], self.store.on(gregorian(leap_year - 1, 12, month_length(leap_year - 1, 12))))

    def test_due_grace_timezone_and_no_past_notification_flood(self):
        for offset in (-2, -1, 0, 1):
            self.store.save(str(offset), "", self.day + timedelta(days=offset), notify=True, reminder_time="09:00")
        now = datetime(2026, 10, 12, 5, 30, tzinfo=timezone.utc)  # 09:00 Tehran
        self.assertEqual({"-1", "0"}, {o.item["title"] for o in self.store.due(now, "Asia/Tehran")})
        later = now + timedelta(seconds=1)
        self.assertEqual(["0"], [o.item["title"] for o in self.store.due(later, "Asia/Tehran")])
        occurrence = self.store.due(later, "Asia/Tehran")[0]
        self.store.set_state(occurrence.item["id"], occurrence.day, "done")
        self.assertEqual([], self.store.due(later, "Asia/Tehran"))

    def test_daily_and_weekly_repeat_each_have_independent_completion(self):
        daily = self.store.save("Daily", "", self.day, "task", "daily", True)
        weekly = self.store.save("Weekly", "", self.day, "task", "weekly", True)
        self.assertEqual({daily, weekly}, {o.item["id"] for o in self.store.on(self.day)})
        self.assertEqual({daily}, {o.item["id"] for o in self.store.on(self.day + timedelta(days=1))})
        self.store.set_state(daily, self.day, "done")
        self.assertFalse(self.store.on(self.day + timedelta(days=1))[0].done)
        self.assertEqual(self.day + timedelta(days=1), next(o.day for o in self.store.entries(self.day) if o.item["id"] == daily))
        self.assertEqual(self.day + timedelta(days=7), next(o.day for o in self.store.entries(self.day + timedelta(days=1)) if o.item["id"] == weekly))
        self.assertEqual([], self.store.on(self.day - timedelta(days=1)))

    def test_dispatch_gate_pending_retry_and_durable_success(self):
        key = self.store.save("Reminder", "", self.day, notify=True)
        now = datetime(2026, 10, 12, 5, 30, tzinfo=timezone.utc)
        calls = []
        engine = ReminderEngine(self.store, lambda o, done: calls.append((o, done)))
        engine.tick(now, "Asia/Tehran", False)
        self.assertEqual([], calls)
        engine.tick(now, "Asia/Tehran", True)
        engine.tick(now, "Asia/Tehran", True)
        self.assertEqual(1, len(calls))
        calls[0][1](False)
        engine.tick(now + timedelta(seconds=30), "Asia/Tehran", True)
        self.assertEqual(1, len(calls))
        engine.tick(now + timedelta(minutes=2), "Asia/Tehran", True)
        self.assertEqual(2, len(calls))
        calls[1][1](True)
        self.store.close()
        self.store = PersonalStore(self.path)
        restarted = ReminderEngine(self.store, lambda o, done: calls.append((o, done)))
        restarted.tick(now + timedelta(minutes=3), "Asia/Tehran", True)
        self.assertEqual(2, len(calls))
        self.assertTrue(self.store.state(key, self.day)[1])

    def test_schedule_edit_resets_delivery_but_text_edit_does_not(self):
        key = self.store.save("Reminder", "", self.day, notify=True)
        self.store.set_state(key, self.day, "delivered")
        self.store.save("Updated text", "", self.day, notify=True, item_id=key)
        self.assertTrue(self.store.state(key, self.day)[1])
        self.store.save("Updated time", "", self.day, notify=True, reminder_time="10:00", item_id=key)
        self.assertFalse(self.store.state(key, self.day)[1])

    def test_pending_old_schedule_cannot_mark_new_schedule_delivered(self):
        key = self.store.save("Reminder", "", self.day, notify=True)
        calls = []
        engine = ReminderEngine(self.store, lambda o, done: calls.append(done))
        engine.tick(datetime(2026, 10, 12, 5, 30, tzinfo=timezone.utc), "Asia/Tehran", True)
        self.store.save("Reminder", "", self.day, notify=True, reminder_time="10:00", item_id=key)
        calls[0](True)
        self.assertFalse(self.store.state(key, self.day)[1])

    def test_dst_gap_moves_forward_and_ambiguous_time_uses_first_fold(self):
        self.assertEqual(datetime(2026, 3, 29, 1, 30, tzinfo=timezone.utc),
                         wall_instant(date(2026, 3, 29), "02:30", "Europe/Berlin"))
        self.assertEqual(datetime(2026, 10, 25, 0, 30, tzinfo=timezone.utc),
                         wall_instant(date(2026, 10, 25), "02:30", "Europe/Berlin"))

    def test_corrupt_and_future_schema_are_kept_without_replacing(self):
        self.store.close()
        self.path.write_bytes(b"not a database")
        with self.assertRaises(PersonalError):
            PersonalStore(self.path)
        self.assertEqual(b"not a database", self.path.read_bytes())
        self.path.unlink()
        self.store = PersonalStore(self.path)
        self.store.connection.execute("PRAGMA user_version=9")
        self.store.close()
        with self.assertRaises(PersonalError):
            PersonalStore(self.path)
        db = sqlite3.connect(self.path)
        self.assertEqual(9, db.execute("PRAGMA user_version").fetchone()[0])
        db.close()

    def test_notification_preference_is_additive_and_opt_in(self):
        self.assertFalse(validate({})["personal"]["notifications_enabled"])
        self.assertTrue(validate({"personal": {"notifications_enabled": True}})["personal"]["notifications_enabled"])
        self.assertFalse(validate({"personal": {"notifications_enabled": "true"}})["personal"]["notifications_enabled"])


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository(user="/nonexistent")
        self.cfg = copy.deepcopy(DEFAULTS)
        self.loc = Localizer(self.cfg)
        self.today = date(2026, 10, 12)

    def test_numeric_dates_in_three_digit_styles_and_named_months(self):
        for text in ("۱۴۰۵/۷/۲۰", "١٤٠٥/٧/٢٠", "1405-07-20", "2026.10.12", "۲۰ مهر ۱۴۰۵", "20 Mehr 1405", "12 October 2026"):
            self.assertEqual(self.today, parse_date(text))
        self.assertEqual(self.today, parse_date("2026/10/12", "gregorian"))
        self.assertEqual(self.today, parse_date("1405/7/20", "shamsi"))

    def test_invalid_and_out_of_range_dates_do_not_silently_match(self):
        for text in ("1405/13/1", "1405/12/30", "2026/2/30", "1349/1/1", "1451/1/1", "1405/7", "20 Unknown 1405"):
            with self.assertRaises(ValueError):
                parse_date(text)
        self.assertIsNone(parse_date("حافظ"))

    def test_persian_normalization_and_bilingual_event_search(self):
        self.assertEqual(normalize("كيكِ\u200c۱۲"), normalize("کیک 12"))
        fa, total = search("حافظ", self.repo, None, self.loc, self.today)
        self.assertGreater(total, 0)
        self.assertTrue(all("حافظ" in r.title for r in fa))
        self.cfg["language"] = "en"
        en, total = search("Hafez", self.repo, None, self.loc, self.today)
        self.assertGreater(total, 0)
        self.assertEqual({r.day for r in fa}, {r.day for r in en})
        self.assertEqual(self.today, search("۱۴۰۵/۷/۲۰", self.repo, None, self.loc, self.today)[0][0].day)

    def test_personal_body_search_undo_and_bounded_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PersonalStore(Path(tmp) / "personal.sqlite3")
            try:
                key = store.save("Private literal", "کیک تولد", self.today)
                matches, total = search("كيك", self.repo, store, self.loc, self.today)
                self.assertEqual(key, matches[0].item_id)
                store.set_deleted(key)
                self.assertEqual(([], 0), search("كيك", self.repo, store, self.loc, self.today))
                store.set_deleted(key, False)
                values, total = search("روز", self.repo, store, self.loc, self.today, limit=5)
                self.assertGreater(total, len(values))
                self.assertEqual(5, len(values))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
