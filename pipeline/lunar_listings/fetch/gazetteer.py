"""IAU/USGS lunar nomenclature -> pipeline/data/landmarks.csv (spec §3.1/§3.8), plus hand-curated sites.

Curated positions (landing sites; Artemis III candidate regions) are approximate (about +/-0.5 deg) and marked so.
Sources: USGS Gazetteer of Planetary Nomenclature (planetarynames.wr.usgs.gov); NASA Artemis III regions (2022).
"""

import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "gaz"
OUT = ROOT / "pipeline" / "data" / "landmarks.csv"
URL = "https://planetarynames.wr.usgs.gov/shapefiles/MOON_nomenclature_center_pts.zip"

KEEP = {
    "Mons, montes": "mons",
    "Dorsum, dorsa": "dorsum",
    "Mare, maria": "mare",
    "Vallis, valles": "vallis",
    "Promontorium, promontoria": "promontorium",
    "Rupes, rupēs": "rupes",
    "Lacus, lacūs": "lacus",
    "Sinus, sinūs": "sinus",
}
MIN_CRATER_KM = 20.0
MAJOR_CRATER_KM = 50.0

# (name, type, lat, lon_east, fame_class)
CURATED = [
    ("Apollo 11", "apollo", 0.674, 23.473, "apollo_artemis"),
    ("Apollo 12", "apollo", -3.012, -23.422, "apollo_artemis"),
    ("Apollo 14", "apollo", -3.645, -17.471, "apollo_artemis"),
    ("Apollo 15", "apollo", 26.132, 3.634, "apollo_artemis"),
    ("Apollo 16", "apollo", -8.973, 15.501, "apollo_artemis"),
    ("Apollo 17", "apollo", 20.191, 30.772, "apollo_artemis"),
    ("Chang'e 4", "robotic", -45.46, 177.59, "other"),
    ("Chang'e 3", "robotic", 44.12, -19.51, "other"),
    ("Chang'e 5", "robotic", 43.06, -51.92, "other"),
    ("Chandrayaan-3", "robotic", -69.37, 32.32, "other"),
    ("Luna 9", "robotic", 7.08, -64.37, "other"),
    ("Luna 16", "robotic", -0.68, 56.30, "other"),
    ("Luna 17 / Lunokhod 1", "robotic", 38.28, -35.0, "other"),
    ("Luna 21 / Lunokhod 2", "robotic", 25.99, 30.9, "other"),
    ("Luna 24", "robotic", 12.75, 62.2, "other"),
    ("Surveyor 1", "robotic", -2.47, -43.34, "other"),
    ("Surveyor 3", "robotic", -3.02, -23.42, "other"),
    ("Surveyor 5", "robotic", 1.46, 23.20, "other"),
    ("Surveyor 6", "robotic", 0.47, -1.37, "other"),
    ("Surveyor 7", "robotic", -40.88, -11.51, "other"),
    # Informal ridge: position checked against the 80 m LOLA DEM (high ground); approximate (+/-0.5 deg)
    ("Connecting Ridge (informal; Artemis III candidate)", "artemis", -89.45, -129.0, "apollo_artemis"),
]


# IAU feature centres used for Artemis III candidate regions (names from NASA's 2022/2024 announcements)
ARTEMIS_FEATURES = {
    "Shackleton": "crater",
    "Faustini": "crater",
    "Haworth": "crater",
    "Nobile": "crater",
    "de Gerlache": "crater",
    "Cabeus": "crater",
    "Mons Malapert": "mons",
    "Mons Mouton": "mons",
}


def build() -> int:
    import shapefile

    RAW.mkdir(parents=True, exist_ok=True)
    z = RAW / "moon.zip"
    if not z.exists():
        subprocess.run(["curl", "-fsSL", "-o", str(z), URL], check=True)
        subprocess.run(["unzip", "-oq", str(z), "-d", str(RAW)], check=True)
    rows = []
    r = shapefile.Reader(str(RAW / "MOON_nomenclature_center_pts.shp"))
    for rec in r.records():
        if rec["approval"] != "Adopted by IAU":
            continue
        t, d = rec["type"], float(rec["diameter"] or 0)
        lon = rec["center_lon"]
        lon = lon - 360 if lon > 180 else lon
        if t.startswith("Crater") and d >= MIN_CRATER_KM:
            rows.append(
                (
                    rec["clean_name"],
                    "crater",
                    rec["center_lat"],
                    lon,
                    d,
                    "major_crater" if d >= MAJOR_CRATER_KM else "other",
                )
            )
        elif t in KEEP:
            rows.append((rec["clean_name"], KEEP[t], rec["center_lat"], lon, d, "other"))
    for n, t, la, lo, d, _ in list(rows):  # IAU centres of the Artemis III candidate-region features
        if ARTEMIS_FEATURES.get(n) == t:
            rows.append((f"Artemis III region: {n}", "artemis", la, lo, d, "apollo_artemis"))
    rows += [(n, t, la, lo, 0.0, f) for n, t, la, lo, f in CURATED]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "type", "lat", "lon", "diameter_km", "fame_class"])
        for n, t, la, lo, d, fc in rows:
            w.writerow([n, t, f"{la:.4f}", f"{lo:.4f}", f"{d:.1f}", fc])
    return len(rows)
