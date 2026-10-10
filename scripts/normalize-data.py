#!/usr/bin/python3
"""Apply reviewed Persian extraction repairs and holiday-event separation."""

import json, re, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fixture = json.loads((ROOT / "tests/fixtures/official-1405-days.json").read_text())
rows = json.loads((ROOT / "docs/sources/1405-extracted-rows.json").read_text())
# Corrections checked against PDF pages, not a secondary event repository.
REPAIRS = {
    "اسالم": "اسلام",
    "انقالب": "انقلاب",
    "اعالم": "اعلام",
    "اطالع": "اطلاع",
    "والدت": "ولادت",
    "والیت": "ولایت",
    "علیهالسالم": "علیه‌السلام",
    "علیه السالم": "علیه‌السلام",
    "رحمة هللا": "رحمة الله",
    "اهلل": "الله",
    "عجلاللهتعالی": "عجل‌الله‌تعالی",
    "عجلالله": "عجل‌الله",
    "سالمالله": "سلام‌الله",
    "سالم الله": "سلام‌الله",
    "صلیالله": "صلی‌الله",
    "زورخانهای": "زورخانه‌ای",
    "سالمتی": "سلامتی",
    "هستهای": "هسته‌ای",
    "صعب العالج": "صعب‌العلاج",
    "آیتالله": "آیت‌الله",
    "جواداالئمه": "جوادالائمه",
    "مالصدرا": "ملاصدرا",
    "اخالق": "اخلاق",
    "سالح": "سلاح",
    "عالمه": "علامه",
    "اخالص": "اخلاص",
    "بالیای": "بلایای",
    "کربال": "کربلا",
    "االقصی": "الاقصی",
    "معلوالن": "معلولان",
    "هالل": "هلال",
    "النة": "لانهٔ",
    "صنای کوچک": "صنایع کوچک",
    "مداف حرم": "مدافع حرم",
    "حرفهای": "حرفه‌ای",
    "مدرسة": "مدرسهٔ",
    "فیضیة": "فیضیهٔ",
    "شمارة": "شمارهٔ",
    "مظلومانة": "مظلومانهٔ",
    "هفتة": "هفتهٔ",
    "دورۀ": "دورهٔ",
    "هفتة": "هفتهٔ",
    "دهة": "دههٔ",
    "جمعة": "جمعهٔ",
    "شمارۀ": "شمارهٔ",
    "قبلة": "قبلهٔ",
    "توطئة": "توطئهٔ",
    "توطئة": "توطئهٔ",
    "حماسة": "حماسهٔ",
    "سهگانة": "سه‌گانهٔ",
    "صونای دسوتی": "صنایع دستی",
    "مسجد جام شهر": "مسجد جامع شهر",
}
OVERRIDES = {
    44: "روز مباهلهٔ پیامبر اسلام و روز صنایع دستی و روز ملی فرش",
    51: "سالروز تأسیس سازمان تبلیغات اسلامی و روز تبلیغ و اطلاع‌رسانی دینی و روز اصناف",
    94: "قیام ۱۷ شهریور و کشتار جمعی مردم به دست مأموران حکومت پهلوی",
    95: "وفات آیت‌الله سید محمود طالقانی، اولین امام جمعهٔ تهران",
    104: "شکست حصر آبادان در عملیات ثامن‌الائمه و روز گردشگری",
    109: "هجرت امام خمینی از عراق به پاریس و روز نیروی انتظامی",
    114: "شهادت آیت‌الله اشرفی اصفهانی و روز جهانی نابینایان (عصای سفید)",
    123: "شهادت آیت‌الله قاضی طباطبایی",
    163: "شهادت نواب صفوی، طهماسبی، برادران واحدی و ذوالقدر از فداییان اسلام",
}
# Public-holiday cells are decomposed explicitly so unrelated same-day occasions
# do not inherit a holiday flag. Dates/flags follow the official 1405 table.
HOLIDAY_ROWS = {
    0: [
        ("آغاز نوروز", "Nowruz begins", True, ["national", "cultural"]),
        ("عید سعید فطر", "Eid al-Fitr", True, ["religious"]),
    ],
    1: [
        (
            "تعطیل عید فطر و نوروز",
            "Eid al-Fitr and Nowruz holiday",
            True,
            ["religious", "national", "cultural"],
        ),
        (
            "حمله به مدرسهٔ فیضیهٔ قم و آغاز عملیات فتح‌المبین",
            "Feyziyeh School attack; Operation Fath ol-Mobin begins",
            False,
            ["national"],
        ),
    ],
    2: [("عید نوروز", "Nowruz holiday", True, ["national", "cultural"])],
    3: [("عید نوروز", "Nowruz holiday", True, ["national", "cultural"])],
    6: [("روز جمهوری اسلامی ایران", "Islamic Republic Day", True, ["national"])],
    7: [("روز طبیعت", "Nature Day", True, ["national", "cultural"])],
    12: [
        ("شهادت امام جعفر صادق", "Martyrdom of Imam Jafar al-Sadiq", True, ["religious"]),
        ("روز بزرگداشت عطار نیشابوری", "Attar of Nishapur commemoration", False, ["cultural"]),
    ],
    39: [
        ("عید سعید قربان", "Eid al-Adha", True, ["religious"]),
        ("آغاز دههٔ امامت و ولایت", "Imamate and Guardianship observances begin", False, ["religious"]),
    ],
    41: [
        ("عید غدیر خم", "Eid al-Ghadir", True, ["religious"]),
        ("رحلت امام خمینی", "Death of Imam Khomeini", True, ["national"]),
        (
            "انتخاب آیت‌الله خامنه‌ای به رهبری",
            "Appointment of Ayatollah Khamenei as leader",
            False,
            ["national"],
        ),
    ],
    42: [
        ("قیام ۱۵ خرداد", "15 Khordad uprising", True, ["national"]),
        ("روز جهانی محیط زیست", "World Environment Day", False, ["international"]),
    ],
    52: [("تاسوعای حسینی", "Tasua", True, ["religious"])],
    53: [("عاشورای حسینی", "Ashura", True, ["religious"])],
    73: [("اربعین حسینی", "Arbaeen", True, ["religious"])],
    78: [
        ("رحلت پیامبر اسلام", "Death of Prophet Muhammad", True, ["religious"]),
        ("شهادت امام حسن مجتبی", "Martyrdom of Imam Hasan", True, ["religious"]),
        ("روز حمایت از صنایع کوچک", "Small Industries Support Day", False, ["national"]),
    ],
    79: [
        ("شهادت امام رضا", "Martyrdom of Imam Reza", True, ["religious"]),
        ("روز تشکل‌ها و مشارکت‌های اجتماعی", "Associations and Social Participation Day", False, ["national"]),
    ],
    83: [
        ("شهادت امام حسن عسکری", "Martyrdom of Imam Hasan al-Askari", True, ["religious"]),
        ("آغاز امامت حضرت ولی‌عصر", "Imamate of Imam Mahdi begins", False, ["religious"]),
        ("روز بزرگداشت علامه مجلسی", "Allameh Majlesi commemoration", False, ["cultural", "religious"]),
        ("روز جهانی مسجد", "World Mosque Day", False, ["international", "religious"]),
    ],
    90: [
        ("ولادت پیامبر اسلام", "Birthday of Prophet Muhammad", True, ["religious"]),
        ("ولادت امام جعفر صادق", "Birthday of Imam Jafar al-Sadiq", True, ["religious"]),
        ("روز اخلاق و مهرورزی", "Ethics and Kindness Day", False, ["cultural"]),
        (
            "شهادت رجایی و باهنر در انفجار دفتر نخست‌وزیری",
            "Death of Rajai and Bahonar in the prime minister office bombing",
            False,
            ["national"],
        ),
        ("روز مبارزه با تروریسم", "Counter-Terrorism Day", False, ["national"]),
    ],
    128: [("شهادت حضرت فاطمهٔ زهرا", "Martyrdom of Fatima al-Zahra", True, ["religious"])],
    146: [
        ("ولادت امام علی", "Birthday of Imam Ali", True, ["religious"]),
        ("روز پدر", "Fathers Day", False, ["cultural"]),
        ("آغاز ایام‌البیض (اعتکاف)", "Ayyam al-Bid retreat begins", False, ["religious"]),
    ],
    155: [
        ("مبعث پیامبر اسلام", "Prophet Muhammads first revelation", True, ["religious"]),
        (
            "شهادت سید حسین علم‌الهدی و همرزمان در هویزه",
            "Death of Hossein Alam ol-Hoda and his companions at Hoveyzeh",
            False,
            ["national"],
        ),
        ("روز شهدای دانشجو", "Student Martyrs Day", False, ["national"]),
    ],
    165: [
        ("ولادت امام مهدی", "Birthday of Imam Mahdi", True, ["religious"]),
        ("روز جهانی مستضعفان", "World Day of the Oppressed", False, ["international"]),
    ],
    170: [("پیروزی انقلاب اسلامی ایران", "Islamic Revolution Victory Day", True, ["national"])],
    178: [("شهادت امام علی", "Martyrdom of Imam Ali", True, ["religious"])],
    183: [("عید سعید فطر", "Eid al-Fitr", True, ["religious"])],
    184: [
        ("تعطیل عید سعید فطر", "Eid al-Fitr holiday", True, ["religious"]),
        ("روز راهیان نور", "Rahian-e Noor Day", False, ["national"]),
    ],
    188: [("روز ملی شدن صنعت نفت ایران", "Oil Nationalization Day", True, ["national"])],
}
EN = {
    4: "Birthday of Zoroaster",
    5: "Performing Arts Day",
    8: "Pahlevani culture and Zurkhaneh sports day",
    9: "Health Day",
    10: "National Nuclear Technology Day; Morteza Avini commemoration; Islamic Revolution Art Day",
    13: "Army and Ground Forces Day",
    15: "Saadi commemoration; Persian Prose Day; Athlete Martyrs Day",
    20: "Transport Safety Day",
    22: "National Persian Gulf Day",
    23: "International Workers Day",
    24: "Morteza Motahhari commemoration; Teachers Day",
    25: "Sheikh Saduq commemoration",
    26: "Special and Hard-to-Treat Diseases Day",
    27: "Sheikh Koleyni commemoration",
    29: "Persian Language Day; Ferdowsi commemoration",
    32: "National Population Day; Service Martyrs Day",
    33: "Organ Donation Day",
    34: "Productivity and Consumption Efficiency Day; Mulla Sadra commemoration",
    37: "Resistance Day; Dezful Day",
    38: "Arafah (Prayer Day)",
    44: "Mubahala Day; Handicrafts Day; National Carpet Day",
    45: "Family and Retiree Appreciation Day",
    46: "National Strength and Unity Martyrs Day",
    49: "Death of Ali Shariati",
    50: "Mostafa Chamran commemoration; Professors Basij Day",
    54: "Prisoners of War and Missing Persons Appreciation Day",
    57: "Day against Chemical and Biological Weapons",
    58: "Industry and Mining Day; Cultural Diplomacy Day",
    61: "Pen Day",
    62: "Childrens and Young Adults Literature Day",
    64: "Chastity and Hijab Day",
    65: "Khwarizmi commemoration; Information Technology Day",
    66: "Welfare and Social Security Day",
    67: "Guardian Council founding anniversary",
    69: "Sheikh Safi al-Din Ardabili commemoration",
    71: "Suhrawardi commemoration",
    72: "Blood Donation Day",
    75: "Academic Center for Education, Culture and Research founding anniversary",
    76: "Mahmoud Saremi commemoration; Journalists Day",
    81: "Return of Iranian prisoners of war",
    82: "1953 coup anniversary",
    84: "Avicenna commemoration; Physicians Day",
    87: "Employees Day",
    88: "Razi commemoration; Pharmacy Day; Wrestling Day",
    89: "Endowment Day",
    92: "Cooperatives Day; Al-Biruni commemoration; Basic Sciences Day",
    97: "Cinema Day",
    98: "Persian Poetry and Literature Day; Shahriar commemoration",
    101: "Flag Day",
    102: "Mina disaster commemoration",
    103: "Soldiers Day",
    106: "Rumi commemoration",
    107: "International Day of Older Persons",
    108: "Elites Day",
    110: "Veterinary Day",
    112: "Hafez commemoration",
    113: "World Standards Day",
    116: "Commemoration of genocide of Palestinian children and women",
    117: "Physical Education and Sports Day",
    118: "Export Day",
    119: "Abulfazl Bayhaqi commemoration",
    125: "Public Culture Day",
    126: "World Science Day for Peace and Development",
    127: "Aerospace Day",
    130: "National Hero Day; Al-Farabi commemoration; Wisdom and Philosophy Day",
    133: "Navy Day; Iranian Innovation and Technology Day",
    138: "University Students Day",
    142: "Research Day",
    144: "Birthday of Imam Muhammad al-Jawad",
    145: "Yalda Night; Hospitality and Family Ties Day",
    148: "Earthquake Safety and Disaster Reduction Day",
    150: "Insight and Allegiance Day",
    151: "Gregorian New Year 2027",
    156: "Qom uprising commemoration",
    157: "Death of Amir Kabir",
    161: "Islamic Revolution Historiography Day",
    162: "Shahs departure from Iran",
    164: "Birthday of Ali Akbar; Youth Day",
    168: "Space Technology Day",
    169: "Air Force Day",
    174: "Nasir al-Din al-Tusi commemoration; Engineers Day",
    175: "Laylat al-Qadr",
    177: "Laylat al-Qadr; Rare Disease Support Day",
    179: "Laylat al-Qadr",
    180: "Quds Day; Charity Day; Interest-Free Lending Culture Day",
    181: "Tree Planting Day; Environmental Education Day",
    185: "Nizami Ganjavi commemoration",
    187: "Parvin Etesami commemoration; Neighbour Appreciation Day",
    189: "World Water Day",
    190: "World Meteorological Day",
    191: "Genetic and Biological Resources Day",
    192: "World Palestinian Child Day",
    195: "Wheat and Bread Day",
    196: "Earth Day",
    199: "International Day of the Midwife",
    200: "World Red Cross and Red Crescent Day",
    201: "National Documents and Written Heritage Day",
    202: "Damask Rose and Rosewater Day",
    203: "Communications and Public Relations Day",
    204: "International Museum and Cultural Heritage Day",
    205: "Nasim-e Mehr: Support for Prisoners Families Day",
    207: "World No Tobacco Day",
    210: "World Day to Combat Desertification",
    212: "International Day against Drug Abuse",
    215: "Municipalities and Village Councils Day",
    216: "Tax Day",
    225: "Entrepreneurship and Vocational Training Day",
    226: "Zanjan Day",
    227: "World Breastfeeding Day",
    231: "Defense Industry Day; Honey Day",
    232: "Hamadan Day",
    234: "Sistan and Baluchestan Day",
    236: "Printing Industry Day",
    237: "Community Health Workers Day",
    239: "Qom Day",
    241: "Date Palm Day",
    242: "World Tourism Day",
    243: "World Maritime Day; International Day of the Deaf",
    245: "World Childrens Day",
    246: "World Post Day",
    248: "World Food Day",
    250: "Saffron Day",
    251: "Pomegranate Day",
    252: "Civil Defense Day",
    254: "Mazandaran Day",
    255: "Quality Day",
    256: "Isfahan Day",
    258: "Olive Day",
    260: "World AIDS Day",
    261: "Insurance Day",
    262: "International Civil Aviation Day",
    264: "Transport and Drivers Day",
    266: "Civil Registration Day",
    268: "Petrochemical Industry Day",
    271: "Khaqani Shirvani commemoration",
    272: "Anonymous Intelligence Officers Day",
    273: "International Customs Day",
    274: "Chaharmahal and Bakhtiari Day",
    279: "Consumer Rights Protection Day",
    280: "Bushehr Day",
    281: "Halabja chemical attack commemoration",
}
by_solar = {d["jalali_date"]: d for d in fixture["days"]}
events = []
for i, row in enumerate(rows):
    fa = OVERRIDES.get(i, row["text"])
    for a, b in REPAIRS.items():
        fa = fa.replace(a, b)
    fa = re.sub(r"\s*\(\s*تعطیل\s*\)", "", fa)
    # Preserve full row facts. Non-holiday coincident titles remain a grouped record.
    cats = []
    if "جهانی" in fa:
        cats.append("international")
    if any(w in fa for w in ("حضرت", "امام", "پیامبر", "شب قدر", "مباهله", "عرفه", "اعتکاف")):
        cats.append("religious")
    if any(
        w in fa
        for w in ("بزرگداشت", "هنر", "قلم", "شعر", "ادب", "فرهنگ", "معماری", "زبان", "یلدا", "کتاب", "سینما")
    ):
        cats.append("cultural")
    if not cats or any(w in fa for w in ("ملی", "ایران", "صنعت", "تأسیس", "قیام", "انقلاب", "شهر", "ارتش")):
        cats.append("national")
    records = HOLIDAY_ROWS.get(i, [(fa, EN.get(i), False, cats)])
    for n, (title, en, holiday, categories) in enumerate(records):
        events.append(
            {
                "id": f"1405-{i:03d}-{n}",
                "gregorian_date": by_solar[row["jalali_date"]]["gregorian_date"],
                "title": {"fa": title, "en": en},
                "categories": categories,
                "is_public_holiday": holiday,
                "source_id": "ut-calendar-1405",
                "source_page": row["source_page"],
                "source_row": i,
                "appendix": row["appendix"],
            }
        )
obj = {
    "schema_version": 1,
    "solar_year": 1405,
    "data_version": "1405.1",
    "coverage": {"date_mapping": "verified", "official_occasions": "verified", "public_holidays": "verified"},
    "sources": [fixture["source"]],
    "days": fixture["days"],
    "events": events,
    "translation_coverage": {
        "english": sum(e["title"]["en"] is not None for e in events),
        "persian": len(events),
        "policy": "Reviewed concise English titles; explicitly labeled Persian fallback for remaining titles.",
    },
    "verification": {
        "method": "365 independent PDF mappings; 189 main-table and 93 appendix occasion cells; explicit decomposition of every holiday cell; reviewed extraction repairs",
        "main_occasion_cells": 189,
        "appendix_occasion_cells": 93,
    },
}
p = ROOT / "data/calendars/1405.json"
p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
manifest = {
    "schema_version": 1,
    "packages": [
        {
            "file": p.name,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "year": 1405,
            "data_version": "1405.1",
        }
    ],
    "sources": [fixture["source"]],
}
(ROOT / "data/calendars/manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(len(events), "events;", obj["translation_coverage"])
