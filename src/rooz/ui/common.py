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
        child.destroy()


def direction(widget, rtl):
    # GTK widget direction is not reliably inherited by newly-created children.
    # The calendar grid has an explicit physical coordinate system in both locales.
    if isinstance(widget, Gtk.Grid):
        return
    widget.set_direction(Gtk.TextDirection.RTL if rtl else Gtk.TextDirection.LTR)
    if isinstance(widget, Gtk.Label) and widget.get_xalign() != 0.5:
        # GtkLabel mirrors xalign with widget direction: zero is logical start.
        widget.set_xalign(0.0)
    if isinstance(widget, Gtk.Container):
        for child in widget.get_children():
            direction(child, rtl)


def navigation_item(text, icon, callback, rtl=False):
    """Native navigation with a leading icon and a locale-aligned label."""
    item = Gtk.Button()
    item.get_style_context().add_class("nav-item")
    row = Gtk.Box(spacing=10)
    from .icons import NavigationIcon
    names = {"x-office-calendar-symbolic":"calendar", "go-jump-symbolic":"today",
             "view-list-symbolic":"occasions", "emblem-system-symbolic":"settings",
             "help-about-symbolic":"about", "preferences-desktop-theme-symbolic":"appearance",
             "preferences-desktop-locale-symbolic":"dates", "preferences-system-symbolic":"desktop",
             "edit-find-symbolic":"search", "accessories-text-editor-symbolic":"personal"}
    row.pack_start(NavigationIcon(names.get(icon, "about")), False, False, 0)
    title = label(text, align=1 if rtl else 0, wrap=True)
    title.set_max_width_chars(19)
    row.pack_start(title, True, True, 0)
    item.add(row)
    direction(row, rtl)
    item.get_accessible().set_name(text)
    item.connect("clicked", lambda *_: callback())
    return item


def brand(text, rtl=False):
    from .icons import NavigationIcon
    row = Gtk.Box(spacing=7)
    icon = NavigationIcon("leaf", 23)
    icon.get_style_context().add_class("brand-mark")
    row.pack_start(icon, False, False, 0)
    row.pack_start(label(text, "heading"), True, True, 0)
    direction(row, rtl)
    return row
