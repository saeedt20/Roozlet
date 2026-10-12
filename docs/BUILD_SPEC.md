> **0.3.0 update:** [UI_0.3.md](UI_0.3.md) supersedes older calendar/settings layout and motion rules. Persian uses RTL, English uses LTR including weekday columns, with Saturday first in both. All accuracy, offline and compatibility rules remain applicable.

> **0.2.0 update:** visible branding is Roozlet / روزلت; the centered Shamsi layout, four seasonal themes, and adaptive shell are specified in [SEASONAL_UI_REDESIGN.md](SEASONAL_UI_REDESIGN.md) and implemented as described in [DESIGN.md](DESIGN.md). Older appearance/order/dimension descriptions below are historical. Accuracy, offline behavior and compatibility requirements remain applicable.

# Rooz — روز

## Complete build brief for Claude Code or Codex

**Specification date:** 2026-10-10  
**Target:** Linux Mint 22.3 Xfce  
**Deliverable:** A working Persian calendar desktop widget, full calendar window, installable `.deb`, and GitHub-ready source.

> Coding agent: read this entire document and implement the project. Deliver a working application, not just a plan, mockup, or scaffold. Use the user's reference images if supplied. This document is self-contained and does not require the original conversation.

## 1. Product intent and agreed decisions

The owner successfully built a compact desktop system-monitor app called Mint Meter. Rooz is a separate companion calendar app with a matching visual style. It is not an extension that requires Mint Meter to be installed.

The owner wants:

- A **small desktop date card**, inspired by a reference showing Persian, Gregorian, and Hijri dates side by side.
- A **full month calendar opened by double-clicking the card**, inspired by a Persian month grid with occasions and holiday indicators.
- Iranian events and official public holidays.
- A macOS-inspired appearance: rounded corners, clean type, subtle translucency, and mint accents.
- A compact footprint consistent with the approved Mint Meter widget. The owner previously rejected an oversized desktop widget.
- A **Start at login** setting.
- **English and Persian interface languages**.
- **Dark and light themes**, customizable accent, opacity, and scale.
- **Vazirmatn as the default font**, bundled for offline use, with font and text-size settings.
- Persistent settings and a `.deb` that works on Linux Mint 22.3 Xfce.

Working product name: **Rooz / روز**. Command and Debian package name: `rooz`. Initial app version: `0.1.0`; initial Debian revision: `-1`. Check for actual package/command conflicts before installation and document any necessary naming adjustment. This is an independent project, not an official Linux Mint or Apple product.

### Requirement priority

User requests above take priority. The dimensions, architecture, defaults, and repository structure below are recommended implementation choices intended to make the work concrete. Adapt them where necessary, explain material changes, and preserve the user experience.

## 2. How to execute this brief

1. Inspect the repository, applicable `AGENTS.md`/project instructions, OS, display session, and available tools.
2. Build a short implementation plan, then proceed through development, validation, documentation, and packaging.
3. Resolve ordinary technical choices autonomously. Ask only when missing information prevents a meaningful next step.
4. If the Mint Meter source is supplied, reuse suitable positioning, settings, and packaging patterns. If it is unavailable, implement Rooz independently without claiming to have inspected it.
5. Complete all feasible work before reporting an environment-specific blocker.
6. Do not claim compatibility, correct event coverage, installation success, or test results without evidence.

The latest visual mockup shows the compact card in the upper-right corner and a separate larger month window to its left, with charcoal surfaces and mint highlights. Reference images are **appearance guidance**; date conversion and calendar layout must come from tested code and verified data, not OCR of a generated mockup. Do not change the user's wallpaper, panel, system theme, or compositor.

## 3. Version 0.1 scope

### Required

- Three-calendar date card with weekday and today's occasions.
- Real month grid, selectable days, previous/next month, previous/next year or year selection, and a Today button.
- Events for the selected day, Friday styling, distinct public-holiday styling, and separate today/selection indicators.
- Offline event data with honest coverage reporting; at minimum a verified **1405 Solar Hijri** dataset, the reference year used in this brief.
- English/Persian interface and separate digit preference.
- Vazirmatn, dark/light appearance, accent, opacity, widget scale, and text-size settings.
- Drag, position lock, reset position, monitor recovery, and optional always-on-top.
- User-controlled login startup, single instance, application-menu launcher, and quit action.
- Copy date actions and a next-public-holiday countdown when supported data covers it.
- Automated calendar/data/configuration tests, GUI checks where possible, documentation, and `.deb` packaging.

### Later enhancements

Personal reminders, desktop notifications, calendar synchronization, `.ics` import/export, date search, additional cultural-event collections, alternate week layouts, tray integration, and true wallpaper blur. Keep extension points where useful, but do not implement these at the expense of a complete first release.

### Not required

Accounts, remote services, telemetry, AI features, web servers, web-based rendering, automatically scraping websites at startup, and automatically updating the app. Basic dates and packaged events must work offline.

## 4. Recommended implementation stack

Use **Python 3 + GTK 3/PyGObject + Pango + Cairo where needed**. GTK 3 is a practical default for an Xfce/X11 utility with desktop-window hints, placement, and normal settings dialogs.

