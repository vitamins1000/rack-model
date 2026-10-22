"""Build every printable STL plus assembled previews. Usage: .venv/bin/python build.py

designs/NAME.py is a front (FACE_SPEC.md), designs/NAME_bezel.py its clip-on bezel, and
panels/*.py the door, PDU and KVM layouts (PANEL_SPEC.md). Every server is a generic
chassis (stl/chassis) plus a snap-on front (stl/fronts).
"""
import json
import pathlib
import runpy
import sys

import extras as E
import rack_lib as L
from check_face import check

ROOT = pathlib.Path(__file__).parent
STL = ROOT / "stl"
BUILD = ROOT / "build"
BEZEL_ALIASES = {"disk_shelf_4u": "unified_controller_4u"}   # same bezel family as the controller
KVM = "kvm_console_1u"
# which designs go where in the previews (bottom unit number)
LAYOUT = json.loads((ROOT / "layout.json").read_text())


def folder(base, name):
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.stl"):
        old.unlink()
    return d


def load(path, key):
    errs = check(path)
    if errs:
        sys.exit(f"{path.relative_to(ROOT)} fails the checker: {errs[0]}")
    return runpy.run_path(str(path))[key]


def save(m, path, lay=None):
    t = L.export_stl(m, path, lay=lay)
    assert t.is_watertight and len(m.decompose()) == 1, f"{path.name}: not one watertight body"
    return t


def clear(a, b, what):
    assert (a ^ b).volume() < 1e-6, f"collision: {what}"


# ---------------------------------------------------------------- chassis, fronts, bezels
chassis_dir, fronts_dir, bezels_dir = folder(STL, "chassis"), folder(STL, "fronts"), folder(STL, "bezels")
designs, chassis = {}, {}
for p in sorted((ROOT / "designs").glob("*.py")):
    if p.stem.endswith("_bezel"):
        continue
    d = load(p, "DESIGN")
    name = p.stem
    bp = ROOT / "designs" / f"{BEZEL_ALIASES.get(name, name)}_bezel.py"
    bezel = load(bp, "BEZEL") if bp.exists() and d["handles"] != "loop" else None
    key = (d["units"], round(d["depth"]))
    if key not in chassis:
        chassis[key] = L.make_chassis(d["units"], d["depth"])
        save(chassis[key], chassis_dir / f"chassis_{key[0]}u_{key[1]}mm.stl")
    plate = L.make_plate(d["units"], d["features"], handles=False if bezel else d["handles"])
    t = save(plate, fronts_dir / f"{name}_front.stl", lay="back")
    deepest = max((f["depth"] for f in d["features"] if f["kind"] == "recess"), default=0)
    assert L.PLATE_T - L.SNAP_L - 0.2 - deepest >= 0.45, f"{name}: recess too deep for the peg pockets"
    clear(plate, chassis[key], f"{name} front vs chassis")
    b = None
    if bezel:
        assert bezel["units"] == d["units"], f"{name}: bezel units mismatch"
        b = L.make_bezel(d["units"], bezel["features"])
        save(b, bezels_dir / f"{name}_bezel.stl", lay="back")
        clear(b, plate, f"{name} bezel vs front")
    designs[name] = (d, key, plate, b)
    print(f"ok   {name:24s} chassis_{key[0]}u_{key[1]}mm + front {t.extents.round(1)}{' + bezel' if b else ''}")
print(f"     {len(chassis)} chassis sizes, {len(designs)} fronts, {sum(1 for v in designs.values() if v[3])} bezels")

# open-top GPU node chassis (gpu_chassis.py): same tongues/pegs as chassis_4u_100mm, lid off, interior details
import gpu_chassis as G
gpu_open = G.make_gpu_chassis(4, 100.0)
save(gpu_open, chassis_dir / "chassis_4u_100mm_gpu_open.stl")
clear(designs["gpu_node_4u"][2], gpu_open, "gpu_node_4u front vs open chassis")
print("ok   chassis_4u_100mm_gpu_open  (open-top HGX-style interior)")

# glow bezel test: bezel with through slots plus a shim in the accent colour
glow_dir = folder(STL, "bezels_glow_test")
glow, shim = E.make_glow_bezel(3), E.make_glow_shim(3)
save(glow, glow_dir / "flash_array_3u_bezel_glow.stl", lay="back")
save(shim, glow_dir / "flash_array_3u_glow_shim.stl", lay="back")
clear(glow, shim, "glow bezel vs shim")
clear(shim, designs["flash_array_3u"][2], "glow shim vs front")
print("ok   glow bezel test (bezel + shim)")

