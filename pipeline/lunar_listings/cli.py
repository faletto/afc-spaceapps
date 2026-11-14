"""`python -m lunar_listings <stage>`."""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "app" / "public" / "data"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="lunar_listings")
    p.add_argument("stage", choices=["stub", "config", "fetch", "polar", "data", "validate"])
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
        import numpy as np

        from . import config, export, plots, pricing
        cfg = config.load()
        work = REPO / "data" / "work"
        raw = REPO / "data" / "raw"
        g = plots.build_global(cfg, work)
        pt = dict(np.load(work / "polar_plots.npz", allow_pickle=False))  # run polar_build first (make polar)
        allv = np.concatenate([g["viability"], pt["viability"]])
        cutoff = pricing.scarcity_cutoff(allv, cfg)
        hot = float(np.percentile(allv, cfg["badges"]["hot_property_pct"]))
        for t in (g, pt):  # shared scarcity cutoff across tiers
            prem = np.where(t["landmark_score"] > 0.5, cfg["price"]["apollo_premium"], 0.0)
            t["price"] = pricing.price_usd(t["viability"], cfg, prem, cutoff)
            t["rent_avg"] = pricing.rent_per_month(t["price"], cfg)
        m = export.export_global(g, cfg, a.out, work / "dem_global_32.npy", hot_cut=hot, cutoff=cutoff)
        m = export.export_polar(pt, cfg, a.out, raw, hot_cut=hot, cutoff=cutoff)
        print("exported:", m["counts"], m["tiers"], "files:", len(m["files"]), "cutoff", round(cutoff, 1))
    elif a.stage == "polar":
        from . import config, polar_build
        cfg = config.load()
        work = REPO / "data" / "work"
        if not (work / "polar_cells.npz").exists():
            polar_build.build_cells(cfg, REPO / "data" / "raw", work)
        polar_build.build_plots(cfg, REPO / "data" / "raw", work)
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
