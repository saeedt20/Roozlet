# Calendar data provenance and coverage

Rooz 0.1.0 ships **1405.1**, one verified annual package for Solar Hijri 1405:
2026-03-21 through 2027-03-20 inclusive. There are 365 daily mappings, 305 occasion
records derived from 282 source table cells, and 26 distinct statutory holiday
dates. Coincident holidays produce multiple records without double-counting days.

The primary source is the University of Tehran Calendar Center's **final 1405
calendar**, including approvals through 1404-07-22, retrieved 2026-10-10:
https://calendar.ut.ac.ir/documents/2139738/7092644/Calendar-1405.pdf/64228cbb-f4de-dc32-4d2b-57db3c8e322f?t=1761972997587
The exact downloaded PDF SHA-256 is in the source manifest and golden fixture.
The original PDF is retained locally for review, ignored by Git and excluded
from the .deb and source release. A gateway JavaScript cookie challenge was
resolved before obtaining the actual 17-page PDF; no HTML error page was used.

## Verification

* Gregorian, Persian and Iranian Hijri columns were extracted independently for
  **every day**, with explicit month/year changes and ditto marks resolved.
  Production jdatetime was not used to generate those expected mappings.
* Vector table boundaries from Poppler SVG constrain each extraction cell.
  This avoids assigning wrapped event lines to neighboring dates.
* All 189 nonempty main-table occasion cells and 93 appendix cells are represented.
  The second Friday of Mehr appendix entry is fixed to 1405-07-10 as printed.
* Every `(تعطیل)` marking and the separately stated Eid al-Fitr follow-up holiday
  was reviewed. Friday status is computed separately from these holiday flags.
* All holiday cells are decomposed explicitly. Ordinary coincident occasions do
  not become holidays. Nowruz and Eid al-Fitr on Farvardin 1, and Ghadir and
  Khomeini's death on Khordad 14, are preserved as separate holiday records.
* Known PDF text extraction defects (Arabic Yeh/Kaf, lam-alef order, omitted
  half-spaces and distorted text in several rows) have reviewed normalization
  rules in `scripts/normalize-data.py`. Full extracted audit rows are retained.
* Continuous dates, complete year membership, conversion agreement, unique dates
  and events, valid source references, bilingual title structure and holiday
  types are checked by `scripts/validate-data.py`. Independent golden tests cover
  all 365 days, lunar month transitions, all 26 holiday dates and coincident events.

Some ordinary coincident occasions stay together in a single record containing
all titles. The English catalog has 190 reviewed concise translations. The other
115 records retain Persian titles and show an explicit English fallback label.
The interface itself is fully bilingual. No invented translations are supplied.

## Three distinct ranges

| Feature | Coverage |
| --- | --- |
| Jalali/Gregorian conversion and browsing | 1350–1450, every day round-trip tested |
| Official Iranian Hijri display | 1405 only, every day checked against source |
| Official occasions and statutory holidays | 1405 only, main and appendix tables |

Round-trip testing is an algorithmic consistency check outside 1405, not an
independent astronomical certification of every historical or future year.
Outside the official annual mapping, Rooz displays Hijri unavailable and an
explicit missing-event-coverage message. It does not extrapolate lunar holidays.
The countdown includes a holiday today (0 days), excludes ordinary Fridays, and
stops with an explicit limitation at the next unsupported date.

## Update procedure

1. Obtain the final annual source directly from the Calendar Center; preserve its
   URL, revision, retrieval date and checksum. Do not use a generic lunar algorithm.
2. Save the source locally, inspect rendered pages, and adapt the offline Poppler
   importer to that year's actual table geometry. For 1405:
   `python3 scripts/import-official.py`.
3. Review date columns, event cells, holiday markings and extraction defects;
   update normalizations/translations: `python3 scripts/normalize-data.py`.
4. Add independent expectations, validate every day, verify English fallback and
   category/holiday distinctions, and run the complete test suite.
5. Update package checksum in `data/calendars/manifest.json`, data version and app
   release notes; distribute through a reviewed app release.

User JSON packages can be placed in `$XDG_DATA_HOME/rooz/calendars`. Invalid files
are ignored with a reported error while bundled data remains active. They cannot
replace the bundled 1405 package or acquire official verified status by declaring
`verified` in JSON. New user years remain untrusted, with no authoritative lunar
display or holiday countdown. No runtime scraping or network update occurs.

Annual date and occasion facts are normalized for this app with attribution.
No general license to the University PDF, website or editorial content is claimed.
See THIRD_PARTY_NOTICES.md before public release.

## Additional leap-year verification

The Calendar Center's long-range leap-year table (1206–1498), retrieved 2026-10-10,
provides star-marked leap flags that agree with Rooz for all **101 years 1350–1450**.
Independent flags, exact URL and PDF checksum are retained in
`tests/fixtures/official-leap-years-1350-1450.json`.
https://calendar.ut.ac.ir/documents/2139738/7092644/Kabise%2BShamsi%2B1206-1498.pdf/fbc45bf4-df46-c298-381c-2bff2c57f0e0?t=1719740029743

That long-range document's printed Gregorian year-start dates conflict with the
final annual 1405 calendar (it prints March 20 for 1405; the final annual table
prints March 21). Rooz does not adopt those Gregorian date columns. The newer,
final annual document is authoritative for the verified year; its preceding
year-end and the leap flags independently constrain the tested 1403/1404 transition.
Future Gregorian year-start dates outside annual coverage remain algorithmic,
with the round-trip limitation stated above. No unexplained correction is applied.
