DESIGN = {
    "name": "storage_server_1u",
    "units": 1,
    "depth": 95.0,
    "handles": "loop",
    "features": []
}

H = 5.556 * 1 - 0.3
usable_v_min = 0.8
usable_v_max = H - 0.8
usable_h = usable_v_max - usable_v_min

# Left control strip
# 2 square button bosses 1.2x1.2 (depth 0.8) at (u 3.8, v 2.03) and (u 5.9, v 2.03)
DESIGN["features"].append({
    "kind": "boss",
    "u": 3.80,
    "v": 2.03,
    "w": 1.20,
    "h": 1.20,
    "depth": 0.8
})
DESIGN["features"].append({
    "kind": "boss",
    "u": 5.90,
    "v": 2.03,
    "w": 1.20,
    "h": 1.20,
    "depth": 0.8
})

# 2 status-light bosses 0.9x0.9 (depth 0.4) stacked at (u 8.0, v 1.0) and (u 8.0, v 2.8)
DESIGN["features"].append({
    "kind": "boss",
    "u": 8.00,
    "v": 1.00,
    "w": 0.90,
    "h": 0.90,
    "depth": 0.4
})
DESIGN["features"].append({
    "kind": "boss",
    "u": 8.00,
    "v": 2.80,
    "w": 0.90,
    "h": 0.90,
    "depth": 0.4
})

# Drive area u 10.3..56.2
drive_u_start = 10.3
drive_u_end = 56.2
drive_width_total = drive_u_end - drive_u_start
num_trays = 4
gap = 0.9
tray_w = (drive_width_total - (num_trays - 1) * gap) / num_trays

for i in range(num_trays):
    tray_u = drive_u_start + i * (tray_w + gap)
    tray_v = usable_v_min
    tray_w_val = tray_w
    tray_h_val = usable_h
    
    # Tray recess
    tray_recess = {
        "kind": "recess",
        "u": tray_u,
        "v": tray_v,
        "w": tray_w_val,
        "h": tray_h_val,
        "depth": 0.6
    }
    DESIGN["features"].append(tray_recess)
    
    # Nested features inside tray_recess
    
    # 1. Honeycomb vent recess: depth 1.3, margin 0.9 left and right, margin 0 at the top, height 0.9
    vent_margin_lr = 0.9
    vent_margin_top = 0.0
    vent_h = 0.9
    vent_w = tray_w_val - 2 * vent_margin_lr
    vent_u = tray_u + vent_margin_lr
    vent_v = tray_v + tray_h_val - vent_margin_top - vent_h
    
    vent_recess = {
        "kind": "recess",
        "u": vent_u,
        "v": vent_v,
        "w": vent_w,
        "h": vent_h,
        "depth": 1.3
    }
    DESIGN["features"].append(vent_recess)
    
    # 2. Latch boss: w 2.2, h = 3.66 - 1.8, margin 0 at the bottom, right edge 0.9 from the tray right edge, depth 0.8
    latch_w = 2.2
    latch_h = 3.66 - 1.8
    latch_margin_bottom = 0.0
    latch_margin_right = 0.9
    
    latch_u = tray_u + tray_w_val - latch_margin_right - latch_w
    latch_v = tray_v + latch_margin_bottom
    
    latch_boss = {
        "kind": "boss",
        "u": latch_u,
        "v": latch_v,
        "w": latch_w,
        "h": latch_h,
        "depth": 0.8
    }
    DESIGN["features"].append(latch_boss)
    
    # 3. Trim boss: from tray_u + 0.9 to latch_u - 0.9, same v and h as the latch, depth 0.4
    trim_u_start = tray_u + 0.9
    trim_u_end = latch_u - 0.9
    trim_w = trim_u_end - trim_u_start
    trim_v = latch_v
    trim_h = latch_h
    
    if trim_w >= 0.8:
        trim_boss = {
            "kind": "boss",
            "u": trim_u_start,
            "v": trim_v,
            "w": trim_w,
            "h": trim_h,
            "depth": 0.4
        }
        DESIGN["features"].append(trim_boss)
