"""Dimensions of the C2P light artillery tractor, in metres.

Tractor faces +Y, right side is +X, ground is Z=0, Y=0 is the middle of the overall length.

The C2P (1937) is the TKS tankette's running gear lengthened and lowered at the rear: front drive
sprocket, four road wheels in two sprung pairs on the external girder and a large spoked idler
let down to the ground. On it sits an open riveted body as wide as the tracks with the engine
under a cylindrical cover in the middle, the radiator box at the rear, a windscreen and two bows
for a canvas tilt. Driver and three gunners.

Sources: overall 2.85 x 1.82 x 1.65 m (data tables), the colour side plate (470 px for the
whole length, about 6.2 mm per pixel), the card model sheet (super-hobby: side, top, front and
rear views), a wartime photograph and a museum replica. Positions along the length and heights
were measured from the side plate, plan positions from the top view, so they are estimates.
"""

VARIANT = "c2p"
STEM = "C2P"
TRACKED = True

GROUND_CLEARANCE = 0.325
CL = GROUND_CLEARANCE
TRACK_X = 0.725          # TKS gauge 1.45 m
TRACK_W = 0.17
TRACK_T = 0.030
ROAD_R = 0.110
ROAD_Z = ROAD_R + TRACK_T
SPROCKET = (1.10, 0.41, 0.19)    # front, toothed drive wheel
IDLER = (-1.04, 0.24, 0.215)     # rear spoked idler, down on the ground
ROAD_Y = [0.73, 0.41, -0.04, -0.37]
WHEELS = [SPROCKET] + [(y, ROAD_Z, ROAD_R) for y in ROAD_Y] + [IDLER]
WHEEL_PAIRS = ((0, 1), (2, 3))

HULL_HALF_WIDTH = 0.60   # lower hull between the tracks
BODY_HALF = 0.91         # open body over the tracks, overall width 1.82
WALL = 0.025
FLOOR_Z = 0.64
FRONT = 1.42
REAR = -1.36

# Lower hull between the tracks, side profile (Y, Z).
HULL_LOWER = [(1.06, CL), (1.36, 0.50), (1.38, FLOOR_Z), (-1.32, FLOOR_Z), (-1.34, 0.45), (-1.12, CL)]

# Body side plate, side profile (Y, Z): top edge front to rear, then the lower edge back.
BODY_TOP = [(FRONT, 0.72), (1.30, 0.77), (1.00, 0.79), (-1.28, 0.79), (REAR, 0.76)]
BODY_BOTTOM = [(REAR, 0.50), (-0.40, 0.53), (0.35, 0.58), (1.20, 0.59), (FRONT, 0.56)]
SIDE = BODY_TOP + BODY_BOTTOM
DECK_Z = 0.79

# Closed decks at both ends of the open crew compartment.
FRONT_DECK_Y = 0.95
REAR_DECK_Y = -1.13
FRONT_BLOCK = [(FRONT, 0.56), (FRONT, 0.72), (1.30, 0.77), (FRONT_DECK_Y, 0.79), (FRONT_DECK_Y, 0.59), (1.20, 0.59)]
REAR_BLOCK = [(REAR_DECK_Y, 0.51), (REAR_DECK_Y, 0.79), (-1.28, 0.79), (REAR, 0.76), (REAR, 0.50)]

# Engine under a cylindrical cover in the middle, radiator box at the rear.
ENGINE = (0.0, 0.70, 0.24, 0.25, -0.70)          # X, axis Z, radius, front Y, rear Y
RADIATOR = ((0.0, -0.915, 0.92), (0.80, 0.43, 0.26))

# Seats: driver front left, gunner front right, two gunners at the rear beside the engine.
SEAT_Z = 0.74
FRONT_SEATS = [(-0.42, 0.42), (0.42, 0.42)]
REAR_SEATS = [(-0.66, -0.42), (0.66, -0.42)]
STEERING = (-0.42, 0.70, 0.98)

