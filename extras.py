"""Add-on parts that need no rack reprint: door + clip-on frame, PDUs, casters, the KVM
console drawer and the glow bezel test.

Rack coordinates as in rack_lib (x across, y = 0 at the wall fronts, +y to the back, z up).
"""
import math

import numpy as np
from manifold3d import CrossSection, FillRule, Manifold

import rack_lib as L
from rack_lib import box, union_all


def prism_xy(pts, z0, z1):
    """Polygon in (x, y) extruded from z0 to z1."""
    return Manifold.extrude(CrossSection([pts], FillRule.NonZero), z1 - z0).translate([0, 0, z0])


def prism_xz(pts, y0, y1):
    """Polygon in (x, z) extruded from y0 to y1."""
    return Manifold.extrude(CrossSection([pts], FillRule.NonZero), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def prism_yz(pts, x0, x1):
    """Polygon in (y, z) extruded from x0 to x1."""
    m = Manifold.extrude(CrossSection([pts], FillRule.NonZero), x1 - x0)
    return m.transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=float))


def rotate_about_z(m, deg, x, y):
    return m.translate([-x, -y, 0]).rotate([0, 0, deg]).translate([x, y, 0])


def rotate_about_x(m, deg, y, z):
    return m.translate([0, -y, -z]).rotate([deg, 0, 0]).translate([0, y, z])


# ============================================================================ door
HW = L.OUTER_W / 2                       # rack half width
FRONT_MAX = L.PLATE_T + L.BEZEL_GAP + L.BEZEL_T + 1.0   # bezel bosses: furthest thing in front of the walls
DOOR_T = 2.4
DOOR_BACK = -(FRONT_MAX + 0.8)           # y of the door's inner face
DOOR_FRONT = DOOR_BACK - DOOR_T
FRAME_FRONT = DOOR_FRONT - 0.6           # the door sits 0.6 inside the frame face
FRAME_BACK = -L.CAP_LIP - 0.1            # frame rests against the plinth/top-cap lips
WIN = 30.5                               # half width of the opening (fronts are 60 wide)
Z_BOT = 3.2                              # frame starts above the caster cups
Z_WIN0 = L.PLINTH_H
Z_WIN1 = L.PLINTH_H + L.BAY_H
FLANGE_T, FLANGE_D = 1.6, 15.0           # side flanges that grip the rack, reaching to y = FLANGE_D
GRIP = 0.10                              # flange interference per side (tune with the fit test)
TOPF_GAP = 0.15
TOP_Z = L.RACK_H + TOPF_GAP + FLANGE_T   # top of the frame (flange lying on the rack top)

AX_X, AX_Y = -28.5, DOOR_BACK - 0.8      # hinge axis
PIN = 1.6                                # square hinge pins
SOCKET_R = 1.3
PIN_BOT, LIFT, PIN_TOP = 1.2, 1.5, 4.5   # lift-off hinge: raise the door by LIFT to free the bottom pin
WASHER = 0.2
DOOR_X0 = -WIN + 0.3
DOOR_X1 = WIN - 0.3                      # free edge at the back; the front is DOOR_T wider (45 deg mitre)
DOOR_Z0 = Z_WIN0 + WASHER
DOOR_Z1 = Z_WIN1 - LIFT
TOOTH = (26.0, 28.5)                     # x range of the gravity-latch tooth under the free end
TOOTH_H = 0.6


def make_door_frame(grip=GRIP, z0=Z_BOT, z1=None):
    """Clip-on frame: side flanges grip the rack sides, a top flange rests on the rack top."""
    full = z1 is None
    z1 = TOP_Z if full else z1
    ring = box(-HW, HW, FRAME_FRONT, FRAME_BACK, z0, z1)
    solids = [ring]
    for s in (-1, 1):
        xi = s * (HW - grip)
        x0, x1 = sorted((xi, xi + s * FLANGE_T))
        flange = box(x0, x1, FRAME_FRONT, FLANGE_D, z0, min(z1, L.RACK_H))
        lead = prism_xy([(xi - s * 0.01, FLANGE_D - 2.5), (xi + s * 0.7, FLANGE_D + 0.01),
                         (xi - s * 0.01, FLANGE_D + 0.01)], z0 - 1, z1 + 1)
        solids.append(flange - lead)
    if full:
        solids.append(box(-(HW - 3), HW - 3, FRAME_FRONT, 12.0, L.RACK_H + TOPF_GAP, TOP_Z))
    frame = union_all(solids)

    cuts = [box(-WIN, WIN, FRAME_FRONT - 1, FRAME_BACK + 1, Z_WIN0, Z_WIN1)] + frame_details()
    return frame - union_all(cuts)