# --------------------------------------------------------------------------- rack + extras
rack = L.make_rack()
t = L.export_stl(rack, STL / "rack_42u.stl", lay="back")
print(f"ok   rack_42u                 print size {t.extents.round(1)}")

panel = {n: load(ROOT / "panels" / f"{n}.py", "PANEL")["features"] for n in ("door", "door_cray", "pdu", "kvm_deck", "kvm_lid")}
extras_dir, kvm_dir, test_dir = folder(STL, "extras"), folder(STL, "kvm"), STL / "fit_test"
test_dir.mkdir(exist_ok=True)

frame, door, door_cray = E.make_door_frame(), E.make_door(panel["door"]), E.make_door(panel["door_cray"])
tf = save(frame, extras_dir / "door_frame.stl", lay="front")
save(E.make_door_frame(z1=15.0), test_dir / "door_frame_grip_test.stl", lay="front")
clear(E.make_door_frame(grip=-0.02), rack, "door frame vs rack")
for dname, d in (("door", door), ("door_cray", door_cray)):   # same frame and hinges, different panel
    td = save(d, extras_dir / f"{dname}.stl", lay="back")
    for angle, lift in ((0, 0), (0, E.LIFT), (10, 0.5), (45, 0.5), (90, 0.5), (95, 0.5)):
        clear(E.door_pose(d, angle, lift), frame, f"{dname} at {angle} deg vs frame")
        clear(E.door_pose(d, angle, lift), rack, f"{dname} at {angle} deg vs rack")
    assert (E.door_pose(d, 2, 0) ^ frame).volume() > 0.1, f"{dname} latch does not hold"
    print(f"ok   door frame {tf.extents.round(1)}, {dname} {td.extents.round(1)}: swings to 95 deg, latch holds, lifts off")

onepiece = E.make_rack_with_frame()     # second-rack option: rack + door frame in one print
to = save(onepiece, STL / "rack_42u_with_frame.stl", lay="back")
for dname, d in (("door", door), ("door_cray", door_cray)):
    for angle, lift in ((0, 0), (0, E.LIFT), (10, 0.5), (45, 0.5), (90, 0.5), (95, 0.5)):
        clear(E.door_pose(d, angle, lift), onepiece, f"{dname} at {angle} deg vs one-piece rack")
    assert (E.door_pose(d, 2, 0) ^ onepiece).volume() > 0.1, f"{dname} latch does not hold on the one-piece rack"
print(f"ok   rack_42u_with_frame      print size {to.extents.round(1)}: both doors swing, latch, lift off")

pdu = E.make_pdu(panel["pdu"])
tp = save(pdu, extras_dir / "pdu.stl", lay="front")
pdus = {f"pdu_{'L' if s < 0 else 'R'}": E.place_pdu(pdu, s) for s in (-1, 1)}
for n, m in pdus.items():
    clear(m, rack, f"{n} vs rack")
    clear(m, onepiece, f"{n} vs one-piece rack")
caster = E.make_caster()
tc = save(caster, extras_dir / "caster.stl", lay="flip")
casters = {f"caster_{i}": caster.translate([x, y, 0]) for i, (x, y) in enumerate(E.LEGS)}
for n, m in casters.items():
    clear(m, rack, f"{n} vs rack")
    clear(m, frame, f"{n} vs door frame")
    clear(m, onepiece, f"{n} vs one-piece rack")
print(f"ok   pdu {tp.extents.round(1)} (print 2), caster {tc.extents.round(1)} (print 4, raises the rack {E.CASTER_LIFT:.1f} mm)")

shell, drawer, lid = E.make_kvm_shell(), E.make_kvm_drawer(panel["kvm_deck"]), E.make_kvm_lid(panel["kvm_lid"])
save(shell, kvm_dir / "kvm_shell.stl")
save(drawer, kvm_dir / "kvm_drawer.stl")
save(lid, kvm_dir / "kvm_screen.stl", lay="back")
keeper = E.make_kvm_keeper()
save(keeper, kvm_dir / "kvm_screen_keeper.stl", lay="flip")
keepers = keeper + keeper.mirror([1, 0, 0])      # one per cradle, glued on
clear(keepers, drawer, "KVM keepers vs drawer")
for angle in (0, 30, 60, 90, E.LID_OPEN):
    clear(E.place_kvm_lid(lid, angle), keepers, f"KVM screen at {angle} deg vs keepers")
    assert (E.place_kvm_lid(lid, angle).translate([0, 0, 0.6]) ^ keepers).volume() > 1e-3, f"keepers don't hold the screen at {angle} deg"
