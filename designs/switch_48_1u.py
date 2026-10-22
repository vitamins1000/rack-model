DESIGN = {
    "name": "switch_48_1u",
    "units": 1,
    "depth": 50.0,
    "handles": True,
    "features": []
}

# H calculation for 1U: 1 * 5.556 - 0.3 = 5.256
H = 5.256

features = []

# 1. 48 RJ45 ports in 2 rows of 24
# Lower row at v=0.9, Upper row at v=2.8
# Column c = 0..23 has u = 3.8 + c * 2.0
# Recess w=1.2, h=1.0, depth=1.2

for c in range(24):
    u = round(3.8 + c * 2.0, 2)
    
    # Lower row
    features.append({
        "kind": "recess",
        "u": u,
        "v": 0.9,
        "w": 1.2,
        "h": 1.0,
        "depth": 1.2
    })
    
    # Upper row
    features.append({
        "kind": "recess",
        "u": u,
        "v": 2.8,
        "w": 1.2,
        "h": 1.0,
        "depth": 1.2
    })

# 2. 2 SFP uplink ports stacked at the right
# Recess u=52.6, w=2.0, h=1.0, depth=1.2
# At v=0.9 and v=2.8

features.append({
    "kind": "recess",
    "u": 52.6,
    "v": 0.9,
    "w": 2.0,
    "h": 1.0,
    "depth": 1.2
})

features.append({
    "kind": "recess",
    "u": 52.6,
    "v": 2.8,
    "w": 2.0,
    "h": 1.0,
    "depth": 1.2
})

DESIGN["features"] = features