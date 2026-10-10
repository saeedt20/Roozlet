#!/bin/sh
set -eu
ROOZ_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$ROOZ_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec /usr/bin/python3 -m rooz "$@"
