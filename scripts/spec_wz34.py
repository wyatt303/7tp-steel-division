"""Samochód pancerny wz. 34, in metres. Faces +Y, right side +X, ground Z=0.

Sources: Polish Wikipedia data (length 3.62 m, width 1.91 m, height 2.20 m, wheelbase
2.57 m, clearance 0.25 m, 30 x 5 tyres, twin rear wheels, spare wheel on the right side)
and the colour side plate "Samochód pancerny wz. 1934", which matches the wheelbase at
3.894 mm per pixel. Plate coordinates convert as Y = (502 - x) * 0.003894 and
Z = (592 - y) * 0.003894. Widths come from the front and rear photos of the training chart.

Set AC_VARIANT to "ckm" (Hotchkiss wz. 25 in the spherical yoke) or "37" (37 mm Puteaux
SA 18 in the rectangular yoke).
"""

import math
import os

VARIANT = os.environ.get("AC_VARIANT", "ckm")
STEM = {"ckm": "WZ34_CKM", "37": "WZ34_37"}[VARIANT]
TRACKED = False

# Wheels: front single, steered; rear twin, driven. Wheel centre height = tyre radius.
TYRE_R = 0.375
TYRE_W = 0.13
RIM_R = 0.215
FRONT_AXLE_Y = 1.43
REAR_AXLE_Y = FRONT_AXLE_Y - 2.57
FRONT_X = 0.67
REAR_X = (0.655, 0.80)  # inner and outer twin tyre centres
WHEEL_Z = TYRE_R
ROAD_R = TYRE_R

# Bonnet: side profile (Y, Z) and half width.
BONNET_HALF = 0.45
BONNET = [(1.378, 0.59), (1.378, 1.145), (0.0, 1.262), (0.0, 0.36), (0.79, 0.36), (1.07, 0.59)]
# Fighting compartment: lower part a prism, upper part lofted to a narrower roof.
CAB_HALF = 0.48
CAB_LOWER = [(0.0, 0.36), (0.0, 1.262), (-1.47, 1.262), (-1.49, 0.78), (-1.47, 0.475), (-0.62, 0.475),
             (-0.55, 0.36)]
CAB_UPPER = [  # Z, front Y, rear Y, half width
    (1.262, 0.0, -1.47, CAB_HALF),
    (1.663, -0.167, -1.413, 0.44),
]
ROOF_Z = CAB_UPPER[-1][0]

# Turret: chamfered rectangle rings (Z, half length, half width, chamfer) round its centre.
TURRET_C = (0.0, -0.876, ROOF_Z)
TURRET_RINGS = [(ROOF_Z, 0.52, 0.37, 0.12), (ROOF_Z + 0.04, 0.52, 0.37, 0.12), (2.00, 0.43, 0.30, 0.10)]
CUPOLA_C = (0.0, -0.99)
CUPOLA = [(2.00, 0.19), (2.215, 0.15)]  # Z, hexagon radius
MOUNT = (0.0, -0.39, 1.86)
MANTLET = "ball" if VARIANT == "ckm" else "rect"
MUZZLE_Y = MOUNT[1] + (0.62 if VARIANT == "ckm" else 0.40)

# Mudguards: arcs round the axles (centre Y, centre Z, radius, start/end angle from +Y).
FRONT_GUARD = (FRONT_AXLE_Y, WHEEL_Z, 0.465, 45, 189, FRONT_X - 0.11, FRONT_X + 0.11)
REAR_GUARD = (REAR_AXLE_Y, WHEEL_Z, 0.51, 18, 182, 0.56, 0.955)

SPARE = (CAB_HALF + 0.075, -0.32, 0.80)  # spare wheel on the right side
HEADLAMP = (-0.40, -0.06, 1.60)
TOW_HOOK = (0.0, -1.74, 0.62)
MUFFLER = (0.32, -1.40, 0.42)

TURRETS = {1: {"center": TURRET_C, "mount": MOUNT, "muzzle_y": MUZZLE_Y}}


def is_tyre(name):
    return name.startswith("Roue_")


UV_COPIES = {"Roue_Gauche_01": "Roue_Droite_01"}

RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (5.6, 5.4, 2.4), (0, 0.0, 1.05), 50),
    "tyl_3_4": ("PERSP", (-4.4, -6.2, 2.6), (0, -0.2, 1.05), 50),
    "bok": ("ORTHO", (12, 0, 1.12), (0, 0, 1.12), 4.4),
    "zblizenie": ("PERSP", (3.0, 2.4, 2.6), (0.0, -0.6, 1.75), 50),
}


