"""Bounded offline search with Persian/Arabic digit and letter normalization."""

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta

from .calendar_service import MIN_YEAR, MAX_YEAR, gregorian, jalali
from .i18n import GMONTHS, JMONTHS

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize(value):
    text = unicodedata.normalize("NFKC", value).translate(DIGITS).casefold()
    text = text.translate(str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک", "\u200c": " ", "\u200d": " ", "ـ": ""}))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def parse_date(query, mode="auto"):
    if mode not in ("auto", "shamsi", "gregorian"):
        raise ValueError("Invalid calendar")
    text = normalize(query)
    m = re.fullmatch(r"([0-9]{4})\s*[/.-]\s*([0-9]{1,2})\s*[/.-]\s*([0-9]{1,2})", text)
    if m:
        y, month, day = map(int, m.groups())
        kind = ("shamsi" if MIN_YEAR <= y <= MAX_YEAR else "gregorian") if mode == "auto" else mode
    else:
        m = re.fullmatch(r"([0-9]{1,2})\s+(.+?)\s+([0-9]{4})", text)
        if not m:
            # Numeric-looking date typos produce a validation message rather than a fake match.
            if re.fullmatch(r"[0-9/ .-]+", text) and any(c in text for c in "/.-"):
                raise ValueError("Use year/month/day")
            return None
        day, name, y = int(m[1]), m[2], int(m[3])
        found = [(k, n + 1) for k, names in (("shamsi", JMONTHS), ("gregorian", GMONTHS))
                 for values in names.values() for n, v in enumerate(values) if normalize(v) == name]
        found = [f for f in found if mode == "auto" or f[0] == mode]
        if not found:
            raise ValueError("Unknown month")
        kind, month = found[0]
    answer = gregorian(y, month, day) if kind == "shamsi" else date(y, month, day)
    jalali(answer)
    return answer


@dataclass(frozen=True)
class SearchResult:
    day: date
    kind: str
    title: str
    item_id: str = ""


def search(query, repo, personal, loc, today, mode="auto", limit=100):
    value = normalize(query)
    if not value:
        return [], 0
    candidate = parse_date(value, mode)
    if candidate:
        return [SearchResult(candidate, "date", loc.t("go_to_date"))], 1
    words = value.split()
    results = []
    for day, entries in sorted(repo.event_index.items()):
        for event in entries:
            haystack = normalize(" ".join(v or "" for v in event["title"].values()))
            if all(word in haystack for word in words):
                results.append(SearchResult(day, "occasion_result", loc.event_title(event)))
    if personal:
        from .personal import occurrence_day
        for item in personal.items():
            if all(word in normalize(item["title"] + " " + item["body"]) for word in words):
                anchor = date.fromisoformat(item["day"])
                day = anchor
                if item["repeat"] == "annual":
                    year = max(jalali(today).year, jalali(anchor).year)
                    day = occurrence_day(item, year)
                    if day and day < today and year < MAX_YEAR:
                        day = occurrence_day(item, year + 1)
                elif item["repeat"] in ("daily", "weekly"):
                    day = max(today, anchor)
                    if item["repeat"] == "weekly":
                        day += timedelta(days=(-(day - anchor).days) % 7)
                    try:
                        jalali(day)
                    except ValueError:
                        day = None
                if day:
                    results.append(SearchResult(day, "personal_result", item["title"], item["id"]))
    results.sort(key=lambda r: (r.day, r.kind, r.title))
    return results[:limit], len(results)
