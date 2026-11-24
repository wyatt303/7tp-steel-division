"""PZL.37B Łoś medium bomber, in metres. Nose +Y, right wing +X, Z=0 on the fuselage axis.

Sources: data (span 17.93 m, length 12.92 m, height 5.08 m, wing area 53.5 m²), the
three-view "PZL P.37B Los B" on the-blueprints.com, viewed in a browser at its free 500 px
size (about 67 mm per pixel: nacelles at ±2.8 m, tailplane span 6.4 m with twin fins), the
side view and cross sections of the drawing from the "Modelarz" monthly (Wikimedia Commons,
CC BY-SA 3.0), and period photographs. Without a full-size drawing the outline is an
approximation; the main dimensions come from the data.

Node layout follows the game's Ju 88 and Ju 188, twin-engine bombers with retractable
gear: Chassis, Bloc_Moteur_1 (left) and Bloc_Moteur_2 (right) with Helice_LS_1/2,
Aileron_D/G, Elevator_D/G, Rudder, the nose gun Tourelle_01, dorsal Tourelle_02, ventral
Tourelle_03, crew helpers Pilot, Pilot2, Pilot3, bomb points AS_1_1 ... AS_2_2. The main
file has no wheels: the <stem>_train file holds the Train (legs), Roue_Avant (main wheels)
and Roue_Arriere (tail wheel) meshes and the Train_Avant / Train_Arriere helpers.
"""

STEM = "PZL37B"
VARIANT = "los"
TRACKED = False
DUST = 0.0

# Fuselage: (Y, top Z, bottom Z, half width), nose to tail. Deep and narrow, as in the
# Modelarz cross sections.
FUSELAGE = [
    (6.02, 0.10, -0.10, 0.05), (5.75, 0.55, -0.55, 0.42), (5.25, 0.82, -0.80, 0.56), (4.20, 0.95, -0.92, 0.62),
    (2.50, 1.02, -0.95, 0.63), (0.50, 1.00, -0.95, 0.62), (-1.50, 0.90, -0.82, 0.55), (-3.50, 0.74, -0.52, 0.42),
    (-5.40, 0.56, -0.18, 0.25), (-6.55, 0.46, 0.08, 0.10), (-6.90, 0.42, 0.22, 0.03),
]
NOSE_GLASS_Y = 4.95     # glazed nose ahead of this station
COCKPIT = (-0.12, 3.35, 2.05, 1.02, 1.38, 0.38)  # X, front Y, rear Y, base Z, top Z, half width

# Wing: (span, LE Y, TE Y, Z, thickness); flat centre section to the nacelles, then dihedral.
WING = [
    (0.65, 1.30, -2.70, -0.55, 0.17), (3.90, 1.18, -2.42, -0.55, 0.16), (6.50, 0.84, -1.86, -0.28, 0.14),
    (8.40, 0.45, -1.32, -0.08, 0.11), (8.80, 0.25, -1.10, -0.04, 0.09), (8.965, 0.00, -0.85, -0.02, 0.06),
]
AILERON = (5.60, 8.45, 0.55)

# Engine nacelles: Bristol Pegasus XX in NACA cowlings, three-blade propellers.
NACELLE_X = 2.80
NACELLE_Z = -0.62
NACELLE = [(3.40, 0.68), (2.70, 0.66), (1.50, 0.62), (0.00, 0.55), (-1.60, 0.40), (-2.60, 0.12)]  # Y, radius
COWL_FRONT, COWL_REAR, COWL_R = 3.40, 2.70, 0.70
PROP_Y, PROP_R, SPINNER_R = 3.62, 1.60, 0.24

# Tail: tailplane (span, LE Y, hinge Y, TE Y) and twin oval fins at the tips.
TAIL_Z = 0.48
TAILPLANE = [(0.05, -5.00, -6.00, -6.55), (2.60, -5.15, -6.00, -6.50), (3.20, -5.30, -6.00, -6.45)]
FIN_X = 3.22
FIN = [(-0.45, -5.40), (0.10, -5.05), (0.90, -5.05), (1.35, -5.35)]   # Z, LE Y
HINGE_RUDDER = -5.98
RUDDER = [(-0.45, -6.25), (0.10, -6.55), (0.90, -6.55), (1.35, -6.20)]  # Z, TE Y