- Use the system Python and target-compatible distribution packages for GTK/PyGObject.
- Use a maintained Jalali conversion library through a small calendar-service adapter. `jdatetime` is one candidate; verify its installed version, dependencies, supported range, license, and conversion results before adopting it.
- Use Python `zoneinfo.ZoneInfo("Asia/Tehran")` with available system timezone data. Do not hard-code a UTC offset.
- Use GTK/Pango for Persian shaping and bidirectional text. Do not implement glyph shaping or reverse strings manually.
- Keep conversion, calendar-grid generation, event lookup, formatting, and configuration independent of GTK.
- Native compilation is not required for a Python app to be packaged as a `.deb`.
- Avoid Electron, embedded browsers, and a browser backend for this utility.
- Target **X11 first**. Inspect the real session. Explain limitations on Wayland rather than claiming untested support.

Expected platform dependencies to verify include `python3`, `python3-gi`, `python3-cairo`, `python3-gi-cairo`, `gir1.2-gtk-3.0`, and `tzdata`. Declare the actual conversion/font-loading dependencies used. Prefer a suitable distribution package; if unavailable, package the needed compatible library and its transitive dependencies properly in the app's private path with notices. Do not run `pip install` at app launch or modify the system Python environment.

## 5. Compact desktop card

### Appearance

| Property | Default |
| --- | --- |
| Dimensions | Approximately **320 × 190 logical pixels** |
| Maximum default footprint | Around 340 × 220 if needed for readable Persian/event text |
| Placement | Upper-right of the primary monitor's usable work area |
| Edge margin | 24 logical pixels, clear of panels |
| Inner padding | 14–16 logical pixels |
| Corner radius | 16–18 logical pixels |
| Dark background | Charcoal near `#14252E`, around 90% background opacity |
| Light background | Warm off-white near `#F4F6F5`, with dark text |
| Main dark-theme text | Off-white near `#F0F5F7` |
| Secondary dark-theme text | Muted gray near `#B8C5CC` |
| Accent | Mint near `#5FE3AF`; use a darker accessible variant on light surfaces |
| Holiday color | Muted coral with sufficient contrast in each theme |
| Borders and separators | Subtle, low-opacity lines |
| Font | Vazirmatn |

Use shared design tokens for all windows. Scale in logical units rather than as a fraction of the screen. Keep the card small. Avoid large icons, excess toolbar buttons, marketing titles, or a clock that forces continuous updates.

Apply opacity to the background only, preserving crisp text. True blur is optional. With compositing disabled, use a readable opaque fallback. Rounded edges must not create opaque black corner artifacts.

### Content

1. Small Rooz title and settings gear.
2. Weekday label.
3. Three date columns with the Persian date visually dominant.
4. Fine separator and one or two lines of today's occasions.

Recommended physical column order: **Hijri on the left, Gregorian in the center, Persian on the right**, matching the reference. The Persian column remains primary in both interface languages. A tooltip can show the full date and timezone.

For each column show day number, month name, and year. Use separate text elements to keep numbers and labels aligned and avoid mixed-direction glitches. The Persian number may be approximately 28–32 px; secondary calendar numbers around 20–24 px; month names and years smaller but readable.

All dates must be computed for the same local civil day. Do not freeze the example date from the mockup. Current day, date labels, event count, and holiday status come from the calendar service.

If there are many events, show a prioritized short list plus a localized remaining count such as `۲ مناسبت دیگر` / `2 more events`. Preserve the compact height; show the complete list in the month window. Prioritize public holidays over ordinary occasions. Long titles should ellipsize with a full tooltip, not resize the entire card.

Differentiate:

- Verified data with no matching occasions: `امروز مناسبتی ثبت نشده` / `No occasions today`.
- Missing/partial coverage: `اطلاعات مناسبت‌ها کامل نیست` / `Occasion data is incomplete`.
- Source/load failure: a concise unavailable state with details in settings.

Do not treat unavailable data as an empty verified event list.

## 6. Full calendar window

- Open a normal separate application window on **double-click** of the compact card's non-control area.
- Keep the compact card present when the full calendar opens.
- Reuse one existing calendar window on repeated activation.
- Default size approximately **560 × 520 logical pixels**, adjustable for DPI and content; make it resizable.
- Provide a keyboard-accessible **Open calendar** action in the context menu so double-click is not the only route.
- Closing or pressing Escape in the calendar closes that view, not the background widget. A distinct Quit action exits the app.

### Header and navigation

- Primary month/year, e.g. `مهر ۱۴۰۵` / `Mehr 1405`.
- Secondary Gregorian month span, accounting for Persian months spanning two Gregorian months and occasionally years.
- Previous/next month controls with unambiguous tooltips.
- Today / `امروز` button.
- Year selection or previous/next year actions.
- Small settings and close controls, accessible by keyboard and screen reader.

### Grid rules

The default **Iranian week layout stays the same in both UI languages**: Saturday at the right, Friday at the left. English changes labels and control direction, not the calendar's logical date placement.

| Physical column, right to left | Persian label | English label |
| --- | --- | --- |
| 1 | شنبه | Sat |
| 2 | یکشنبه | Sun |
| 3 | دوشنبه | Mon |
| 4 | سه‌شنبه | Tue |
| 5 | چهارشنبه | Wed |
| 6 | پنجشنبه | Thu |
| 7 | جمعه | Fri |

Generate the grid from weekday offsets and month lengths; never maintain hand-written layouts for each month. Use five or six rows as needed, keeping cell dimensions stable. Blank cells or clearly subdued adjacent-month dates are acceptable, but they must not look like dates in the active month.

