"""Validated XDG preferences with atomic writes and recovery."""

import copy
import json
import math
import os
import re
import tempfile
from pathlib import Path

DEFAULTS = {
    "schema_version": 1,
    "language": "fa",
    "digits": "persian",
    "timezone": "Asia/Tehran",
    "appearance": {
        "theme": "dark",
        "style": "seasonal",
        "season": "auto",
        "accent_source": "seasonal",
        "show_artwork": True,
        "artwork_intensity": 0.65,
        "calendar_follow_viewed_month": False,
        "motion_effects": True,
        "accent_color": "#5FE3AF",
        "background_opacity": 0.9,
        "widget_scale": 1.0,
        "font_mode": "vazirmatn",
        "custom_font_family": "Sans",
        "text_scale": 1.0,
    },
    "calendar": {
        "prefer_numerical_dates": False,
        "show_gregorian_cell_numbers": True,
        "show_hijri_column": True,
        "show_gregorian_column": True,
        "show_next_public_holiday": True,
    },
    "events": {
        "visible_categories": ["national", "cultural", "religious", "international"],
        "show_public_holidays": True,
    },
    "window": {
        "monitor": "primary",
        "position": None,
        "locked": False,
        "always_on_top": False,
        "all_workspaces": True,
        "margin": 24,
    },
}


def config_home():
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def validate(raw):
    cfg = copy.deepcopy(DEFAULTS)
    if not isinstance(raw, dict):
        raise ValueError("Configuration must be an object")
    if raw.get("schema_version", 1) not in (0, 1):
        raise ValueError("Unsupported configuration schema")
    for k, vals in {
        "language": ["fa", "en"],
        "digits": ["persian", "latin"],
        "timezone": ["Asia/Tehran", "system"],
    }.items():
        if raw.get(k) in vals:
            cfg[k] = raw[k]
    for section in ("appearance", "calendar", "events", "window"):
        values = raw.get(section, {})
        if not isinstance(values, dict):
            continue
        for k, default in cfg[section].items():
            v = values.get(k, default)
            if type(default) is bool and type(v) is bool:
                cfg[section][k] = v
            elif type(default) is str and isinstance(v, str):
                cfg[section][k] = v[:200]
    a = cfg["appearance"]
    r = raw.get("appearance", {})
    r = r if isinstance(r, dict) else {}
    for k, lo, hi in [
        ("background_opacity", 0.5, 1.0),
        ("widget_scale", 0.8, 1.6),
        ("text_scale", 0.85, 1.4),
        ("artwork_intensity", 0.0, 1.0),
    ]:
        v = r.get(k, a[k])
        a[k] = max(lo, min(hi, v)) if type(v) in (float, int) and math.isfinite(v) else a[k]
    if "appearance" in raw and "style" not in r:
        a["style"] = "classic"
        a["accent_source"] = "custom"
    for key, choices in {
        "style": ("classic", "seasonal"),
        "season": ("auto", "spring", "summer", "autumn", "winter"),
        "accent_source": ("seasonal", "custom"),
    }.items():
        if a[key] not in choices:
            a[key] = DEFAULTS["appearance"][key]
    if a["theme"] not in ("dark", "light"):
        a["theme"] = "dark"
    if a["font_mode"] not in ("vazirmatn", "system", "custom"):
        a["font_mode"] = "vazirmatn"
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", a["accent_color"]):
        a["accent_color"] = "#5FE3AF"
    w = raw.get("window", {})
    w = w if isinstance(w, dict) else {}
    p = w.get("position")
    if isinstance(p, list) and len(p) == 2 and all(type(n) is int and abs(n) < 100000 for n in p):
        cfg["window"]["position"] = p
    e = raw.get("events", {})
    e = e if isinstance(e, dict) else {}
    cats = e.get("visible_categories")
    if isinstance(cats, list):
        cfg["events"]["visible_categories"] = [
            v for v in cats if v in DEFAULTS["events"]["visible_categories"]
        ]
    return cfg


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".rooz-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf8") as out:
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Config:
    def __init__(self, path=None):
        self.path = Path(path) if path else config_home() / "rooz/config.json"
        self.warning = None
        try:
            self.value = validate(json.loads(self.path.read_text()))
        except FileNotFoundError:
            self.value = copy.deepcopy(DEFAULTS)
        except (ValueError, TypeError, OSError) as e:
            self.warning = str(e)
            if self.path.exists():
                import time

                backup = self.path.with_name(f"config.bad-{time.time_ns()}.json")
                self.path.rename(backup)
            self.value = copy.deepcopy(DEFAULTS)

    def save(self):
        self.value = validate(self.value)
        atomic_write(self.path, json.dumps(self.value, ensure_ascii=False, indent=2) + "\n")
