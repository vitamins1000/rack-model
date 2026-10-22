DESIGN = {
    "name": "gpu_node_4u",
    "units": 4,
    "depth": 105.0,
    "handles": "loop",
    "features": [
        # TOP VENT BAND: One recess u 3.8, v 17.5, w 52.4, h 3.6, depth 0.8
        {"kind": "recess", "u": 3.8, "v": 17.5, "w": 52.4, "h": 3.6, "depth": 0.8},
        # 5 deeper vent slots inside top vent band recess
        # v = 18.85, u = 6.0 + i * 10.0 for i = 0..4
        # w=8.0, h=0.9, depth=1.3
        {"kind": "recess", "u": 6.0, "v": 18.85, "w": 8.0, "h": 0.9, "depth": 1.3},
        {"kind": "recess", "u": 16.0, "v": 18.85, "w": 8.0, "h": 0.9, "depth": 1.3},
        {"kind": "recess", "u": 26.0, "v": 18.85, "w": 8.0, "h": 0.9, "depth": 1.3},
        {"kind": "recess", "u": 36.0, "v": 18.85, "w": 8.0, "h": 0.9, "depth": 1.3},
        {"kind": "recess", "u": 46.0, "v": 18.85, "w": 8.0, "h": 0.9, "depth": 1.3},

        # SLOT BAND: 14 PCIe brackets
        # v=7.0, u = 3.8 + i * 3.8 for i=0..13
        # Each bracket: w=2.9, h=9.6, depth=0.8
        # Nested inside EACH bracket: two port recesses
        # Spanning full width (margin 0 left/right), so u is same as bracket u
        # Port recesses: depth=1.2, h=1.6, at v=9.5 and v=12.0
        {"kind": "recess", "u": 3.8, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 3.8, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 3.8, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 7.6, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 7.6, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 7.6, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 11.4, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 11.4, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 11.4, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 15.2, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 15.2, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 15.2, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 19.0, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 19.0, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 19.0, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 22.8, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 22.8, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 22.8, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 26.6, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 26.6, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 26.6, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 30.4, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 30.4, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 30.4, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 34.2, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 34.2, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 34.2, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 38.0, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 38.0, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 38.0, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 41.8, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 41.8, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 41.8, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 45.6, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 45.6, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 45.6, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 49.4, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 49.4, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 49.4, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        {"kind": "recess", "u": 53.2, "v": 7.0, "w": 2.9, "h": 9.6, "depth": 0.8},
        {"kind": "recess", "u": 53.2, "v": 9.5, "w": 2.9, "h": 1.6, "depth": 1.2},
        {"kind": "recess", "u": 53.2, "v": 12.0, "w": 2.9, "h": 1.6, "depth": 1.2},

        # MANAGEMENT BAND: One recess u 3.8, v 0.8, w 52.4, h 5.3, depth 0.6
        {"kind": "recess", "u": 3.8, "v": 0.8, "w": 52.4, "h": 5.3, "depth": 0.6},

        # Nested inside Management Band recess:
        # MGMT port: recess u 10.0, v 2.6, w 2.0, h 1.6, depth 1.2
        {"kind": "recess", "u": 10.0, "v": 2.6, "w": 2.0, "h": 1.6, "depth": 1.2},

        # Blue pull tab: boss u 20.0, v 2.6, w 10.0, h 1.4, depth 0.6
        {"kind": "boss", "u": 20.0, "v": 2.6, "w": 10.0, "h": 1.4, "depth": 0.6},

        # RMM port: recess u 32.0, v 1.7, w 2.0, h 1.6, depth 1.2
        {"kind": "recess", "u": 32.0, "v": 1.7, "w": 2.0, "h": 1.6, "depth": 1.2},

        # 3 status lights: boss w 0.9, h 0.9, depth 0.4, at v 3.0 and u = 36.0, 37.8, 39.6
        {"kind": "boss", "u": 36.0, "v": 3.0, "w": 0.9, "h": 0.9, "depth": 0.4},
        {"kind": "boss", "u": 37.8, "v": 3.0, "w": 0.9, "h": 0.9, "depth": 0.4},
        {"kind": "boss", "u": 39.6, "v": 3.0, "w": 0.9, "h": 0.9, "depth": 0.4},

        # 2 USB ports: recess w 1.4, h 0.9, depth 1.2, at v 3.0 and u = 42.0, 44.3
        {"kind": "recess", "u": 42.0, "v": 3.0, "w": 1.4, "h": 0.9, "depth": 1.2},
        {"kind": "recess", "u": 44.3, "v": 3.0, "w": 1.4, "h": 0.9, "depth": 1.2}
    ]
}