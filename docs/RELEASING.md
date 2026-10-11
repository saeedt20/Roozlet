# Build and release

The authoritative application version is `src/rooz/__init__.py`; the Debian
changelog must match it with revision `-1`. Current artifact:
`dist/roozlet_0.1.1-1_all.deb`.

```
sudo apt install python3 python3-gi python3-cairo python3-gi-cairo gir1.2-gtk-3.0 tzdata libfontconfig1
scripts/build-deb.sh
python3 scripts/source-archive.py
(cd dist && sha256sum -c SHA256SUMS)
```

The default script validates tests/data, stages standard Debian paths and builds
with `dpkg-deb --root-owner-group` as an ordinary user. It needs no sudo, pip,
network download or native compiler. Sources, data and static fonts are platform
independent, so Architecture: all is appropriate. Native GTK/Cairo/Fontconfig
libraries are system dependencies. The output is reproducible with fixed
SOURCE_DATE_EPOCH (default 1791633600), sorted files and normalized metadata.

Standard debhelper packaging is also supplied:

```
sudo apt install debhelper dh-python
dpkg-buildpackage -us -uc -b
```

Debhelper
uses the same stage implementation. This alternative needs the listed build
dependencies; the local artifact uses the rootless fallback because debhelper
was not installed. There are no maintainer scripts or automatic launch/startup.

## Repository and licensing

Repository: https://github.com/saeedt20/Roozlet. Original application code and
documentation use the MIT license selected by the owner. Copyright and Debian
maintainer attribution are Saeed Taheri; the public GitHub noreply address is
used rather than a personal email. Third-party licenses stay unchanged.

The GitHub project and release downloads use the Roozlet name. Version 0.1.1 uses
the established Rooz application name and `rooz` CLI/package, so the new
`roozlet_0.1.1-1_all.deb` upgrades existing installations normally.
The original University PDF is excluded from source archives; retrieve it using
its provenance URL for re-verification. Never add real XDG user settings,
unrelated desktop captures, credentials or runtime logs.

CI runs on Ubuntu 24.04 using GTK distribution packages, unit/data tests, an Xvfb
smoke check and the package build. GitHub action release versions were checked
against their primary upstream release APIs during implementation. They are
pinned to immutable commits. Virtual GTK CI does not certify Xfce behavior.

The release-preparation workflow responds to `v*` tags and manual dispatch,
uploading reviewed artifacts with read-only repository permissions. Publishing
is a separate, explicitly authorized action.

For an explicitly authorized release, build and verify the artifacts, commit the
reviewed source, and wait for CI to pass. Then publish the tag and assets:

```sh
git tag -a v0.1.1 -m "Roozlet 0.1.1"
git push origin v0.1.1
gh release create v0.1.1 --repo saeedt20/Roozlet --verify-tag \
  --title "Roozlet 0.1.1 — Persian calendar for Xfce" \
  --notes-file docs/releases/v0.1.1.md \
  dist/roozlet_0.1.1-1_all.deb dist/roozlet-0.1.1-source.tar.gz dist/SHA256SUMS
```

Download the published assets and check their SHA256SUMS. Verify checksums before
installation. Future publication requires user authorization.
