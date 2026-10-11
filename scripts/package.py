#!/usr/bin/python3
"""Deterministic rootless staging, also used by standard debhelper rules."""

import argparse, gzip, hashlib, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rooz import __version__

VERSION = __version__ + "-1"


def stage(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    package = dest / "usr/share/rooz/rooz"
    shutil.copytree(ROOT / "src/rooz", package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(ROOT / "data/calendars", package / "data/calendars")
    shutil.copytree(ROOT / "data/fonts", package / "data/fonts")
    launcher = dest / "usr/bin/rooz"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(
        '#!/usr/bin/python3\nimport sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\nsys.path.insert(0, str(Path(__file__).resolve().parents[1] / "share/rooz"))\nfrom rooz.app import main\nraise SystemExit(main())\n'
    )
    launcher.chmod(0o755)
    for source, target in [
        ("data/rooz.desktop", "usr/share/applications/rooz.desktop"),
        ("data/icons/rooz.svg", "usr/share/icons/hicolor/scalable/apps/rooz.svg"),
        ("debian/copyright", "usr/share/doc/rooz/copyright"),
    ]:
        p = dest / target
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, p)
    doc = dest / "usr/share/doc/rooz"
    for name in ["README.md", "README.fa.md", "THIRD_PARTY_NOTICES.md", "LICENSE"]:
        shutil.copyfile(ROOT / name, doc / name)
    for name in ["DATA_SOURCES.md", "DESIGN.md", "TESTING.md", "RELEASING.md"]:
        shutil.copyfile(ROOT / "docs" / name, doc / name)
    (doc / "changelog.Debian.gz").write_bytes(
        gzip.compress((ROOT / "debian/changelog").read_bytes(), mtime=0)
    )
    man = dest / "usr/share/man/man1/rooz.1.gz"
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_bytes(gzip.compress((ROOT / "data/rooz.1").read_bytes(), mtime=0))


def build():
    changelog = (ROOT / "debian/changelog").read_text()
    if not changelog.startswith(f"rooz ({VERSION})"):
        raise SystemExit("Version mismatch")
    metadata = (ROOT / "debian/control").read_text()
    maintainer = re.search(r"^Maintainer: (.+)$", metadata, re.MULTILINE).group(1)
    homepage = re.search(r"^Homepage: (.+)$", metadata, re.MULTILINE).group(1)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    artifact = dist / f"roozlet_{VERSION}_all.deb"
    with tempfile.TemporaryDirectory(prefix="rooz-build-") as tmp:
        dest = Path(tmp)
        stage(dest)
        control = dest / "DEBIAN"
        control.mkdir()
        deps = "python3 (>= 3.9), python3-gi, python3-cairo, python3-gi-cairo, gir1.2-gtk-3.0, tzdata, libfontconfig1"
        size = sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())
        (control / "control").write_text(
            f"Package: rooz\nVersion: {VERSION}\nArchitecture: all\nSection: utils\nPriority: optional\nMaintainer: {maintainer}\nHomepage: {homepage}\nDepends: {deps}\nInstalled-Size: {(size + 1023) // 1024}\nDescription: compact offline Persian calendar for Xfce\n Rooz displays three calendars with bilingual settings and offline Iranian holidays.\n"
        )
        md5 = []
        for p in sorted(dest.rglob("*")):
            if p.is_file() and control not in p.parents:
                md5.append(f"{hashlib.md5(p.read_bytes()).hexdigest()}  {p.relative_to(dest)}")
        (control / "md5sums").write_text("\n".join(md5) + "\n")
        epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "1791633600"))
        for p in dest.rglob("*"):
            os.utime(p, (epoch, epoch))
            p.chmod(0o755 if p.is_dir() or p == dest / "usr/bin/rooz" else 0o644)
        os.utime(dest, (epoch, epoch))
        dest.chmod(0o755)
        subprocess.run(
            ["dpkg-deb", "--root-owner-group", "--build", str(dest), str(artifact)],
            check=True,
            env={**os.environ, "SOURCE_DATE_EPOCH": str(epoch)},
        )
    (dist / "SHA256SUMS").write_text(
        f"{hashlib.sha256(artifact.read_bytes()).hexdigest()}  {artifact.name}\n"
    )
    print(artifact)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage")
    args = parser.parse_args()
    stage(args.stage) if args.stage else build()
