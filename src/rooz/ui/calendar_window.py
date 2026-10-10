"""Native accessible month view; fixed Iranian physical weekday order."""

from datetime import timedelta

from gi.repository import Gdk, Gtk

from ..calendar_service import MAX_YEAR, MIN_YEAR, gregorian, jalali, month_cells, month_length, shift_month
from ..formatting import dates, full_date
from ..i18n import GMONTHS, JMONTHS, SHORT_WEEK, WEEKDAYS
from .common import button, clear, direction, label


class CalendarWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Rooz")
        self.app = app
        self.selected = app.today
        j = jalali(app.today)
        self.year, self.month = j.year, j.month
        self.get_style_context().add_class("rooz")
        monitor = self.get_display().get_primary_monitor() or self.get_display().get_monitor(0)
        area = monitor.get_workarea()
        self.set_default_size(min(560, area.width - 48), min(560, area.height - 64))
        self.set_size_request(360, 300)
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.root.set_border_width(14)
        self.outer = Gtk.ScrolledWindow()
        self.outer.set_overlay_scrolling(False)
        self.outer.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.outer.add(self.root)
        self.add(self.outer)
        self.connect("delete-event", lambda *_: self.hide() or True)
        self.connect("key-press-event", self.key)
        self.cells = {}
        self.apply()
        self.show_all()

    def navigate(self, delta):
        self.year, self.month = shift_month(self.year, self.month, delta)
        old = jalali(self.selected)
        self.selected = gregorian(self.year, self.month, min(old.day, month_length(self.year, self.month)))
        self.apply()
        self.focus_selected()

    def go_today(self):
        self.selected = self.app.today
        j = jalali(self.selected)
        self.year, self.month = j.year, j.month
        self.apply()
        self.focus_selected()

    def select(self, day):
        self.selected = day
        self.apply()
        self.focus_selected()

    def focus_selected(self):
        if self.selected in self.cells:
            self.cells[self.selected].grab_focus()

    def key(self, _, event):
        k = event.keyval
        if k == Gdk.KEY_Escape:
            self.hide()
            return True
        # Only date-cell focus overrides arrows, preserving native control navigation.
        if self.get_focus() not in self.cells.values():
            return False
        deltas = {Gdk.KEY_Left: 1, Gdk.KEY_Right: -1, Gdk.KEY_Up: -7, Gdk.KEY_Down: 7}
        if k in deltas:
            day = self.selected + timedelta(days=deltas[k])
            try:
                j = jalali(day)
            except ValueError:
                return True
            self.selected = day
            self.year, self.month = j.year, j.month
            self.apply()
            self.focus_selected()
            return True
        if k in (Gdk.KEY_Page_Up, Gdk.KEY_Page_Down):
            self.navigate(-1 if k == Gdk.KEY_Page_Up else 1)
            return True
        if k in (Gdk.KEY_Home, Gdk.KEY_End):
            self.select(
                gregorian(
                    self.year, self.month, 1 if k == Gdk.KEY_Home else month_length(self.year, self.month)
                )
            )
            return True
        return False

    def apply(self):
        was_visible = self.get_visible()
        loc = self.app.loc
        repo = self.app.repo
        cfg = self.app.cfg
        self.set_direction(Gtk.TextDirection.RTL if loc.lang == "fa" else Gtk.TextDirection.LTR)
        self.set_title("روز · تقویم" if loc.lang == "fa" else "Rooz · Calendar")
        clear(self.root)
        self.cells = {}
        header = Gtk.Box(spacing=8)
        self.root.pack_start(header, False, False, 0)
        title = label(loc.n(f"{JMONTHS[loc.lang][self.month - 1]} {self.year}"), "heading")
        header.pack_start(title, True, True, 0)
        header.pack_end(button("×", self.hide, loc.t("close")), False, False, 0)
        header.pack_end(button("⚙", self.app.open_settings, loc.t("settings")), False, False, 0)
        first = gregorian(self.year, self.month, 1)
        last = gregorian(self.year, self.month, month_length(self.year, self.month))
        span = loc.n(
            f"{GMONTHS[loc.lang][first.month - 1]} {first.year} — {GMONTHS[loc.lang][last.month - 1]} {last.year}"
        )
        self.root.pack_start(label(span, "muted"), False, False, 0)
        nav = Gtk.Box(spacing=5)
        self.root.pack_start(nav, False, False, 0)
        for text, delta, key in [("«", -12, "previous_year"), ("‹", -1, "previous_month")]:
            b = button(text, lambda d=delta: self.navigate(d), loc.t(key))
            b.set_sensitive(not (self.year == MIN_YEAR and (delta == -12 or self.month == 1)))
            nav.pack_start(b, False, False, 0)
        b = button(loc.t("today"), self.go_today, loc.t("today"))
        nav.pack_start(b, True, False, 0)
        for text, delta, key in [("›", 1, "next_month"), ("»", 12, "next_year")]:
            b = button(text, lambda d=delta: self.navigate(d), loc.t(key))
            b.set_sensitive(not (self.year == MAX_YEAR and (delta == 12 or self.month == 12)))
            nav.pack_start(b, False, False, 0)
        grid = Gtk.Grid()
        grid.set_direction(Gtk.TextDirection.LTR)
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(2)
        grid.set_column_spacing(4)
        self.root.pack_start(grid, False, False, 0)
        for col, wd in enumerate(SHORT_WEEK[loc.lang]):
            weekday_label = label(wd, "holiday" if col == 0 else "muted", 0.5)
            grid.attach(weekday_label, col, 0, 1, 1)
        cells = month_cells(self.year, self.month)
        rows = max(5, max(c.row for c in cells) + 1)
        for row in range(rows):
            for col in range(7):
                spacer = Gtk.Box()
                spacer.set_size_request(-1, 43)
                grid.attach(spacer, col, row + 1, 1, 1)
        for cell in cells:
            b = Gtk.Button()
            b.get_style_context().add_class("day")
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            b.add(box)
            number = label(loc.n(cell.solar_day), "primary", 0.5)
            box.pack_start(number, False, False, 0)
            if cell.day.weekday() == 4:
                number.get_style_context().add_class("friday")
            holiday = repo.holiday(cell.day)
            all_events = repo.events(cell.day)
            visible = repo.visible(cell.day, cfg["events"])
            markers = "◆" if holiday else "•" if visible else ""
            secondary = (
                loc.n(cell.day.day) + " " if cfg["calendar"]["show_gregorian_cell_numbers"] else ""
            ) + markers
            sub = label(secondary, "holiday" if holiday else "muted", 0.5)
            box.pack_start(sub, False, False, 0)
            if cell.day == self.app.today:
                b.get_style_context().add_class("today")
            if cell.day == self.selected:
                b.get_style_context().add_class("selected")
            tags = []
            if holiday:
                tags.append(loc.t("holiday"))
            if cell.day.weekday() == 4:
                tags.append(loc.t("friday"))
            if cell.day == self.app.today:
                tags.append(loc.t("today"))
            tip = (
                full_date(cell.day, loc, repo)
                + "\n"
                + " · ".join(tags)
                + "\n"
                + "\n".join(loc.event_title(e) for e in all_events)
            )
            b.set_tooltip_text(tip)
            b.get_accessible().set_name(tip)
            b.connect("clicked", lambda _, d=cell.day: self.select(d))
            grid.attach(b, cell.column, cell.row + 1, 1, 1)
            self.cells[cell.day] = b
        self.root.pack_start(Gtk.Separator(), False, False, 3)
        day_header = WEEKDAYS[loc.lang][self.selected.weekday()] + " · " + dates(self.selected, loc, repo)[0]
        self.root.pack_start(label(day_header), False, False, 0)
        self.root.pack_start(
            label(" · ".join(dates(self.selected, loc, repo)[1:]), "muted", wrap=True), False, False, 0
        )
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(48)
        details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        scroll.add(details)
        self.root.pack_start(scroll, True, True, 0)
        es = repo.visible(self.selected, cfg["events"])
        if not repo.known(self.selected):
            details.pack_start(label(loc.t("incomplete"), "muted", wrap=True), False, False, 0)
        if not es:
            key = (
                "filtered"
                if repo.events(self.selected)
                else "empty"
                if repo.known(self.selected)
                else "hijri_unavailable"
            )
            details.pack_start(label(loc.t(key), "muted", wrap=True), False, False, 0)
        for e in es:
            prefix = (
                "◆ " + loc.t("holiday")
                if e["is_public_holiday"]
                else "• " + " / ".join(loc.t(c) for c in e["categories"])
            )
            event = label(
                prefix + " · " + loc.event_title(e), "holiday" if e["is_public_holiday"] else None, wrap=True
            )
            event.set_selectable(True)
            details.pack_start(event, False, False, 0)
        footer = Gtk.Box(spacing=4)
        for key, index in [("copy_persian", 0), ("copy_gregorian", 1), ("copy_all", None)]:
            footer.pack_start(
                button(loc.t(key), lambda i=index: self.app.copy(self.selected, i)), True, True, 0
            )
        self.root.pack_start(footer, False, False, 0)
        direction(self.root, loc.lang == "fa")
        self.show_all()
        if not was_visible:
            self.hide()