def frame_details():
    """Cuts shared by the clip-on frame and the one-piece rack: door rebate, hinge sockets, latch, vents."""
    cuts = []
    # 45 deg rebate on the free side: the door's mitred edge closes against it
    cuts.append(prism_xy([(WIN - 0.5, DOOR_BACK), (WIN, DOOR_BACK), (WIN + 3.0, DOOR_BACK - 3.0),
                          (WIN + 3.6, FRAME_FRONT - 0.5), (WIN - 0.5, FRAME_FRONT - 0.5)], Z_WIN0, Z_WIN1))
    # hinge sockets in the bottom and top bars
    sock = Manifold.cylinder(1.0, SOCKET_R, SOCKET_R, 32)
    cuts.append(sock.scale([1, 1, PIN_BOT + 0.6 + 0.01]).translate([AX_X, AX_Y, Z_WIN0 - PIN_BOT - 0.6]))
    cuts.append(sock.scale([1, 1, PIN_TOP + 0.9 + 0.01]).translate([AX_X, AX_Y, Z_WIN1 - 0.01]))
    # gravity latch: notch for the door's tooth, with ramps so the tooth rides in and out
    x0, x1 = TOOTH[0] - 0.4, TOOTH[1] + 0.4
    ny0, ny1 = DOOR_BACK - 1.7, DOOR_BACK + 0.3
    cuts.append(box(x0, x1, ny0, ny1, Z_WIN0 - 0.7, Z_WIN0 + 0.01))
    cuts.append(prism_yz([(FRAME_FRONT - 0.01, Z_WIN0 - 0.7), (FRAME_FRONT - 0.01, Z_WIN0 + 0.01),
                          (FRAME_FRONT + 0.7, Z_WIN0 + 0.01)], x0 - 0.6, x1 + 0.6))
    cuts.append(prism_yz([(ny0 - 0.5, Z_WIN0 + 0.01), (ny0 + 0.01, Z_WIN0 + 0.01), (ny0 + 0.01, Z_WIN0 - 0.5)], x0, x1))
    # vent slots on the bottom bar, like the plinth behind it
    for x in np.arange(-22, 23, 4):
        cuts.append(box(x - 1, x + 1, FRAME_FRONT - 1, FRAME_FRONT + 1.0, 5.0, 8.0))
    return cuts


def make_rack_with_frame():
    """Rack and door frame as one print: the frame ring is filled back to the wall fronts, no flanges.

    Prints on its back like the rack, so the ring grows straight up off the wall, plinth and cap fronts.
    The U ticks are left out: the ring would seal them in (the clip-on frame hid them anyway).
    """
    ring = box(-HW, HW, FRAME_FRONT, 0.01, Z_BOT, L.RACK_H) - box(-WIN, WIN, FRAME_FRONT - 1, 1.0, Z_WIN0, Z_WIN1)
    return union_all([L.make_rack(ticks=False), ring]) - union_all(frame_details())


