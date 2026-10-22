DESIGN = {
    "name": "storage_server_2u",
    "units": 2,
    "depth": 100.0,
    "handles": "loop",
    "features": []
}

H = 2 * 5.556 - 0.3
usable_v_min = 0.8
usable_v_max = H - 0.8

features = []

# Left control strip
strip_u = 3.8
strip_w = 6.0 - 3.8
strip_v = usable_v_min
strip_h = usable_v_max - usable_v_min
strip_depth = 0.6

features.append({
    "kind": "recess",
    "u": round(strip_u, 2),
    "v": round(strip_v, 2),
    "w": round(strip_w, 2),
    "h": round(strip_h, 2),
    "depth": strip_depth
})

# Power button inside strip
# Top 0.9 below strip top. Strip top v is strip_v + strip_h.
power_h = 1.2
power_depth = 0.8
power_top_v = (strip_v + strip_h) - 0.9
power_v = power_top_v - power_h
# Centered horizontally in strip? "nested bosses spanning the full strip width (margin 0 left/right)"
# Wait, the prompt says: "nested bosses spanning the full strip width (margin 0 left/right)".
# This implies the boss width equals the strip width.
power_w = strip_w
power_u = strip_u

features.append({
    "kind": "boss",
    "u": round(power_u, 2),
    "v": round(power_v, 2),
    "w": round(power_w, 2),
    "h": round(power_h, 2),
    "depth": power_depth
})

# 3 Status lights
# "3 status lights h 0.9, 0.9 apart below it"
# Below power button.
# Power button bottom is power_v.
# First light top should be 0.9 below power button bottom? Or just placed in a sequence?
# "0.9 apart below it" usually means gap between previous and current is 0.9.
# So, Light 1 top = Power bottom - 0.9.
light_h = 0.9
light_depth = 0.4
light_w = strip_w # Spanning full strip width
light_u = strip_u

current_v_top = power_v - 0.9
for i in range(3):
    light_v = current_v_top - light_h
    features.append({
        "kind": "boss",
        "u": round(light_u, 2),
        "v": round(light_v, 2),
        "w": round(light_w, 2),
        "h": round(light_h, 2),
        "depth": light_depth
    })
    current_v_top = light_v - 0.9

# Drive Area
# u 6.9..56.2
# 4 columns x 3 rows
# 0.9 gaps
# tray w = (49.3 - 3*0.9)/4
# tray h = (9.21 - 2*0.9)/3

drive_area_u_start = 6.9
drive_area_u_end = 56.2
drive_area_v_start = usable_v_min # 0.8
drive_area_v_end = usable_v_max # 10.012

# Calculate tray dimensions
total_w = drive_area_u_end - drive_area_u_start # 49.3
total_h = drive_area_v_end - drive_area_v_start # 9.212

tray_w = (total_w - 3 * 0.9) / 4
tray_h = (total_h - 2 * 0.9) / 3

# Place trays
for row in range(3):
    for col in range(4):
        tray_u = drive_area_u_start + col * (tray_w + 0.9)
        tray_v = drive_area_v_start + row * (tray_h + 0.9)
        
        # Tray Recess
        tray_recess_depth = 0.6
        features.append({
            "kind": "recess",
            "u": round(tray_u, 2),
            "v": round(tray_v, 2),
            "w": round(tray_w, 2),
            "h": round(tray_h, 2),
            "depth": tray_recess_depth
        })
        
        # Latch Boss
        # w 2.2, right edge 0.9 from tray right edge
        latch_w = 2.2
        latch_depth = 0.8
        latch_right_edge = tray_u + tray_w - 0.9
        latch_u = latch_right_edge - latch_w
        # Nested with margin 0 at top and bottom (same v and h as tray)
        latch_v = tray_v
        latch_h = tray_h
        
        features.append({
            "kind": "boss",
            "u": round(latch_u, 2),
            "v": round(latch_v, 2),
            "w": round(latch_w, 2),
            "h": round(latch_h, 2),
            "depth": latch_depth
        })
        
        # Honeycomb Vent Recess
        # depth 1.3, from tray_u + 0.9 to latch_u - 0.9
        vent_depth = 1.3
        vent_u = tray_u + 0.9
        vent_right_edge = latch_u - 0.9
        vent_w = vent_right_edge - vent_u
        # Nested with margin 0 at top and bottom (same v and h as tray)
        vent_v = tray_v
        vent_h = tray_h
        
        features.append({
            "kind": "recess",
            "u": round(vent_u, 2),
            "v": round(vent_v, 2),
            "w": round(vent_w, 2),
            "h": round(vent_h, 2),
            "depth": vent_depth
        })

DESIGN["features"] = features