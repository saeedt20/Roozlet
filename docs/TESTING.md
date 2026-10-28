# Validation record

The original 0.1.0 tests were performed on Linux Mint 22.3 Xfce/X11 with Python 3.12.3, GTK 3.24.41,
PyGObject 3.48.2, Cairo 1.25.1, Xfwm4 4.18.0, Fontconfig 2.15.0 and Poppler 24.02.0.
Only application window captures belong in docs/screenshots.

## 0.4.2 audit fixes — 28 October 2026

- All **93 tests** passed at normal and 200% scale: 53 logic/data checks, 34 GTK checks and six notification protocol checks, using temporary personal data and private D-Bus sessions.
- New regressions cover malformed nested annual records, archive exclusion of untracked files/symlinks/databases, reminder read failures, System-timezone spring DST catch-up, future annual entries and retained Settings state. The previously failing narrow-window check now passes by measuring content width without window decorations. Navigation and search help scroll instead of forcing large-text windows taller than short screens.
- A warm lookup of a 30-day month with 10,000 synthetic daily entries made **30 SQL queries in 0.864 seconds**, down from 300,000 queries and 6.484 seconds in the audit. This measures the data lookup, not complete rendering.
- The extracted 0.4.2 package passed headless version/data commands from `/tmp` and real window checks at normal and 200% scale. Settings, Search and personal-entry routes reused one calendar window; raising it preserved the current page. Mapped card geometry measured 320 × 236 and 640 × 472 physical pixels.
- Annual data remains unchanged: 365 mappings, 305 occasions and 26 holiday dates, with no validation issues. Personal tables remain schema 1; an index speeds up occurrence lookups by day.
- No system installation, physical monitor changes, login/suspend cycle or native pointer/Show Desktop check was performed. The desktop-input helper was updated for the current titles, geometry and embedded Settings; those gestures still require a manual run.

The installed-layout helper accepts an explicit extracted launcher:
`dbus-run-session -- python3 scripts/installed-gui-check.py /path/to/extracted/usr/bin/rooz`.
Its report is written to `dist/installed-gui-check-0.4.2.json`.

## 0.4.1 seasonal visuals and embedded navigation — 12 October 2026

- All **86 tests** passed: 47 logic/data checks, 33 native GTK checks and six notification protocol checks. The complete suite passed at normal and 200% scale in isolated virtual X11/private D-Bus.
- New regressions cover repeated settings/search/About activation without new application windows, retained search/section state, Persian RTL/English LTR, Escape navigation, wrapped long Credits at narrow sizes, all four live season boundaries and stale stored artwork reconciled with both card marks. Manual season selection and viewed-month scope are preserved.
- The real application coordinator was exercised under Xfwm4 on virtual X11: 12 repeated activations per route, actual language-setting callbacks, winter/manual → autumn/auto selection, search result activation, About/Credits, and English light mode. Only the desktop card and one calendar application window existed. The same application stages passed from the extracted Debian package. Window captures contain only Roozlet, with an isolated synthetic profile.
- Annual data validation passed with no issues: unchanged 365-day 1405 mapping, 305 occasions and 26 holiday dates. No annual-data or personal-store migration.
- The supplied winter-scene/autumn-accent screenshot did not reproduce with fresh 0.4.0 automatic-season defaults. Fresh 20 Mehr 1405 showed autumn artwork and a leaf. The original cause is unconfirmed; live reconciliation is hardened and upgrade instructions explicitly stop/restart the old process. Manual season choices remain intentional.
- Native Mint apt installation, physical multi-monitor recovery, login/resume and actual notification presentation were not repeated. Virtual tests do not certify those environments.

## 0.4.0 search/personal reminders — 12 October 2026

- All **83 tests** passed: 47 logic/data checks, 30 native GTK checks and six
  notification protocol checks. The complete suite also passed at 200% scale,
  including large-font bilingual popup bounds, in isolated virtual X11.
