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

Roozlet keeps today's Persian, Gregorian and official Iranian Hijri dates on a
compact desktop card. Double-click it to open a full month calendar with Iranian
occasions and public holidays. Built with native GTK3 for **Linux Mint 22.3 Xfce**,
it works offline and stays out of the way.

The visible application name is **Roozlet / روزلت**. The established `rooz` command
and Debian package identity remain unchanged so existing installations upgrade normally.

## Four seasons, one compact calendar

Roozlet includes **Spring, Summer, Autumn and Winter** appearances with bundled
scenery and scalable seasonal icons. The **Shamsi date is always in the middle**
of the 320 × 236 logical-pixel widget, with Gregorian on the left and Iranian
Hijri on the right. Hiding either auxiliary calendar keeps Shamsi centered.

These are actual GTK window captures from an isolated virtual X11 display, not
design mockups or a claim of a native Mint installation test.

<table>
<tr><th>Spring</th><th>Summer</th></tr>
<tr><td><img src="docs/screenshots/v0.3.0-card-spring-fa-dark.png" width="320" alt="Spring centered Shamsi widget"></td><td><img src="docs/screenshots/v0.3.0-card-summer-fa-dark.png" width="320" alt="Summer centered Shamsi widget"></td></tr>
<tr><th>Autumn</th><th>Winter</th></tr>
<tr><td><img src="docs/screenshots/v0.3.0-card-autumn-fa-dark.png" width="320" alt="Autumn centered Shamsi widget"></td><td><img src="docs/screenshots/v0.3.0-card-winter-fa-dark.png" width="320" alt="Winter widget with snowflake"></td></tr>
</table>

![Persian calendar with right sidebar](docs/screenshots/v0.3.0-calendar-fa-dark.png)
![English light calendar with left sidebar](docs/screenshots/v0.3.0-calendar-en-light.png)
![Persian preferences with right-aligned sidebar](docs/screenshots/v0.3.0-settings-fa-dark.png)
![English preferences with left-aligned sidebar](docs/screenshots/v0.3.0-settings-en-dark.png)

### Fixed in 0.3.1

- About, Credits and Licenses now use localized, work-area-sized scrolling pages.
- Long artwork notices and unbroken text wrap without enlarging the window.
- Explicit **GitHub** and **Report an issue** links, an actual native app mark and offline original license texts.
- Persian RTL and English LTR follow the app language independently of system translations.

![Persian About and credits](docs/screenshots/v0.3.1-credits-fa-dark.png)
![English About](docs/screenshots/v0.3.1-about-en-light.png)

### New in 0.3.0

- Scenic calendar header, quiet date grid and a selected-day card with one **Copy date** dropdown, including numerical variants.
- **Persian RTL / English LTR** navigation and weekday columns. Saturday starts the week in both; keyboard arrows follow the visible direction.
- Grouped preferences, a live current-date widget preview, four season tiles, light/dark controls and an advanced section for fonts, scales and Classic mode.
- **Subtle transitions:** 160–180 ms content fades, 260 ms artwork crossfades and gentle button feedback. Disable them in Appearance; system GTK animation preferences are respected. There is no looping or idle animation.
- Automatic/manual seasons and calendar-only **Follow displayed month** remain available. The widget's Shamsi date stays centered.
- Click the month title or right-click **Today** (Shift+F10 when focused) to choose a month and year.
- Independent digits, numerical copies, verified data, font/position settings and opt-in startup are preserved.

**Upgrading:** old settings keep their Classic appearance and custom accent. To
turn on scenery, open **Settings → Appearance → Advanced settings → Appearance style → Seasonal**.
Fresh installations use automatic seasonal appearance. No wallpaper or system
theme is changed and no artwork is downloaded at runtime.

<details>
<summary>Earlier 0.1.0 Mint Xfce examples: English calendar, independent digits, holidays and 200% scaling</summary>

![English month calendar](docs/screenshots/calendar-en-light.png)

Persian interface with independently selected Latin digits:

![Persian interface with Latin digits](docs/screenshots/card-fa-latin-light.png)

Selected official holiday and its details:

![Official holiday details](docs/screenshots/calendar-fa-holiday.png)

Full calendar at 200% scale on a constrained work area; scroll to reach the lower controls:

![Calendar at 200% scale](docs/screenshots/calendar-fa-dark-2x.png)

![Reachable calendar controls at 200% scale](docs/screenshots/calendar-fa-dark-2x-scrolled.png)

</details>

## Features

- **Compact desktop widget:** three dates, an occasion summary and the next public-holiday countdown.
- **Full calendar:** computed Persian month grids, Gregorian secondary dates, distinct holiday/event markers, selected-day details and copy actions.
- **Quick month selection:** right-click **Today** (or focus it and press Shift+F10) to choose from all 12 Persian months, with year navigation. Left-click returns to today.
- **Numerical dates:** enable **Settings → Dates → Prefer numerical form of dates** for `year/month/day` hover text, date details and clipboard copies. The widget's **Copy numerical date** menu also works without enabling the preference.
- **Bilingual controls:** complete Persian and English interfaces, independent Persian/Latin digits and bundled Vazirmatn fonts.
- **Personal appearance:** dark/light themes, accent color, background opacity, font choice, card size and text scale.
- **Desktop behavior:** header dragging, position lock/reset, optional always-on-top and all-workspaces placement, and single-instance operation.
- **Your startup choice:** start at login is off by default and controlled in Settings.
- **Offline operation:** no account, telemetry, runtime downloads or calendar API dependency.

## Install

