"""Complete application catalog; does not require a system Persian locale."""

PAIRS = {
    "font_load_error": ("The bundled font could not be loaded.", "قلم همراه برنامه بارگذاری نشد."),
    "startup_error": ("Rooz could not start", "روز راه‌اندازی نشد"),
    "open": ("Open calendar", "باز کردن تقویم"),
    "today": ("Today", "امروز"),
    "settings": ("Settings", "تنظیمات"),
    "language": ("Language", "زبان"),
    "startup": ("Start at login", "اجرا هنگام ورود"),
    "theme": ("Theme", "پوسته"),
    "dark": ("Dark", "تیره"),
    "light": ("Light", "روشن"),
    "font": ("Font", "قلم"),
    "text_size": ("Text size", "اندازهٔ متن"),
    "digits": ("Digit style", "نوع ارقام"),
    "numerical_dates": ("Prefer numerical form of dates", "نمایش عددی تاریخ‌ها"),
    "numerical_help": (
        "Use year/month/day (2000/1/1) instead of 1 January 2000 in hover text and copied dates.",
        "در متن راهنما و تاریخ‌های کپی‌شده، سال/ماه/روز (۲۰۰۰/۱/۱) به‌جای ۱ ژانویهٔ ۲۰۰۰ نمایش داده می‌شود.",
    ),
    "copy_numeric": ("Copy numerical date", "کپی تاریخ عددی"),
    "copy_hijri": ("Copy Hijri date", "کپی تاریخ قمری"),
    "choose_month": ("Choose month", "انتخاب ماه"),
    "today_help": (
        "Click to return to today. Right-click to choose a month (Shift+F10 with keyboard focus).",
        "برای بازگشت به امروز کلیک کنید. برای انتخاب ماه راست‌کلیک کنید (با صفحه‌کلید: Shift+F10).",
    ),
    "persian": ("Persian", "فارسی"),
    "latin": ("Latin", "لاتین"),
    "opacity": ("Background opacity", "میزان کدری پس‌زمینه"),
    "scale": ("Widget scale", "اندازهٔ کارت"),
    "lock": ("Lock position", "قفل موقعیت"),
    "above": ("Always on top", "همیشه روی پنجره‌ها"),
    "reset_position": ("Reset position", "بازنشانی موقعیت"),
    "reset_appearance": ("Reset appearance", "بازنشانی ظاهر"),
    "copy_persian": ("Copy Persian date", "کپی تاریخ شمسی"),
    "copy_gregorian": ("Copy Gregorian date", "کپی تاریخ میلادی"),
    "copy_all": ("Copy all dates", "کپی همهٔ تاریخ‌ها"),
    "holiday": ("Public holiday", "تعطیل رسمی"),
    "unavailable": ("Occasion data unavailable", "اطلاعات مناسبت‌ها در دسترس نیست"),
    "incomplete": ("Occasion data is incomplete", "اطلاعات مناسبت‌ها کامل نیست"),
    "none": ("No occasions today", "امروز مناسبتی ثبت نشده"),
    "empty": ("No occasions on this day", "مناسبتی در این روز ثبت نشده"),
    "filtered": ("Occasions hidden by your filters", "مناسبت‌ها با فیلتر شما پنهان شده‌اند"),
    "quit": ("Quit", "خروج"),
    "close": ("Close", "بستن"),
    "appearance": ("Appearance", "ظاهر"),
    "dates": ("Language & dates", "زبان و تاریخ"),
    "events": ("Events", "مناسبت‌ها"),
    "desktop": ("Desktop & startup", "میزکار و راه‌اندازی"),
    "accent": ("Accent color", "رنگ تأکید"),
    "timezone": ("Timezone", "منطقهٔ زمانی"),
    "tehran": ("Tehran", "تهران"),
    "system": ("System default", "پیش‌فرض سیستم"),
    "custom": ("Custom installed font", "قلم نصب‌شدهٔ دلخواه"),
    "gregorian_cells": ("Gregorian day numbers", "روزهای میلادی در جدول"),
    "hijri_column": ("Hijri date column", "ستون تاریخ قمری"),
    "countdown": ("Next public holiday", "تعطیل رسمی بعدی"),
    "national": ("National", "ملی"),
    "cultural": ("Cultural", "فرهنگی"),
    "religious": ("Religious", "مذهبی"),
    "international": ("International", "جهانی"),
    "show_holidays": ("Show public holidays", "نمایش تعطیلات رسمی"),
    "all_workspaces": ("Show on all workspaces", "نمایش در همهٔ میزکارها"),
    "previous_month": ("Previous month", "ماه قبل"),
    "next_month": ("Next month", "ماه بعد"),
    "previous_year": ("Previous year", "سال قبل"),
    "next_year": ("Next year", "سال بعد"),
    "hijri_unavailable": ("Hijri unavailable", "تاریخ قمری در دسترس نیست"),
    "friday": ("Friday · weekly day off", "جمعه · تعطیلی هفتگی"),
    "coverage": (
        "Verified 1405 dates & holidays • Hijri only in 1405",
        "تاریخ‌ها و تعطیلات ۱۴۰۵ تأیید شده · قمری فقط در ۱۴۰۵",
    ),
    "startup_help": ("Install Rooz to enable login startup.", "برای اجرا هنگام ورود، روز را نصب کنید."),
    "zone_help": (
        "Controls the displayed day. Iranian holidays keep their original dates.",
        "روز نمایش‌داده‌شده را تعیین می‌کند. تاریخ تعطیلات ایران تغییر نمی‌کند.",
    ),
    "font_help": (
        "Larger text increases card height to keep dates readable.",
        "متن بزرگ‌تر، ارتفاع کارت را برای خوانایی تاریخ‌ها افزایش می‌دهد.",
    ),
    "fallback": (
        "Persian title; English translation unavailable",
        "عنوان فارسی؛ ترجمهٔ انگلیسی در دسترس نیست",
    ),
    "year_limit": ("Supported years: 1350–1450", "سال‌های پشتیبانی‌شده: ۱۳۵۰ تا ۱۴۵۰"),
    "no_next": ("Upcoming holidays beyond 1405 are not verified", "تعطیلات بعد از ۱۴۰۵ تأیید نشده‌اند"),
    "source_error": (
        "Using bundled data; invalid local data was ignored.",
        "دادهٔ محلی نامعتبر نادیده گرفته شد؛ دادهٔ همراه برنامه فعال است.",
    ),
    "recovered": ("Invalid settings were backed up and reset.", "تنظیمات نامعتبر پشتیبان‌گیری و بازنشانی شد."),
    "font_fallback": (
        "Selected font is unavailable; using Sans.",
        "قلم انتخاب‌شده موجود نیست؛ Sans فعال است.",
    ),
}
JMONTHS = {
    "en": "Farvardin Ordibehesht Khordad Tir Mordad Shahrivar Mehr Aban Azar Dey Bahman Esfand".split(),
    "fa": "فروردین اردیبهشت خرداد تیر مرداد شهریور مهر آبان آذر دی بهمن اسفند".split(),
}
GMONTHS = {
    "en": "January February March April May June July August September October November December".split(),
    "fa": "ژانویه فوریه مارس آوریل مه ژوئن ژوئیه اوت سپتامبر اکتبر نوامبر دسامبر".split(),
}
HMONTHS = {
    "en": [
        "Muharram",
        "Safar",
        "Rabi I",
        "Rabi II",
        "Jumada I",
        "Jumada II",
        "Rajab",
        "Shaban",
        "Ramadan",
        "Shawwal",
        "Dhu al-Qadah",
        "Dhu al-Hijjah",
    ],
    "fa": [
        "محرم",
        "صفر",
        "ربیع‌الاول",
        "ربیع‌الثانی",
        "جمادی‌الاول",
        "جمادی‌الثانی",
        "رجب",
        "شعبان",
        "رمضان",
        "شوال",
        "ذی‌القعده",
        "ذی‌الحجه",
    ],
}
WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "fa": ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"],
}
SHORT_WEEK = {
    "en": ["Fri", "Thu", "Wed", "Tue", "Mon", "Sun", "Sat"],
    "fa": ["جمعه", "پنجشنبه", "چهارشنبه", "سه‌شنبه", "دوشنبه", "یکشنبه", "شنبه"],
}


