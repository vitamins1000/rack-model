import math

def build():
    features = []
    
    # Allowed zone
    u_min, u_max = 4.0, 56.5
    v_min, v_max = 4.0, 228.0
    
    # Rail bands (solid areas to avoid)
    # Band 1: v 76.0 .. 80.0
    # Band 2: v 152.0 .. 156.0
    # Condition: Skip if box_top > band_bottom - 0.9 AND box_bottom < band_top + 0.9
    
    bands = [
        (76.0, 80.0),
        (152.0, 156.0)
    ]
    
    tol = 1e-6
    
    for r in range(81): # 0 to 80
        v_c = 5.5 + r * 3.07
        
        for c in range(21): # 0 to 20
            u_c = 5.4 + c * 3.55
            if r % 2 == 1:
                u_c += 1.775
                
            # Hole dimensions
            w_hole = 2.6
            h_hole = 3.0
            
            # Box edges
            u_left = u_c - w_hole / 2.0
            v_bottom = v_c - h_hole / 2.0
            u_right = u_left + w_hole
            v_top = v_bottom + h_hole
            
            # Check allowed zone (with tolerance)
            if not (u_left >= u_min - tol and 
                    u_right <= u_max + tol and 
                    v_bottom >= v_min - tol and 
                    v_top <= v_max + tol):
                continue
                
            # Check rail bands
            skip = False
            for b_bot, b_top in bands:
                # Skip if overlapping with the exclusion zone around the band
                # Exclusion zone is [b_bot - 0.9, b_top + 0.9]
                # Overlap condition: box_top > excl_bottom AND box_bottom < excl_top
                if v_top > (b_bot - 0.9) and v_bottom < (b_top + 0.9):
                    skip = True
                    break
            
            if skip:
                continue
                
            # Add feature
            features.append({
                "kind": "hole",
                "shape": "hex",
                "u": round(u_left, 2),
                "v": round(v_bottom, 2),
                "w": round(w_hole, 2),
                "h": round(h_hole, 2),
                "depth": 0
            })
            
    return features

PANEL = {
    "name": "door",
    "features": build()
}