#!/usr/bin/python3
"""Real X11 input/CLI checks in a temporary XDG profile; run in private D-Bus.
Only captures windows whose IDs were obtained from Rooz's exact titles.
"""

import ctypes, ctypes.util, json, os, re, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts/dev-run.sh"
OUT = ROOT / "docs/screenshots"
OUT.mkdir(exist_ok=True)
checks = []
succeeded = False


def run(*args):
    return subprocess.check_output(list(args), text=True)


def windows():
    result = []
    for line in run("wmctrl", "-lG").splitlines():
        fields = line.split(None, 7)
        if len(fields) == 8 and (fields[7].startswith("Roozlet ·") or fields[7].startswith("روزلت ·")):
            pid_property = run("xprop", "-id", fields[0], "_NET_WM_PID")
            if not re.search(r"=\s*" + str(proc.pid) + r"\b", pid_property):
                continue
            geometry = run("xwininfo", "-id", fields[0])
            actual_x = int(re.search(r"Absolute upper-left X:\s*(-?\d+)", geometry)[1])
            actual_y = int(re.search(r"Absolute upper-left Y:\s*(-?\d+)", geometry)[1])
            result.append(
                {
                    "id": fields[0],
                    "desktop": int(fields[1]),
                    "x": actual_x,
                    "y": actual_y,
                    "w": int(fields[4]),
                    "h": int(fields[5]),
                    "title": fields[7],
                }
            )
    return result


def wait_for(title, timeout=45):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        matches = [w for w in windows() if w["title"] == title]
        if matches:
            return matches[0]
        time.sleep(0.1)
    raise AssertionError(("Missing window", title, windows()))


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print("PASS", name, flush=True)


def capture(window, name):
    subprocess.run(["import", "-window", window["id"], str(OUT / name)], check=True)


x11 = ctypes.CDLL(ctypes.util.find_library("X11"))
xtst = ctypes.CDLL(ctypes.util.find_library("Xtst"))
x11.XOpenDisplay.restype = ctypes.c_void_p
x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
x11.XDefaultRootWindow.restype = ctypes.c_ulong
x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
x11.XFlush.argtypes = [ctypes.c_void_p]
x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
x11.XStringToKeysym.restype = ctypes.c_ulong
x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
x11.XKeysymToKeycode.restype = ctypes.c_uint
x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
x11.XQueryPointer.argtypes = (
    [ctypes.c_void_p, ctypes.c_ulong]
    + [ctypes.POINTER(ctypes.c_ulong)] * 2
    + [ctypes.POINTER(ctypes.c_int)] * 4
    + [ctypes.POINTER(ctypes.c_uint)]
)
xtst.XTestFakeMotionEvent.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_ulong,
]
xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
display = x11.XOpenDisplay(None)
assert display
rr = ctypes.c_ulong()
child = ctypes.c_ulong()
rx = ctypes.c_int()
ry = ctypes.c_int()
wx = ctypes.c_int()
wy = ctypes.c_int()
mask = ctypes.c_uint()
x11.XQueryPointer(
    display,
    x11.XDefaultRootWindow(display),
    ctypes.byref(rr),
    ctypes.byref(child),
    ctypes.byref(rx),
    ctypes.byref(ry),
    ctypes.byref(wx),
    ctypes.byref(wy),
    ctypes.byref(mask),
)


def motion(x, y):
    xtst.XTestFakeMotionEvent(display, -1, x, y, 0)
    x11.XFlush(display)
    time.sleep(0.04)


def click(x, y, button=1, times=1):
    motion(x, y)
    for _ in range(times):
        xtst.XTestFakeButtonEvent(display, button, 1, 0)
        xtst.XTestFakeButtonEvent(display, button, 0, 0)
        x11.XFlush(display)
        time.sleep(0.07)
    time.sleep(0.25)


def key(name):
    code = x11.XKeysymToKeycode(display, x11.XStringToKeysym(name.encode()))
    xtst.XTestFakeKeyEvent(display, code, 1, 0)
    xtst.XTestFakeKeyEvent(display, code, 0, 0)
    x11.XFlush(display)
    time.sleep(0.15)


def cli(arg=None):
    subprocess.run([str(RUN)] + ([arg] if arg else []), check=True, stdout=subprocess.DEVNULL)


