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
    p.add_argument("--force", action="store_true")
    a = p.parse_args(argv)
    if a.stage == "stub":
        import json

        from . import stub
        mf = a.out / "manifest.json"
        if mf.exists() and "real" in json.loads(mf.read_text()).get("tiers", {}).values() and not a.force:
            print("refusing to overwrite real data with stub; pass --force", file=sys.stderr)
            return 1
        stub.write_stub(a.out)
    elif a.stage == "data":
        from . import config, export, plots
        cfg = config.load()
        work = REPO / "data" / "work"
        tab = plots.build_global(cfg, work)
        m = export.export_global(tab, cfg, a.out, work / "dem_global_32.npy")
        print("exported global:", m["counts"], "files:", len(m["files"]))
    elif a.stage == "config":
        from . import config
        config.export(config.load(), a.out / "config.json")
    elif a.stage == "fetch":
        from .fetch import run
        run.fetch_all()
    elif a.stage == "validate":
        from . import validate
        return validate.main()
    else:
        print(f"stage '{a.stage}' not implemented yet", file=sys.stderr)
        return 2
    return 0