- Pure checks cover three digit styles, named/numerical dates, invalid/out-of-range
  rejection, cross-language search, personal-body search, limits, private SQLite
  permissions, durable reopen, transactional write failure, reversible delete,
  one-time/daily/weekly/Shamsi-yearly recurrence and per-occurrence completion.
- Reminder checks cover timezone conversion, 24-hour grace, future/missed times,
  first DST fold and spring gaps, opt-in, in-flight suppression, retry, accepted
  delivery persistence and edits racing an old pending delivery.
- Native UI checks exercise Ctrl+F, actual result activation across months,
  note save/edit/calendar markers, complete/delete/undo buttons, birthday defaults,
  explicit notification opt-in, date-calendar conversion, invalid times, dirty
  draft handling, callback cleanup and a personal-read failure leaving official
  calendar browsing usable.
- Native asynchronous freedesktop calls are checked against a synthetic private
  D-Bus service: GetCapabilities, escaped/plain bodies, optional actions, action
  date routing, close signals, opt-out during connection, cancellation and error
  propagation. No test sends reminders to the user's real desktop service.
- The extracted .deb ran from /tmp with a temporary XDG profile. All 12 real App
  checks passed: search/month jump, editor persistence, saved recurrence/markers,
  draft retained on forced write failure, default-off notifications, delete/undo,
  actual notification settings, coordinator Notify, no duplicate poll, date
  action, independent database reopen and durable opt-out. See
  v0.4.0-installed-check.json.
- Ten actual native GTK captures use synthetic demonstration entries only:
  Persian dark and English light search, editor, personal list, calendar and
  notification preferences. They were visually reviewed; no user notes or other
  desktop windows were captured.
- A 35.01-second fresh widget-only idle observation used 76,408–76,412 KiB RSS
  (about 74.62 MiB) and 0.0006 seconds process CPU (0.002% of one core).
  See v0.4.0-resource-check.json; this is a short virtual-X11 observation.
- Annual data is unchanged and validation reports no issues: 365 date mappings,
  305 occasions, 26 statutory holiday dates. Personal entries stay separate.
- The readable /tmp installation instructions avoid the private-home `_apt` notice.
  Rootless package builds are checked for byte-identical output, source/archive
  checksums and exclusion of SQLite database/journal files from publications.

Native Mint apt upgrade/removal, real login/suspend/overnight transitions, physical
monitor changes and actual Xfce notification presentation were not repeated. The
protocol checks certify the private service exchange, not every desktop's popup
presentation or do-not-disturb policy. Notification service acceptance is reported
accurately. See [PERSONAL.md](PERSONAL.md) for exact runtime and recurrence rules.

## 0.3.1 About/Credits overflow — 12 October 2026

- All **54 tests** passed: 31 logic/data checks and 23 native GTK checks.
- All **23 GTK checks also passed at 200% scale** in isolated virtual X11.
- The real Credits switcher button is pressed after inserting a multi-thousand-
  character notice including a 1,200-character unbroken token. Window size stays
  unchanged, vertical scrolling is available, horizontal scrolling is disabled,
  and the themed window can shrink to a 300 × 220 content allocation.
- About uses the parent monitor work area, with space reserved for window chrome.
  Persian/English titles, controls and RTL/LTR are checked independently of the
  desktop locale. GitHub and issue destinations, one-window reuse, Escape and
  parent destruction are verified.
- All four complete original license texts match their local files exactly.
  License text retains LTR independently of Persian controls; motion opt-out and
  the existing reduced-motion gate remain supported.
- Six actual About/Credits/Licenses captures (Persian dark and English light) were
  reviewed. These are native GTK captures, not generated design mockups.
- The extracted .deb was launched from /tmp with temporary XDG settings. Version,
  installed resources, unchanged Credits size, four installed license files and
  the real Close callback passed. Native Mint apt upgrade/login/suspend/physical
  monitor lifecycle was not repeated.
- Annual validation remains unchanged: 365 dates, 305 occasions and 26 statutory
  public-holiday dates, with no validation issues.
- The headless-command test now preserves an injected dependency PYTHONPATH so
  subprocesses use the same private GTK runtime as the parent test process.

## 0.3.0 calendar/settings and motion — 12 October 2026

