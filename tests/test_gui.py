"""GTK smoke checks; run on a real or virtual display in an isolated D-Bus session."""

import copy, os, unittest
from datetime import date
from types import SimpleNamespace
import gi
import cairo

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, Gio, Pango, PangoCairo
from rooz.config import DEFAULTS
from rooz.events import Repository
from rooz.i18n import Localizer
from rooz import fonts
from rooz.ui.widget import Card
from rooz.ui.calendar_window import CalendarWindow
from rooz.ui.settings import Settings
from rooz.ui.theme import apply, rgb, tokens
from rooz.calendar_service import MIN_YEAR, MAX_YEAR, gregorian


def pump():
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)


@unittest.skipUnless(os.environ.get("ROOZ_GUI_TESTS") == "1", "Run scripts/test-gui.sh for GUI checks")
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Gtk.init_check()[0]:
            raise unittest.SkipTest("Display unavailable")
        cls.font_errors = fonts.load()

        class FakeApp(Gtk.Application):
            def __init__(self):
                super().__init__(application_id=None, flags=Gio.ApplicationFlags.NON_UNIQUE)
                self.register(None)
                self.cfg = copy.deepcopy(DEFAULTS)
                self.loc = Localizer(self.cfg)
                self.repo = Repository(user="/nonexistent")
                self.today = date(2026, 10, 10)
                self.config = SimpleNamespace(warning=None)
                self.font_warnings = []
                self.actions = []

            def open_calendar(self):
                self.actions.append("calendar")

            def open_settings(self):
                self.actions.append("settings")

            def save(self):
                self.actions.append("save")

            def change(self, s, k, v):
                self.cfg[s][k] = v

            def copy(self, *args, **kwargs):
                self.actions.append(("copy", args, kwargs))

            def reset_position(self):
                pass

            def reset_appearance(self):
                pass

        cls.app = FakeApp()

    def setUp(self):
        self.app.cfg = copy.deepcopy(DEFAULTS)
        self.app.loc = Localizer(self.app.cfg)
        self.app.actions = []
        self.windows = []

    def tearDown(self):
        for w in self.windows:
            w.destroy()
        pump()

    def window(self, kind):
        w = kind(self.app)
        self.windows.append(w)
        pump()
        return w

    def test_card_compact_font_and_gear(self):
        card = self.window(Card)
        self.assertEqual((320, 236), tuple(card.get_size()))
        self.assertEqual([], self.font_errors)
        f = PangoCairo.FontMap.get_default().create_context().load_font(Pango.FontDescription("Vazirmatn 12"))
        self.assertIn("Vazirmatn", f.describe().to_string())
        card.gear.clicked()
        self.assertEqual(["settings"], self.app.actions)

    def test_double_click_lock_and_drag_threshold(self):
        c = self.window(Card)
        self.app.cfg["window"]["locked"] = True
        e = SimpleNamespace(button=1, type=Gdk.EventType.DOUBLE_BUTTON_PRESS, y=75, x_root=10, y_root=10)
        self.assertTrue(c.press(c.canvas, e))
        self.assertEqual(["calendar"], self.app.actions)
        e.type = Gdk.EventType.BUTTON_PRESS
        e.y = 10
        self.assertFalse(c.press(c.canvas, e))
        self.app.cfg["window"]["locked"] = False
        c.press(c.canvas, e)
        c.motion(c.canvas, SimpleNamespace(x_root=12, y_root=12))
        self.assertFalse(c.dragged)
        c.cancel_drag()

    def test_selection_navigation_and_hide(self):
        w = self.window(CalendarWindow)
        w.select(date(2026, 10, 9))
        self.assertEqual(date(2026, 10, 10), self.app.today)
        w.navigate(-7)
        self.assertEqual((1404, 12), (w.year, w.month))
        w.navigate(1)
        self.assertEqual((1405, 1), (w.year, w.month))
        w.go_today()
        self.assertEqual(self.app.today, w.selected)
        w.hide()
        w.apply()
        self.assertFalse(w.get_visible())

    def test_grid_keys_and_accessibility(self):
        w = self.window(CalendarWindow)
        w.focus_selected()
        pump()
        event = SimpleNamespace(keyval=Gdk.KEY_Left)
        self.assertTrue(w.key(w, event))
        self.assertEqual(date(2026, 10, 11), w.selected)
        event.keyval = Gdk.KEY_Right
        w.key(w, event)
        self.assertEqual(date(2026, 10, 10), w.selected)
        self.assertIn("امروز", w.cells[self.app.today].get_accessible().get_name())
        self.assertTrue(w.cells[self.app.today].get_style_context().has_class("selected"))
        self.assertTrue(w.cells[self.app.today].get_style_context().has_class("today"))

    def test_language_digits_and_settings(self):
        w = self.window(CalendarWindow)
        s = self.window(Settings)
        self.app.cfg["language"] = "en"
        self.app.cfg["digits"] = "latin"
        w.apply()
        s.apply()
        self.assertEqual("Roozlet · Calendar", w.get_title())
        self.assertEqual(Gtk.TextDirection.LTR, w.root.get_direction())
        self.assertEqual(date(2026, 10, 10), w.selected)
        self.assertIn("18 Mehr 1405", w.cells[self.app.today].get_accessible().get_name())
        s.hide()
        s.apply()
        self.assertFalse(s.get_visible())

    def test_missing_custom_font_fallback(self):
        self.app.cfg["appearance"].update(font_mode="custom", custom_font_family="Rooz Missing Family 98765")
        self.assertEqual("Sans", fonts.family(self.app.cfg))
        window = self.window(Settings)

        def texts(widget):
            result = [widget.get_text()] if isinstance(widget, Gtk.Label) else []
            if isinstance(widget, Gtk.Container):
                for child in widget.get_children():
                    result.extend(texts(child))
            return result

        self.assertIn(self.app.loc.t("font_fallback"), texts(window))

    def test_large_text_scale_and_light_theme(self):
        c = self.window(Card)
        w = self.window(CalendarWindow)
        s = self.window(Settings)
        self.app.cfg["appearance"].update(theme="light", text_scale=1.4, widget_scale=1.6)
        provider = Gtk.CssProvider()
        apply(self.app.cfg, provider)
        c.apply()
        w.apply()
        s.apply()
        pump()
        area = c.get_display().get_primary_monitor().get_workarea()
        self.assertLessEqual(c.dimensions()[0], area.width)
        self.assertLessEqual(c.dimensions()[1], area.height)
        self.assertEqual(30, len(w.cells))
        self.assertGreaterEqual(w.get_size().height, 300)

    def test_header_title_pixels_and_gear_are_on_opposite_correct_edges(self):
        c = self.window(Card)
        for lang in ("fa", "en"):
            self.app.cfg["language"] = lang
            c.apply()
            c.fixed.check_resize()
            pump()
            width, height = c.dimensions()
            self.assertEqual(lang == "fa", c.gear.get_allocation().x < width / 2)
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            c.draw(c.canvas, cairo.Context(surface))
            surface.flush()
            pixels = bytes(surface.get_data())
            target = tuple(round(v * 255) for v in rgb(tokens(self.app.cfg, self.app.today)["fg"]))
            xs = []
            for y in range(10, 35):
                for x in range(width):
                    offset = y * surface.get_stride() + x * 4
                    actual = (pixels[offset + 2], pixels[offset + 1], pixels[offset])
                    if all(abs(a - b) < 5 for a, b in zip(actual, target)):
                        xs.append(x)
            self.assertTrue(xs, "Title should render in the header")
            self.assertEqual(lang == "fa", sum(xs) / len(xs) > width / 2)

    def test_numeric_setting_tooltip_and_explicit_numeric_context_copy(self):
        c = self.window(Card)
        self.app.cfg.update(language="en", digits="latin")
        self.app.cfg["calendar"]["prefer_numerical_dates"] = True
        c.apply()
        tooltip = SimpleNamespace(set_text=lambda value: setattr(self, "tip", value))
        c.tooltip(c.canvas, 100, 100, False, tooltip)
        self.assertIn("1405/7/18", self.tip)
        self.assertIn("2026/10/10", self.tip)
        settings = self.window(Settings)
        switches = []

        def find_switches(widget):
            if isinstance(widget, Gtk.Box):
                children = widget.get_children()
                if any(isinstance(c, Gtk.Label) and c.get_text() == self.app.loc.t("numerical_dates") for c in children):
                    switches.extend(c for c in children if isinstance(c, Gtk.Switch))
            if isinstance(widget, Gtk.Container):
                for child in widget.get_children():
                    find_switches(child)

        find_switches(settings)
        self.assertEqual(1, len(switches))
        self.assertTrue(switches[0].get_active())
        switches[0].set_active(False)
        self.assertFalse(self.app.cfg["calendar"]["prefer_numerical_dates"])
        event = Gdk.Event.new(Gdk.EventType.BUTTON_PRESS)
        event.window = c.canvas.get_window()
        event.button, event.x, event.y = 3, 100, 100
        event.time = Gdk.CURRENT_TIME
        menu = c.menu(event)
        numeric = next(i for i in menu.get_children() if i.get_label() == self.app.loc.t("copy_numeric"))
        numeric.get_submenu().get_children()[1].activate()
        self.assertIn(("copy", (self.app.today, 1), {"numerical": True}), self.app.actions)
        menu.popdown()
        menu.destroy()

    def test_today_right_click_picker_selection_and_left_click(self):
        w = self.window(CalendarWindow)
        w.navigate(-1)
        previous = w.selected
        self.assertTrue(w.today_press(w.today_button, SimpleNamespace(button=3)))
        picker = w.month_picker
        self.assertEqual(previous, w.selected, "Right-click must not reset the selected date")
        self.assertEqual(set(range(1, 13)), set(picker.month_buttons))
        picker.change_year(1)
        picker.month_buttons[12].clicked()
        self.assertEqual((1406, 12), (w.year, w.month))
        self.assertIsNone(w.month_picker)
        self.assertEqual(date(2026, 10, 10), self.app.today)
        self.assertFalse(w.today_press(w.today_button, SimpleNamespace(button=1)))
        w.today_button.clicked()
        self.assertEqual(self.app.today, w.selected)

    def test_month_picker_clamps_days_and_obeys_year_limits_in_both_languages(self):
        w = self.window(CalendarWindow)
        w.select(gregorian(1405, 1, 31))
        w.choose_month(1405, 12)
        self.assertEqual(gregorian(1405, 12, 29), w.selected)
        for lang in ("fa", "en"):
            self.app.cfg["language"] = lang
            w.apply()
            self.assertTrue(w.today_button.emit("popup-menu"))
            picker = w.month_picker
            self.assertEqual(12, len(picker.month_buttons))
            self.assertEqual(
                "فروردین" if lang == "fa" else "Farvardin", picker.month_buttons[1].get_label()
            )
            picker.year = MIN_YEAR
            picker.apply()
            picker.change_year(-1)
            self.assertEqual(MIN_YEAR, picker.year)
            self.assertFalse(picker.previous_year.get_sensitive())
            picker.year = MAX_YEAR
            picker.apply()
            picker.change_year(1)
            self.assertEqual(MAX_YEAR, picker.year)
            self.assertFalse(picker.next_year.get_sensitive())
            w.dismiss_month_picker()

    def test_centered_primary_survives_language_and_hidden_satellites(self):
        from rooz.seasons import SEASONS
        c = self.window(Card)
        for language in ("fa", "en"):
            for season in SEASONS:
                for gregorian_visible, hijri_visible in ((True, True), (True, False), (False, True), (False, False)):
                    self.app.cfg["language"] = language
                    self.app.cfg["appearance"]["season"] = season
                    self.app.cfg["calendar"].update(show_gregorian_column=gregorian_visible, show_hijri_column=hijri_visible)
                    c.apply()
                    c.fixed.check_resize()
                    pump()
                    x, width = c.date_slots()["shamsi"]
                    self.assertEqual(160, x + width / 2)
                    self.assertEqual(320, c.dimensions()[0])
                    self.assertEqual(language == "fa", c.gear.get_allocation().x < 160)

    def test_window_scoped_seasons_and_title_picker(self):
        c = self.window(Card)
        w = self.window(CalendarWindow)
        self.app.cfg["appearance"]["calendar_follow_viewed_month"] = True
        w.choose_month(1405, 1)
        c.apply()
        self.assertTrue(w.get_style_context().has_class("season-spring"))
        self.assertTrue(c.get_style_context().has_class("season-autumn"))
        w.title_button.clicked()
        self.assertEqual(12, len(w.month_picker.month_buttons))
        w.dismiss_month_picker()
        w.show_view("occasions")
        self.assertEqual("occasions", w.view)
        w.select(self.app.today)
        self.assertEqual("calendar", w.view)
        self.assertEqual(self.app.today, w.selected)

    def test_missing_scene_fallback_and_native_preview_controls(self):
        from rooz.ui.artwork import image
        self.assertIsNone(image("unknown", 100, 80))
        s = self.window(Settings)
        s.season_previews["winter"].clicked()
        self.assertEqual("winter", self.app.cfg["appearance"]["season"])
        self.assertEqual("seasonal", self.app.cfg["appearance"]["style"])
        self.assertEqual(4, len(s.season_previews))
        self.assertIn("روزلت", s.get_title())


if __name__ == "__main__":
    unittest.main()
