DESIGN = {
    "name": "disk_shelf_4u",
    "units": 4,
    "depth": 100.0,
    "handles": False,
    "features": [],
}

# Usable area constants
U_MIN = 3.8
U_MAX = 56.2
V_MIN = 0.8
H_TOTAL = 4 * 5.556 - 0.3
V_MAX = H_TOTAL - 0.8

# Grid parameters
COLS = 4
ROWS = 6
GAP = 0.9

# Calculate carrier dimensions to fit within usable area with gaps
# Total width available: U_MAX - U_MIN
# Total height available: V_MAX - V_MIN
# Width per column: (Total Width - (COLS-1)*GAP) / COLS
# Height per row: (Total Height - (ROWS-1)*GAP) / ROWS

total_w = U_MAX - U_MIN
total_h = V_MAX - V_MIN

carrier_w = (total_w - (COLS - 1) * GAP) / COLS
carrier_h = (total_h - (ROWS - 1) * GAP) / ROWS

features = []

for c in range(COLS):
    for r in range(ROWS):
        # Carrier position
        cu = U_MIN + c * (carrier_w + GAP)
        cv = V_MIN + r * (carrier_h + GAP)
        
        # 1. Carrier Recess (Parent)
        # Depth 0.8
        features.append({
            "kind": "recess",
            "u": round(cu, 2),
            "v": round(cv, 2),
            "w": round(carrier_w, 2),
            "h": round(carrier_h, 2),
            "depth": 0.8
        })
        
        # Nested features inside the carrier
        
        # Define margins and sub-regions
        MARGIN = 0.9
        
        # Left Half: Vent Recess
        # Margin 0.9 on all sides (top, bottom, left, right relative to parent)
        vent_u = cu + MARGIN
        vent_v = cv + MARGIN
        vent_w = carrier_w / 2 - MARGIN * 2
        vent_h = carrier_h - MARGIN * 2
        
        # Check validity of vent (must be >= 0.8 w/h)
        if vent_w >= 0.8 and vent_h >= 0.8:
            features.append({
                "kind": "recess",
                "u": round(vent_u, 2),
                "v": round(vent_v, 2),
                "w": round(vent_w, 2),
                "h": round(vent_h, 2),
                "depth": 1.3  # Deeper than parent (0.8)
            })
        
        # Right Third: Handle Boss
        # "along the carrier's right third"
        # Margin 0.9 top/bottom, 0 at the right edge
        
        # Define the region for the handle
        # The handle is in the right third of the carrier width.
        # Region start u: cu + (2/3)*carrier_w
        # Region end u: cu + carrier_w
        
        # Handle Boss dimensions:
        # Depth 0.6
        # Margin 0 top/bottom? No, spec says "margin 0.9 top/bottom".
        # So handle v is cv + 0.9 to cv + carrier_h - 0.9
        # Handle u starts at cu + (2/3)*carrier_w + MARGIN? 
        # Spec: "margin 0.9 top/bottom, 0 at the right edge".
        # It doesn't explicitly state left margin for the handle region itself relative to the "right third" boundary, 
        # but since it's nested inside the carrier recess, and we want it distinct from the vent,
        # let's look at the geometry.
        
        # Vent occupies: u [cu+0.9, cu + carrier_w/2 - 0.9]
        # Right third starts at: cu + (2/3)*carrier_w
        
        # Is there a gap between Vent and Handle?
        # Vent right edge: cu + carrier_w/2 - 0.9
        # Handle left edge: ?
        
        # The spec says the handle is "along the carrier's right third".
        # Let's assume the handle boss fills the right third area, respecting top/bottom margins.
        # What about the left margin of the handle? 
        # The spec lists margins for the handle: "margin 0.9 top/bottom, 0 at the right edge".
        # It does not specify a left margin for the handle relative to the carrier or the vent.
        # However, Rule 2 says features not nested in each other must be >= 0.8 apart.
        # Vent and Handle are siblings inside the Carrier Recess.
        
        # Let's calculate positions carefully.
        
        # Vent Right Edge: cu + carrier_w/2 - MARGIN
        # Handle Left Edge: Must be >= Vent Right Edge + 0.8
        
        # Let's define the Handle based on "Right Third".
        # Right third u-range: [cu + (2/3)*carrier_w, cu + carrier_w]
        
        handle_depth = 0.6
        handle_v = cv + MARGIN
        handle_h = carrier_h - 2 * MARGIN
        
        # Handle U and W
        # "0 at the right edge" means handle_u + handle_w = cu + carrier_w
        # What is the left boundary? 
        # If we just use the right third, handle_u = cu + (2/3)*carrier_w.
        # Let's check if this leaves enough space from the vent.
        
        vent_right = cu + carrier_w / 2 - MARGIN
        handle_left = cu + (2 * carrier_w) / 3
        
        gap_between = handle_left - vent_right
        
        if gap_between < 0.8:
            # If they are too close, we might need to adjust. 
            # However, with standard 4U dimensions:
            # H_TOTAL ~ 21.922. V_MIN 0.8, V_MAX 21.122. Total H ~ 20.322.
            # Carrier H = (20.322 - 5*0.9)/6 = (20.322 - 4.5)/6 = 15.822/6 = 2.637 mm.
            # Total W = 52.4. Carrier W = (52.4 - 3*0.9)/4 = (52.4 - 2.7)/4 = 49.7/4 = 12.425 mm.
            
            # Vent Right: cu + 6.2125 - 0.9 = cu + 5.3125
            # Handle Left: cu + 8.2833
            # Gap: 2.97 mm. This is > 0.8. So no collision.
            
            handle_u = handle_left
            handle_w = (cu + carrier_w) - handle_u
            
            if handle_w >= 0.8 and handle_h >= 0.8:
                features.append({
                    "kind": "boss",
                    "u": round(handle_u, 2),
                    "v": round(handle_v, 2),
                    "w": round(handle_w, 2),
                    "h": round(handle_h, 2),
                    "depth": handle_depth
                })

DESIGN["features"] = features
