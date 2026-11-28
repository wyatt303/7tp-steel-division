"""Polski Fiat 621L 2.5 t military truck, in metres. Faces +Y, right +X, ground Z = 0.

Two variants share this file: PF621L with the canvas tilt (TILT = True) and PF621L_OPEN with
the open wooden cargo body (spec_pf621_open.py).

Sources:
- Overall data (length 5.78 m, width 2.07 m, height with the tilt 2.62 m, wheelbase 3.65 m)
  from the English Wikipedia and techno-science.net.
- Cab, bonnet, mudguards, cargo body heights and the front view: the 1:25 side and front
  drawing "Polski Fiat 621 L Truck (1937-1939)" (vector-templates.com), measured at about
  0.0103 m per pixel and placed against the front axle. The drawing has a shorter wheelbase
  (3.2 m) than the data; the cab and bonnet are taken from it, the wheelbase and the length of
  the cargo body from the data.
- Details: photographs of scale models supplied by the user (two rows of bonnet louvres, the
  roof visor, the planked rear wall of the cab, the tubular front bumper, stakes on the cargo
  body) and a coloured side, top, front and rear drawing (Polish illustration).

Node layout follows the game's Opel Blitz (GER/Vehicule.zip): Chassis, front wheels
Roue_Droite_01 / Roue_Gauche_01, the whole rear axle Roue_02 (twin tyres on each side), helpers
Driver, Remorque_1, Fx_Stress_01/02 and FX_Fumee_Roue_D1/G1. No turret.
"""

STEM = "PF621L"
VARIANT = "pf621"
TRACKED = False
DUST = 0.8
TILT = True

TYRE_R, TYRE_W, RIM_R = 0.40, 0.19, 0.24   # drawing: wheels 0.80 m
ROAD_R = TYRE_R
WHEEL_Z = TYRE_R
FRONT_AXLE_Y = 2.14
REAR_AXLE_Y = FRONT_AXLE_Y - 3.65
FRONT_X = 0.80                             # front view: tyre centres 1.6 m apart
REAR_X = (0.68, 0.89)                      # twin rear tyres on each side

A = FRONT_AXLE_Y
FRONT_Y, REAR_Y = A + 0.52, -2.93          # front bumper and tailgate
FRAME_Z = (0.40, 0.55)

# Radiator shell and grille (front view: 0.46 m wide, from 0.55 to 1.30 m).
RADIATOR_Y = A + 0.19
GRILLE = (0.23, 0.55, 1.30)                # half width, bottom, top
# Bonnet: (Y, bottom Z, top Z, half width) from the radiator back to the cowl, then the cowl
# widening and rising to the cab (side view: bonnet top 1.33 m, cab front at 1.41 m).
# The bonnet sides reach down to the mudguards, as on the drawing. Seen from above the bonnet
# widens strongly from the radiator to the cab (top view of the coloured drawing: half width
# about 0.36 m at the radiator, 0.61 m at the cowl, then to the cab corners).
BONNET = [(RADIATOR_Y, 0.55, 1.30, 0.29), (RADIATOR_Y - 0.08, 0.46, 1.33, 0.34), (A - 0.85, 0.42, 1.36, 0.61)]
COWL = [(A - 0.85, 0.42, 1.36, 0.61), (A - 0.97, 0.38, 1.40, 0.71), (A - 1.05, 0.36, 1.41, 0.75)]
LOUVRES = [(1.04, 1.20), (0.80, 0.96)]     # two rows of bonnet louvres: Z ranges
LOUVRE_Y = (A - 0.30, A - 0.80)

# Cab (drawing: 1.02 m long, 1.51 m wide, roof at 2.00 m, windscreen leaning back by 0.09 m).
CAB_FRONT, CAB_REAR = A - 1.05, A - 2.07
CAB_Z = (0.36, 1.41, 2.00)                 # bottom, top of the cowl line, roof
CAB_HALF = 0.75
CAB_LEAN = 0.09                            # windscreen top lies this much behind its bottom
VISOR = 0.06                               # roof overhang in front of the windscreen top
WINDSCREEN_Z = (1.43, 1.80)
SIDE_WINDOW = (A - 1.19, A - 1.90, 1.39, 1.83)  # Y from, Y to, Z from, Z to
# The cab is hollow behind its see-through windows (glass.py): solid up to the floor, walls up to
# the window line, pillars, the strip over the windscreen and the roof, with a bench, dashboard
# and steering wheel inside.
CAB_FLOOR = 0.90
CAB_WALL = 0.035
ROOF_IN_Z = 1.84                           # underside of the roof, just above the windows
WINDSCREEN_PANES = [(-0.66, -0.03), (0.03, 0.66)]   # X from, X to of the two panes

# Cargo body: front Y, rear Y, floor Z, side top Z, half width (front view 1.90 m wide).
BODY = (CAB_REAR - 0.06, REAR_Y, 1.02, 1.65, 0.95)
TILT_TOP = 2.62
TILT_WINDOWS = [(-1.18, -1.34), (-1.38, -1.54)]  # two small panes in each tilt side: Y from, Y to
TILT_WINDOW_Z = (1.99, 2.16)

