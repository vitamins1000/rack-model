features = []

# 1. Mesh zone: through holes ("kind": "hole", "depth": 0) with "shape": "hex_h"
# Zone limits: u 3.8..56.2, v 10.0..21.12
# Hole box: w 2.6, h 1.2
# Centers: row r -> v_c = 10.0 + 0.6 + r * 2.15; column c -> u_c = 3.8 + 1.3 + c * 3.55 (+ 1.775 on odd rows)
# Box left/bottom (u,v) derived from center: u = u_c - w/2, v = v_c - h/2

zone_u_min = 3.8
zone_u_max = 56.2
zone_v_min = 10.0
zone_v_max = 21.12

hole_w = 2.6
hole_h = 1.2

# Generous loop range for rows and columns
for r in range(-5, 15):
    v_c = 10.0 + 0.6 + r * 2.15
    for c in range(-5, 25):
        u_c = 3.8 + 1.3 + c * 3.55
        if r % 2 != 0: # Odd rows (assuming 0 is even, so 1, 3, ... are odd)
            u_c += 1.775
        
        # Calculate box coordinates
        u_box = u_c - hole_w / 2.0
        v_box = v_c - hole_h / 2.0
        
        # Check if box is completely inside the allowed zone
        if (u_box >= zone_u_min and 
            u_box + hole_w <= zone_u_max and 
            v_box >= zone_v_min and 
            v_box + hole_h <= zone_v_max):
            
            features.append({
                "kind": "hole",
                "u": round(u_box, 2),
                "v": round(v_box, 2),
                "w": hole_w,
                "h": hole_h,
                "depth": 0,
                "shape": "hex_h"
            })

# 2. Raised divider strip: boss u 3.8, v 8.2, w 52.4, h 0.9, depth 0.6
features.append({
    "kind": "boss",
    "u": 3.8,
    "v": 8.2,
    "w": 52.4,
    "h": 0.9,
    "depth": 0.6
})

# 3. Small plain badge: boss w 7.0, h 1.8, centred at u 30.0, v 4.6 (so u 26.5, v 3.7), depth 0.4
badge_w = 7.0
badge_h = 1.8
badge_u_c = 30.0
badge_v_c = 4.6

badge_u = badge_u_c - badge_w / 2.0
badge_v = badge_v_c - badge_h / 2.0

features.append({
    "kind": "boss",
    "u": round(badge_u, 2),
    "v": round(badge_v, 2),
    "w": badge_w,
    "h": badge_h,
    "depth": 0.4
})

BEZEL = {"units": 4, "features": features}