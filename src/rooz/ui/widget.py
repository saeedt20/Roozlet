"""Compact Cairo/Pango date card with native gear and managed Xfce hints."""

import math

import cairo
from gi.repository import Gdk, GLib, Gtk, Pango, PangoCairo

from ..calendar_service import jalali
from ..fonts import family
from ..formatting import full_date
from ..i18n import GMONTHS, HMONTHS, JMONTHS, WEEKDAYS
from ..position import place
from .theme import rgb, tokens


class Card(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Rooz · Widget")
        self.app = app
        self.drag_origin = None
        self.dragged = False
        self.position_timer = 0
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.get_style_context().add_class("rooz-card")
        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self.canvas = Gtk.DrawingArea()
        self.fixed.put(self.canvas, 0, 0)
        self.canvas.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.canvas.connect("draw", self.draw)
        self.canvas.connect("button-press-event", self.press)
        self.canvas.connect("motion-notify-event", self.motion)
        self.canvas.connect("button-release-event", self.release)
        self.canvas.set_has_tooltip(True)
        self.canvas.connect("query-tooltip", self.tooltip)
        self.gear = Gtk.Button()
        self.gear.set_image(Gtk.Image.new_from_icon_name("emblem-system-symbolic", Gtk.IconSize.MENU))
        self.gear.connect("clicked", lambda *_: self.app.open_settings())
        self.fixed.put(self.gear, 278, 10)
        self.connect("delete-event", lambda *_: self.app.quit() or True)
        self.connect("destroy", self.cleanup)
        for name in ("monitors-changed", "size-changed"):
            self.get_screen().connect(name, lambda *_: self.apply())
        self.get_screen().connect("composited-changed", lambda *_: self.queue_draw())
        self.apply()
        self.show_all()
        GLib.idle_add(self.reposition)

    @property
    def cfg(self):
        return self.app.cfg

    def layout_scale(self):
        a = self.cfg["appearance"]
        s = a["widget_scale"]
        monitor = self.monitor()
        if monitor:
            area = monitor.get_workarea()
            s = min(
                s,
                max(0.4, (area.width - 48) / 320),
                max(0.4, (area.height - 48) / (208 * max(1, a["text_scale"]))),
            )
        return s

    def dimensions(self):
        a = self.cfg["appearance"]
        s = self.layout_scale()
        ts = max(1, a["text_scale"])
        return round(320 * s), round(208 * s * ts)

    def apply(self):
        w, h = self.dimensions()
        self.canvas.set_size_request(w, h)
        self.fixed.set_size_request(w, h)
        self.resize(w, h)
        s = self.layout_scale()
        gear_x = round(10 * s) if self.app.loc.lang == "fa" else w - round(40 * s)
        self.fixed.move(self.gear, gear_x, round(10 * s))
        self.gear.set_tooltip_text(self.app.loc.t("settings"))
        self.gear.get_accessible().set_name(self.app.loc.t("settings"))
        fg = Gdk.RGBA()
        fg.parse(tokens(self.cfg)["muted"])
        self.gear.override_color(Gtk.StateFlags.NORMAL, fg)
        win = self.cfg["window"]
        above = win["always_on_top"]
        self.set_keep_above(False)
        self.set_keep_below(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL if above else Gdk.WindowTypeHint.DESKTOP)
        self.set_keep_above(above)
        self.set_keep_below(not above)
        self.stick() if win["all_workspaces"] else self.unstick()
        self.canvas.get_accessible().set_name(full_date(self.app.today, self.app.loc, self.app.repo))
        self.reposition()
        self.queue_draw()

    def monitor_key(self, monitor):
        display = self.get_display()
        for i in range(display.get_n_monitors()):
            if display.get_monitor(i) == monitor:
                return self.get_screen().get_monitor_plug_name(i) or f"monitor-{i}"
        return "primary"

    def monitor(self):
        display = self.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        for i in range(display.get_n_monitors()):
            candidate = display.get_monitor(i)
            if self.monitor_key(candidate) == self.cfg["window"]["monitor"]:
                monitor = candidate
                break
        return monitor

    def reposition(self):
        monitor = self.monitor()
        if monitor:
            a = monitor.get_workarea()
            self.move(
                *place((a.x, a.y, a.width, a.height), self.dimensions(), self.cfg["window"]["position"], 24)
            )
        return False

    def save_position(self):
        self.position_timer = 0
        self.cfg["window"]["position"] = list(self.get_position())
        self.cfg["window"]["monitor"] = self.monitor_key(
            self.get_display().get_monitor_at_window(self.get_window())
        )
        self.reposition()
        self.app.save()
        return False

    def press(self, _, e):
        if e.button == 3:
            self.menu(e)
            return True
        if e.button == 1 and e.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.cancel_drag()
            self.app.open_calendar()
            return True
        if e.button == 1 and e.y < 40 * self.layout_scale() and not self.cfg["window"]["locked"]:
            self.drag_origin = (e.x_root, e.y_root, *self.get_position())
            self.dragged = False
            self.canvas.grab_add()
            return True
        return False

    def motion(self, _, e):
        if self.drag_origin:
            rx, ry, x, y = self.drag_origin
            dx, dy = e.x_root - rx, e.y_root - ry
            if math.hypot(dx, dy) >= 6:
                self.dragged = True
            if self.dragged:
                self.move(round(x + dx), round(y + dy))
            return True
        return False

    def cancel_drag(self):
        if self.drag_origin:
            self.canvas.grab_remove()
        self.drag_origin = None

    def release(self, _, e):
        if e.button == 1 and self.drag_origin:
            moved = self.dragged
            self.cancel_drag()
            if moved:
                if self.position_timer:
                    GLib.source_remove(self.position_timer)
                self.position_timer = GLib.timeout_add(150, self.save_position)
            return True
        return False

    def cleanup(self, *_):
        if self.position_timer:
            GLib.source_remove(self.position_timer)
            self.position_timer = 0

    def menu(self, e=None):
        loc = self.app.loc
        m = Gtk.Menu()
        m.get_style_context().add_class("rooz")
        m.set_direction(Gtk.TextDirection.RTL if loc.lang == "fa" else Gtk.TextDirection.LTR)
        for key, fn in [
            ("open", self.app.open_calendar),
            ("settings", self.app.open_settings),
            ("copy_persian", lambda: self.app.copy(self.app.today, 0)),
            ("copy_gregorian", lambda: self.app.copy(self.app.today, 1)),
            ("copy_all", lambda: self.app.copy(self.app.today, None)),
        ]:
            item = Gtk.MenuItem(label=loc.t(key))
            item.connect("activate", lambda _, f=fn: f())
            m.append(item)
        numeric = Gtk.MenuItem(label=loc.t("copy_numeric"))
        submenu = Gtk.Menu()
        submenu.set_direction(m.get_direction())
        for key, index in [
            ("copy_persian", 0),
            ("copy_gregorian", 1),
            ("copy_hijri", 2),
            ("copy_all", None),
        ]:
            item = Gtk.MenuItem(label=loc.t(key))
            if index == 2:
                item.set_sensitive(bool(self.app.repo.hijri(self.app.today)))
            item.connect("activate", lambda _, i=index: self.app.copy(self.app.today, i, numerical=True))
            submenu.append(item)
        numeric.set_submenu(submenu)
        m.append(numeric)
        for key, setting in [("lock", "locked"), ("above", "always_on_top")]:
            item = Gtk.CheckMenuItem(label=loc.t(key))
            item.set_active(self.cfg["window"][setting])
            item.connect("toggled", lambda b, k=setting: self.app.change("window", k, b.get_active()))
            m.append(item)
        for key, fn in [("reset_position", self.app.reset_position), ("quit", self.app.quit)]:
            item = Gtk.MenuItem(label=loc.t(key))
            item.connect("activate", lambda _, f=fn: f())
            m.append(item)
        m.show_all()
        m.popup_at_pointer(e)
        return m

    def tooltip(self, _, x, y, keyboard, tip):
        tip.set_text(
            full_date(self.app.today, self.app.loc, self.app.repo)
            + "\n"
            + self.cfg["timezone"]
            + "\n"
            + "\n".join(self.app.loc.event_title(e) for e in self.app.repo.events(self.app.today))
        )
        return True

    def draw(self, area, cr):
        w, h = self.dimensions()
        s = self.layout_scale()
        t = tokens(self.cfg)
        loc = self.app.loc
        a = self.cfg["appearance"]
        ts = a["text_scale"]
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0) if self.get_screen().is_composited() else cr.set_source_rgb(
            *rgb(t["bg"])
        )
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        opacity = a["background_opacity"] if self.get_screen().is_composited() else 1.0
        radius = 17 * s
        cr.new_sub_path()
        for cx, cy, start in [
            (w - radius, radius, -math.pi / 2),
            (w - radius, h - radius, 0),
            (radius, h - radius, math.pi / 2),
            (radius, radius, math.pi),
        ]:
            cr.arc(cx, cy, radius, start, start + math.pi / 2)
        cr.close_path()
        cr.set_source_rgba(*rgb(t["bg"]), opacity)
        cr.fill_preserve()
        cr.set_source_rgba(*rgb(t["line"]), 0.8)
        cr.set_line_width(1)
        cr.stroke()
        cr.scale(s, s)
        hh = h / s

        def text(value, x, y, width, size=11, color="fg", weight=400, align=Pango.Alignment.CENTER):
            layout = PangoCairo.create_layout(cr)
            desc = Pango.FontDescription()
            desc.set_family(family(self.cfg))
            desc.set_absolute_size(size * ts * Pango.SCALE)
            desc.set_weight(weight)
            layout.set_font_description(desc)
            # Edge alignment must not be flipped again by Pango's auto RTL handling.
            if align != Pango.Alignment.CENTER:
                layout.set_auto_dir(False)
                layout.get_context().set_base_dir(Pango.Direction.LTR)
            layout.set_text(str(value), -1)
            layout.set_width(round(width * Pango.SCALE))
            layout.set_ellipsize(Pango.EllipsizeMode.END)
            layout.set_alignment(align)
            cr.set_source_rgb(*rgb(t[color]))
            cr.move_to(x, y)
            PangoCairo.show_layout(cr, layout)

        rtl = loc.lang == "fa"
        text(
            "روز" if rtl else "Rooz", 54 if rtl else 16, 11, w / s - 70,
            12, "accent_text", 600, Pango.Alignment.RIGHT if rtl else Pango.Alignment.LEFT,
        )
        text(WEEKDAYS[loc.lang][self.app.today.weekday()], 16, 38 * max(1, ts), 288, 11, "muted")
        day = self.app.today
        j = jalali(day)
        hijri = self.app.repo.hijri(day)
        columns = []
        if self.cfg["calendar"]["show_hijri_column"]:
            if hijri:
                hy, hm, hd = map(int, hijri.split("-"))
                columns.append((loc.n(hd), HMONTHS[loc.lang][hm - 1], loc.n(hy), False))
            else:
                columns.append(("—", loc.t("hijri_unavailable"), "—", False))
        columns.extend(
            [
                (loc.n(day.day), GMONTHS[loc.lang][day.month - 1], loc.n(day.year), False),
                (loc.n(j.day), JMONTHS[loc.lang][j.month - 1], loc.n(j.year), True),
            ]
        )
        cw = 288 / len(columns)
        yy = 57 * max(1, ts)
        for i, (num, month, year, primary) in enumerate(columns):
            x = 16 + i * cw
            text(num, x, yy, cw, 30 if primary else 23, "accent_text" if primary else "fg", 600)
            text(month, x, yy + 39 * ts, cw, 10.5, "fg", 500)
            text(year, x, yy + 57 * ts, cw, 10, "muted")
        sep = hh - 67
        cr.set_source_rgb(*rgb(t["line"]))
        cr.set_line_width(1)
        cr.move_to(16, sep)
        cr.line_to(304, sep)
        cr.stroke()
        visible = self.app.repo.visible(day, self.cfg["events"])
        events = self.app.repo.events(day)
        if visible:
            value = loc.n(visible[0]["title"].get(loc.lang) or visible[0]["title"]["fa"])
            if len(visible) > 1:
                value += " · " + loc.more(len(visible) - 1)
            if visible[0]["is_public_holiday"]:
                value = "◆ " + value
        else:
            value = (
                loc.t("none" if self.app.repo.known(day) else "incomplete")
                if not events
                else loc.t("filtered")
            )
        if self.app.repo.errors and not self.app.repo.known(day):
            value = loc.t("unavailable")
        text(value, 16, sep + 9, 288, 10.5, "holiday" if self.app.repo.holiday(day) else "fg")
        if self.cfg["calendar"]["show_next_public_holiday"]:
            nxt = self.app.repo.next_holiday(day)
            caption = loc.remaining(nxt[1]) if nxt else loc.t("no_next")
            text(caption, 16, sep + 32 * ts, 288, 9.5, "muted")
        return False