- All **51 tests** passed: 31 calendar/data/configuration/format/season checks and
  20 native GTK checks in an isolated Ubuntu 24.04 GTK3 virtual X11 runtime.
- All **20 GTK checks also passed at 200% scale**. Temporary XDG profiles and
  private D-Bus/display transports kept tests independent of user settings.
- New checks cover Persian/English physical columns and keyboard arrows,
  navigation-icon/label order, settings-page retention, actual switch/season
  callbacks, textual/numerical dropdown copy routing, missing artwork on a light
  surface, narrow-window navigation and work-area bounds.
- Motion checks exercise rapid navigation (at most two content trees, one after
  completion), 260 ms scene completion, unmap cleanup, opt-out and native GTK
  animation opt-out. Appearance updates preserve existing date cells, focus and
  preview content rather than rebuilding them on slider input.
- Annual data is unchanged: 365 date mappings, 305 occasions and 26 statutory
  holiday dates; validation reports no issues.
- Actual GTK window captures in Persian/English and dark/light were reviewed;
  scene headers, grouped preferences, centered Shamsi preview, copy menu and
  outlined native icons are real UI, not generated mockups. Capture dates use a
  deterministic 12 October fixture in the isolated screenshot harness.
- The extracted Debian package ran from /tmp; real language/digit/season/color/
  font callbacks, validated configuration replacement, actual numerical GTK
  clipboard, month-title picker, filters, motion persistence and unavailable
  Hijri copy were checked. All 12 installed-layout checks passed; see v0.3.0-installed-check.json.
- A 35.00-second widget-only idle observation held at **75,020–75,024 KiB RSS**
  (about 73.27 MiB), with **0.0009 seconds process CPU** (0.003% of one core).
  See v0.3.0-resource-check.json; this is a short in-process observation.

Native Mint apt installation/upgrade/removal, login, overnight/resume, physical
monitor hotplug, mixed-DPI desktop behavior and Wayland were not repeated.
Earlier native desktop reports below apply to the versions explicitly named.

## 0.2.0 seasonal redesign — 11 October 2026

- Passed all **44 tests**: 30 calendar/data/configuration/format/season tests and 14 native GTK checks in an isolated Ubuntu 24.04 private GTK3 runtime with virtual X11 and temporary XDG profiles.
- Passed all **14 GTK checks at GDK_SCALE=2**. This is virtual-display evidence, not a claim of native Mint/Xfce installation or desktop interaction testing.
- Added checks for all seasonal boundaries, manual/automatic precedence, calendar-only follow-month contexts, legacy appearance migration, persisted custom accents, finite slider values, scene checksums, centered Shamsi in both languages/all satellite visibility cases, title picker and actual preview callbacks.
- Annual data validation passed with 365 mappings, 305 occasions, 26 statutory holiday dates, and no issues; annual data was not modified.
- Actual application-window captures were reviewed for seasonal cards, Persian right-sidebar calendar, English light calendar, settings previews and monthly occasions.
- The extracted installed package launched from `/tmp` with all four scenes, independent resource paths, live language/season controls, actual numerical GTK clipboard, title month picker and occasion view callbacks verified. This is not an apt install/upgrade.
- Rootless package `roozlet_0.2.0-1_all.deb` was built and its control metadata inspected. It retains `Package: rooz`, version `0.2.0-1`, architecture `all`, declared native dependencies and all four offline scene assets.

Native Mint apt installation/upgrade, login startup cycle, physical monitor hotplug, mixed DPI, overnight/resume and Wayland checks were not repeated. Existing historical checks below do not certify the redesigned version. An initial logic-only command without this workspace's private GI dependencies could not exercise the graphical startup check; the complete configured runtime run above passed it.

## 0.1.1 regression checks — 11 October 2026

The fixes were checked in an isolated Ubuntu 24.04 environment with distribution
GTK3/PyGObject packages, Python 3.12.3, temporary XDG directories, Xvfb and a private
D-Bus session. This workspace required local TCP transports for the test display
and bus; the application itself has no runtime network dependency.