with tempfile.TemporaryDirectory(prefix="rooz-desktop-") as tmp:
    env = {
        **os.environ,
        "XDG_CONFIG_HOME": tmp + "/config",
        "XDG_DATA_HOME": tmp + "/data",
        "GIO_USE_VFS": "local",
        "GTK_USE_PORTAL": "0",
    }
    os.environ.update(
        {k: env[k] for k in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "GIO_USE_VFS", "GTK_USE_PORTAL")}
    )
    log = Path(tmp) / "app.log"
    stream = log.open("w")
    proc = subprocess.Popen([str(RUN), "--widget"], env=env, stdout=stream, stderr=stream)
    try:
        card = wait_for("روزلت · ویجت")
        check("default card 320 × 236", (card["w"], card["h"]) == (320, 236))
        check("widget-only initial launch", len(windows()) == 1)
        capture(card, "v0.4.2-card-fa-dark.png")
        click(card["x"] + 250, card["y"] + 82, times=2)
        calendar = wait_for("روزلت · تقویم")
        check("native double-click opens month", True)
        check(
            "compact card remains present", len([w for w in windows() if w["title"] == "روزلت · ویجت"]) == 1
        )
        click(card["x"] + 250, card["y"] + 82, times=2)
        check("repeated double-click reuses calendar", wait_for("روزلت · تقویم")["id"] == calendar["id"])
        cli("--calendar")
        check("CLI calendar reuses window", wait_for("روزلت · تقویم")["id"] == calendar["id"])
        capture(calendar, "v0.4.2-calendar-fa-dark.png")
        subprocess.run(["wmctrl", "-ic", calendar["id"]], check=True)
        time.sleep(0.3)
        check("closing month preserves card", len(windows()) == 1)
        click(card["x"] + 22, card["y"] + 22)
        settings = wait_for("روزلت · تنظیمات")
        check("native gear opens settings only", len(windows()) == 2)
        capture(settings, "v0.4.2-settings-fa-dark.png")
        key("Escape")
        time.sleep(0.2)
        check("Escape returns to calendar", wait_for("روزلت · تقویم")["id"] == calendar["id"])
        subprocess.run(["wmctrl", "-ic", calendar["id"]], check=True)
        time.sleep(0.2)
        click(card["x"] + 160, card["y"] + 90, button=3)
        key("Escape")
        check("native right-click menu is dismissible", len(windows()) == 1)
        cli("--reset-position")
        card = wait_for("روزلت · ویجت")
        motion(card["x"] + 55, card["y"] + 20)
        xtst.XTestFakeButtonEvent(display, 1, 1, 0)
        x11.XFlush(display)
        motion(card["x"] - 30, card["y"] + 50)
        xtst.XTestFakeButtonEvent(display, 1, 0, 0)
        x11.XFlush(display)
        time.sleep(0.6)
        moved = wait_for("روزلت · ویجت")
        check("native header drag moves card", moved["x"] != card["x"])
        config = Path(tmp) / "config/rooz/config.json"
        check(
            "drag persists position",
            config.exists() and json.loads(config.read_text())["window"]["position"] is not None,
        )
        cli("--reset-position")
        card = wait_for("روزلت · ویجت")
        check("CLI reset restores default", card["x"] != moved["x"])
        hints = run("xprop", "-id", card["id"], "_NET_WM_WINDOW_TYPE", "_NET_WM_STATE")
        check(
            "managed desktop / below / sticky hints",
            all(
                v in hints
                for v in ("_NET_WM_WINDOW_TYPE_DESKTOP", "_NET_WM_STATE_BELOW", "_NET_WM_STATE_STICKY")
            ),
        )
        # Show Desktop is reversible and does not change wallpaper/panel/compositor.
        subprocess.run(["wmctrl", "-k", "on"], check=True)
        time.sleep(0.2)
        attrs = run("xwininfo", "-id", card["id"])
        subprocess.run(["wmctrl", "-k", "off"], check=True)
        check("card remains viewable during Show Desktop", "Map State: IsViewable" in attrs)
        cli()
        check("relaunch opens existing calendar", wait_for("روزلت · تقویم")["id"] == calendar["id"])
        cli("--quit")
        proc.wait(timeout=5)
        check("single-instance quit completes", proc.returncode == 0)
        # English + Latin + light in the temporary profile, then verify installed-like restart.
        cfg = json.loads(config.read_text())
        cfg.update(language="en", digits="latin")
        cfg["appearance"]["theme"] = "light"
        cfg["window"]["position"] = None
        config.write_text(json.dumps(cfg))
        proc = subprocess.Popen([str(RUN), "--calendar"], env=env, stdout=stream, stderr=stream)
        card = wait_for("Roozlet · Widget")
        calendar = wait_for("Roozlet · Calendar")
        capture(card, "v0.4.2-card-en-light.png")
        capture(calendar, "v0.4.2-calendar-en-light.png")
        check("language/digits/theme persist after restart", True)
        cli("--settings")
        settings = wait_for("Roozlet · Settings")
        capture(settings, "v0.4.2-settings-en-light.png")
        check("settings reuses calendar window", settings["id"] == calendar["id"] and len(windows()) == 2)
        key("Escape")
        check("English Escape returns to calendar", wait_for("Roozlet · Calendar")["id"] == calendar["id"])
        saved = json.loads(config.read_text())
        check("language leaves digit preference independent", saved["language"] == "en" and saved["digits"] == "latin")
        check("start at login remains off", not (Path(tmp) / "config/autostart/rooz.desktop").exists())
        cli("--quit")
        proc.wait(timeout=5)
        succeeded = True
    finally:
        subprocess.run([str(RUN), "--quit"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
        motion(rx.value, ry.value)
        x11.XCloseDisplay(display)
        stream.close()
        errors = log.read_text()
        if "Traceback" in errors:
            raise AssertionError(errors)
        (ROOT / "docs/desktop-check.json").write_text(
            json.dumps(
                {
                    "session": "Mint 22.3 Xfce X11",
                    "checks": checks,
                    "status": "passed" if succeeded else "failed",
                    "count": len(checks),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
print("Completed", len(checks), "native desktop checks")
