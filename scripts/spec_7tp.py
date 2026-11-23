"""Shared 7TP dimensions, in metres. Tank faces +Y, right side is +X, ground is Z=0.

Hull figures come from the dimensioned frame drawing (length 4091, width 1626, height 1097,
roof 1265 + 17 + 1145, rear plate 321 x 556 at 30 degrees). Running gear positions were
measured from the longitudinal section, so they are estimates.

Set TP_VARIANT to "jw" (single turret, Bofors 37 mm) or "dw" (two MG turrets).
"""

import math
import os

VARIANT = os.environ.get("TP_VARIANT", "jw")

GROUND_CLEARANCE = 0.38
HULL_TOP = GROUND_CLEARANCE + 1.097
HULL_HALF_WIDTH = 0.813
UPPER_HALF_WIDTH = 0.79
ROOF_FRONT_Y = 0.702
BULKHEAD_Y = ROOF_FRONT_Y - 1.265
ROOF_REAR_Y = ROOF_FRONT_Y - 2.427
HULL_REAR_Y = -2.046
SHOULDER_Z = 1.125

HULL_LOWER = [
    (1.678, 0.38), (2.010, 0.657), (2.045, 0.887), (0.81, SHOULDER_Z), (-1.928, SHOULDER_Z),
    (HULL_REAR_Y, 0.921), (-1.95, 0.44), (-1.42, 0.38),
]
HULL_UPPER = [
    (0.81, SHOULDER_Z), (ROOF_FRONT_Y, HULL_TOP), (ROOF_REAR_Y, HULL_TOP), (-1.928, SHOULDER_Z),
]

TRACK_X = 1.0665
TRACK_W = 0.267
TRACK_T = 0.035
ROAD_R = 0.140
ROAD_Z = ROAD_R + TRACK_T
SPROCKET = (1.92, 0.74, 0.300)
IDLER = (-1.97, 0.60, 0.270)
ROAD_Y = [1.464, 1.069, 0.675, 0.267, -0.114, -0.508, -0.903, -1.297]
BOGIE_Y = (0.866, -0.705)
RETURN_Y = [1.30, 0.50, -0.30, -1.10]
RETURN_Z = 0.93
RETURN_R = 0.075
WHEELS = [SPROCKET] + [(y, ROAD_Z, ROAD_R) for y in ROAD_Y] + [IDLER]

FENDER_Z = 0.74
FENDER_R = 0.38
FENDER_Y = 1.92

ROOF_Z_JW = 2.08

if VARIANT == "dw":
    TURRETS = {
        1: {"center": (-0.40, 0.12, HULL_TOP), "mount": (-0.40, 0.51, 1.75), "muzzle_y": 1.04},
        2: {"center": (0.40, 0.12, HULL_TOP), "mount": (0.40, 0.51, 1.75), "muzzle_y": 1.04},
    }
    EXTRA_MOUNT = TURRETS[1]["mount"]
    EXTRA_MUZZLE_Y = TURRETS[1]["muzzle_y"]
else:
    TURRETS = {1: {"center": (-0.16, 0.15, HULL_TOP), "mount": (-0.11, 0.66, 1.76), "muzzle_y": 2.02}}
    EXTRA_MOUNT = (-0.27, 0.66, 1.72)
    EXTRA_MUZZLE_Y = 1.30


def turret_plan_jw(segments=13):
    """Rounded body with a flat front plate and a rectangular rear niche."""
    points = []
    for i in range(segments):
        angle = math.radians(-38 + 256 * i / (segments - 1))
        x, y = 0.50 * math.cos(angle), 0.50 * math.sin(angle)
        points.append((x, min(y, 0.46)))
    return points + [(-0.42, -0.84), (0.42, -0.84)]
