import hashlib
import json

import numpy as np
import pytest

from lunar_listings import contract, stub


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    stub.write_stub(d)
    return d


def test_manifest(out):
    m = json.loads((out / "manifest.json").read_text())
    assert m["horizon"]["offset_deg"] < 0
    assert m["contract_version"] == 2 and m["counts"]["global"] == 64800 and m["counts"]["polar"] > 50_000
    for f in m["files"][:20]:
        assert hashlib.sha256((out / f["path"]).read_bytes()).hexdigest() == f["sha256"]


@pytest.mark.parametrize("tier", ["global", "polar"])
def test_cols_roundtrip(out, tier):
    meta = json.loads((out / tier / "cols.json").read_text())
    buf = (out / tier / "cols.bin").read_bytes()
    assert len(meta["bounds"]) == 4 and "type" in meta["projection"]
    n = meta["rows"]
    got = {
        c["name"]: np.frombuffer(
            buf, dtype=np.dtype(c["dtype"]).newbyteorder("<"), count=n, offset=c["offset"]
        )
        for c in meta["columns"]
    }
    assert [c["name"] for c in meta["columns"]] == [c[0] for c in contract.COLUMNS]
    assert got["viability"].max() <= 100 and got["price"].min() >= 5000
    # tile/row_in_tile consistent with detail files and horizon sizes
    for t in np.unique(got["tile"]):
        rows = (got["tile"] == t).sum()
        tx, ty = int(t) % 16, int(t) // 16
        assert len(json.loads((out / tier / "detail" / f"{tx}_{ty}.json").read_text())) == rows
        assert got["row_in_tile"][got["tile"] == t].max() == rows - 1
        if tier == "polar":
            assert (out / tier / "horizon" / f"{tx}_{ty}.bin").stat().st_size == rows * 180


def test_ephemeris(out):
    a = np.fromfile(out / "ephemeris.bin", dtype="<f4")
    assert a.size == 8784 * 8
    assert np.allclose(np.linalg.norm(a[: 8784 * 3].reshape(-1, 3), axis=1), 1, atol=1e-5)
