"""Core geometry for a 1:8 scale 42U rack and slide-in servers.

Coordinates (mm): X = width (0 at rack centre), Y = depth (front face of the
rack side walls at y=0, +Y towards the back), Z = up.
All solids are built with manifold3d, so exported STLs are always watertight.
"""
from manifold3d import CrossSection, FillRule, Manifold
import numpy as np
import trimesh

SCALE = 8.0
U = 44.45 / SCALE            # 5.556 mm per rack unit
RACK_UNITS = 42

# --- fit / printability ------------------------------------------------------
GAP_V = 0.3                  # vertical gap between stacked servers
SIDE_CLEAR = 0.35            # server body to rack wall, each side
MIN_FEATURE = 0.8            # smallest printable wall/rib/gap (2 lines @ 0.4 nozzle)

# --- server chassis -----------------------------------------------------------
BODY_W = 54.0                # 434 mm real chassis width
FACE_W = 60.0                # 482.6 mm real 19" face incl. ears
FACE_T = 2.0                 # one-piece servers (fit-test sleds only)
PLATE_T = 4.0                # snap-on front plate thickness (sits in front of the rack)
SNAP_L = 2.0                 # chassis pegs reach this far into the front plate (same as bezel pegs)
SNAP_X = 20.0                # chassis pegs sit this far left/right of centre
EAR_W = (FACE_W - BODY_W) / 2  # 3 mm ears each side

# bezel pegs on the ears (used when a design has handles=False)
PEG_W, PEG_H, PEG_L = 2.2, 3.0, 3.2
PEG_CLEAR = 0.12             # per side: chassis pegs into the front plate pockets (snap-fit test)
BEZEL_PEG_CLEAR = 0.0        # per side: bezel pockets on the front's upright ear pegs (bezel coupon test)
BEZEL_GAP = 1.2              # air gap between face plate and bezel (clears 1.0 bosses)
BEZEL_T = 3.0
BEZEL_CHAMFER = 0.5          # must differ from the 0.8 feature margin, or edges coincide

# loop handles (handles="loop"): bar 1.2 thick standing LOOP_OUT proud on LOOP_POST tall standoffs
LOOP_OUT, LOOP_BAR, LOOP_POST = 2.6, 1.2, 1.5

TONGUE_OUT = 1.2             # rail tongue sticks out of the server side
TONGUE_H = 1.6

