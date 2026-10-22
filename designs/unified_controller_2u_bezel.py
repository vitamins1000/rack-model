import math

def main():
    units = 2
    H = 2 * 5.556 - 0.3
    features = []
    
    # 1. End caps
    # Left cap recess
    lc_u, lc_v, lc_w, lc_h, lc_d = 3.8, 0.8, 5.2, 9.21, 0.6
    features.append({"kind": "recess", "u": lc_u, "v": lc_v, "w": lc_w, "h": lc_h, "depth": lc_d})
    # Left finger-grip slot
    lfg_w, lfg_h, lfg_d = 1.4, 5.6, 1.2
    lfg_u = lc_u + 1.9
    lfg_v = lc_v + (lc_h - lfg_h) / 2
    features.append({"kind": "recess", "u": lfg_u, "v": lfg_v, "w": lfg_w, "h": lfg_h, "depth": lfg_d})
    
    # Right cap recess
    rc_u, rc_v, rc_w, rc_h, rc_d = 51.0, 0.8, 5.2, 9.21, 0.6
    features.append({"kind": "recess", "u": rc_u, "v": rc_v, "w": rc_w, "h": rc_h, "depth": rc_d})
    # Right finger-grip slot
    rfg_w, rfg_h, rfg_d = 1.4, 5.6, 1.2
    rfg_u = rc_u + 1.9
    rfg_v = rc_v + (rc_h - rfg_h) / 2
    features.append({"kind": "recess", "u": rfg_u, "v": rfg_v, "w": rfg_w, "h": rfg_h, "depth": rfg_d})
    
    # 2. Badge bar
    bb_u, bb_v, bb_w, bb_h, bb_d = 9.9, 4.21, 14.1, 2.4, 0.8
    features.append({"kind": "boss", "u": bb_u, "v": bb_v, "w": bb_w, "h": bb_h, "depth": bb_d})
    
    # 3. Diamond field
    zone_u_min, zone_u_max = 9.9, 50.1
    zone_v_min, zone_v_max = 0.8, 10.01
    
    keep_outs = [
        {"u": bb_u, "v": bb_v, "w": bb_w, "h": bb_h}
    ]
    
    hole_w, hole_h = 3.2, 1.5
    
    # Loop rows and columns generously
    # v_c = 0.8 + 0.75 + r * 1.65 => v_c = 1.55 + r * 1.65
    # u_c = 9.9 + 0.65 + 1.6 + c * 4.2 => u_c = 12.15 + c * 4.2 (even rows)
    #       u_c = 14.25 + c * 4.2 (odd rows)
    
    r = 0
    while True:
        v_c = 1.55 + r * 1.65
        # If the bottom of the hole is already above the zone, stop
        if v_c - hole_h / 2 > zone_v_max:
            break
            
        # Determine offset for u_c based on row parity
        u_offset = 2.1 if (r % 2 == 1) else 0.0
        
        c = -2 # Start a bit left
        while True:
            u_c = 12.15 + c * 4.2 + u_offset
            
            # If the left of the hole is already right of the zone, stop this row
            if u_c - hole_w / 2 > zone_u_max:
                break
                
            # Calculate box
            h_u = u_c - hole_w / 2
            h_v = v_c - hole_h / 2
            
            # Check if box is inside zone
            if h_u >= zone_u_min and h_u + hole_w <= zone_u_max and \
               h_v >= zone_v_min and h_v + hole_h <= zone_v_max:
                
                # Check keep-out distance
                valid = True
                for ko in keep_outs:
                    # Calculate gaps
                    gap_u = max(ko["u"] - (h_u + hole_w), h_u - (ko["u"] + ko["w"]), 0)
                    gap_v = max(ko["v"] - (h_v + hole_h), h_v - (ko["v"] + ko["h"]), 0)
                    
                    if max(gap_u, gap_v) < 0.9:
                        valid = False
                        break
                
                if valid:
                    features.append({
                        "kind": "hole", 
                        "u": round(h_u, 2), 
                        "v": round(h_v, 2), 
                        "w": hole_w, 
                        "h": hole_h, 
                        "depth": 0,
                        "shape": "diamond"
                    })
            c += 1
        r += 1

    BEZEL = {"units": units, "features": features}
    return BEZEL

BEZEL = main()