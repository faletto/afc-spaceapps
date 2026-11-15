"""EPH-3: compare our Sun/Earth elevations with direct Horizons topocentric queries (spec §3.12)."""

from datetime import datetime
from pathlib import Path

import numpy as np

from . import ephemeris, geometry
from .fetch import horizons

REPO = Path(__file__).resolve().parents[2]
SITES = {  # name: (lat, lon_E)
    "Near side (0°, 0°)": (0.0, 0.0),
    "Near side (30°N, 20°E)": (30.0, 20.0),
    "Limb (0°, 90°E)": (0.0, 90.0),
    "Mid-lat south (60°S, 150°W)": (-60.0, -150.0),
    "South polar (85°S, 30°W)": (-85.0, -30.0),
    "South polar (89.7°S, 45°E)": (-89.7, 45.0),
    "South Pole (90°S)": (-90.0, 0.0),
}
DATES = ["2028-03-01", "2028-06-21", "2028-09-15", "2028-12-20"]
HOURS = 48
TOL_POLAR_DEG = 0.1  # sites poleward of 80°S: the "polar method"
TOL_GLOBAL_DEG = 1.0  # EPH-3: Moon-wide tolerance (we are far tighter in practice)


def query(target: str, lat, lon, start: str) -> np.ndarray:
    t0 = datetime.fromisoformat(start)
    stop = (t0 + np.timedelta64(HOURS, "h").astype("timedelta64[s]").astype(object)).strftime(
        "%Y-%m-%d %H:%M"
    )
    p = {
        "format": "text",
        "COMMAND": f"'{target}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'coord@301'",
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": f"'{lon},{lat},0'",
        "START_TIME": f"'{start} 00:00'",
        "STOP_TIME": f"'{stop}'",
        "STEP_SIZE": "'1h'",
        "QUANTITIES": "'4'",
        "ANG_FORMAT": "'DEG'",
        "CSV_FORMAT": "'YES'",
    }
    txt = horizons.get(p)
    body = txt.split("$$SOE", 1)[1].split("$$EOE", 1)[0].strip().splitlines()
    return np.array([[float(x) for x in ln.split(",")[3:5]] for ln in body])  # az, el


def run() -> list[dict]:
    eph = ephemeris.load()
    rows = []
    for name, (lat, lon) in SITES.items():
        for date in DATES:
            i0 = int((np.datetime64(date) - np.datetime64("2028-01-01")).astype("timedelta64[h]").astype(int))
            sl = slice(i0, i0 + HOURS + 1)
            for tgt, label in (("10", "Sun"), ("399", "Earth")):
                h = query(tgt, lat, lon, date)
                if tgt == "10":
                    el, az = geometry.sun_az_el(eph["sun_xyz"][sl], lat, lon)
                else:
                    el, az = geometry.earth_az_el(eph["earth_xyz"][sl], eph["earth_dist_m"][sl], lat, lon)
                n = min(len(h), len(el))
                d_el = np.abs(el[:n] - h[:n, 1])
                d_az = np.abs((az[:n] - h[:n, 0] + 180) % 360 - 180)
                above = h[:n, 1] > -1
                rows.append(
                    {
                        "site": name,
                        "date": date,
                        "target": label,
                        "max_el_err": d_el.max(),
                        "max_az_err": d_az[above].max() if above.any() and lat > -89.9 else float("nan"),
                        "polar": lat <= -80,
                    }
                )
    return rows


def write_report(rows, md: Path, png: Path, extra=None, cc=None) -> bool:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ok = all(r["max_el_err"] <= (TOL_POLAR_DEG if r["polar"] else TOL_GLOBAL_DEG) for r in rows)
    worst = max(r["max_el_err"] for r in rows)
    lines = [
        "# Validation: ephemeris vs JPL Horizons (EPH-3)",
        "",
        (
            f"Our Sun/Earth elevations vs direct Horizons topocentric queries (`CENTER='coord@301'`, `QUANTITIES='4'`), "
            f"{len(SITES)} sites × {len(DATES)} dates × {HOURS} h. Pass: polar sites ≤ {TOL_POLAR_DEG}°, "
            f"Moon-wide sites ≤ {TOL_GLOBAL_DEG}°. **Result: {'PASS' if ok else 'FAIL'}** (worst elevation error {worst:.4f}°)."
        ),
        "",
        "| Site | Target | Max elevation error (°) over 4 dates | Max azimuth error (°, target above horizon) |",
        "|---|---|---|---|",
    ]
    for name in SITES:
        for tgt in ("Sun", "Earth"):
            rr = [r for r in rows if r["site"] == name and r["target"] == tgt]
            az = [r["max_az_err"] for r in rr if not np.isnan(r["max_az_err"])]
            mx = max(r["max_el_err"] for r in rr)
            azt = f"{max(az):.3f}" if az else "n/a (pole / below horizon)"
            lines.append(f"| {name} | {tgt} | {mx:.4f} | {azt} |")
    md.write_text("\n".join(lines + (extra or [])) + "\n")
    ncol = 3 if cc else 1
    fig, axs = plt.subplots(1, ncol, figsize=(8 if ncol == 1 else 14, 4))
    ax = axs[0] if ncol > 1 else axs
    names = list(SITES)
    for k, (tgt, c) in enumerate((("Sun", "#e69f00"), ("Earth", "#0072b2"))):
        v = [max(r["max_el_err"] for r in rows if r["site"] == s and r["target"] == tgt) for s in names]
        ax.bar(np.arange(len(names)) + k * 0.38, v, 0.38, label=tgt, color=c)
    ax.axhline(TOL_POLAR_DEG, color="k", ls="--", lw=1, label=f"polar tolerance {TOL_POLAR_DEG}°")
    ax.set_xticks(
        np.arange(len(names)) + 0.19, [n.split(" (")[0] + "\n(" + n.split("(")[1] for n in names], fontsize=7
    )
    ax.set_ylabel("max elevation error (°)")
    ax.set_title("Lunar Listings ephemeris vs JPL Horizons")
    ax.legend(fontsize=8)
    if cc:
        a = cc["_arrays"]
        for axx, (xk, yk, ttl) in zip(
            axs[1:],
            (
                ("sun_lola", "sun_ours", "Sun visibility: ours vs NASA LOLA"),
                ("earth_lola", "earth_ours", "Earth visibility: ours vs NASA LOLA"),
            ),
            strict=True,
        ):
            axx.hexbin(a[xk], a[yk], gridsize=40, bins="log", cmap="viridis", mincnt=1)
            axx.plot([0, 1], [0, 1], "w--", lw=1)
            axx.set(xlabel="LOLA average visibility", ylabel="ours", title=ttl)
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(png, dpi=150)
    return ok


def main() -> int:
    rows = run()
    extra, cc = None, None
    work = REPO / "data" / "work" / "polar_plots.npz"
    if (
        work.exists()
        and (REPO / "data" / "raw" / "illum").exists()
        and (REPO / "data" / "raw" / "diviner").exists()
    ):
        from . import crosscheck

        cc = crosscheck.run(work)
        extra = crosscheck.markdown(cc)
        sl = crosscheck.slope_vs_ldsm()
        if sl:
            extra += crosscheck.slope_markdown(sl)
    ok = write_report(
        rows, REPO / "docs" / "validation.md", REPO / "docs" / "img" / "validation.png", extra, cc
    )
    print("EPH-3", "PASS" if ok else "FAIL", f"worst el err {max(r['max_el_err'] for r in rows):.4f} deg")
    return 0 if ok else 1
