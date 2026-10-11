# Roozlet — Complete Four-Season UI Redesign Brief

**Repository:** https://github.com/saeedt20/Roozlet  
**Target desktop:** Linux Mint 22.3 Xfce, X11 first  
**Brief date:** 2026-10-11  
**Owner:** Saeed Taheri / `saeedt20`  
**Visible product name:** **Roozlet / روزلت**  
**Suggested next version:** `0.2.0`, subject to the repository version when implementation starts.

> This is an implementation brief for Codex or Claude Code. Continue the existing Roozlet project. Read this entire file and the repository instructions, implement the redesign, verify it, update the documentation, and build a reviewable Debian package. Deliver working native application code and real assets, not just a plan or a static mockup.

**خلاصهٔ فارسی:** رابط روزلت با چهار ظاهر بهار، تابستان، پاییز و زمستان بازطراحی شود. تاریخ شمسی در ویجت همیشه دقیقاً وسط و برجسته‌تر باشد؛ میلادی سمت چپ و قمری سمت راست. فونت وزیرمتن، فارسی و انگلیسی، تنظیمات شروع با ورود به سیستم، تاریخ عددی، کپی تاریخ، مناسبت‌های ایران و امکانات فعلی حفظ شوند. تصاویر در حاشیه‌ها باشند و نوشته‌ها خوانا بمانند. این کار ادامهٔ پروژهٔ موجود است.

## 1. Instruction to the coding agent

Use the repository above, or the existing local checkout provided by the owner. Do not start a replacement application in a different framework.

1. Inspect `git status`, the current branch, version, applicable `AGENTS.md`, and the relevant source files before editing.
2. Preserve unrelated local changes. Use an isolated branch/worktree when necessary; never reset or discard the owner's work.
3. Inspect current `main`. The snapshot described here was version `0.1.1`, at commit `5c9b86b2b342714605d8923fd7d7a1170b54ddcf`. Treat this as a reference snapshot, not a request to check out or overwrite an older revision.
4. Read `docs/BUILD_SPEC.md`, `docs/DESIGN.md`, `docs/DATA_SOURCES.md`, `docs/TESTING.md`, and `docs/RELEASING.md`.
5. Make a short implementation plan, then complete the code, assets, validation, documentation, and package work.
6. Resolve ordinary implementation details autonomously using the defaults in this brief. Report meaningful deviations and actual environmental limitations.
7. Preserve the working calendar/data/packaging architecture and the existing fixes. Refactor only where the redesign needs it.
8. Complete local reviewable deliverables. Follow the repository's publication rules; creating this brief does not itself authorize pushing, merging, tagging, or publishing a GitHub release.

This brief updates the older build brief's **visible branding, widget date order, and appearance design**. It does not replace its accuracy, offline operation, desktop behavior, or compatibility requirements. Resolve conflicting visual descriptions in favor of this brief and update the outdated design documentation. Do not silently remove safeguards or working features.

## 2. Product goal and scope

Roozlet is a small, offline Persian calendar desktop companion. It already works and needs a cohesive visual redesign with four seasonal appearances.

The owner likes macOS-inspired rounded panels, crisp typography, restrained translucency, atmospheric seasonal scenery, and a compact desktop footprint. Roozlet remains a native Linux utility, independent of the owner's Mint Meter system-monitor widget.

### Required for this redesign

- A compact desktop widget with the **Shamsi date physically centered**, largest and most prominent.
- Four complete seasonal themes, including artwork, palette, icons, and control states.
- Automatic season selection and manual season override.
- Dark/light appearance independent of the seasonal choice.
- Optional simple appearance without scenic artwork, plus the existing custom-accent capability.
- A redesigned full month calendar with an adaptive navigation sidebar, selected-day details, working copy controls, and easy month/year selection.
- A complete, matching settings interface with seasonal previews.
- Persian and English interfaces; independent Persian/Latin digit selection.
- Vazirmatn as the bundled default font.
- Existing Iranian occasion/holiday data and its honest coverage reporting.
- Configuration compatibility, working installed assets, actual screenshots, and an installable `.deb`.

### Preserve, rather than reimplement unnecessarily

Date conversion, official Iranian Hijri lookup, event categories, holiday countdown, numerical-date preference, explicit numerical copy actions, header dragging, position lock/reset, monitor recovery, startup preference, single instance, and existing keyboard navigation.

### Separate future work

Week/day layouts, personal notes, reminders, notifications, calendar synchronization, `.ics` import/export, weather, wallpaper downloads, tray integration, and automatic updates are not part of this redesign. Do not add buttons for unimplemented features. The decorative sun/snowflake/leaf icons indicate seasons, not live weather.

## 3. Visual references and interpretation

The owner supplied four seasonal concepts: winter, summer, spring, and autumn. A later approved autumn concept shows the proposed centered Shamsi widget and a readable full calendar with its Persian sidebar on the right.

**Reference priority:**

1. The latest autumn concept governs composition, centered widget hierarchy, and restrained readability.
2. The original four concepts govern the atmosphere and identity of each season.
3. The measurements and functional requirements below govern the actual app when a concept image exaggerates size or decoration.

If the owner attaches the latest concept to the coding session, inspect it. An optional local filename is `roozlet-autumn-ui-reference.png`. The brief is self-contained if images are unavailable; do not invent an attachment path or make missing screenshots a reason to stop all implementation.

Preserve these visual qualities:

- Smoked glass surfaces, fine borders, soft corners, understated shadows.
- A calm, readable date grid with artwork concentrated at edges and in a lower scenic band.
- Consistent simple outline icons and a distinctive orange/colored leaf brand mark.
- Seasonal emphasis on selected controls and the Shamsi date.
- Small, carefully aligned typography and controlled whitespace.

Do not reproduce generated-image errors: incorrect date conversions, duplicate grid numbers, mismatched seasons/months, invented occasions, or the winter button label “تاریخ زمستانی”. The correct calendar label is always **تاریخ شمسی**. Never use the entire UI concept image as an application background or fake working controls with a screenshot.

