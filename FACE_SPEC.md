# Front and bezel design spec (1:8 scale rack servers)

A front is a Python file (standard library only) in `designs/` that defines one dict named `DESIGN`.
Its optional clip-on bezel is a second file, `designs/NAME_bezel.py`, defining `BEZEL = {"units": n, "features": [...]}`.
The file MUST contain the line `DESIGN = {` (or assign DESIGN after building lists).

```python
DESIGN = {
    "name": "flash_array_3u",      # snake_case, no brand names anywhere
    "units": 3,                    # rack units tall: 1..4
    "depth": 95.0,                 # chassis depth, 10..105 mm
    "handles": False,              # False = bezel pegs, True = grip bars, "loop" = loop handles (no bezel)
    "features": [ ... ],           # the server's front face
}
```

## Coordinates
Seen from the front, in millimetres. `u` runs left to right 0..60 and `v` runs bottom to top 0..H,
where H = units * 5.556 - 0.3 (1U 5.256, 2U 10.811, 3U 16.367, 4U 21.922).
All features (face and bezel) must lie inside u 3.8..56.2 and v 0.8..H-0.8 (the ears are reserved).

## Feature = rectangle
```python
{"kind": "recess", "u": left, "v": bottom, "w": width, "h": height, "depth": d}
{"kind": "boss",   "u": ..., "v": ..., "w": ..., "h": ..., "depth": d}
{"kind": "hole",   "u": ..., "v": ..., "w": ..., "h": ..., "depth": 0}      # bezel only
# optional on any feature:  "angle": degrees   (-75..75, rotates the rectangle about its centre)
#                           "shape": "rect" (default) | "diamond" | "hex" (pointy top) | "hex_h" (pointy sides)
#                           the shape is inscribed in the u, v, w, h box
```
- `recess`: cut into the surface. Face: depth 0.6..1.3 (the snap-on front is 4 mm thick with peg
  pockets behind it). Bezel: depth 0.4..1.2.
- `boss`: stands out from the surface it sits on. depth 0.4..1.0.
- `hole`: goes right through the bezel (lets the drives show through). Bezel only.
- With `angle`, u/v/w/h describe the rectangle BEFORE rotation; the rotated corners must still be
  inside the allowed area.

## Nesting (for realistic drive trays)
A feature may sit completely inside a `recess` (its parent):
- a `boss` inside a recess is a tray handle/latch standing up from the recess floor;
- a deeper `recess` inside a recess is a vent or label area in a drive tray (its depth must be
  larger than the parent's depth, still <= the max).
The distance from a nested feature to each edge of its parent must be either exactly 0 or >= 0.8.
Only one level of nesting. Nothing may be nested inside a boss or a hole.

## Hard rules (0.4 mm nozzle)
1. Every feature has w >= 0.8 and h >= 0.8.
2. Features that are not nested in each other must be >= 0.8 mm apart (no touching, no overlap).
   Siblings inside the same parent must also be >= 0.8 mm apart.
3. At most 400 features on the face and 400 on the bezel.
4. No text, no logos, no brand names. A plain raised or recessed "badge" rectangle is fine.
5. Round numbers to 2 decimals, and use a margin of 0.9 in the arithmetic (not 0.8) so rounding
   never pushes a gap below 0.8.

Build lists with loops. Output only the Python file.
