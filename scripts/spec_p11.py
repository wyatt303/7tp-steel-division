"""PZL P.11c fighter, in metres. Nose +Y, right wing +X, Z up, Z=0 on the thrust line.

Sources: data (span 10.72 m, length 7.55 m, height 2.85 m) and the three-view drawing
"PZL 11c.svg" (Wikimedia Commons, CC BY-SA 3.0), measured at 7.97 mm per pixel of the
2000 px tall preview: Y = (290 - x) * s and Z = (262 - y) * s in the side view, X from the
top view. The origin sits at about 30 % of the wing chord, like the game's own aircraft.

Node layout follows the game's fixed-gear aircraft (Fieseler Storch, Ju 87D): Chassis,
Bloc_Moteur_1 -> Helice_LS_1, Rudder, Elevator_D/G, Aileron_D/G, Roue_Avant (both main
wheels), Roue_Arriere (tail skid), Tourelle_01 -> Axe_Canon_01 -> Canon_01 with
Fx_tourelle1_tir_01-04, Pilot, FX_Vortex_D/G, Fx_Stress_01/02, plus a separate
<stem>_train file holding the ground contact helpers Train_Avant and Train_Arriere.
"""

S = 0.00797
STEM = "P11C"
VARIANT = "p11c"
TRACKED = False
DUST = 0.0


def Y(x):
    return (290 - x) * S


def Z(y):
    return (262 - y) * S


# Fuselage sections: (Y, top Z, bottom Z, half width), nose to tail.
FUSELAGE = [
    (Y(205), Z(185), Z(350), 80 * S),
    (Y(260), Z(178), Z(345), 64 * S),
    (Y(370), Z(172), Z(335), 52 * S),
    (Y(510), Z(178), Z(318), 42 * S),
    (Y(650), Z(185), Z(300), 30 * S),
    (Y(790), Z(193), Z(280), 15 * S),
    (Y(885), Z(222), Z(262), 4 * S),
]

# Engine: Bristol Mercury in a Townend ring, spinner and two-blade propeller.
COWL_FRONT, COWL_REAR, COWL_R = Y(115), Y(205), 0.66
SPINNER_TIP, SPINNER_R = Y(45), 0.20
PROP_Y, PROP_R = Y(80), 1.40

# Gull wing: spanwise stations (span, LE Y, TE Y, Z of chord line, thickness ratio).
WING = [
    (0.33, Y(210), Y(370), Z(180), 0.12),
    (0.95, Y(212), Y(460), Z(160), 0.13),
    (1.95, Y(213), Y(460), Z(145), 0.12),
    (2.50, Y(215), Y(455), Z(146), 0.115),
    (4.60, Y(225), Y(392), Z(150), 0.10),
    (5.05, Y(240), Y(378), Z(151), 0.09),
    (5.36, Y(290), Y(345), Z(152), 0.06),
]
AILERON = (2.55, 4.85, 0.55)  # span from, span to, chord from the trailing edge

# Tail: tailplane stations (span, LE Y, hinge Y, TE Y), fin stations (Z, LE Y), rudder.
TAIL_Z = Z(200)
TAILPLANE = [(0.05, Y(797), Y(880), Y(935)), (1.20, Y(820), Y(880), Y(935)), (1.55, Y(850), Y(882), Y(925)),
             (1.67, Y(875), Y(885), Y(905))]
HINGE_RUDDER = Y(888)
FIN = [(Z(193), Y(790)), (Z(120), Y(820)), (Z(60), Y(850)), (Z(42), Y(878))]
RUDDER = [(Z(265), Y(930)), (Z(190), Y(975)), (Z(120), Y(972)), (Z(70), Y(955)), (Z(42), Y(900))]

# Fixed main gear and tail skid.
WHEEL_R, WHEEL_W = 47 * S, 0.17
WHEEL_Y, WHEEL_Z = Y(238), Z(449)
WHEEL_X = 1.21
SKID = (0.0, Y(865), Z(300))

# Guns: two in the fuselage sides, two in the wings (P.11c).
MUZZLES = [(0.42, Y(275), Z(245)), (-0.42, Y(275), Z(245)), (2.65, Y(195), Z(158)), (-2.65, Y(195), Z(158))]
GUN_PIVOT = (0.0, Y(300), Z(250))

PILOT = (0.0, Y(465), Z(200))
VORTEX = (5.30, Y(300), Z(152))
TRAIN_AVANT = (0.0, WHEEL_Y, WHEEL_Z - WHEEL_R)
TRAIN_ARRIERE = (0.0, SKID[1], SKID[2] - 0.04)
GROUND_Z = TRAIN_AVANT[2]

ROAD_R = WHEEL_R
MUFFLER = (99.0, 99.0, 99.0)


def is_tyre(name):
    if name == "Roue_Avant":
        return WHEEL_R
    return False


RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (9.0, 9.5, 3.5), (0, -0.6, 0.0), 45),
    "tyl_3_4": ("PERSP", (-8.0, -10.0, 4.5), (0, -1.0, 0.0), 45),
    "bok": ("ORTHO", (16, -1.6, -0.2), (0, -1.6, -0.2), 9.0),
    "zblizenie": ("PERSP", (3.6, 4.2, 1.6), (0.0, 0.4, 0.3), 45),
}

# Paint, September 1939: khaki upper surfaces, light blue-grey undersides, red and white
# checkerboards on both wing surfaces and on the rear fuselage sides (approximation).
KHAKI = (0.29, 0.28, 0.19)
UNDER = (0.55, 0.60, 0.62)
RED = (0.55, 0.06, 0.06)
WHITE = (0.86, 0.85, 0.80)
CHECKER_WING = (3.70, 4.70)        # span band
CHECKER_FUSE = (-2.55, -1.95)      # Y band on the fuselage sides


def paint_color(pos, nrm, np):
    khaki = np.array(KHAKI, np.float32)
    under = np.array(UNDER, np.float32)
    low = np.clip((-nrm[:, 2] - 0.15) / 0.3, 0, 1)
    color = khaki * (1 - low[:, None]) + under * low[:, None]

    def checker(a, b, size, mask):
        cell = (np.floor(a / size) + np.floor(b / size)) % 2
        c = np.where(cell[:, None] > 0.5, np.array(RED, np.float32), np.array(WHITE, np.float32))
        return np.where(mask[:, None], c, color)

    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    span = np.abs(x)
    wing = (span > CHECKER_WING[0]) & (span < CHECKER_WING[1]) & (np.abs(nrm[:, 2]) > 0.6) & (z > 0.5)
    chord_lo, chord_hi = Y(380), Y(222)
    wing &= (y > chord_lo) & (y < chord_hi)
    size = (CHECKER_WING[1] - CHECKER_WING[0]) / 4
    color = checker(span - CHECKER_WING[0], y - chord_lo, size, wing)
    fuse = (y > CHECKER_FUSE[0]) & (y < CHECKER_FUSE[1]) & (np.abs(nrm[:, 0]) > 0.6) & (z > -0.25) & (z < 0.35)
    color = checker(y - CHECKER_FUSE[0], z + 0.25, 0.30, fuse)
    return color


def rivet_lines(Vector):
    """Panel lines only: the P.11 had a smooth duralumin skin with few visible rivets."""
    lines, seams = [], []
    for y, top, bottom, half in FUSELAGE[1:-1]:
        mid = (top + bottom) / 2
        for s in (-1, 1):
            seams.append((Vector((s * half, y, mid + 0.25)), Vector((s * half, y, mid - 0.25))))
    return lines, seams
