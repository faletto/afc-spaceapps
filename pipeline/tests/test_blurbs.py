import yaml

from lunar_listings import blurbs

BASE = dict(sunlit=0.5, earth=0.5, land="highlands", ice_km=99.0, tmin_k=95.0, tmax_k=300.0, slope_deg=5.0, viability=40.0,
            safe=1, dark_h=100.0, polar=1, apollo_km=999.0, nearby="")


def test_deterministic_and_condition_driven():
    f = dict(BASE, sunlit=0.9, land="peak_of_light")
    assert blurbs.blurb("SP-0001-0002", f) == blurbs.blurb("SP-0001-0002", f)
    assert "Peak" in blurbs.blurb("SP-0001-0002", f) or "peak" in blurbs.blurb("SP-0001-0002", f).lower() or "Bright" in blurbs.blurb("SP-0001-0002", f)
    assert "buildable" in blurbs.blurb("x", dict(BASE, safe=0))
    assert "ice" in blurbs.blurb("y", dict(BASE, ice_km=0.5, safe=1)).lower() or "PSR" in blurbs.blurb("y", dict(BASE, ice_km=0.5))


def test_every_template_renders_and_ids_vary():
    t = yaml.safe_load(blurbs.PATH.read_text())
    assert 20 <= len(t["lead"]) + len(t["extra"]) <= 30
    out = {blurbs.blurb(f"G-{i:03d}-000", dict(BASE, sunlit=0.75, earth=0.99, land="crater_rim", ice_km=0.5, nearby="Tycho",
                                               apollo_km=10.0, dark_h=500.0, tmax_k=390.0)) for i in range(60)}
    assert len(out) > 1 and all("{" not in s for s in out)


def test_why_line():
    assert blurbs.why({"power": 0.9, "comms": 0.8, "safety": 0.3}) == "Priced up for abundant sunlight and excellent Earth contact"
    assert blurbs.why({"power": 0.1, "comms": 0.8}) == "Priced up for excellent Earth contact, down for long nights"
    assert blurbs.why({"power": 0.1, "comms": 0.3}) == "Priced down for long nights"
    assert blurbs.why({"power": 0.3, "comms": 0.3}) == "Priced as a typical lunar lot"
