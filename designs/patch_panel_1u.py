DESIGN = {
    "name": "patch_panel_1u",
    "units": 1,
    "depth": 20.0,
    "handles": True,
    "features": [],
}

H = 5.256
u_min = 3.8
u_max = 56.2
v_min = 0.8
v_max = H - 0.8

port_w = 1.26
port_h = 1.8
port_depth = 1.2
intra_gap = 0.8
inter_gap = 2.0
groups = 4
ports_per_group = 6

total_w = (
    groups * (ports_per_group * port_w + (ports_per_group - 1) * intra_gap)
    + (groups - 1) * inter_gap
)

start_u = round((u_min + u_max) / 2 - total_w / 2, 2)
start_v = round((v_min + v_max) / 2 - port_h / 2, 2)

group_pitch = ports_per_group * port_w + (ports_per_group - 1) * intra_gap + inter_gap
port_pitch = port_w + intra_gap

features = []
for g in range(groups):
    for p in range(ports_per_group):
        u = round(start_u + g * group_pitch + p * port_pitch, 2)
        v = start_v
        features.append({
            "kind": "recess",
            "u": u,
            "v": v,
            "w": round(port_w, 2),
            "h": round(port_h, 2),
            "depth": round(port_depth, 2),
        })

DESIGN["features"] = features