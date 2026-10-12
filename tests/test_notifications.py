"""Native notification protocol checks against a private session-bus service."""

import copy
import os
import time
import unittest
from datetime import date

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk
from rooz.config import DEFAULTS
from rooz.i18n import Localizer
from rooz.notifications import DesktopNotifier, SERVICE, PATH
from rooz.personal import Occurrence

XML = '''<node><interface name="org.freedesktop.Notifications">
<method name="GetCapabilities"><arg type="as" direction="out"/></method>
<method name="Notify"><arg type="s" direction="in"/><arg type="u" direction="in"/>
<arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="in"/>
<arg type="as" direction="in"/><arg type="a{sv}" direction="in"/><arg type="i" direction="in"/>
<arg type="u" direction="out"/></method>
<signal name="ActionInvoked"><arg type="u"/><arg type="s"/></signal>
<signal name="NotificationClosed"><arg type="u"/><arg type="u"/></signal>
</interface></node>'''


def wait_for(condition):
    end = time.monotonic() + 3
    while not condition() and time.monotonic() < end:
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)
        time.sleep(.005)
    return condition()


@unittest.skipUnless(os.environ.get("ROOZ_GUI_TESTS") == "1", "Requires the isolated GUI session")
class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.cfg = copy.deepcopy(DEFAULTS)
        self.cfg["personal"]["notifications_enabled"] = True
        self.loc = Localizer(self.cfg)
        self.calls, self.status, self.opened, self.finished = [], [], [], []
        self.capabilities = ["actions", "body-markup"]
        self.fail = False
        self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.node = Gio.DBusNodeInfo.new_for_xml(XML)
        self.registration = self.connection.register_object(PATH, self.node.interfaces[0], self.method, None, None)
        self.connection.call_sync("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                                  "RequestName", GLib.Variant("(su)", (SERVICE, 0)), None,
                                  Gio.DBusCallFlags.NONE, 2000, None)
        self.client = DesktopNotifier(lambda: self.cfg, lambda: self.loc, self.opened.append, self.status.append)
        self.occurrence = Occurrence({"id": "synthetic", "title": "Synthetic reminder", "body": "<b>literal & text</b>",
                                      "time": "09:30", "notify": True, "repeat": "none", "kind": "note"}, date(2026, 10, 12))

    def tearDown(self):
        self.client.close()
        self.connection.unregister_object(self.registration)
        self.connection.call_sync("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                                  "ReleaseName", GLib.Variant("(s)", (SERVICE,)), None,
                                  Gio.DBusCallFlags.NONE, 2000, None)
        wait_for(lambda: not GLib.MainContext.default().pending())

    def method(self, connection, sender, path, interface, method, params, invocation):
        if method == "GetCapabilities":
            invocation.return_value(GLib.Variant("(as)", (self.capabilities,)))
        elif method == "Notify":
            self.calls.append(params.unpack())
            if self.fail:
                invocation.return_dbus_error(SERVICE + ".Error", "Synthetic failure")
            else:
                invocation.return_value(GLib.Variant("(u)", (41,)))

    def test_real_async_payload_markup_escape_and_default_action(self):
        self.client.send(self.occurrence, self.finished.append)
        self.assertTrue(wait_for(lambda: bool(self.finished)))
        self.assertEqual([True], self.finished)
        payload = self.calls[0]
        self.assertEqual("Roozlet", payload[0])
        self.assertIn("&lt;b&gt;literal &amp; text&lt;/b&gt;", payload[4])
        self.assertEqual(["default", self.loc.t("open")], payload[5])
        self.assertEqual("rooz", payload[6]["desktop-entry"])
        self.connection.emit_signal(None, PATH, SERVICE, "ActionInvoked", GLib.Variant("(us)", (41, "default")))
        self.assertTrue(wait_for(lambda: bool(self.opened)))
        self.assertEqual([self.occurrence.day], self.opened)
        self.connection.emit_signal(None, PATH, SERVICE, "NotificationClosed", GLib.Variant("(uu)", (41, 2)))
        self.assertTrue(wait_for(lambda: not self.client.targets))

    def test_no_actions_or_markup_when_service_does_not_support_them(self):
        self.capabilities = []
        self.client.send(self.occurrence, self.finished.append)
        self.assertTrue(wait_for(lambda: bool(self.finished)))
        self.assertIn("<b>literal & text</b>", self.calls[0][4])
        self.assertEqual([], self.calls[0][5])

    def test_disabled_or_closed_client_does_not_send(self):
        self.cfg["personal"]["notifications_enabled"] = False
        self.client.send(self.occurrence, self.finished.append)
        self.assertEqual([False], self.finished)
        self.assertEqual([], self.calls)
        self.cfg["personal"]["notifications_enabled"] = True
        self.client.close()
        self.client.send(self.occurrence, self.finished.append)
        self.assertEqual([False, False], self.finished)
        self.assertEqual([], self.calls)

    def test_disabled_during_async_connect_does_not_send(self):
        self.client.send(self.occurrence, self.finished.append)
        self.cfg["personal"]["notifications_enabled"] = False
        self.assertTrue(wait_for(lambda: bool(self.finished)))
        self.assertEqual([False], self.finished)
        self.assertEqual([], self.calls)

    def test_ineligible_entry_is_rechecked_before_queued_send(self):
        self.client.send(self.occurrence, self.finished.append)
        self.client.eligible = lambda _: False
        self.assertTrue(wait_for(lambda: bool(self.finished)))
        self.assertEqual([False], self.finished)
        self.assertEqual([], self.calls)

    def test_notify_failure_is_reported_without_claiming_success(self):
        self.fail = True
        self.client.send(self.occurrence, self.finished.append)
        self.assertTrue(wait_for(lambda: bool(self.finished)))
        self.assertEqual([False], self.finished)
        self.assertEqual([False], self.status)
        self.assertEqual({}, self.client.targets)


if __name__ == "__main__":
    unittest.main()
