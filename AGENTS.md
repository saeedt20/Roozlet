# Rooz development

Read docs/BUILD_SPEC.md; keep the default card compact. Source and installed
assets are independent of the working directory. No runtime network calls.

Run: scripts/dev-run.sh --calendar
Logic tests: PYTHONPATH=src python3 -m unittest discover -s tests -v
GTK tests: scripts/test-gui.sh (needs a graphical display)
Data validation: python3 scripts/validate-data.py
Build: scripts/build-deb.sh

Keep the authoritative version in src/rooz/__init__.py and matching Debian
changelog. Follow docs/DATA_SOURCES.md when updating annual data. Never mark a
user data package officially verified based on structural checks alone.

Do not copy real user settings, third-party desktop windows, secrets or logs into
this repository. Capture screenshots using exact Rooz window IDs. Publication
uses the owner's MIT license and attribution. Repository: saeedt20/Roozlet.
Do not publish new releases or send external messages without user authorization.
