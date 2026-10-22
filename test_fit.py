"""Fit-test kit: a 3U slice of the rack plus test sleds. Usage: .venv/bin/python test_fit.py

The slice uses the same wall, groove and rear-panel geometry as rack_42u and
prints in the same orientation (on its back), so a sled that slides nicely here
will slide the same way in the full rack.
"""
import pathlib

import rack_lib as L
from rack_lib import box, union_all

OUT = pathlib.Path(__file__).parent / "stl" / "fit_test"
OUT.mkdir(parents=True, exist_ok=True)

UNITS = 3
FLOOR = ROOF = 3.0
# sleds: (file name, units, side clearance, dots on the face)
SLEDS = [("sled_1u_tight_1dot", 1, 0.25, 1),
         ("sled_1u_nominal_2dots", 1, L.SIDE_CLEAR, 2),
         ("sled_1u_loose_3dots", 1, 0.45, 3),
         ("sled_2u_nominal", 2, L.SIDE_CLEAR, 0)]
SLED_DEPTH = 95.0


def slot_z(unit):
    return FLOOR + 0.2 + (unit - 1) * L.U


def make_slice():
    hw_in, hw_out = L.INNER_W / 2, L.OUTER_W / 2
    depth = L.INNER_D + L.REAR_T
    top = FLOOR + UNITS * L.U + 0.4
    solid = union_all([
        box(-hw_out, -hw_in, 0, depth, 0, top + ROOF),
        box(hw_in, hw_out, 0, depth, 0, top + ROOF),
        box(-hw_out, hw_out, L.INNER_D, depth, 0, top + ROOF),
        box(-hw_out, hw_out, 0, depth, 0, FLOOR),
        box(-hw_out, hw_out, 0, depth, top, top + ROOF),
    ])
    cuts = []
    for u in range(1, UNITS + 1):
        zc = slot_z(u) + L.U / 2
        z0, z1 = zc - L.GROOVE_H / 2, zc + L.GROOVE_H / 2
        cuts.append(box(-hw_in - L.GROOVE_DEPTH, -hw_in + 0.01, -1, L.INNER_D + 0.01, z0, z1))
        cuts.append(box(hw_in - 0.01, hw_in + L.GROOVE_DEPTH, -1, L.INNER_D + 0.01, z0, z1))
    return solid - union_all(cuts)


def dots(n):
    """n raised 1.6 mm square dots centred on a 1U face, to tell the sleds apart."""
    v = (L.U - L.GAP_V) / 2 - 0.8
    start = 30 - (n * 1.6 + (n - 1) * 1.6) / 2
    return [{"kind": "boss", "u": start + i * 3.2, "v": v, "w": 1.6, "h": 1.6, "depth": 0.8}
            for i in range(n)]


# bezel fit: a short 1U stub with ear pegs plus three bezels at different peg clearances
BEZEL_TESTS = [("bezel_tight_1dot", 0.08, 1), ("bezel_nominal_2dots", L.PEG_CLEAR, 2),
               ("bezel_loose_3dots", 0.16, 3)]


def bezel_dots(n):
    """Same dots as the sleds, but raised on the bezel front."""
    return [dict(f, depth=0.6) for f in dots(n)]


# bezel pocket coupons: the right ear end of the 3U bezel, tried on an already printed front's real pegs
COUPONS = [
    ("bezel_coupon_000_1dot", 0.00, 1),
    ("bezel_coupon_003_2dots", 0.03, 2),
    ("bezel_coupon_006_3dots", 0.06, 3),
    ("bezel_coupon_009_4dots", 0.09, 4),
]

def coupon_dots(n):
    """Return n dot dicts in a row."""
    return [{"kind": "boss", "u": 46.5 + i * 3.2, "v": 7.38, "w": 1.6, "h": 1.6, "depth": 0.6} for i in range(n)]


if __name__ == "__main__":
    rack = make_slice()
    t = L.export_stl(rack, OUT / "rack_slice_3u.stl", lay_on_back=True)
    print(f"rack_slice_3u   print size {t.extents.round(1)}  watertight {t.is_watertight}")
    for name, units, clear, n in SLEDS:
        m = L.make_server(units, SLED_DEPTH, dots(n), side_clear=clear)
        for u in range(1, UNITS - units + 2):  # must slide into every slot it can use
            for drop in (0.0, 0.15):
                hit = (rack ^ m.translate([0, 0, slot_z(u) - drop])).volume()
                assert hit < 1e-6, f"{name} collides in U{u} (drop {drop}): {hit}"
        t = L.export_stl(m, OUT / f"{name}.stl")
        print(f"{name:24s} clearance {clear:.2f}/side  size {t.extents.round(1)}  watertight {t.is_watertight}")
    stub = L.make_server(1, 12, handles=False)
    L.export_stl(stub, OUT / "bezel_peg_stub_1u.stl")
    for name, clear, n in BEZEL_TESTS:
        b = L.make_bezel(1, bezel_dots(n), peg_clear=clear, face_t=L.FACE_T)
        assert (b ^ stub).volume() < 1e-6, name
        t = L.export_stl(b, OUT / f"{name}.stl", lay_on_back=True)
        print(f"{name:24s} peg clearance {clear:.2f}/side  size {t.extents.round(1)}  watertight {t.is_watertight}")
    plate3 = L.make_plate(3, handles=False)
    for name, clear, n in COUPONS:
        b = L.make_bezel(3, coupon_dots(n), peg_clear=clear) ^ box(15, 31, -20, 5, -1, 20)
        assert (b ^ plate3).volume() < 1e-6, name
        t = L.export_stl(b, OUT / f"{name}.stl", lay_on_back=True)
        print(f"{name:24s} peg clearance {clear:.2f}/side  size {t.extents.round(1)}  watertight {t.is_watertight}")
