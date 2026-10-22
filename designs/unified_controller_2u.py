DESIGN = {
    "name": "unified_controller_2u",
    "units": 2,
    "depth": 100.0,
    "handles": False,
    "features": [],
    "bezel": {"features": []}
}

def build_design():
    # Constants
    H = 2 * 5.556 - 0.3  # 10.812 -> rounded to 10.81 in spec description, but calculation is precise
    # Spec says H = 10.81 for 2U. Let's use the formula.
    # 2 * 5.556 - 0.3 = 11.112 - 0.3 = 10.812
    
    # Usable area
    u_min = 3.8
    u_max = 56.2
    v_min = 0.8
    v_max = H - 0.8
    
    # Carrier layout
    # 24 carriers across u 3.8..56.2
    # Total width available = 56.2 - 3.8 = 52.4
    # 24 carriers, 23 gaps of 0.9
    # Carrier width w_c = (52.4 - 23 * 0.9) / 24
    total_gaps_width = 23 * 0.9
    carrier_w = (52.4 - total_gaps_width) / 24
    
    # Carrier height: full usable height
    carrier_h = v_max - v_min
    
    features = []
    
    for i in range(24):
        # Calculate carrier position
        c_u = u_min + i * (carrier_w + 0.9)
        c_v = v_min
        
        # Carrier Recess
        # Depth 0.6
        # Spans full width and height
        carrier_recess = {
            "kind": "recess",
            "u": round(c_u, 2),
            "v": round(c_v, 2),
            "w": round(carrier_w, 2),
            "h": round(carrier_h, 2),
            "depth": 0.6
        }
        features.append(carrier_recess)
        
        # Features inside the carrier recess
        # Margin to edges is 0 (spec: "nested features spanning the FULL carrier width (margin 0 left/right)")
        # This implies the internal features also have margin 0 horizontally? 
        # Spec says: "nested features spanning the FULL carrier width (margin 0 left/right)"
        # And "nested features ... margin to each edge of the parent is exactly 0 or >= 0.9"
        # So horizontal margin 0 is allowed.
        
        # 1. Top latch boss
        # h 1.4, top edge 0.9 below the carrier top, depth 0.8
        # Carrier top v = c_v + carrier_h
        # Latch top v = c_v + carrier_h - 0.9
        # Latch bottom v = Latch top v - 1.4
        latch_h = 1.4
        latch_top_v = c_v + carrier_h - 0.9
        latch_v = latch_top_v - latch_h
        latch_boss = {
            "kind": "boss",
            "u": round(c_u, 2),       # Margin 0 left
            "v": round(latch_v, 2),
            "w": round(carrier_w, 2), # Margin 0 right
            "h": round(latch_h, 2),
            "depth": 0.8
        }
        features.append(latch_boss)
        
        # 2. Label boss
        # h 1.0, bottom edge at carrier_v + 0.9, depth 0.4
        label_h = 1.0
        label_v = c_v + 0.9
        label_boss = {
            "kind": "boss",
            "u": round(c_u, 2),       # Margin 0 left
            "v": round(label_v, 2),
            "w": round(carrier_w, 2), # Margin 0 right
            "h": round(label_h, 2),
            "depth": 0.4
        }
        features.append(label_boss)
        
        # 3. "Cut-out" recess
        # Depth 1.3, from 0.9 below the latch down to 2.8 above the carrier bottom
        # "from 0.9 below the latch" -> Top of cut-out
        # Latch bottom is at latch_v.
        # Cut-out top = latch_v - 0.9
        # "down to 2.8 above the carrier bottom" -> Bottom of cut-out
        # Cut-out bottom = c_v + 2.8
        
        cutout_top_v = latch_v - 0.9
        cutout_bottom_v = c_v + 2.8
        cutout_h = cutout_top_v - cutout_bottom_v
        
        # Check if valid height
        if cutout_h >= 0.8:
            cutout_recess = {
                "kind": "recess",
                "u": round(c_u, 2),       # Margin 0 left
                "v": round(cutout_bottom_v, 2),
                "w": round(carrier_w, 2), # Margin 0 right
                "h": round(cutout_h, 2),
                "depth": 1.3
            }
            features.append(cutout_recess)
            
    DESIGN["features"] = features

build_design()