Download `roozlet_0.3.1-1_all.deb` from the [latest release](https://github.com/saeedt20/Roozlet/releases/latest).
From the folder containing the downloaded file:

```bash
sudo apt install ./roozlet_0.3.1-1_all.deb
rooz
```

APT resolves the native GTK, Cairo, Fontconfig and timezone dependencies.
Installation adds a desktop launcher; it does not start the app or enable login startup.
Run the app as your ordinary user.

Optional: download all three release assets into the same folder and verify them:

```bash
sha256sum -c SHA256SUMS
```

### Everyday use

Double-click the card to open the month view. Use the gear for Settings, right-click
for calendar/copy/position actions, and drag the header to move the unlocked card.
Closing the calendar or Settings leaves the card running. The **Copy date** menu includes textual/numerical formats and all-date copies.

| Command | Action |
| --- | --- |
| `rooz` | Start the card; a repeat invocation raises the calendar |
| `rooz --widget` | Start or retain card mode, without opening the month view |
| `rooz --calendar` | Open or raise the month view |
| `rooz --settings` | Open or raise Settings |
| `rooz --reset-position` | Restore a safe default card position |
| `rooz --check-data` | Report installed calendar coverage and validation |
| `rooz --version` | Print the version |
| `rooz --quit` | Close the running application |

In Persian, **Saturday is on the right** and **Friday is on the left**; Left moves one day forward. In English, **Saturday is on the left** and **Friday is on the right**; Right moves one day forward.
Up/Down move one week, Page Up/Down move one month, and Home/End select the first/last
day of the month. The Today button returns to the current civil day.

Start at login uses your XDG autostart entry. Enable or disable it in Settings
under Desktop & startup. The development checkout cannot enable it until
`/usr/bin/rooz` is installed.

## Calendar accuracy and coverage

Dates come from tested conversion logic, not from screenshot layouts.
The default civil timezone is **Asia/Tehran**; the system timezone is also selectable.

| Data | Verified coverage |
| --- | --- |
| Persian/Gregorian browsing and conversion | 1350–1450; all 36,890 days round-trip tested |
| Independent official annual date mappings | Every day of 1405: 2026-03-21 through 2027-03-20 |
| Official Iranian Hijri dates | 1405 only; derived from the final Iranian annual calendar |
| Iranian occasions | 305 records from all 189 main and 93 appendix occasion cells for 1405 |
| Statutory public holidays | 26 distinct dates in 1405; ordinary Fridays are separate |

The bundled dataset is **1405.1**, sourced from the final University of Tehran
Calendar Center calendar. Leap flags across the conversion range are checked
against the Center's independent leap-year reference.

Outside 1405, the app states that annual occasion coverage is incomplete and
Hijri dates are unavailable. Future lunar holidays are not guessed. Of the occasion
records, 190 have reviewed English translations; 115 display their Persian title
with an explicit translation-fallback notice.

See [data provenance, checksums and update procedure](docs/DATA_SOURCES.md).

## Build from source

```bash
git clone https://github.com/saeedt20/Roozlet.git
cd Roozlet
sudo apt install python3 python3-gi python3-cairo python3-gi-cairo gir1.2-gtk-3.0 tzdata libfontconfig1
./scripts/dev-run.sh --calendar
```

Build the Debian package and publication source archive:

```bash
./scripts/build-deb.sh
python3 scripts/source-archive.py
(cd dist && sha256sum -c SHA256SUMS)
```

Output is in `dist/`. The rootless build uses `dpkg-deb`, needs no pip or runtime
network downloads, and bundles pinned conversion-library source and static fonts
with their licenses. Native libraries remain declared system dependencies.
Standard debhelper packaging is also available; see [release instructions](docs/RELEASING.md).

### Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/validate-data.py
./scripts/test-gui.sh
GDK_SCALE=2 ./scripts/test-gui.sh
```

Version 0.3.1 passes **54 tests**, including **23 GTK checks**, also checked at 200% scaling. The GTK checks need an active display or Xvfb. They use temporary XDG directories
and a private D-Bus session. The original 0.1.0 validation includes **20 core tests**, **seven
GTK checks at each scale**, **21 native Xfce interaction checks**, installed-layout
launches, Persian clipboard round trips and reproducible package builds.
Version 0.1.1 passes **24 logic tests and 11 GTK checks**, with all 11 GTK checks
also passing at 200% scale; its extracted-package GUI and numerical clipboard
callbacks were checked separately.

See the [full validation record](docs/TESTING.md), including checks still requiring
real login, suspend, physical monitor changes and package-manager lifecycle testing.
X11 is the release target; Wayland has not been validated.

## Remove

```bash
rooz --quit
sudo apt remove rooz
```

User preferences are preserved. If you enabled login startup, disable it before
removal or remove only its entry afterwards:

```bash
rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/autostart/rooz.desktop"
```

## Contributing

Bug reports and focused pull requests are welcome. Include your desktop session,
app version, relevant settings and steps to reproduce. Calendar-data corrections
must cite an authoritative source and include a regression check. Keep the default
card compact, preserve independent language/digit settings, and avoid runtime
network dependencies. See [design notes](docs/DESIGN.md) and [development instructions](AGENTS.md).

## License and acknowledgments

Original application code and documentation are licensed under the **[MIT license](LICENSE)**,
copyright © 2026 Saeed Taheri.

Bundled jdatetime, jalali-core and Vazirmatn retain their own licenses. Calendar
facts are attributed to the University of Tehran Calendar Center; the original
annual PDF is not redistributed. See [third-party notices](THIRD_PARTY_NOTICES.md).

Roozlet is an independent project, not an official Linux Mint product.
