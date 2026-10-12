"""Compact Cairo/Pango date card with native gear and managed Xfce hints."""

import math

import cairo
from gi.repository import Gdk, GLib, Gtk, Pango, PangoCairo

from ..calendar_service import jalali
from ..fonts import family
from ..formatting import full_date
from ..i18n import GMONTHS, HMONTHS, JMONTHS, WEEKDAYS
from ..position import place
from .theme import rgb, tokens, style_window
from .icons import seasonal


class Card(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Roozlet · Widget")
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
        from .motion import ArtworkTransition
        self.artwork_transition = ArtworkTransition(self.canvas, app.cfg)
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
        self.occasion = Gtk.Button()
        self.occasion.get_style_context().add_class("occasion")
        self.occasion.connect("clicked", lambda *_: self.show_today())
        self.fixed.put(self.occasion, 16, 194)
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
                max(0.4, (area.height - 48) / (236 * max(1, a["text_scale"]))),
            )
        return s

    def dimensions(self):
        a = self.cfg["appearance"]
        s = self.layout_scale()
        ts = max(1, a["text_scale"])
        return round(320 * s), round(236 * s * ts)

    def date_slots(self):
        # Physical geometry never mirrors with UI language or hidden satellites.
        return {"gregorian": (14, 88), "shamsi": (110, 100), "hijri": (218, 88)}

    def summary(self):
        repo, loc, day = self.app.repo, self.app.loc, self.app.today
        events = repo.events(day)
        visible = sorted(repo.visible(day, self.cfg["events"]), key=lambda e: not e["is_public_holiday"])
        if visible:
            value = loc.event_title(visible[0])
            if visible[0]["is_public_holiday"]:
                value = "◆ " + value
            if len(visible) > 1:
                value += " · " + loc.more(len(visible) - 1)
            return value
        if repo.errors and not repo.known(day):
            return loc.t("unavailable")
        return loc.t("filtered" if events else "none" if repo.known(day) else "incomplete")

    def show_today(self):
        self.app.open_calendar()
        calendar = getattr(self.app, "calendar", None)
        if calendar:
            calendar.go_today()

    def apply(self):
        style_window(self, self.cfg, self.app.today)
        t = tokens(self.cfg, self.app.today)
        self.artwork_transition.cfg = self.cfg
        self.artwork_transition.set_scene(t["season"] if t["seasonal"] and self.cfg["appearance"]["show_artwork"] else None)
        self.set_title("روزلت · ویجت" if self.app.loc.lang == "fa" else "Roozlet · Widget")
        w, h = self.dimensions()
        self.canvas.set_size_request(w, h)
        self.fixed.set_size_request(w, h)
        self.resize(w, h)
        s = self.layout_scale()
        gear_x = round(10 * s) if self.app.loc.lang == "fa" else w - round(40 * s)
        self.fixed.move(self.gear, gear_x, round(10 * s))
        ts = max(1, self.cfg["appearance"]["text_scale"])
        self.fixed.move(self.occasion, round(16*s), round(193*s*ts))
        self.occasion.set_size_request(round(288*s), round(23*s*ts))
        self.occasion.set_label(self.summary())
        content = self.occasion.get_child()
        content.set_ellipsize(Pango.EllipsizeMode.END)
        content.set_max_width_chars(42)
        self.occasion.set_tooltip_text("\n".join(self.app.loc.event_title(e) for e in
                                      self.app.repo.visible(self.app.today, self.cfg["events"])) or self.summary())
        self.occasion.get_accessible().set_name(self.summary() + " · " + self.app.loc.t("open"))
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
        self.artwork_transition.stop()
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
            ("search", self.app.open_search),
            ("personal", self.app.open_personal),
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
        t = tokens(self.cfg, self.app.today)
        loc, a = self.app.loc, self.cfg["appearance"]
        ts = a["text_scale"]
        ys = max(1, ts)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        if self.get_screen().is_composited():
            cr.set_source_rgba(0, 0, 0, 0)
        else:
            cr.set_source_rgb(*rgb(t["bg"]))
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        def rounded(x, y, width, height, radius):
            cr.new_sub_path()
            for cx, cy, start in [(x+width-radius,y+radius,-math.pi/2),
                                   (x+width-radius,y+height-radius,0),
                                   (x+radius,y+height-radius,math.pi/2),
                                   (x+radius,y+radius,math.pi)]:
                cr.arc(cx, cy, radius, start, start+math.pi/2)
            cr.close_path()

        rounded(0, 0, w, h, 18*s)
        cr.save()
        cr.clip()
        opacity = a["background_opacity"] if self.get_screen().is_composited() else 1.0
        cr.set_source_rgba(*rgb(t["bg"]), opacity)
        cr.paint()
        if t["seasonal"] and a["show_artwork"]:
            self.artwork_transition.paint(cr, w, h, a["artwork_intensity"]*.58)
            shade = cairo.LinearGradient(0, 0, 0, h)
            shade.add_color_stop_rgba(0, *rgb(t["bg"]), .15)
            shade.add_color_stop_rgba(.32, *rgb(t["bg"]), .75)
            shade.add_color_stop_rgba(1, *rgb(t["bg"]), .96)
            cr.set_source(shade)
            cr.paint()
        cr.restore()
        rounded(.5, .5, w-1, h-1, 18*s)
        cr.set_source_rgba(*rgb(t["muted"]), .35)
        cr.set_line_width(1)
        cr.stroke()
        cr.scale(s, s)

        def text(value, x, y, width, size=11, color="fg", weight=400, align=Pango.Alignment.CENTER):
            layout = PangoCairo.create_layout(cr)
            desc = Pango.FontDescription()
            desc.set_family(family(self.cfg))
            desc.set_absolute_size(size*ts*Pango.SCALE)
            desc.set_weight(weight)
            layout.set_font_description(desc)
            if align != Pango.Alignment.CENTER:
                layout.set_auto_dir(False)
                layout.get_context().set_base_dir(Pango.Direction.LTR)
            layout.set_text(str(value), -1)
            layout.set_width(round(width*Pango.SCALE))
            layout.set_ellipsize(Pango.EllipsizeMode.END)
            layout.set_alignment(align)
            cr.set_source_rgb(*rgb(t[color]))
            cr.move_to(x, y)
            PangoCairo.show_layout(cr, layout)

        rtl = loc.lang == "fa"
        text("روزلت" if rtl else "Roozlet", 54 if rtl else 40, 11, 228,
             12, "fg", 600, Pango.Alignment.RIGHT if rtl else Pango.Alignment.LEFT)
        seasonal(cr, "autumn", 286 if rtl else 14, 11, 18, t["accent_text"])
        text(WEEKDAYS[loc.lang][self.app.today.weekday()], 16, 39*ys, 288, 11, "muted")
        day = self.app.today
        j = jalali(day)
        columns = {"shamsi": (loc.n(j.day), JMONTHS[loc.lang][j.month-1], loc.n(j.year))}
        if self.cfg["calendar"]["show_gregorian_column"]:
            columns["gregorian"] = (loc.n(day.day), GMONTHS[loc.lang][day.month-1], loc.n(day.year))
        if self.cfg["calendar"]["show_hijri_column"]:
            hijri = self.app.repo.hijri(day)
            if hijri:
                hy, hm, hd = map(int, hijri.split("-"))
                columns["hijri"] = (loc.n(hd), HMONTHS[loc.lang][hm-1], loc.n(hy))
            else:
                columns["hijri"] = ("—", loc.t("unavailable"), "—")
        for key, (num, month, year) in columns.items():
            x, width = self.date_slots()[key]
            primary = key == "shamsi"
            y = (62 if primary else 75)*ys
            rounded(x, y, width, (120 if primary else 107)*ys, 12)
            cr.set_source_rgba(*rgb(t["accent"] if primary else t["muted"]), .16 if primary else .04)
            cr.fill_preserve()
            cr.set_source_rgba(*rgb(t["accent"] if primary else t["muted"]), .7 if primary else .16)
            cr.set_line_width(1)
            cr.stroke()
            if primary:
                seasonal(cr, t["season"], 150, 66*ys, 20, t["accent_text"])
            text(num, x+3, (90 if primary else 99)*ys, width-6,
                 34 if primary else 24, "accent_text" if primary else "fg", 600)
            text(month, x+3, 140*ys, width-6, 10.5, "fg", 500)
            text(year, x+3, 162*ys, width-6, 10, "muted")
        cr.set_source_rgba(*rgb(t["line"]), .85)
        cr.set_line_width(1)
        cr.move_to(16, 188*ys)
        cr.line_to(304, 188*ys)
        cr.stroke()
        if self.cfg["calendar"]["show_next_public_holiday"]:
            nxt = self.app.repo.next_holiday(day)
            text(loc.remaining(nxt[1]) if nxt else loc.t("no_next"),
                 16, 219*ys, 288, 9.5, "muted")
        return False