- Large primary Persian day number; optional smaller Gregorian day number, enabled by default.
- Friday styling reflects the regular weekly day off. Public holidays use an explicit additional marker/accessible label; do not classify every Thursday as a nationwide holiday.
- **Today:** outlined circle or rounded outline.
- **Selected day:** filled accent marker.
- If today is selected, render both states without ambiguity.
- Event dots indicate occasions without turning every cell into a large circle.
- Tooltips and accessible labels give the full date, events, and holiday status; meaning must not rely on color alone.
- Support keyboard focus, navigation, and activation of dates. Make previous/next chronological day handling correct despite RTL placement.

### Selected-day detail area

Below the grid, show the selected weekday and date, equivalent dates, and all relevant event titles. Use a scrollable detail area when necessary rather than letting event text force the desktop card or window off-screen.

Public holidays and ordinary occasions must be labeled separately. Small category tags may show national/cultural, religious, international, or public holiday; an occasion can have multiple categories. Missing data needs an explicit message.

Provide Copy Persian date, Copy Gregorian date, and Copy all dates via a small menu or buttons. Clipboard content is plain Unicode text.

## 7. Calendar correctness and time

### Civil day and timezone

- Default timezone: **Asia/Tehran**, independent of the machine's default timezone.
- Obtain one timezone-aware current instant and derive the civil date from it. All calendars and today's events use that same date.
- Offer Tehran / System timezone in settings if practical. Explain that this controls the displayed civil day, not the location of Iranian public holidays.
- Recompute at midnight in the chosen zone, on resume, and after detected clock/timezone changes.
- A lightweight reconciliation check, for example once a minute, is acceptable; redraw only when the day or settings change. Do not use the stats widget's once-per-second repaint loop unnecessarily.
- Use the system timezone database, including historical rules. A fixed `+03:30` conversion is insufficient for historical dates.

### Persian and Gregorian calendars

- Use actual month lengths, including 29/30-day Esfand depending on the year.
- Conversion must round-trip within the explicitly supported range.
- Verify year boundaries and leap years against authoritative references.
- Document a supported browsing/conversion range rather than promising unlimited astronomical accuracy. Clamp navigation at its boundaries with a clear message.
- Keep **conversion range**, **Iranian lunar-date mapping range**, and **event-data coverage** separate. A browsable date does not imply its occasions are known.

### Hijri dates and religious holidays

- A generic Islamic civil/Umm al-Qura calculation must not silently determine Iran's official holiday dates.
- For years with official Iranian data, use a date mapping checked against that year's Iranian calendar for both the Hijri display and lunar-based occasions.
- Outside verified mapping coverage, either show `Hijri unavailable` or an explicitly labeled approximate date in both languages. Document the chosen policy; prefer unavailable to falsely authoritative data.
- Never invent a Hijri month length or apply an unexplained one-day correction globally.
- Date-display algorithms do not replace annual event data. Keep the calendar adapter and event provider separate.

### Golden tests

Create independent expected-date fixtures from the official year source, not by calling the same conversion library used in production. Include every day of a supported year if practical and at least month starts, year transitions, and holiday dates. Source-based examples for 1405 include `1405-01-01 = 2026-03-21` and `1405-07-18 = 2026-10-10`; recheck them during implementation. Examples are not a complete dataset.

## 8. Iranian occasions and public-holiday data

### Source policy

The University of Tehran Calendar Center publishes the official Iranian calendar, including equivalent dates, occasions, and explicit holiday markings. Use it as a verification reference. See the primary links at the end of this document.

- Bundle a normalized, versioned annual dataset that works offline.
- Start with verified 1405 coverage; add other years only when their data can be checked. For a later release date, also obtain the actual current year's data rather than perpetually treating 1405 as current.
- Treat a parsed PDF or community repository as input that needs validation. PDF extraction can merge dates and break Persian text.
- Record source URLs, publication/revision information, retrieval date, coverage, and checksums where useful.
- Record licenses/notices for reused code, fonts, and event datasets. Select an appropriate source or data preparation route rather than assuming all public repositories are interchangeable.
- Do not transplant Android UI code or a complete app just because its screenshot is a reference.
- Use verified fixed dates for lunar-derived holiday occurrences within each annual dataset. Do not guess a future year's lunar holidays when data is absent.
- English event titles should be reviewed translations; untranslated titles may fall back to Persian with an honest indication, not fabricated English text.

### Suggested data model

Use one immutable data package per Solar Hijri year, plus a source manifest. A possible layout is `data/calendars/1405.json` with daily date mappings and an event list. Coverage metadata must state whether all days and all official events for the year have been checked.

```json
{
  "schema_version": 1,
  "solar_year": 1405,
  "data_version": "1405.1",
  "coverage": {
    "date_mapping": "verified",
    "official_occasions": "verified",
    "public_holidays": "verified"
  },
  "sources": [
    {
      "id": "ut-calendar-1405",
      "url": "https://calendar.ut.ac.ir/",
      "description": "Official annual calendar; retain the precise document URL in the real manifest"
    }
  ],
  "days": [
    {
      "gregorian_date": "2026-03-21",
      "jalali_date": "1405-01-01",
      "hijri_date": "1447-10-01"
    }
  ],
  "events": [
    {
      "id": "1405-nowruz-1",
      "gregorian_date": "2026-03-21",
      "title": { "fa": "آغاز نوروز", "en": "Nowruz begins" },
      "categories": ["national", "cultural"],
      "is_public_holiday": true,
      "source_id": "ut-calendar-1405"
    }
  ]
}
```

**This is a schema example, not a complete year.** Its single event does not mean that day has only one occasion. A real verified dataset must include all relevant records, including coincident holidays such as the religious occasions listed for the same day. Never ship this one-day example with `verified` coverage for the year.

