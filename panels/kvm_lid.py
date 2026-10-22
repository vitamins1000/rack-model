PANEL = {
    "name": "kvm_lid",
    "features": [
        {
            "kind": "recess",
            "u": 2.6,
            "v": 6.0,
            "w": 38.2,
            "h": 27.4,
            "depth": 0.5
        },
        {
            "kind": "boss",
            "u": 4.0,
            "v": 3.0,
            "w": 0.9,
            "h": 0.9,
            "depth": 0.4
        }
    ]
}

for i in range(5):
    PANEL["features"].append({
        "kind": "boss",
        "u": round(28.0 + i * 1.8, 2),
        "v": 3.0,
        "w": 0.9,
        "h": 0.9,
        "depth": 0.4
    })