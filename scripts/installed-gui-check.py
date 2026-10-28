#!/usr/bin/python3
"""Launch extracted package from /tmp and capture real live windows at both DPIs."""

import argparse, json, os, re, subprocess, tempfile, time
from pathlib import Path
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("launcher", type=Path, help="Path to the extracted usr/bin/rooz launcher")
launcher = parser.parse_args().launcher.resolve()
if not launcher.is_file():
    parser.error("The extracted launcher does not exist")


def windows(pid):
    items = []
    for line in subprocess.check_output(["wmctrl", "-lG"], text=True).splitlines():
        f = line.split(None, 7)
        if len(f) != 8 or not f[7].startswith(("Roozlet ·", "روزلت ·")):
            continue
        prop = subprocess.check_output(["xprop", "-id", f[0], "_NET_WM_PID"], text=True)
        if not re.search(r"=\s*" + str(pid) + r"\b", prop):
            continue
        items.append((f[0], int(f[4]), int(f[5]), f[7]))
    return items


reports = []
with tempfile.TemporaryDirectory(prefix="rooz-installed-gui-") as tmp:
    env = {
        **os.environ,
        "XDG_CONFIG_HOME": tmp + "/config",
        "XDG_DATA_HOME": tmp + "/data",
        "GIO_USE_VFS": "local",
        "GTK_USE_PORTAL": "0",
    }
    for scale in ("1", "2"):
        env["GDK_SCALE"] = scale
        with open(tmp + "/app.log", "w") as log:
            proc = subprocess.Popen(
                [str(launcher), "--calendar"], cwd="/tmp", env=env, stdout=log, stderr=log
            )
            try:
                deadline = time.monotonic() + 45
                while time.monotonic() < deadline:
                    ws = windows(proc.pid)
                    if len(ws) >= 2:
                        break
                    time.sleep(0.15)
                assert len(ws) == 2, ws
                card = next(w for w in ws if w[3] == "روزلت · ویجت")
                cal = next(w for w in ws if w[3] == "روزلت · تقویم")
                assert card[1:3] == (320 * int(scale), 236 * int(scale)), card
                if scale == "2":
                    time.sleep(.3)
                    subprocess.run(
                        ["import", "-window", card[0], str(ROOT / "docs/screenshots/v0.4.2-installed-card-fa-dark-2x.png")],
                        check=True,
                    )
                    subprocess.run(
                        ["import", "-window", cal[0], str(ROOT / "docs/screenshots/v0.4.2-installed-calendar-fa-dark-2x.png")],
                        check=True,
                    )
                for command, title in (("--settings", "روزلت · تنظیمات"), ("--search", "روزلت · جستجو"),
                                       ("--personal", "روزلت · یادداشت و یادآور")):
                    subprocess.run([str(launcher), command], env=env, cwd="/tmp", check=True)
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        routed = windows(proc.pid)
                        if any(w[0] == cal[0] and w[3] == title for w in routed):
                            break
                        time.sleep(.05)
                    assert len(routed) == 2 and any(w[0] == cal[0] and w[3] == title for w in routed), (command, routed)
                subprocess.run([str(launcher), "--calendar"], env=env, cwd="/tmp", check=True)
                assert {w[0] for w in windows(proc.pid)} == {card[0], cal[0]}
                reports.append(
                    {
                        "scale": scale,
                        "card_physical_size": list(card[1:3]),
                        "calendar_physical_size": list(cal[1:3]),
                        "cwd": "/tmp",
                        "launcher": "extracted installed /usr/bin/rooz",
                        "status": "passed",
                    }
                )
            finally:
                subprocess.run(
                    [str(launcher), "--quit"],
                    env=env,
                    cwd="/tmp",
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                proc.wait(timeout=5)
            assert "Traceback" not in Path(tmp + "/app.log").read_text(), Path(tmp + "/app.log").read_text()
(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist/installed-gui-check-0.4.2.json").write_text(json.dumps(reports, indent=2) + "\n")
print(json.dumps(reports, indent=2))
