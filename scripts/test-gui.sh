#!/bin/sh
set -eu
ROOZ_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ROOZ_TEST_HOME=$(mktemp -d)
trap 'rm -rf "$ROOZ_TEST_HOME"' EXIT
cd "$ROOZ_ROOT"
XDG_CONFIG_HOME="$ROOZ_TEST_HOME/config" XDG_DATA_HOME="$ROOZ_TEST_HOME/data" GIO_USE_VFS=local GTK_USE_PORTAL=0 ROOZ_GUI_TESTS=1 PYTHONPATH=src dbus-run-session -- /usr/bin/python3 -m unittest discover -s tests -v
