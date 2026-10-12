"""Optional asynchronous freedesktop notifications on the user's session bus."""

from gi.repository import Gio, GLib

SERVICE = "org.freedesktop.Notifications"
PATH = "/org/freedesktop/Notifications"


class DesktopNotifier:
    def __init__(self, cfg, loc, open_day, status=lambda _: None, eligible=lambda _: True):
        self.cfg, self.loc, self.open_day, self.status = cfg, loc, open_day, status
        self.eligible = eligible
        self.connection = None
        self.capabilities = None
        self.connecting = self.loading = self.closed = False
        self.queue, self.targets = [], {}
        self.subscription = 0
        self.cancel = Gio.Cancellable()

    def send(self, occurrence, finished):
        if self.closed or not self.cfg()["personal"]["notifications_enabled"]:
            finished(False)
            return
        self.queue.append((occurrence, finished))
        if self.connection is None:
            if not self.connecting:
                self.connecting = True
                Gio.bus_get(Gio.BusType.SESSION, self.cancel, self.connected)
        else:
            self.prepare()

    def connected(self, _, result):
        self.connecting = False
        try:
            self.connection = Gio.bus_get_finish(result)
            if self.closed:
                return
            self.subscription = self.connection.signal_subscribe(SERVICE, SERVICE, None, PATH, None,
                                                                 Gio.DBusSignalFlags.NONE, self.signal)
            self.prepare()
        except GLib.Error:
            self.fail_queue()

    def prepare(self):
        if self.closed:
            return
        if self.capabilities is not None:
            self.flush()
        elif not self.loading:
            self.loading = True
            self.connection.call(SERVICE, PATH, SERVICE, "GetCapabilities", None,
                                 GLib.VariantType.new("(as)"), Gio.DBusCallFlags.NONE, 3000,
                                 self.cancel, self.prepared)

    def prepared(self, connection, result):
        self.loading = False
        try:
            self.capabilities = set(connection.call_finish(result).unpack()[0])
            self.flush()
        except GLib.Error:
            self.capabilities = None
            self.fail_queue()

    def fail_queue(self):
        queued, self.queue = self.queue, []
        if not self.closed:
            self.status(False)
        for _, callback in queued:
            callback(False)

    def flush(self):
        queued, self.queue = self.queue, []
        for occurrence, callback in queued:
            if self.closed or not self.cfg()["personal"]["notifications_enabled"] or not self.eligible(occurrence):
                callback(False)
                continue
            loc = self.loc()
            from .calendar_service import jalali
            j = jalali(occurrence.day)
            body = loc.n(f"{j.year}/{j.month}/{j.day} · {occurrence.item['time']}")
            if occurrence.item["body"]:
                body += "\n" + occurrence.item["body"][:300]
            if "body-markup" in self.capabilities:
                body = GLib.markup_escape_text(body)
            actions = ["default", loc.t("open")] if "actions" in self.capabilities else []
            hints = {"desktop-entry": GLib.Variant("s", "rooz"), "urgency": GLib.Variant("y", 1)}
            summary = " ".join(occurrence.item["title"].split())[:120]
            params = GLib.Variant("(susssasa{sv}i)", ("Roozlet", 0, "rooz", summary, body, actions, hints, -1))
            self.connection.call(SERVICE, PATH, SERVICE, "Notify", params, GLib.VariantType.new("(u)"),
                                 Gio.DBusCallFlags.NONE, 3000, self.cancel, self.sent, (occurrence, callback))

    def sent(self, connection, result, data):
        occurrence, callback = data
        try:
            notification_id = connection.call_finish(result).unpack()[0]
            if self.closed:
                callback(False)
                return
            if not self.closed:
                self.targets[notification_id] = occurrence.day
                if len(self.targets) > 500:
                    self.targets.pop(next(iter(self.targets)))
                self.status(True)
            callback(True)
        except GLib.Error:
            self.capabilities = None
            if not self.closed:
                self.status(False)
            callback(False)

    def signal(self, _, sender, path, interface, name, parameters):
        if self.closed:
            return
        values = parameters.unpack()
        if name == "ActionInvoked" and values[1] == "default" and values[0] in self.targets:
            self.open_day(self.targets[values[0]])
        elif name == "NotificationClosed":
            self.targets.pop(values[0], None)

    def close(self):
        self.closed = True
        self.cancel.cancel()
        if self.connection and self.subscription:
            self.connection.signal_unsubscribe(self.subscription)
        self.subscription = 0
        self.targets.clear()
        self.fail_queue()