Validation should check uniqueness, real date values, year membership, mapping consistency, bilingual title fields, source references, missing days, duplicate events, and valid public-holiday flags. Use a documented schema and a command that reports coverage and problems.

### Filtering and countdown

- Settings allow national/cultural, religious, international, and public-holiday display preferences.
- Category filtering changes visible occasions, not the underlying official holiday status.
- Public holiday is a property separate from religious/national classification.
- Separate dates that are Fridays from statutory holiday events.
- A next-public-holiday countdown should exclude ordinary Fridays by default. Count civil-date differences, not seconds divided by 86400.
- If verified data does not cover the search through the next year, display that limitation instead of declaring there are no upcoming holidays.

For version 0.1, distribute data updates through an app release or documented validated local-data installation. Runtime scraping or an online API dependency is unnecessary.

## 9. English, Persian, and number formatting

### Language settings

- Choices: **English** and **فارسی**.
- Default: Persian, with an easily recognizable language control in settings.
- Apply changes immediately to open windows, menus, tooltips, errors, and accessible labels. Persist the choice.
- Persian control layouts use RTL; English controls use LTR.
- Preserve the explicit Iranian calendar column order in both modes. Avoid letting a toolkit automatically mirror a manually positioned grid twice.
- Persian month names become standard English transliterations in English mode, e.g. `مهر` / `Mehr`, rather than substituting an unrelated Gregorian month.
- Prefer explicit app translations instead of requiring `fa_IR` to be installed or changing the user's global locale.

Use gettext or a small complete translation catalog. Include both languages from the first implementation, not as a later replacement pass. User/event text must be treated as plain text or safely escaped before GTK markup rendering.

### Digit style

The digit preference is independent of interface language:

- Persian: `۰۱۲۳۴۵۶۷۸۹`.
- Latin: `0123456789`.

Default to Persian digits. Apply the preference consistently to display dates, counters, years, and copied human-readable dates. Canonical storage and machine-readable ISO dates remain ASCII.

Use Persian Yeh/Kaf consistently and preserve appropriate half-spaces. Give mixed Persian/English strings, ISO dates, and paths explicit direction handling where necessary. Calendar cells and date columns should be separate widgets/layout elements, not manually reordered strings.

### Minimum translation inventory

| English | Persian |
| --- | --- |
| Open calendar | باز کردن تقویم |
| Today | امروز |
| Settings | تنظیمات |
| Language | زبان |
| Start at login | اجرا هنگام ورود |
| Theme | پوسته |
| Dark / Light | تیره / روشن |
| Font | قلم |
| Text size | اندازهٔ متن |
| Digit style | نوع ارقام |
| Background opacity | میزان کدری پس‌زمینه |
| Lock position | قفل موقعیت |
| Always on top | همیشه روی پنجره‌ها |
| Reset position | بازنشانی موقعیت |
| Copy date | کپی تاریخ |
| Public holiday | تعطیل رسمی |
| Occasion data unavailable | اطلاعات مناسبت‌ها در دسترس نیست |
| Quit | خروج |

Also translate weekday/month names, event-count plural forms, countdowns, explanatory help, and error states. Keep icons recognizable without relying on English words.

## 10. Vazirmatn and typography

Vazirmatn is the default for both interface languages. Use its standard variant containing Latin glyphs, not the Non-Latin-only variant. It supports a consistent bilingual interface without downloading fonts at runtime.

- Bundle a pinned upstream release's static TTF weights: **Regular, Medium, Semibold**. Include the appropriate license and attribution files; upstream publishes the font under SIL OFL 1.1.
- Use Regular for event descriptions/settings, Medium for weekdays/month names, and Semibold for prominent date numbers/headings.
- Load fonts through an app-private Fontconfig/Pango integration or another verified native mechanism. Do not silently change the user's system font settings.
- Confirm that the displayed Pango family is actually Vazirmatn. Document any font-loading dependency and packaging behavior.
- Settings offer **Vazirmatn / System default / Custom installed font** and a text-size adjustment.
- Use a readable fallback if a selected custom font disappears.
- Keep digit selection separate from font selection. Do not force all characters to Persian digits via a special font variant.
- Provide a live preview including a Persian sentence, English text, and both digit sets.
- Test ascenders/descenders, half-spaces, joining, mixed-script text, and 100%/200% DPI to avoid clipping.

Allow reasonable text scaling independently of card scale. Clamp settings to safe ranges and explain when larger text requires a slightly larger card. Do not produce an unreadable micro-widget just to preserve exact pixel dimensions.

## 11. Themes and settings

All three views—compact card, calendar, and settings—share design tokens and immediately reflect changes.

| Setting | Options / default |
| --- | --- |
| UI language | Persian default; English selectable |
| Digit style | Persian default; Latin selectable independently |
| Start at login | Off initially; user-controlled |
| Theme | Dark default; Light |
| Accent color | Mint default; selectable/custom |
| Background opacity | About 0.90; background only |
| Widget scale | 1.0 default; usable bounded range |
| Font | Vazirmatn default; system/custom installed font |
| Text scale | 1.0 default; independent of widget scale |
| Timezone | Asia/Tehran default; optional System setting |
| Gregorian cell numbers | On by default |
| Hijri date column | On by default; honest coverage state |
| Event categories | National/cultural, religious, international, public holidays |
| Next public holiday | Enabled when verified coverage permits |
| Lock position | Off by default |
| Always on top | Off by default |
| Show on all workspaces | On for compact card by default |
| Reset appearance / position | Separate actions |

