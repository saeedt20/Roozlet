"""Small vector seasonal marks, drawn consistently at any logical scale."""

import math


def seasonal(cr, season, x, y, size, color):
    from .theme import rgb

    cr.save()
    cr.translate(x + size / 2, y + size / 2)
    cr.set_source_rgb(*rgb(color))
    cr.set_line_width(max(1, size / 12))
    cr.set_line_cap(1)
    r = size * 0.32
    if season == "winter":
        for i in range(6):
            cr.save()
            cr.rotate(i * math.pi / 3)
            cr.move_to(0, 0)
            cr.line_to(0, -r)
            for t in (0.55, 0.8):
                cr.move_to(-r * .22, -r * (t - .15))
                cr.line_to(0, -r * t)
                cr.line_to(r * .22, -r * (t - .15))
            cr.stroke()
            cr.restore()
    elif season == "summer":
        cr.arc(0, 0, r * .55, 0, math.tau)
        cr.stroke()
        for i in range(8):
            a = i * math.pi / 4
            cr.move_to(math.cos(a) * r * .83, math.sin(a) * r * .83)
            cr.line_to(math.cos(a) * r * 1.17, math.sin(a) * r * 1.17)
        cr.stroke()
    elif season == "spring":
        for i in range(5):
            a = i * math.tau / 5
            cr.arc(math.sin(a) * r * .65, -math.cos(a) * r * .65, r * .43, 0, math.tau)
            cr.fill()
        cr.arc(0, 0, r * .2, 0, math.tau)
        cr.stroke()
    else:
        cr.move_to(-r * .75, r * .8)
        cr.curve_to(-r * 1.3, -r * .4, r * .1, -r * .6, r * .9, -r)
        cr.curve_to(r * 1.2, r * .25, r * .4, r, -r * .75, r * .8)
        cr.stroke()
        cr.move_to(-r, r * 1.05)
        cr.line_to(r * .45, -r * .5)
        cr.stroke()
    cr.restore()


class Mark:
    def __new__(cls, season, color, size=22):
        from gi.repository import Gtk
        area = Gtk.DrawingArea()
        area.set_size_request(size, size)
        def draw(widget, cr):
            a = widget.get_allocation()
            seasonal(cr, season, (a.width-size)/2, (a.height-size)/2, size, color)
            return False
        area.connect("draw", draw)
        return area
