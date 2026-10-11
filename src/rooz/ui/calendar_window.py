"""Native accessible month view; fixed Iranian physical weekday order."""

from datetime import timedelta

from gi.repository import Gdk, Gtk

from ..calendar_service import MAX_YEAR, MIN_YEAR, gregorian, jalali, month_cells, month_length, shift_month
from ..formatting import dates, full_date
from ..i18n import GMONTHS, JMONTHS, SHORT_WEEK, WEEKDAYS
from .common import button, clear, direction, label
from .month_picker import MonthPicker
from .theme import style_window
from .artwork import ScenicBand


class CalendarWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Roozlet")
        self.app = app
        self.selected = app.today
        j = jalali(app.today)
        self.year, self.month = j.year, j.month
        self.get_style_context().add_class("rooz")
        monitor = self.get_display().get_primary_monitor() or self.get_display().get_monitor(0)
        area = monitor.get_workarea()
        self.set_default_size(min(860, area.width - 48), min(680, area.height - 64))
        self.set_size_request(360, 300)
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.root.set_border_width(14)
        self.outer = Gtk.ScrolledWindow()
        self.outer.set_overlay_scrolling(False)
        self.outer.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.outer.add(self.root)
        self.view = "calendar"
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.sidebar.get_style_context().add_class("sidebar")
        self.sidebar.set_size_request(148, -1)
        self.sidebar.set_no_show_all(True)
        self.shell = Gtk.Box(spacing=4)
        self.shell.set_direction(Gtk.TextDirection.LTR)
        self.shell.pack_start(self.outer, True, True, 0)
        self.shell.pack_start(self.sidebar, False, False, 0)
        self.add(self.shell)
        self.connect("size-allocate", self.responsive)
        self.connect("delete-event", lambda *_: self.hide() or True)
        self.connect("key-press-event", self.key)
        self.cells = {}
        self.month_picker = None
        self.connect("destroy", lambda *_: self.dismiss_month_picker())
        self.apply()
        self.show_all()

    def responsive(self, _, allocation):
        self.sidebar.set_visible(allocation.width >= 660)

    def show_view(self, view):
        self.view = view
        self.apply()

    def show_about(self):
        from .. import __version__
        from ..resources import DATA
        dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        dialog.set_program_name("روزلت" if self.app.loc.lang == "fa" else "Roozlet")
        dialog.set_version(__version__)
        dialog.set_authors(["Saeed Taheri"])
        dialog.set_website("https://github.com/saeedt20/Roozlet")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_comments(self.app.loc.t("coverage"))
        attribution = DATA / "themes/seasons/ATTRIBUTION.md"
        dialog.add_credit_section(self.app.loc.t("attribution"), [
            "Vazirmatn — SIL Open Font License 1.1",
            "University of Tehran Calendar Center — verified 1405 dates and occasions",
            attribution.read_text() if attribution.is_file() else "Roozlet original seasonal artwork",
        ])
        dialog.connect("response", lambda d, _: d.destroy())
        style_window(dialog, self.app.cfg, self.app.today)
        dialog.get_style_context().add_class("rooz")
        dialog.show()

    def navigate(self, delta):
        self.year, self.month = shift_month(self.year, self.month, delta)
        old = jalali(self.selected)
        self.selected = gregorian(self.year, self.month, min(old.day, month_length(self.year, self.month)))
        self.apply()
        self.focus_selected()

    def go_today(self):
        self.view = "calendar"
        self.selected = self.app.today
        j = jalali(self.selected)
        self.year, self.month = j.year, j.month
        self.apply()
        self.focus_selected()

    def choose_month(self, year, month):
        if not (MIN_YEAR <= year <= MAX_YEAR and 1 <= month <= 12):
            return
        old = jalali(self.selected)
        self.year, self.month = year, month
        self.selected = gregorian(year, month, min(old.day, month_length(year, month)))
        self.apply()
        self.focus_selected()

    def dismiss_month_picker(self):
        picker, self.month_picker = self.month_picker, None
        if picker:
            picker.popdown()
            picker.destroy()

    def open_month_picker(self, anchor=None):
        self.dismiss_month_picker()
        self.month_picker = MonthPicker(self, anchor or self.today_button)
        self.month_picker.popup()
        self.month_picker.focus_month()
        return True

    def today_press(self, _, event):
        if event.button == 3:
            return self.open_month_picker()
        return False

    def select(self, day):
        self.view = "calendar"
        self.selected = day
        self.apply()
        self.focus_selected()

    def focus_selected(self):
        if self.selected in self.cells:
            self.cells[self.selected].grab_focus()

    def key(self, _, event):
        k = event.keyval
        if k == Gdk.KEY_Escape:
            if self.month_picker:
                self.dismiss_month_picker()
                return True
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
        self.dismiss_month_picker()
        was_visible = self.get_visible()
        loc = self.app.loc
        repo = self.app.repo
        cfg = self.app.cfg
        self.set_direction(Gtk.TextDirection.RTL if loc.lang == "fa" else Gtk.TextDirection.LTR)
        season = style_window(self, cfg, self.app.today, self.month)
        self.set_title("روزلت · تقویم" if loc.lang == "fa" else "Roozlet · Calendar")
        self.shell.set_direction(Gtk.TextDirection.LTR)
        self.shell.reorder_child(self.sidebar, 1 if loc.lang == "fa" else 0)
        clear(self.sidebar)
        brand = Gtk.Box(spacing=7)
        from .icons import Mark
        from .theme import tokens
        brand.pack_start(Mark("autumn", tokens(cfg, self.app.today, self.month)["accent_text"], 24), False, False, 0)
        brand.pack_start(label("روزلت" if loc.lang == "fa" else "Roozlet", "heading"), True, True, 0)
        self.sidebar.pack_start(brand, False, False, 10)
        for key, callback in [
            ("calendar", lambda: self.show_view("calendar")),
            ("today", self.go_today),
            ("occasions", lambda: self.show_view("occasions")),
            ("settings", self.app.open_settings),
            ("about", self.show_about),
        ]:
            item = button(loc.t(key), callback)
            row = Gtk.Box(spacing=9)
            item.remove(item.get_child())
            names = {"calendar": "x-office-calendar-symbolic", "today": "go-jump-symbolic",
                     "occasions": "view-list-symbolic", "settings": "emblem-system-symbolic", "about": "help-about-symbolic"}
            row.pack_start(Gtk.Image.new_from_icon_name(names[key], Gtk.IconSize.MENU), False, False, 0)
            row.pack_start(label(loc.t(key)), True, True, 0)
            item.add(row)
            item.get_accessible().set_name(loc.t(key))
            if key == self.view:
                item.get_style_context().add_class("selected")
            self.sidebar.pack_start(item, False, False, 0)
        self.sidebar.pack_start(Gtk.Box(), True, True, 0)
        if cfg["appearance"]["style"] == "seasonal" and cfg["appearance"]["show_artwork"]:
            self.sidebar.pack_start(ScenicBand(season, 120, cfg["appearance"]["artwork_intensity"]), False, False, 0)
        direction(self.sidebar, loc.lang == "fa")
        for child in self.sidebar.get_children():
            child.show_all()
        clear(self.root)
        self.cells = {}
        header = Gtk.Box(spacing=8)
        self.root.pack_start(header, False, False, 0)
        title = button(loc.n(f"{JMONTHS[loc.lang][self.month - 1]} {self.year}") + "  ▾", lambda: self.open_month_picker(self.title_button), loc.t("choose_month"))
        title.get_style_context().add_class("month-title")
        self.title_button = title
        header.pack_start(title, True, False, 0)
        header.pack_end(button("×", self.hide, loc.t("close")), False, False, 0)
        header.pack_end(button("⚙", self.app.open_settings, loc.t("settings")), False, False, 0)
        menu = Gtk.MenuButton()
        menu.set_label("≡")
        menu.set_tooltip_text(loc.t("occasions"))
        menu.get_accessible().set_name(loc.t("open"))
        popup = Gtk.Menu()
        popup.get_style_context().add_class("rooz")
        style_window(popup, cfg, self.app.today, self.month)
        for key, fn in [("calendar", lambda: self.show_view("calendar")), ("occasions", lambda: self.show_view("occasions")), ("about", self.show_about)]:
            item = Gtk.MenuItem(label=loc.t(key))
            item.connect("activate", lambda _, f=fn: f())
            popup.append(item)
        popup.show_all()
        menu.set_popup(popup)
        header.pack_end(menu, False, False, 0)
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
        b = button(loc.t("today"), self.go_today, loc.t("today_help"))
        b.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        b.connect("button-press-event", self.today_press)
        b.connect("popup-menu", lambda *_: self.open_month_picker())
        self.today_button = b
        nav.pack_start(b, True, False, 0)
        for text, delta, key in [("›", 1, "next_month"), ("»", 12, "next_year")]:
            b = button(text, lambda d=delta: self.navigate(d), loc.t(key))
            b.set_sensitive(not (self.year == MAX_YEAR and (delta == 12 or self.month == 12)))
            nav.pack_start(b, False, False, 0)
        if self.view == "occasions":
            self.build_occasions(first, last)
            direction(self.root, loc.lang == "fa")
            self.show_all()
            self.responsive(self, self.get_allocation())
            if not was_visible:
                self.hide()
            return
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
                spacer.set_size_request(-1, 48)
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
        if cfg["appearance"]["style"] == "seasonal" and cfg["appearance"]["show_artwork"]:
            self.root.pack_start(ScenicBand(season, 88, cfg["appearance"]["artwork_intensity"]), False, False, 0)
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
        self.responsive(self, self.get_allocation())
        if not was_visible:
            self.hide()

    def build_occasions(self, first, last):
        loc, repo, cfg = self.app.loc, self.app.repo, self.app.cfg
        self.root.pack_start(label(loc.t("occasions"), "heading"), False, False, 4)
        if not repo.known(first):
            self.root.pack_start(label(loc.t("incomplete"), "muted", wrap=True), False, False, 8)
            return
        any_visible = False
        day = first
        while day <= last:
            events = repo.visible(day, cfg["events"])
            if events:
                any_visible = True
                row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                row.pack_start(button(dates(day, loc, repo)[0], lambda d=day: self.select(d)), False, False, 0)
                for event in events:
                    value = ("◆ " if event["is_public_holiday"] else "• ") + loc.event_title(event)
                    row.pack_start(label(value, "holiday" if event["is_public_holiday"] else None, wrap=True), False, False, 0)
                self.root.pack_start(row, False, False, 7)
                self.root.pack_start(Gtk.Separator(), False, False, 0)
            day += timedelta(days=1)
        if not any_visible:
            self.root.pack_start(label(loc.t("filtered"), "muted", wrap=True), False, False, 8)
