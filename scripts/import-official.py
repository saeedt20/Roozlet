#!/usr/bin/python3
"""Reproducible offline extraction from UT's final 1405 PDF using Poppler.
Table vector boundaries prevent multiline occasions bleeding into adjacent dates.
No production calendar conversion is used to create the independent mapping.
"""

import hashlib, json, re, subprocess, tempfile, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/sources/Calendar-1405.pdf"
NS = {"h": "http://www.w3.org/1999/xhtml"}
BIDI = re.compile("[\u202a-\u202e\u2066-\u2069\f]")


def clean(s):
    return " ".join(BIDI.sub("", s).replace("ي", "ی").replace("ك", "ک").split())


def text(page, x, y, w, h):
    return clean(
        subprocess.check_output(
            [
                "pdftotext",
                "-f",
                str(page),
                "-l",
                str(page),
                "-x",
                str(round(x)),
                "-y",
                str(round(y)),
                "-W",
                str(round(w)),
                "-H",
                str(round(h)),
                "-r",
                "72",
                "-layout",
                str(SOURCE),
                "-",
            ]
        ).decode()
    )


def boundaries(page, work, max_x):
    svg = work / f"{page}.svg"
    subprocess.run(
        ["pdftocairo", "-f", str(page), "-l", str(page), "-svg", str(SOURCE), str(svg)], check=True
    )
    rects = []
    for d in re.findall(r'<path[^>]+d="([^"]+)"', svg.read_text()):
        pts = re.findall(r"[ML] ([\d.]+) ([\d.]+)", d)
        if not pts:
            continue
        xs = [float(x) for x, y in pts]
        ys = [float(y) for x, y in pts]
        if max(xs) - min(xs) > 200 and max(xs) < max_x and max(ys) - min(ys) < 2:
            rects.append((min(ys), min(xs), max(xs)))
    ys = []
    for y, x, r in sorted(rects):
        if not ys or y - ys[-1] > 2:
            ys.append(y)
    return ys, min(v[1] for v in rects), max(v[2] for v in rects)


HM = [
    "محرم",
    "صفر",
    "ربیع الاول",
    "ربیع الثانی",
    "جمادی الاولی",
    "جمادی الثانیه",
    "رجب",
    "شعبان",
    "رمضان",
    "شوال",
    "ذی القعده",
    "ذی الحجه",
]
GM = [
    "ژانویه",
    "فوریه",
    "مارس",
    "آوریل",
    "مه",
    "ژوئن",
    "ژوئیه",
    "اوت",
    "سپتامبر",
    "اکتبر",
    "نوامبر",
    "دسامبر",
]
JM = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]


def key(s):
    return re.sub(r"[^\w]", "", clean(s)).replace("اا", "ا")


HINDEX = {key(v): i + 1 for i, v in enumerate(HM)}
HINDEX.update(
    {
        "ربیالا ول": 3,
        "ربیالاول": 3,
        "ربیالول": 3,
        "جمادیالولی": 5,
        "جمادیالثانی": 6,
        "ربیالثانی": 4,
        "جمادیالاولی": 5,
        "جمادیالثانیه": 6,
        "ذیالقعده": 11,
        "ذیالحجه": 12,
    }
)
GIDX = {key(v): i + 1 for i, v in enumerate(GM)}


def month_index(s, idx):
    k = key(s)
    if k in idx:
        return idx[k]
    for v, n in idx.items():
        if k.replace("ال", "").replace("ی", "") == v.replace("ال", "").replace("ی", ""):
            return n
    raise ValueError(("Unknown month", s, k))


