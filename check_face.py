"""Validate face designs, bezels (FACE_SPEC.md) and panels (PANEL_SPEC.md).

Usage: check_face.py designs/x.py designs/x_bezel.py panels/door.py ...
A face file defines DESIGN, a bezel file BEZEL = {"units": n, "features": [...]},
a panel file PANEL = {"name": ..., "features": [...]}.
"""
import runpy
import sys

from shapely import STRtree
from shapely.geometry import box as rect

from face_geom import SHAPES, TOL, outline, parents

U, GAP_V = 44.45 / 8, 0.3
MIN, GAP = 0.8, 0.8
ZERO_TOL = 0.03                # a "0" margin may be off by rounding
BRANDS = ("dell", "hp", "hpe", "cisco", "apc", "supermicro", "lenovo", "ubiquiti", "synology",
          "juniper", "netgear", "ibm", "poweredge", "proliant", "netapp", "nimble", "pure")
LIMITS = {"face": {"recess": (0.6, 1.3), "boss": (0.4, 1.0)},
          "bezel": {"recess": (0.4, 1.2), "boss": (0.4, 1.0), "hole": (0, 0)}}
# panels: allowed zone (u0, v0, u1, v1), allowed kinds with depth ranges, feature-count limit
PANELS = {
    "door": {"zone": (4.0, 4.0, 56.5, 228.0), "kinds": {"hole": (0, 0)}, "max": 1200},
    "door_cray": {"zone": (4.0, 4.0, 56.5, 228.0), "kinds": {"hole": (0, 0), "boss": (0.6, 0.6)}, "max": 1200},
    "kvm_deck": {"zone": (0, 0, 42.0, 46.0), "kinds": {"boss": (0.4, 0.4), "recess": (0.4, 0.4)}, "max": 150},
    "kvm_lid": {"zone": (1.5, 1.5, 41.9, 34.5), "kinds": {"boss": (0.4, 0.4), "recess": (0.4, 0.6)}, "max": 50},
    "pdu": {"zone": (1.0, 3.0, 5.2, 205.0), "kinds": {"recess": (0.6, 1.2)}, "max": 60},
}


def check_features(fs, units, where, zone=None, limits=None, max_n=400):
    errs = []
    zone = zone or (3.8, 0.8, 56.2, units * U - GAP_V - 0.8)
    limits = limits or LIMITS[where]
    area = rect(*zone).buffer(TOL)
    if len(fs) > max_n:
        errs.append(f"{len(fs)} features > {max_n}")
    for i, f in enumerate(fs):
        lim = limits.get(f.get("kind"))
        if lim is None:
            errs.append(f"#{i} kind {f.get('kind')!r} not allowed on the {where}")
            continue
        if not lim[0] - 1e-6 <= f.get("depth", 0) <= lim[1] + 1e-6:
            errs.append(f"#{i} depth {f.get('depth')} outside {lim}")
        if f["w"] < MIN - 1e-6 or f["h"] < MIN - 1e-6:
            errs.append(f"#{i} too small {f['w']}x{f['h']}")
        if f.get("shape", "rect") not in SHAPES:
            errs.append(f"#{i} shape {f.get('shape')!r} not one of {SHAPES}")
            continue
        if f.get("shape") == "poly":
            p = outline(f)
            if len(f.get("pts", ())) < 3 or not p.is_valid:
                errs.append(f"#{i} poly outline is not a simple polygon")
                continue
            if p.area - p.buffer(-MIN / 2).buffer(MIN / 2).area > 0.05 * p.area:
                errs.append(f"#{i} poly narrower than {MIN} in places")
        if abs(f.get("angle", 0) or 0) > 75:
            errs.append(f"#{i} angle {f['angle']} beyond +-75")
        if not area.contains(outline(f)):
            b = [round(x, 2) for x in outline(f).bounds]
            errs.append(f"#{i} outside zone u {zone[0]}..{zone[2]} / v {zone[1]}..{zone[3]:.2f}: bounds {b}")
    if errs:
        return errs

    polys = [outline(f) for f in fs]
    par = parents(fs)
    for i, p in enumerate(par):
        if p is None:
            continue
        if par[p] is not None:
            errs.append(f"#{i} nested two levels deep")
        if fs[i]["kind"] == "recess" and fs[i]["depth"] <= fs[p]["depth"]:
            errs.append(f"#{i} nested recess must be deeper than its parent #{p}")
        if fs[i]["kind"] == "hole":
            errs.append(f"#{i} holes can't be nested")
        # margin to every parent edge: 0 or >= 0.8 (axis-aligned pairs only)
        plain = all(not g.get("angle") and g.get("shape", "rect") == "rect" for g in (fs[i], fs[p]))
        if plain:
            a, b = fs[i], fs[p]
            for m in (a["u"] - b["u"], b["u"] + b["w"] - a["u"] - a["w"],
                      a["v"] - b["v"], b["v"] + b["h"] - a["v"] - a["h"]):
                if ZERO_TOL < m < GAP - 1e-6:  # slivers up to ZERO_TOL are rounding, they merge when sliced
                    errs.append(f"#{i} margin {m:.2f} to parent #{p} (must be 0 or >= 0.8)")
                    break
    # everything that is not parent/child must keep the gap
    tree = STRtree(polys)
    for i, p in enumerate(polys):
        for j in tree.query(p.buffer(GAP)):
            if j <= i or par[i] == j or par[j] == i:
                continue
            d = p.distance(polys[j])
            if d < GAP - 1e-6:
                errs.append(f"#{i} and #{j} gap {d:.2f} < {GAP}")
                if len(errs) > 40:
                    return errs
    return errs


def check(path):
    try:
        ns = runpy.run_path(str(path))
    except Exception as e:  # noqa: BLE001
        return [f"cannot load: {e!r}"]
    if "PANEL" in ns:
        pn = ns["PANEL"]
        rule = PANELS.get(pn.get("name"))
        if rule is None:
            return [f"unknown panel name {pn.get('name')!r}"]
        return check_features(pn["features"], None, pn["name"], rule["zone"], rule["kinds"], rule["max"])
    if "BEZEL" in ns:
        b = ns["BEZEL"]
        if b.get("units") not in (1, 2, 3, 4):
            return ["BEZEL units must be 1-4"]
        return check_features(b["features"], b["units"], "bezel")
    if "DESIGN" not in ns:
        return ["no DESIGN, BEZEL or PANEL defined"]
    d = ns["DESIGN"]
    errs = [f"missing key {k}" for k in ("name", "units", "depth", "handles", "features") if k not in d]
    if errs:
        return errs
    if any(b in d["name"].lower() for b in BRANDS):
        errs.append("brand name in design name")
    if d["units"] not in (1, 2, 3, 4):
        errs.append("units must be 1-4")
    if d["handles"] not in (True, False, "loop"):
        errs.append("handles must be True, False or 'loop'")
    if not 10 <= d["depth"] <= 105:
        errs.append("depth out of range")
    return errs or check_features(d["features"], d["units"], "face")


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        e = check(p)
        print(f"{'OK  ' if not e else 'FAIL'} {p}" + ("" if not e else "\n  " + "\n  ".join(e[:12])))
        bad += bool(e)
    sys.exit(bad)
