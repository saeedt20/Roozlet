"""Localized About pages whose long notices cannot enlarge the window."""

from gi.repository import Gdk, Gtk, Pango

from .. import __version__
from ..resources import DATA, ROOT
from .common import button, direction, label
from .icons import NavigationIcon
from .motion import enabled
from .theme import style_window

PROJECT_URL = "https://github.com/saeedt20/Roozlet"


class AboutWindow(Gtk.Window):
    def __init__(self, parent):
        self.app = parent.app
        loc = self.app.loc
        super().__init__(transient_for=parent, modal=True, title=loc.t("about_title"))
        self.set_destroy_with_parent(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.get_style_context().add_class("rooz")
        style_window(self, self.app.cfg, self.app.today)
        display = parent.get_display()
        monitor = (display.get_monitor_at_window(parent.get_window()) if parent.get_window()
                   else display.get_primary_monitor() or display.get_monitor(0))
        area = monitor.get_workarea()
        self.set_default_size(min(560, max(240, area.width - 48)),
                              min(560, max(180, area.height - 120)))
        self.set_size_request(240, 180)
        self.header = Gtk.HeaderBar(title=loc.t("about_title"), show_close_button=True)
        self.set_titlebar(self.header)
        shell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        shell.set_border_width(16)
        self.add(shell)
        self.stack = Gtk.Stack()
        self.stack.set_transition_duration(160 if enabled(self.app.cfg, self) else 0)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE
                                       if enabled(self.app.cfg, self) else Gtk.StackTransitionType.NONE)
        self.switcher = Gtk.StackSwitcher(stack=self.stack)
        self.switcher.get_style_context().add_class("about-tabs")
        self.switcher.set_halign(Gtk.Align.CENTER)
        shell.pack_start(self.switcher, False, False, 0)
        self.pages = {}
        self.credit_labels = []
        self.links = {}
        self.about_page = self.page("about", loc.t("about"))
        self.about_page.set_spacing(8)
        self.build_about(loc)
        self.credits_page = self.page("credits", loc.t("credits"))
        self.build_credits(loc)
        self.license_page = self.page("licenses", loc.t("licenses"))
        self.build_licenses(loc)
        shell.pack_start(self.stack, True, True, 0)
        self.close_button = button(loc.t("close"), self.destroy)
        self.close_button.set_halign(Gtk.Align.END)
        shell.pack_start(self.close_button, False, False, 0)
        direction(shell, loc.lang == "fa")
        direction(self.header, loc.lang == "fa")
        # License originals retain their own writing direction, independently of UI.
        self.license_text.set_direction(Gtk.TextDirection.LTR)
        self.connect("key-press-event", self.key)
        self.show_all()

    def page(self, key, title):
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_border_width(4)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_overlay_scrolling(False)
        scroll.add(content)
        self.stack.add_titled(scroll, key, title)
        self.pages[key] = scroll
        return content

    def text(self, value, style=None, center=False):
        item = label(value, style, align=.5 if center else 0, wrap=True)
        item.set_width_chars(1)
        item.set_max_width_chars(52)
        item.set_selectable(True)
        item.set_hexpand(True)
        return item

    def section(self, container, title, text):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        panel.get_style_context().add_class("details-panel")
        panel.pack_start(self.text(title, "detail-heading"), False, False, 0)
        body = self.text(text)
        panel.pack_start(body, False, False, 0)
        container.pack_start(panel, False, False, 0)
        return body

    def link(self, container, key, title, url):
        link = Gtk.LinkButton.new_with_label(url, title)
        link.set_halign(Gtk.Align.CENTER)
        link.get_accessible().set_name(title)
        container.pack_start(link, False, False, 0)
        self.links[key] = link

    def build_about(self, loc):
        icon = NavigationIcon("calendar", 56)
        icon.set_halign(Gtk.Align.CENTER)
        icon.get_style_context().add_class("brand-mark")
        self.about_page.pack_start(icon, False, False, 4)
        name = "روزلت" if loc.lang == "fa" else "Roozlet"
        self.about_page.pack_start(self.text(name, "heading", True), False, False, 0)
        self.about_page.pack_start(self.text(loc.t("version") + " " + loc.n(__version__), "muted", True), False, False, 0)
        self.about_page.pack_start(self.text(loc.t("about_summary"), center=True), False, False, 0)
        self.link(self.about_page, "github", "GitHub", PROJECT_URL)
        self.link(self.about_page, "issues", loc.t("report_issue"), PROJECT_URL + "/issues")
        self.section(self.about_page, loc.t("data_coverage"), loc.t("about_coverage"))
        self.about_page.pack_start(self.text(loc.t("made_by"), "muted", True), False, False, 0)
        self.about_page.pack_start(self.text("© 2026 Saeed Taheri · MIT", "muted", True), False, False, 0)

    def build_credits(self, loc):
        for title, body in (("created_by", "creator_credit"), ("font", "font_credit"),
                            ("calendar_source", "calendar_credit"), ("date_libraries", "libraries_credit"),
                            ("seasonal_artwork", "artwork_credit"), ("native_toolkit", "toolkit_credit")):
            self.credit_labels.append(self.section(self.credits_page, loc.t(title), loc.t(body)))

    def build_licenses(self, loc):
        self.license_page.pack_start(self.text(loc.t("license_help"), "muted"), False, False, 0)
        project_license = DATA.parent / "LICENSE"
        if not project_license.is_file():
            project_license = ROOT.parents[1] / "doc/rooz/LICENSE"
        self.license_files = {
            "project": project_license,
            "font": DATA / "fonts/vazirmatn/OFL.txt",
            "jdatetime": ROOT / "_vendor/jdatetime/PSF-LICENSE",
            "jalali": ROOT / "_vendor/jalali-core-LICENSE",
        }
        self.license_choice = Gtk.ComboBoxText()
        for key, name in (("project", "Roozlet — MIT"), ("font", "Vazirmatn — SIL OFL 1.1"),
                          ("jdatetime", "jdatetime — PSF"), ("jalali", "jalali-core — LGPL 2.1+")):
            self.license_choice.append(key, name)
        self.license_choice.get_accessible().set_name(loc.t("licenses"))
        for renderer in self.license_choice.get_cells():
            renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
            renderer.set_property("width-chars", 1)
        self.license_page.pack_start(self.license_choice, False, False, 0)
        self.license_text = Gtk.TextView(editable=False, cursor_visible=False)
        self.license_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.license_text.set_left_margin(8)
        self.license_text.set_right_margin(8)
        self.license_text.set_top_margin(8)
        self.license_text.set_bottom_margin(8)
        self.license_text.get_accessible().set_name(loc.t("license_text"))
        self.license_page.pack_start(self.license_text, False, False, 0)
        self.license_choice.connect("changed", self.load_license)
        self.license_choice.set_active_id("project")

    def load_license(self, choice):
        try:
            text = self.license_files[choice.get_active_id()].read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            text = self.app.loc.t("license_unavailable")
        self.license_text.get_buffer().set_text(text)
        scroll = self.pages["licenses"].get_vadjustment()
        scroll.set_value(scroll.get_lower())

    def key(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False