Do not add an unreliable automatic system-theme setting solely for feature count. Dark/light are sufficient for version 0.1. If system following is added, verify actual Xfce behavior and retain explicit choices.

Settings should be an ordinary keyboard-accessible dialog organized into Appearance, Language & Dates, Events, and Desktop/Startup. Keep controls straightforward and localized. Do not put technical implementation details into normal settings explanations.

## 12. Desktop behavior and startup

### Window integration

- Compact card starts without stealing keyboard focus and sits above the wallpaper but below ordinary app windows.
- Avoid reserving desktop space or altering maximized-window geometry.
- Hide the card from the taskbar/pager where supported. Full calendar and settings windows behave as ordinary app windows and can receive keyboard focus.
- Show the compact card on all workspaces by default. Do not automatically stick the full calendar/settings to every workspace.
- Always-on-top applies to the compact card only unless separately specified. Never set keep-above and keep-below simultaneously.
- Test GTK/GDK/EWMH hints under Xfce's actual window manager and desktop. Hints are requests, not guarantees.
- Verify desktop clicks, workspace changes, and Show Desktop. Avoid override-redirect behavior that breaks input and reliable window management.

### Pointer and keyboard actions

- Double-click the card background/date area to open or raise the calendar.
- Gear opens Settings; it must not also trigger the card's double-click action.
- Drag a small header region to move the card when unlocked. Distinguish drag from click/double-click using a movement threshold.
- Right-click menu includes Open calendar, Settings, Copy date actions, Lock/Unlock position, Always on top, Reset position, and Quit.
- Do not assign immediate single-click copy to the same area that recognizes double-click, which could cause accidental copy behavior. Use explicit copy actions.
- Locking position must still allow calendar opening, settings, and context menus.
- Keyboard users can open the calendar/settings from the launcher or commands, navigate the grid, and activate controls.

### Placement and recovery

- Save position after dragging ends or with a debounce, not continuously.
- Persist monitor identity where practical, with fallback to the current primary monitor.
- Support monitors with negative coordinates and different scaling/work areas.
- Clamp restored coordinates to a usable monitor area after hotplug, resolution, or scaling changes.
- Provide a reset-position command usable even if the card cannot be found.
- When settings change widget dimensions, reposition as necessary to keep it visible.

### Startup at login

- The requested **Start at login** toggle creates/removes or enables/disables a **user-scoped XDG autostart** entry.
- Entry uses the installed stable Rooz command and launches only the compact widget, not the large month window.
- Derive the displayed setting from the actual autostart entry; avoid a separate unsynchronized boolean.
- Do not run as root, create a system service, or enable startup automatically during `.deb` installation.
- Make the development-checkout limitation clear if a stable installed executable path is unavailable.
- An uninstall guide must explain removing/disabling a leftover user startup entry without deleting unrelated files.

## 13. Lifecycle, commands, and persistence

Use a stable application ID, e.g. `org.roozcalendar.Rooz`, without assuming a GitHub owner. Implement single-instance handling through `Gtk.Application`/GApplication or an equivalent reliable mechanism. Repeated launch should raise the existing calendar or another useful view instead of creating duplicate widgets.

Provide these commands and document their exact behavior:

| Command | Behavior |
| --- | --- |
| `rooz` | Start compact widget; if already running, open/raise its calendar |
| `rooz --widget` | Start/ensure compact mode; suitable for autostart |
| `rooz --calendar` | Open/raise month view in the existing instance |
| `rooz --settings` | Open/raise settings |
| `rooz --reset-position` | Restore compact card to default visible position |
| `rooz --quit` | Gracefully terminate the existing app |
| `rooz --check-data` | Report dataset versions, coverage, and validation issues without a GUI |
| `rooz --version` | Print app version and exit |

Forward UI commands to the running instance. Display-independent commands must work without a graphical session. A GUI invocation without a usable display should produce a clear message. Use an explicit test/demo mode only if needed; it must never silently replace today's real data.

### XDG storage

- Configuration: `$XDG_CONFIG_HOME/rooz/config.json`, fallback `~/.config/rooz/config.json`.
- Optional user-supplied verified annual data: `$XDG_DATA_HOME/rooz/calendars/`, fallback `~/.local/share/rooz/calendars/`.
- Optional bounded logs: XDG state directory.
- System-bundled calendar/font assets: installed app resource paths, never a source-checkout-relative path.

No continuous sample logging, user-data writes inside `/usr`, or unexplained persistence of clipboard content.

Suggested configuration:

```json
{
  "schema_version": 1,
  "language": "fa",
  "digits": "persian",
  "timezone": "Asia/Tehran",
  "appearance": {
    "theme": "dark",
    "accent_color": "#5FE3AF",
    "background_opacity": 0.9,
    "widget_scale": 1.0,
    "font_mode": "vazirmatn",
    "custom_font_family": null,
    "text_scale": 1.0
  },
  "calendar": {
    "show_gregorian_cell_numbers": true,
    "show_hijri_column": true,
    "week_layout": "iran_rtl",
    "show_next_public_holiday": true
  },
  "events": {
    "visible_categories": ["national", "cultural", "religious", "international"],
    "show_public_holidays": true
  },
  "window": {
    "monitor": "primary",
    "anchor": "top-right",
    "margin": 24,
    "position": null,
    "locked": false,
    "always_on_top": false,
    "all_workspaces": true
  }
}
```

This deliberately omits an autostart boolean: the XDG startup entry is its source of truth.

