DESIGN = {
    "name": "ups_2u",
    "units": 2,
    "depth": 80.0,
    "handles": True,
    "features": [],
}

H = 2 * 5.556 - 0.3  # 10.812

# Usable area
u_min = 3.8
u_max = 56.2
v_min = 0.8
v_max = H - 0.8  # 10.012

usable_w = u_max - u_min  # 52.4
usable_h = v_max - v_min  # 9.212

# Left 55% for ventilation grille
vent_w = usable_w * 0.55  # 28.82
vent_u_start = u_min
vent_u_end = vent_u_start + vent_w  # 32.62

# Slot parameters
slot_h = 0.8
slot_gap = 0.9
slot_depth = 1.0

# Number of slots that fit
n_slots = int((usable_h + slot_gap) / (slot_h + slot_gap))  # 5
total_slots_h = n_slots * slot_h + (n_slots - 1) * slot_gap  # 7.6
vent_v_offset = v_min + (usable_h - total_slots_h) / 2.0  # 1.606

features = []

# Ventilation slots
for i in range(n_slots):
    v = vent_v_offset + i * (slot_h + slot_gap)
    features.append({
        "kind": "recess",
        "u": round(vent_u_start, 2),
        "v": round(v, 2),
        "w": round(vent_w, 2),
        "h": round(slot_h, 2),
        "depth": round(slot_depth, 2),
    })

# Right side: gap then display + buttons
gap_lr = 0.8
right_u_start = vent_u_end + gap_lr  # 33.42
right_w = u_max - right_u_start  # 22.78

# Display window
display_w = 12.0
display_h = 4.0
display_depth = 0.8

# Buttons
btn_count = 4
btn_w = 1.6
btn_h = 1.6
btn_depth = 0.6
btn_gap = 0.8
total_btn_w = btn_count * btn_w + (btn_count - 1) * btn_gap  # 8.8

# Vertical layout for right side
gap_db = 0.8  # gap between display and buttons
total_right_h = display_h + gap_db + btn_h  # 6.4
right_v_offset = v_min + (usable_h - total_right_h) / 2.0  # 2.206

# Buttons row (bottom)
buttons_v = right_v_offset  # 2.206
buttons_u_start = right_u_start + (right_w - total_btn_w) / 2.0  # 40.41

for i in range(btn_count):
    u = buttons_u_start + i * (btn_w + btn_gap)
    features.append({
        "kind": "boss",
        "u": round(u, 2),
        "v": round(buttons_v, 2),
        "w": round(btn_w, 2),
        "h": round(btn_h, 2),
        "depth": round(btn_depth, 2),
    })

# Display window (above buttons)
display_v = buttons_v + btn_h + gap_db  # 4.606
display_u = right_u_start + (right_w - display_w) / 2.0  # 38.81

features.append({
    "kind": "recess",
    "u": round(display_u, 2),
    "v": round(display_v, 2),
    "w": round(display_w, 2),
    "h": round(display_h, 2),
    "depth": round(display_depth, 2),
})

DESIGN["features"] = features