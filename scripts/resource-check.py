#!/usr/bin/python3
"""Measure a 60-second idle widget interval in a temporary profile."""

import json, os, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def reading(pid):
    raw = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    status = Path(f"/proc/{pid}/status").read_text()
    rss = int(next(line.split()[1] for line in status.splitlines() if line.startswith("VmRSS:")))
    return {"rss_kib": rss, "cpu_ticks": int(raw[11]) + int(raw[12]), "monotonic": time.monotonic()}


with tempfile.TemporaryDirectory(prefix="rooz-resource-") as tmp:
    env = {
        **os.environ,
        "XDG_CONFIG_HOME": tmp + "/config",
        "XDG_DATA_HOME": tmp + "/data",
        "GIO_USE_VFS": "local",
        "GTK_USE_PORTAL": "0",
    }
    with open(tmp + "/app.log", "w") as log:
        proc = subprocess.Popen(
            [str(ROOT / "scripts/dev-run.sh"), "--widget"], env=env, stdout=log, stderr=log
        )
        try:
            time.sleep(5)
            start = reading(proc.pid)
            samples = [start]
            for _ in range(12):
                time.sleep(5)
                samples.append(reading(proc.pid))
            end = samples[-1]
            elapsed = end["monotonic"] - start["monotonic"]
            cpu_seconds = (end["cpu_ticks"] - start["cpu_ticks"]) / os.sysconf("SC_CLK_TCK")
            report = {
                "context": "Mint 22.3 Xfce X11; real widget only, default theme/font/scale, temporary XDG profile",
                "duration_seconds": round(elapsed, 2),
                "cpu_seconds": round(cpu_seconds, 4),
                "cpu_percent_one_core": round(cpu_seconds / elapsed * 100, 3),
                "rss_start_kib": start["rss_kib"],
                "rss_end_kib": end["rss_kib"],
                "rss_min_kib": min(x["rss_kib"] for x in samples),
                "rss_max_kib": max(x["rss_kib"] for x in samples),
                "limitations": "One minute is not an endurance or overnight/resume test.",
            }
            (ROOT / "docs/resource-check.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report, indent=2))
        finally:
            subprocess.run(
                [str(ROOT / "scripts/dev-run.sh"), "--quit"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            proc.wait(timeout=5)
