import math

def floor2(x):
    return math.floor(x * 100) / 100

DESIGN = {
    "name": "flash_array_3u",
    "units": 3,
    "depth": 95.0,
    "handles": False,
    "features": []
}

f = DESIGN["features"]

# H = 16.37 (approx 3*5.556 - 0.3 = 16.368)
# Usable v: 0.8 .. 15.57

# 1. TOP BAND
# Upper row: v 13.77..15.57 (h=1.8)
# Lower row: v 11.07..12.87 (h=1.8)
# Modules across u 3.8..46.0
# Module width w_mod = (42.2 - 3*0.9)/4 = (42.2 - 2.7)/4 = 39.5/4 = 9.875

w_mod_raw = (42.2 - 3 * 0.9) / 4
w_mod = floor2(w_mod_raw) # Floor to 2 decimals
gap = 0.9

rows_v = [13.77, 11.07]
h_row = 1.8

for v_row in rows_v:
    u_cursor = 3.8
    for i in range(4):
        # Module Recess
        mod_u = floor2(u_cursor)
        mod_v = v_row
        mod_w = w_mod
        mod_h = h_row
        
        f.append({
            "kind": "recess",
            "u": mod_u,
            "v": mod_v,
            "w": mod_w,
            "h": mod_h,
            "depth": 0.6
        })
        
        # Nested features inside module
        
        # 1. Logo Boss
        # u = module_u + 0.9, w 1.2, depth 0.4
        # Margin top/bottom 0 -> same v and h as module
        logo_u_raw = mod_u + 0.9
        logo_u = floor2(logo_u_raw)
        logo_v = mod_v
        logo_w = 1.2
        logo_h = mod_h
        
        f.append({
            "kind": "boss",
            "u": logo_u,
            "v": logo_v,
            "w": logo_w,
            "h": logo_h,
            "depth": 0.4
        })
        
        # 2. Handle Boss
        # w 0.9, u = module_right - 0.9 - 0.9 = mod_u + mod_w - 1.8
        # depth 0.8
        handle_w = 0.9
        handle_u_raw = mod_u + mod_w - 0.9 - 0.9
        handle_u = floor2(handle_u_raw)
        handle_v = mod_v
        handle_h = mod_h
        
        f.append({
            "kind": "boss",
            "u": handle_u,
            "v": handle_v,
            "w": handle_w,
            "h": handle_h,
            "depth": 0.8
        })
        
        # 3. Window Recess
        # depth 1.2
        # from u = module_u + 3.0 to (handle_u - 0.9)
        win_u_raw = mod_u + 3.0
        win_u = floor2(win_u_raw)
        win_right_raw = handle_u - 0.9
        win_right = floor2(win_right_raw)
        win_w_raw = win_right - win_u
        win_w = floor2(win_w_raw)
        win_v = mod_v
        win_h = mod_h
        
        if win_w >= 0.8: # Ensure valid size
             f.append({
                "kind": "recess",
                "u": win_u,
                "v": win_v,
                "w": win_w,
                "h": win_h,
                "depth": 1.2
            })
        
        # Advance cursor by ROUNDED size + gap
        u_cursor += mod_w + gap

# 2. CONTROL PANEL (Top-level features)
# Buttons: 1.2x1.2, depth 0.8
f.append({"kind": "boss", "u": 47.3, "v": 14.0, "w": 1.2, "h": 1.2, "depth": 0.8})
f.append({"kind": "boss", "u": 49.4, "v": 14.0, "w": 1.2, "h": 1.2, "depth": 0.8})

# Status lights: 0.9x0.9, depth 0.4
f.append({"kind": "boss", "u": 47.3, "v": 11.3, "w": 0.9, "h": 0.9, "depth": 0.4})
f.append({"kind": "boss", "u": 49.1, "v": 11.3, "w": 0.9, "h": 0.9, "depth": 0.4})
f.append({"kind": "boss", "u": 50.9, "v": 11.3, "w": 0.9, "h": 0.9, "depth": 0.4})

