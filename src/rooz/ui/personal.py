"""Localized personal entries, explicit save, reversible delete and native editing."""

import re
from datetime import date

from gi.repository import Gdk, Gtk

from ..calendar_service import jalali
from ..formatting import dates
from ..personal import KINDS, REPEATS, PersonalError
from ..search import DIGITS, parse_date
from .common import button, clear, direction, label
from .theme import style_window


def wrapped(text, style=None):
    result = label(text, style, wrap=True)
    result.set_width_chars(1)
    result.set_selectable(True)
    return result


class PersonalEditor(Gtk.Window):
    def __init__(self, calendar, day, item_id=None):
        super().__init__(transient_for=calendar, modal=True)
        self.calendar, self.app, self.item_id = calendar, calendar.app, item_id
        self.set_destroy_with_parent(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        area = calendar.get_display().get_monitor_at_window(calendar.get_window()).get_workarea()
        self.set_default_size(min(520, area.width - 48), min(620, area.height - 120))
        self.set_size_request(320, 240)
        self.get_style_context().add_class("rooz")
        self.header = Gtk.HeaderBar(show_close_button=True)
        self.set_titlebar(self.header)
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.root.set_border_width(16)
        self.add(self.root)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_overlay_scrolling(False)
        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.add(form)
        self.root.pack_start(scroll, True, True, 0)
        self.field_labels = {}
        self.building = True
        self.title_entry = Gtk.Entry()
        self.title_entry.set_max_length(200)
        self.title_entry.set_width_chars(1)
        self.kind = Gtk.ComboBoxText()
        self.date_entry = Gtk.Entry()
        self.date_entry.set_max_length(40)
        self.date_entry.set_width_chars(12)
        self.date_mode = Gtk.ComboBoxText()
        date_row = Gtk.Box(spacing=8)
        date_row.pack_start(self.date_entry, True, True, 0)
        date_row.pack_end(self.date_mode, False, False, 0)
        self.body = Gtk.TextView()
        self.body.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.body.set_accepts_tab(False)
        self.body.set_left_margin(8)
        self.body.set_right_margin(8)
        body_scroll = Gtk.ScrolledWindow()
        body_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        body_scroll.set_min_content_height(85)
        body_scroll.add(self.body)
        self.repeat = Gtk.ComboBoxText()
        self.notify = Gtk.CheckButton()
        self.time_entry = Gtk.Entry()
        self.time_entry.set_max_length(5)
        self.time_entry.set_width_chars(6)
        self.time_entry.set_direction(Gtk.TextDirection.LTR)
        identity = Gtk.Box(spacing=10)
        for key, control in (("entry_title", self.title_entry), ("entry_kind", self.kind)):
            field = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            text = wrapped("")
            self.field_labels[key] = text
            field.pack_start(text, False, False, 0)
            field.pack_start(control, False, False, 0)
            identity.pack_start(field, key == "entry_title", key == "entry_title", 0)
        form.pack_start(identity, False, False, 0)
        for key, control in (("entry_date", date_row), ("entry_body", body_scroll)):
            text = wrapped("")
            self.field_labels[key] = text
            form.pack_start(text, False, False, 0)
            form.pack_start(control, False, False, 0)
        form.pack_start(self.repeat, False, False, 0)
        self.repeat_help = wrapped("", "muted")
        self.repeat_help.set_no_show_all(True)
        self.repeat.connect("changed", lambda *_: self.repeat_help.set_visible(self.repeat.get_active_id() == "annual"))
        form.pack_start(self.repeat_help, False, False, 0)
        form.pack_start(self.notify, False, False, 0)
        self.field_labels["reminder_time"] = wrapped("")
        form.pack_start(self.field_labels["reminder_time"], False, False, 0)
        form.pack_start(self.time_entry, False, False, 0)
        self.notification_help = wrapped("", "muted")
        form.pack_start(self.notification_help, False, False, 0)
        self.enable_notifications = button("", self.enable_global)
        self.enable_notifications.set_no_show_all(True)
        form.pack_start(self.enable_notifications, False, False, 0)
        self.error = wrapped("", "holiday")
        self.root.pack_start(self.error, False, False, 0)
        footer = Gtk.Box(spacing=8)
        self.cancel_button = button("", self.request_close)
        self.discard_button = button("", self.destroy)
        self.discard_button.set_no_show_all(True)
        self.save_button = button("", self.save)
        self.save_button.get_style_context().add_class("selected")
        footer.pack_start(self.cancel_button, False, False, 0)
        footer.pack_start(self.discard_button, False, False, 0)
        footer.pack_end(self.save_button, False, False, 0)
        self.root.pack_start(footer, False, False, 0)
        item = self.app.personal.get(item_id) if item_id else None
        if item_id and item is None:
            raise PersonalError("Original entry unavailable")
        self.date_calendar = "shamsi"
        self.refresh_locale()
        self.title_entry.set_text(item["title"] if item else "")
        self.kind.set_active_id(item["kind"] if item else "note")
        anchor = date.fromisoformat(item["day"]) if item else day
        j = jalali(anchor)
        self.date_entry.set_text(self.app.loc.n(f"{j.year}/{j.month}/{j.day}"))
        self.body.get_buffer().set_text(item["body"] if item else "")
        self.repeat.set_active_id(item["repeat"] if item else "none")
        self.notify.set_active(bool(item and item["notify"]))
        self.time_entry.set_text(item["time"] if item else "09:00")
        self.title_entry.connect("changed", lambda *_: self.save_button.set_sensitive(bool(self.title_entry.get_text().strip())))
        self.kind.connect("changed", self.kind_changed)
        self.date_mode.connect("changed", self.calendar_changed)
        self.notify.connect("toggled", lambda *_: self.sync_notification())
        self.building = False
        self.initial = self.values()
        self.connect("delete-event", lambda *_: self.request_close() or True)
        self.connect("key-press-event", self.key)
        self.show_all()
        self.repeat_help.set_visible(self.repeat.get_active_id() == "annual")
        self.sync_notification()
        self.save_button.set_sensitive(bool(self.title_entry.get_text().strip()))
        self.title_entry.grab_focus()

    def refresh_locale(self):
        previous = self.building
        self.building = True
        loc = self.app.loc
        title = loc.t("edit_entry") if self.item_id else loc.t("new_entry")
        self.header.set_title(title)
        self.set_title(title)
        selected = self.kind.get_active_id() or "note"
        self.kind.remove_all()
        for kind in KINDS:
            self.kind.append(kind, loc.t(kind))
        self.kind.set_active_id(selected)
        self.date_mode.remove_all()
        self.date_mode.append("shamsi", loc.t("shamsi"))
        self.date_mode.append("gregorian", loc.t("gregorian"))
        self.date_mode.set_active_id(self.date_calendar)
        for key, field in self.field_labels.items():
            field.set_text(loc.t(key))
        for key, control in (("entry_title", self.title_entry), ("entry_kind", self.kind),
                             ("entry_date", self.date_entry), ("entry_body", self.body),
                             ("reminder_time", self.time_entry), ("date_calendar", self.date_mode)):
            control.get_accessible().set_name(loc.t(key))
        self.field_labels["reminder_time"].set_text(loc.t("reminder_time") + " · " +
            loc.t("tehran_time" if self.app.cfg["timezone"] == "Asia/Tehran" else "system_time"))
        repeat = self.repeat.get_active_id() or "none"
        self.repeat.remove_all()
        for key in REPEATS:
            self.repeat.append(key, loc.t("no_repeat" if key == "none" else "repeat_" + key))
        self.repeat.set_active_id(repeat)
        self.repeat.get_accessible().set_name(loc.t("repeat_schedule"))
        self.repeat_help.set_text(loc.t("repeat_help"))
        self.notify.set_label(loc.t("notify_entry"))
        self.enable_notifications.set_label(loc.t("enable_notifications"))
        self.cancel_button.set_label(loc.t("cancel"))
        self.discard_button.set_label(loc.t("discard"))
        self.save_button.set_label(loc.t("save"))
        direction(self.root, loc.lang == "fa")
        direction(self.header, loc.lang == "fa")
        self.time_entry.set_direction(Gtk.TextDirection.LTR)
        style_window(self, self.app.cfg, self.app.today)
        self.building = previous
        self.sync_notification()

    def sync_notification(self):
        enabled = self.app.cfg["personal"]["notifications_enabled"]
        self.time_entry.set_sensitive(self.notify.get_active() or self.kind.get_active_id() != "note")
        self.notification_help.set_text(self.app.loc.t("reminder_runtime_short") if enabled else self.app.loc.t("notifications_off"))
        self.enable_notifications.set_visible(self.notify.get_active() and not enabled)

    def enable_global(self):
        self.app.change("personal", "notifications_enabled", True)
        self.sync_notification()

    def kind_changed(self, *_):
        if not self.building and self.kind.get_active_id() == "birthday":
            self.repeat.set_active_id("annual")
        if not self.building:
            self.sync_notification()

    def calendar_changed(self, *_):
        if self.building:
            return
        selected = self.date_mode.get_active_id()
        try:
            day = parse_date(self.date_entry.get_text(), self.date_calendar)
            if day:
                j = jalali(day)
                text = f"{j.year}/{j.month}/{j.day}" if selected == "shamsi" else f"{day.year}/{day.month}/{day.day}"
                self.date_entry.set_text(self.app.loc.n(text))
        except ValueError:
            pass
        self.date_calendar = selected

    def values(self):
        buf = self.body.get_buffer()
        return (self.title_entry.get_text(), self.kind.get_active_id(), self.date_entry.get_text(),
                self.date_calendar, buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True),
                self.repeat.get_active_id(), self.notify.get_active(), self.time_entry.get_text())

    def save(self):
        title, kind, text, mode, body, repeat, notify, clock = self.values()
        loc = self.app.loc
        try:
            day = parse_date(text, mode)
            if not day:
                raise ValueError()
        except ValueError:
            self.error.set_text(loc.t("invalid_date"))
            return
        clock = clock.translate(DIGITS)
        if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", clock):
            self.error.set_text(loc.t("invalid_time"))
            return
        if not title.strip() or len(body) > 10000:
            self.error.set_text(loc.t("entry_limits"))
            return
        try:
            self.app.personal.save(title, body, day, kind, repeat, notify, clock, self.item_id)
        except (PersonalError, OSError):
            self.error.set_text(loc.t("personal_save_error"))
            return
        self.app.personal_changed()
        self.destroy()

    def request_close(self):
        if self.values() != self.initial:
            self.error.set_text(self.app.loc.t("unsaved_entry"))
            self.discard_button.show()
        else:
            self.destroy()
        return True

    def key(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            return self.request_close()
        return False


class PersonalView(Gtk.Box):
    def __init__(self, calendar, compact=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.calendar, self.app, self.compact = calendar, calendar.app, compact
        self.rows = {}
        loc = self.app.loc
        top = Gtk.Box(spacing=8)
        top.pack_start(wrapped(loc.t("personal"), "detail-heading" if compact else "heading"), True, True, 0)
        self.add_button = button(loc.t("new_entry"), lambda: calendar.open_personal_editor(calendar.selected))
        top.pack_end(self.add_button, False, False, 0)
        self.pack_start(top, False, False, 0)
        self.data_warning = wrapped(loc.t("personal_save_error"), "holiday")
        self.data_warning.set_no_show_all(True)
        self.data_warning.set_visible(getattr(self.app, "personal_error", False))
        self.pack_start(self.data_warning, False, False, 0)
        if not getattr(self.app, "personal", None):
            self.add_button.set_sensitive(False)
            self.pack_start(wrapped(loc.t("personal_unavailable"), "holiday"), False, False, 0)
            return
        if not compact:
            self.mode = Gtk.ComboBoxText()
            for key in ("selected_day", "today", "upcoming", "all_entries"):
                self.mode.append(key, loc.t(key))
            self.mode.set_active_id(calendar.personal_mode)
            self.mode.get_accessible().set_name(loc.t("personal_filter"))
            self.mode.connect("changed", self.changed_mode)
            self.pack_start(self.mode, False, False, 0)
            row = Gtk.Box(spacing=10)
            row.pack_start(wrapped(loc.t("desktop_notifications")), True, True, 0)
            self.notifications = Gtk.Switch()
            self.notifications.set_active(self.app.cfg["personal"]["notifications_enabled"])
            self.notifications.get_accessible().set_name(loc.t("desktop_notifications"))
            self.notifications.connect("notify::active", lambda b, _: self.app.change("personal", "notifications_enabled", b.get_active()))
            row.pack_end(self.notifications, False, False, 0)
            self.pack_start(row, False, False, 0)
            self.pack_start(wrapped(loc.t("reminder_runtime"), "muted"), False, False, 0)
            self.notification_status = wrapped("", "muted")
            self.pack_start(self.notification_status, False, False, 0)
            self.update_status()
        if getattr(self.app, "last_deleted", None):
            row = Gtk.Box(spacing=8)
            row.pack_start(wrapped(loc.t("entry_deleted"), "muted"), True, True, 0)
            self.undo_button = button(loc.t("undo"), self.undo)
            row.pack_end(self.undo_button, False, False, 0)
            self.pack_start(row, False, False, 0)
        mode = "selected_day" if compact else calendar.personal_mode
        try:
            occurrences = (self.app.personal.on(calendar.selected) if mode == "selected_day" else
                           self.app.personal.entries(self.app.today, {"all_entries": "all"}.get(mode, mode)))
        except PersonalError:
            self.app.personal_error = True
            self.add_button.set_sensitive(False)
            self.pack_start(wrapped(loc.t("personal_unavailable"), "holiday"), False, False, 0)
            occurrences = []
        if not occurrences:
            self.pack_start(wrapped(loc.t("personal_empty"), "muted"), False, False, 0)
        for occurrence in occurrences[:5 if compact else 100]:
            self.append_occurrence(occurrence)
        if len(occurrences) > (5 if compact else 100):
            self.pack_start(wrapped(loc.t("personal_limit"), "muted"), False, False, 0)
        if compact and occurrences:
            self.pack_start(button(loc.t("show_personal"), self.show_all_entries), False, False, 0)
        direction(self, loc.lang == "fa")

    def update_status(self):
        if not hasattr(self, "notification_status"):
            return
        value = getattr(self.app, "notification_available", None)
        self.notification_status.set_text(self.app.loc.t("notification_sent") if value is True else
                                          self.app.loc.t("notification_unavailable") if value is False else "")

    def show_data_error(self):
        self.data_warning.show()

    def changed_mode(self, combo):
        self.calendar.personal_mode = combo.get_active_id()
        self.calendar.apply()

    def show_all_entries(self):
        self.calendar.personal_mode = "selected_day"
        self.calendar.show_view("personal")

    def append_occurrence(self, occurrence):
        item, day, loc = occurrence.item, occurrence.day, self.app.loc
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        panel.get_style_context().add_class("details-panel")
        heading = Gtk.Box(spacing=8)
        title = wrapped(item["title"], "muted" if occurrence.done else "detail-heading")
        heading.pack_start(title, True, True, 0)
        if item["kind"] != "note":
            done = Gtk.CheckButton(label=loc.t("done"))
            done.set_active(occurrence.done)
            done.get_accessible().set_name(loc.t("done") + " · " + item["title"])
            done.connect("toggled", lambda b, o=occurrence: self.complete(o, b.get_active()))
            heading.pack_end(done, False, False, 0)
        else:
            done = None
        panel.pack_start(heading, False, False, 0)
        subtitle = loc.t(item["kind"]) + " · " + dates(day, loc, self.app.repo)[0]
        if item["repeat"] != "none":
            subtitle += " · " + loc.t("repeat_" + item["repeat"])
        if item["notify"] or item["kind"] != "note":
            subtitle += " · " + loc.n(item["time"])
        panel.pack_start(wrapped(subtitle, "muted"), False, False, 0)
        if item["body"]:
            body = item["body"][:240] + ("…" if len(item["body"]) > 240 else "")
            panel.pack_start(wrapped(body), False, False, 0)
        actions = Gtk.Box(spacing=6)
        edit = button(loc.t("edit"), lambda: self.calendar.open_personal_editor(day, item["id"]))
        delete = button(loc.t("delete"), lambda: self.delete(item["id"]))
        actions.pack_start(edit, False, False, 0)
        actions.pack_start(delete, False, False, 0)
        if not self.compact:
            actions.pack_end(button(loc.t("go_to_date"), lambda: self.calendar.select(day)), False, False, 0)
        panel.pack_start(actions, False, False, 0)
        self.pack_start(panel, False, False, 0)
        self.rows[item["id"]] = {"edit": edit, "delete": delete, "done": done, "occurrence": occurrence}

    def complete(self, occurrence, value):
        try:
            self.app.personal.set_state(occurrence.item["id"], occurrence.day, "done", value)
            self.app.personal_changed()
        except PersonalError:
            self.failed_save()

    def delete(self, item_id):
        try:
            self.app.personal.set_deleted(item_id)
            self.app.last_deleted = item_id
            self.app.personal_changed()
        except PersonalError:
            self.failed_save()

    def undo(self):
        try:
            self.app.personal.set_deleted(self.app.last_deleted, False)
            self.app.last_deleted = None
            self.app.personal_changed()
        except PersonalError:
            self.failed_save()

    def failed_save(self):
        self.app.personal_error = True
        self.calendar.apply()
