"""Strict annual validation, provenance trust, and offline lookup."""

import hashlib
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

from .calendar_service import jalali, month_length
from .resources import DATA

CATEGORIES = {"national", "cultural", "religious", "international"}


def validate(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Unsupported data schema")
    year = data["solar_year"]
    if type(year) is not int or not 1350 <= year <= 1450:
        raise ValueError("Invalid year")
    if not isinstance(data.get("data_version"), str) or not data["data_version"]:
        raise ValueError("Missing data version")
    for s in data["sources"]:
        if (
            not isinstance(s.get("id"), str)
            or not s["id"]
            or not isinstance(s.get("url"), str)
            or not s["url"].startswith(("https://", "http://"))
        ):
            raise ValueError("Invalid source metadata")
    sources = {s["id"] for s in data["sources"]}
    if len(sources) != len(data["sources"]) or not sources:
        raise ValueError("Invalid source IDs")
    cov = data["coverage"]
    if any(
        cov.get(k) not in ("verified", "partial", "unavailable")
        for k in ("date_mapping", "official_occasions", "public_holidays")
    ):
        raise ValueError("Invalid coverage")
    seen = set()
    solar = set()
    for record in data["days"]:
        if not all(
            isinstance(record.get(k), str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", record[k])
            for k in ("gregorian_date", "jalali_date")
        ):
            raise ValueError("Noncanonical date")
        day = date.fromisoformat(record["gregorian_date"])
        j = jalali(day)
        if j.year != year or j.isoformat() != record["jalali_date"]:
            raise ValueError("Date mapping mismatch")
        if day in seen or record["jalali_date"] in solar:
            raise ValueError("Duplicate date mapping")
        h = record.get("hijri_date")
        if h:
            if not isinstance(h, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", h):
                raise ValueError("Noncanonical Hijri date")
            parts = h.split("-")
            if len(parts) != 3 or not all(v.isascii() and v.isdigit() for v in parts):
                raise ValueError("Invalid Hijri mapping")
            y, m, d = map(int, parts)
            if not 1300 <= y <= 1600 or not 1 <= m <= 12 or not 1 <= d <= 30:
                raise ValueError("Invalid Hijri values")
        seen.add(day)
        solar.add(record["jalali_date"])
    total = sum(month_length(year, m) for m in range(1, 13))
    if cov["date_mapping"] == "verified" and len(seen) != total:
        raise ValueError("Missing verified dates")
    ids = set()
    duplicates = set()
    for e in data["events"]:
        if not isinstance(e.get("id"), str) or not e["id"]:
            raise ValueError("Invalid event ID")
        if not isinstance(e.get("gregorian_date"), str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}", e["gregorian_date"]
        ):
            raise ValueError("Noncanonical event date")
        if e["id"] in ids:
            raise ValueError("Duplicate event ID")
        ids.add(e["id"])
        day = date.fromisoformat(e["gregorian_date"])
        if day not in seen:
            raise ValueError("Event outside mapped year")
        if type(e["is_public_holiday"]) is not bool:
            raise ValueError("Holiday flag must be boolean")
        if e["source_id"] not in sources:
            raise ValueError("Unknown event source")
        if (
            not isinstance(e["title"].get("fa"), str)
            or not e["title"]["fa"].strip()
            or "en" not in e["title"]
            or e["title"]["en"] is not None
            and not isinstance(e["title"]["en"], str)
        ):
            raise ValueError("Invalid bilingual title")
        if (
            not isinstance(e["categories"], list)
            or not e["categories"]
            or len(e["categories"]) != len(set(e["categories"]))
            or not set(e["categories"]) <= CATEGORIES
        ):
            raise ValueError("Invalid categories")
        sig = (day, e["title"]["fa"])
        if sig in duplicates:
            raise ValueError("Duplicate occasion")
        duplicates.add(sig)
    return {
        "year": year,
        "days": len(seen),
        "events": len(ids),
        "holiday_dates": len({e["gregorian_date"] for e in data["events"] if e["is_public_holiday"]}),
        "coverage": cov,
        "data_version": data["data_version"],
    }


class Repository:
    def __init__(self, bundled=None, user=None):
        self.packages = {}
        self.records = {}
        self.event_index = {}
        self.errors = []
        self.reports = []
        base = Path(bundled) if bundled else DATA / "calendars"
        try:
            manifest = json.loads((base / "manifest.json").read_text())
        except (OSError, ValueError) as e:
            self.errors.append("Bundled manifest: " + str(e))
            return
        for entry in manifest["packages"]:
            p = base / entry["file"]
            try:
                if hashlib.sha256(p.read_bytes()).hexdigest() != entry["sha256"]:
                    raise ValueError("Bundled data checksum mismatch")
                self._load(json.loads(p.read_text()), trusted=True)
            except (ValueError, KeyError, TypeError, AssertionError, OSError) as e:
                self.errors.append(f"{p.name}: {e}")
        user = (
            Path(user)
            if user
            else Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "rooz/calendars"
        )
        for p in sorted(user.glob("*.json")):
            try:
                obj = json.loads(p.read_text())
                validate(obj)
                if obj["solar_year"] in self.packages:
                    continue
                self._load(obj, trusted=False)
            except (ValueError, KeyError, TypeError, AssertionError, OSError) as e:
                self.errors.append(f"{p.name}: {e}")

    def _load(self, obj, trusted):
        report = validate(obj)
        report["trusted"] = trusted
        self.reports.append(report)
        self.packages[obj["solar_year"]] = {"data": obj, "trusted": trusted}
        for r in obj["days"]:
            self.records[date.fromisoformat(r["gregorian_date"])] = r
        for e in obj["events"]:
            self.event_index.setdefault(date.fromisoformat(e["gregorian_date"]), []).append(e)

    def known(self, day, kind="official_occasions"):
        try:
            year = jalali(day).year
        except ValueError:
            return False
        p = self.packages.get(year)
        return bool(p and p["trusted"] and p["data"]["coverage"][kind] == "verified" and day in self.records)

    def hijri(self, day):
        return (
            self.records[day].get("hijri_date")
            if day in self.records and self.known(day, "date_mapping")
            else None
        )

    def events(self, day):
        return sorted(self.event_index.get(day, []), key=lambda e: not e["is_public_holiday"])

    def visible(self, day, cfg):
        return [
            e
            for e in self.events(day)
            if set(e["categories"]) & set(cfg["visible_categories"])
            and (not e["is_public_holiday"] or cfg["show_public_holidays"])
        ]

    def holiday(self, day):
        return any(e["is_public_holiday"] for e in self.events(day))

    def next_holiday(self, day):
        for offset in range(370):
            candidate = day + timedelta(days=offset)
            if not self.known(candidate, "public_holidays"):
                return None
            if self.holiday(candidate):
                return candidate, offset
        return None
