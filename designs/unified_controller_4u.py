DESIGN = {
    "name": "unified_controller_4u",
    "units": 4,
    "depth": 100.0,
    "handles": False,
    "features": [],
}

# Constants derived from spec and design description
H = 21.92
U_START = 3.8
U_END = 56.2
V_START = 0.8
V_END = H - 0.8

ROWS_COUNT = 2
COLS_COUNT = 24

# Calculate row height and carrier width based on spec instructions
# Usable V for rows: 0.8 to 21.12 -> Height 20.32
# Row gap: 0.9
# Total vertical space for 2 rows + 1 gap = 2 * row_h + 0.9 = 20.32
# 2 * row_h = 19.42 => row_h = 9.71
row_h = (H - 1.6 - 0.9) / 2.0

# Usable U for carriers: 3.8 to 56.2 -> Width 52.4
# Carrier gaps: 23 * 0.9
# Total horizontal space for 24 carriers + 23 gaps = 24 * carrier_w + 23 * 0.9 = 52.4
# 24 * carrier_w = 52.4 - 20.7 = 31.7 => carrier_w = 31.7 / 24
carrier_w = (U_END - U_START - (COLS_COUNT - 1) * 0.9) / COLS_COUNT

# Define feature parameters relative to a carrier
# Carrier recess: depth 0.6, spans full carrier width (margin 0 left/right)
CARRIER_DEPTH = 0.6

# Latch boss: h 1.6, top edge 0.9 below carrier top, depth 0.8
LATCH_H = 1.6
LATCH_TOP_OFFSET = 0.9 # Distance from carrier top to latch top
LATCH_DEPTH = 0.8

# Cut-out recess: depth 1.3, from 0.9 below latch down to 2.8 above carrier bottom
CUTOUT_DEPTH = 1.3
CUTOUT_TOP_OFFSET = LATCH_TOP_OFFSET + LATCH_H + 0.9 # 0.9 below the latch
CUTOUT_BOTTOM_OFFSET = 2.8 # Above carrier bottom

# Label boss: h 1.0, bottom edge at carrier_v + 0.9, depth 0.4
LABEL_H = 1.0
LABEL_BOTTOM_OFFSET = 0.9
LABEL_DEPTH = 0.4

features = []

for r in range(ROWS_COUNT):
    # Calculate V start for this row
    if r == 0:
        row_v_start = V_START
    else:
        # Lower row starts at 0.8, upper row starts 0.8 + row_h + 0.9
        row_v_start = V_START + row_h + 0.9
    
    for c in range(COLS_COUNT):
        # Calculate U start for this carrier
        col_u_start = U_START + c * (carrier_w + 0.9)
        
        # 1. Carrier Recess
        # Spans full carrier width, margin 0 left/right relative to parent? 
        # Spec says "nested features spanning the FULL carrier width (margin 0 left/right)"
        # The carrier itself is a recess on the face.
        carrier = {
            "kind": "recess",
            "u": round(col_u_start, 2),
            "v": round(row_v_start, 2),
            "w": round(carrier_w, 2),
            "h": round(row_h, 2),
            "depth": CARRIER_DEPTH
        }
        features.append(carrier)
        
        # Nested features inside the carrier recess
        
        # 2. Top Latch Boss
        # Top edge is 0.9 below carrier top.
        # Carrier V range: [row_v_start, row_v_start + row_h]
        # Latch Top V = row_v_start + row_h - LATCH_TOP_OFFSET
        # Latch Bottom V = Latch Top V - LATCH_H
        latch_top_v = row_v_start + row_h - LATCH_TOP_OFFSET
        latch_bottom_v = latch_top_v - LATCH_H
        
        latch_boss = {
            "kind": "boss",
            "u": round(col_u_start, 2), # Margin 0 left/right
            "v": round(latch_bottom_v, 2),
            "w": round(carrier_w, 2),   # Full width
            "h": LATCH_H,
            "depth": LATCH_DEPTH
        }
        features.append(latch_boss)
        
        # 3. Cut-out Recess
        # From 0.9 below the latch down to 2.8 above the carrier bottom
        # Top of cutout: Latch Bottom V - 0.9
        # Bottom of cutout: row_v_start + CUTOUT_BOTTOM_OFFSET
        cutout_top_v = latch_bottom_v - 0.9
        cutout_bottom_v = row_v_start + CUTOUT_BOTTOM_OFFSET
        
        cutout_h = cutout_top_v - cutout_bottom_v
        
        cutout_recess = {
            "kind": "recess",
            "u": round(col_u_start, 2), # Margin 0 left/right
            "v": round(cutout_bottom_v, 2),
            "w": round(carrier_w, 2),   # Full width
            "h": round(cutout_h, 2),
            "depth": CUTOUT_DEPTH
        }
        features.append(cutout_recess)
        
        # 4. Label Boss
        # Bottom edge at carrier_v + 0.9
        label_bottom_v = row_v_start + LABEL_BOTTOM_OFFSET
        
        label_boss = {
            "kind": "boss",
            "u": round(col_u_start, 2), # Margin 0 left/right
            "v": round(label_bottom_v, 2),
            "w": round(carrier_w, 2),   # Full width
            "h": LABEL_H,
            "depth": LABEL_DEPTH
        }
        features.append(label_boss)

DESIGN["features"] = features
