import math

def main():
    UNITS = 4
    H_TOTAL = 4 * 5.556 - 0.3  # 21.924
    
    features = []
    
    def is_inside(box, container, margin=0.8):
        bu, bv, bw, bh = box
        cu, cv, cw, ch = container
        
        if bu < cu - 1e-6: return False
        if bv < cv - 1e-6: return False
        if bu + bw > cu + cw + 1e-6: return False
        if bv + bh > cv + ch + 1e-6: return False
        
        return True

    def boxes_far_enough(box1, box2, margin=0.9):
        u1, v1, w1, h1 = box1
        u2, v2, w2, h2 = box2
        
        if u1 + w1 <= u2:
            dx = u2 - (u1 + w1)
        elif u2 + w2 <= u1:
            dx = u1 - (u2 + w2)
        else:
            dx = 0
            
        if v1 + h1 <= v2:
            dy = v2 - (v1 + h1)
        elif v2 + h2 <= v1:
            dy = v1 - (v2 + h2)
        else:
            dy = 0
            
        return max(dx, dy) >= margin

    # 1. End caps
    
    left_cap = {"kind": "recess", "u": 3.8, "v": 0.8, "w": 5.2, "h": 20.32, "depth": 0.6}
    features.append(left_cap)
    
    left_slot = {"kind": "recess", "u": 5.7, "v": 4.96, "w": 1.4, "h": 12.0, "depth": 1.2}
    features.append(left_slot)
    
    right_cap = {"kind": "recess", "u": 51.0, "v": 0.8, "w": 5.2, "h": 20.32, "depth": 0.6}
    features.append(right_cap)
    
    right_slot = {"kind": "recess", "u": 52.9, "v": 4.96, "w": 1.4, "h": 12.0, "depth": 1.2}
    features.append(right_slot)

    # 2. Badge Bar Boss
    badge = {"kind": "boss", "u": 9.9, "v": 9.46, "w": 14.1, "h": 3.0, "depth": 0.8}
    features.append(badge)

    # 3. Diamond Field
    
    zone_u_min = 9.9
    zone_u_max = 50.1
    zone_v_min = 0.8
    zone_v_max = 21.12
    
    keep_outs = [
        (badge["u"], badge["v"], badge["w"], badge["h"])
    ]
    
    hole_w = 3.2
    hole_h = 1.5
    
    # Row loop: v_c starts at bottom, increments by 1.65
    # Condition: box top passes 21.12? No, "Loop rows until the box top passes 21.12, keeping every row whose box fits."
    # This implies we generate rows as long as the potential top of the box (v_c + hole_h/2) is <= zone_v_max + small epsilon?
    # Or strictly: while v_c - hole_h/2 >= zone_v_min AND v_c + hole_h/2 <= zone_v_max.
    # The prompt says "Loop rows until the box top passes 21.12". This suggests a while loop or range that covers enough, 
    # and we filter by fit.
    
    r = 0
    while True:
        v_c = 0.8 + 0.75 + r * 1.65
        
        hole_v = v_c - hole_h / 2.0
        if hole_v < zone_v_min - 1e-9:
            r += 1
            continue
            
        # Check if box top exceeds limit significantly to break
        if hole_v + hole_h > zone_v_max + 1e-9:
             # Even if it doesn't fit, check if we've gone too far up?
             # The prompt says "Loop rows until the box top passes 21.12". 
             # So if v_c + 0.75 > 21.12, we stop generating further rows.
             break
        
        u_offset = 2.1 if (r % 2 != 0) else 0.0
        
        # Column loop
        # u_c = 9.9 + 0.65 + 1.6 + c * 4.2 + offset
        # Base u_c for c=0, even row: 9.9 + 0.65 + 1.6 = 12.15
        # Left edge of hole at c=0, even: 12.15 - 1.6 = 10.55. Gap to 9.9 is 0.65. Correct.
        
        c_min = 0
        # Find max c roughly
        # u_c_max approx zone_u_max + 4.2
        c_max = int((zone_u_max - (9.9 + 0.65 + 1.6)) / 4.2) + 2
        
        for c in range(c_min, c_max + 1):
            u_c = 9.9 + 0.65 + 1.6 + c * 4.2 + u_offset
            
            hole_u = u_c - hole_w / 2.0
            hole_box = (hole_u, hole_v, hole_w, hole_h)
            
            # Check if inside allowed zone
            if not is_inside(hole_box, (zone_u_min, zone_v_min, zone_u_max - zone_u_min, zone_v_max - zone_v_min), margin=0.0):
                continue
                
            # Check keep-outs
            valid = True
            for ko in keep_outs:
                if not boxes_far_enough(hole_box, ko, margin=0.9):
                    valid = False
                    break
            
            if valid:
                features.append({
                    "kind": "hole",
                    "u": round(hole_u, 2),
                    "v": round(hole_v, 2),
                    "w": hole_w,
                    "h": hole_h,
                    "depth": 0,
                    "shape": "diamond"
                })
        
        r += 1

    BEZEL = {"units": UNITS, "features": features}
    
    return BEZEL

BEZEL = main()