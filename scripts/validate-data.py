#!/usr/bin/python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rooz.app import main

raise SystemExit(main(["--check-data"]))
