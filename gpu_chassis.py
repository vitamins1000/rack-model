"""Open-top 4U chassis modelled on an 8-GPU HGX A100 node, as one watertight solid."""
import pathlib
from manifold3d import Manifold
import rack_lib as L


def make_gpu_chassis(units=4, depth=100.0):
    h = units * L.U - L.GAP_V          # 21.92 body height
    hb = L.INNER_W / 2 - L.SIDE_CLEAR  # 27.0 body half width
    T = 1.2                            # wall thickness
    FLOOR = 1.0                        # floor thickness
    xi = hb - T                        # 25.8 inner half width
    yb = depth - T                     # inner face of the back wall
    OV = 0.2                           # overlap: parts standing on the floor start at z = FLOOR - OV; parts touching a wall reach OV into it. No two faces may coincide exactly.

    adds = []
    cuts = []

    # Shell
    adds.append(L.box(-hb, hb, 0, depth, 0, FLOOR))          # floor
    adds.append(L.box(-hb, -xi, 0, depth, 0, h))             # left wall
    adds.append(L.box(xi, hb, 0, depth, 0, h))               # right wall
    adds.append(L.box(-hb, hb, 0, T, 0, h))                  # front wall
    adds.append(L.box(-hb, hb, yb, depth, 0, h))             # back wall

    # Rail tongues
    for i in range(units):
        zc = (i + 0.5) * L.U - L.GAP_V / 2
        for s in (-1, 1):
            adds.append(L.rail_tongue(s, hb, zc, 1.0, depth - 0.5, L.SIDE_CLEAR))

    # Front snap pegs
    for x, z in L.snap_pegs(units):
        adds.append(L.snap_peg(x, z, -L.SNAP_L, 0.01))

    # PCIe card cage
    card_xs = []
    for i in range(14):
        xc = -24.75 + 3.8 * i
        card_xs.append(xc)
        adds.append(L.box(xc - 0.4, xc + 0.4, 2.0, 17.0, FLOOR - OV, 15.0))

    for y0 in (5.0, 12.0):
        adds.append(L.box(-xi - OV, xi + OV, y0, y0 + 2.0, 15.0 - OV, 17.0))
        for xc in card_xs:
            adds.append(L.box(xc - 0.6, xc + 0.6, y0 + 0.4, y0 + 1.6, 17.0 - OV, 18.0))

    # Motherboard
    adds.append(L.box(-xi + 0.8, xi - 0.8, 19.0, 40.0, FLOOR - OV, 1.6))
    for cx in (-10.0, 10.0):
        # CPU heatsinks
        adds.append(L.box(cx - 4.0, cx + 4.0, 25.5, 33.5, 1.6 - OV, 6.0))
        # DIMMs
        for s in (-1, 1):
            for k in (0, 1, 2):
                dx = cx + s * (5.4 + 1.6 * k)
                adds.append(L.box(dx - 0.4, dx + 0.4, 25.0, 34.0, 1.6 - OV, 3.2))

    # GPU tray
    adds.append(L.box(-xi - OV, xi + OV, 41.0, 84.0, FLOOR - OV, 2.5))
    gpu_modules = []
    for cx in (-5.8, 5.8):
        for r in range(4):
            y0 = 44.0 + 10.0 * r
            gpu_modules.append((cx, y0))
            adds.append(L.box(cx - 5.2, cx + 5.2, y0, y0 + 9.0, 2.5 - OV, 13.0))

    # Left busbar
    for bx in (-22.0, -19.0):
        adds.append(L.box(bx - 0.6, bx + 0.6, 42.0, 83.0, 2.5 - OV, 4.5))
    for r in range(4):
        adds.append(L.box(-23.5, -17.5, 46.0 + 10.0 * r, 48.0 + 10.0 * r, 2.5 - OV, 5.5))

    # Right side heatsinks
    for y0 in (44.0, 64.0):
        adds.append(L.box(13.0, 23.0, y0, y0 + 18.0, 2.5 - OV, 8.0))

    # Rear heatsink row
    rear_xs = []
    for i in range(4):
        x0 = -22.0 + 12.0 * i
        rear_xs.append(x0)
        adds.append(L.box(x0, x0 + 9.0, 85.0, 90.5, FLOOR - OV, 9.0))

    # Fan wall
    fan_ranges = [(-xi - OV, -16.0), (-15.2, -5.6), (-4.8, 4.8), (5.6, 15.2), (16.0, xi + OV)]
    for x0, x1 in fan_ranges:
        adds.append(L.box(x0, x1, 91.5, yb + OV, FLOOR - OV, 17.0))

    # Cuts

    # A. CPU heatsink fin grooves
    for cx in (-10.0, 10.0):
        for k in range(4):
            gx = cx - 2.4 + 1.6 * k
            cuts.append(L.box(gx - 0.4, gx + 0.4, 25.0, 34.0, 4.5, 7.0))

    # B. GPU module shroud slots
    for cx, y0 in gpu_modules:
        for d in (-3.0, 0.0, 3.0):
            cuts.append(L.box(cx + d - 0.6, cx + d + 0.6, y0 + 1.5, y0 + 7.5, 12.2, 14.0))

    # C. Right heatsink grooves
    for y0 in (44.0, 64.0):
        for k in range(8):
            gy = y0 + 2.0 + 2.0 * k
            cuts.append(L.box(12.5, 23.5, gy - 0.4, gy + 0.4, 6.0, 9.0))

    # D. Rear heatsink grooves
    for x0 in rear_xs:
        for k in range(4):
            gx = x0 + 1.5 + 2.0 * k
            cuts.append(L.box(gx - 0.4, gx + 0.4, 84.5, 91.0, 7.0, 10.0))

    # E. Round fan recesses in the outside of the back wall
    for xc in (-20.9, -10.4, 0.0, 10.4, 20.9):
        cuts.append(Manifold.cylinder(1.6, 3.6, 3.6, 48).rotate([-90, 0, 0]).translate([xc, depth - 0.6, 9.0]))

    return L.union_all(adds) - L.union_all(cuts)


if __name__ == "__main__":
    import pathlib
    m = make_gpu_chassis()
    bb = m.bounding_box()
    print("volume", round(m.volume(), 1), "bbox", [round(v, 2) for v in bb], "bodies", len(m.decompose()))
    out = pathlib.Path(__file__).parent / "stl" / "chassis" / "chassis_4u_100mm_gpu_open.stl"
    t = L.export_stl(m, str(out))
    print("watertight", t.is_watertight, "extents", t.extents.round(2))