The background landscape surrounding a concept is optional wallpaper styling. This project must not change the user's desktop wallpaper, panel, system theme, compositor, or window-manager configuration.

## 4. Existing architecture to retain

At the reviewed snapshot, the application uses **Python 3, GTK3/PyGObject, Pango/PangoCairo, and Cairo**. The compact card is a custom-painted `Gtk.ApplicationWindow` with a native settings button. The calendar and settings use native GTK widgets. Calendar calculations and event lookup are separate from UI rendering.

| Existing path | Current responsibility | Redesign responsibility |
| --- | --- | --- |
| `src/rooz/app.py` | Application lifecycle, clock reconciliation, shared refresh, clipboard | Theme contexts, visible branding, reusable view lifecycle |
| `src/rooz/ui/widget.py` | Compact card, Cairo/Pango drawing, drag/menu/gear | Centered date geometry, scenic layers, new interactive occasion affordance |
| `src/rooz/ui/calendar_window.py` | Native month grid, selection, navigation, details | Adaptive shell/sidebar and themed month view |
| `src/rooz/ui/month_picker.py` | Twelve-month/year popover | Reuse from title click and existing Today actions |
| `src/rooz/ui/settings.py` | Appearance, dates, events, desktop/startup | Seasonal previews and additional validated settings |
| `src/rooz/ui/theme.py` | Color tokens, contrast-aware accents, GTK CSS | Shared seasonal tokens and safely scoped window styles |
| `src/rooz/config.py` | Validated preferences, atomic writes, recovery | Additive defaults and legacy migration |
| `src/rooz/i18n.py` | Persian/English strings and localized digits | Every new label, tooltip, status, and accessible name |
| `src/rooz/formatting.py` | Text/numerical date formatting | Preserve; share across tooltip/details/clipboard |
| `src/rooz/calendar_service.py` | Conversion, month cells, timezone clock | Preserve calendar engine; expose pure season selection if useful |
| `src/rooz/events.py` | Verified annual data, categories, coverage | Preserve; reuse for occasion list and data status |
| `src/rooz/resources.py` | Source/installed asset resolution | Seasonal assets independent of current working directory |
| `src/rooz/fonts.py` | Application-private bundled fonts | Preserve offline registration and fallback |
| `src/rooz/autostart.py` | User XDG startup entry | Preserve behavior; update visible name |
| `scripts/package.py` | Rootless package staging/build | Include all new assets and notices |
| `scripts/source-archive.py` | Source archive/checksums | Include source assets; retain reproducibility |

Keep GTK3 for this update. Do not introduce Electron, a web view, a web server, a Qt rewrite, a mandatory GPU effect, or a runtime dependency downloader.

## 5. Branding and upgrade identity

Change user-visible branding to **Roozlet** in English and **روزلت** in Persian. Audit widget/header text, window titles, Settings/About, launcher names, font preview text, startup entry names, help/version output, README files, package descriptions, and release documentation.

Keep the technical identifiers that preserve updates and existing installations:

- Python import package: `rooz`.
- Executable: `/usr/bin/rooz`; current command-line options remain valid.
- Debian package identity: `Package: rooz`.
- Existing configuration directory: `$XDG_CONFIG_HOME/rooz/`.
- Existing user calendar-data directories and formats.
- Desktop launcher and autostart filenames: `rooz.desktop`.
- Existing application ID `org.roozcalendar.Rooz` and current window-manager matching identifiers unless a separately verified migration requires a change.

Changing a displayed title does not require changing the package, application ID, `WM_CLASS`, or executable. Keep `StartupWMClass` consistent with the actual application. Do not create two running applications or duplicate startup entries.

External downloadable names use Roozlet, as the current build already does:

- `roozlet_<VERSION>-1_all.deb`
- `roozlet-<VERSION>-source.tar.gz`
- `SHA256SUMS`
- Suggested release title: `Roozlet <VERSION>`.

The logo should remain recognizable across seasons. Use one stable leaf brand mark with seasonal coloring; use a **separate seasonal icon** in the Shamsi card. In winter that seasonal icon must be a snowflake.

## 6. Shared visual system

### Surfaces and spacing

Use a shared set of tokens for background, raised surface, grid surface, text, muted text, border, separator, accent fill, readable accent text, selection foreground, holiday color, hover, focus, corner radii, and spacing.

- Spacing scale: approximately `4, 8, 12, 16, 24` logical pixels.
- Widget outer radius: `17–18` logical pixels.
- Main window/panel radius: `16–20`; internal date/control radius: `8–12`.
- Fine borders: about `1` logical pixel; focus/today outlines may use `2`.
- Surfaces stay calm; accent fills occupy a minority of the interface.
- Apply transparency to background surfaces, not to text or icons.
- Glass is a visual treatment achievable with tint, static artwork, gradients, borders, and shadows. True live wallpaper blur is not required.
- When compositing is unavailable, use a clean opaque background and readable edges.
- Do not draw bright artwork immediately under small text or wash the grid in a vivid photo.

### Starter palettes

These are initial design values, not an excuse to bypass contrast validation.

| Season | Scenic identity | Dark accent seed | Light accent seed | Icon |
| --- | --- | --- | --- | --- |
| Spring / بهار | Pink blossoms, fresh greenery, morning light, lake/mountains | `#E99ABB` | `#A63B69` | Five-petal blossom |
| Summer / تابستان | Green foliage, clear lake, warm sun, bright mountain sky | `#E6C45C` | `#805E0C` | Simple sun |
| Autumn / پاییز | Copper leaves, warm sunset, forest/lake/mountains | `#F2A15B` | `#A34D15` | Autumn leaf |
| Winter / زمستان | Snow-covered trees, blue mountains, warm distant cabin lights | `#82C8F4` | `#216995` | Snowflake |

Suggested common dark foundation: `#171D27`, raised surface near `#222A36`, main text `#F3F5F7`, secondary text near `#BDC7D2`. Suggested light foundation: `#F6F4F0`, raised surface `#FFFFFF`, main text `#202630`, secondary text near `#596370`. Use subtle seasonal tint rather than unrelated layouts.

