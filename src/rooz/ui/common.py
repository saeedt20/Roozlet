from gi.repository import Gtk, Pango


def label(text="", style=None, align=0, wrap=False):
    widget = Gtk.Label(label=text)
    widget.set_xalign(align)
    if style:
        widget.get_style_context().add_class(style)
    if wrap:
        widget.set_line_wrap(True)
        widget.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        widget.set_max_width_chars(60)
    return widget


def button(text, callback, tip=None):
    b = Gtk.Button(label=text)
    b.connect("clicked", lambda *_: callback())
    if tip:
        b.set_tooltip_text(tip)
        b.get_accessible().set_name(tip)
    return b


def clear(container):
    for child in container.get_children():
        container.remove(child)


def direction(widget, rtl):
    # GTK widget direction is not reliably inherited by newly-created children.
    # The calendar grid has an explicit physical coordinate system in both locales.
    if isinstance(widget, Gtk.Grid):
        return
    widget.set_direction(Gtk.TextDirection.RTL if rtl else Gtk.TextDirection.LTR)
    if isinstance(widget, Gtk.Container):
        for child in widget.get_children():
            direction(child, rtl)