drawer_k = drawer + keepers
for pull in (0, 20, E.KVM_PULL, 90):
    for drop in (0, 0.19):
        clear(drawer_k.translate([0, -pull, -drop]), shell, f"KVM drawer (with keepers) pulled {pull} vs shell")
        clear(E.place_kvm_lid(lid).translate([0, -pull, -drop]), shell, f"KVM screen (folded) pulled {pull} vs shell")
for angle in (0, 30, 60, 90, E.LID_OPEN):
    clear(E.place_kvm_lid(lid, angle), drawer, f"KVM screen at {angle} deg vs drawer")
print(f"ok   kvm console: shell, drawer, screen (opens to {E.LID_OPEN:.0f} deg with the drawer out {E.KVM_PULL:.0f} mm)")


# -------------------------------------------------------------------------------- previews
def kvm_parts(z, pull=0.0, angle=0.0):
    return {"kvm_shell": shell.translate([0, 0, z]), "kvm_drawer": drawer_k.translate([0, -pull, z]),
            "kvm_screen": E.place_kvm_lid(lid, angle).translate([0, -pull, z])}


def scene(name, bezels=False, door_angle=None, kvm_open=False, door_m=None, rack_m=None):
    out = folder(BUILD, name)
    body = rack if rack_m is None else rack_m
    parts = {"rack_42u": body, **casters, **pdus}
    placed, used = {}, set()
    for dname, unit in LAYOUT:
        z = L.slot_z(unit) - 0.15
        if dname == KVM:
            units, group = 1, kvm_parts(z, E.KVM_PULL if kvm_open else 0, E.LID_OPEN if kvm_open else 0)
            group = {f"{k}_U{unit:02d}": m for k, m in group.items()}
        else:
            d, key, plate, b = designs[dname]
            units = d["units"]
            group = {f"{dname}_U{unit:02d}": (chassis[key] + plate).translate([0, 0, z])}
            if bezels and b is not None:
                group[f"{dname}_U{unit:02d}_zbezel"] = b.translate([0, 0, z])
        rng = set(range(unit, unit + units))
        assert not rng & used, f"overlap at U{unit} ({dname})"
        used |= rng
        placed.update(group)
    door_now = E.door_pose(door if door_m is None else door_m, door_angle) if door_angle is not None else None
    for k, m in placed.items():
        clear(m, body, f"{k} vs rack")
        if door_now is not None:
            clear(m, frame, f"{k} vs door frame")
            clear(m, door_now, f"{k} vs door")
    for a, ma in placed.items():          # neighbours must not touch (bezels, open screen, ...)
        for b_, mb in placed.items():
            same_unit = a.replace("_zbezel", "") == b_.replace("_zbezel", "")   # a front and its own bezel
            if a < b_ and not same_unit and not (a.startswith("kvm") and b_.startswith("kvm")):
                clear(ma, mb, f"{a} vs {b_}")
    parts.update(placed)
    if door_now is not None:
        if rack_m is None:
            parts["door_frame"] = frame
        parts["door_panel" if door_m is None else "door_cray_panel"] = door_now
    for k, m in parts.items():
        L.to_trimesh(m).export(out / f"{k}.stl")
    print(f"build/{name}/: {len(parts)} parts, {len(used)}/42U filled")


scene("preview_parts")
scene("preview_bezel_parts", bezels=True)
scene("preview_door_parts", bezels=True, door_angle=0)
scene("preview_cray_door_parts", bezels=True, door_angle=0, door_m=door_cray)
scene("preview_open_parts", bezels=True, door_angle=95, kvm_open=True)
scene("preview_onepiece_parts", bezels=True, door_angle=0, door_m=door_cray, rack_m=onepiece)
scene("preview_onepiece_open_parts", bezels=True, door_angle=95, kvm_open=True, door_m=door_cray, rack_m=onepiece)
out = folder(BUILD, "kvm_parts")
for k, m in kvm_parts(0, E.KVM_PULL, E.LID_OPEN).items():
    L.to_trimesh(m).export(out / f"{k}.stl")