Keep holiday semantics stable: readable coral/red on dark surfaces and a darker red on light surfaces. Ordinary Fridays, statutory holidays, event dots, selection, and today remain distinguishable by shape/text as well as color.

Use contrast-aware selected foregrounds and separate readable text/outline accents. In particular, summer gold must not produce unreadable yellow text on a light surface. Aim for at least `4.5:1` for ordinary text and `3:1` for large text and meaningful control boundaries against their actual backed surfaces.

### Typography

- Bundle and load the existing Vazirmatn Regular, Medium, and SemiBold files for both languages.
- Use approximately 400 for normal text, 500 for labels, and 600 for primary dates/headings.
- Keep independent font-family and text-scale settings, including a clear fallback if a chosen custom font is unavailable.
- Use Pango for Persian shaping and bidirectional layout. Never reverse displayed strings manually.
- Separate mixed-direction calendar fields where necessary; keep numeric date strings in an appropriate directional span while surrounding Persian UI remains RTL.
- Avoid all-caps labels, decorative font substitutions, and undersized years.

### Icon family

Use one consistent outline family at roughly 16–22 logical pixels for controls. Include calendar, settings gear, clipboard, previous/next chevrons, list/occasion, information, sun/today, and the four seasonal symbols. Bundle needed assets or draw simple icons consistently with Cairo; do not depend on platform emoji appearance. If SVG loading needs a decoder not already guaranteed, declare it or supply small raster fallbacks.

## 7. Seasonal behavior

Compute automatic seasons from the **current Solar Hijri month**, using the same configured civil day as the date display:

| Jalali months | Season |
| --- | --- |
| 1–3: فروردین، اردیبهشت، خرداد | Spring |
| 4–6: تیر، مرداد، شهریور | Summer |
| 7–9: مهر، آبان، آذر | Autumn |
| 10–12: دی، بهمن، اسفند | Winter |

Recommended precedence:

1. `style=classic` uses the retained plain appearance and custom accent.
2. `style=seasonal` plus a manual `season` uses that season everywhere.
3. `style=seasonal`, `season=auto`, normal behavior uses today's season everywhere.
4. Only when automatic mode and **Follow displayed month** are enabled does the full calendar use the season of its browsed Jalali month. The widget and Settings remain on today's season.

Thus manual selection always wins. Disable the follow-month control outside automatic seasonal mode, with a short localized explanation. Merely selecting another day inside a month does not cause unrelated theme changes.

Dark/light choice and digit/language preferences are independent of season. A user can choose light winter or dark summer. The seasonal theme supplies the accent by default; a separate custom-accent option overrides control accents without changing the scene or season icon.

Refresh at the existing civil-day/timezone reconciliation point and after setting changes. Handle sleep/resume and year/season boundaries. Do not use UTC month, Gregorian month, or a hard-coded Tehran offset to choose the season.

No snow/petal/leaf particle animation by default. A static scene is sufficient. Do not add a new high-frequency redraw loop for decorative effects.

## 8. Desktop widget: geometry and hierarchy

### Compact footprint

The current card is `320 × 208` logical pixels. Use approximately **320 × 236** as the redesign starting point, with a default upper bound around **340 × 250** only if measured Persian text and the footer require it. Preserve compactness rather than reproducing the concept image's apparent large size.

Widget scale and text scale remain independent. At default scales the entire widget must fit this compact range; larger text may increase height deliberately. Clamp effective geometry to the monitor work area and retain panel-safe positioning. Derive all hit regions, icon placement, and text widths from the same layout calculation.

Suggested layout at the base size:

| Region | Approximate treatment |
| --- | --- |
| Outer inset | 14–16 px |
| Header | Brand/gear row, roughly 28 px |
| Weekday | Centered, 11–12 px text |
| Date area | Roughly 110–122 px high |
| Primary day | 34–38 px, semibold |
| Auxiliary day | 22–25 px, medium |
| Month | 10.5–12 px; ellipsize only if necessary |
| Year | 10–11 px |
| Footer | Separator, occasion summary, optional holiday countdown |

These are starting measurements. Validate rendered glyph metrics at both languages and text scales instead of relying on fixed text widths guessed from Latin labels.

### Mandatory physical order

| Physical left | Physical center | Physical right |
| --- | --- | --- |
| Gregorian / میلادی | **Shamsi / شمسی** | Iranian Hijri / قمری |

This order follows the latest approved autumn concept. It stays the same in English and Persian. The **centerline of the Shamsi card and its main number must coincide with the widget's content centerline**; an RTL switch must not reorder it.

- Shamsi gets the largest number, a compact seasonal icon, a tinted rounded panel, and a subtle accent border.
- Auxiliary calendars get smaller numbers, quieter borders/surfaces, and no competing vivid fill.
- Each column shows day, localized month name, and year for the same civil date.
- Keep the center card only slightly taller/more prominent; avoid turning it into a giant hero panel.
- Place the weekday above the columns, centered across the full content width.

Add independent widget visibility settings for Gregorian and Hijri. Shamsi is always visible. Hiding an auxiliary column must not move Shamsi off center: preserve equal invisible side-slot widths and omit hidden content, or use another explicitly symmetrical layout. Do not center the group of remaining columns if that displaces Shamsi. When both auxiliaries are hidden, keep one modest Shamsi card centered.

When official Hijri data is unavailable, a visible Hijri column shows a dash and localized “Unavailable” state with a tooltip. Do not substitute an approximate lunar date without a separate verified data source and policy.

### Header and artwork

- Persian: brand aligned to the right outer inset, gear on the left.
- English: brand aligned to the left outer inset, gear on the right.
- Brand consists of the localized product name and a small stable leaf mark.
- Reserve the gear's full hit area before laying out the title; keep them from overlapping at larger text sizes.
- Keep the current native settings button and its tooltip/accessibility label. Aim for a usable 28–32 px hit target, independently of the icon's drawn size.
- Concentrate scenery around a corner/top edge or a subtle lower band. Apply a dark/light backing underneath date text; retain full text opacity.

