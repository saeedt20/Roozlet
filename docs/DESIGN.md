# Design and interaction

The default card is 320 × 208 logical pixels: 16-pixel inset, 17-pixel corner
radius, charcoal #14252E and mint #5FE3AF. At default text scale it remains within
the approved compact footprint. Larger text independently increases card height;
widget scaling increases both dimensions. On a small work area, effective card
scale is capped to keep the entire card visible. Text stays opaque while only the
background uses opacity. A non-composited session uses an opaque fallback.
No wallpaper blur or compositor/theme settings are changed.

Persian is the physically rightmost, visually dominant date column in both
languages. Gregorian is centered and Hijri leftmost. Calendar-grid coordinates
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
