"""A year overview for choosing any Persian month without stepping through months."""

from gi.repository import Gdk, Gtk

from ..calendar_service import MAX_YEAR, MIN_YEAR, jalali
from ..i18n import JMONTHS
from .common import button, clear, direction, label


class MonthPicker(Gtk.Popover):
    def __init__(self, calendar, anchor):
        super().__init__(relative_to=anchor)
        self.calendar = calendar
        self.year = calendar.year
        self.month_buttons = {}
        self.get_style_context().add_class("rooz")
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.root.set_border_width(12)
        self.add(self.root)
        self.connect("key-press-event", self.key)
        self.apply()

    def key(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.popdown()
            return True
        return False

    def change_year(self, delta):
        if MIN_YEAR <= self.year + delta <= MAX_YEAR:
            self.year += delta
            self.apply()

    def choose(self, month):
        # Calendar.apply dismisses this popover before rebuilding its anchor button.
        self.calendar.choose_month(self.year, month)

    def apply(self):
        loc = self.calendar.app.loc
        rtl = loc.lang == "fa"
        clear(self.root)
        self.root.pack_start(label(loc.t("choose_month"), "heading", 0.5), False, False, 0)
        header = Gtk.Box(spacing=8)
        self.previous_year = button("‹", lambda: self.change_year(-1), loc.t("previous_year"))
        self.previous_year.set_sensitive(self.year > MIN_YEAR)
        self.next_year = button("›", lambda: self.change_year(1), loc.t("next_year"))
        self.next_year.set_sensitive(self.year < MAX_YEAR)
        header.pack_start(self.previous_year, False, False, 0)
        header.pack_start(label(loc.n(self.year), "heading", 0.5), True, True, 0)
        header.pack_start(self.next_year, False, False, 0)
        self.root.pack_start(header, False, False, 0)

        grid = Gtk.Grid()
        grid.set_direction(Gtk.TextDirection.LTR)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(4)
        grid.set_row_spacing(4)
        self.root.pack_start(grid, False, False, 0)
        self.month_buttons = {}
        today = jalali(self.calendar.app.today)
        for index, name in enumerate(JMONTHS[loc.lang]):
            month = index + 1
            b = button(loc.n(name), lambda m=month: self.choose(m))
            b.get_accessible().set_name(loc.n(f"{name} {self.year}"))
            b.set_tooltip_text(loc.n(f"{name} {self.year}"))
            if (self.year, month) == (self.calendar.year, self.calendar.month):
                b.get_style_context().add_class("selected")
            if (self.year, month) == (today.year, today.month):
                b.get_style_context().add_class("today")
            column = 2 - index % 3 if rtl else index % 3
            grid.attach(b, column, index // 3, 1, 1)
            self.month_buttons[month] = b
        direction(self.root, rtl)
        self.show_all()

    def focus_month(self):
        self.month_buttons[self.calendar.month].grab_focus()