Validate config enums/types, clamp numeric ranges, use atomic writes, and preserve malformed config in a backup before reverting to defaults. Include schema migrations for future releases. Save only when settings/placement change. Discard invalid user data packages with an actionable message while keeping the bundled dataset usable. Do not label custom data officially verified merely because it passes structural validation.

## 14. Internal architecture

Use a small separation of responsibilities:

| Component | Responsibility |
| --- | --- |
| Calendar service | Conversion, weekdays/month lengths, supported range, day snapshots |
| Clock/timezone service | Selected civil day, rollover and resume reconciliation |
| Month model | Logical rows/cells from real dates; independent of text direction |
| Event repository | Load/validate/index annual data; return events and coverage status |
| Formatter/localizer | Date labels, digits, translated UI, plural forms, clipboard formats |
| Theme/font service | Shared tokens, app-private font loading, live appearance updates |
| Desktop-window controller | Layering, movement, monitor recovery, single-instance commands |
| Config/autostart services | Atomic preferences, migrations, startup-entry management |
| GTK views | Compact card, month window, settings dialog, context menu |

A date snapshot should contain a canonical Gregorian civil date, converted Persian date, verified/approximate/unavailable Hijri status, localized presentation, event coverage, occasions, and holiday flags. Do not scatter contradictory date calculations across views.

Opening another month must not change the compact card's displayed current day. Track **today**, **displayed month**, and **selected day** separately. If midnight arrives while browsing another month, update today/event/countdown indicators without unexpectedly resetting navigation. Today button explicitly resets selection/navigation.

Cache annual datasets and month models as appropriate; invalidate when data, timezone, or relevant settings change. Avoid a needless background thread for simple date math. Any slow file work must not freeze the GTK loop.

## 15. Suggested repository structure

Adapt details to the actual project while retaining these responsibilities:

| Path | Purpose |
| --- | --- |
| `README.md` / `README.fa.md` | English/Persian features, install, usage, limitations |
| `pyproject.toml` | App metadata, dependencies, lint/test setup |
| `src/rooz/__init__.py` | Package/version metadata |
| `src/rooz/__main__.py` | Module entry point |
| `src/rooz/app.py` | Lifecycle, CLI, single instance |
| `src/rooz/calendar_service.py` | Jalali/Gregorian/Hijri adapter and range policy |
| `src/rooz/clock.py` | Timezone-aware day reconciliation |
| `src/rooz/month_model.py` | Week layout and date cells |
| `src/rooz/events.py` | Dataset validation, coverage, holiday lookup/countdown |
| `src/rooz/formatting.py` | Digits, date/clipboard presentation |
| `src/rooz/i18n.py` | Translation integration |
| `src/rooz/config.py` | Validation, persistence, migrations |
| `src/rooz/autostart.py` | User startup integration |
| `src/rooz/fonts.py` | Native bundled-font loading and fallback |
| `src/rooz/ui/widget.py` | Compact desktop card |
| `src/rooz/ui/calendar_window.py` | Month grid and event detail view |
| `src/rooz/ui/settings.py` | Preferences dialog |
| `src/rooz/ui/desktop.py` | Positioning, monitor/window-manager behavior |
| `src/rooz/ui/theme.py` | Shared tokens/CSS and accessibility contrast |
| `locale/` | English/Persian translation catalogs |
| `data/rooz.desktop` | Application-menu launcher |
| `data/icons/` | Original app icon |
| `data/fonts/vazirmatn/` | Pinned static TTF weights and notices |
| `data/calendars/1405.json` | Complete checked annual data |
| `data/calendars/manifest.json` | Coverage, sources, versions |
| `data/schemas/calendar.schema.json` | Dataset structure |
| `debian/` | Package control, rules, install and copyright metadata |
| `scripts/dev-run.sh` | Launch from checkout using documented dependencies |
| `scripts/build-deb.sh` | Repeatable package build |
| `scripts/validate-data.py` | Dataset schema/coverage checks |
| `tests/` | Independent logic and integration tests |
| `tests/fixtures/` | Sourced conversion/event expectations |
| `docs/BUILD_SPEC.md` | This brief |
| `docs/DESIGN.md` | Appearance, interaction, RTL decisions |
| `docs/DATA_SOURCES.md` | Annual provenance, verification, update procedure |
| `docs/TESTING.md` | Actual checks and remaining limitations |
| `docs/RELEASING.md` | Versions, package/checksum/release instructions |
| `docs/screenshots/` | Actual app screenshots, distinct from concept images |
| `.github/workflows/ci.yml` | Logic/data tests and package build |
| `.github/workflows/release.yml` | Explicit tag-triggered release preparation |
| `AGENTS.md` | Concise verified run/test/build instructions |
| `.gitignore` | Caches, build products, local user data, credentials |
| `CHANGELOG.md` | User-facing changes |
| `THIRD_PARTY_NOTICES.md` | Libraries, fonts, and data notices |
| `LICENSE` | Owner-selected app license |

Do not create empty modules solely to mimic a file list. A simpler arrangement is acceptable if responsibilities remain clear. Choose one authoritative app version. Do not maintain inconsistent parallel specifications in multiple agent-specific files.

## 16. Debian packaging and GitHub handoff

### Package

