import math

def frac(x): return x - math.floor(x)
def h01(k, j): return frac(math.sin(k * 12.9898 + j * 78.233) * 43758.5453)
def D(u, t):
    return (3.4 * math.sin(2 * math.pi * u / 75 + 2 * math.pi * t / 110)
            + 1.5 * math.sin(2 * math.pi * u / 43 - 2 * math.pi * t / 60 + 1.3)
            + 0.6 * math.sin(2 * math.pi * u / 24 + 2 * math.pi * t / 33 + 4.1))
def line(k, u): t = V0 + k * P; return t + D(u, t)

U0, V0, U1, V1 = 4.0, 4.0, 56.5, 228.0     # allowed zone
P = 5.0          # row pitch
B = 1.8          # solid bar height between rows
G = 1.8          # solid bridge between slots in the same row
MIN_H = 1.2      # minimum slot height
MIN_LEN = 4.0    # minimum slot length
E = 1.0          # length of the rounded end cap
STEP = 0.25      # sampling step for trimming
EDGE = 0.5       # max spacing of points along slot edges
KU0, KU1, KV0 = 6.4, 31.6, 216.4   # keep-out box around the badge (u range, bottom v)

def bot(u, k): return max(line(k, u) + B / 2, V0)
def top(u, k): return min(line(k + 1, u) - B / 2, V1)
def good(u, k):
    if not (top(u, k) - bot(u, k) >= MIN_H):
        return False
    if KU0 <= u <= KU1 and top(u, k) > KV0:
        return False
    return True

features = []

# FEATURE 1: Badge boss
pts_badge = []
# Bottom-right corner center (28.0, 220.0), angles -90 to 0
for deg in range(-90, 1, 15):
    a = math.radians(deg)
    pts_badge.append((round(28.0 + 2 * math.cos(a), 2), round(220.0 + 2 * math.sin(a), 2)))
# Top-right corner center (28.0, 224.0), angles 0 to 90
for deg in range(0, 91, 15):
    a = math.radians(deg)
    pts_badge.append((round(28.0 + 2 * math.cos(a), 2), round(224.0 + 2 * math.sin(a), 2)))
# Top-left corner center (10.0, 224.0), angles 90 to 180
for deg in range(90, 181, 15):
    a = math.radians(deg)
    pts_badge.append((round(10.0 + 2 * math.cos(a), 2), round(224.0 + 2 * math.sin(a), 2)))
# Bottom-left corner center (10.0, 220.0), angles 180 to 270
for deg in range(180, 271, 15):
    a = math.radians(deg)
    pts_badge.append((round(10.0 + 2 * math.cos(a), 2), round(220.0 + 2 * math.sin(a), 2)))

# Remove duplicate points if any (e.g. corners meeting)
clean_pts = []
for p in pts_badge:
    if not clean_pts or clean_pts[-1] != p:
        clean_pts.append(p)

features.append({
    "kind": "boss", 
    "shape": "poly", 
    "pts": clean_pts, 
    "u": 8.0, 
    "v": 218.0, 
    "w": 22.0, 
    "h": 8.0, 
    "depth": 0.6
})

# SLOTS
for k in range(-3, 49):
    s = U0
    j = 1
    while U1 - s >= MIN_LEN:
        L = (6.0 + 10.0 * h01(k, 0)) if j == 1 else (9.0 + 9.0 * h01(k, j))
        a0 = s
        b0 = min(s + L, U1)
        if U1 - (b0 + G) < 6.0:     # too little room left for another slot: stretch this one to the edge
            b0 = U1
        s = b0 + G
        j += 1
        
        # Generate samples
        samples_u = []
        curr = a0
        while curr <= b0 + 1e-9:
            samples_u.append(curr)
            curr += STEP
        if not samples_u or abs(samples_u[-1] - b0) > 1e-9:
            samples_u.append(b0)
            
        # Find longest run of good(u)
        best_start = -1
        best_len = 0
        curr_start = -1
        
        for idx, u in enumerate(samples_u):
            if good(u, k):
                if curr_start == -1:
                    curr_start = idx
            else:
                if curr_start != -1:
                    run_len = idx - curr_start
                    if run_len > best_len:
                        best_len = run_len
                        best_start = curr_start
                    curr_start = -1
        
        if curr_start != -1:
            run_len = len(samples_u) - curr_start
            if run_len > best_len:
                best_len = run_len
                best_start = curr_start
                
        if best_start == -1 or best_len == 0:
            continue
            
        a = samples_u[best_start]
        b = samples_u[best_start + best_len - 1]
        
        if b - a < MIN_LEN:
            continue
            
        pts = []
        
        # 1. Top edge, left to right
        n = max(1, math.ceil((b - a - 2 * E) / EDGE))
        for i in range(n + 1):
            u = a + E + i * (b - a - 2 * E) / n
            pts.append((round(u, 2), round(top(u, k), 2)))
            
        # 2. Right cap
        um = b - E
        mid = (top(um, k) + bot(um, k)) / 2
        rh = (top(um, k) - bot(um, k)) / 2
        for i in range(1, 8):
            phi = math.radians(90 - i * 22.5)
            u_pt = um + E * math.cos(phi)
            v_pt = mid + rh * math.sin(phi)
            pts.append((round(u_pt, 2), round(v_pt, 2)))
            
        # 3. Bottom edge, right to left
        for i in range(n + 1):
            u = b - E - i * (b - a - 2 * E) / n
            pts.append((round(u, 2), round(bot(u, k), 2)))
            
        # 4. Left cap
        um = a + E
        mid = (top(um, k) + bot(um, k)) / 2
        rh = (top(um, k) - bot(um, k)) / 2
        for i in range(1, 8):
            phi = math.radians(-90 - i * 22.5)
            u_pt = um + E * math.cos(phi)
            v_pt = mid + rh * math.sin(phi)
            pts.append((round(u_pt, 2), round(v_pt, 2)))
            
        # Drop consecutive duplicates
        clean_pts = []
        for p in pts:
            if not clean_pts or clean_pts[-1] != p:
                clean_pts.append(p)
                
        us = [p[0] for p in clean_pts]
        vs = [p[1] for p in clean_pts]
        
        features.append({
            "kind": "hole", 
            "shape": "poly", 
            "pts": clean_pts, 
            "u": round(min(us), 2), 
            "v": round(min(vs), 2), 
            "w": round(max(us) - min(us), 2), 
            "h": round(max(vs) - min(vs), 2), 
            "depth": 0
        })

PANEL = {"name": "door_cray", "features": features}