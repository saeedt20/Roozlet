"""Native accessible month view; locale-aware Iranian week layout and scenic header."""

from datetime import timedelta

from gi.repository import Gdk, Gtk

from ..calendar_service import MAX_YEAR, MIN_YEAR, gregorian, jalali, month_cells, month_length, shift_month
from ..formatting import dates, full_date
from ..i18n import GMONTHS, JMONTHS, SHORT_WEEK, WEEKDAYS
from .common import button, clear, direction, label, navigation_item, brand
from .month_picker import MonthPicker
from .theme import style_window
from .presentation import ScenicSurface
from .motion import ContentStack, enabled


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
        self.set_default_size(min(880, area.width - 48), min(640, area.height - 120))
        self.set_size_request(360, 300)
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.root.set_border_width(18)
        self.outer = Gtk.ScrolledWindow()
        self.outer.set_overlay_scrolling(False)
        self.outer.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.outer.add(self.root)
        self.view = "calendar"
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.sidebar.get_style_context().add_class("sidebar")
        self.sidebar.set_size_request(156, -1)
        self.sidebar.set_no_show_all(True)
        self.shell = Gtk.Box(spacing=4)
        self.shell.set_direction(Gtk.TextDirection.LTR)
        self.page_stack = Gtk.Stack()
        self.page_stack.set_hhomogeneous(False)
        self.page_stack.set_vhomogeneous(False)
        self.page_stack.set_interpolate_size(False)
        self.page_stack.add_named(self.outer, "calendar")
        self.panes = {}
        self.shell.pack_start(self.page_stack, True, True, 0)
        self.shell.pack_start(self.sidebar, False, False, 0)
        self.add(self.shell)
        self.header_bar = Gtk.HeaderBar(show_close_button=True)
        self.set_titlebar(self.header_bar)
        from .icons import NavigationIcon
        self.search_button = Gtk.Button()
        self.search_button.add(NavigationIcon("search"))
        self.search_button.connect("clicked", lambda *_: self.open_search())
        self.header_bar.pack_end(self.search_button)
        self.compact_menu = Gtk.MenuButton()
        self.compact_menu.set_image(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU))
        self.compact_menu.set_no_show_all(True)
        self.header_bar.pack_start(self.compact_menu)
        self.hero = ScenicSurface(app, 124)
        self.body_stack = ContentStack()
        self.root.pack_start(self.hero, False, False, 0)
        self.root.pack_start(self.body_stack, False, False, 0)
        self.connect("size-allocate", self.responsive)
        self.connect("delete-event", lambda *_: self.hide() or True)
        self.connect("key-press-event", self.key)
        self.cells = {}
        self.month_picker = None
        self.about_window = None
        self.search_window = self.personal_editor = None
        self.personal_mode = "upcoming"
        self.personal_view = None
        self.connect("destroy", lambda *_: self.dismiss_month_picker())
        self.apply()
        self.show_all()

    def responsive(self, _, allocation):
        wide = allocation.width >= 660
        self.sidebar.set_visible(wide)
        self.compact_menu.set_visible(not wide)
        if hasattr(self, "header_row"):
            narrow = self.hero.get_allocated_width() < 440
            orientation = Gtk.Orientation.VERTICAL if narrow else Gtk.Orientation.HORIZONTAL
            if self.header_row.get_orientation() != orientation:
                self.header_row.set_orientation(orientation)
            self.hero.scene.set_size_request(-1, round((156 if narrow else 124) * max(1, self.app.cfg["appearance"]["text_scale"])))

    def show_view(self, view):
        if self.view == view and (view not in ("settings", "search", "about") or view in self.panes):
            if view == "search":
                self.panes[view].refresh_locale()
                self.panes[view].entry.grab_focus()
            return
        self.view = view
        self.apply(animate=True)

    def refresh_appearance(self):
        """Scenery and typography updates keep current cells, selection and focus."""
        viewed = self.month if self.view in ("calendar", "occasions") else None
        style_window(self, self.app.cfg, self.app.today, viewed)
        self.hero.sync(self.month)
        for menu in (self.compact_menu.get_popup(), getattr(self, "copy_menu", None)):
            if menu:
                style_window(menu, self.app.cfg, self.app.today, self.month)
        if not enabled(self.app.cfg, self):
            self.page_stack.set_transition_type(Gtk.StackTransitionType.NONE)
            self.page_stack.set_transition_duration(0)
            self.body_stack.set_transition_type(Gtk.StackTransitionType.NONE)
            self.body_stack.set_transition_duration(0)
            self.body_stack.prune(force=True)
        self.responsive(self, self.get_allocation())

    def show_about(self):
        self.show_view("about")
        return self.panes["about"]

    def open_search(self):
        self.show_view("search")
        return self.search_window

    def show_pane(self, animate):
        from .settings import SettingsPane
        from .search_window import SearchPane
        from .about import AboutPane
        kind = {"settings": SettingsPane, "search": SearchPane, "about": AboutPane}[self.view]
        pane = self.panes.get(self.view)
        locale_key = (self.app.loc.lang, self.app.cfg["digits"],
                      self.app.cfg["appearance"]["font_mode"],
                      self.app.cfg["appearance"]["custom_font_family"])
        if pane is not None and self.view == "about" and pane.locale_key != locale_key:
            self.page_stack.remove(pane)
            pane.destroy()
            pane = None
        if pane is None:
            pane = kind(self.app if self.view == "settings" else self)
            pane.locale_key = locale_key
            self.panes[self.view] = pane
            self.page_stack.add_named(pane, self.view)
            pane.connect("destroy", self.pane_closed, self.view)
            if self.view == "settings":
                self.app.settings = pane
            elif self.view == "search":
                self.search_window = pane
        elif self.view == "settings":
            if pane.locale_key != locale_key:
                pane.apply()
                pane.locale_key = locale_key
            else:
                pane.refresh_appearance()
        elif self.view == "search":
            pane.refresh_locale()
        pane.show_all()
        style_window(pane, self.app.cfg, self.app.today)
        if self.view == "about":
            pane.stack.set_transition_duration(160 if enabled(self.app.cfg, self) else 0)
            pane.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE if enabled(self.app.cfg, self)
                                           else Gtk.StackTransitionType.NONE)
        if self.view == "settings":
            pane.responsive(pane, pane.get_allocation())
        self.page_stack.set_transition_duration(160 if animate and enabled(self.app.cfg, self) else 0)
        self.page_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE if animate and enabled(self.app.cfg, self)
                                            else Gtk.StackTransitionType.NONE)
        self.page_stack.set_visible_child(pane)
        if self.view == "search":
            pane.entry.grab_focus()

    def pane_closed(self, pane, key):
        if self.panes.get(key) is pane:
            self.panes.pop(key)
        if key == "search" and self.search_window is pane:
            self.search_window = None
        if key == "settings" and getattr(self.app, "settings", None) is pane:
            self.app.settings = None

    def open_personal_editor(self, day, item_id=None):
        from .personal import PersonalEditor
        if not getattr(self.app, "personal", None):
            return None
        if self.personal_editor is None:
            self.personal_editor = PersonalEditor(self, day, item_id)
            self.personal_editor.connect("destroy", lambda *_: setattr(self, "personal_editor", None))
        self.personal_editor.present()
        return self.personal_editor

    def personal_on(self, day):
        from ..personal import PersonalError
        if not getattr(self.app, "personal", None):
            return []
        try:
            return self.app.personal.on(day)
        except PersonalError:
            self.app.personal_error = True
            return []

    def navigate(self, delta):
        self.year, self.month = shift_month(self.year, self.month, delta)
        old = jalali(self.selected)
        self.selected = gregorian(self.year, self.month, min(old.day, month_length(self.year, self.month)))
        self.apply(animate=True)
        self.focus_selected()

    def go_today(self):
        self.view = "calendar"
        self.selected = self.app.today
        j = jalali(self.selected)
        self.year, self.month = j.year, j.month
        self.apply(animate=True)
        self.focus_selected()

    def choose_month(self, year, month):
        if not (MIN_YEAR <= year <= MAX_YEAR and 1 <= month <= 12):
            return
        old = jalali(self.selected)
        self.year, self.month = year, month
        self.selected = gregorian(year, month, min(old.day, month_length(year, month)))
        self.apply(animate=True)
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
        j = jalali(day)
        self.year, self.month = j.year, j.month
        self.apply()
        self.focus_selected()

    def focus_selected(self):
        if self.selected in self.cells:
            self.cells[self.selected].grab_focus()

    def key(self, _, event):
        k = event.keyval
        if getattr(event, "state", 0) & Gdk.ModifierType.CONTROL_MASK:
            if k in (Gdk.KEY_f, Gdk.KEY_F, Gdk.KEY_k, Gdk.KEY_K):
                self.open_search()
                return True
            if k in (Gdk.KEY_n, Gdk.KEY_N):
                self.open_personal_editor(self.selected)
                return True
        if k == Gdk.KEY_Escape:
            if self.month_picker:
                self.dismiss_month_picker()
                return True
            if self.view in ("settings", "search", "about"):
                self.show_view("calendar")
                return True
            self.hide()
            return True
        # Only date-cell focus overrides arrows, preserving native control navigation.
        if self.get_focus() not in self.cells.values():
            return False
        forward = 1 if self.app.loc.lang == "en" else -1
        deltas = {Gdk.KEY_Left: -forward, Gdk.KEY_Right: forward, Gdk.KEY_Up: -7, Gdk.KEY_Down: 7}
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

    def apply(self, animate=False):
        self.dismiss_month_picker()
        was_visible = self.get_visible()
        loc, repo, cfg = self.app.loc, self.app.repo, self.app.cfg
        rtl = loc.lang == "fa"
        self.set_direction(Gtk.TextDirection.RTL if rtl else Gtk.TextDirection.LTR)
        style_window(self, cfg, self.app.today, self.month if self.view in ("calendar", "occasions") else None)
        title_text = ("روزلت" if rtl else "Roozlet") + " · " + loc.t(self.view)
        self.set_title(title_text)
        self.header_bar.set_title(title_text)
        self.search_button.set_tooltip_text(loc.t("search") + " · Ctrl+F")
        self.search_button.get_accessible().set_name(loc.t("search"))
        self.shell.set_direction(Gtk.TextDirection.LTR)
        self.shell.reorder_child(self.sidebar, 1 if rtl else 0)
        clear(self.sidebar)
        self.sidebar.pack_start(brand("روزلت" if rtl else "Roozlet", rtl), False, False, 10)
        self.nav_items = {}
        actions = [("calendar", "x-office-calendar-symbolic", lambda: self.show_view("calendar")),
                   ("today", "go-jump-symbolic", self.go_today),
                   ("occasions", "view-list-symbolic", lambda: self.show_view("occasions")),
                   ("search", "edit-find-symbolic", self.open_search),
                   ("personal", "accessories-text-editor-symbolic", lambda: self.show_view("personal")),
                   ("settings", "emblem-system-symbolic", self.app.open_settings),
                   ("about", "help-about-symbolic", lambda: self.show_view("about"))]
        popup = Gtk.Menu()
        popup.get_style_context().add_class("rooz")
        style_window(popup, cfg, self.app.today, self.month)
        for key, icon, callback in actions:
            item = navigation_item(loc.t(key), icon, callback, rtl)
            if key == self.view:
                item.get_style_context().add_class("selected")
            self.sidebar.pack_start(item, False, False, 0)
            self.nav_items[key] = item
            menu_item = Gtk.MenuItem(label=loc.t(key))
            menu_item.connect("activate", lambda _, fn=callback: fn())
            popup.append(menu_item)
        direction(self.sidebar, rtl)
        direction(popup, rtl)
        for child in self.sidebar.get_children():
            child.show_all()
        popup.show_all()
        old_popup = self.compact_menu.get_popup()
        self.compact_menu.set_popup(popup)
        if old_popup:
            old_popup.destroy()
        self.compact_menu.set_tooltip_text(loc.t("open"))
        if self.view in ("settings", "search", "about"):
            self.show_pane(animate and was_visible)
            self.show_all()
            self.responsive(self, self.get_allocation())
            if self.view == "settings":
                self.panes["settings"].responsive(self.panes["settings"], self.panes["settings"].get_allocation())
            if not was_visible:
                self.hide()
            return
        self.page_stack.set_transition_duration(160 if animate and was_visible and enabled(cfg, self) else 0)
        self.page_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE if animate and was_visible and enabled(cfg, self)
                                            else Gtk.StackTransitionType.NONE)
        self.page_stack.set_visible_child(self.outer)
        self.hero.sync(self.month)
        clear(self.hero.content)
        header = Gtk.Box(spacing=12)
        self.header_row = header
        self.hero.content.pack_start(header, True, True, 0)
        heading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        title = button(loc.n(f"{JMONTHS[loc.lang][self.month - 1]} {self.year}") + "  ▾",
                       lambda: self.open_month_picker(self.title_button), loc.t("choose_month"))
        title.get_style_context().add_class("month-title")
        title.set_halign(Gtk.Align.START)
        self.title_button = title
        heading.pack_start(title, False, False, 0)
        first = gregorian(self.year, self.month, 1)
        last = gregorian(self.year, self.month, month_length(self.year, self.month))
        span = loc.n(f"{GMONTHS[loc.lang][first.month - 1]} {first.year} — {GMONTHS[loc.lang][last.month - 1]} {last.year}")
        heading.pack_start(label(span, "muted", wrap=True), False, False, 0)
        header.pack_start(heading, True, True, 0)
        nav = Gtk.Box(spacing=4)
        nav.set_valign(Gtk.Align.END)
        header.pack_end(nav, False, False, 0)
        previous = button("›" if rtl else "‹", lambda: self.navigate(-1), loc.t("previous_month"))
        previous.set_sensitive(not (self.year == MIN_YEAR and self.month == 1))
        nav.pack_start(previous, False, False, 0)
        self.today_button = button(loc.t("today"), self.go_today, loc.t("today_help"))
        self.today_button.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.today_button.connect("button-press-event", self.today_press)
        self.today_button.connect("popup-menu", lambda *_: self.open_month_picker())
        nav.pack_start(self.today_button, False, False, 0)
        following = button("‹" if rtl else "›", lambda: self.navigate(1), loc.t("next_month"))
        following.set_sensitive(not (self.year == MAX_YEAR and self.month == 12))
        nav.pack_start(following, False, False, 0)
        direction(self.hero.content, rtl)
        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.cells = {}
        self.personal_view = None
        if self.view == "occasions":
            self.build_occasions(first, last)
        elif self.view == "personal":
            from .personal import PersonalView
            self.personal_view = PersonalView(self)
            self.body.pack_start(self.personal_view, False, False, 0)
        else:
            self.build_calendar()
        direction(self.body, rtl)
        self.body_stack.replace(self.body, cfg, animate and was_visible, 160)
        direction(self.root, rtl)
        self.show_all()
        self.responsive(self, self.get_allocation())
        if not was_visible:
            self.hide()

    def build_calendar(self):
        loc, repo, cfg = self.app.loc, self.app.repo, self.app.cfg
        rtl = loc.lang == "fa"
        grid = Gtk.Grid()
        grid.set_direction(Gtk.TextDirection.LTR)
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(2)
        grid.set_column_spacing(4)
        self.body.pack_start(grid, False, False, 0)
        weekdays = SHORT_WEEK[loc.lang] if rtl else list(reversed(SHORT_WEEK[loc.lang]))
        for col, wd in enumerate(weekdays):
            weekday_label = label(wd, "holiday" if col == (0 if rtl else 6) else "muted", 0.5)
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
            personal = getattr(self.app, "personal", None)
            personal_entries = self.personal_on(cell.day) if personal else []
            if personal_entries:
                markers += " ◇"
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
                + ("\n" + loc.t("personal") + ": " + " · ".join(o.item["title"] for o in personal_entries) if personal_entries else "")
            )
            b.set_tooltip_text(tip)
            b.get_accessible().set_name(tip)
            b.connect("clicked", lambda _, d=cell.day: self.select(d))
            grid.attach(b, cell.column if rtl else 6 - cell.column, cell.row + 1, 1, 1)
            self.cells[cell.day] = b
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        panel.get_style_context().add_class("details-panel")
        self.body.pack_start(panel, False, False, 0)
        top = Gtk.Box(spacing=12)
        panel.pack_start(top, False, False, 0)
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        day_header = WEEKDAYS[loc.lang][self.selected.weekday()] + " · " + dates(self.selected, loc, repo)[0]
        titles.pack_start(label(day_header, "detail-heading", wrap=True), False, False, 0)
        titles.pack_start(label(" · ".join(dates(self.selected, loc, repo)[1:]), "muted", wrap=True), False, False, 0)
        top.pack_start(titles, True, True, 0)
        self.copy_button = Gtk.MenuButton(label=loc.t("copy_date") + "  ▾")
        self.copy_button.set_valign(Gtk.Align.START)
        self.copy_button.get_style_context().add_class("copy-button")
        self.copy_button.get_accessible().set_name(loc.t("copy_date"))
        self.copy_menu = Gtk.Menu()
        self.copy_menu.get_style_context().add_class("rooz")
        style_window(self.copy_menu, cfg, self.app.today, self.month)
        for key, index in (("copy_persian", 0), ("copy_gregorian", 1), ("copy_hijri", 2), ("copy_all", None)):
            item = Gtk.MenuItem(label=loc.t(key))
            if index == 2:
                item.set_sensitive(bool(repo.hijri(self.selected)))
            item.connect("activate", lambda _, i=index: self.app.copy(self.selected, i))
            self.copy_menu.append(item)
        numeric = Gtk.MenuItem(label=loc.t("copy_numeric"))
        submenu = Gtk.Menu()
        for key, index in (("copy_persian", 0), ("copy_gregorian", 1), ("copy_hijri", 2), ("copy_all", None)):
            item = Gtk.MenuItem(label=loc.t(key))
            item.set_sensitive(index != 2 or bool(repo.hijri(self.selected)))
            item.connect("activate", lambda _, i=index: self.app.copy(self.selected, i, numerical=True))
            submenu.append(item)
        numeric.set_submenu(submenu)
        self.copy_menu.append(numeric)
        direction(self.copy_menu, rtl)
        self.copy_menu.show_all()
        self.copy_button.set_popup(self.copy_menu)
        top.pack_end(self.copy_button, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(42)
        scroll.set_max_content_height(110)
        scroll.set_propagate_natural_height(True)
        details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scroll.add(details)
        panel.pack_start(scroll, False, False, 0)
        events = repo.visible(self.selected, cfg["events"])
        if not repo.known(self.selected):
            details.pack_start(label(loc.t("incomplete"), "muted", wrap=True), False, False, 0)
        if not events:
            key = "filtered" if repo.events(self.selected) else "empty" if repo.known(self.selected) else "hijri_unavailable"
            details.pack_start(label(loc.t(key), "muted", wrap=True), False, False, 0)
        for event in events:
            prefix = "◆ " + loc.t("holiday") if event["is_public_holiday"] else "• " + " / ".join(loc.t(c) for c in event["categories"])
            item = label(prefix + " · " + loc.event_title(event), "holiday" if event["is_public_holiday"] else None, wrap=True)
            item.set_selectable(True)
            details.pack_start(item, False, False, 0)
        from .personal import PersonalView
        self.personal_view = PersonalView(self, compact=True)
        self.body.pack_start(self.personal_view, False, False, 0)

    def build_occasions(self, first, last):
        loc, repo, cfg = self.app.loc, self.app.repo, self.app.cfg
        self.body.pack_start(label(loc.t("occasions"), "heading"), False, False, 4)
        if not repo.known(first):
            self.body.pack_start(label(loc.t("incomplete"), "muted", wrap=True), False, False, 8)
            return
        any_visible = False
        day = first
        while day <= last:
            events = repo.visible(day, cfg["events"])
            if events:
                any_visible = True
                row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                row.get_style_context().add_class("details-panel")
                row.pack_start(button(dates(day, loc, repo)[0], lambda d=day: self.select(d)), False, False, 0)
                for event in events:
                    value = ("◆ " if event["is_public_holiday"] else "• ") + loc.event_title(event)
                    row.pack_start(label(value, "holiday" if event["is_public_holiday"] else None, wrap=True), False, False, 0)
                self.body.pack_start(row, False, False, 7)
                self.body.pack_start(Gtk.Separator(), False, False, 0)
            day += timedelta(days=1)
        if not any_visible:
            self.body.pack_start(label(loc.t("filtered"), "muted", wrap=True), False, False, 8)
