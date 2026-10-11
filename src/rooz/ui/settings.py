from gi.repository import Gdk, Gtk

from .. import autostart
from .common import button, clear, direction, label


class Settings(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Rooz")
        self.app = app
        self.building = False
        monitor = self.get_display().get_primary_monitor() or self.get_display().get_monitor(0)
        area = monitor.get_workarea()
        self.set_default_size(min(490, area.width - 48), min(500, area.height - 64))
        self.set_size_request(360, 300)
        self.get_style_context().add_class("rooz")
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.root.set_border_width(16)
        self.add(self.root)
        self.connect("delete-event", lambda *_: self.hide() or True)
        self.connect(
            "key-press-event", lambda _, e: (self.hide() or True) if e.keyval == Gdk.KEY_Escape else False
        )
        self.apply()
        self.show_all()

    def change(self, section, key, value):
        if not self.building:
            self.app.change(section, key, value)

    def apply(self):
        was_visible = self.get_visible()
        loc = self.app.loc
        cfg = self.app.cfg
        old_page = getattr(self, "notebook", None)
        old_page = old_page.get_current_page() if old_page else 0
        self.building = True
        self.set_title(("روز" if loc.lang == "fa" else "Rooz") + " · " + loc.t("settings"))
        self.set_direction(Gtk.TextDirection.RTL if loc.lang == "fa" else Gtk.TextDirection.LTR)
        clear(self.root)
        self.root.pack_start(label(loc.t("settings"), "heading"), False, False, 0)
        self.notebook = Gtk.Notebook()
        self.root.pack_start(self.notebook, True, True, 0)
        pages = {}
        for key in ("appearance", "dates", "events", "desktop"):
            scroll = Gtk.ScrolledWindow()
            scroll.set_overlay_scrolling(False)
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
            box.set_border_width(12)
            scroll.add(box)
            pages[key] = box
            self.notebook.append_page(scroll, label(loc.t(key)))

        def row(page, key, control):
            box = Gtk.Box(spacing=12)
            box.pack_start(label(loc.t(key)), True, True, 0)
            box.pack_end(control, False, False, 0)
            pages[page].pack_start(box, False, False, 0)

        def combo(page, key, section, field, options):
            c = Gtk.ComboBoxText()
            for value, text in options:
                c.append(value, text)
            v = cfg[section][field] if section else cfg[field]
            c.set_active_id(v)
            c.connect("changed", lambda b: self.change(section, field, b.get_active_id()))
            row(page, key, c)

        def spin(page, key, section, field, lo, hi, step):
            b = Gtk.SpinButton.new_with_range(lo, hi, step)
            b.set_digits(2)
            b.set_value(cfg[section][field])
            b.set_numeric(True)
            b.connect("value-changed", lambda b: self.change(section, field, b.get_value()))
            row(page, key, b)

        def toggle(page, key, section, field):
            b = Gtk.Switch()
            b.set_active(cfg[section][field])
            b.connect("notify::active", lambda b, _: self.change(section, field, b.get_active()))
            row(page, key, b)

        combo("appearance", "theme", "appearance", "theme", [(v, loc.t(v)) for v in ("dark", "light")])
        color = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(cfg["appearance"]["accent_color"])
        color.set_rgba(rgba)
        color.connect(
            "color-set",
            lambda b: self.change(
                "appearance",
                "accent_color",
                "#"
                + "".join(
                    f"{round(v * 255):02X}" for v in (b.get_rgba().red, b.get_rgba().green, b.get_rgba().blue)
                ),
            ),
        )
        row("appearance", "accent", color)
        spin("appearance", "opacity", "appearance", "background_opacity", 0.5, 1.0, 0.05)
        spin("appearance", "scale", "appearance", "widget_scale", 0.8, 1.6, 0.1)
        combo(
            "appearance",
            "font",
            "appearance",
            "font_mode",
            [("vazirmatn", "Vazirmatn"), ("system", loc.t("system")), ("custom", loc.t("custom"))],
        )
        font = Gtk.FontButton()
        font.set_use_font(True)
        font.set_show_size(False)
        font.set_font_name(cfg["appearance"]["custom_font_family"])

        def choose_font(b):
            if self.building:
                return
            self.app.cfg["appearance"]["font_mode"] = "custom"
            self.change("appearance", "custom_font_family", b.get_font_desc().get_family())

        font.connect("font-set", choose_font)
        row("appearance", "custom", font)
        spin("appearance", "text_size", "appearance", "text_scale", 0.85, 1.4, 0.05)
        pages["appearance"].pack_start(
            label("روزهای روشن؛ زندگی زیباست.\nRooz · 0123456789 · ۰۱۲۳۴۵۶۷۸۹", wrap=True), False, False, 0
        )
        from ..fonts import family

        chosen = (
            "Vazirmatn"
            if cfg["appearance"]["font_mode"] == "vazirmatn"
            else cfg["appearance"]["custom_font_family"]
        )
        if (
            cfg["appearance"]["font_mode"] != "system"
            and family(cfg) == "Sans"
            and chosen.casefold() != "sans"
        ):
            pages["appearance"].pack_start(
                label(loc.t("font_fallback"), "holiday", wrap=True), False, False, 0
            )
        if self.app.font_warnings:
            pages["appearance"].pack_start(
                label(loc.t("font_load_error"), "holiday", wrap=True), False, False, 0
            )
        pages["appearance"].pack_start(label(loc.t("font_help"), "muted", wrap=True), False, False, 0)
        pages["appearance"].pack_start(
            button(loc.t("reset_appearance"), self.app.reset_appearance), False, False, 0
        )
        combo("dates", "language", None, "language", [("fa", "فارسی"), ("en", "English")])
        combo("dates", "digits", None, "digits", [("persian", loc.t("persian")), ("latin", loc.t("latin"))])
        combo(
            "dates",
            "timezone",
            None,
            "timezone",
            [("Asia/Tehran", loc.t("tehran")), ("system", loc.t("system"))],
        )
        pages["dates"].pack_start(label(loc.t("zone_help"), "muted", wrap=True), False, False, 0)
        toggle("dates", "numerical_dates", "calendar", "prefer_numerical_dates")
        pages["dates"].pack_start(label(loc.t("numerical_help"), "muted", wrap=True), False, False, 0)
        toggle("dates", "gregorian_cells", "calendar", "show_gregorian_cell_numbers")
        toggle("dates", "hijri_column", "calendar", "show_hijri_column")
        for category in ("national", "cultural", "religious", "international"):
            b = Gtk.CheckButton(label=loc.t(category))
            b.set_active(category in cfg["events"]["visible_categories"])
            b.connect("toggled", lambda b, c=category: self.filter(b, c))
            pages["events"].pack_start(b, False, False, 0)
        toggle("events", "show_holidays", "events", "show_public_holidays")
        toggle("events", "countdown", "calendar", "show_next_public_holiday")
        pages["events"].pack_start(
            label(loc.t("coverage") if self.app.repo.reports else loc.t("unavailable"), "muted", wrap=True),
            False,
            False,
            0,
        )
        if self.app.repo.errors:
            pages["events"].pack_start(label(loc.t("source_error"), "holiday", wrap=True), False, False, 0)
        startup = Gtk.Switch()
        startup.set_active(autostart.enabled())
        startup.set_sensitive(__import__("pathlib").Path("/usr/bin/rooz").is_file())
        if not startup.get_sensitive():
            startup.set_tooltip_text(loc.t("startup_help"))
            pages["desktop"].pack_start(label(loc.t("startup_help"), "muted", wrap=True), False, False, 0)
        startup.connect("notify::active", self.startup)
        row("desktop", "startup", startup)
        for key, field in [
            ("lock", "locked"),
            ("above", "always_on_top"),
            ("all_workspaces", "all_workspaces"),
        ]:
            toggle("desktop", key, "window", field)
        pages["desktop"].pack_start(button(loc.t("reset_position"), self.app.reset_position), False, False, 0)
        if self.app.config.warning:
            pages["desktop"].pack_start(label(loc.t("recovered"), "holiday", wrap=True), False, False, 0)
        self.root.pack_start(button(loc.t("close"), self.hide), False, False, 0)
        direction(self.root, loc.lang == "fa")
        self.show_all()
        self.notebook.set_current_page(max(0, old_page))
        self.building = False
        if not was_visible:
            self.hide()

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
