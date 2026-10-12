"""Small native search dialog: debounced input, bounded results, keyboard jump."""

from gi.repository import Gdk, GLib, Gtk

from ..formatting import dates
from ..search import search
from ..personal import PersonalError
from .common import button, clear, direction, label
from .theme import style_window


class SearchWindow(Gtk.Window):
    def __init__(self, parent):
        super().__init__(transient_for=parent, modal=True)
        self.parent, self.app, self.timeout = parent, parent.app, 0
        self.set_destroy_with_parent(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        area = parent.get_display().get_monitor_at_window(parent.get_window()).get_workarea()
        self.set_default_size(min(620, area.width - 48), min(520, area.height - 120))
        self.set_size_request(300, 220)
        self.get_style_context().add_class("rooz")
        self.header = Gtk.HeaderBar(show_close_button=True)
        self.set_titlebar(self.header)
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.root.set_border_width(18)
        self.add(self.root)
        row = Gtk.Box(spacing=8)
        self.entry = Gtk.SearchEntry()
        self.entry.set_width_chars(12)
        self.entry.set_max_length(300)
        self.entry.connect("search-changed", self.changed)
        self.entry.connect("activate", self.activate_first)
        row.pack_start(self.entry, True, True, 0)
        self.mode = Gtk.ComboBoxText()
        self.mode.connect("changed", self.changed)
        row.pack_end(self.mode, False, False, 0)
        self.root.pack_start(row, False, False, 0)
        self.help = label(wrap=True)
        self.help.set_width_chars(1)
        self.root.pack_start(self.help, False, False, 0)
        self.status = label(style="muted", wrap=True)
        self.status.set_width_chars(1)
        self.root.pack_start(self.status, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_overlay_scrolling(False)
        self.results = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scroll.add(self.results)
        self.root.pack_start(scroll, True, True, 0)
        self.close_button = button("", self.destroy)
        self.close_button.set_halign(Gtk.Align.END)
        self.root.pack_start(self.close_button, False, False, 0)
        self.building = False
        self.result_values = []
        self.connect("destroy", self.cleanup)
        self.connect("key-press-event", self.key)
        self.refresh_locale()
        self.show_all()
        self.entry.grab_focus()

    def refresh_locale(self):
        self.building = True
        loc = self.app.loc
        self.set_title(loc.t("search"))
        self.header.set_title(loc.t("search"))
        self.entry.set_placeholder_text(loc.t("search_placeholder"))
        self.entry.get_accessible().set_name(loc.t("search"))
        self.help.set_text(loc.t("search_help") + "\n" + loc.t("search_coverage"))
        self.mode.get_accessible().set_name(loc.t("date_calendar"))
        selected = self.mode.get_active_id() or "auto"
        self.mode.remove_all()
        for key, title in (("auto", "detect_date"), ("shamsi", "shamsi"), ("gregorian", "gregorian")):
            self.mode.append(key, loc.t(title))
        self.mode.set_active_id(selected)
        self.close_button.set_label(loc.t("close"))
        direction(self.root, loc.lang == "fa")
        direction(self.header, loc.lang == "fa")
        style_window(self, self.app.cfg, self.app.today)
        self.building = False
        self.run_search()

    def changed(self, *_):
        if self.building:
            return
        if self.timeout:
            GLib.source_remove(self.timeout)
        self.timeout = GLib.timeout_add(160, self.run_search)

    def run_search(self):
        if self.timeout:
            GLib.source_remove(self.timeout)
            self.timeout = 0
        clear(self.results)
        self.result_values = []
        loc = self.app.loc
        try:
            values, total = search(self.entry.get_text(), self.app.repo, getattr(self.app, "personal", None),
                                   loc, self.app.today, self.mode.get_active_id() or "auto")
        except PersonalError:
            self.status.set_text(loc.t("personal_unavailable"))
            return False
        except ValueError:
            self.status.set_text(loc.t("invalid_date"))
            return False
        self.result_values = values
        self.status.set_text((loc.n(total) + " " + loc.t("search_results") +
                              (" · " + loc.t("search_limit") if total > len(values) else ""))
                             if total else loc.t("search_empty") if self.entry.get_text().strip() else "")
        for value in values:
            row = Gtk.Button()
            row.get_style_context().add_class("search-result")
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            title = label(value.title, "detail-heading", wrap=True)
            title.set_width_chars(1)
            content.pack_start(title, False, False, 0)
            subtitle = label(loc.t(value.kind) + " · " + dates(value.day, loc, self.app.repo)[0], "muted", wrap=True)
            subtitle.set_width_chars(1)
            content.pack_start(subtitle, False, False, 0)
            row.add(content)
            row.get_accessible().set_name(value.title + " · " + subtitle.get_text())
            row.connect("clicked", lambda _, v=value: self.choose(v))
            self.results.pack_start(row, False, False, 0)
        direction(self.results, loc.lang == "fa")
        self.results.show_all()
        return False

    def choose(self, value):
        self.parent.view = "calendar"
        self.parent.select(value.day)
        self.parent.focus_selected()
        self.destroy()

    def activate_first(self, *_):
        self.run_search()
        if self.result_values:
            self.choose(self.result_values[0])

    def cleanup(self, *_):
        if self.timeout:
            GLib.source_remove(self.timeout)
            self.timeout = 0

    def key(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False
