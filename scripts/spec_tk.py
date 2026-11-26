"""Shared dimensions of the TK-3 and TKS tankettes, in metres.

Tank faces +Y, right side is +X, ground is Z=0, Y=0 is the middle of the overall length.

Sources: the TK-3 and TKS data tables (length 2580, width 1780 / 1796, height 1320 / 1326,
clearance 300 / 325, track width 140 / 170, gauge 1475 / 1450) and two colour side plates,
both drawn at about 2.6 mm per pixel. Running gear, superstructure outline and the gun
position were measured from those plates, so they are estimates. Plan widths come from the
top-view drawings.

Set TK_VARIANT to "tk3", "tks" or "tks20". "tks20" is the TKS hull with the 20 mm nkm wz. 38
FK-A in place of the Hotchkiss machine gun, as in the tankettes re-armed in 1939 (the tank of
Roman Orlik). The gun is about 1.85 m long overall; in the ball mount roughly a metre of it, the
recoil jacket and the barrel with its muzzle brake, sticks out in front of the mount. These
figures are estimates from photographs.
"""

import os

VARIANT = os.environ.get("TK_VARIANT", "tks")
STEM = {"tk3": "TK3", "tks": "TKS", "tks20": "TKS20"}[VARIANT]
GUN = "nkm20" if VARIANT == "tks20" else "hotchkiss"

if VARIANT == "tk3":
    GROUND_CLEARANCE = 0.30
    TRACK_X = 0.7375
    TRACK_W = 0.14
else:
    GROUND_CLEARANCE = 0.325
    TRACK_X = 0.725
    TRACK_W = 0.17

TRACK_T = 0.030
ROAD_R = 0.110
ROAD_Z = ROAD_R + TRACK_T
SPROCKET = (1.00, 0.45, 0.19)   # front, toothed drive wheel
IDLER = (-1.06, 0.29, 0.17)     # rear, spoked idler on the end of the girder
ROAD_Y = [0.62, 0.23, -0.20, -0.59]
WHEELS = [SPROCKET] + [(y, ROAD_Z, ROAD_R) for y in ROAD_Y] + [IDLER]
WHEEL_PAIRS = ((0, 1), (2, 3))

HULL_HALF_WIDTH = 0.60
DECK_Z = 0.735
FENDER_OUTER = 0.90
CL = GROUND_CLEARANCE

# Lower hull between the tracks, side profile (Y, Z).
HULL_LOWER = [
    (0.92, CL), (1.17, 0.50), (1.15, 0.66), (1.04, DECK_Z), (-0.80, DECK_Z),
    (-1.27, 0.60), (-1.24, 0.45), (-0.98, CL),
]

# Track guard over each track: front arc around the sprocket, flat deck, sloped rear.
FENDER_ARC = (SPROCKET[0], SPROCKET[1] - 0.005, 0.29)  # centre Y, centre Z, radius
FENDER_ARC_DEG = (90, 14)
FENDER_REAR = [(-0.80, DECK_Z), (-1.31, 0.60)]

# Superstructure as horizontal plan rings: Z, then (Y, half width) for the right side,
# front to rear. Each ring has the same point count so the rings can be lofted.
if VARIANT == "tk3":
    SUPER_RINGS = [
        (DECK_Z, [(0.57, 0.56), (0.48, 0.86), (-0.66, 0.86), (-0.81, 0.58)]),
        (1.04, [(0.57, 0.56), (0.48, 0.86), (-0.66, 0.86), (-0.80, 0.58)]),
        (1.06, [(0.57, 0.56), (0.48, 0.84), (-0.48, 0.84), (-0.53, 0.58)]),
        (1.19, [(0.47, 0.56), (0.40, 0.80), (-0.50, 0.80), (-0.53, 0.56)]),
        (1.305, [(0.38, 0.54), (0.32, 0.76), (-0.44, 0.76), (-0.48, 0.54)]),
    ]
    MOUNT = (0.40, 0.63, 1.02)
    MUZZLE_Y = 1.29
    MUFFLER = (0.40, -0.64, 1.27)
    MANTLET = "box"
else:
    SUPER_RINGS = [
        (DECK_Z, [(0.64, 0.58), (0.54, 0.88), (-0.70, 0.88), (-0.90, 0.60)]),
        (0.97, [(0.64, 0.58), (0.54, 0.88), (-0.70, 0.88), (-0.90, 0.60)]),
        (1.00, [(0.63, 0.58), (0.53, 0.87), (-0.52, 0.87), (-0.64, 0.60)]),
        (1.21, [(0.52, 0.50), (0.42, 0.70), (-0.40, 0.70), (-0.56, 0.52)]),
        (1.275, [(0.24, 0.46), (0.15, 0.60), (-0.34, 0.60), (-0.47, 0.46)]),
    ]
    MOUNT = (0.40, 0.66, 1.01)
    MUZZLE_Y = 1.72 if GUN == "nkm20" else 1.29
    MUFFLER = (0.40, -0.80, 1.17)
    MANTLET = "ball"

ROOF_Z = SUPER_RINGS[-1][0]

# Crew positions (driver left, commander-gunner right, under the roof hatches) and the tow
# hook on the rear plate. Names and roles follow the game's Universal Carrier, which has
# Driver, Tireur and Remorque_1 helpers at about 0.45 m above its floor and at the rear.
DRIVER = (-0.28, -0.05, 0.85)
GUNNER = (0.30, -0.05, 0.85)
TOW_HOOK = (0.0, -1.31, 0.45)
TURRETS = {1: {"center": MOUNT, "mount": MOUNT, "muzzle_y": MUZZLE_Y}}
EXTRA_MOUNT = MOUNT
EXTRA_MUZZLE_Y = MUZZLE_Y

# External suspension girder, outside the wheels.
GIRDER_X = TRACK_X + TRACK_W / 2 + 0.035
GIRDER_Y = (0.76, -0.96)
GIRDER_Z = 0.275
RAIL = ((0.68, 0.57), (-0.76, 0.40))  # upper diagonal bar, front and rear (Y, Z)


def ring_points(plan, z):
    """Closed ring from a right-side half plan: right side front to rear, left side back."""
    right = [(hx, y, z) for y, hx in plan]
    left = [(-hx, y, z) for y, hx in reversed(plan)]
    return right + left
