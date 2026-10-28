# Changelog

## 0.4.2 — 2026-10-28

- Archive only tracked release files; exclude symbolic links and private database files.
- Ignore malformed annual imports while keeping bundled calendar data available.
- Report reminder storage failures, recover alerts across daylight-saving changes, and retain future annual entries in Upcoming.
- Read personal occurrence states once per day instead of once per entry.
- Measure usable content width for compact navigation, scroll navigation and search help on short screens, and synchronize retained Settings controls.
- Update desktop and extracted-package checks for current branding, card size and embedded navigation.

## 0.4.0 — 2026-10-12

- Offline Shamsi/Gregorian date, bilingual occasion and personal-entry search with digit/letter normalization and direct month jumps.
- Private notes, birthdays, appointments and tasks with explicit save, editing, per-occurrence completion and reversible deletion.
- One-time/daily/weekly/Shamsi-yearly recurrence and documented Esfand leap-day handling.
- Opt-in asynchronous desktop notifications, 24-hour catch-up, bounded batches, failure retry and durable delivery deduplication.
- Bilingual native search/editor/list controls, calendar markers, launcher actions and --search/--personal commands.
- Preserve verified annual data, centered widget, appearance, startup choice and package identity; document readable /tmp installation.

## 0.3.1 — 2026-10-12

- Replace the overflowing stock About dialog with bounded, scrolling About/Credits/Licenses pages.
- Wrap long attribution text and localize headings, actions and RTL/LTR independently of system locale.
- Explicit GitHub and issue links, native app mark and complete offline original licenses.
- Preserve package identity, widget layout, preferences, seasonal UI and calendar data.

## 0.3.0 — 2026-10-12

- Scenic calendar header, lighter date grid and a compact selected-day card with Copy date menu.
- Grouped preferences with mirrored sidebar, live current-date widget preview and advanced controls.
- Persian RTL and English LTR navigation and month grids, with matching keyboard direction.
- Consistent native outline icons and theme-colored controls.
- Short scene/content fades, opt-out preference and native reduced-motion support; no idle animation.
- Existing widget, verified data, fonts, numerical dates, startup choice and installation identities preserved.

## 0.2.0 — 2026-10-11

- Four bundled seasonal scenes and scalable icons; automatic/manual seasons, dark/light and custom accent controls.
- Centered Shamsi card with independent Gregorian/Hijri visibility and preserved compactness.
- Adaptive bilingual sidebar, monthly occasions, About and title-click month selection.
- Real seasonal settings previews and preserved legacy appearance/configuration.
- Roozlet / روزلت visible branding with unchanged `rooz` package/command identity.
- Existing verified 1405 data, numerical dates, clipboard and opt-in startup retained.


## 0.1.0

Compact three-calendar card; double-click month view; offline verified 1405
Iranian dates, Hijri mapping, occasions and public holidays; bilingual interface;
independent digits; bundled Vazirmatn; themes and appearance controls; opt-in
login startup; managed Xfce placement; keyboard and clipboard actions; Debian package.

Published as Roozlet with an illustrated English/Persian README, MIT application
license, source archive, checksums, and GitHub CI/release-preparation workflows.
The first release retains the Rooz application name and `rooz` package/command.