PAIRS.update({
    'style': ('Appearance style', 'سبک ظاهر'),
    'seasonal': ('Seasonal', 'فصلی'),
    'classic': ('Classic', 'ساده'),
    'season': ('Season', 'فصل'),
    'auto': ('Automatic season', 'انتخاب خودکار فصل'),
    'spring': ('Spring', 'بهار'),
    'summer': ('Summer', 'تابستان'),
    'autumn': ('Autumn', 'پاییز'),
    'winter': ('Winter', 'زمستان'),
    'accent_source': ('Accent source', 'رنگ تأکیدی'),
    'custom_accent': ('Custom accent', 'رنگ دلخواه'),
    'show_artwork': ('Scenic artwork', 'تصویر منظره'),
    'artwork_intensity': ('Artwork intensity', 'شدت تصویر زمینه'),
    'follow_month': ('Follow displayed month', 'ظاهر مطابق ماه نمایش\u200cداده\u200cشده'),
    'follow_help': ('Only the calendar follows the browsed month in automatic seasonal mode.', 'فقط در حالت فصلی خودکار، ظاهر تقویم با ماه نمایش\u200cداده\u200cشده تغییر می\u200cکند.'),
    'gregorian_column': ('Gregorian date in widget', 'نمایش تاریخ میلادی در ویجت'),
    'calendar': ('Calendar', 'تقویم'),
    'occasions': ('Occasions', 'مناسبت\u200cها'),
    'about': ('About', 'درباره'),
    'attribution': ('Artwork and data attribution', 'منابع تصاویر و تقویم'),
    'copied': ('Date copied', 'تاریخ کپی شد'),
})

class Localizer:
    def __init__(self, cfg):
        self.cfg = cfg

    @property
    def lang(self):
        return self.cfg["language"]

    def t(self, key):
        return PAIRS[key][self.lang == "fa"]

    def n(self, value):
        s = str(value).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        return (
            s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")) if self.cfg["digits"] == "persian" else s
        )

    def more(self, n):
        return self.n(n) + (
            " مناسبت دیگر" if self.lang == "fa" else " more event" if n == 1 else " more events"
        )

    def remaining(self, n):
        return self.n(n) + (
            " روز تا تعطیل رسمی"
            if self.lang == "fa"
            else " day to public holiday"
            if n == 1
            else " days to public holiday"
        )

    def event_title(self, e):
        if self.lang == "en" and not e["title"].get("en"):
            return self.n(e["title"]["fa"]) + " · " + self.t("fallback")
        return self.n(e["title"][self.lang])
