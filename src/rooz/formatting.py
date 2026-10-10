from .calendar_service import jalali
from .i18n import GMONTHS, HMONTHS, JMONTHS, WEEKDAYS


def dates(day, loc, repo):
    j = jalali(day)
    h = repo.hijri(day)
    result = [
        loc.n(f"{j.day} {JMONTHS[loc.lang][j.month - 1]} {j.year}"),
        loc.n(f"{day.day} {GMONTHS[loc.lang][day.month - 1]} {day.year}"),
    ]
    if h:
        y, m, d = map(int, h.split("-"))
        result.append(loc.n(f"{d} {HMONTHS[loc.lang][m - 1]} {y}"))
    else:
        result.append(loc.t("hijri_unavailable"))
    return result


def full_date(day, loc, repo):
    return WEEKDAYS[loc.lang][day.weekday()] + "\n" + "\n".join(dates(day, loc, repo))
