# Third-party materials

* **jdatetime 5.2.0** — Milad Rastian, PSF license. Unmodified pure-Python source
  from https://github.com/slashmili/jdatetime/tree/v5.2.0 is included in
  `src/rooz/_vendor/jdatetime/`. Its original LICENSE and the PSF license text
  accompany the library. This version supports Python >=3.9 and has one required
  dependency, jalali-core. Rooz does not use its optional greenlet integration.
* **jalali-core 1.0.0** — Roozbeh Pournader, Mohammad Toossi and Parspooyesh
  Fanavar, LGPL 2.1 or later. Complete unmodified source and LGPL text in
  `src/rooz/_vendor/`. Upstream: https://github.com/slashmili/jalali-core/tree/v1.0.0.
  Python source remains replaceable, including in the installed private directory.
* **Vazirmatn 33.003** — Saber Rastikerdar, SIL OFL 1.1. Regular, Medium and
  SemiBold static TTFs are unmodified standard Latin/Persian fonts. Font license:
  `data/fonts/vazirmatn/OFL.txt`. https://github.com/rastikerdar/vazirmatn/tree/v33.003.
* **Iranian calendar facts** — University of Tehran Calendar Center, final 1405
  annual calendar. Rooz distributes normalized date/occasion facts and its own
  concise translations, not a copy of the PDF or a license to the website.
  Exact source, revision, checksum, extraction repairs and coverage are recorded
  in `docs/DATA_SOURCES.md` and the annual JSON. No community event repository
  was incorporated; it was inspected and rejected because it conflated Fridays
  with statutory holidays and omitted coincident religious occasions.
* GTK, PyGObject, Cairo, Pango, Fontconfig and timezone data are system packages,
  declared as Debian dependencies. They are not copied into Rooz.

Original application code and documentation are MIT licensed, copyright
2026 Saeed Taheri; see `LICENSE`. The materials above retain their own licenses
and attribution; the MIT license does not relicense them.

## Original seasonal artwork

The four seasonal landscapes were generated specifically for Roozlet with OpenAI image generation on 2026-10-11 and are distributed by the owner under the project MIT license. They are imagined scenery, not stock photographs of an identified place. Provenance and SHA-256 checksums are in `data/themes/seasons/ATTRIBUTION.md` and `manifest.json`. No reference UI screenshots are embedded in the scenes.