# --- rack ---------------------------------------------------------------------
WALL = 8.0                   # side wall thickness (slicer infill keeps it light)
INNER_W = BODY_W + 2 * SIDE_CLEAR
OUTER_W = INNER_W + 2 * WALL
GROOVE_DEPTH = 1.6           # into the wall
GROOVE_H = 2.2
INNER_D = 110.0              # front of walls to rear panel
REAR_T = 3.0
PLINTH_H = 10.0
TOP_H = 6.0
CAP_LIP = 3.0                # top/plinth stick out in front of the walls
BAY_H = RACK_UNITS * U + 0.4
RACK_H = PLINTH_H + BAY_H + TOP_H


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from min/max corners."""
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def union_all(parts):
    parts = [p for p in parts if p is not None]
    return Manifold.batch_boolean(parts, manifold3d.OpType.Add) if len(parts) > 1 else parts[0]


import manifold3d  # noqa: E402  (needed for OpType above)


def slot_z(unit):
    """Bottom z of rack unit `unit` (1 = lowest)."""
    return PLINTH_H + 0.2 + (unit - 1) * U


# ============================================================================ rack
def make_rack(ticks=True):
    hw_in, hw_out = INNER_W / 2, OUTER_W / 2
    depth = INNER_D + REAR_T
    top_z = PLINTH_H + BAY_H
    solids = [
        box(-hw_out, -hw_in, 0, depth, PLINTH_H, top_z),           # left wall
        box(hw_in, hw_out, 0, depth, PLINTH_H, top_z),             # right wall
        box(-hw_out, hw_out, INNER_D, depth, PLINTH_H, top_z),     # rear panel
        box(-hw_out, hw_out, -CAP_LIP, depth, 0, PLINTH_H),        # plinth
        box(-hw_out, hw_out, -CAP_LIP, depth, top_z, RACK_H),      # top cap
    ]
    rack = union_all(solids)

    cuts = []
    # rail grooves, one per U, both walls, open at the front
    for u in range(1, RACK_UNITS + 1):
        zc = slot_z(u) + U / 2
        z0, z1 = zc - GROOVE_H / 2, zc + GROOVE_H / 2
        cuts.append(box(-hw_in - GROOVE_DEPTH, -hw_in + 0.01, -1, INNER_D + 0.01, z0, z1))
        cuts.append(box(hw_in - 0.01, hw_in + GROOVE_DEPTH, -1, INNER_D + 0.01, z0, z1))
    # engraved U ticks on the wall fronts every 5U (outer part not hidden by ears)
    for u in range(1, RACK_UNITS + 1, 5) if ticks else ():
        z = slot_z(u) + 0.1
        for s in (-1, 1):
            x_in, x_out = s * (FACE_W / 2 + 0.6), s * (hw_out - 1.0)
            cuts.append(box(min(x_in, x_out), max(x_in, x_out), -1, 0.6, z, z + 0.8))
    # rear vent slots (through), 2 mm wide
    for col in range(-5, 6):
        x = col * 4.5
        for z0 in np.arange(PLINTH_H + 12, top_z - 30, 28):
            cuts.append(box(x - 1.0, x + 1.0, INNER_D - 1, depth + 1, z0, z0 + 22))
    # plinth: front vent recess and feet (cut-outs leave 8 mm corner legs)
    cuts.append(box(-hw_out + 8, hw_out - 8, -CAP_LIP - 1, depth + 1, -1, 3))
    cuts.append(box(-hw_out - 1, hw_out + 1, -CAP_LIP + 8, depth - 8, -1, 3))
    for x in np.arange(-24, 25, 4):
        cuts.append(box(x - 1.0, x + 1.0, -CAP_LIP - 1, -CAP_LIP + 1.0, 4.5, 8))
    # top cap: cable entry slot (big, printable)
    cuts.append(box(-15, 15, INNER_D - 18, INNER_D - 6, top_z - 1, RACK_H + 1))
    return rack - union_all(cuts)


# ========================================================================= servers
def rail_tongue(s, hb, zc, y0, y1, side_clear=SIDE_CLEAR):
    """Rail tongue on side s (+1 right, -1 left) of a body whose side is at x = s * hb, centred at zc.

    Servers print on their bottom, so a flat underside would be a 1.2 mm ledge in mid-air that droops
    and strings. The underside is a 45 degree slope instead. It starts `side_clear` lower at the body,
    so it crosses the rack wall face (the groove edge) where the old flat bottom was: same rest height.
    """
    bot, top = zc - TONGUE_H / 2, zc + TONGUE_H / 2
    root = bot - side_clear
    d = [(hb - 0.01, root - 0.01), (hb + TONGUE_OUT, root + TONGUE_OUT), (hb + TONGUE_OUT, top), (hb - 0.01, top)]
    pts = [(s * x, z) for x, z in (d if s > 0 else d[::-1])]
    m = Manifold.extrude(CrossSection([pts], FillRule.NonZero), y1 - y0)
    return m.rotate([90, 0, 0]).translate([0, y1, 0])


def make_server(units, depth, features=(), handles=True, side_clear=SIDE_CLEAR):
    """Chassis for a `units`-U server.

    Local origin: x = 0 at centre, y = 0 at the back of the face plate (it sits
    against the rack wall fronts), z = 0 at the server bottom.
    `features` come from a face design: dicts in face coordinates (u from the
    left edge of the 60 mm face, v from the bottom), see FACE_SPEC.md.
    `side_clear` other than SIDE_CLEAR is only for fit-test sleds.
    """
    h = units * U - GAP_V
    hb = INNER_W / 2 - side_clear
    solids = [
        box(-FACE_W / 2, FACE_W / 2, -FACE_T, 0, 0, h),     # face plate + ears
        box(-hb, hb, 0, depth, 0, h),                       # body
    ]
    # rail tongues: one per U, centred where the rack groove is
    for i in range(units):
        zc = (i + 0.5) * U - GAP_V / 2
        for s in (-1, 1):
            solids.append(rail_tongue(s, hb, zc, 1.0, depth - 0.5, side_clear))
    hh = min(h - 1.6, 12.0)
    if handles == "loop":  # loop handles: a front bar on two standoffs, with a finger gap behind it
        for s in (-1, 1):
            xc = s * (FACE_W / 2 - EAR_W / 2)
            z0, z1 = h / 2 - hh / 2, h / 2 + hh / 2
            solids.append(box(xc - 0.9, xc + 0.9, -FACE_T - LOOP_OUT, -FACE_T + 0.01, z0, z1))
            if hh - 2 * LOOP_POST >= 1.0:  # too short (1U): leave the handle solid
                solids[-1] = solids[-1] - box(xc - 1, xc + 1, -FACE_T - LOOP_OUT + LOOP_BAR, -FACE_T + 0.02,
                                              z0 + LOOP_POST, z1 - LOOP_POST)
    elif handles:  # raised grips on the ears, for pulling the server out
        for s in (-1, 1):
            xc = s * (FACE_W / 2 - EAR_W / 2)
            solids.append(box(xc - 0.9, xc + 0.9, -FACE_T - 1.5, -FACE_T + 0.01,
                              h / 2 - hh / 2, h / 2 + hh / 2))
    else:  # bezel pegs on the ears instead of handles
        for s in (-1, 1):
            xc = s * (FACE_W / 2 - EAR_W / 2)
            solids.append(box(xc - PEG_W / 2, xc + PEG_W / 2, -FACE_T - PEG_L, -FACE_T + 0.01,
                              h / 2 - PEG_H / 2, h / 2 + PEG_H / 2))
    return apply_features(union_all(solids), features, front_y=-FACE_T)


def feature_prism(f, y0, y1, origin=(-FACE_W / 2, 0.0)):
    """Feature outline (face coords, any shape/angle) as a solid spanning y0..y1.

    `origin` is where u = 0, v = 0 sits in x, z.
    """
    from face_geom import outline
    pts = [(u + origin[0], v + origin[1]) for u, v in list(outline(f).exterior.coords)[:-1]]
    m = Manifold.extrude(CrossSection([pts], FillRule.NonZero), y1 - y0)
    # extruded along +z with the outline in x/y: turn so outline-y -> z and z -> -y
    return m.rotate([90, 0, 0]).translate([0, y1, 0])


def apply_features(m, features, front_y, through=None, origin=(-FACE_W / 2, 0.0)):
    """Cut recesses/holes into and add bosses onto the surface at y=front_y (facing -Y).

    Nested features (FACE_SPEC.md) sit on their parent recess floor. `through` is the
    y of the back surface, used for holes. `origin` is where u = 0, v = 0 sits in x, z.
    """
    from face_geom import parents
    features = list(features)
    par = parents(features) if features else []
    cuts, adds = [], []
    for f, p in zip(features, par):
        base = front_y + (features[p]["depth"] if p is not None else 0)
        if f["kind"] == "recess":
            cuts.append(feature_prism(f, front_y - 1, front_y + f["depth"], origin))
        elif f["kind"] == "hole":
            cuts.append(feature_prism(f, front_y - 1, through + 1, origin))
        elif f["kind"] == "boss":  # reaches 0.5 into the material below so it's fused
            adds.append(feature_prism(f, base - f["depth"], base + 0.5, origin))
    if cuts:
        m = m - union_all(cuts)
    if adds:
        m = union_all([m] + adds)
    return m


# ============================================================ chassis + snap-on front
def snap_pegs(units):
    """(x, z) centres of the pegs that hold a front plate on its chassis."""
    h = units * U - GAP_V
    zs = [h / 2] if units == 1 else [0.5 * U - GAP_V / 2, (units - 0.5) * U - GAP_V / 2]
    return [(s * SNAP_X, z) for z in zs for s in (-1, 1)]


def snap_peg(x, z, y0, y1, grow=0.0):
    """Chassis peg (or its pocket, grown by `grow`) from y0 to y1.

    The peg sticks out sideways when the chassis prints, so its underside is a 45 degree V
    instead of a flat: a flat underside sags and then won't enter the pocket.
    """
    w, top = PEG_W / 2 + grow, PEG_H / 2 + grow
    tip = -(PEG_H / 2 + grow * 2 ** 0.5)
    pts = [(x - w, z + top), (x - w, z + tip + w), (x, z + tip), (x + w, z + tip + w), (x + w, z + top)]
    m = Manifold.extrude(CrossSection([pts], FillRule.NonZero), y1 - y0)
    return m.rotate([90, 0, 0]).translate([0, y1, 0])


def make_chassis(units, depth, side_clear=SIDE_CLEAR):
    """Generic chassis: body, rail tongues and front pegs. Any front plate of the same height fits."""
    h = units * U - GAP_V
    hb = INNER_W / 2 - side_clear
    solids = [box(-hb, hb, 0, depth, 0, h)]
    for i in range(units):
        zc = (i + 0.5) * U - GAP_V / 2
        for s in (-1, 1):
            solids.append(rail_tongue(s, hb, zc, 1.0, depth - 0.5, side_clear))
    for x, z in snap_pegs(units):
        solids.append(snap_peg(x, z, -SNAP_L, 0.01))
    return union_all(solids)


def ear_hardware(h, front, handles):
    """Handles or bezel pegs on the two ears of a face whose front surface is at y=front."""
    solids = []
    hh = min(h - 1.6, 12.0)
    for s in (-1, 1):
        xc = s * (FACE_W / 2 - EAR_W / 2)
        z0, z1 = h / 2 - hh / 2, h / 2 + hh / 2
        if handles == "loop":  # a front bar on two standoffs, with a finger gap behind it
            bar = box(xc - 0.9, xc + 0.9, front - LOOP_OUT, front + 0.01, z0, z1)
            if hh - 2 * LOOP_POST >= 1.0:  # too short (1U): leave the handle solid
                bar = bar - box(xc - 1, xc + 1, front - LOOP_OUT + LOOP_BAR, front + 0.02,
                                z0 + LOOP_POST, z1 - LOOP_POST)
            solids.append(bar)
        elif handles:  # raised grips for pulling the server out
            solids.append(box(xc - 0.9, xc + 0.9, front - 1.5, front + 0.01, z0, z1))
        else:  # bezel pegs
            solids.append(box(xc - PEG_W / 2, xc + PEG_W / 2, front - PEG_L, front + 0.01,
                              h / 2 - PEG_H / 2, h / 2 + PEG_H / 2))
    return solids


def make_plate(units, features=(), handles=True, peg_clear=PEG_CLEAR):
    """Snap-on front: the face with ears, pushed onto the chassis pegs. Prints flat, face up."""
    h = units * U - GAP_V
    solids = [box(-FACE_W / 2, FACE_W / 2, -PLATE_T, 0, 0, h)] + ear_hardware(h, -PLATE_T, handles)
    plate = apply_features(union_all(solids), features, front_y=-PLATE_T)
    pockets = [snap_peg(x, z, -SNAP_L - 0.2, 1, peg_clear) for x, z in snap_pegs(units)]
    return plate - union_all(pockets)


# ========================================================================== bezels
def make_bezel(units, features=(), peg_clear=BEZEL_PEG_CLEAR, face_t=PLATE_T, t=BEZEL_T, gap=BEZEL_GAP):
    """Clip-on bezel: plugs onto the ear pegs, stands `gap` in front of a face `face_t` thick."""
    h = units * U - GAP_V
    back = -face_t - gap
    front = back - t
    c = BEZEL_CHAMFER
    body = Manifold.batch_hull([
        box(-FACE_W / 2, FACE_W / 2, front + c, back, 0, h),
        box(-FACE_W / 2 + c, FACE_W / 2 - c, front, back, c, h - c),
    ])
    pockets = []
    for s in (-1, 1):
        xc = s * (FACE_W / 2 - EAR_W / 2)
        pockets.append(box(xc - PEG_W / 2 - peg_clear, xc + PEG_W / 2 + peg_clear,
                           back - (PEG_L - gap) - 0.2, back + 1,
                           h / 2 - PEG_H / 2 - peg_clear, h / 2 + PEG_H / 2 + peg_clear))
    body = body - union_all(pockets)
    return apply_features(body, features, front_y=front, through=back)


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)


def export_stl(m, path, lay_on_back=False, lay=None):
    """Export in print orientation: lay = "back" (+Y down: rack, fronts, bezels), "front" (-Y down)
    or "flip" (upside down); default is as modelled, on its bottom."""
    t = to_trimesh(m)
    lay = lay or ("back" if lay_on_back else None)
    angle = {"back": -np.pi / 2, "front": np.pi / 2, "flip": np.pi}.get(lay)
    if angle:
        t.apply_transform(trimesh.transformations.rotation_matrix(angle, [1, 0, 0]))
    t.apply_translation(-t.bounds[0])  # sit on the bed at the origin
    t.export(path)
    return t
