"""GApplication lifecycle and headless commands."""

import argparse
import copy
import json
import sys
from datetime import datetime, timezone

from . import __version__
from .calendar_service import Clock
from .config import DEFAULTS, Config
from .events import Repository
from .i18n import Localizer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rooz", description="Roozlet — Persian calendar for Xfce")
    group = parser.add_mutually_exclusive_group()
    for command in ("widget", "calendar", "search", "personal", "settings", "reset-position", "quit", "check-data", "version"):
        group.add_argument("--" + command, action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        print("Roozlet " + __version__)
        return 0
    if args.check_data:
        try:
            r = Repository()
            print(
                json.dumps(
                    {
                        "datasets": r.reports,
                        "issues": r.errors,
                        "conversion_range": "1350–1450",
                        "hijri_policy": "Official 1405 only; unavailable elsewhere",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 1 if r.errors else 0
        except (OSError, ValueError, KeyError) as e:
            print("Roozlet: " + str(e), file=sys.stderr)
            return 1
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Gdk, Gio, GLib, Gtk

    if not Gtk.init_check()[0]:
        print(
            "Roozlet needs a graphical display. Use --check-data or --version without a desktop.",
            file=sys.stderr,
        )
        return 1
    GLib.set_prgname("rooz")
    GLib.set_application_name("Roozlet")
    Gdk.set_program_class("Rooz")
    from . import fonts
    from .formatting import dates
    from .ui import theme
    from .ui.calendar_window import CalendarWindow
    from .ui.widget import Card
    from .personal import PersonalStore, PersonalError, ReminderEngine, Occurrence
    from .notifications import DesktopNotifier

    class App(Gtk.Application):
        def __init__(self):
            super().__init__(
                application_id="org.roozcalendar.Rooz", flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
            )
            self.card = self.calendar = self.settings = None
            self.timer = 0
            self.initialized = False
            self.personal = None
            self.personal_error = False
            self.last_deleted = None
            self.notification_available = None
            self.notifier = self.reminders = None

        @property
        def cfg(self):
            return self.config.value

        def initialize(self):
            if self.initialized:
                return
            self.config = Config()
            self.loc = Localizer(self.cfg)
            self.repo = Repository()
            self.clock = Clock(self.cfg["timezone"])
            self.clock.reconcile()
            self.today = self.clock.day
            try:
                self.personal = PersonalStore()
            except (PersonalError, OSError):
                self.personal_error = True
            self.notifier = DesktopNotifier(lambda: self.cfg, lambda: self.loc, self.open_notification,
                                            self.notification_status, self.notification_eligible)
            if self.personal:
                self.reminders = ReminderEngine(self.personal, self.notifier.send, self.personal_failed)
            self.font_warnings = fonts.load()
            self.provider = Gtk.CssProvider()
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            theme.apply(self.cfg, self.provider, self.today)
            self.card = Card(self)
            self.timer = GLib.timeout_add_seconds(30, self.reconcile)
            self.initialized = True
            self.check_reminders()

        def do_command_line(self, command):
            incoming = parser.parse_args(command.get_arguments()[1:])
            if incoming.quit:
                self.quit()
                return 0
            was_running = self.initialized
            try:
                self.initialize()
            except (OSError, ValueError, KeyError) as error:
                loc = getattr(self, "loc", Localizer(DEFAULTS))
                print(loc.t("startup_error") + ": " + str(error), file=sys.stderr)
                return 1
            if incoming.settings:
                self.open_settings()
            elif incoming.search:
                self.open_search()
            elif incoming.personal:
                self.open_personal()
            elif incoming.reset_position:
                self.reset_position()
            elif incoming.calendar or was_running and not incoming.widget:
                self.open_calendar()
            return 0

        def do_activate(self):
            self.initialize()
            self.open_calendar()

        def open_calendar(self):
            if self.calendar is None:
                self.calendar = CalendarWindow(self)
            self.calendar.show()
            self.calendar.present()

        def open_settings(self):
            self.open_calendar()
            self.calendar.show_view("settings")

        def open_search(self):
            self.open_calendar()
            self.calendar.open_search()

        def open_personal(self):
            self.open_calendar()
            self.calendar.show_view("personal")

        def open_notification(self, day):
            self.open_calendar()
            self.calendar.select(day)

        def notification_status(self, value):
            self.notification_available = value
            if self.calendar and self.calendar.personal_view:
                self.calendar.personal_view.update_status()
            if self.settings:
                self.settings.update_notification_status()

        def notification_eligible(self, occurrence):
            if occurrence.item["id"] == "test":
                return True
            if not self.personal:
                return False
            try:
                item = self.personal.get(occurrence.item["id"])
                return bool(item and item["notify"] and all(item[k] == occurrence.item[k] for k in ("day", "time", "repeat"))
                            and not any(self.personal.state(item["id"], occurrence.day)))
            except PersonalError:
                self.personal_failed()
                return False

        def personal_failed(self):
            self.personal_error = True
            if self.calendar and self.calendar.personal_view:
                self.calendar.personal_view.show_data_error()

        def personal_changed(self):
            self.personal_error = False
            self.refresh()
            self.check_reminders()

        def check_reminders(self):
            if self.reminders:
                self.reminders.tick(datetime.now(timezone.utc), self.cfg["timezone"],
                                    self.cfg["personal"]["notifications_enabled"])

        def test_notification(self):
            if self.cfg["personal"]["notifications_enabled"]:
                item = {"id": "test", "title": "Roozlet", "body": self.loc.t("test_notification_body"),
                        "time": "09:00", "notify": True, "repeat": "none", "kind": "note"}
                self.notifier.send(Occurrence(item, self.today), lambda _: None)

        def save(self):
            self.config.save()
            self.loc = Localizer(self.cfg)

        def change(self, section, key, value):
            if section:
                self.cfg[section][key] = value
            else:
                self.cfg[key] = value
            self.save()
            previous_day = self.today
            self.clock.zone = self.cfg["timezone"]
            self.clock.reconcile()
            self.today = self.clock.day
            self.refresh(rebuild_calendar=section != "appearance" or self.today != previous_day)
            if section == "personal" or key == "timezone":
                self.check_reminders()
            if self.settings and key in ("language", "digits", "font_mode", "custom_font_family"):
                GLib.idle_add(self.rebuild_settings)

        def rebuild_settings(self):
            if self.settings:
                self.settings.apply()
            return False

        def refresh(self, rebuild_calendar=True):
            theme.apply(self.cfg, self.provider, self.today)
            if self.card:
                self.card.apply()
            if self.calendar:
                if rebuild_calendar:
                    self.calendar.apply()
                else:
                    self.calendar.refresh_appearance()
                for window in (self.calendar.search_window, self.calendar.personal_editor):
                    if window:
                        window.refresh_locale()
            if self.settings:
                self.settings.refresh_appearance()

        def reconcile(self):
            if self.clock.reconcile():
                self.today = self.clock.day
                self.refresh()
            self.check_reminders()
            return True

        def copy(self, day, index, numerical=None):
            values = dates(day, self.loc, self.repo, numerical)
            text = "\n".join(values) if index is None else values[index]
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)
            clipboard.store()

        def reset_position(self):
            self.cfg["window"]["position"] = None
            self.cfg["window"]["monitor"] = "primary"
            self.save()
            self.card.reposition()

        def reset_appearance(self):
            self.cfg["appearance"] = copy.deepcopy(DEFAULTS["appearance"])
            self.save()
            self.refresh()
            self.rebuild_settings()

        def do_shutdown(self):
            if self.timer:
                GLib.source_remove(self.timer)
                self.timer = 0
            if self.notifier:
                self.notifier.close()
            if self.personal:
                self.personal.close()
            Gtk.Application.do_shutdown(self)

    app = App()
    return app.run(["rooz"] + (sys.argv[1:] if argv is None else argv))
