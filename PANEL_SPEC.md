# Panel layout spec (door, PDU, KVM parts)

A panel is a Python file (standard library + math only) that assigns one dict:

```python
PANEL = {"name": "door", "features": features}
```

The panel is a flat rectangle seen from the front, in millimetres: `u` runs left to right from 0,
`v` runs bottom to top from 0. Each feature is a shape inside a box:

```python
{"kind": "hole" | "recess" | "boss", "u": left_edge, "v": bottom_edge, "w": width, "h": height, "depth": d}
# optional: "shape": "rect" (default) | "hex" (hexagon, pointy top and bottom) | "hex_h" (pointy left and right) | "diamond"
```
- `u` and `v` are the LEFT and BOTTOM edges of the box, never its centre.
- `hole` goes right through (depth 0). `recess` is cut in by `depth`. `boss` stands out by `depth`.
- A feature may sit completely inside a `recess` (nested). Its distance to each edge of that recess
  must be exactly 0 or >= 0.8, and a nested recess must be deeper than its parent.

## Rules
1. Every feature has w >= 0.8 and h >= 0.8.
2. Every feature's box must lie inside the allowed zone given in the brief. The zone edge is NOT a
   feature: a box may touch it. Compare with a tolerance of 1e-6 (e.g. `v0 >= zone_v0 - 1e-6`),
   because 2.53 - 1.73 is 0.7999999999999998 in floating point.
3. Features that are not nested in each other must be >= 0.8 apart.
4. Round all numbers to 2 decimals. Build the list with loops.
5. Output only the complete Python file: no markdown fences, no explanation, no print statements.
