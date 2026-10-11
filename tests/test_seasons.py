import copy
import json
import math
import tempfile
import unittest
from datetime import date
from pathlib import Path

from rooz.calendar_service import gregorian
from rooz.config import Config, DEFAULTS, validate
from rooz.seasons import SEASONS, effective_season, season_for_month


class SeasonTests(unittest.TestCase):
    def test_all_months_and_invalid_inputs(self):
        self.assertEqual([s for s in SEASONS for _ in range(3)], [season_for_month(m) for m in range(1, 13)])
        for invalid in (0, 13, True, "7", 7.0):
            with self.assertRaises(ValueError):
                season_for_month(invalid)

    def test_actual_year_and_season_boundaries(self):
        cfg = copy.deepcopy(DEFAULTS)
        for month, season in ((1, "spring"), (4, "summer"), (7, "autumn"), (10, "winter")):
            self.assertEqual(season, effective_season(cfg, gregorian(1405, month, 1)))
        self.assertEqual("winter", effective_season(cfg, gregorian(1405, 12, 29)))
        self.assertEqual("spring", effective_season(cfg, gregorian(1406, 1, 1)))

    def test_viewed_month_is_scoped_and_manual_wins(self):
        cfg = copy.deepcopy(DEFAULTS)
        today = date(2026, 10, 11)
        self.assertEqual("autumn", effective_season(cfg, today, 1))
        cfg["appearance"]["calendar_follow_viewed_month"] = True
        self.assertEqual("spring", effective_season(cfg, today, 1))
        self.assertEqual("autumn", effective_season(cfg, today))
        cfg["appearance"]["season"] = "winter"
        self.assertEqual("winter", effective_season(cfg, today, 1))

    def test_legacy_migration_preserves_preferences_and_startup_identity(self):
        raw = {"language": "en", "digits": "latin", "appearance": {
            "theme": "light", "accent_color": "#AA33FF", "widget_scale": 1.3,
        }, "calendar": {"prefer_numerical_dates": True}, "window": {"position": [-200, 30], "locked": True}}
        cfg = validate(raw)
        self.assertEqual("classic", cfg["appearance"]["style"])
        self.assertEqual("custom", cfg["appearance"]["accent_source"])
        self.assertEqual("#AA33FF", cfg["appearance"]["accent_color"])
        self.assertEqual("light", cfg["appearance"]["theme"])
        self.assertEqual(1.3, cfg["appearance"]["widget_scale"])
        self.assertEqual([-200, 30], cfg["window"]["position"])
        self.assertTrue(cfg["calendar"]["prefer_numerical_dates"])
        self.assertEqual("en", cfg["language"])
        cfg["appearance"].update(style="seasonal", season="winter")
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary) / "config.json"
            p.write_text(json.dumps(cfg))
            reloaded = Config(p).value
            self.assertEqual("winter", reloaded["appearance"]["season"])
            self.assertEqual("#AA33FF", reloaded["appearance"]["accent_color"])
            self.assertTrue(reloaded["window"]["locked"])

    def test_fresh_defaults_and_invalid_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            fresh = Config(Path(temporary) / "missing.json").value
            self.assertEqual("seasonal", fresh["appearance"]["style"])
            self.assertEqual("auto", fresh["appearance"]["season"])
        for invalid in (math.inf, -math.inf, math.nan, True, "0.2"):
            cfg = validate({"appearance": {"style": "bad", "season": "bad",
                            "artwork_intensity": invalid, "show_artwork": "true"}})
            self.assertEqual(.65, cfg["appearance"]["artwork_intensity"])
            self.assertEqual("seasonal", cfg["appearance"]["style"])
            self.assertEqual("auto", cfg["appearance"]["season"])
            self.assertTrue(cfg["appearance"]["show_artwork"])

    def test_packaged_scene_manifest_checksums(self):
        import hashlib
        root = Path(__file__).resolve().parents[1] / "data/themes/seasons"
        manifest = json.loads((root / "manifest.json").read_text())
        self.assertEqual(set(SEASONS), set(manifest["seasons"]))
        for season, entry in manifest["seasons"].items():
            asset = root / entry["file"]
            self.assertTrue(asset.is_file(), season)
            self.assertEqual(entry["sha256"], hashlib.sha256(asset.read_bytes()).hexdigest())