def make_door(features=()):
    """Lift-off door, perforated from a panel layout (PANEL_SPEC.md, panel "door")."""
    slab = box(DOOR_X0, DOOR_X1 + DOOR_T, DOOR_FRONT, DOOR_BACK, DOOR_Z0, DOOR_Z1)
    zmid = (DOOR_Z0 + DOOR_Z1) / 2
    adds = [
        box(AX_X - PIN / 2, AX_X + PIN / 2, DOOR_BACK - PIN, DOOR_BACK, DOOR_Z0 - WASHER - PIN_BOT, DOOR_Z0 + 0.01),
        box(AX_X - PIN / 2, AX_X + PIN / 2, DOOR_BACK - PIN, DOOR_BACK, DOOR_Z1 - 0.01, DOOR_Z1 + PIN_TOP),
        box(AX_X - 1.3, AX_X + 2.0, DOOR_BACK - 1.9, DOOR_BACK, DOOR_Z0 - WASHER, DOOR_Z0 + 0.01),       # washer
        box(TOOTH[0], TOOTH[1], DOOR_BACK - 1.4, DOOR_BACK, DOOR_Z0 - TOOTH_H, DOOR_Z0 + 0.01),          # latch tooth
        box(DOOR_X1 - 2.8, DOOR_X1 - 0.8, DOOR_FRONT - 1.2, DOOR_FRONT + 0.01, zmid - 9, zmid + 9),      # handle
    ]
    cuts = [
        prism_xy([(DOOR_X1, DOOR_BACK + 0.01), (DOOR_X1 + DOOR_T + 0.02, DOOR_BACK + 0.01),
                  (DOOR_X1 + DOOR_T + 0.02, DOOR_FRONT - 0.01)], DOOR_Z0 - 1, DOOR_Z1 + 1),              # mitre
        prism_xy([(DOOR_X0 - 0.01, DOOR_FRONT - 0.01), (DOOR_X0 + 0.8, DOOR_FRONT - 0.01),
                  (DOOR_X0 - 0.01, DOOR_FRONT + 0.8)], DOOR_Z0 - 1, DOOR_Z1 + 1),                        # hinge relief
    ]
    door = union_all([slab - union_all(cuts)] + adds)
    return L.apply_features(door, features, front_y=DOOR_FRONT, through=DOOR_BACK, origin=(DOOR_X0, DOOR_Z0))


def door_pose(door, angle=0.0, lift=0.0):
    """Door swung open by `angle` degrees and raised by `lift`."""
    return rotate_about_z(door, -angle, AX_X, AX_Y).translate([0, 0, lift])


# ============================================================================= PDU
PDU_W, PDU_T, PDU_LEN = 6.2, 4.0, 208.0
PDU_X = 22.5                              # vent-slot column the PDU hangs on (also -PDU_X)
PDU_Z0 = 14.0
VENT_Z = [L.PLINTH_H + 12 + 28 * k for k in range(7)]   # bottom of each 22 mm tall rear vent slot
PDU_HOOKS = (VENT_Z[0], VENT_Z[6])
HOOK_W, HOOK_H, HOOK_DROP = 1.6, 6.0, 2.0


def make_pdu(features=()):
    """PDU strip in its own frame: face at y=0 (facing -y), back hooks at y > PDU_T."""
    body = L.apply_features(box(0, PDU_W, 0, PDU_T, 0, PDU_LEN), features, front_y=0, origin=(0, 0))
    hooks = []
    through = L.REAR_T + 0.3
    for zs in PDU_HOOKS:
        z0 = zs - PDU_Z0
        x0, x1 = PDU_W / 2 - HOOK_W / 2, PDU_W / 2 + HOOK_W / 2
        hooks.append(box(x0, x1, PDU_T - 0.01, PDU_T + through, z0, z0 + HOOK_H))
        y = PDU_T + through  # wedge that drops behind the rear panel (45 deg, prints without support)
        hooks.append(prism_yz([(y - 0.01, z0), (y + HOOK_DROP, z0 - HOOK_DROP), (y + HOOK_DROP, z0 + HOOK_H),
                               (y - 0.01, z0 + HOOK_H)], x0, x1))
    return union_all([body] + hooks)


def place_pdu(pdu, side):
    """Hang a PDU on the rear panel; side = -1 (left, seen from the front) or 1."""
    rear = L.INNER_D + L.REAR_T
    return pdu.rotate([0, 0, 180]).translate([side * PDU_X + PDU_W / 2, rear + PDU_T, PDU_Z0])