### Footer and data states

Show one prioritized occasion summary, optionally followed by a localized count such as `۲ مناسبت دیگر` / `2 more occasions`. Prefer a visible public holiday first. Keep long text within the allocated width, using ellipsis plus full tooltip.

- Verified date with no matching events: `امروز مناسبتی ثبت نشده` / `No occasions today`.
- All matching events hidden by filters: an explicit filtered state.
- Uncovered year/date: explicit incomplete/unavailable coverage, not “No occasions”.
- Load or validation failure: concise unavailable state with details accessible from Settings.
- When enabled and supported, show the next verified statutory public-holiday countdown on the second footer line. Preserve the existing semantics that ordinary Fridays are separate from public holidays.

Clicking the occasion summary or its “more” affordance opens the full calendar with today selected and its complete occasion list reachable. Keep the compact height stable regardless of event count. A small Open calendar affordance may be used when it fits; it must not replace an enabled holiday countdown or introduce a permanent extra row by default.

### Existing widget interactions to preserve

- Double-click the non-control body to open/raise the reusable calendar window.
- Gear opens/raises Settings; interacting with it does not start a drag or open the calendar.
- Header dragging uses the current motion threshold and saves after drag completion.
- Position lock, reset, monitor recovery, all-workspaces behavior, and optional always-on-top remain functional.
- Right-click retains Open calendar, Settings, copy actions, lock/layer actions, reset, and Quit.
- Keep **Copy numerical date** with Shamsi, Gregorian, Hijri when available, and All dates. Explicit numerical copying works without enabling the global preference.
- Hover shows full date information and configured timezone, respecting numerical-date and digit choices. Footer tooltips can additionally show the full occasion title.
- Closing a full window does not terminate the card.

## 9. Expanded month calendar

### Adaptive shell

Use approximately **860 × 680** logical pixels as a starting default for the redesigned window. Clamp opening dimensions to the current monitor work area. The existing smaller calendar can remain the compact responsive layout.

Suggested sidebar width is `140–160` px on sufficiently wide windows. At constrained widths, collapse it into a compact navigation control or accessible menu. Permit content scrolling when height or DPI requires it; every action remains reachable. Test widths around 420, 680, and 860 rather than imposing a desktop-sized minimum.

Persian sidebar is on the **right**; English sidebar is on the **left**. Month grid order is independent of sidebar mirroring. Use window-manager/native functional controls. macOS inspiration concerns the surfaces and spacing; decorative traffic-light controls are not required.

Sidebar items and concrete behavior:

| Persian | English | Action |
| --- | --- | --- |
| تقویم | Calendar | Show the month grid and selected-day details |
| امروز | Today | Select today's date and show its month |
| مناسبت‌ها | Occasions | Show an in-window list for the currently displayed month |
| تنظیمات | Settings | Open the existing reusable Settings window |
| درباره | About | Show a small actual About dialog/panel |

Use a visual divider before Settings/About. Preserve the displayed month and selected date when moving between Calendar and Occasions. In the Occasions view, group items by civil day, apply the user's existing event filters, show public-holiday badges, and let an item select that date in the calendar. For months without supported data, show the coverage state. Do not create another data engine.

About includes Roozlet/version, owner, project URL, MIT license, and an accessible route to data/font/artwork attribution. Use existing provenance documents rather than claiming all assets share the source-code license.

### Header and navigation

- Localized Jalali month/year is the main title, with a dropdown chevron.
- Clicking the title opens the **existing 12-month picker**, enhanced as needed.
- Show the correctly computed Gregorian date span below the title. Handle two Gregorian years when a Jalali month crosses a year boundary.
- Provide Previous month, Today, and Next month controls with localized tooltips and accessible names.
- Retain year navigation through existing controls or the month/year picker.
- Ordinary left-click Today resets to today. Right-click Today and its keyboard context-menu action still open the picker.
- Do not add nonfunctional Month/Week/Day tabs.

### Grid and date states

- Use real `month_cells()`/calendar-service results.
- **Saturday is physically rightmost; Friday is physically leftmost in both languages.**
- Generate the actual needed five or six rows; never copy positions/numbers from reference imagery.
- Keep equal column widths, stable row spacing, visible text, and distinct focus outlines.
- Primary cell number is Shamsi. Gregorian secondary numbers follow the existing independent setting; disabling them must not remove occasion/holiday markers.
- Existing blank leading/trailing cells may remain blank; adjacent-month dates are not required.
- Selected date: seasonal accent fill with an accessible foreground.
- Today: outline/ring. Today plus selection: show both signals.
- Friday: consistent weekly-off styling.
- Statutory public holiday: distinct badge/diamond and accessible status, even when occasion filters hide its textual event.
- Ordinary occasion: small dot or equally subtle marker.
- Hover/focus tooltip includes full date, relevant statuses, and occasions using the existing formatting/data services.

Keep native focusable GTK date buttons and meaningful accessible names. Do not flatten the calendar into a single painted image.

### Month/year picker

Reuse `MonthPicker` and the existing supported year range. At the reviewed snapshot that range is `1350–1450`; use repository constants rather than new duplicate limits.

- Display all twelve localized Jalali months, with year navigation/selection.
- Open from title click, Today right-click, or Today keyboard popup.
- Mark current viewed month clearly; distinguish the actual current month if desired.
- Choosing a shorter month clamps the selected day correctly.
- Year-range limits disable impossible navigation.
- Support keyboard focus, Escape, localized accessible names, and clean dismissal on rebuild.
- The popover inherits its owning calendar's appearance, including optional follow-month mode.

### Details and copy actions

Below the grid, show selected weekday and Shamsi date prominently, Gregorian and verified Hijri dates secondarily, followed by a readable scrollable event list.

Use a restrained scenic strip mainly at the panel edge, with a solid/tinted backing under the text. Long event titles wrap; event count must not push copy controls off screen.

