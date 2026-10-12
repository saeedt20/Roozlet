"""Complete application catalog; does not require a system Persian locale."""

PAIRS = {
    "search": ("Search", "جستجو"),
    "search_placeholder": ("Date, occasion or personal entry…", "تاریخ، مناسبت یا یادداشت…"),
    "search_help": ("Try 1405/7/20, 2026-10-12, 20 Mehr 1405, or words from an occasion or note. Enter opens the first result.", "مثال: ۱۴۰۵/۷/۲۰، 2026-10-12، ۲۰ مهر ۱۴۰۵ یا بخشی از مناسبت و یادداشت. Enter اولین نتیجه را باز می‌کند."),
    "search_coverage": ("Searches all loaded occasions, independently of filters, and your entries. Official annual coverage is 1405 only.", "در همهٔ مناسبت‌های بارگذاری‌شده، مستقل از فیلترها، و یادداشت‌های شما جستجو می‌شود. پوشش رسمی سالانه فقط ۱۴۰۵ است."),
    "search_results": ("results", "نتیجه"),
    "search_empty": ("No matching results. Try a different date or word.", "نتیجه‌ای پیدا نشد؛ تاریخ یا واژهٔ دیگری را امتحان کنید."),
    "search_limit": ("Showing the first 100; refine the search", "نمایش ۱۰۰ نتیجهٔ اول؛ جستجو را دقیق‌تر کنید"),
    "detect_date": ("Auto", "خودکار"),
    "date_calendar": ("Date calendar", "نوع تقویم تاریخ"),
    "shamsi": ("Shamsi", "شمسی"),
    "gregorian": ("Gregorian", "میلادی"),
    "go_to_date": ("Go to date", "رفتن به تاریخ"),
    "date": ("Date", "تاریخ"),
    "occasion_result": ("Occasion", "مناسبت"),
    "personal_result": ("Personal entry", "یادداشت شخصی"),
    "invalid_date": ("Enter a valid supported date, such as 1405/7/20 or 2026/10/12. Shamsi years: 1350–1450.", "تاریخ معتبر وارد کنید؛ مانند ۱۴۰۵/۷/۲۰ یا 2026/10/12. محدودهٔ سال شمسی: ۱۳۵۰ تا ۱۴۵۰."),
    "personal": ("Notes & reminders", "یادداشت و یادآور"),
    "new_entry": ("Add entry", "افزودن"),
    "edit_entry": ("Edit entry", "ویرایش یادداشت"),
    "entry_title": ("Title", "عنوان"),
    "entry_kind": ("Type", "نوع"),
    "entry_date": ("Date · year/month/day", "تاریخ · سال/ماه/روز"),
    "entry_body": ("Note", "متن یادداشت"),
    "note": ("Note", "یادداشت"),
    "birthday": ("Birthday", "تولد"),
    "appointment": ("Appointment", "قرار"),
    "task": ("Task", "کار روزانه"),
    "reminder_time": ("Time · 24-hour", "زمان · ۲۴ ساعته"),
    "tehran_time": ("Tehran time", "وقت تهران"),
    "system_time": ("System time", "وقت سیستم"),
    "repeat_annual": ("Repeat every Shamsi year", "تکرار هر سال شمسی"),
    "repeat_schedule": ("Repeat", "تکرار"),
    "no_repeat": ("Does not repeat", "بدون تکرار"),
    "repeat_daily": ("Repeat every day", "تکرار هر روز"),
    "repeat_weekly": ("Repeat every week", "تکرار هر هفته"),
    "repeat_help": ("For annual entries, Esfand 30 uses Esfand's last day in non-leap years. Completion applies to one occurrence.", "در تکرار سالانه، اسفند ۳۰ در سال غیرکبیسه به آخرین روز اسفند می‌رود. «انجام شد» فقط برای همان نوبت است."),
    "notify_entry": ("Notify me for this entry", "برای این یادداشت اعلان بده"),
    "desktop_notifications": ("Desktop notifications", "اعلان‌های میزکار"),
    "enable_notifications": ("Enable desktop notifications", "فعال‌کردن اعلان‌های میزکار"),
    "notifications_off": ("Desktop notifications are off. Enable them here or in Desktop & startup settings; each entry also has its own notification choice.", "اعلان‌های میزکار خاموش‌اند. از اینجا یا تنظیمات «میزکار و راه‌اندازی» فعال کنید؛ هر یادداشت هم انتخاب اعلان خودش را دارد."),
    "reminder_runtime": ("Reminders work while Roozlet is running. Start at login is optional. Missed alerts within the last 24 hours are checked on startup or resume; Checks run every 30 seconds; desktop delivery can take longer. Notifications follow the app timezone.", "یادآورها هنگام اجرای روزلت کار می‌کنند. اجرای هنگام ورود اختیاری است. اعلان‌های ازدست‌رفتهٔ ۲۴ ساعت اخیر هنگام اجرا یا بازگشت بررسی می‌شوند؛ بررسی هر ۳۰ ثانیه انجام می‌شود؛ زمان نمایش به سرویس میزکار هم وابسته است. منطقهٔ زمانی برنامه ملاک است."),
    "test_notification": ("Test notification", "آزمایش اعلان"),
    "reminder_runtime_short": ("Notifications require Roozlet to be running and use the app timezone.", "برای ارسال اعلان، روزلت باید در حال اجرا باشد. منطقهٔ زمانی برنامه ملاک است."),
    "test_notification_body": ("Roozlet desktop notifications are working.", "اعلان‌های میزکار روزلت کار می‌کنند."),
    "notification_sent": ("The desktop notification service accepted the alert.", "سرویس اعلان میزکار، اعلان را پذیرفت."),
    "notification_unavailable": ("The desktop notification service is unavailable. Your entries are saved; alerts will be retried while Roozlet runs.", "سرویس اعلان میزکار در دسترس نیست. یادداشت‌ها ذخیره‌اند؛ تا وقتی روزلت اجراست، ارسال دوباره امتحان می‌شود."),
    "personal_unavailable": ("Personal data could not be opened. The original file was kept. Restore your backup or check permissions, then restart Roozlet.", "اطلاعات شخصی باز نشد. فایل اصلی حفظ شده است. نسخهٔ پشتیبان یا دسترسی فایل را بررسی و روزلت را دوباره اجرا کنید."),
    "personal_save_error": ("Could not save personal data. Your draft is still here. Check available disk space and permissions.", "اطلاعات شخصی ذخیره نشد. متن واردشده حفظ شده است. فضای دیسک و دسترسی فایل را بررسی کنید."),
    "entry_limits": ("Enter a title; note text must be no more than 10,000 characters.", "عنوان وارد کنید؛ متن یادداشت باید حداکثر ۱۰٬۰۰۰ کاراکتر باشد."),
    "invalid_time": ("Enter a 24-hour time in HH:MM, such as 09:30.", "زمان را با قالب ۲۴ ساعتهٔ HH:MM وارد کنید؛ مانند ۰۹:۳۰."),
    "save": ("Save", "ذخیره"),
    "cancel": ("Cancel", "لغو"),
    "discard": ("Discard", "دور انداختن"),
    "unsaved_entry": ("You have unsaved changes. Keep editing, save, or choose Discard to close.", "تغییرات ذخیره نشده‌اند. ویرایش را ادامه دهید، ذخیره کنید یا برای بستن «دور انداختن» را بزنید."),
    "edit": ("Edit", "ویرایش"),
    "delete": ("Delete", "حذف"),
    "undo": ("Undo", "بازگردانی"),
    "entry_deleted": ("Entry deleted. You can undo this action.", "یادداشت حذف شد؛ می‌توانید آن را بازگردانید."),
    "done": ("Done", "انجام شد"),
    "selected_day": ("Selected day", "روز انتخاب‌شده"),
    "upcoming": ("Upcoming", "پیش رو"),
    "all_entries": ("All entries", "همهٔ یادداشت‌ها"),
    "personal_filter": ("Personal entry filter", "فیلتر یادداشت‌ها"),
    "personal_empty": ("No personal entries here yet. Add a note, birthday, appointment or task.", "هنوز یادداشتی در این بخش نیست. یادداشت، تولد، قرار یا کار روزانه اضافه کنید."),
    "personal_limit": ("More entries are saved. Use a narrower filter or Search to find them.", "یادداشت‌های بیشتری ذخیره شده‌اند؛ با فیلتر محدودتر یا جستجو آن‌ها را پیدا کنید."),
    "show_personal": ("Show personal entries", "نمایش یادداشت‌های شخصی"),
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
    "events": ("Occasions", "مناسبت‌ها"),
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
    'appearance_intro': ('Make Roozlet feel like home.', 'روزلت را به سلیقهٔ خود تنظیم کنید.'),
    'widget_preview': ('Live widget preview', 'پیش‌نمایش زندهٔ ویجت'),
    'season_help': ('Follow today’s Persian season.', 'ظاهر مطابق فصل فعلی تقویم شمسی تغییر می‌کند.'),
    'color_mode': ('Color mode', 'حالت نمایش'),
    'advanced': ('Advanced settings', 'تنظیمات پیشرفته'),
    'motion_effects': ('Subtle transitions', 'حرکت‌های ملایم'),
    'motion_help': ('Short fades; respects the system animation setting.', 'محو شدن کوتاه؛ مطابق تنظیمات حرکت سیستم.'),
    'copy_date': ('Copy date', 'کپی تاریخ'),
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
    'about_title': ('About Roozlet', 'دربارهٔ روزلت'),
    'credits': ('Credits', 'سازندگان'),
    'licenses': ('Licenses', 'مجوزها'),
    'version': ('Version', 'نسخه'),
    'about_summary': ('A compact offline Persian calendar for your Linux desktop.', 'تقویم شمسی کوچک و آفلاین برای میزکار لینوکس شما.'),
    'report_issue': ('Report an issue', 'گزارش مشکل'),
    'data_coverage': ('Calendar coverage', 'پوشش تقویم'),
    'about_coverage': ('Official Iranian occasions, holidays and Hijri dates cover 1405. Other years show coverage limits; lunar dates are not guessed.', 'مناسبت‌ها، تعطیلات و تاریخ‌های قمری رسمی ایران برای سال ۱۴۰۵ تأیید شده‌اند. در سال‌های دیگر محدودیت پوشش مشخص می‌شود و تاریخ قمری حدس زده نمی‌شود.'),
    'made_by': ('Made by Saeed Taheri', 'ساختهٔ سعید طاهری'),
    'created_by': ('Creator', 'سازنده'),
    'creator_credit': ('Saeed Taheri — original application code and documentation, MIT license.', 'سعید طاهری — کد اصلی برنامه و مستندات با مجوز MIT.'),
    'font_credit': ('Vazirmatn by Saber Rastikerdar — bundled unmodified fonts, SIL Open Font License 1.1.', 'وزیرمتن، اثر صابر راستی‌کردار — قلم‌های همراه برنامه بدون تغییر، با مجوز SIL OFL 1.1.'),
    'calendar_source': ('Calendar source', 'منبع تقویم'),
    'calendar_credit': ('University of Tehran Calendar Center — final official 1405 calendar, normalized dates and occasions. The original PDF is not redistributed.', 'مرکز تقویم مؤسسهٔ ژئوفیزیک دانشگاه تهران — تقویم رسمی نهایی ۱۴۰۵، منبع تاریخ‌ها و مناسبت‌ها. فایل PDF اصلی بازنشر نشده است.'),
    'date_libraries': ('Date libraries', 'کتابخانه‌های تاریخ'),
    'libraries_credit': ('jdatetime 5.2.0 by Milad Rastian (PSF); jalali-core 1.0.0 by Roozbeh Pournader, Mohammad Toossi and Parspooyesh Fanavar (LGPL 2.1+). Bundled source retains its original licenses.', '⁨jdatetime 5.2.0⁩ اثر میلاد راستیان با مجوز PSF؛ ⁨jalali-core 1.0.0⁩ اثر روزبه پورنادر، محمد طوسی و پارس‌پویش فناور با مجوز LGPL 2.1+. سورس همراه برنامه مجوزهای اصلی خود را حفظ می‌کند.'),
    'seasonal_artwork': ('Seasonal artwork', 'تصاویر چهار فصل'),
    'artwork_credit': ('Four original mountain-and-lake scenes were created for Roozlet with OpenAI image generation on 2026-10-11. They depict imaginary scenery, not photographs of a real location. No stock images or reference UI screenshots were incorporated. Distributed by Saeed Taheri under the project MIT license.', 'چهار منظرهٔ اختصاصی کوهستان و دریاچه در ۲۰۲۶/۱۰/۱۱ با ابزار تولید تصویر OpenAI برای روزلت ساخته شدند. مناظر خیالی‌اند و عکس مکان واقعی نیستند. هیچ تصویر آماده یا عکس مرجع رابط کاربری در آن‌ها استفاده نشده است. سعید طاهری این تصاویر را با مجوز MIT پروژه منتشر می‌کند.'),
    'native_toolkit': ('Native desktop tools', 'ابزارهای بومی میزکار'),
    'toolkit_credit': ('GTK, PyGObject, Cairo, Pango, Fontconfig and timezone data are system dependencies and retain their own licenses.', 'GTK، PyGObject، Cairo، Pango، Fontconfig و داده‌های منطقهٔ زمانی وابستگی‌های سیستم‌اند و مجوزهای خود را حفظ می‌کنند.'),
    'license_help': ('Original license texts are available offline. Each bundled component retains its own license.', 'متن اصلی مجوزها به‌صورت آفلاین در دسترس است. هر جزء همراه برنامه مجوز خودش را حفظ می‌کند.'),
    'license_text': ('Original license text', 'متن اصلی مجوز'),
    'license_unavailable': ('This license file is unavailable. See THIRD_PARTY_NOTICES.md in the project on GitHub.', 'فایل این مجوز در دسترس نیست. به THIRD_PARTY_NOTICES.md در پروژهٔ GitHub مراجعه کنید.'),
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
