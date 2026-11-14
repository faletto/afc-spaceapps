"""`python -m lunar_listings <stage>`."""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "app" / "public" / "data"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="lunar_listings")
    p.add_argument("stage", choices=["stub", "config", "fetch", "data", "validate"])
    p.add_argument("--out", type=Path, default=OUT)
    a = p.parse_args(argv)
    if a.stage == "stub":
        from . import stub
        stub.write_stub(a.out)
    elif a.stage == "config":
        from . import config
        config.export(config.load(), a.out / "config.json")
    elif a.stage == "fetch":
        from .fetch import run
        run.fetch_all()
    else:
        print(f"stage '{a.stage}' not implemented yet", file=sys.stderr)
        return 2
    return 0
