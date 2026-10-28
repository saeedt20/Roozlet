<p align="center">
  <img src="data/icons/rooz.svg" alt="Roozlet icon" width="72" height="72">
</p>

<h1 align="center">Roozlet</h1>
<p align="center">A little Persian calendar for your Linux desktop.</p>
<p align="center">
  <a href="https://github.com/saeedt20/Roozlet/releases/latest"><img src="https://img.shields.io/github/v/release/saeedt20/Roozlet" alt="Latest release"></a>
  <a href="https://github.com/saeedt20/Roozlet/actions/workflows/ci.yml"><img src="https://github.com/saeedt20/Roozlet/actions/workflows/ci.yml/badge.svg" alt="Build and tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/desktop-Xfce-blue" alt="Xfce desktop">
</p>
<p align="center">
  <a href="https://github.com/saeedt20/Roozlet/releases/latest">Download</a> ·
  <a href="README.fa.md">فارسی</a> ·
  <a href="docs/DATA_SOURCES.md">Calendar data</a> ·
  <a href="https://github.com/saeedt20/Roozlet/issues">Report an issue</a>
</p>

Roozlet keeps Persian, Gregorian and official Iranian Hijri dates on a compact desktop card. Double-click for the month calendar, occasions, notes and reminders. Built with native GTK 3 for **Linux Mint 22.3 Xfce/X11**, it works offline.

The visible name is **Roozlet / روزلت**; the command and Debian package remain **`rooz`** so existing installations upgrade normally. Wayland has not been validated.

## Install

Download **[roozlet_0.4.2-1_all.deb](https://github.com/saeedt20/Roozlet/releases/download/v0.4.2/roozlet_0.4.2-1_all.deb)**. In the download folder:

```sh
install -m 644 ./roozlet_0.4.2-1_all.deb /tmp/roozlet_0.4.2-1_all.deb
sudo apt install /tmp/roozlet_0.4.2-1_all.deb
rooz
```

**Upgrading:** run `rooz --quit` before installation and restart afterward; installing a package does not reload an existing process. Settings and personal entries are preserved. APT resolves native dependencies; the readable `/tmp` copy avoids `_apt` access notices. Installation does not launch the app or enable startup.

To verify checksums, download all three [release assets](https://github.com/saeedt20/Roozlet/releases/tag/v0.4.2) into one folder and run `sha256sum -c SHA256SUMS`.

## Preview

<table>
<tr><th>Seasonal card</th><th>Settings in the calendar</th></tr>
<tr><td><img src="docs/screenshots/v0.4.1-card-autumn-fa.png" alt="Persian autumn calendar card" width="320"></td><td><img src="docs/screenshots/v0.4.1-settings-fa.png" alt="Persian settings inside the native calendar" width="540"></td></tr>
</table>

*Native GTK captures from an isolated virtual X11 display. Personal-entry examples in the documentation are synthetic.*

## Features

- **Three calendars:** a centered Shamsi date with optional Gregorian and Iranian Hijri dates, plus a full month view and copy actions.
- **Search and personal entries:** date jumps, occasions, notes, birthdays, appointments and tasks, with Shamsi recurrence and undo deletion.
- **Optional reminders:** desktop notifications are off by default; enable them globally and for each entry. Reminders run **only while Roozlet is running**.
- **Four seasons:** bundled Spring/Summer/Autumn/Winter artwork, automatic/manual selection, Classic mode and light/dark themes.
- **Persian and English:** RTL/LTR layouts, independent numeral choices and bundled Vazirmatn fonts.
- **Desktop controls:** dragging, position lock/reset, optional top/all-workspaces placement and opt-in login startup.
- **Local operation:** personal entries use a private SQLite database; no account, telemetry or runtime downloads are required.

Settings, Search and About share the existing calendar window. Automatic season follows today's Shamsi date; “follow displayed month” affects calendar scenery, not the desktop card. Older Classic profiles retain their appearance. [Current changes](docs/releases/v0.4.2.md) · [Personal-entry and reminder guide](docs/PERSONAL.md).

## Calendar coverage

| Data | Verified range |
|---|---|
| Persian/Gregorian browsing and conversion | Shamsi **1350–1450** |
| Official Iranian Hijri dates | **1405 only** |
| Official occasions and holidays | **1405 only**: 305 records, 26 distinct statutory holiday dates |

The bundled **1405.1** dataset comes from the final University of Tehran Calendar Center calendar. Outside that year, annual coverage is marked incomplete and Iranian Hijri dates unavailable; future lunar holidays are not guessed. Some English occasion titles retain an explicit Persian fallback. [Sources and validation](docs/DATA_SOURCES.md).

The default civil timezone is **Asia/Tehran**, with a system-timezone option. Personal entries remain separate from official public holidays.

## Everyday commands

| Command | Action |
|---|---|
| `rooz` | Start the card; a repeat launch raises the calendar |
| `rooz --calendar` | Open the month view |
| `rooz --search` | Search dates, occasions and entries |
| `rooz --personal` | Open notes and reminders |
| `rooz --settings` | Open Settings |
| `rooz --reset-position` | Recover the card's position |
| `rooz --quit` | Close the app |

Double-click the card for the calendar; use the gear or right-click for controls. Escape returns to the calendar, and closing it leaves the card running. Enable login startup in **Desktop & startup** if wanted; a source checkout cannot enable it before the installed launcher exists.

## Build and test

```sh
git clone https://github.com/saeedt20/Roozlet.git
cd Roozlet
sudo apt install git python3 python3-gi python3-cairo python3-gi-cairo gir1.2-gtk-3.0 tzdata libfontconfig1
./scripts/dev-run.sh --calendar
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/validate-data.py
./scripts/build-deb.sh
```

The rootless package build writes `dist/`. [Release instructions](docs/RELEASING.md) cover the source archive and checksums. [Testing](docs/TESTING.md) covers isolated GTK/notification and 200% scale checks, plus remaining real-session, suspend and monitor tests.

## Help and license

- [Personal entries](docs/PERSONAL.md) · [Data provenance](docs/DATA_SOURCES.md) · [0.4.1 interface](docs/UI_0.4.1.md)
- [Contributing](AGENTS.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

To remove: `rooz --quit`, then `sudo apt remove rooz`. Preferences remain; disable login startup first if enabled.

Original code and documentation are **[MIT-licensed](LICENSE)**, copyright © 2026 Saeed Taheri. Bundled libraries/fonts retain their licenses; calendar data credits the University of Tehran Calendar Center. Roozlet is independent of Linux Mint.
