"""Blender: import build/PARTS_DIR/*.stl, colour the parts, save previews/OUT_NAME.blend and .png.
Run: Blender -b --python render.py [-- PARTS_DIR OUT_NAME [front|rear|left]]
"front" is a straight-on orthographic view; "rear" and "left" move the 3/4 camera."""
import math
import pathlib
import sys

import bpy

ROOT = pathlib.Path(__file__).resolve().parent
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PARTS = ROOT / "build" / (ARGS[0] if ARGS else "preview_parts")
OUT = ROOT / "previews"
OUT.mkdir(exist_ok=True)
VIEW = ARGS[2] if len(ARGS) > 2 else ""
NAME = ARGS[1] if len(ARGS) > 1 else "preview"
bpy.ops.wm.read_factory_settings(use_empty=True)
for f in sorted(PARTS.glob("*.stl")):
    bpy.ops.wm.stl_import(filepath=str(f))

COLOURS = {  # prefix -> RGB
    "rack": (0.05, 0.05, 0.055), "sled": (0.5, 0.5, 0.52), "flash_array": (0.09, 0.09, 0.1),
    "hybrid_array": (0.16, 0.16, 0.17), "unified_controller": (0.1, 0.35, 0.78),
    "disk_shelf": (0.1, 0.35, 0.78), "storage_server": (0.62, 0.63, 0.65),
    "switch": (0.1, 0.4, 0.45), "patch_panel": (0.2, 0.2, 0.22),
    "ups": (0.12, 0.12, 0.12), "blank": (0.08, 0.08, 0.09), "gpu_node": (0.72, 0.73, 0.75),
    "kvm_shell": (0.1, 0.1, 0.11), "kvm_drawer": (0.3, 0.3, 0.32), "kvm_screen": (0.12, 0.14, 0.2),
    "door_frame": (0.08, 0.08, 0.09), "door_panel": (0.22, 0.22, 0.24), "door_cray": (0.68, 0.68, 0.66), "pdu": (0.7, 0.12, 0.1),
    "caster": (0.3, 0.3, 0.32),
}


def mat(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.45
    return m


BEZEL_COLOURS = {  # prefix -> RGB for clip-on bezels
    "flash_array": (0.12, 0.12, 0.13), "hybrid_array": (0.0, 0.6, 0.45),
    "unified_controller": (0.75, 0.77, 0.8), "disk_shelf": (0.75, 0.77, 0.8),
    "storage_server": (0.07, 0.07, 0.08),
}

for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    table = BEZEL_COLOURS if "zbezel" in ob.name else COLOURS
    key = next((k for k in table if ob.name.startswith(k)), None)
    rgb = table[key] if key else COLOURS["blank"]
    ob.data.materials.clear()
    ob.data.materials.append(mat(("bezel_" if table is BEZEL_COLOURS else "") + (key or "blank"), rgb))

scene = bpy.context.scene
# model units are mm (1 Blender unit = 1 mm); front of the rack faces -Y
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
# frame whatever was imported: look from front-right, distance scaled to the parts' size
pts = [ob.matrix_world @ v.co for ob in scene.objects if ob.type == "MESH" for v in ob.data.vertices]
lo = [min(p[i] for p in pts) for i in range(3)]
hi = [max(p[i] for p in pts) for i in range(3)]
centre = [(a + b) / 2 for a, b in zip(lo, hi)]
tall = hi[2] - lo[2] > 150
size = max(hi[0] - lo[0], hi[2] - lo[2]) if tall else max(h - l for h, l in zip(hi, lo))
dist = size * (2.0 if tall else 2.4)
elev = 0.0 if tall else math.radians(25)  # tall rack: level view; small parts: from above
az = {"rear": 158.0, "left": -30.0}.get(VIEW, 22.0)   # camera azimuth: 0 = straight in front, 180 = behind
cam.location = (centre[0] + dist * math.sin(math.radians(az)) * math.cos(elev),
                centre[1] - dist * math.cos(math.radians(az)) * math.cos(elev),
                centre[2] + dist * math.sin(elev))
cam.rotation_euler = (math.radians(90) - elev, 0, math.radians(az))
cam_data.lens = 50
FRONT = VIEW == "front"
if FRONT:  # orthographic, looking along +Y at the front faces
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(hi[0] - lo[0], (hi[2] - lo[2]) * 1400 / 900) * 1.05
    cam.location = (centre[0], lo[1] - 200, centre[2])
    cam.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam
cam_data.clip_end = 5000

# key light from the upper left so recesses and bosses cast readable shadows
sy = -1 if VIEW == "rear" else 1   # light the side the camera looks at
for loc, energy in (((300, -400 * sy, 400), 3e6), ((-300, -200 * sy, 150), 1.2e6)) if not FRONT else \
        (((centre[0] - 150, lo[1] - 250, centre[2] + 150), 1.6e6), ((centre[0] + 200, lo[1] - 300, centre[2] - 50), 4e5)):
    light = bpy.data.objects.new("light", bpy.data.lights.new("light", "AREA"))
    light.data.energy = energy
    light.data.size = 300
    light.location = loc
    light.rotation_euler = (math.radians(60), 0, math.atan2(loc[0], -loc[1]))
    scene.collection.objects.link(light)
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.82, 0.85, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
scene.world = world

scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = (900, 1400) if tall and not FRONT else (1400, 900)
scene.render.filepath = str(OUT / f"{NAME}.png")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{NAME}.blend"))
bpy.ops.render.render(write_still=True)
