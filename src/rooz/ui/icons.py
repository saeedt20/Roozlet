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


class NavigationIcon:
    """Consistent outlined native marks, independent of the desktop icon theme."""
    def __new__(cls, name, size=18):
        from gi.repository import Gtk
        area = Gtk.DrawingArea()
        area.set_size_request(size, size)
        def draw(widget, cr):
            allocation = widget.get_allocation()
            color = widget.get_style_context().get_color(widget.get_state_flags())
            cr.save()
            cr.translate((allocation.width-size)/2, (allocation.height-size)/2)
            cr.scale(size/18, size/18)
            cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
            cr.set_line_width(1.4)
            cr.set_line_cap(1)
            cr.set_line_join(1)
            if name == "calendar":
                cr.rectangle(3, 4, 12, 11)
                cr.move_to(3, 8); cr.line_to(15, 8)
                for x in (6, 12):
                    cr.move_to(x, 2); cr.line_to(x, 6)
                cr.stroke()
                for x in (6, 9, 12):
                    cr.arc(x, 11, .6, 0, math.tau); cr.fill()
            elif name == "today":
                cr.arc(9, 9, 6, 0, math.tau)
                cr.move_to(9, 5); cr.line_to(9, 9); cr.line_to(12, 10)
                cr.stroke()
            elif name == "occasions":
                for y in (5, 9, 13):
                    cr.move_to(7, y); cr.line_to(15, y); cr.stroke()
                    cr.arc(3.5, y, .6, 0, math.tau); cr.fill()
            elif name == "settings":
                for i in range(32):
                    angle = math.tau*i/32
                    radius = 6.5 if i%4 in (1, 2) else 4.9
                    x, y = 9+radius*math.cos(angle), 9+radius*math.sin(angle)
                    cr.move_to(x, y) if i == 0 else cr.line_to(x, y)
                cr.close_path(); cr.stroke()
                cr.arc(9, 9, 2.2, 0, math.tau); cr.stroke()
            elif name == "search":
                cr.arc(7.5, 7.5, 4.5, 0, math.tau)
                cr.move_to(11, 11); cr.line_to(15.5, 15.5); cr.stroke()
            elif name == "personal":
                cr.rectangle(3, 2, 12, 14)
                for y in (6, 9, 12):
                    cr.move_to(6, y); cr.line_to(12, y)
                cr.stroke()
            elif name == "about":
                cr.arc(9, 9, 6, 0, math.tau); cr.stroke()
                cr.move_to(9, 8); cr.line_to(9, 12); cr.stroke()
                cr.arc(9, 5.5, .6, 0, math.tau); cr.fill()
            elif name == "appearance":
                cr.move_to(9, 3); cr.curve_to(1, 2, 1, 14, 8, 15)
                cr.curve_to(12, 16, 8, 11, 12, 10); cr.curve_to(18, 9, 15, 3, 9, 3)
                cr.close_path(); cr.stroke()
                for x, y in ((5, 7), (9, 5), (12.5, 6.5)):
                    cr.arc(x, y, .6, 0, math.tau); cr.fill()
            elif name == "dates":
                cr.arc(9, 9, 6, 0, math.tau)
                cr.move_to(3, 9); cr.line_to(15, 9); cr.stroke()
                cr.save(); cr.translate(9, 9); cr.scale(.45, 1)
                cr.arc(0, 0, 6, 0, math.tau); cr.stroke(); cr.restore()
            elif name == "desktop":
                cr.rectangle(2, 3, 14, 10)
                cr.move_to(9, 13); cr.line_to(9, 16)
                cr.move_to(5, 16); cr.line_to(13, 16); cr.stroke()
            else:
                seasonal(cr, "autumn", 0, 0, 18, "#"+"".join(f"{round(v*255):02X}" for v in (color.red,color.green,color.blue)))
            cr.restore()
            return False
        area.connect("draw", draw)
        return area
