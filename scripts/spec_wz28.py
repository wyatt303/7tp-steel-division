"""Samochód pancerny wz. 28 (Citroën-Kégresse half-track), in metres. Faces +Y, right +X.

Sources: Polish Wikipedia data (length 3.50 m, width 1.40 m, height 2.10 m, clearance
0.28 m) and the 1/76 drawing "Samochod pancerny wz 28, late model" by M C Bell (1981,
Wikimedia Commons, CC BY 4.0). Measured on a 2x crop of the 1920 px scan, 4.09 mm per
crop pixel: Y = (640 - x) * 0.00409 and Z = (548 - y) * 0.00409 in the side view.
The length from the data then gives 2.13 m height, matching the data within 3 cm.

Set AC_VARIANT to "ckm" (Hotchkiss wz. 25) or "37" (37 mm Puteaux SA 18).
"""

import os

VARIANT = os.environ.get("AC_VARIANT", "ckm")
STEM = {"ckm": "WZ28_CKM", "37": "WZ28_37"}[VARIANT]
TRACKED = True

# Front axle: single steered wheels, no mudguards on the late model.
TYRE_R = 0.37
TYRE_W = 0.09
RIM_R = 0.22
FRONT_AXLE_Y = 1.37
FRONT_X = 0.62
WHEEL_Z = TYRE_R

# Kegresse rubber track: front drum, four small road wheels, rear drive wheel.
TRACK_X = 0.61
TRACK_W = 0.164
TRACK_T = 0.025
ROAD_R = 0.09
ROAD_Z = ROAD_R + TRACK_T
FRONT_DRUM = (-0.205, 0.286, 0.205)
REAR_DRIVE = (-1.41, 0.278, 0.21)
ROAD_Y = [-0.51, -0.74, -0.96, -1.11]
WHEELS = [FRONT_DRUM] + [(y, ROAD_Z, ROAD_R) for y in ROAD_Y] + [REAR_DRIVE]
SPROCKET, IDLER = FRONT_DRUM, REAR_DRIVE  # names used by the shared track code

# Bonnet: sections across the car (Y, bottom Z, side top Z, half width); the top has a
# shallow ridge along the middle, as in the front view.
BONNET = [(1.317, 0.626, 1.145, 0.29), (0.98, 0.565, 1.172, 0.335), (0.80, 0.38, 1.187, 0.36), (0.0, 0.38, 1.26, 0.47)]
RIDGE = 0.07

# Fighting compartment over the tracks: plan rings (Z, front Y, rear Y, half width, chamfer).
BODY_HALF = 0.51
BODY = [
    (0.565, 0.06, -1.68, BODY_HALF, 0.10),
    (1.26, -0.08, -1.56, BODY_HALF, 0.14),
    (1.554, -0.27, -1.51, BODY_HALF - 0.01, 0.16),
]
ROOF_Z = BODY[-1][0]
DECK_Z = 0.565

# Rotating turret: octagonal truncated pyramid and a hexagonal cupola.
TURRET_C = (0.0, -0.95, ROOF_Z)
TURRET_RINGS = [  # Z, centre Y, half length, half width, chamfer
    (ROOF_Z, -0.95, 0.52, 0.48, 0.17),
    (ROOF_Z + 0.03, -0.95, 0.52, 0.48, 0.17),
    (1.947, -1.03, 0.32, 0.37, 0.12),
]
CUPOLA_C = (0.0, -1.05)
CUPOLA = [(1.947, 0.20), (2.127, 0.15)]
MOUNT = (0.0, -0.45, 1.75)
MANTLET = "ball" if VARIANT == "ckm" else "rect"
MUZZLE_Y = MOUNT[1] + (0.67 if VARIANT == "ckm" else 0.42)

LOCKERS = [(0.57, 0.12, 0.53, 0.63, 0.94)]  # X centre, Y rear, Y front, Z bottom, Z top
TOW_HOOK = (0.0, -1.72, 0.52)
MUFFLER = (-0.30, 0.50, 0.42)

TURRETS = {1: {"center": TURRET_C, "mount": MOUNT, "muzzle_y": MUZZLE_Y}}
EXTRA_MOUNT = MOUNT
EXTRA_MUZZLE_Y = MUZZLE_Y


def is_tyre(name):
    if name in ("Roue_Droite_01", "Roue_Gauche_01"):
        return TYRE_R
    if name.startswith("Roue_") and name[6:].isdigit() and 2 <= int(name[6:]) <= 1 + len(ROAD_Y):
        return ROAD_R
    return False


UV_COPIES = {"Roue_Gauche_01": "Roue_Droite_01"}

RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (5.4, 5.2, 2.3), (0, -0.1, 0.95), 50),
    "tyl_3_4": ("PERSP", (-4.2, -6.0, 2.5), (0, -0.3, 0.95), 50),
    "bok": ("ORTHO", (12, 0, 1.08), (0, -0.15, 1.08), 4.3),
    "zblizenie": ("PERSP", (2.6, 2.4, 2.5), (0.0, -0.7, 1.65), 50),
}


def chamfer_ring(cx, cy, z, half_l, half_w, c):
    pts = [(half_w - c, half_l), (-half_w + c, half_l), (-half_w, half_l - c), (-half_w, -half_l + c),
           (-half_w + c, -half_l), (half_w - c, -half_l), (half_w, -half_l + c), (half_w, half_l - c)]
    return [(cx + x, cy + y, z) for x, y in pts]


def body_ring(z, front, rear, half, c):
    mid = (front + rear) / 2
    return chamfer_ring(0.0, mid, z, (front - rear) / 2, half, c)


def rivet_lines(Vector):
    lines, seams = [], []

    def row(a, b, spacing=0.075):
        lines.append((Vector(a), Vector(b), spacing))

    def seam(a, b):
        seams.append((Vector(a), Vector(b)))

    def ring_rows(rings, inset=0.03):
        for lo, hi in zip(rings, rings[1:]):
            if abs(hi[0][2] - lo[0][2]) < 0.06:
                continue
            for i in range(len(lo)):
                j = (i + 1) % len(lo)
                a0, a1 = Vector(lo[i]).lerp(Vector(hi[i]), 0.08), Vector(lo[j]).lerp(Vector(hi[j]), 0.08)
                b0, b1 = Vector(lo[i]).lerp(Vector(hi[i]), 0.92), Vector(lo[j]).lerp(Vector(hi[j]), 0.92)
                if (a1 - a0).length > 0.12:
                    d = (a1 - a0).normalized() * inset
                    row(a0 + d, a1 - d)
                    row(b0 + d, b1 - d)
                    row(a0 + d, b0 + d, 0.07)
                seam(Vector(lo[i]), Vector(hi[i]))

    ring_rows([body_ring(*r) for r in BODY])
    cx = TURRET_C[0]
    ring_rows([chamfer_ring(cx, cy, z, hl, hw, c) for z, cy, hl, hw, c in TURRET_RINGS[1:]])
    for s in (-1, 1):
        for k in range(len(BONNET) - 1):
            y0, b0, t0, h0 = BONNET[k]
            y1, b1, t1, h1 = BONNET[k + 1]
            row((s * (h0 - 0.005), y0 - 0.03, t0 - 0.03), (s * (h1 - 0.005), y1 + 0.03, t1 - 0.03))
            row((s * (h0 - 0.005), y0 - 0.03, b0 + 0.03), (s * (h1 - 0.005), y1 + 0.03, b1 + 0.03))
    row((-0.25, 1.317, 0.66), (0.25, 1.317, 0.66))
    row((-0.25, 1.317, 1.11), (0.25, 1.317, 1.11))
    return lines, seams