# Retractable gear (in the _train file): twin main wheels under each nacelle, tail wheel.
WHEEL_R, WHEEL_W = 0.48, 0.20
WHEEL_Y, WHEEL_Z = 1.30, -2.60
WHEEL_X = (NACELLE_X - 0.24, NACELLE_X + 0.24)
TAIL_WHEEL = (0.0, -6.25, -0.95, 0.20)  # X, Y, Z, radius

# Guns and crew.
NOSE_GUN = (0.0, 5.55, -0.25)
NOSE_MUZZLE_Y = 6.45
DORSAL = (0.0, -1.10, 1.02)
DORSAL_MUZZLE_Y = -2.05
VENTRAL = (0.0, -2.40, -0.80)
VENTRAL_MUZZLE_Y = -3.30
PILOT = (-0.12, 2.80, 0.95)
PILOT2 = (0.0, 5.00, 0.0)
PILOT3 = (0.0, -1.40, 0.55)
VORTEX = (8.95, -0.30, -0.02)
BOMBS = [(0.0, 0.60, -0.70), (0.0, -0.60, -0.70), (1.60, -0.20, -0.62), (-1.60, -0.20, -0.62)]
TRAIN_AVANT = (0.0, WHEEL_Y, WHEEL_Z - WHEEL_R)
TRAIN_ARRIERE = (0.0, TAIL_WHEEL[1], TAIL_WHEEL[2] - TAIL_WHEEL[3])
GROUND_Z = TRAIN_AVANT[2]

ROAD_R = WHEEL_R
MUFFLER = (99.0, 99.0, 99.0)


def is_tyre(name):
    return WHEEL_R if name == "Roue_Avant" else (TAIL_WHEEL[3] if name == "Roue_Arriere" else False)


RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (15.0, 15.5, 6.0), (0, -0.5, -0.6), 45),
    "tyl_3_4": ("PERSP", (-13.0, -16.5, 7.5), (0, -0.8, -0.6), 45),
    "bok": ("ORTHO", (24, -0.4, -0.6), (0, -0.4, -0.6), 14.0),
    "zblizenie": ("PERSP", (5.5, 9.0, 2.5), (0.0, 3.5, 0.0), 45),
}

KHAKI = (0.29, 0.28, 0.19)
UNDER = (0.55, 0.60, 0.62)
RED = (0.55, 0.06, 0.06)
WHITE = (0.86, 0.85, 0.80)
GLASS = (0.16, 0.20, 0.24)
CHECKER_WING = (6.60, 8.20)


def paint_color(pos, nrm, np, part=None):
    low = np.clip((-nrm[:, 2] - 0.15) / 0.3, 0, 1)
    color = np.array(KHAKI, np.float32) * (1 - low[:, None]) + np.array(UNDER, np.float32) * low[:, None]

    def checker(a, b, size, mask, color):
        cell = (np.floor(a / size) + np.floor(b / size)) % 2
        c = np.where(cell[:, None] > 0.5, np.array(RED, np.float32), np.array(WHITE, np.float32))
        return np.where(mask[:, None], c, color)

    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    span = np.abs(x)
    wing = (span > CHECKER_WING[0]) & (span < CHECKER_WING[1]) & (np.abs(nrm[:, 2]) > 0.6) & (y > -1.4) & (y < 0.6)
    color = checker(span - CHECKER_WING[0], y + 1.4, (CHECKER_WING[1] - CHECKER_WING[0]) / 4, wing, color)
    fins = (np.abs(span - FIN_X) < 0.15) & (np.abs(nrm[:, 0]) > 0.6) & (y < -5.2) & (y > -5.9) & (z > 0.2) & (z < 0.95)
    color = checker(y + 5.9, z - 0.2, 0.35, fins, color)
    glass = (y > NOSE_GLASS_Y) | ((np.abs(x - COCKPIT[0]) < COCKPIT[5]) & (y < COCKPIT[1]) & (y > COCKPIT[2]) & (z > COCKPIT[3] + 0.04))
    color[glass] = GLASS
    return color


def rivet_lines(Vector):
    lines, seams = [], []
    for y, top, bottom, half in FUSELAGE[2:-2]:
        mid = (top + bottom) / 2
        for sgn in (-1, 1):
            seams.append((Vector((sgn * half, y, mid + 0.4)), Vector((sgn * half, y, mid - 0.4))))
    return lines, seams

# The _train file holds meshes (retractable gear), textured by texture_tk.py.
TRAIN_MESHES = True