# ========================================================================== casters
LEG = 8.0
CUP_CLEAR, CUP_WALL, CUP_D, CUP_FLOOR = 0.15, 1.2, 2.8, 1.2
WHEEL_R, WHEEL_W = 3.5, 3.6
LEGS = [(sx * (HW - LEG / 2), y) for sx in (-1, 1)
        for y in (-L.CAP_LIP + LEG / 2, L.INNER_D + L.REAR_T - LEG / 2)]


def make_caster():
    """Push-on caster for one plinth leg; the leg sits in the cup (leg bottom at z=0). Decorative: no rolling."""
    o = LEG / 2 + CUP_CLEAR + CUP_WALL
    i = LEG / 2 + CUP_CLEAR
    cup = box(-o, o, -o, o, -CUP_FLOOR, CUP_D) - box(-i, i, -i, i, 0, CUP_D + 1)
    hz = -CUP_FLOOR - 2.5                                    # underside of the housing
    housing = Manifold.batch_hull([box(-o, o, -o, o, -CUP_FLOOR - 0.01, -CUP_FLOOR),
                                   box(-3.2, 3.2, -3.2, 3.2, hz, hz + 0.01)])
    az = hz - math.sqrt(WHEEL_R ** 2 - 3.0 ** 2)             # axle height: the wheel's top is buried in the housing
    cyl = Manifold.cylinder(1.0, 1.0, 1.0, 48).rotate([0, 90, 0])   # unit cylinder along +x
    wheel = cyl.scale([WHEEL_W, WHEEL_R, WHEEL_R]).translate([-WHEEL_W / 2, 0, az])
    wheel = wheel - box(-5, 5, -5, 5, az - WHEEL_R - 1, az - WHEEL_R + 0.23)      # flat where it meets the floor
    cheeks = []
    for s in (-1, 1):
        x0, x1 = sorted((s * WHEEL_W / 2, s * 3.0))
        cheeks.append(box(x0, x1, -2.2, 2.2, az, hz + 0.01))
        cheeks.append(cyl.scale([x1 - x0, 2.2, 2.2]).translate([x0, 0, az]))
    return union_all([cup, housing, wheel] + cheeks)


CASTER_LIFT = CUP_FLOOR + 2.5 + math.sqrt(WHEEL_R ** 2 - 3.0 ** 2) + WHEEL_R - 0.23   # how far the rack is raised


# =============================================================================== KVM
KVM_H = L.U - L.GAP_V
KVM_DEPTH = 95.0
KVM_WALL_IN = 25.0                        # inner face of the shell side walls
DRAWER_HW = 24.8
SHELL_FLOOR = 1.0
DRAWER_Z0, DRAWER_Z1 = 1.2, 2.2           # drawer floor
DECK = (42.0, 46.0)                       # keyboard deck panel size
DECK_Y0 = 1.5
LID_W, LID_LEN, LID_T = 43.4, 36.0, 1.6   # a 17 inch 4:3 screen at 1:8
LID_C = 0.47                              # chamfer that makes the pins (and the hinge end) octagonal
HINGE_Y, HINGE_Z = 38.5, 3.7
POST_X = (22.0, 24.0)
POST_TOP = 5.0                            # top of the screen cradle posts
KEEPER_T = 0.4                            # glue-on cradle cap: the unit above is only 0.556 over the post tops
STOP_GAP = 1.07                           # stop wall this far behind the hinge axis: the screen leans back ~11 deg
LID_OPEN = 100.0
KVM_PULL = 56.0                           # drawer travel so the open screen clears the bezels above it


