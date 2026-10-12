"""Private, transactional notes and occurrence-aware reminders; no GTK or network."""

import os
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .calendar_service import MIN_YEAR, MAX_YEAR, gregorian, jalali, month_length

KINDS = ("note", "birthday", "appointment", "task")
REPEATS = ("none", "daily", "weekly", "annual")


class PersonalError(ValueError):
    """A personal-data operation failed without discarding the original database."""


@dataclass(frozen=True)
class Occurrence:
    item: dict
    day: date
    done: bool = False
    delivered: bool = False

    @property
    def key(self):
        return self.item["id"], self.day.isoformat(), self.item["time"]


def occurrence_day(item, year):
    anchor = date.fromisoformat(item["day"])
    j = jalali(anchor)
    if item["repeat"] == "none":
        return anchor if year == j.year else None
    if not j.year <= year <= MAX_YEAR:
        return None
    # An Esfand 30 anniversary falls on Esfand's last day in a non-leap year.
    return gregorian(year, j.month, min(j.day, month_length(year, j.month)))


def occurs_on(item, day):
    anchor = date.fromisoformat(item["day"])
    if day < anchor:
        return False
    if item["repeat"] == "daily":
        return True
    if item["repeat"] == "weekly":
        return (day - anchor).days % 7 == 0
    return occurrence_day(item, jalali(day).year) == day


def wall_instant(day, value, zone):
    """First fold; nonexistent local times move forward through the DST gap."""
    if zone == "system":
        try:
            configured = os.environ.get("TZ", "").lstrip(":")
            if configured and not configured.startswith("/"):
                tz = ZoneInfo(configured)
            else:
                with open(configured or "/etc/localtime", "rb") as source:
                    tz = ZoneInfo.from_file(source)
        except (OSError, ValueError, KeyError):
            tz = datetime.now().astimezone().tzinfo
    else:
        tz = ZoneInfo(zone)
    local = datetime.combine(day, time.fromisoformat(value)).replace(tzinfo=tz, fold=0)
    return local.astimezone(timezone.utc)