- Prefer standard debhelper packaging with appropriate Python helpers.
- Package name `rooz`, version `0.1.0-1`, expected artifact `dist/rooz_0.1.0-1_all.deb` if the contents are architecture-independent.
- Use `Architecture: all` only when appropriate. Native binaries require correct architecture handling.
- Install a stable `/usr/bin/rooz` launcher and place app modules/assets under standard Debian paths consistently.
- Install desktop entry and icon with valid metadata and translated display names where appropriate.
- Include bundled font/library notices and a Debian copyright record.
- Declare actual runtime dependencies so `apt` can resolve them. Bundle non-distribution dependencies appropriately when needed; no downloads on launch.
- Build as an ordinary user with proper package ownership, not an app executed as root.
- Installation must not alter the system theme, enable login startup, or launch Rooz automatically as root.
- Verify that an installed app can find fonts, translations, and calendar data when started from an unrelated working directory.
- Prefer no maintainer scripts unless necessary. Inspect package contents, run metadata checks and lintian when available, and explain material findings.

Document commands using the **actual** filename, for example:

```bash
sudo apt install ./rooz_0.1.0-1_all.deb
rooz
rooz --settings
```

Document package-manager removal, optional user-config deletion, and startup-entry cleanup separately. Removal must preserve user settings by default. Test install/launch/upgrade/removal in an appropriate disposable environment where available; do not remove unrelated user software to satisfy a test.

### GitHub

Prepare source, documentation, actual screenshots, `.deb`, and SHA-256 checksums. Keep binaries out of ordinary source commits and attach them as release assets.

The owner has not specified a GitHub account/repository or app license in this brief. Finish the reviewable local project first. Do not invent an owner or remote, silently select a license, or publish without live-session instructions identifying the destination. If the owner supplies the repository and authorization, use normal authentication and deliver the actual release URL; otherwise list only the concrete remaining publication decisions. These decisions need not block implementation/testing.

Do not copy secrets, personal calendar entries, real user config, or machine-specific details into the repository. Concept images may be kept as design references if supplied, but README screenshots must clearly show the real app.

CI should run logic tests, translation/data validation, and a package build on a compatible baseline. A virtual-display GTK smoke test is useful where available, but not proof of Xfce desktop behavior. Verify current CI action versions during implementation. Release publishing should have explicit tag triggers and narrowly scoped permissions; simply opening the repository must not publish anything.

## 17. Performance, privacy, and accessibility

- Run as an ordinary user; no privileged service is needed.
- Remain usable offline after package dependencies are installed.
- Make no routine external requests. Data provenance/update instructions belong in docs/settings, not a live API dependency.
- Use event-driven updates and lightweight day checks. Avoid animations or redraws at video frame rates.
- Bound logs and caches; stop timers and release resources when quitting.
- Aim for negligible idle CPU and approximately 100 MiB RSS or less on a typical desktop. These are targets; measure on actual hardware and report limitations rather than inventing performance figures.
- Handle missing timezone data, missing fonts, malformed event files, invalid configuration, and unavailable graphical sessions clearly.
- Ensure text contrast in both themes and with custom accent colors; use a contrasting foreground for selected dates.
- Add accessible names to gears/arrows/dates and preserve keyboard focus indicators.
- Keep calendars understandable without color through labels/markers/tooltips.
- Opening the calendar/settings may request focus; background widget startup should not.

## 18. Automated validation

Test meaningful logic and integration boundaries with deterministic fixtures, a fake clock, and temporary XDG directories. Do not mirror implementation with tests that simply repeat its own calculations.

### Calendar and clock

- Jalali/Gregorian round trips in the supported range, independently checked dates, leap years, Nowruz, and Esfand boundaries.
- Months beginning on each weekday, months requiring six rows, and exact 29/30/31-day counts.
- Default visual grid mapping: Saturday rightmost, Friday leftmost, exactly one cell per date.
- Selecting a day updates details without changing the card's today state.
- Previous/next month/year and Today actions across year boundaries.
- Midnight, resume, backward/forward clock changes, and differing system/Tehran dates.
- Historical Tehran timezone behavior where the supported range includes it.
- Verified Hijri mapping, approximate/unavailable behavior, and lunar-data coverage boundaries.

### Event data

- Every mapped day in a verified year is present exactly once.
- Independently sourced official holiday dates, coincident occasions, duplicate handling, and coverage manifests.
- Public-holiday flags remain distinct from Fridays and from event categories.
- Missing years/partial data are not presented as no events.
- Countdowns count calendar days, handle a holiday today, and detect missing next-year coverage.
- Filtering hides relevant occasions without falsifying underlying holiday status.
- English title fallback and source identifiers remain valid.

### Localization, settings, and integration

- English/Persian translation keys, count plurals, digit conversions, month names, and clipboard formats.
- Canonical ASCII dates remain unchanged by localized digit preferences.
- Malformed config backup/recovery, bounds, migration, atomic saving, and immediate apply.
- Autostart entry opt-in/out in temporary directories; installed command and CLI semantics.
- Position clamping with negative/mixed-monitor coordinates and font fallback logic.
- Headless data/version commands; GUI single-instance open/quit smoke test where possible.

Text shaping, visual clipping, compositor stacking, and real input gestures require GUI inspection; unit tests alone are insufficient.

## 19. Manual acceptance checklist

Record each item as **passed, failed, or not tested** with the OS/session/tool versions used.

