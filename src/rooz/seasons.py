"""Pure Solar Hijri seasonal appearance decisions; no GTK or network dependency."""

SEASONS = ("spring", "summer", "autumn", "winter")
ACCENTS = {
    "dark": dict(zip(SEASONS, ("#E99ABB", "#E6C45C", "#F2A15B", "#82C8F4"))),
    "light": dict(zip(SEASONS, ("#A63B69", "#805E0C", "#A34D15", "#216995"))),
}


def season_for_month(month):
    if type(month) is not int or not 1 <= month <= 12:
        raise ValueError("A Jalali month from 1 to 12 is required")
    return SEASONS[(month - 1) // 3]


def effective_season(cfg, today, viewed_month=None):
    from .calendar_service import jalali

    appearance = cfg["appearance"]
    chosen = appearance.get("season", "auto")
    if chosen in SEASONS:
        return chosen
    month = jalali(today).month
    if (appearance.get("style") == "seasonal"
            and appearance.get("calendar_follow_viewed_month") and viewed_month is not None):
        month = viewed_month
    return season_for_month(month)
