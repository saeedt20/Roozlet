"""Offline, bounded scenic image loading shared by the card and native panels."""

from functools import lru_cache
import math
import cairo

from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

from ..resources import DATA
from ..seasons import SEASONS


@lru_cache(maxsize=8)
def image(season, width, height):
    if season not in SEASONS:
        return None
    try:
        # Decode near the requested size rather than retaining full-resolution scenes.
        source = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            str(DATA / "themes/seasons" / season / "landscape.png"),
            max(width, round(height * 1.5)), max(height, round(width / 1.5)), True,
        )
        ratio = max(width / source.get_width(), height / source.get_height())
        scaled = source.scale_simple(
            max(width, round(source.get_width() * ratio)),
            max(height, round(source.get_height() * ratio)), GdkPixbuf.InterpType.BILINEAR,
        )
        return scaled.new_subpixbuf(
            (scaled.get_width() - width) // 2, (scaled.get_height() - height) // 2, width, height,
        )
    except (GLib.Error, OSError, ValueError):
        # Invalid/missing optional artwork must not prevent calendar operation.
        return None


def paint(cr, season, width, height, alpha=1.0):
    if width <= 0 or height <= 0 or alpha <= 0:
        return
    # Quantization bounds resize cache churn without blurring text, which is separate.
    pixbuf = image(season, max(16, ((int(width) + 15) // 16) * 16),
                   max(16, ((int(height) + 15) // 16) * 16))
    if pixbuf:
        cr.save()
        cr.rectangle(0, 0, width, height)
        cr.clip()
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
        cr.paint_with_alpha(alpha)
        cr.restore()


class ScenicBand(Gtk.DrawingArea):
    def __init__(self, season, height=100, intensity=0.65, cfg=None, shade=False):
        super().__init__()
        self.season, self.intensity = season, intensity
        self.shade = shade
        self.resolve = None
        self.transition = None
        if cfg:
            from .motion import ArtworkTransition
            self.transition = ArtworkTransition(self, cfg)
            self.transition.set_scene(season)
        self.set_size_request(-1, height)
        self.connect("draw", self.draw)

    def update(self, season, intensity):
        self.season, self.intensity = season, intensity
        if self.transition:
            self.transition.set_scene(season)
        self.queue_draw()

    def draw(self, _, cr):
        if self.resolve:
            season, intensity = self.resolve()
            if (season, intensity) != (self.season, self.intensity):
                self.update(season, intensity)
        allocation = self.get_allocation()
        width, height = allocation.width, allocation.height
        cr.save()
        radius = min(12, width / 2, height / 2)
        for x, y, start in ((width-radius, radius, -math.pi/2),
                            (width-radius, height-radius, 0),
                            (radius, height-radius, math.pi/2), (radius, radius, math.pi)):
            cr.arc(x, y, radius, start, start + math.pi/2)
        cr.close_path()
        cr.clip()
        if self.transition:
            self.transition.paint(cr, width, height, self.intensity)
        elif self.season:
            paint(cr, self.season, width, height, self.intensity)
        if self.shade and self.season:
            gradient = cairo.LinearGradient(0, 0, 0, height)
            gradient.add_color_stop_rgba(0, .04, .07, .11, .20)
            gradient.add_color_stop_rgba(1, .04, .07, .11, .86)
            cr.set_source(gradient)
            cr.paint()
        cr.restore()
        return False
