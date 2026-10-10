"""Civil calendar adapter, deliberately limited to Solar Hijri 1350–1450."""

import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent / "_vendor"))
import jdatetime

MIN_YEAR, MAX_YEAR = 1350, 1450


def jalali(day):
    j = jdatetime.date.fromgregorian(date=day)
    if not MIN_YEAR <= j.year <= MAX_YEAR:
        raise ValueError("Supported Solar Hijri years: 1350–1450")
    return j


def gregorian(year, month, day):
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError("Supported Solar Hijri years: 1350–1450")
    return jdatetime.date(year, month, day).togregorian()


def month_length(year, month):
    return 31 if month <= 6 else 30 if month < 12 or jdatetime.date(year, 1, 1).isleap() else 29


def shift_month(year, month, delta):
    n = year * 12 + month - 1 + delta
    y, m = n // 12, n % 12 + 1
    if not MIN_YEAR <= y <= MAX_YEAR:
        return year, month
    return y, m


@dataclass(frozen=True)
class Cell:
    day: date
    solar_day: int
    row: int
    column: int


def month_cells(year, month):
    first = gregorian(year, month, 1)
    offset = (first.weekday() + 2) % 7
    return [
        Cell(first + timedelta(days=i), i + 1, (offset + i) // 7, 6 - (offset + i) % 7)
        for i in range(month_length(year, month))
    ]


def civil_day(zone="Asia/Tehran", instant=None):
    instant = instant or datetime.now().astimezone()
    if instant.tzinfo is None:
        raise ValueError("An aware instant is required")
    return (instant.astimezone(ZoneInfo(zone)) if zone != "system" else instant.astimezone()).date()


class Clock:
    def __init__(self, zone="Asia/Tehran", now=None):
        self.zone, self.now, self.day = zone, now, None

    def reconcile(self):
        day = civil_day(self.zone, self.now() if self.now else None)
        changed = day != self.day
        self.day = day
        return changed
