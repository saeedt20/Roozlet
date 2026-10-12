"""Short, interruptible native transitions; no work at rest."""

from gi.repository import GLib, Gtk


def enabled(cfg, widget=None):
    settings = widget.get_settings() if widget else Gtk.Settings.get_default()
    return bool(cfg["appearance"].get("motion_effects", True)
                and settings and settings.get_property("gtk-enable-animations"))


class ContentStack(Gtk.Stack):
    """At most two content trees during a fade, one after completion."""
    def __init__(self):
        super().__init__()
        self.set_hhomogeneous(False)
        self.set_vhomogeneous(False)
        self._pruning = False
        self.connect("notify::transition-running", self.prune)

    def prune(self, *_, force=False):
        if not self._pruning and (force or not self.get_transition_running()):
            self._pruning = True
            current = self.get_visible_child()
            for child in self.get_children():
                if child is not current:
                    self.remove(child)
                    child.destroy()
            self._pruning = False

    def replace(self, child, cfg, animate=False, duration=180):
        # Rapid input replaces the previous pending state rather than queuing it.
        self.set_transition_type(Gtk.StackTransitionType.NONE)
        self.prune(force=True)
        child.show_all()
        self.add(child)
        use_motion = animate and enabled(cfg, self) and self.get_mapped()
        self.set_transition_duration(duration if use_motion else 0)
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE if use_motion
                                 else Gtk.StackTransitionType.NONE)
        self.set_visible_child(child)
        self.prune()


class ArtworkTransition:
    """Frame-clock callbacks exist only for a visible, 260 ms scene change."""
    duration = 260_000

    def __init__(self, widget, cfg):
        self.widget, self.cfg = widget, cfg
        self.current = self.previous = None
        self.started = 0
        self.tick_id = 0
        widget.connect("unmap", self.stop)
        widget.connect("destroy", self.stop)

    def stop(self, *_):
        if self.tick_id:
            self.widget.remove_tick_callback(self.tick_id)
            self.tick_id = 0
        self.previous = None

    def set_scene(self, season):
        if season == self.current:
            if not enabled(self.cfg, self.widget):
                self.stop()
            return
        old = self.current
        self.stop()
        self.current = season
        if old and season and self.widget.get_mapped() and enabled(self.cfg, self.widget):
            self.previous = old
            self.started = GLib.get_monotonic_time()
            self.tick_id = self.widget.add_tick_callback(self.tick)
        self.widget.queue_draw()

    def tick(self, _, clock):
        if not enabled(self.cfg, self.widget) or clock.get_frame_time() - self.started >= self.duration:
            self.tick_id = 0
            self.previous = None
            self.widget.queue_draw()
            return False
        self.widget.queue_draw()
        return True

    def paint(self, cr, width, height, intensity):
        from .artwork import paint
        if self.previous:
            progress = max(0, min(1, (GLib.get_monotonic_time() - self.started) / self.duration))
            progress = 1 - (1 - progress) ** 3
            cr.push_group()
            paint(cr, self.previous, width, height, 1)
            paint(cr, self.current, width, height, progress)
            cr.pop_group_to_source()
            cr.paint_with_alpha(intensity)
        elif self.current:
            paint(cr, self.current, width, height, intensity)