days = []
raw = []
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    bbox = work / "bbox.html"
    subprocess.run(["pdftotext", "-bbox-layout", str(SOURCE), str(bbox)], check=True)
    pages = ET.parse(bbox).findall(".//h:page", NS)
    for month in range(1, 13):
        pn = month + 2
        p = pages[pn - 1]
        words = p.findall(".//h:word", NS)
        ys, left, right = boundaries(pn, work, 330)
        solars = sorted(
            [w for w in words if 490 < float(w.attrib["xMin"]) < 510 and w.text.isdigit()],
            key=lambda w: float(w.attrib["yMin"]),
        )
        for sw in solars:
            sd = int(sw.text)
            y = float(sw.attrib["yMin"])
            low = max(v for v in ys if v < y)
            high = min(v for v in ys if v > y)

            def col(lo, hi):
                return sorted(
                    [
                        w
                        for w in words
                        if lo < float(w.attrib["xMin"]) < hi and low < float(w.attrib["yMin"]) < high
                    ],
                    key=lambda w: float(w.attrib["xMin"]),
                )

            gc = col(right, 380)
            hc = col(368, 448)
            gn = [int(w.text) for w in gc if w.text.isdigit()]
            hn = [int(w.text) for w in hc if w.text.isdigit()]
            gd = next(int(w.text) for w in gc if w.text.isdigit() and int(w.text) < 32)
            hd = next(
                int(w.text)
                for w in hc
                if w.text.isdigit() and int(w.text) < 32 and float(w.attrib["xMin"]) > 420
            )
            gy = next((n for n in gn if n > 1900), gy if days else 2026)
            hy = next((n for n in hn if 1000 < n < 1900), hy if days else 1447)
            gname = " ".join(
                w.text[::-1]
                for w in reversed(gc)
                if not w.text.isdigit() and w.text != '"' and float(w.attrib["xMin"]) < 367
            )
            hname = " ".join(
                w.text[::-1]
                for w in reversed(hc)
                if not w.text.isdigit() and w.text != '"' and float(w.attrib["xMin"]) > 385
            )
            if gname:
                gm = month_index(gname, GIDX)
            if hname:
                hm = month_index(hname, HINDEX)
            g = date(gy, gm, gd)
            j = f"1405-{month:02d}-{sd:02d}"
            h = f"{hy:04d}-{hm:02d}-{hd:02d}"
            title = text(pn, left + 1, low + 1, right - left - 2, high - low - 2)
            days.append(
                {"gregorian_date": g.isoformat(), "jalali_date": j, "hijri_date": h, "source_page": pn}
            )
            if title:
                raw.append({"jalali_date": j, "text": title, "source_page": pn, "appendix": False})
    for pn in (15, 16, 17):
        p = pages[pn - 1]
        words = p.findall(".//h:word", NS)
        ys, left, right = boundaries(pn, work, 500)
        for low, high in zip(ys, ys[1:]):
            ds = text(pn, right + 2, low + 1, 595 - right - 8, high - low - 2)
            if not ds or "فروردین" not in ds and not any(m in ds for m in JM):
                continue
            title = text(pn, left + 1, low + 1, right - left - 2, high - low - 2)
            m = next(i + 1 for i, n in enumerate(JM) if n in ds)
            match = re.match(r"(\d+)", ds) or re.search(r"(\d+)\s*مهر", ds)
            if not match:
                raise ValueError(("Appendix date", pn, ds))
            sd = int(match[1])
            raw.append(
                {"jalali_date": f"1405-{m:02d}-{sd:02d}", "text": title, "source_page": pn, "appendix": True}
            )
source = {
    "id": "ut-calendar-1405",
    "url": "https://calendar.ut.ac.ir/documents/2139738/7092644/Calendar-1405.pdf/64228cbb-f4de-dc32-4d2b-57db3c8e322f?t=1761972997587",
    "revision": "Final; approvals through 1404-07-22",
    "retrieved": "2026-10-10",
    "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
}
(ROOT / "tests/fixtures/official-1405-days.json").write_text(
    json.dumps({"source": source, "days": days}, ensure_ascii=False, indent=2) + "\n"
)
(ROOT / "docs/sources/1405-extracted-rows.json").write_text(
    json.dumps(raw, ensure_ascii=False, indent=2) + "\n"
)
print("Extracted", len(days), "independent date mappings and", len(raw), "occasion cells including appendix")