Retain all existing footer actions: Copy Shamsi date, Copy Gregorian date, and Copy all dates. In Persian the main label is **کپی تاریخ شمسی**, in every season. If narrow, wrap or use a small copy menu containing these actions rather than deleting one to match the mockup's two visible buttons.

Normal copying respects the preference for textual/numerical dates and independent digits. Explicit numerical copying always uses the numerical form. Use the actual GTK clipboard and give a short localized confirmation only if it can be implemented without disruptive modal dialogs.

### Keyboard behavior

Preserve existing chronological arrow navigation: Left `+1` day, Right `−1` day, Up `−7`, Down `+7`; Page Up/Down change month; Home/End select the month's first/last day. Retain Tab, button activation, and visible focus. Escape hides the full view or closes the active popover first. Do not reverse chronology simply because the UI language changes.

## 10. Settings: complete control inventory

Keep a coherent native settings window. The existing notebook may be adapted; a new sidebar is optional. Use scrolling and preserve the selected settings page across live changes. Avoid rebuilding controls on every slider tick in a way that drops focus or creates feedback loops.

### Appearance

- Style: Seasonal / Classic.
- Four selectable season preview cards using the actual packaged artwork: Spring, Summer, Autumn, Winter. Use a responsive two-by-two arrangement when needed.
- Automatic season option with the currently effective season indicated.
- Follow displayed month toggle, meaningful only in automatic seasonal mode; default off.
- Dark / Light appearance.
- Seasonal accent / Custom accent choice; retain the color picker and stored color.
- Scenic artwork on/off.
- Artwork intensity slider with live preview. Suggested range `0.0–1.0`, default `0.65`.
- Background opacity: retain the existing validated range and behavior.
- Widget scale: retain the existing validated range.
- Font: Vazirmatn / System / Custom.
- Text size: retain independent text scale.
- A preview containing Persian, English, Persian digits, and Latin digits.
- Reset appearance only; do not reset language, desktop placement, startup, or event filters.

Keep preview selection clear with outline/check and text, not only color. Preview cards can show a miniature real widget generated by shared rendering helpers; do not use the full concept screenshot as the live preview.

### Language and dates

- UI language: فارسی / English.
- Digits: Persian / Latin, independently of UI language.
- Timezone: Asia/Tehran / System, preserving the current behavior.
- Prefer numerical form of dates.
- Show Gregorian date in widget: new option, default on.
- Show Hijri date in widget: preserve existing option, default on.
- Show Gregorian numbers in calendar cells: preserve existing option independently of the widget column.

Numerical formatting retains the existing `year/month/day` policy, for example `2026/10/11` and `۱۴۰۵/۷/۱۹`. Reuse the formatter's padding policy rather than introducing a second implementation. The decorative widget still uses day/month/year elements; the preference controls its full-date tooltips, detailed date text, and copies.

### Occasions and data

- Existing national, cultural, religious, and international category filters.
- Existing public-holiday display option and next-public-holiday countdown option.
- Data coverage/provenance status, errors, and the existing import/update route if present.
- Explain missing English translations using the existing fallback notice rather than inventing translations.

### Desktop and startup

- **Start at login**: user controlled, off for new installs, existing preference retained.
- Lock widget position; reset position; always-on-top; all-workspaces behavior.
- Preserve existing monitor/work-area recovery.
- Enabling startup uses the current XDG per-user entry and installed executable. Development checkout behavior remains clear when `/usr/bin/rooz` is unavailable.
- Package installation must not start the application or enable startup automatically.

Language and theme changes apply to visible views without restarting the app. They do not make hidden windows reappear, reset the selected date, clear filters, or toggle startup.

## 11. New localized labels

Use localization keys, not scattered language conditionals. Preserve existing strings where appropriate. This table supplies the key new terminology; localize all tooltips, help text, status messages, and accessibility names too.

| English | Persian |
| --- | --- |
| Roozlet | روزلت |
| Seasonal | فصلی |
| Classic | ساده |
| Automatic season | انتخاب خودکار فصل |
| Spring | بهار |
| Summer | تابستان |
| Autumn | پاییز |
| Winter | زمستان |
| Follow displayed month | ظاهر مطابق ماه نمایش‌داده‌شده |
| Seasonal accent | رنگ هماهنگ با فصل |
| Custom accent | رنگ دلخواه |
| Scenic artwork | تصویر منظره |
| Artwork intensity | شدت تصویر زمینه |
| Show Gregorian date in widget | نمایش تاریخ میلادی در ویجت |
| Show Hijri date in widget | نمایش تاریخ قمری در ویجت |
| Occasions | مناسبت‌ها |
| About | درباره |
| Copy Shamsi date | کپی تاریخ شمسی |
| Copy Gregorian date | کپی تاریخ میلادی |
| Copy all dates | کپی همه تاریخ‌ها |
| Copy numerical date | کپی تاریخ عددی |
| Start at login | اجرا هنگام ورود به سیستم |
| Data for this year is unavailable | اطلاعات مناسبت‌های این سال موجود نیست |

Maintain natural Persian shaping and the established English calendar-name terminology. Both `fa + Latin digits` and `en + Persian digits` must work.

## 12. Configuration and migration

Extend the existing configuration, using additive keys and centralized validation. Do not replace the entire preferences object or create a second config file.

Recommended **new-install defaults**, showing only new/related fields:

```json
{
  "schema_version": 1,
  "appearance": {
    "style": "seasonal",
    "season": "auto",
    "theme": "dark",
    "accent_source": "seasonal",
    "accent_color": "#5FE3AF",
    "show_artwork": true,
    "artwork_intensity": 0.65,
    "calendar_follow_viewed_month": false
  },
  "calendar": {
    "show_gregorian_column": true,
    "show_hijri_column": true
  }
}
```

This is a **partial example**, not a complete replacement config. Retain existing defaults for font, scales, opacity, dates, categories, timezone, and desktop behavior. Startup continues to be represented by the actual XDG entry, as it is now; do not introduce a contradictory JSON startup flag.

