DESIGN = {
    "name": "storage_server_4u",
    "units": 4,
    "depth": 105.0,
    "handles": "loop",
    "features": []
}

H = 4 * 5.556 - 0.3 # 21.924 -> 21.92
usable_v_min = 0.8
usable_v_max = H - 0.8 # 21.124 -> 21.12

features = []

# Left control strip u 3.8..6.0 (width 2.2)
# Strip recess: v 8.0 to 20.2, depth 0.6
strip_u = 3.8
strip_w = 2.2
strip_v = 8.0
strip_h = 12.2 # 20.2 - 8.0
features.append({
    "kind": "recess",
    "u": round(strip_u, 2),
    "v": round(strip_v, 2),
    "w": round(strip_w, 2),
    "h": round(strip_h, 2),
    "depth": 0.6
})

# Power button boss inside strip
# Top 0.9 below strip top (20.2). Height 1.2.
# Bottom = 20.2 - 0.9 - 1.2 = 18.1
btn_w = 1.2
btn_h = 1.2
btn_u = round(strip_u + (strip_w - btn_w) / 2, 2) # Centered horizontally
btn_v = round(20.2 - 0.9 - btn_h, 2)
features.append({
    "kind": "boss",
    "u": btn_u,
    "v": btn_v,
    "w": btn_w,
    "h": btn_h,
    "depth": 0.8
})

# Status lights: 4 bosses, 0.9x0.9, stacked 0.9 apart (center-to-center? or edge-to-edge?)
# "stacked 0.9 apart" usually implies pitch or gap. Given "margin >= 0.9 from strip edges... make lights span full width", 
# and "siblings ... >= 0.9 apart". Let's assume vertical spacing between features is 0.9 (gap).
# Light h = 0.9. Gap = 0.9. Pitch = 1.8.
# Stack starts below button. Button bottom is 18.1.
# First light top should be >= 0.9 away from button bottom? "siblings inside a parent are >= 0.9 apart".
# So gap between button and first light is 0.9.
# Light 1 Top = 18.1 - 0.9 = 17.2. Bottom = 17.2 - 0.9 = 16.3.
# Light 2 Top = 16.3 - 0.9 = 15.4. Bottom = 15.4 - 0.9 = 14.5.
# ...

light_w = 0.9 # Span full width? "make the lights and button span the full strip width instead, margin 0 left/right"
# Strip width is 2.2. Light width 0.9 does not span full width.
# Re-reading: "margin >= 0.9 from strip edges horizontally means the strip is only 2.2 wide: make the lights and button span the full strip width instead, margin 0 left/right"
# This implies if we tried to keep 0.9 margins, we'd have no room for 1.2/0.9 items? 
# Strip is 2.2 wide. Item 1.2 wide. Margin = (2.2-1.2)/2 = 0.5. This is < 0.9.
# The instruction says: "make the lights and button span the full strip width instead, margin 0 left/right".
# So Button W should be 2.2? Light W should be 2.2?
# But spec said "power-button boss 1.2x1.2". And "status-light bosses 0.9x0.9".
# This is a contradiction in the prompt text vs standard interpretation.
# "make the lights and button span the full strip width" -> W = 2.2.
# But earlier it said "1.2x1.2" and "0.9x0.9".
# Let's look at the nesting rule: "margin to each edge of the parent is exactly 0 or >= 0.9".
# If I keep W=1.2, margin is 0.5 (invalid).
# If I make W=2.2, margin is 0 (valid).
# The prompt says: "make the lights and button span the full strip width instead". This overrides the specific dimensions given earlier for the purpose of fitting in the strip? 
# Or does it mean center them? No, "margin 0 left/right".
# I will follow the explicit instruction to span full width (W=2.2) to satisfy the margin rule.

btn_w = 2.2
btn_u = round(strip_u, 2) # Margin 0
btn_v = round(20.2 - 0.9 - btn_h, 2) # Height still 1.2? "power-button boss 1.2x1.2". 
# If W changes to 2.2, H stays 1.2.
features[-1] = {
    "kind": "boss",
    "u": btn_u,
    "v": btn_v,
    "w": round(btn_w, 2),
    "h": round(btn_h, 2),
    "depth": 0.8
}