# Windscreen and the two bows of the canvas tilt (seen as bare posts on the side plate).
SCREEN_Y = 0.93
SCREEN_HALF = 0.84
SCREEN_Z = (DECK_Z, 1.42)
BOWS_Y = [-0.12, -1.05]
BOW_TOP = 1.57
BOW_HALF = 0.87

# Windscreen panes (x0, x1, z0, z1): see-through glass, as in the game's own vehicles (glass.py).
SCREEN_PANES = [(-SCREEN_HALF + 0.02, -0.02, 0.84, 1.38), (0.02, SCREEN_HALF - 0.02, 0.84, 1.38)]

# External suspension girder, as on the TKS, ending at the idler arm.
GIRDER_X = TRACK_X + TRACK_W / 2 + 0.035
GIRDER_Y = (0.86, -0.78)
GIRDER_Z = 0.275
RAIL = ((0.62, 0.52), (-0.62, 0.43))

# Crew and tow hook, named as on the game's Loyd Carrier (Driver, Remorque_1).
DRIVER = (-0.42, 0.42, 0.78)
TOW_HOOK = (0.0, -1.40, 0.45)

RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (3.8, 4.2, 1.9), (0, 0.1, 0.70), 50),
    "tyl_3_4": ("PERSP", (-3.3, -4.4, 2.0), (0, -0.1, 0.70), 50),
    "bok": ("ORTHO", (8, 0, 0.80), (0, 0, 0.80), 3.3),
    "zblizenie": ("PERSP", (1.9, 2.4, 1.9), (0.0, 0.1, 0.85), 50),
}


def rivet_lines(Vector):
    """Rivet rows along the edges of the body plates and the plate seams on both sides."""
    lines, seams = [], []

    def row(a, b, spacing=0.07):
        lines.append((Vector(a), Vector(b), spacing))

    for s in (-1, 1):
        x = s * BODY_HALF
        row((x, FRONT - 0.06, 0.70), (x, REAR + 0.05, 0.75), 0.075)
        row((x, 1.20, 0.61), (x, -0.40, 0.555), 0.075)
        row((x, -0.40, 0.555), (x, REAR + 0.05, 0.525), 0.075)
        for y in (0.55, -0.10, -0.91):
            row((x, y, 0.58 - 0.03 * (0.55 - y)), (x, y, 0.76), 0.06)
            seams.append((Vector((x, y, 0.53)), Vector((x, y, 0.79))))
        # Deck edges at both ends.
        row((s * (BODY_HALF - 0.04), FRONT - 0.05, 0.73), (s * (BODY_HALF - 0.04), FRONT_DECK_Y + 0.03, 0.79), 0.07)
        row((s * (BODY_HALF - 0.04), REAR_DECK_Y - 0.03, 0.79), (s * (BODY_HALF - 0.04), REAR + 0.05, 0.765), 0.07)
        # Lower hull side between the tracks.
        row((s * HULL_HALF_WIDTH, 1.00, CL + 0.03), (s * HULL_HALF_WIDTH, -1.05, CL + 0.03), 0.10)
        gx = s * GIRDER_X
        y0, y1 = GIRDER_Y
        row((gx, y0 - 0.04, GIRDER_Z + 0.02), (gx, y1 + 0.04, GIRDER_Z + 0.03), 0.08)
    row((-0.85, FRONT - 0.005, 0.66), (0.85, FRONT - 0.005, 0.66), 0.08)
    row((-0.85, REAR + 0.005, 0.70), (0.85, REAR + 0.005, 0.70), 0.08)
    row((-0.85, REAR + 0.005, 0.55), (0.85, REAR + 0.005, 0.55), 0.08)
    seams.append((Vector((-BODY_HALF, FRONT_DECK_Y, DECK_Z)), Vector((BODY_HALF, FRONT_DECK_Y, DECK_Z))))
    return lines, seams