Recommended legacy behavior: existing configurations lacking `appearance.style` migrate to **classic** appearance to preserve their visible custom accent and plain theme. The centered Shamsi layout and new branding still apply. Users can enable seasonal appearance in Settings immediately. Fresh installations use seasonal/automatic mode. Distinguish a missing file/new config from a loaded old config; keep this migration decision in one place and test it.

Preserve every valid legacy field, including `accent_color`, dark/light theme, fonts, scales, opacity, language, digits, numerical dates, timezone, event filters, position, monitor, and window hints. Seasonal accent selection must not overwrite the stored custom accent when changing seasons. Reset appearance uses documented new defaults and leaves other sections untouched.

Allowed values: `style` is `seasonal|classic`; `season` is `auto|spring|summer|autumn|winter`; `accent_source` is `seasonal|custom`. Validate booleans as actual booleans. Validate slider values as finite numbers and clamp to ranges; do not accept NaN/infinity or bool-as-number. Invalid values use safe defaults and existing recovery reporting.

Additive keys can retain schema version 1 if existing rules allow it. If implementation requires a schema bump, implement explicit migration from existing supported schemas; do not simply reject all old settings. Writes remain atomic and do not touch global system configuration.

## 13. Calendar/data accuracy requirements

Preserve the existing data boundaries. At the reviewed snapshot:

- Shamsi/Gregorian browsing range: `1350–1450`, defined by calendar-service constants.
- Bundled verified annual dataset: Solar Hijri `1405`, dataset `1405.1`.
- Official Iranian Hijri dates and official occasions are available for that covered year; they are not guessed for other years.
- The existing dataset contains 305 occasion records and 26 statutory holiday dates; ordinary Fridays are separate.

Read the current manifest and provenance documents before relying on those snapshot counts. This update must not silently edit the annual event data, replace Iranian lunar mapping with a generic approximate algorithm, or claim a structural schema check establishes official verification.

Generate current dates, weekday positions, year rollover, month lengths, countdowns, and occasion lists through existing services. Use `zoneinfo` and the selected civil timezone. Preserve translation-fallback behavior and distinctions between no events, filtered events, missing coverage, and load failure.

A useful deterministic visual fixture is **2026-10-11 / 1405-07-19**, a Sunday in Mehr and therefore automatic autumn. Derive its Iranian Hijri value from the bundled data when testing; do not hard-code it in production.

## 14. Asset deliverables and runtime loading

Provide four actual cohesive scenic assets, one for each season, plus previews/crops and the icon family. Keep a similar landscape composition across seasons so the theme feels intentional. Appropriate subjects are a lake, layered mountains, trees/blossoms/leaves/snow, and restrained distant cabin light in winter. Literal Alpine scenery is not a functional requirement; coherent high-quality scenery is.

Recommended asset structure:

```text
data/themes/seasons/manifest.json
data/themes/seasons/spring/landscape.png
data/themes/seasons/spring/widget.png
data/themes/seasons/spring/preview.png
data/themes/seasons/summer/landscape.png
data/themes/seasons/summer/widget.png
data/themes/seasons/summer/preview.png
data/themes/seasons/autumn/landscape.png
data/themes/seasons/autumn/widget.png
data/themes/seasons/autumn/preview.png
data/themes/seasons/winter/landscape.png
data/themes/seasons/winter/widget.png
data/themes/seasons/winter/preview.png
data/themes/seasons/ATTRIBUTION.md
data/icons/seasons/spring.svg
data/icons/seasons/summer.svg
data/icons/seasons/autumn.svg
data/icons/seasons/winter.svg
```

Adapt filenames or avoid redundant derivatives if a common source crop works better. Suggested sizes: a landscape around `1600 × 900`, a pre-cropped widget asset around `640 × 472`, and a small preview around `320 × 180`. Preserve aspect ratio and record focal points so important content is not cut awkwardly. Avoid upscaling tiny thumbnails or shipping enormous source images for a small utility.

- Assets contain scenery only, without baked-in text, date numbers, controls, watermark, or UI screenshots.
- Use original/generated assets or material that permits redistribution; record actual provenance and applicable terms. Do not fabricate attribution or label unknown images MIT/public domain.
- Keep font/vendor licenses and extend `THIRD_PARTY_NOTICES.md` and `debian/copyright` where required.
- Prefer PNG/JPEG formats supported by the existing installed image loaders. Add a codec dependency only if necessary and verified. A build-time optimizer must not become a runtime dependency.
- Assets are bundled and work offline. No runtime download/API account is required.
- Resolve assets through `resources.DATA`, never through the current working directory or a developer's absolute path.
- A missing/corrupt optional scene produces a readable solid seasonal fallback, not a crash.

The complete design needs actual artwork, not permanently empty placeholders. If an asset source is blocked, complete the functional renderers/fallbacks and clearly identify the incomplete artwork requirement rather than marking the visual acceptance criteria as passed.

## 15. Recommended code organization

Add small focused modules where needed; the following is a proposal, not a demand to create unused files:

| Proposed file | Purpose |
| --- | --- |
| `src/rooz/seasons.py` | Pure month-to-season selection and effective-season precedence |
| `src/rooz/ui/artwork.py` | Asset manifest lookup, safe image loading, crop/scale, bounded cache |
| `src/rooz/ui/icons.py` | Consistent brand/season/control icon helpers if useful |
| `src/rooz/ui/occasions_view.py` | Month occasion list using the existing repository |
| `src/rooz/ui/about.py` | Actual localized About view and attribution routes |
| `tests/test_seasons.py` | Boundary, precedence, and migration-related behavior |

Keep pure theme decisions testable without GTK. Return a resolved theme context rather than deriving a different season independently inside every widget. Share tokens across Cairo and GTK rendering so widget and calendar colors agree.

**Important existing constraint:** `theme.apply()` currently installs an application-wide CSS provider. Optional follow-month mode needs **window-scoped season classes/providers or equivalent isolation**. Changing the calendar's month must not recolor the widget or Settings. Avoid continually adding CSS providers or unbounded style variants on every navigation/resize.