- **Passed:** all 35 tests (24 logic/configuration/data tests and 11 GTK checks).
- **Passed:** all 11 GTK checks repeated at `GDK_SCALE=2`.
- New regressions cover persisted numerical dates, both UI languages and digit
  styles, unavailable Hijri dates, actual title pixels and gear placement,
  numerical copy callbacks, right-click and keyboard month picker opening, normal
  Today clicks, shorter-month day clamping and supported-year boundaries.
- Actual GTK window captures were reviewed for the Persian/English headers,
  numerical-date setting and 12-month picker.
- **Passed:** the standard rootless build and annual data validation (no issues).
  The extracted 0.1.1 package launched from an unrelated working directory; real
  application callbacks changed settings, copied numerical dates through the GTK
  clipboard and selected a month. This is an extracted-layout test, not an apt
  install/upgrade.

Native Xfce desktop behavior and a real Mint package install/upgrade were not
repeated for 0.1.1. The original release's additional checks below remain historical
evidence rather than new 0.1.1 results.

Run logic/data checks:

```
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/validate-data.py
```

Run native GTK checks on an existing display:

```
scripts/test-gui.sh
GDK_SCALE=2 scripts/test-gui.sh
```

The GTK tests use temporary XDG directories and a separate D-Bus session. Desktop
portal/keyring activation may emit host warnings unrelated to app features. The
app makes no network requests. Desktop interaction checks and package inspection
are recorded below as they are completed; unchecked scenarios are not implied.

## Automated results

* **Passed:** 20 core/data/configuration/localization tests, including **36,890**
  daily round trips in 1350–1450 and all 365 independent official 1405 mappings.
* **Passed:** seven GTK checks at default scale and the same seven at `GDK_SCALE=2`.
  Includes compact size, Pango font resolution, gear/double-click/drag threshold,
  keyboard date navigation, today/selection accessible states, live view rebuilds,
  large text, light theme, and hidden-view preservation.
* **Passed:** data validation — 365 days, 305 records, 26 distinct public-holiday
  dates, all 189 main/93 appendix cells represented; no validation issues.
* **Passed:** `desktop-file-validate`, Python compilation, declared dependency
  resolution with `apt -s install`, and rootless `.deb` metadata/content inspection.
* **Passed:** extracted installed launcher from unrelated `/tmp` working directory;
  headless version/data commands find private data/font/library resources.

Tests run in private D-Bus sessions emit host portal/FUSE/keyring warnings and a
roughly 25-second portal activation delay on this machine. Default desktop-session
launches are responsive. These warnings are not from a runtime network request.
A few GTK3 monitor/font APIs emit deprecation notices but remain supported by the
target GTK3. No system theme, panel, wallpaper or compositor was changed.

## Acceptance checklist

| Check | Status / evidence |
| --- | --- |
| Compact card, three dates, no clipping | Passed; actual 320 × 208 captures |
| Native double-click, one month view, gear/context/drag independence | Passed; XTest/CLI interaction report |
| Calendar day counts/placement, Fridays vs statutory holidays | Passed; golden/core tests and screenshots |
| Today/selection indicators and accessible labels | Passed; GTK checks and screenshots |
| Details, copy actions, event filters, countdown | Logic/GTK checks passed; native holiday details and exact Persian clipboard round-trip passed |
| Unsupported-year messages | Passed; core/GTK coverage checks |
| English/Persian control direction and independent digits | Passed; GTK checks, restart and native setting callback checks |
| Vazirmatn resolution, Persian joining/half-spaces | Passed; Pango reports Vazirmatn and rendered source/text inspection |
| Dark/light colors and readable custom selection foreground | Passed; screenshot review and contrast calculation |
| Default and 200% scale, large text, reachable full-view controls | Passed; GTK scale checks; body scrolls on constrained screens |
| Background-only alpha, opaque fallback | Alpha passed; fallback implemented, compositor-disabled session not tested |
| Drag/reset/persist/negative-coordinate clamp | Passed; native drag and pure placement tests |
| Physical monitor hotplug / mixed DPI | Not tested; requires physical display changes |
| Above-wallpaper / below normal app windows | Managed Xfce hints verified; ordinary desktop display passed |
| Show Desktop | Passed; widget stays viewable |
| Workspace switching and always-on-top | Sticky/layer hints verified; live workspace switching and layer toggles not tested |
| Midnight/resume/clock changes | Fake-clock changes passed; real overnight rollover and suspend not tested |
| Startup opt-in/out and saved-state derivation | Passed in temporary XDG directories; actual login cycle not tested |
| CLI single instance / quit / reopening | Passed; native desktop check |
| Installed paths and offline resources | Extracted layout passed; actual apt-installed GUI pending |
| .deb real install / upgrade / removal | Not tested; sudo requires a password in this session |
| Idle CPU/memory | Measured separately below; long-running endurance not tested |
| Wayland | Not tested; X11 is the release target |
| Screen-reader session | Accessible labels checked; actual screen reader not tested |
| lintian / debhelper alternative | Not tested locally; tools not available |
| GitHub CI execution | Passed on Ubuntu 24.04; core/data checks, Xvfb GTK checks and package build |

