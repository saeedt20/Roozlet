# Roozlet 0.4.0 — search, notes and reminders

## Search and date jumps

Open Search from the calendar header/sidebar, widget context menu, launcher action,
`rooz --search`, or Ctrl+F/Ctrl+K in the calendar. Type a Shamsi/Gregorian date or
words from an occasion, entry title or entry body. Enter activates the first result;
each result is also a native keyboard-accessible button.

- Numerical forms: `1405/7/20`, `۱۴۰۵/۷/۲۰`, Arabic digits, and `2026-10-12`.
  Slash, dash and dot separators are supported, with year first.
- Named forms: `20 Mehr 1405`, `۲۰ مهر ۱۴۰۵`, `12 October 2026`.
- Auto identifies supported Shamsi years or a Gregorian year; use the explicit
  calendar selector when desired. Invalid dates never open a different day.
- Persian/Arabic kaf/yeh, digits, diacritics and word spacing are normalized.
  Every search word must match. Both bundled title languages are searchable.
- Search includes all loaded occasions independently of visibility filters.
  The selected-day panel still follows those filters. Official annual/Hijri
  coverage remains 1405 only; browsing/personal data supports Shamsi 1350–1450.
- Results are chronological and capped at 100 with a visible refinement hint.
  Empty input does not query or create an entry. Input debounce and callbacks
  are canceled when the search window is destroyed.
- Activating a result updates both the selected civil day and displayed month.
  It never changes the desktop widget's current-day date.

## Personal entries

Open Notes & reminders or `rooz --personal`; Ctrl+N or Add entry creates an entry
for the selected day. Choose Note, Birthday, Appointment or Task. Titles are
required (200 characters maximum), body text is limited to 10,000 characters,
and at most 10,000 active records are accepted. Text is displayed literally;
personal input is not interpreted as UI markup.

Dates can be edited in Shamsi or Gregorian form. The selector converts a valid
date, preserving the same civil day. Times use 24-hour HH:MM and the application's
Tehran/system timezone. Tasks and appointments can retain a time without alerts.
Changes are committed only by Save. Save failures keep the draft; closing a dirty
editor asks for an explicit Discard or lets the user keep editing.

The calendar displays a separate ◇ personal marker and selected-day cards. User
entries never enter the official holiday dataset or holiday countdown. The main
personal list offers Selected day, Today, Upcoming and All entries. Upcoming shows
the next unfinished occurrence per series; All entries shows each original anchor.
Compact selected-day lists show five entries and a link to the full view; full
lists show 100, with search and day filters available for larger collections.

## Recurrence and completion

- One-time: the stored day only.
- Daily: each civil day beginning on the anchor date.
- Weekly: the anchor weekday, at seven-day intervals.
- Shamsi annual: the anchor month/day in later supported Solar Hijri years.
  Esfand 30 becomes Esfand's last day in non-leap years. No occurrence precedes
  the anchor year/date. Birthday type selects annual recurrence by default.

Done applies to one occurrence. Completing today's daily task does not complete
tomorrow's task; completing a birthday does not suppress next year's birthday.
Changing the entry edits the series. Changing its day, time or recurrence clears
the old occurrence state; editing text alone keeps delivery state.

Delete sets a recoverable flag. Undo restores the latest deletion, including its
identity and completion/delivery history. Deleted records remain in the local
database and are excluded from normal lists/search. No permanent purge UI is used.

## Optional desktop notifications

Global desktop notifications default to off, including upgrades. Enable them in
Notes & reminders or Settings → Desktop & startup, or via the explicit enable
button in the editor. Each entry also needs its own Notify me choice. Start at
login is independently opt-in. Test notification sends a synthetic message without
creating a personal entry or marking a real reminder delivered.

Roozlet must be running to deliver reminders. It uses the existing 30-second clock
poll and asynchronously calls the session's freedesktop notification service.
There is no extra daemon, privileged service or runtime Internet access.

- Startup/resume catches undelivered, unfinished reminders whose scheduled instant
  is no more than 24 hours old. Older missed alerts remain entries, without a flood.
- At most five reminders are sent per poll; larger backlogs may take longer.
- In-flight sends are deduplicated. Successful service acceptance is recorded in
  the database per entry/day; failed sends retry after two minutes.
- A queued send checks global and per-entry opt-in, its current schedule and completion state again before calling Notify. Disabling alerts
  stops new sends; the desktop may already be showing an accepted notification.
- Notification-body markup is escaped when the server supports markup. Click
  actions are included only when GetCapabilities advertises support. While Roozlet
  runs, clicking opens the occurrence's day. Desktop presentation, do-not-disturb,
  sound and action support remain the desktop service's choices.
- Normal notifications use the standard urgency level and desktop-entry `rooz`.
  Service availability/failure is reported in the app without claiming delivery.
- Ambiguous DST wall times use the first fold; a nonexistent time moves through
  the spring gap. Delivery state prevents a repeated alert in the second fold.

If accepted-delivery state cannot be saved, the process suppresses a repeat while
it remains open and shows a personal-data warning. Restore writable storage before
restarting, since no application can guarantee durable deduplication after a failed
database write.

Protocol reference: https://specifications.freedesktop.org/notification/latest-single/.
SQLite transaction reference: https://docs.python.org/3.12/library/sqlite3.html.

## Storage, upgrade and backup

User data lives in `$XDG_DATA_HOME/rooz/personal.sqlite3`, normally
`~/.local/share/rooz/personal.sqlite3`. The app-owned directory is 0700 and the file
is 0600. The data is local SQLite, not encrypted cloud storage. It is separate
from appearance preferences and packaged official calendar data. Package upgrades
and normal removal do not delete it. Corrupt/future-schema data is not silently
replaced; the app shows an unavailable state and retains the original file.

For a simple consistent backup, quit Roozlet first and copy the database to a
private location. Restore only while the app is closed. A live backup should use
SQLite's backup API. Source/publication archives exclude SQLite databases and
journal/WAL/SHM files. Published screenshots and reports contain synthetic test
records only.

Schema 1 separates editable entries from occurrence completion/delivery state,
with transactions and foreign keys. No new Python package dependency is needed.
CLI identity, XDG preference/autostart paths, widget geometry, Vazirmatn, seasonal
motion and the bounded About/Credits UI from 0.3.1 remain intact.
