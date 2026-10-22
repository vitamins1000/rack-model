import math

DESIGN = {
    "name": "hybrid_array_4u",
    "units": 4,
    "depth": 100.0,
    "handles": False,
    "features": []
}

H = 21.92
U_MIN = 3.8
U_MAX = 56.2
V_MIN = 0.8
V_MAX = H - 0.8

COLS = 4
ROWS = 6
GAP = 0.9

TOTAL_W = U_MAX - U_MIN
TOTAL_H = V_MAX - V_MIN

# Exact calculation then floor to 2 decimals
CARRIER_W = math.floor(((TOTAL_W - (COLS - 1) * GAP) / COLS) * 100) / 100.0
CARRIER_H = math.floor(((TOTAL_H - (ROWS - 1) * GAP) / ROWS) * 100) / 100.0

features = DESIGN["features"]

for r in range(ROWS):
    for c in range(COLS):
        # Advance cursor by ROUNDED size + GAP, then floor position to 2 decimals
        u_start = math.floor((U_MIN + c * (CARRIER_W + GAP)) * 100) / 100.0
        v_start = math.floor((V_MIN + r * (CARRIER_H + GAP)) * 100) / 100.0
        
        is_bottom_row = (r == 0)
        is_right_most = (c == COLS - 1)
        
        # Determine type
        if not is_bottom_row:
            carrier_type = "HDD"
        else:
            if is_right_most:
                carrier_type = "HDD"
            else:
                carrier_type = "FLASH"

        # Parent Recess (Carrier Tray)
        parent_recess = {
            "kind": "recess",
            "u": u_start,
            "v": v_start,
            "w": CARRIER_W,
            "h": CARRIER_H,
            "depth": 0.6
        }
        features.append(parent_recess)

        if carrier_type == "HDD":
            # HDD Carrier Features:
            
            # 1. Green latch boss
            latch_u = math.floor((u_start + 0.9) * 100) / 100.0
            latch_v = v_start
            latch_w = 0.9
            latch_h = CARRIER_H
            
            latch_boss = {
                "kind": "boss",
                "u": latch_u,
                "v": latch_v,
                "w": latch_w,
                "h": latch_h,
                "depth": 0.8
            }
            features.append(latch_boss)

            # 2. Mesh recess
            mesh_u = math.floor((u_start + 2.7) * 100) / 100.0
            mesh_v = v_start
            mesh_w_exact = (u_start + CARRIER_W - 3.6) - mesh_u
            mesh_w = math.floor(mesh_w_exact * 100) / 100.0
            mesh_h = CARRIER_H
            
            mesh_recess = {
                "kind": "recess",
                "u": mesh_u,
                "v": mesh_v,
                "w": mesh_w,
                "h": mesh_h,
                "depth": 1.3
            }
            features.append(mesh_recess)

            # 3. Small release boss
            # u = carrier_right - 0.9 - 0.9 - 0.9
            release_u_exact = u_start + CARRIER_W - 2.7
            release_u = math.floor(release_u_exact * 100) / 100.0
            
            release_v = v_start
            release_w = 0.9
            release_h = CARRIER_H
            
            release_boss = {
                "kind": "boss",
                "u": release_u,
                "v": release_v,
                "w": release_w,
                "h": release_h,
                "depth": 0.6
            }
            features.append(release_boss)

        elif carrier_type == "FLASH":
            # Dual-flash carriers: recess depth 0.6 (parent already added).
            # Two nested deeper slot recesses (depth 1.3) side by side.
            
            inner_width_total = CARRIER_W - 3 * GAP
            slot_w = math.floor((inner_width_total / 2) * 100) / 100.0
            
            # Slot 1 (Left)
            slot1_u = math.floor((u_start + GAP) * 100) / 100.0
            slot1_v = v_start
            slot1_h = CARRIER_H
            
            slot1_recess = {
                "kind": "recess",
                "u": slot1_u,
                "v": slot1_v,
                "w": slot_w,
                "h": slot1_h,
                "depth": 1.3
            }
            features.append(slot1_recess)
            
            # Slot 2 (Right)
            slot2_u_exact = slot1_u + slot_w + GAP
            slot2_u = math.floor(slot2_u_exact * 100) / 100.0
            slot2_v = v_start
            slot2_h = CARRIER_H
            
            slot2_recess = {
                "kind": "recess",
                "u": slot2_u,
                "v": slot2_v,
                "w": slot_w,
                "h": slot2_h,
                "depth": 1.3
            }
            features.append(slot2_recess)

DESIGN["features"] = features