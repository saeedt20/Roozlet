from .calendar_service import jalali
from .i18n import GMONTHS, HMONTHS, JMONTHS, WEEKDAYS


def dates(day, loc, repo, numerical=None):
    """Format dates consistently for tooltips, details and clipboard actions."""
    if numerical is None:
        numerical = loc.cfg.get("calendar", {}).get("prefer_numerical_dates", False)

    def formatted(year, month, day_number, names):
        value = (
            f"{year}/{month}/{day_number}"
            if numerical
            else f"{day_number} {names[month - 1]} {year}"
        )
        return loc.n(value)

    j = jalali(day)
    h = repo.hijri(day)
    result = [
        formatted(j.year, j.month, j.day, JMONTHS[loc.lang]),
        formatted(day.year, day.month, day.day, GMONTHS[loc.lang]),
    ]
    if h:
        y, m, d = map(int, h.split("-"))
        result.append(formatted(y, m, d, HMONTHS[loc.lang]))
    else:
        result.append(loc.t("hijri_unavailable"))
    return result


def full_date(day, loc, repo, numerical=None):
    return WEEKDAYS[loc.lang][day.weekday()] + "\n" + "\n".join(dates(day, loc, repo, numerical))