# Network port: 1.8x1.8, depth 1.2
f.append({"kind": "recess", "u": 52.7, "v": 11.3, "w": 1.8, "h": 1.8, "depth": 1.2})

# USB: 1.6x0.9, depth 1.2
f.append({"kind": "recess", "u": 52.7, "v": 14.0, "w": 1.6, "h": 0.9, "depth": 1.2})

# 3. LOWER BAND
# v 0.8..10.17 (Height = 9.37)
# Columns across u 3.8..56.2 (Width = 52.4)
# 23 columns, 0.9 gaps
# col_w = (52.4 - 22*0.9)/23

col_w_raw = (52.4 - 22 * 0.9) / 23
col_w = floor2(col_w_raw) # Floor to 2 decimals

band_v = 0.8
band_h_raw = 10.17 - 0.8
band_h = floor2(band_h_raw) # Floor to 2 decimals

# Column types: 4 modules, vent, 4 modules, vent, 4 modules, vent, 8 modules
col_types = ['module']*4 + ['vent'] + ['module']*4 + ['vent'] + ['module']*4 + ['vent'] + ['module']*8

u_cursor = 3.8

for ctype in col_types:
    col_u = floor2(u_cursor)
    
    if ctype == 'module':
        # Module Recess (Full band height)
        f.append({
            "kind": "recess",
            "u": col_u,
            "v": band_v,
            "w": col_w,
            "h": band_h,
            "depth": 0.6
        })
        
        # Nested Features
        
        # Top Latch Boss: h 0.9, margin 0.9 from top
        # Top of module is band_v + band_h
        latch_v_raw = band_v + band_h - 0.9 - 0.9
        latch_v = floor2(latch_v_raw)
        latch_h = 0.9
        latch_w = col_w # margin 0 left/right
        
        f.append({
            "kind": "boss",
            "u": col_u,
            "v": latch_v,
            "w": latch_w,
            "h": latch_h,
            "depth": 0.8
        })
        
        # Bottom Status Boss: h 0.9, bottom at module_v + 0.9
        status_v_raw = band_v + 0.9
        status_v = floor2(status_v_raw)
        status_h = 0.9
        status_w = col_w
        
        f.append({
            "kind": "boss",
            "u": col_u,
            "v": status_v,
            "w": status_w,
            "h": status_h,
            "depth": 0.4
        })
        
        # Handle Boss: depth 0.8
        # From 0.9 below latch down to 2.7 above module bottom
        # Latch bottom is latch_v. So handle top = latch_v - 0.9
        # Module bottom is band_v. Handle bottom = band_v + 2.7
        handle_top_raw = latch_v - 0.9
        handle_top = floor2(handle_top_raw)
        handle_bottom_raw = band_v + 2.7
        handle_bottom = floor2(handle_bottom_raw)
        
        if handle_top > handle_bottom:
            h_h_raw = handle_top - handle_bottom
            h_h = floor2(h_h_raw)
            f.append({
                "kind": "boss",
                "u": col_u,
                "v": handle_bottom,
                "w": col_w,
                "h": h_h,
                "depth": 0.8
            })
            
    elif ctype == 'vent':
        # Vent: Column of horizontal slot recesses
        # Each col_w wide and 0.8 tall, 0.9 apart (gap between slots)
        # Filling band height
        
        v_slot_cursor = band_v
        while True:
            # Check if a slot fits starting at v_slot_cursor
            # Slot height 0.8
            if v_slot_cursor + 0.8 <= band_v + band_h + 1e-9:
                f.append({
                    "kind": "recess",
                    "u": col_u,
                    "v": floor2(v_slot_cursor),
                    "w": col_w,
                    "h": 0.8,
                    "depth": 1.0
                })
                # Advance by height + gap
                v_slot_cursor += 0.8 + 0.9
            else:
                break
                
    u_cursor += col_w + gap