- [ ] Real compact card is around 320 × 190 logical pixels at default scale and never becomes an oversized sidebar.
- [ ] Persian date is prominent; all three dates refer to the same civil day.
- [ ] Weekday and today's occasions are readable without clipping.
- [ ] Double-click opens one full calendar; gear/right-click/drag do not trigger conflicting actions.
- [ ] Month starts, day counts, weekday placement, Fridays, and official holidays are correct.
- [ ] Today and selected day have different visible and accessible states.
- [ ] Event details, copy actions, category filters, and countdown behave as documented.
- [ ] Unsupported data years show an honest coverage message.
- [ ] English and Persian immediately update every view/menu/tooltip, with correct control direction.
- [ ] Digit style can change independently of UI language.
- [ ] Vazirmatn is actually loaded; Persian joining, half-spaces, digits, and mixed English text display correctly.
- [ ] Dark/light themes and custom accent have readable contrast.
- [ ] Font/text/card size changes work at 100% and 200% DPI without hiding controls.
- [ ] Transparency works with compositing; opaque fallback remains readable without it.
- [ ] Drag, lock, reset position, restart persistence, and display hotplug work.
- [ ] Widget is above wallpaper/below normal windows, with optional always-on-top.
- [ ] Xfce desktop click, Show Desktop, workspace change, and panel interaction do not lose the widget.
- [ ] Midnight, suspend/resume, and clock changes update dates without resetting unrelated navigation.
- [ ] Start at login is opt-in, launches compact mode, can be disabled, and shows the actual saved state.
- [ ] Single-instance commands and quitting work; reopening the app does not duplicate cards.
- [ ] Installed app runs offline and outside the source checkout with fonts, data, and translations available.
- [ ] `.deb` metadata, install, upgrade, launch, and removal are checked where possible.
- [ ] Sustained idle session shows no unbounded memory, logs, or frequent repainting.

If Mint 22.3 Xfce or an actual desktop is unavailable, finish all feasible development, tests, and packaging and explicitly list the checks that still need the user's machine. An Ubuntu container or virtual X server cannot establish full target-desktop compatibility.

## 20. Delivery milestones

### Milestone 1 — Correct calendar core

Implement timezone/clock, conversion adapter, real month grid, dataset schema, annual-data validation, coverage states, independent golden fixtures, and localization infrastructure. Establish a verified current/reference-year dataset. No fixed sample date masquerading as live data.

### Milestone 2 — Approved visual design

Build the small card and separate month window with live calendar data, Vazirmatn, RTL layout, distinct today/selection/holiday styles, and event details. Compare actual screenshots to the mockup. Verify size early.

### Milestone 3 — Usable desktop app

Finish bilingual settings, theme/font/digit controls, copy/countdown actions, desktop integration, single instance, position recovery, and user autostart. Verify all settings persist and update live.

### Milestone 4 — Installable release

Complete docs/CI/notices, build and inspect the `.deb`, execute feasible acceptance checks, take actual screenshots, and prepare checksums/release instructions. Publish only according to the owner's supplied destination and authorization.

Do not stop at any intermediate milestone unless a concrete blocker prevents further work. Complete independent tasks and identify that blocker precisely.

## 21. Definition of done and final report

The first version is complete when required behavior is implemented, calendars/events are validated within declared coverage, the UI is reviewable, and an installable package is produced. Optional later features need not be built.

The coding agent's final response should provide:

1. Source location and concise description of implemented behavior.
2. Actual `.deb` path and SHA-256 checksum file.
3. Exact install, launch, settings, reset, test, data-check, build, and uninstall commands.
4. An actual screenshot if graphical execution was possible.
5. Tested calendar range, verified data years/source revisions, and Hijri coverage policy.
6. Checks performed and any unverified Mint/Xfce behavior.
7. Resource usage only if measured, with context.
8. GitHub release status or the specific remaining owner decisions.

Never label a concept image a screenshot of the completed app or state that tests passed without running them.

## 22. Primary references

Verify installed/current versions while implementing. Links here are reference sources, not runtime dependencies.

- [University of Tehran Calendar Center](https://calendar.ut.ac.ir/)
- [Official Iranian calendar for 1405, final PDF](https://calendar.ut.ac.ir/documents/2139738/7092644/Calendar-1405.pdf/64228cbb-f4de-dc32-4d2b-57db3c8e322f?t=1761972997587)
- [Vazirmatn upstream font and license](https://github.com/rastikerdar/vazirmatn)
- [PyGObject GTK 3 resources](https://pygobject.gnome.org/tutorials/gtk3.html)
- [GTK 3 Window API](https://docs.gtk.org/gtk3/class.Window.html)
- [GTK keep-below window-manager caveats](https://docs.gtk.org/gtk3/method.Window.set_keep_below.html)
- [Pango documentation](https://docs.gtk.org/Pango/)
- [jdatetime upstream](https://github.com/slashmili/jdatetime)
- [Python zoneinfo](https://docs.python.org/3/library/zoneinfo.html)
- [Xfce documentation](https://docs.xfce.org/)
- [XDG Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
- [XDG Autostart Specification](https://specifications.freedesktop.org/autostart-spec/latest/)
- [Debian Policy](https://www.debian.org/doc/debian-policy/)

## 23. Prompt to start the coding agent

Copy this instruction along with the Markdown file and optional mockup images:

> Read `ROOZ_CALENDAR_BUILD_SPEC.md` completely. Build the working Rooz Persian calendar desktop app for Linux Mint 22.3 Xfce. Implement the compact widget, double-click month view, verified offline Iranian occasions and holidays, Persian/English interface, Vazirmatn, dark/light themes, user login-startup toggle, persistent settings, tests, and `.deb` packaging. Make ordinary technical decisions and finish all feasible milestones. Inspect actual screenshots and report real test results, data coverage, and remaining target-environment checks. Use supplied mockups for appearance, never as a source of date calculations. Prepare a GitHub-ready repository and release artifacts; use publication instructions from our live session if provided.
