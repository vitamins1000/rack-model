"""Shared 2D geometry for face/bezel features (FACE_SPEC_V2.md): outlines and nesting."""
from shapely import affinity
from shapely.geometry import Polygon

TOL = 0.01
SHAPES = ("rect", "diamond", "hex", "hex_h", "poly")


def _corners(f):
    """Outline points of the shape inscribed in the feature's u, v, w, h rectangle."""
    u0, v0, w, h = f["u"], f["v"], f["w"], f["h"]
    u1, v1, uc, vc = u0 + w, v0 + h, u0 + w / 2, v0 + h / 2
    shape = f.get("shape", "rect")
    if shape == "poly":     # free outline: "pts" is a list of (u, v), the box is its bounds
        return [tuple(p) for p in f["pts"]]
    if shape == "diamond":  # points at the middle of each side
        return [(uc, v0), (u1, vc), (uc, v1), (u0, vc)]
    if shape == "hex":      # pointy top and bottom, flat left/right sides
        return [(uc, v0), (u1, v0 + h / 4), (u1, v1 - h / 4), (uc, v1), (u0, v1 - h / 4), (u0, v0 + h / 4)]
    if shape == "hex_h":    # pointy left and right, flat top/bottom
        return [(u0, vc), (u0 + w / 4, v0), (u1 - w / 4, v0), (u1, vc), (u1 - w / 4, v1), (u0 + w / 4, v1)]
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def outline(f):
    """Feature footprint in face coordinates (u, v), rotated CCW-from-the-front by `angle`."""
    p = Polygon(_corners(f))
    a = f.get("angle", 0) or 0
    return affinity.rotate(p, a, origin=((f["u"] + f["w"] / 2), f["v"] + f["h"] / 2)) if a else p


def parents(features):
    """Index of the recess each feature sits inside, or None for top-level features.

    When several recesses contain a feature, the smallest one is the parent.
    """
    polys = [outline(f) for f in features]
    recesses = [(j, polys[j].buffer(TOL), polys[j].area) for j, f in enumerate(features) if f["kind"] == "recess"]
    out = []
    for i, p in enumerate(polys):
        best, best_area = None, None
        for j, q, area in recesses:
            if i == j or area <= p.area + 1e-9 or not q.contains(p):
                continue
            if best is None or area < best_area:
                best, best_area = j, area
        out.append(best)
    return out