def make_kvm_shell(depth=KVM_DEPTH):
    """1U sleeve with rack ears; the drawer slides in from the front under two hold-down ridges."""
    hb = L.INNER_W / 2 - L.SIDE_CLEAR
    # the floor runs under the drawer front, so the drawer's own bottom is flat and prints without support
    solids = [box(-hb, hb, -L.PLATE_T, depth, 0, SHELL_FLOOR), box(-hb, hb, depth - 1.2, depth, 0, KVM_H)]
    zc = 0.5 * L.U - L.GAP_V / 2
    for s in (-1, 1):
        x0, x1 = sorted((s * KVM_WALL_IN, s * hb))
        solids.append(box(x0, x1, -L.PLATE_T, depth, 0, KVM_H))                               # side wall + cheek
        x0, x1 = sorted((s * (hb - 0.01), s * L.FACE_W / 2))
        solids.append(box(x0, x1, -L.PLATE_T, 0, 0, KVM_H))                                   # ear
        solids.append(L.rail_tongue(s, hb, zc, 1.0, depth - 0.5))                              # rail tongue
        w = s * (KVM_WALL_IN + 0.01)
        solids.append(prism_xz([(w, DRAWER_Z1), (s * (KVM_WALL_IN - 0.8), DRAWER_Z1 + 0.8),
                                (s * (KVM_WALL_IN - 0.8), DRAWER_Z1 + 1.4), (w, DRAWER_Z1 + 1.4)], 0, depth - 1.2))
    return union_all(solids)


def make_kvm_drawer(deck_features=()):
    """Drawer: floor with the keyboard deck, front panel with a finger ledge, hinge cradle for the screen."""
    top = KVM_H - 0.2
    # floor slab with the keyboard deck on it, built facing -y and then turned to face up
    floor = L.apply_features(box(0, 2 * DRAWER_HW, 0, DRAWER_Z1 - DRAWER_Z0, 0, KVM_DEPTH - 0.9), deck_features,
                             front_y=0, origin=(DRAWER_HW - DECK[0] / 2, DECK_Y0 + 0.5))
    solids = [
        floor.rotate([-90, 0, 0]).translate([-DRAWER_HW, -0.5, DRAWER_Z1]),
        box(-DRAWER_HW, DRAWER_HW, -L.PLATE_T, 0, DRAWER_Z0, top),                  # front panel
        prism_yz([(-L.PLATE_T + 0.01, 2.0), (-L.PLATE_T - 2.0, 4.0), (-L.PLATE_T - 2.0, top),
                  (-L.PLATE_T + 0.01, top)], -12, 12),                              # finger ledge
        box(-22.5, 22.5, HINGE_Y + STOP_GAP, HINGE_Y + STOP_GAP + 1.2, DRAWER_Z1 - 0.01, 5.0),   # screen stop wall
    ]
    for s in (-1, 1):
        x0, x1 = sorted((s * POST_X[0], s * POST_X[1]))
        post = box(x0, x1, HINGE_Y - 2.0, HINGE_Y + 2.0, DRAWER_Z1 - 0.01, POST_TOP)
        solids.append(post - box(x0 - 0.1, x1 + 0.1, HINGE_Y - 1.05, HINGE_Y + 1.05, HINGE_Z - 0.9, 5.1))
    return union_all(solids)


def make_kvm_keeper():
    """Glue-on cap for a screen cradle (print 2, fits either side): a plate over the open slot so the pin
    can't lift out. KEEPER_T is all the room there is under the unit above. A lip down the post's outer
    face and a nub in the slot line it up for gluing. Modelled on the right-hand post."""
    x0, x1 = POST_X
    y0, y1 = HINGE_Y - 2.0, HINGE_Y + 2.0
    return union_all([
        box(x0, x1 + 0.8, y0, y1, POST_TOP, POST_TOP + KEEPER_T),                          # plate
        box(x1, x1 + 0.8, y0, y1, POST_TOP - 0.8, POST_TOP + 0.01),                        # lip
        box(x0 + 0.2, x1 - 0.2, HINGE_Y - 0.95, HINGE_Y + 0.95, POST_TOP - 0.2, POST_TOP + 0.01),   # nub
    ])


def make_kvm_lid(features=()):
    """Flip-up screen in its own frame: screen face at y=0 (facing -y), hinge pins at z=0..LID_T."""
    t, c = LID_T, LID_C
    body = prism_yz([(0, c), (c, 0), (t - c, 0), (t, c), (t, LID_LEN), (0, LID_LEN)], 0, LID_W)
    lid = L.apply_features(body, features, front_y=0, origin=(0, 0))
    octagon = [(c, 0), (t - c, 0), (t, c), (t, t - c), (t - c, t), (c, t), (0, t - c), (0, c)]
    return union_all([lid, prism_yz(octagon, -1.9, 0.01), prism_yz(octagon, LID_W - 0.01, LID_W + 1.9)])


