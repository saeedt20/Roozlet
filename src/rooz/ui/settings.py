"""Native grouped preferences, mirrored navigation and a live date preview."""

from pathlib import Path
from gi.repository import Gdk, Gtk

from .. import autostart
from ..seasons import SEASONS, effective_season
from .artwork import image
from .common import button, clear, direction, label, navigation_item, brand
from .motion import enabled
from .presentation import DatePreview
from .theme import style_window


class SettingsContent:
    pages = ("appearance", "dates", "events", "desktop")
    icons = ("preferences-desktop-theme-symbolic", "preferences-desktop-locale-symbolic",
             "view-list-symbolic", "preferences-system-symbolic")

    def build(self, app):
        self.app, self.building, self.page = app, False, "appearance"
        self.get_style_context().add_class("rooz")
        if self.embedded:
            self.header = Gtk.Box(spacing=12)
            self.header.set_border_width(12)
            self.header_title = label(app.loc.t("settings"), "heading")
            self.header.pack_start(self.header_title, True, True, 0)
            self.pack_start(self.header, False, False, 0)
        else:
            self.header = Gtk.HeaderBar(show_close_button=True)
            self.set_titlebar(self.header)
        self.page_picker = Gtk.ComboBoxText()
        self.page_picker.connect("changed", lambda b: self.show_page(b.get_active_id()) if not self.building else None)
        self.page_picker.set_no_show_all(True)
        if self.embedded:
            self.header.pack_end(self.page_picker, False, False, 0)
        else:
            self.header.pack_end(self.page_picker)
        self.root = Gtk.Box()
        self.root.set_direction(Gtk.TextDirection.LTR)
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.sidebar.get_style_context().add_class("sidebar")
        self.sidebar.set_size_request(172, -1)
        self.sidebar.set_no_show_all(True)
        self.stack = Gtk.Stack()
        self.stack.set_hhomogeneous(False)
        self.stack.set_vhomogeneous(False)
        self.stack.set_interpolate_size(False)
        self.root.pack_start(self.sidebar, False, False, 0)
        self.root.pack_start(self.stack, True, True, 0)
        if self.embedded:
            self.pack_start(self.root, True, True, 0)
        else:
            self.add(self.root)
        self.connect("size-allocate", self.responsive)
        if not self.embedded:
            self.connect("delete-event", lambda *_: self.hide() or True)
            self.connect("key-press-event", lambda _, e: (self.hide() or True) if e.keyval == Gdk.KEY_Escape else False)
        self.apply()
        self.show_all()
        self.responsive(self, self.get_allocation())

    def responsive(self, _, allocation):
        wide = not self.embedded and self.root.get_allocated_width() >= 660
        self.sidebar.set_visible(wide)
        self.page_picker.set_visible(not wide)

    def change(self, section, key, value):
        if not self.building:
            self.app.change(section, key, value)
            self.refresh_appearance()

    def show_page(self, page):
        if page not in self.pages:
            return
        self.page = page
        self.stack.set_transition_duration(180 if enabled(self.app.cfg, self) else 0)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE if enabled(self.app.cfg, self)
                                       else Gtk.StackTransitionType.NONE)
        self.stack.set_visible_child_name(page)
        for key, item in self.nav_items.items():
            ctx = item.get_style_context()
            ctx.add_class("selected") if key == page else ctx.remove_class("selected")
        self.building = True
        self.page_picker.set_active_id(page)
        self.building = False

    def apply(self):
        was_visible = self.get_visible()
        loc, cfg = self.app.loc, self.app.cfg
        previous_scroll = {k: scroll.get_vadjustment().get_value() for k, scroll in getattr(self, "scrolls", {}).items()}
        advanced_open = getattr(self, "advanced", None)
        advanced_open = advanced_open.get_expanded() if advanced_open else False
        top = self.get_toplevel()
        focus = top.get_focus() if isinstance(top, Gtk.Window) else None
        focused_key = next((k for k, control in getattr(self, "controls", {}).items() if control is focus), None)
        self.building = True
        style_window(self, cfg, self.app.today)
        title = ("روزلت" if loc.lang == "fa" else "Roozlet") + " · " + loc.t("settings")
        if not self.embedded:
            self.set_title(title)
        if self.embedded:
            self.header_title.set_text(loc.t("settings"))
            direction(self.header, loc.lang == "fa")
        else:
            self.header.set_title(title)
        self.set_direction(Gtk.TextDirection.RTL if loc.lang == "fa" else Gtk.TextDirection.LTR)
        self.root.set_direction(Gtk.TextDirection.LTR)
        self.root.reorder_child(self.sidebar, 1 if loc.lang == "fa" else 0)
        clear(self.sidebar)
        self.sidebar.pack_start(brand("روزلت" if loc.lang == "fa" else "Roozlet", loc.lang == "fa"), False, False, 10)
        self.nav_items = {}
        self.page_picker.remove_all()
        self.page_picker.get_accessible().set_name(loc.t("settings"))
        for key, icon in zip(self.pages, self.icons):
            item = navigation_item(loc.t(key), icon, lambda k=key: self.show_page(k), loc.lang == "fa")
            self.sidebar.pack_start(item, False, False, 0)
            self.nav_items[key] = item
            self.page_picker.append(key, loc.t(key))
        direction(self.sidebar, loc.lang == "fa")
        for child in self.sidebar.get_children():
            child.show_all()
        clear(self.stack)
        self.controls, self.scrolls, self.sections = {}, {}, {}
        for key in self.pages:
            scroll = Gtk.ScrolledWindow()
            scroll.set_overlay_scrolling(False)
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_border_width(20)
            box.pack_start(label(loc.t(key), "heading"), False, False, 0)
            scroll.add(box)
            self.sections[key] = box
            self.scrolls[key] = scroll
            self.stack.add_named(scroll, key)

        def group(page):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.get_style_context().add_class("preferences-group")
            page.pack_start(box, False, False, 0)
            return box

        def row(container, key, control, help_key=None):
            control.get_accessible().set_name(loc.t(key))
            if help_key:
                control.get_accessible().set_description(loc.t(help_key))
            if container.get_children():
                container.pack_start(Gtk.Separator(), False, False, 0)
            box = Gtk.Box(spacing=12)
            box.get_style_context().add_class("preference-row")
            text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            text.pack_start(label(loc.t(key), wrap=True), False, False, 0)
            if help_key:
                text.pack_start(label(loc.t(help_key), "muted", wrap=True), False, False, 0)
            box.pack_start(text, True, True, 0)
            control.set_valign(Gtk.Align.CENTER)
            box.pack_end(control, False, False, 0)
            container.pack_start(box, False, False, 0)

        def combo(container, key, section, field, options):
            c = Gtk.ComboBoxText()
            for value, text in options:
                c.append(value, text)
            c.set_active_id(cfg[section][field] if section else cfg[field])
            c.connect("changed", lambda b: self.change(section, field, b.get_active_id()))
            self.controls[section, field] = c
            row(container, key, c)
            return c

        def spin(container, key, section, field, lo, hi, step):
            b = Gtk.SpinButton.new_with_range(lo, hi, step)
            b.set_digits(2)
            b.set_value(cfg[section][field])
            b.set_numeric(True)
            b.connect("value-changed", lambda b: self.change(section, field, b.get_value()))
            self.controls[section, field] = b
            row(container, key, b)

        def toggle(container, key, section, field, help_key=None):
            b = Gtk.Switch()
            b.set_active(cfg[section][field])
            b.connect("notify::active", lambda b, _: self.change(section, field, b.get_active()))
            self.controls[section, field] = b
            row(container, key, b, help_key)
            return b

        appearance = self.sections["appearance"]
        appearance.pack_start(label(loc.t("appearance_intro"), "muted", wrap=True), False, False, 0)
        self.preview = DatePreview(self.app)
        appearance.pack_start(self.preview, False, False, 0)
        basic = group(appearance)
        self.auto_switch = Gtk.Switch()
        self.auto_switch.set_active(cfg["appearance"]["season"] == "auto")
        self.auto_switch.connect("notify::active", self.automatic)
        row(basic, "auto", self.auto_switch, "season_help")
        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_homogeneous(True)
        flow.set_min_children_per_line(2)
        flow.set_max_children_per_line(4)
        flow.set_column_spacing(6)
        flow.set_row_spacing(6)
        self.season_previews = {}
        for season in SEASONS:
            tile = Gtk.Button()
            tile.get_style_context().add_class("season-tile")
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            scene = image(season, 100, 58)
            if scene:
                content.pack_start(Gtk.Image.new_from_pixbuf(scene), False, False, 0)
            content.pack_start(label(loc.t(season), align=.5), False, False, 0)
            tile.add(content)
            tile.get_accessible().set_name(loc.t(season))
            tile.set_tooltip_text(loc.t(season))
            tile.connect("clicked", lambda _, v=season: self.choose_season(v))
            flow.add(tile)
            self.season_previews[season] = tile
        appearance.pack_start(flow, False, False, 0)
        main = group(appearance)
        self.theme_buttons = {}
        modes = Gtk.Box(spacing=4)
        for mode in ("light", "dark"):
            b = Gtk.ToggleButton(label=loc.t(mode))
            b.connect("clicked", lambda _, v=mode: self.change("appearance", "theme", v))
            modes.pack_start(b, False, False, 0)
            self.theme_buttons[mode] = b
        row(main, "color_mode", modes)
        self.intensity = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, .05)
        self.intensity.set_draw_value(False)
        self.intensity.set_size_request(130, -1)
        self.intensity.set_value(cfg["appearance"]["artwork_intensity"])
        self.intensity.get_accessible().set_name(loc.t("artwork_intensity"))
        self.intensity.connect("value-changed", lambda b: self.change("appearance", "artwork_intensity", b.get_value()))
        self.controls["appearance", "artwork_intensity"] = self.intensity
        row(main, "artwork_intensity", self.intensity)
        toggle(main, "motion_effects", "appearance", "motion_effects", "motion_help")
        color = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(cfg["appearance"]["accent_color"])
        color.set_rgba(rgba)
        def choose_color(b):
            if self.building:
                return
            self.app.cfg["appearance"]["accent_source"] = "custom"
            self.change("appearance", "accent_color", "#" + "".join(f"{round(v*255):02X}" for v in
                         (b.get_rgba().red, b.get_rgba().green, b.get_rgba().blue)))
        color.connect("color-set", choose_color)
        row(main, "accent", color)
        self.controls["appearance", "accent_color"] = color
        self.advanced = Gtk.Expander(label=loc.t("advanced"))
        advanced = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        advanced.set_margin_top(10)
        self.advanced.add(advanced)
        self.advanced.set_expanded(advanced_open)
        appearance.pack_start(self.advanced, False, False, 0)
        extra = group(advanced)
        combo(extra, "style", "appearance", "style", [(v, loc.t(v)) for v in ("seasonal", "classic")])
        combo(extra, "accent_source", "appearance", "accent_source", [("seasonal", loc.t("seasonal")), ("custom", loc.t("custom_accent"))])
        toggle(extra, "show_artwork", "appearance", "show_artwork")
        follow = toggle(extra, "follow_month", "appearance", "calendar_follow_viewed_month", "follow_help")
        follow.set_sensitive(cfg["appearance"]["style"] == "seasonal" and cfg["appearance"]["season"] == "auto")
        spin(extra, "opacity", "appearance", "background_opacity", .5, 1, .05)
        spin(extra, "scale", "appearance", "widget_scale", .8, 1.6, .1)
        typography = group(advanced)
        combo(typography, "font", "appearance", "font_mode", [("vazirmatn", "Vazirmatn"), ("system", loc.t("system")), ("custom", loc.t("custom"))])
        font = Gtk.FontButton()
        font.set_use_font(True)
        font.set_show_size(False)
        font.set_font_name(cfg["appearance"]["custom_font_family"])
        def choose_font(b):
            if not self.building:
                self.app.cfg["appearance"]["font_mode"] = "custom"
                self.change("appearance", "custom_font_family", b.get_font_desc().get_family())
        font.connect("font-set", choose_font)
        self.controls["appearance", "custom_font_family"] = font
        row(typography, "custom", font)
        spin(typography, "text_size", "appearance", "text_scale", .85, 1.4, .05)
        advanced.pack_start(label("روزهای روشن؛ زندگی زیباست.\nRoozlet · 0123456789 · ۰۱۲۳۴۵۶۷۸۹", wrap=True), False, False, 0)
        from ..fonts import family
        chosen = "Vazirmatn" if cfg["appearance"]["font_mode"] == "vazirmatn" else cfg["appearance"]["custom_font_family"]
        if cfg["appearance"]["font_mode"] != "system" and family(cfg) == "Sans" and chosen.casefold() != "sans":
            appearance.pack_start(label(loc.t("font_fallback"), "holiday", wrap=True), False, False, 0)
        if self.app.font_warnings:
            appearance.pack_start(label(loc.t("font_load_error"), "holiday", wrap=True), False, False, 0)
        advanced.pack_start(label(loc.t("font_help"), "muted", wrap=True), False, False, 0)
        advanced.pack_start(button(loc.t("reset_appearance"), self.app.reset_appearance), False, False, 0)

        dates = group(self.sections["dates"])
        combo(dates, "language", None, "language", [("fa", "فارسی"), ("en", "English")])
        combo(dates, "digits", None, "digits", [("persian", loc.t("persian")), ("latin", loc.t("latin"))])
        combo(dates, "timezone", None, "timezone", [("Asia/Tehran", loc.t("tehran")), ("system", loc.t("system"))])
        self.sections["dates"].pack_start(label(loc.t("zone_help"), "muted", wrap=True), False, False, 0)
        format_group = group(self.sections["dates"])
        toggle(format_group, "numerical_dates", "calendar", "prefer_numerical_dates", "numerical_help")
        toggle(format_group, "gregorian_cells", "calendar", "show_gregorian_cell_numbers")
        toggle(format_group, "gregorian_column", "calendar", "show_gregorian_column")
        toggle(format_group, "hijri_column", "calendar", "show_hijri_column")
        categories = group(self.sections["events"])
        self.category_switches = {}
        for category in ("national", "cultural", "religious", "international"):
            b = Gtk.Switch()
            b.set_active(category in cfg["events"]["visible_categories"])
            b.connect("notify::active", lambda b, _, c=category: self.filter(b, c))
            row(categories, category, b)
            self.category_switches[category] = b
        holidays = group(self.sections["events"])
        toggle(holidays, "show_holidays", "events", "show_public_holidays")
        toggle(holidays, "countdown", "calendar", "show_next_public_holiday")
        self.sections["events"].pack_start(label(loc.t("coverage") if self.app.repo.reports else loc.t("unavailable"), "muted", wrap=True), False, False, 0)
        if self.app.repo.errors:
            self.sections["events"].pack_start(label(loc.t("source_error"), "holiday", wrap=True), False, False, 0)
        desktop = group(self.sections["desktop"])
        startup = Gtk.Switch()
        startup.set_active(autostart.enabled())
        startup.set_sensitive(Path("/usr/bin/rooz").is_file())
        if not startup.get_sensitive():
            startup.set_tooltip_text(loc.t("startup_help"))
            self.sections["desktop"].pack_start(label(loc.t("startup_help"), "muted", wrap=True), False, False, 0)
        startup.connect("notify::active", self.startup)
        row(desktop, "startup", startup)
        reminders = group(self.sections["desktop"])
        self.notification_switch = toggle(reminders, "desktop_notifications", "personal", "notifications_enabled", "reminder_runtime")
        self.notification_test = button(loc.t("test_notification"), self.app.test_notification)
        self.notification_test.set_sensitive(cfg["personal"]["notifications_enabled"])
        self.sections["desktop"].pack_start(self.notification_test, False, False, 0)
        self.notification_status_label = label("", "muted", wrap=True)
        self.sections["desktop"].pack_start(self.notification_status_label, False, False, 0)
        self.update_notification_status()
        for key, field in (("lock", "locked"), ("above", "always_on_top"), ("all_workspaces", "all_workspaces")):
            toggle(desktop, key, "window", field)
        self.sections["desktop"].pack_start(button(loc.t("reset_position"), self.app.reset_position), False, False, 0)
        if self.app.config.warning:
            self.sections["desktop"].pack_start(label(loc.t("recovered"), "holiday", wrap=True), False, False, 0)
        for box in self.sections.values():
            direction(box, loc.lang == "fa")
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.show_all()
        for key, value in previous_scroll.items():
            if value:
                scroll = self.scrolls[key]
                def restore_scroll(widget, allocation, position=value):
                    widget.get_vadjustment().set_value(position)
                    widget.disconnect(widget._restore_scroll_handler)
                scroll._restore_scroll_handler = scroll.connect("size-allocate", restore_scroll)
        self.building = False
        self.show_page(self.page)
        self.refresh_appearance()
        self.responsive(self, self.get_allocation())
        if focused_key in self.controls:
            self.controls[focused_key].grab_focus()
        if not was_visible:
            self.hide()

    def refresh_appearance(self):
        if self.building or not hasattr(self, "preview"):
            return
        cfg = self.app.cfg
        self.building = True
        for (section, key), control in self.controls.items():
            value = cfg[section][key] if section else cfg[key]
            if isinstance(control, Gtk.Switch):
                control.set_active(value)
            elif isinstance(control, Gtk.ComboBoxText):
                control.set_active_id(value)
            elif isinstance(control, (Gtk.SpinButton, Gtk.Range)):
                control.set_value(value)
        for category, control in self.category_switches.items():
            control.set_active(category in cfg["events"]["visible_categories"])
        self.notification_test.set_sensitive(cfg["personal"]["notifications_enabled"])
        style_window(self, cfg, self.app.today)
        self.auto_switch.set_active(cfg["appearance"]["season"] == "auto")
        season = effective_season(cfg, self.app.today)
        for key, tile in self.season_previews.items():
            context = tile.get_style_context()
            context.add_class("season-choice") if cfg["appearance"]["style"] == "seasonal" and key == season else context.remove_class("season-choice")
        for key, b in self.theme_buttons.items():
            b.set_active(key == cfg["appearance"]["theme"])
            context = b.get_style_context()
            context.add_class("selected") if key == cfg["appearance"]["theme"] else context.remove_class("selected")
        follow = self.controls["appearance", "calendar_follow_viewed_month"]
        follow.set_sensitive(cfg["appearance"]["style"] == "seasonal" and cfg["appearance"]["season"] == "auto")
        from .theme import tokens
        color = Gdk.RGBA()
        color.parse(tokens(cfg, self.app.today)["accent"])
        self.controls["appearance", "accent_color"].set_rgba(color)
        self.preview.sync()
        if not enabled(cfg, self):
            self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
            self.stack.set_transition_duration(0)
        self.building = False

    def update_notification_status(self):
        if not hasattr(self, "notification_status_label"):
            return
        value = getattr(self.app, "notification_available", None)
        self.notification_status_label.set_text(self.app.loc.t("notification_sent") if value is True else
                                                self.app.loc.t("notification_unavailable") if value is False else "")

    def automatic(self, b, _):
        if not self.building:
            self.change("appearance", "season", "auto" if b.get_active() else effective_season(self.app.cfg, self.app.today))

    def choose_season(self, season):
        self.app.cfg["appearance"]["style"] = "seasonal"
        self.change("appearance", "season", season)

    def filter(self, b, category):
        if self.building:
            return
        cats = list(self.app.cfg["events"]["visible_categories"])
        if b.get_active() and category not in cats:
            cats.append(category)
        elif not b.get_active() and category in cats:
            cats.remove(category)
        self.change("events", "visible_categories", cats)

    def startup(self, b, _):
        if self.building:
            return
        try:
            autostart.set_enabled(b.get_active())
        except (ValueError, OSError):
            self.building = True
            b.set_active(autostart.enabled())
            self.building = False
            b.set_tooltip_text(self.app.loc.t("startup_help"))


class Settings(SettingsContent, Gtk.ApplicationWindow):
    """Standalone adapter retained for native component checks."""
    embedded = False

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title="Roozlet")
        monitor = self.get_display().get_primary_monitor() or self.get_display().get_monitor(0)
        area = monitor.get_workarea()
        self.set_default_size(min(760, area.width - 48), min(680, area.height - 120))
        self.set_size_request(360, 300)
        self.build(app)


class SettingsPane(SettingsContent, Gtk.Box):
    """Preferences in the calendar shell: no separate native window."""
    embedded = True

    def __init__(self, app):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.build(app)
