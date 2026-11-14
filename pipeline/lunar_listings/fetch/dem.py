"""Resumable DEM download + SHA-256 verify (spec §3.1). Raw DEMs live in data/raw/ (gitignored)."""
import hashlib
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "pipeline" / "data" / "sources.yaml"
RAW = ROOT / "data" / "raw"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def fetch_all() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    spec = yaml.safe_load(SOURCES.read_text())
    for f in spec["files"]:
        dest = RAW / f["name"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.stat().st_size != f["bytes"]:
            subprocess.run(["curl", "-fL", "-C", "-", "--retry", "5", "-o", str(dest), f["url"]], check=True)
        if dest.stat().st_size != f["bytes"]:
            raise RuntimeError(f"{f['name']}: size {dest.stat().st_size} != {f['bytes']}")
        digest = _sha256(dest)
        if f["sha256"] is None:
            f["sha256"] = digest
            SOURCES.write_text(yaml.safe_dump(spec, sort_keys=False, width=200))
        elif f["sha256"] != digest:
            raise RuntimeError(f"{f['name']}: sha256 mismatch")
        print("ok", f["name"], flush=True)