Refactor `CalendarWindow.apply()` with care: it currently rebuilds content and dismisses month popovers. Preserve selection, current subview, scroll where appropriate, focus, and visibility during changes. Do not call `show_all()` in a way that resurrects hidden windows.

For the card, compute a reusable geometry model for date slots, gear, header, footer, and hit targets. Use that same model for drawing and interaction/testing. Preserve native accessible controls for meaningful actions; descriptive canvas text alone does not make a clickable region keyboard accessible.

## 16. Layering, accessibility, and performance

Recommended visual order: rounded base surface → clipped scenic asset → readability tint/gradient → panel surfaces/borders → opaque text and icons → focus/selection/status markers. Popovers and tooltips must remain legible in dark/light and every season.

Cache decoded/scaled images by asset and size, with a bounded cache and resize coalescing. Do not decode scenery on every Cairo draw. Do not predecode every full-resolution seasonal scene when only one is visible. Preserve the existing approximately 30-second civil-clock reconciliation unless an actual functional requirement needs otherwise.

Provisional engineering budgets, to measure rather than claim:

- Artwork package contribution around 8 MiB or less; investigate large deviations.
- Widget-only steady RSS target around 100 MiB or less on the target desktop; the existing recorded baseline was about 65 MiB in its documented environment.
- Idle CPU should stay close to the existing behavior, without continuous decorative repainting.
- Repeated theme/window switching must not grow memory without bound.

Document measurement conditions and meaningful tradeoffs. These are practical targets, not established measurements of the redesigned app.

Every new button needs a localized accessible name and keyboard operation. Preserve native focus, readable text at larger scales, and text/shape indicators for important states. No action should depend exclusively on hover, color, double-click, or an unlabelled tiny icon.

## 17. Implementation sequence

1. **Baseline:** inspect source and current instructions; run existing logic/data checks; record any existing failures.
2. **Theme foundations:** pure season resolver, config extensions/migration, per-window theme contexts, color tokens, icons, and asset loading.
3. **Widget:** centered physical geometry, branded header, seasonal scene, preserved dragging/copy/tooltips, hide-column behavior, occasion interaction.
4. **Calendar:** adaptive RTL/LTR shell, month title picker, existing native grid, details panel, occasion subview, About, scoped themes.
5. **Settings:** real four-season previews, automatic/manual behavior, simple mode, independent accent/artwork/scales, complete bilingual labels.
6. **Assets/package:** all four scenes, attribution, installed asset lookup, package staging.
7. **Verification:** new meaningful behavior tests, GTK interaction/visual checks, real target-desktop checks where available.
8. **Documentation/delivery:** version/changelog updates, accurate README screenshots, `.deb`, source archive, checksums, and a concise review report.

Do not postpone all visual review until the end. Review the centered widget early, then a full autumn calendar, before applying the other three season palettes to the shared components.

## 18. Required regression and new tests

Use the existing test framework and scripts. Add behavior tests where they verify important requirements; do not write brittle tests for decorative constants or tests that simply restate the implementation.

### Pure logic/configuration

- All twelve month-to-season mappings and all four boundaries.
- Manual season precedence; automatic follow-month affects only the calendar context.
- Timezone/civil-day changes and year/season rollover through the clock/resolver seam.
- Fresh defaults versus legacy appearance migration; valid old preferences retained.
- Invalid enum/bool/number recovery and finite slider validation.
- Stored custom accent survives season changes and switching between classic/seasonal.
- Asset manifest handling and missing-asset fallback.
- Existing conversion, official-data, numerical-date, and copy-format tests still pass.

### GTK behavior

- Shamsi geometry is centered in both languages, all four seasons, both appearances, and every auxiliary-column visibility combination.
- Title and gear remain on correct opposite edges without overlap.
- Native gear, double-click, context copy, lock/drag threshold, and calendar reuse work.
- Title-click month picker, Today right-click, Shift+F10, selection clamping, and bounds work.
- Native calendar grid and existing keyboard navigation remain correct.
- Today/selected/holiday/event states remain distinct and accessible.
- Opening a month in another season does not recolor the card when follow-month mode is enabled.
- New settings persist after restart; hidden views remain hidden after refresh.
- Occasion-summary click and month-list item activation select the intended date.
- Installed asset loading works outside the source working directory.

An equality assertion on geometry is useful for centering; visual inspection must also confirm that glyphs/panels look centered. Update old tests that deliberately assert the previous `320 × 208` size or old branding to the newly documented behavior without deleting their functional coverage.

## 19. Visual and desktop verification matrix

Capture real application windows using synthetic test profiles. Do not present generated design concepts as implemented screenshots.

| Dimension | Cases |
| --- | --- |
| Season | Spring, Summer, Autumn, Winter; auto and manual |
| Appearance | Dark, Light, Classic; custom accent; artwork off |
| Language/digits | fa/Persian, fa/Latin, en/Latin, en/Persian |
| Widget columns | Both auxiliaries, either one, neither one; unavailable Hijri |
| Size | Default, maximum text scale, widget scale extremes, 200% DPI |
| Window/work area | Narrow calendar, normal calendar, short work area, monitor recovery |
| Calendar | Five-row month, six-row month, shorter month, leap Esfand, supported bounds |
| Data | No events, several events, long Persian event, holiday, filtered events, uncovered year |
| Desktop | Compositor on/off where possible; drag/lock, close/reopen, restart, startup |

Exercise automated resolver/layout tests over the combinatorial cases. For manual visual review, use a representative coverage set rather than hundreds of nearly identical screenshots. At minimum inspect all four dark seasonal widgets, one light calendar, Persian/English header/sidebar layouts, large text, six-row month, and missing-data fallback.

Use only Roozlet's actual window IDs for screenshots. Temporary profiles must not copy real user settings or unrelated desktop windows. If Mint/Xfce is unavailable, clearly distinguish virtual-X11 GTK validation from a real target-desktop check. Do not claim startup, installation, or upgrade success based solely on mocked/unit tests.

## 20. Existing commands and package verification

From the repository root, use its actual scripts, adjusting only when a documented project change requires it:

```bash
# Functional launch on an active graphical session
./scripts/dev-run.sh --calendar

# Existing logic/config/format/data tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/validate-data.py

# GTK checks: need a display or correctly configured Xvfb environment
./scripts/test-gui.sh
GDK_SCALE=2 ./scripts/test-gui.sh

# Rootless Debian build and source archive
./scripts/build-deb.sh
python3 scripts/source-archive.py
(cd dist && sha256sum -c SHA256SUMS)
```

Read and reuse `scripts/desktop-check.py`, `scripts/resource-check.py`, and `scripts/installed-gui-check.py` where their required tools/environment are available. Report unavailable checks accurately. A logic-only run may skip GUI tests by design; it is not evidence the GTK suite passed.

Update `scripts/package.py` to copy seasonal artwork and any bundled seasonal icons into paths the installed application actually resolves. The current source/installed `DATA` mechanism distinguishes a source `data/` folder from the private installed app data; verify both layouts.

For an approved local build version such as `0.2.0`, inspect and extract the resulting package:

```bash
dpkg-deb --info dist/roozlet_0.2.0-1_all.deb
dpkg-deb --contents dist/roozlet_0.2.0-1_all.deb
dpkg-deb --extract dist/roozlet_0.2.0-1_all.deb /tmp/roozlet-package-check
```

Adapt those example paths to the actual chosen version and use a fresh extraction directory. Inspect the control metadata, packaged asset paths, licenses, launcher, and source/installed behavior. Test the extracted launcher or existing installed-layout check rather than accidentally importing the development checkout.

On the owner's authorized test installation, verify upgrade from the previous `rooz` package, a normal-user launch, and retained settings. Example install command for that environment:

```bash
sudo apt install ./dist/roozlet_0.2.0-1_all.deb
rooz --version
rooz --calendar
```

Do not install on the owner's system just to produce a package unless that action is authorized. Never run the graphical app as root. Keep architecture `all` if the contents remain Python/static assets; declare actual native/system dependencies. No network activity or `pip install` at runtime.

Synchronize `src/rooz/__init__.py`, `debian/changelog`, `CHANGELOG.md`, and artifact names. Avoid downgrading a newer checked-out version. Use deterministic build settings and verify that reproducibility is retained where the existing tooling supports it.

## 21. Documentation and screenshot deliverables

Update English and Persian README files to describe the actual implemented UI and controls. Remove the outdated claim that the visible application is still Rooz/روز, while explaining the retained `rooz` command/package identity for users upgrading.

Update `docs/DESIGN.md`, relevant testing/releasing instructions, provenance/notices, and a release-notes draft. Update the older `docs/BUILD_SPEC.md` enough that its old date-column order and branding no longer contradict the implemented design, or clearly mark the superseded visual sections and link the new design document.

Recommended real screenshot set under `docs/screenshots/`:

- Four Persian dark seasonal cards.
- Autumn Persian month calendar with right sidebar and selected date.
- One English light calendar with left sidebar.
- Seasonal Settings preview cards.
- Month/year picker.
- Large-text/small-work-area validation screenshot if useful.

Use captions that say what the screenshots actually demonstrate. Keep design concepts separate from real application captures and retain useful older validation evidence without implying it proves the new version was tested.

The review report should state what changed, how to run it, chosen version, tests executed, checks not available, asset provenance, package paths/checksums, and any remaining material limitations. Do not add persistent publication privileges or automatic release publication as part of this redesign.

## 22. Definition of done

- [ ] Existing Roozlet project is extended using its native GTK3 stack.
- [ ] Visible name is Roozlet / روزلت; upgrade-relevant technical identities are preserved.
- [ ] Shamsi is physically centered and visually dominant in the widget in both languages and all visibility combinations.
- [ ] Default widget stays compact; title/gear and large text remain readable.
- [ ] All four seasonal themes include usable real artwork, correct icons, and complete dark/light/control states.
- [ ] Winter uses a snowflake; autumn uses a leaf; calendar-copy labels remain Shamsi labels.
- [ ] Automatic/manual season, custom accent, simple mode, artwork intensity, and optional calendar-follow-month work predictably.
- [ ] Calendar-only season changes do not recolor other windows.
- [ ] Month grid is computed, native, keyboard accessible, and shows distinct today/selection/holiday/event states.
- [ ] Month title picker and existing Today right-click/keyboard popup work.
- [ ] Sidebar items have real behavior; no unfinished reminder/week/day controls appear.
- [ ] Occasion summary, full lists, filters, translation fallback, and missing-data states work.
- [ ] Startup, language, digits, font, numerical dates, copies, desktop positioning, and single instance retain their functionality.
- [ ] Existing settings survive migration/restart; custom accent is not overwritten by seasons.
- [ ] Runtime is offline; assets resolve in source and installed layouts; missing artwork has a readable fallback.
- [ ] Existing checks plus meaningful new tests pass, with real visual review and honestly described environment limits.
- [ ] English/Persian docs, real screenshots, versions, notices, and package staging are updated.
- [ ] A checked `.deb`, source archive, checksums, and local review summary are delivered.
- [ ] Publication occurs only within separately authorized scope and repository rules.

## 23. Ready-to-use accompanying prompt

Paste this when giving the file to Codex or Claude Code, and optionally attach the latest autumn concept image:

> Continue my existing project at https://github.com/saeedt20/Roozlet. Read `ROOZLET_SEASONAL_UI_REDESIGN.md` completely and follow the repository's `AGENTS.md`. Implement the full four-season native GTK3 redesign, keeping the Shamsi date physically centered in the desktop widget and preserving the current calendar accuracy, settings, startup, numerical-date and copy features. Use the approved autumn concept as visual guidance if attached; the brief supplies the behavior and geometry. Work through implementation, real assets, migration, tests, actual screenshots, documentation, and a checked `.deb` rather than stopping at a plan. Preserve unrelated changes and existing package/command compatibility. Deliver the completed local result and verification report; follow the repository's rules for any later GitHub publication.