HEADLAMPS = [(0.40, A + 0.16, 0.94), (-0.40, A + 0.16, 0.94)]
HEADLAMP_R = 0.12
# Front mudguard, side view: from the tip in front of the wheel (0.46 m ahead, 0.67 m up) over
# the wheel (top 0.92 m) and down to the running board 0.74 m behind the axle.
FRONT_GUARD_R = 0.53
FRONT_GUARD_X = (0.64, 0.92)
FRONT_GUARD_END = (A - 0.74, 0.37)
REAR_GUARD = (REAR_AXLE_Y, WHEEL_Z, 0.57, 15, 165, REAR_X[0] - 0.13, REAR_X[1] + 0.12)
STEP = (A - 0.74, CAB_REAR - 0.10, 0.36)  # running board from Y, to Y, Z
STEP_X = (0.55, 0.90)
TOOLBOX = (0.72, CAB_REAR - 0.36, 0.69, 0.34, 0.56, 0.30)  # centre X, Y, Z and size under the body
FUEL_TANK = (-0.66, CAB_REAR - 0.36, 0.69)
BUMPER = (FRONT_Y - 0.05, 0.45, 0.65)      # Y, Z, half length of the tube

DRIVER = (-0.38, A - 1.60, 0.95)           # left-hand drive; 0.46 m under the window line, as in the Opel Blitz (0.48) and Bedford (0.44)
STEERING = (-0.38, A - 1.42, 1.50)         # steering wheel in front of the driver
TOW_HOOK = (0.0, REAR_Y - 0.06, 0.55)
MUFFLER = (0.45, -0.95, 0.38)
FX_STRESS = [(0.0, -1.5, 1.9), (0.3, 1.6, 1.2)]


def cab_front(z):
    """Y of the cab front at height z: vertical below the cowl line, leaning back above it."""
    z1, z2 = CAB_Z[1], CAB_Z[2]
    if z <= z1:
        return CAB_FRONT
    return CAB_FRONT - CAB_LEAN * (z - z1) / (z2 - z1)


def is_tyre(name):
    return name.startswith("Roue_")


UV_COPIES = {"Roue_Gauche_01": "Roue_Droite_01"}

RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (7.8, 8.0, 3.2), (0, 0.0, 1.1), 45),
    "tyl_3_4": ("PERSP", (-6.5, -8.8, 3.5), (0, -0.3, 1.1), 45),
    "bok": ("ORTHO", (14, 0, 1.35), (0, 0, 1.35), 6.6),
    "zblizenie": ("PERSP", (3.4, 5.4, 2.0), (0.0, 1.3, 1.2), 45),
}


def rivet_lines(Vector):
    """Panel seams of the cab, the boards of its rear wall and of the wooden cargo body."""
    lines, seams = [], []
    by0, by1, floor, side_top, bh = BODY
    for side in (-1, 1):
        x = side * (bh + 0.001)
        for k in range(1, 5):
            z = floor + (side_top - floor) * k / 5
            seams.append((Vector((x, by0 - 0.05, z)), Vector((x, by1 + 0.05, z))))
        x = side * (CAB_HALF + 0.001)
        # Door: front and rear edges, and the bonnet side trim line.
        seams.append((Vector((x, SIDE_WINDOW[0] + 0.08, CAB_Z[0] + 0.10)), Vector((x, SIDE_WINDOW[0] + 0.08, CAB_Z[2] - 0.12))))
        seams.append((Vector((x, SIDE_WINDOW[1] - 0.06, CAB_Z[0] + 0.10)), Vector((x, SIDE_WINDOW[1] - 0.06, CAB_Z[2] - 0.12))))
        seams.append((Vector((side * 0.386, A - 0.05, 1.22)), Vector((side * 0.597, A - 0.80, 1.22))))  # follows the widening bonnet
    # Vertical boards of the cab rear wall.
    for k in range(-6, 7):
        x = k * CAB_HALF / 7
        seams.append((Vector((x, CAB_REAR - 0.001, CAB_Z[0] + 0.05)), Vector((x, CAB_REAR - 0.001, CAB_Z[2] - 0.08))))
    return lines, seams


# Painted panes (x0, x1, y0, y1, z0, z1): the small rear window of the cab and the panes in the
# tilt. The windscreen and the cab side windows are see-through glass (glass.py).
GLASS_BOXES = [
    (-0.30, 0.30, CAB_REAR - 0.03, CAB_REAR + 0.01, 1.55, 1.78),
] + ([(sx0, sx1, y1, y0, TILT_WINDOW_Z[0], TILT_WINDOW_Z[1])
      for y0, y1 in TILT_WINDOWS for sx0, sx1 in ((-1.06, -0.96), (0.96, 1.06))] if TILT else [])