class PersonalStore:
    def __init__(self, path=None):
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
        self.path = Path(path) if path else base / "rooz/personal.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path.parent.chmod(0o700)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        except FileExistsError:
            pass
        self.path.chmod(0o600)
        self.connection = None
        self._cache = None
        try:
            self.connection = sqlite3.connect(self.path, timeout=3)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            version = self.connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise PersonalError("Unsupported personal-data schema")
            with self.connection:
                self.connection.execute("""CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL,
                    day TEXT NOT NULL, kind TEXT NOT NULL, repeat TEXT NOT NULL,
                    notify INTEGER NOT NULL, time TEXT NOT NULL, deleted INTEGER NOT NULL DEFAULT 0)""")
                self.connection.execute("""CREATE TABLE IF NOT EXISTS occurrences (
                    item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                    day TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, delivered INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(item_id, day))""")
                self.connection.execute("PRAGMA user_version = 1")
            self.items()  # Validate existing rows before exposing or changing personal data.
        except (sqlite3.Error, OSError, ValueError, KeyError) as error:
            self.close()
            raise PersonalError("Personal data could not be opened") from error

    @staticmethod
    def validate(item):
        if not isinstance(item.get("title"), str) or not item["title"].strip() or len(item["title"]) > 200:
            raise PersonalError("A title of 1–200 characters is required")
        if not isinstance(item.get("body", ""), str) or len(item.get("body", "")) > 10000:
            raise PersonalError("Note text exceeds 10000 characters")
        if "\x00" in item["title"] or "\x00" in item.get("body", ""):
            raise PersonalError("Invalid text character")
        try:
            anchor = date.fromisoformat(item["day"])
            jalali(anchor)
        except (ValueError, TypeError, KeyError) as error:
            raise PersonalError("Unsupported or invalid date") from error
        if item.get("kind") not in KINDS or item.get("repeat") not in REPEATS:
            raise PersonalError("Invalid kind or repeat")
        if type(item.get("notify")) not in (bool, int) or item["notify"] not in (0, 1):
            raise PersonalError("Invalid notification choice")
        if not isinstance(item.get("time"), str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", item["time"]):
            raise PersonalError("Invalid reminder time")
        return dict(item, title=item["title"].strip(), body=item.get("body", ""), notify=bool(item["notify"]))

    def items(self, include_deleted=False):
        if self._cache is None:
            try:
                self._cache = [self.validate(dict(row)) for row in self.connection.execute("SELECT * FROM items ORDER BY day, id")]
            except (sqlite3.Error, PersonalError) as error:
                raise PersonalError("Personal data could not be read") from error
        return [dict(i) for i in self._cache if include_deleted or not i["deleted"]]

    def get(self, item_id):
        return next((i for i in self.items() if i["id"] == item_id), None)

    def save(self, title, body, day, kind="note", repeat="none", notify=False, reminder_time="09:00", item_id=None):
        if type(day) is not date:
            raise PersonalError("A date is required")
        item = self.validate(dict(id=item_id or uuid.uuid4().hex, title=title, body=body, day=day.isoformat(),
                                  kind=kind, repeat=repeat, notify=notify, time=reminder_time))
        old = self.get(item_id) if item_id else None
        if item_id and old is None:
            raise PersonalError("The original item is no longer available")
        if not old and len(self.items()) >= 10000:
            raise PersonalError("Personal item limit reached")
        try:
            with self.connection:
                self.connection.execute("""INSERT INTO items(id,title,body,day,kind,repeat,notify,time)
                    VALUES(:id,:title,:body,:day,:kind,:repeat,:notify,:time)
                    ON CONFLICT(id) DO UPDATE SET title=excluded.title,body=excluded.body,day=excluded.day,
                    kind=excluded.kind,repeat=excluded.repeat,notify=excluded.notify,time=excluded.time""", item)
                if old and any(old[k] != item[k] for k in ("day", "repeat", "time")):
                    self.connection.execute("DELETE FROM occurrences WHERE item_id=?", (item["id"],))
            self._cache = None
        except sqlite3.Error as error:
            raise PersonalError("Personal data could not be saved") from error
        return item["id"]

    def set_deleted(self, item_id, deleted=True):
        try:
            with self.connection:
                self.connection.execute("UPDATE items SET deleted=? WHERE id=?", (int(deleted), item_id))
            self._cache = None
        except sqlite3.Error as error:
            raise PersonalError("Personal data could not be saved") from error

    def state(self, item_id, day):
        try:
            row = self.connection.execute("SELECT done,delivered FROM occurrences WHERE item_id=? AND day=?",
                                          (item_id, day.isoformat())).fetchone()
        except sqlite3.Error as error:
            raise PersonalError("Personal data could not be read") from error
        return (bool(row[0]), bool(row[1])) if row else (False, False)

    def set_state(self, item_id, day, field, value=True):
        if field not in ("done", "delivered"):
            raise PersonalError("Invalid occurrence field")
        item = self.get(item_id)
        if item is None or not occurs_on(item, day):
            raise PersonalError("Invalid occurrence")
        try:
            with self.connection:
                self.connection.execute(f"""INSERT INTO occurrences(item_id,day,{field}) VALUES(?,?,?)
                    ON CONFLICT(item_id,day) DO UPDATE SET {field}=excluded.{field}""",
                                        (item_id, day.isoformat(), int(value)))
        except sqlite3.Error as error:
            raise PersonalError("Personal data could not be saved") from error

    def on(self, day):
        year = jalali(day).year
        return [Occurrence(i, day, *self.state(i["id"], day)) for i in self.items()
                if occurs_on(i, day)]

    def entries(self, today, mode="upcoming"):
        if mode == "today":
            return self.on(today)
        year = jalali(today).year
        result = []
        for item in self.items():
            if item["repeat"] in ("daily", "weekly") and mode != "all":
                anchor = date.fromisoformat(item["day"])
                first = max(today, anchor)
                if item["repeat"] == "weekly":
                    first += timedelta(days=(-(first - anchor).days) % 7)
                for step in range(367):
                    day = first + timedelta(days=step * (7 if item["repeat"] == "weekly" else 1))
                    try:
                        jalali(day)
                    except ValueError:
                        break
                    state = self.state(item["id"], day)
                    if not state[0]:
                        result.append(Occurrence(item, day, *state))
                        break
                continue
            years = range(year, min(MAX_YEAR, year + 1) + 1) if item["repeat"] == "annual" and mode != "all" else (jalali(date.fromisoformat(item["day"])).year,)
            for y in years:
                day = occurrence_day(item, y)
                if day is None:
                    continue
                state = self.state(item["id"], day)
                if mode == "all" or day >= today and not state[0]:
                    result.append(Occurrence(item, day, *state))
                    break
        return sorted(result, key=lambda o: (o.day, o.item["time"], o.item["title"]))

    def due(self, now, zone):
        if now.tzinfo is None:
            raise PersonalError("An aware time is required")
        local_day = now.astimezone(ZoneInfo(zone)).date() if zone != "system" else now.astimezone().date()
        result = []
        for day in (local_day - timedelta(days=1), local_day):
            try:
                occurrences = self.on(day)
            except ValueError:
                continue
            for o in occurrences:
                if o.item["notify"] and not o.done and not o.delivered:
                    age = now.astimezone(timezone.utc) - wall_instant(day, o.item["time"], zone)
                    if timedelta(0) <= age <= timedelta(hours=24):
                        result.append(o)
        return sorted(result, key=lambda o: (o.day, o.item["time"]))

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None


class ReminderEngine:
    """Persist successful deliveries; retry failures slowly without duplicate in-flight sends."""
    def __init__(self, store, send, error=lambda: None):
        self.store, self.send, self.error = store, send, error
        self.pending, self.sent, self.retry = set(), {}, {}

    def tick(self, now, zone, enabled):
        if not enabled:
            return
        cutoff = now - timedelta(hours=25)
        self.sent = {k: v for k, v in self.sent.items() if v >= cutoff}
        self.retry = {k: v for k, v in self.retry.items() if v >= cutoff}
        try:
            due = self.store.due(now, zone)
        except (PersonalError, sqlite3.Error):
            self.error()
            return
        batch = [o for o in due if o.key not in self.pending and o.key not in self.sent
                 and self.retry.get(o.key, now) <= now][:5]
        for occurrence in batch:
            self.pending.add(occurrence.key)
            def delivered(success, o=occurrence):
                self.pending.discard(o.key)
                if success:
                    self.sent[o.key] = now
                    self.retry.pop(o.key, None)
                    try:
                        current = self.store.get(o.item["id"])
                        if current and all(current[k] == o.item[k] for k in ("day", "time", "repeat", "notify")):
                            self.store.set_state(o.item["id"], o.day, "delivered")
                    except (PersonalError, sqlite3.Error):
                        self.error()
                else:
                    self.retry[o.key] = now + timedelta(minutes=2)
            self.send(occurrence, delivered)
