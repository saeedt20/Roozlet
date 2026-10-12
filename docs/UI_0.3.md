# Roozlet 0.3: native calendar, preferences and gentle motion

This specification records the owner's approved autumn UI concepts and the
English/Persian motion preview. It supersedes older layout and no-animation
instructions in BUILD_SPEC / SEASONAL_UI_REDESIGN; accuracy and offline behavior
remain required. Generated concepts are appearance references, not date fixtures.

## Calendar

- Native GTK3 month window with one HeaderBar, a scenic hero and a single
  previous-month / Today / next-month control group. The month title opens the
  existing 12-month/year picker; Today right-click and Shift+F10 remain available.
- Theme-aware, light borders; no repeated photos below the grid or in the sidebar.
- Persian: sidebar on the right, icons at the leading/right edge, logical-start
  text alignment; Saturday on the right, Friday on the left.
- English: sidebar on the left, icons before left-aligned labels; Saturday on the
  left, Friday on the right. Week starts Saturday in both languages. Keyboard
  Left/Right follow the physical direction; Up/Down still move one week.
- Conversion service keeps its existing canonical cells. English projects the
  columns as `6 - canonical_column`; dates, holidays and mappings are unchanged.
- Today has an outline; selected date has an accessible contrasting fill.
  Gregorian numbers remain secondary and can be independently disabled.
- Selected-date card holds equivalent dates and scrollable occasions, with one
  Copy date dropdown for Persian, Gregorian, Hijri, all dates and numerical
  variants. Unsupported Hijri copy actions are disabled.
- Occasions view, filters, missing-data states, year bounds and keyboard access
  remain functional. Closing the month window leaves the widget running.
- Default content size 880 × 640 logical pixels, clamped to the work area with
  room for native decorations. Under 660 pixels the sidebar gives way to an
  accessible compact menu. A narrow scenic header wraps its navigation.

## Preferences

- Native sidebar + Stack replaces notebook tabs. Categories are Appearance,
  Language & dates, Occasions and Desktop & startup; Persian/English mirror.
  Under 660 pixels, the HeaderBar category picker exposes every page.
- Grouped rows put the label at logical start and its control at the opposite
  edge. Persian uses GTK direction and native shaping, not reversed strings.
- Live preview computes real current civil dates and official Hijri coverage.
  Gregorian stays physically left, Shamsi center, Hijri right in both locales.
  Hiding auxiliary columns does not move Shamsi.
- Automatic season toggle, four offline scene tiles, light/dark buttons,
  intensity slider, custom accent chooser and subtle-transition switch.
- Advanced expander retains Classic/Seasonal style, accent source, artwork,
  follow-viewed-month scope, opacity, widget/text scale and all font controls.
  Font fallback remains visible even when advanced settings are collapsed.
- Numerical dates, timezone, independent digits, date-column visibility,
  category filters, statutory holidays/countdown, position, workspaces and
  opt-in startup remain available. Startup identity is still rooz.desktop.
- Scene/theme changes update the persistent preview without rebuilding active
  controls or date cells; slider changes preserve the calendar selection/focus. Locale/font rebuilds retain the selected page and expanded state,
  restore scroll position after allocation and restore a focused setting.
- Default content size 760 × 680, work-area clamped; contents scroll rather than
  hiding settings. No installation or redesign enables login startup.

## Motion contract

| Interaction | Native implementation | Duration |
| --- | --- | --- |
| Button hover/press feedback | GTK CSS background/border/color | 140 ms |
| Calendar month/view content | GtkStack crossfade | 160 ms |
| Preferences page change | GtkStack crossfade | 180 ms |
| Seasonal scene change | GTK frame clock, artwork only | 260 ms |

No looping leaves, snow, parallax, bounce or large sliding panels. Dates update
immediately and remain readable; transitions do not delay input or data changes.
The calendar keeps at most two native content trees while fading, and only one
at rest. Rapid navigation replaces pending content. A scene retains at most its
current/previous image reference, within the existing bounded decode cache.
Frame callbacks stop at completion, on unmap/destruction, or when motion is off.

`appearance.motion_effects` is an additive validated boolean, default true.
Existing false values persist. The app also respects the process's native GTK
`gtk-enable-animations` setting, without changing system configuration. The
switch disables Roozlet's scenic and content transitions; native controls keep
their normal platform behavior. Missing/invalid artwork uses a readable plain
surface. No runtime downloads, new service, browser rendering or wallpaper edits.

GTK API references:
- https://docs.gtk.org/gtk3/class.Stack.html
- https://docs.gtk.org/gtk3/property.Settings.gtk-enable-animations.html
- https://docs.gtk.org/gtk3/method.Widget.add_tick_callback.html
- https://docs.gtk.org/gtk3/css-properties.html

## Compatibility and validation

Keep Python/GTK3, Package: rooz, command /usr/bin/rooz, application ID, XDG paths,
Vazirmatn, verified annual data and licenses. Bump authoritative version and
Debian changelog together. No CI publication workflow or broader permissions.

Tests must cover locale-specific coordinates/arrows, right/left navigation,
actual preference callbacks, dropdown clipboard routing, reduced motion,
interrupted transitions, cleanup, missing-art fallback and narrow-window access.
Run normal and 200% GTK checks, annual-data validation and the rootless package
build. Review actual application captures in fa/en and dark/light; distinguish
virtual-display tests from native Mint installation, login/resume and hotplug.
