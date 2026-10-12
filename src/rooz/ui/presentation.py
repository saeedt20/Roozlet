"""Shared scenic surfaces with native readable controls above the artwork."""

from gi.repository import Gtk

from ..calendar_service import jalali
from ..i18n import GMONTHS, HMONTHS, JMONTHS
from ..seasons import effective_season
from .artwork import ScenicBand, image
from .common import clear, direction, label


class ScenicSurface(Gtk.Overlay):
    def __init__(self, app, height=144):
        super().__init__()
        self.app = app
        self.get_style_context().add_class("hero")
        self.scene = ScenicBand(None, height, cfg=app.cfg, shade=True)
        self.add(self.scene)
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content.set_border_width(16)
        self.add_overlay(self.content)

    def sync(self, viewed_month=None):
        cfg = self.app.cfg
        a = cfg["appearance"]
        visible = a["style"] == "seasonal" and a["show_artwork"] and a["artwork_intensity"] > 0
        season = effective_season(cfg, self.app.today, viewed_month)
        visible = visible and image(season, 16, 16) is not None
        context = self.get_style_context()
        context.add_class("scenic") if visible else context.remove_class("scenic")
        self.scene.transition.cfg = cfg
        self.scene.update(season if visible else None,
                          a["artwork_intensity"])


class DatePreview(ScenicSurface):
    """Live civil dates and fixed physical columns, without creating a desktop window."""
    def __init__(self, app):
        super().__init__(app, 160)
        self.content.set_border_width(12)
        self.get_accessible().set_name(app.loc.t("widget_preview"))
        self.sync()

    def sync(self, viewed_month=None):
        super().sync()
        self.scene.set_size_request(-1, round(160 * max(1, self.app.cfg["appearance"]["text_scale"])))
        loc, cfg, day = self.app.loc, self.app.cfg, self.app.today
        key = (day, loc.lang, cfg["digits"], cfg["calendar"]["show_gregorian_column"],
               cfg["calendar"]["show_hijri_column"], self.app.repo.hijri(day))
        if key == getattr(self, "_date_key", None):
            return
        self._date_key = key
        clear(self.content)
        self.content.pack_start(label("روزلت" if loc.lang == "fa" else "Roozlet", align=.5), False, False, 0)
        grid = Gtk.Grid()
        grid.set_direction(Gtk.TextDirection.LTR)
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(8)
        grid.set_halign(Gtk.Align.FILL)
        grid.set_hexpand(True)
        self.content.pack_start(grid, True, True, 0)
        j = jalali(day)
        hijri = self.app.repo.hijri(day)
        values = [(day.day, GMONTHS[loc.lang][day.month-1], day.year),
                  (j.day, JMONTHS[loc.lang][j.month-1], j.year),
                  (None, loc.t("hijri_unavailable"), None)]
        if hijri:
            year, month, number = map(int, hijri.split("-"))
            values[2] = (number, HMONTHS[loc.lang][month-1], year)
        for column, (number, month, year) in enumerate(values):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            box.get_style_context().add_class("preview-primary" if column == 1 else "preview-date")
            if column == 1 or cfg["calendar"]["show_gregorian_column" if column == 0 else "show_hijri_column"]:
                box.pack_start(label(loc.n(number) if number is not None else "—", "preview-number", .5), False, False, 0)
                box.pack_start(label(month, align=.5, wrap=True), False, False, 0)
                box.pack_start(label(loc.n(year) if year else "—", "muted", .5), False, False, 0)
            else:
                box.get_style_context().remove_class("preview-date")
            direction(box, loc.lang == "fa")
            grid.attach(box, column, 0, 1, 1)
        self.show_all()