No scenario marked not tested is implied by unit or virtual-display tests.

The final native desktop report, `docs/desktop-check.json`, records **21 passed
checks**, including a real language-combo change applying immediately while Latin
digits remain independently selected. Screenshot tests isolate the application
PID and use exact client-window coordinates and IDs; unrelated windows are excluded.
Source formatting and Ruff checks passed (vendored upstream source excluded).
The CI workflow YAML files parse successfully. The first published source commit
passed [GitHub CI run 38085348396](https://github.com/saeedt20/Roozlet/actions/runs/38085348396)
on Ubuntu 24.04, including logic/data checks, seven GTK checks under Xvfb, and the
rootless package build. This supplements the native Mint validation above.

## Package reproducibility and resources

Two consecutive rootless builds produced byte-identical `.deb` files. The package
contains root-owned standard paths, declared system dependencies, private complete
conversion-library source, three font weights and licenses, versioned annual data,
translated desktop actions, icon, man page and documentation. No maintainer script,
autostart entry or bytecode is shipped. No command/package conflict was found.

A real default widget in a temporary profile held at **66,812 KiB (65.25 MiB) RSS**
through a **60.01-second** idle interval. The kernel CPU counter increased by
**0 ticks** (no measurable process CPU at that counter's resolution). This is a
short idle measurement, not an endurance, login, overnight or resume test. The
minimal public report in `docs/resource-check.json` excludes machine identity
and user configuration. Reproduce with `python3 scripts/resource-check.py` when
no other Rooz instance is running in that D-Bus session.

The **extracted installed package** also launched its real GTK views from `/tmp`
at both 100% and 200% (`docs/installed-gui-check.json`). Physical card dimensions
were 320 × 208 and 640 × 416 respectively. The 200% month view opened within the
work area at 1120 × 740 physical pixels, with the body scrollbar keeping the lower
controls reachable. These are installed-layout tests, not a claim of apt-installed
package-manager lifecycle testing.

A native installed-layout review selected the statutory holiday on 22 Aban 1405,
confirmed its holiday details and copied `۲۲ آبان ۱۴۰۵` through the real button
and GTK clipboard. At 200% scaling, scrolling reached all three copy controls.
The holiday and scrolled 200% screenshots were inspected; visible scrollbars,
joined Persian text, selected-day contrast and reachable controls were confirmed.

The 0.2.0 artwork is about 10.73 MiB before packaging, exceeding the brief’s provisional 8 MiB artwork target to retain the generated scene quality. The complete Debian package is about 10.52 MiB. Images are loaded near display size with a bounded cache.

The 0.2.0 seasonal widget held at 74,476–74,480 KiB RSS during a 35.01-second idle interval in the private GTK virtual X11 test environment. Process CPU increased by 0.0006 seconds (0.002% of one core). See `docs/v0.2.0-resource-check.json`. This short measurement does not establish native Xfce, overnight, suspend/resume or login behavior.
