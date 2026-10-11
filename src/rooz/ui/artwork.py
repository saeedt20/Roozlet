"""Offline, bounded scenic image loading shared by the card and native panels."""

from functools import lru_cache

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
    def __init__(self, season, height=100, intensity=0.65):
        super().__init__()
        self.season, self.intensity = season, intensity
        self.set_size_request(-1, height)
        self.connect("draw", self.draw)

    def draw(self, _, cr):
        allocation = self.get_allocation()
        paint(cr, self.season, allocation.width, allocation.height, self.intensity)
        return False
