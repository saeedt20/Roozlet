# Version 0.3 interface

See [UI_0.3.md](UI_0.3.md) for the implemented bilingual layout, preferences and bounded motion contract. It replaces the older fixed weekday order and notebook settings. The content fades are native GTK; scene frames exist only during a 260 ms change. Existing date services and widget geometry are preserved.

# Roozlet 0.2.0 seasonal design

The desktop card is **320 × 236 logical pixels**. Its physical date order is
Gregorian / Shamsi / Iranian Hijri. Shamsi stays on the content centerline in both
languages and with either satellite hidden. Primary date panels, vector seasonal
marks and translucent scenery use shared tokens. Winter uses a snowflake.

Four original bundled scenes are drawn from `data/themes/seasons/`, with a bounded
8-entry scaled-image cache and a solid-color fallback. No runtime download,
wallpaper modification or live blur is required. An opaque non-composited fallback
keeps corners readable. Fonts and text are not made translucent.

Automatic seasons follow the configured civil day converted to Jalali, not the
Gregorian month. Manual overrides win. Dark/light appearance and custom accents
are independent. Optional follow-month mode applies a scoped season class only
to the calendar and its popover; widget and Settings keep today's season.

Fresh profiles default to Seasonal/Automatic. Legacy appearance records migrate
to Classic/Custom so their stored colors and other preferences survive. The owner
can enable Seasonal in Settings. Technical package, executable, application-ID,
WM-class and config-directory identities remain unchanged; visible names are
Roozlet / روزلت.

The expanded calendar defaults to 860 × 680 logical pixels, clamped to work area.
Its right Persian / left English sidebar collapses below 660 logical pixels; a
header menu exposes the same actions on narrow windows. Native date cells retain
physical Saturday-right / Friday-left order. The body can scroll at large text
or 200% DPI. Clicking the month title and Today right-click open the shared picker.
An actual monthly occasion list and About dialog back the sidebar actions.

All dates and event states remain computed from the existing calendar/data
services. The remainder below records retained interactions from earlier versions;
older default dimensions and date order are superseded by this section.

# Design and interaction

The default card is 320 × 208 logical pixels: 16-pixel inset, 17-pixel corner
radius, charcoal #14252E and mint #5FE3AF. At default text scale it remains within
the approved compact footprint. Larger text independently increases card height;
widget scaling increases both dimensions. On a small work area, effective card
scale is capped to keep the entire card visible. Text stays opaque while only the
background uses opacity. A non-composited session uses an opaque fallback.
No wallpaper blur or compositor/theme settings are changed.

Persian is physically centered and visually dominant in both languages.
Gregorian is leftmost and Hijri rightmost. Calendar-grid coordinates
are generated from real weekdays; Saturday is physically rightmost and Friday
leftmost regardless of language. Persian controls are RTL; English controls LTR.
Pango handles joining and bidi text. No text is manually reversed in the UI.
The offline PDF importer reverses isolated extracted visual words only when
recovering source table columns, which is separate from UI text rendering.

The month window defaults to 560 × 560 logical pixels, a small increase from the
brief's approximate 560 × 520 to preserve readable Gregorian cell numbers and
scrollable event details. Both full windows clamp their opening size to the work
area; the month body can scroll on small screens or at 200% DPI. Rows retain stable
cell sizing and use five or six rows according to the actual month.

Filled accent marks selection, outlined accent marks today, and both remain
visible when today is selected. Coral Fridays indicate the regular weekly day
off; a diamond and accessible public-holiday text identify statutory holidays.
Event dots mark ordinary occasions. Official holiday status survives filters.
Custom accents use a contrast-aware selected foreground and a separate readable
text/outline accent when the custom color is unsuitable for text.

Double-click card content opens one reusable month view. Gear is a separate GTK
button. Header drag starts after a 6-pixel threshold and saves after release.
Right-click offers the same calendar/settings/copy actions plus position lock,
layering, reset and Quit. Closing or Escape hides a full view without quitting
the card. Hidden windows stay hidden during day/settings refreshes.

Arrow keys on a focused date move chronologically: Left +1, Right -1, Up -7,
Down +7. Page Up/Down change month; Home/End select first/last day. Tab and native
button activation remain available. At range boundaries navigation is disabled;
tooltips state supported years. Today explicitly resets navigation.

The managed DESKTOP window requests keep-below, skip-taskbar/pager and sticky
workspace hints, following the inspected Mint Meter pattern. Optional always-on-top
switches to a managed normal window and keep-above. No strut or override-redirect
is used. Hints remain subject to the window manager; see TESTING.md.