def chamfer_ring(cx, cy, z, half_l, half_w, c):
    """Octagon: rectangle with cut corners, counter-clockwise from the front right."""
    pts = [(half_w - c, half_l), (-half_w + c, half_l), (-half_w, half_l - c), (-half_w, -half_l + c),
           (-half_w + c, -half_l), (half_w - c, -half_l), (half_w, -half_l + c), (half_w, half_l - c)]
    return [(cx + x, cy + y, z) for x, y in pts]


def hexagon(cx, cy, z, r):
    return [(cx + r * math.cos(math.radians(30 + 60 * i)), cy + r * math.sin(math.radians(30 + 60 * i)), z)
            for i in range(6)]


def rivet_lines(Vector):
    """Rivet rows inside the plate edges of the bonnet, the compartment and the turret."""
    lines, seams = [], []

    def row(a, b, spacing=0.075):
        lines.append((Vector(a), Vector(b), spacing))

    def seam(a, b):
        seams.append((Vector(a), Vector(b)))

    def outline(profile, x, inset=0.03):
        n = len(profile)
        cy = sum(p[0] for p in profile) / n
        cz = sum(p[1] for p in profile) / n
        pts = []
        for y, z in profile:
            dy, dz = cy - y, cz - z
            d = math.hypot(dy, dz) or 1
            pts.append((y + dy / d * inset, z + dz / d * inset))
        for i in range(n):
            (y0, z0), (y1, z1) = pts[i], pts[(i + 1) % n]
            if math.hypot(y1 - y0, z1 - z0) > 0.15:
                row((x, y0, z0), (x, y1, z1))

    for s in (-1, 1):
        outline(BONNET, s * BONNET_HALF)
        outline(CAB_LOWER, s * CAB_HALF)
        x = s * CAB_HALF
        for y in (-0.55, -1.0):
            row((x, y, 0.50), (x, y, 1.22), 0.07)
            seam((x, y + 0.03, 0.48), (x, y + 0.03, 1.25))
        seam((s * BONNET_HALF, 0.70, 0.40), (s * BONNET_HALF, 0.70, 1.18))
    for y, z in ((1.378, 0.62), (1.378, 1.11)):
        row((-0.42, y, z), (0.42, y, z), 0.07)
    for x in (-0.42, 0.42):
        row((x, 1.378, 0.62), (x, 1.378, 1.11), 0.07)
    for y in (0.03, -1.44):
        row((-0.44, y, 1.25), (0.44, y, 1.25), 0.07)
    lo, hi = CAB_UPPER
    for s in (-1, 1):
        a, b = (s * (lo[3] - 0.02), lo[1] - 0.04, lo[0] + 0.03), (s * (hi[3] - 0.02), hi[1] - 0.04, hi[0] - 0.03)
        row(a, b, 0.07)
        row((s * (hi[3] - 0.03), hi[1] - 0.05, hi[0] - 0.02), (s * (hi[3] - 0.03), hi[2] + 0.05, hi[0] - 0.02))
    row((-0.40, hi[1] - 0.04, hi[0] - 0.02), (0.40, hi[1] - 0.04, hi[0] - 0.02))
    row((-0.40, hi[2] + 0.04, hi[0] - 0.02), (0.40, hi[2] + 0.04, hi[0] - 0.02))

    cx, cy, _ = TURRET_C
    low = chamfer_ring(cx, cy, TURRET_RINGS[1][0], *TURRET_RINGS[1][1:])
    top = chamfer_ring(cx, cy, TURRET_RINGS[2][0], *TURRET_RINGS[2][1:])
    for i in range(len(low)):
        j = (i + 1) % len(low)
        a0, a1 = Vector(low[i]).lerp(Vector(top[i]), 0.12), Vector(low[j]).lerp(Vector(top[j]), 0.12)
        b0, b1 = Vector(low[i]).lerp(Vector(top[i]), 0.88), Vector(low[j]).lerp(Vector(top[j]), 0.88)
        if (a1 - a0).length > 0.12:
            inset = (a1 - a0).normalized() * 0.03
            row(a0 + inset, a1 - inset, 0.07)
            row(b0 + inset, b1 - inset, 0.07)
        seam(Vector(low[i]), Vector(top[i]))
    return lines, seams