light_w = 2.2 # Span full width
light_h = 0.9
# Vertical placement:
# Button Bottom = 18.1.
# Gap >= 0.9. 
curr_v_top = btn_v - 0.9
for i in range(4):
    l_v = curr_v_top - light_h
    features.append({
        "kind": "boss",
        "u": round(strip_u, 2),
        "v": round(l_v, 2),
        "w": round(light_w, 2),
        "h": round(light_h, 2),
        "depth": 0.8 # Assuming same depth as button or standard boss? Prompt didn't specify light depth, just size. Use 0.8.
    })
    curr_v_top = l_v - 0.9

# Drive Area u 6.9..56.2
drive_u_start = 6.9
drive_u_end = 56.2
cols = 4
rows = 6
gap = 0.9

total_w = drive_u_end - drive_u_start # 49.3
tray_w = (total_w - (cols - 1) * gap) / cols
# tray_w = (49.3 - 2.7)/4 = 46.6/4 = 11.65

total_h = 20.32 # From prompt: usable v 0.8..21.12 is 20.32 height? 
# Prompt says: "tray h = (20.32 - 5*0.9)/6".
# Let's verify drive area vertical bounds.
# Control strip is at u 3.8..6.0. Drive area starts at u 6.9.
# Vertical extent of drive area? Prompt says "Drive area u 6.9..56.2: ... tray h = (20.32 - 5*0.9)/6".
# It doesn't explicitly state v start/end for the grid, but implies it fills the usable height or a specific block.
# Usable H is 21.92. Min v 0.8, Max v 21.12. Total 20.32.
# So the grid spans the full usable vertical height.
grid_v_start = 0.8
tray_h = (20.32 - (rows - 1) * gap) / rows
# tray_h = (20.32 - 4.5)/6 = 15.82/6 = 2.6366...

for r in range(rows):
    for c in range(cols):
        t_u = drive_u_start + c * (tray_w + gap)
        t_v = grid_v_start + r * (tray_h + gap)
        
        # Tray Recess
        features.append({
            "kind": "recess",
            "u": round(t_u, 2),
            "v": round(t_v, 2),
            "w": round(tray_w, 2),
            "h": round(tray_h, 2),
            "depth": 0.6
        })
        
        # Nested: Honeycomb vent recess
        # Depth 1.3 (> 0.6)
        # Margin 0.9 left/right, margin 0 top
        # Height 0.9
        v_w = tray_w - 2 * 0.9
        v_h = 0.9
        v_u = t_u + 0.9
        v_v = t_v + tray_h - v_h # Top aligned (margin 0 at top)
        
        features.append({
            "kind": "recess",
            "u": round(v_u, 2),
            "v": round(v_v, 2),
            "w": round(v_w, 2),
            "h": round(v_h, 2),
            "depth": 1.3
        })
        
        # Latch Boss
        # w 2.2, h = tray_h - 1.8 (fills rest below vent gap)
        # Vent is at top. Gap between vent and latch? 
        # Prompt: "h = tray_h - 1.8 (it fills the rest below the vent gap)".
        # Vent h=0.9. If latch starts immediately below vent, total used = 0.9 + latch_h.
        # If latch_h = tray_h - 1.8, then space above latch is 1.8. 
        # Vent takes 0.9 at top. Remaining space for gap between vent and latch = 1.8 - 0.9 = 0.9.
        # This satisfies "siblings >= 0.9 apart".
        # Margin 0 at bottom. Right edge 0.9 from tray right edge.
        
        l_w = 2.2
        l_h = tray_h - 1.8
        l_v = t_v # Margin 0 at bottom
        l_u = t_u + tray_w - 0.9 - l_w # Right edge 0.9 from tray right
        
        features.append({
            "kind": "boss",
            "u": round(l_u, 2),
            "v": round(l_v, 2),
            "w": round(l_w, 2),
            "h": round(l_h, 2),
            "depth": 0.8
        })
        
        # Trim Boss
        # From tray_u + 0.9 to latch_u - 0.9
        # Same v and h as latch
        tr_v = l_v
        tr_h = l_h
        tr_u = t_u + 0.9
        tr_w = (l_u - 0.9) - tr_u
        
        features.append({
            "kind": "boss",
            "u": round(tr_u, 2),
            "v": round(tr_v, 2),
            "w": round(tr_w, 2),
            "h": round(tr_h, 2),
            "depth": 0.4
        })

DESIGN["features"] = features

