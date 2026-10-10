#!/usr/bin/python3
"""Create a deterministic publication-review source bundle, without private files."""

import gzip, hashlib, io, os, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rooz import __version__

DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
target = DIST / f"rooz-{__version__}-source.tar.gz"
epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "1791633600"))
EXCLUDED = {".git", "dist", "build", "__pycache__", ".ruff_cache", ".pytest_cache"}
with (
    target.open("wb") as out,
    gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=epoch) as compressed,
    tarfile.open(fileobj=compressed, mode="w") as archive,
):
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if (
            not p.is_file()
            or any(part in EXCLUDED or part.startswith(".venv") for part in rel.parts)
            or p.suffix.lower() in (".pdf", ".pyc", ".deb")
            or rel.parts[:2] == ("debian", "rooz")
        ):
            continue
        entry = tarfile.TarInfo(f"rooz-{__version__}/{rel}")
        data = p.read_bytes()
        entry.size = len(data)
        entry.mtime = epoch
        entry.mode = 0o755 if os.access(p, os.X_OK) else 0o644
        entry.uid = entry.gid = 0
        archive.addfile(entry, io.BytesIO(data))
assets = sorted([*DIST.glob("*.deb"), target])
(DIST / "SHA256SUMS").write_text(
    "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in assets)
)
print(target)