def place_kvm_lid(lid, angle=0.0):
    """Screen on the drawer: angle 0 = folded flat on the keyboard, LID_OPEN = standing up."""
    m = lid.rotate([90, 0, 0]).translate([-LID_W / 2, HINGE_Y + LID_T / 2, HINGE_Z - LID_T / 2])
    return rotate_about_x(m, -angle, HINGE_Y, HINGE_Z)


# ====================================================================== glow bezel test
GLOW_SHIM = 0.6


def glow_features(units=3, pitch=6.2, groove=1.2):
    """Two rows of honeycomb cells around a blank emblem: grooves on every cell edge, through slots
    on the vertical edges. The slots never share a vertex, so the bezel stays one piece; a coloured
    shim behind shows through them.
    """
    h = units * L.U - L.GAP_V
    pad = groove / 2 + 0.3
    zone = (3.8 + pad, 0.8 + pad, 56.2 - pad, h - 0.8 - pad)
    R = pitch / math.sqrt(3)
    cu, cv = 30.0, h / 2
    feats = [{"kind": "boss", "shape": "hex_h", "u": cu - 4.85, "v": cv - 4.2, "w": 9.7, "h": 8.4, "depth": 0.8}]
    edges = {}
    for r in (0, 1):
        y = cv + (r - 0.5) * pitch * math.sqrt(3) / 2
        for c in range(-5, 6):
            x = cu + c * pitch + (0 if r else pitch / 2)
            v = [(x + R * math.sin(math.radians(60 * k)), y + R * math.cos(math.radians(60 * k))) for k in range(6)]
            for a, b in zip(v, v[1:] + v[:1]):
                key = tuple(sorted((round(a[0], 2), round(a[1], 2), round(b[0], 2), round(b[1], 2))))
                edges[key] = (a, b)
    for (ax, ay), (bx, by) in edges.values():
        mx, my = (ax + bx) / 2, (ay + by) / 2
        if not all(zone[0] <= px <= zone[2] and zone[1] <= py <= zone[3] for px, py in ((ax, ay), (bx, by))):
            continue
        if math.hypot(mx - cu, my - cv) < 5.6:   # keep clear of the emblem
            continue
        length = math.hypot(bx - ax, by - ay)
        ang = math.degrees(math.atan2(-(bx - ax), by - ay))   # rotation of a vertical bar onto the edge
        ang = (ang + 90) % 180 - 90
        feats.append({"kind": "recess", "u": mx - groove / 2, "v": my - length / 2 - 0.3, "w": groove,
                      "h": length + 0.6, "angle": ang, "depth": 0.6})
        if abs(ang) < 1:
            feats.append({"kind": "hole", "u": mx - groove / 2, "v": my - length / 2 + 0.5, "w": groove,
                          "h": length - 1.0, "depth": 0})
    return feats


def make_glow_bezel(units=3):
    """Bezel with through slots; GLOW_SHIM thinner at the back to make room for the coloured shim."""
    return L.make_bezel(units, glow_features(units), t=L.BEZEL_T - GLOW_SHIM, gap=L.BEZEL_GAP + GLOW_SHIM)


def make_glow_shim(units=3):
    """Thin plate in the accent colour: it goes on the ear pegs first, the glow bezel on top."""
    h = units * L.U - L.GAP_V
    back = -L.PLATE_T - L.BEZEL_GAP
    shim = box(-L.FACE_W / 2 + 0.3, L.FACE_W / 2 - 0.3, back - GLOW_SHIM, back, 0.3, h - 0.3)
    holes = []
    for s in (-1, 1):
        xc = s * (L.FACE_W / 2 - L.EAR_W / 2)
        c = L.PEG_CLEAR + 0.05
        holes.append(box(xc - L.PEG_W / 2 - c, xc + L.PEG_W / 2 + c, back - 1, back + 1,
                         h / 2 - L.PEG_H / 2 - c, h / 2 + L.PEG_H / 2 + c))
    return shim - union_all(holes)
