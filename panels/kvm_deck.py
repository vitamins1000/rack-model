PANEL = {
    "name": "kvm_deck",
    "features": []
}

# 1. Two mouse-button bosses
for u in [16.5, 21.5]:
    PANEL["features"].append({
        "kind": "boss",
        "u": round(u, 2),
        "v": round(0.9, 2),
        "w": round(4.0, 2),
        "h": round(1.4, 2),
        "depth": round(0.4, 2)
    })

# 2. Trackpad recess
PANEL["features"].append({
    "kind": "recess",
    "u": round(16.5, 2),
    "v": round(3.2, 2),
    "w": round(9.0, 2),
    "h": round(6.0, 2),
    "depth": round(0.4, 2)
})

# 3. Keyboard keys
# Row 0 special case: Spacebar replaces cols 5-9
for r in range(5):
    v = 13.0 + r * 2.4
    if r == 0:
        # Add normal keys for c not in [5, 6, 7, 8, 9]
        for c in range(15):
            if c not in [5, 6, 7, 8, 9]:
                u = 3.4 + c * 2.4
                PANEL["features"].append({
                    "kind": "boss",
                    "u": round(u, 2),
                    "v": round(v, 2),
                    "w": round(1.6, 2),
                    "h": round(1.6, 2),
                    "depth": round(0.4, 2)
                })
        # Add spacebar
        PANEL["features"].append({
            "kind": "boss",
            "u": round(15.4, 2),
            "v": round(13.0, 2),
            "w": round(11.2, 2),
            "h": round(1.6, 2),
            "depth": round(0.4, 2)
        })
    else:
        for c in range(15):
            u = 3.4 + c * 2.4
            PANEL["features"].append({
                "kind": "boss",
                "u": round(u, 2),
                "v": round(v, 2),
                "w": round(1.6, 2),
                "h": round(1.6, 2),
                "depth": round(0.4, 2)
            })

# 4. Function-key row
for c in range(15):
    u = 3.4 + c * 2.4
    PANEL["features"].append({
        "kind": "boss",
        "u": round(u, 2),
        "v": round(25.3, 2),
        "w": round(1.6, 2),
        "h": round(0.9, 2),
        "depth": round(0.4, 2)
    })

# 5. Status-light bosses
for u in [3.4, 5.2, 7.0]:
    PANEL["features"].append({
        "kind": "boss",
        "u": round(u, 2),
        "v": round(30.0, 2),
        "w": round(0.9, 2),
        "h": round(0.9, 2),
        "depth": round(0.4, 2)
    })