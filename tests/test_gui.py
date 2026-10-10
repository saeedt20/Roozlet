"""GTK smoke checks; run on a real or virtual display in an isolated D-Bus session."""

import copy, os, unittest
from datetime import date
from types import SimpleNamespace
import gi

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
from rooz.ui.theme import apply


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

            def copy(self, *args):
                self.actions.append(("copy", args))

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
        self.assertEqual((320, 208), tuple(card.get_size()))
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
        self.assertEqual("Rooz · Calendar", w.get_title())
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


if __name__ == "__main__":
    unittest.main()
