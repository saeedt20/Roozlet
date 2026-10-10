#!/bin/sh
set -eu
ROOZ_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOZ_ROOT"
PYTHONPATH=src /usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 scripts/validate-data.py
/usr/bin/python3 scripts/package.py
