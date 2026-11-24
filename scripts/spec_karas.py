"""PZL.23B Karaś light bomber, in metres. Nose +Y, right wing +X, Z=0 on the thrust line.

Sources: data (span 13.95 m, length 9.68 m, height 3.30 m) and the three-view drawing
"PZL P.23B Karas.svg" (Wikimedia Commons, CC BY-SA 3.0), measured at 9.33 mm per pixel of
the 2000 px tall preview: Y = (366 - x) * s and Z = (222 - y) * s in the side view.

Node layout follows the game's Ju 87D, a single-engine bomber with a fixed undercarriage
and a rear gunner: Chassis, Bloc_Moteur_1 -> Helice_LS_1, control surfaces, Roue_Avant,
Roue_Arriere, the fixed forward gun Tourelle_01 -> Axe_Canon_01 -> Canon_01, the dorsal
gun Tourelle_02 and the ventral gondola gun Tourelle_03, crew helpers Pilot, Pilot2 and
Pilot3, bomb attachment points AS_1_1 ... AS_2_2 under the wings, and a <stem>_train file
with the ground contacts.
"""

S = 0.00933
STEM = "PZL23B"
VARIANT = "karas"
TRACKED = False
DUST = 0.0


def Y(x):
    return (366 - x) * S


def Z(y):
    return (222 - y) * S


# Fuselage sections: (Y, top Z, bottom Z, half width), nose to tail.
FUSELAGE = [
    (Y(195), Z(150), Z(300), 70 * S),
    (Y(280), Z(118), Z(276), 62 * S),
    (Y(400), Z(112), Z(278), 60 * S),
    (Y(520), Z(118), Z(282), 54 * S),
    (Y(600), Z(128), Z(285), 50 * S),
    (Y(700), Z(165), Z(272), 38 * S),
    (Y(830), Z(176), Z(250), 18 * S),
    (Y(960), Z(190), Z(235), 7 * S),
    (Y(1040), Z(205), Z(222), 2 * S),
]
# Ventral gondola of the bomb aimer / rear gunner: (Y, bottom Z, half width).
GONDOLA = [(Y(440), Z(286), 0.20), (Y(475), Z(308), 0.38), (Y(640), Z(310), 0.38), (Y(668), Z(298), 0.30)]

COWL_FRONT, COWL_REAR, COWL_R = Y(100), Y(195), 0.70
SPINNER_TIP, SPINNER_R = Y(35), 0.22
PROP_Y, PROP_R = Y(78), 1.62

# Wing: (span, LE Y, TE Y, Z of chord line, thickness ratio); 4 degree dihedral.
WING = [
    (0.55, Y(285), Y(555), Z(245), 0.16),
    (1.20, Y(287), Y(552), Z(241), 0.155),
    (3.00, Y(290), Y(523), Z(229), 0.14),
    (5.50, Y(295), Y(475), Z(211), 0.12),
    (6.50, Y(300), Y(455), Z(204), 0.11),
    (6.80, Y(312), Y(440), Z(202), 0.09),
    (6.97, Y(335), Y(400), Z(201), 0.06),
]
AILERON = (4.90, 6.55, 0.40)

TAIL_Z = Z(195)
TAILPLANE = [(0.10, Y(830), Y(945), Y(1000)), (1.50, Y(870), Y(945), Y(1000)), (2.20, Y(895), Y(946), Y(995)),
             (2.45, Y(925), Y(950), Y(985))]
HINGE_RUDDER = Y(975)
FIN = [(Z(176), Y(820)), (Z(115), Y(880)), (Z(67), Y(925)), (Z(52), Y(958))]
RUDDER = [(Z(216), Y(1035)), (Z(175), Y(1050)), (Z(115), Y(1050)), (Z(70), Y(1030)), (Z(50), Y(990))]

# Fixed main gear in trouser fairings, tail wheel.
WHEEL_R, WHEEL_W = 0.37, 0.20
WHEEL_Y, WHEEL_Z = Y(330), Z(405)
WHEEL_X = 1.52
SKID = (0.0, Y(965), Z(272))

# Guns: fixed forward MG in the fuselage, dorsal and ventral rear MGs.
MUZZLES = [(-0.40, Y(196), Z(205))]
GUN_PIVOT = (-0.40, Y(260), Z(205))
DORSAL = (0.0, Y(660), Z(165))
DORSAL_MUZZLE_Y = Y(750)
VENTRAL = (0.0, Y(662), Z(298))
VENTRAL_MUZZLE_Y = Y(740)

PILOT = (0.0, Y(305), Z(150))
PILOT2 = (0.0, Y(560), Z(270))
PILOT3 = (0.0, Y(640), Z(175))
VORTEX = (6.95, Y(330), Z(201))
BOMBS = [(1.00, Y(330), Z(265)), (-1.00, Y(330), Z(265)), (1.95, Y(330), Z(258)), (-1.95, Y(330), Z(258))]
TRAIN_AVANT = (0.0, WHEEL_Y, WHEEL_Z - WHEEL_R)
TRAIN_ARRIERE = (0.0, SKID[1], SKID[2] - 0.17)
GROUND_Z = TRAIN_AVANT[2]

ROAD_R = WHEEL_R
MUFFLER = (99.0, 99.0, 99.0)


def is_tyre(name):
    return WHEEL_R if name == "Roue_Avant" else False


RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (11.5, 12.0, 4.5), (0, -1.0, -0.3), 45),
    "tyl_3_4": ("PERSP", (-10.0, -13.0, 5.5), (0, -1.5, -0.3), 45),
    "bok": ("ORTHO", (18, -1.8, -0.3), (0, -1.8, -0.3), 10.5),
    "zblizenie": ("PERSP", (4.5, 3.0, 2.0), (0.0, -1.5, 0.0), 45),
}

KHAKI = (0.29, 0.28, 0.19)
UNDER = (0.55, 0.60, 0.62)
RED = (0.55, 0.06, 0.06)
WHITE = (0.86, 0.85, 0.80)
CHECKER_WING = (5.00, 6.40)
CHECKER_FUSE = (Y(840), Y(780))


def paint_color(pos, nrm, np, part=None):
    low = np.clip((-nrm[:, 2] - 0.15) / 0.3, 0, 1)
    color = np.array(KHAKI, np.float32) * (1 - low[:, None]) + np.array(UNDER, np.float32) * low[:, None]

    def checker(a, b, size, mask, color):
        cell = (np.floor(a / size) + np.floor(b / size)) % 2
        c = np.where(cell[:, None] > 0.5, np.array(RED, np.float32), np.array(WHITE, np.float32))
        return np.where(mask[:, None], c, color)

    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]
    span = np.abs(x)
    lo, hi = Y(450), Y(300)
    wing = (span > CHECKER_WING[0]) & (span < CHECKER_WING[1]) & (np.abs(nrm[:, 2]) > 0.6) & (y > lo) & (y < hi)
    color = checker(span - CHECKER_WING[0], y - lo, (CHECKER_WING[1] - CHECKER_WING[0]) / 4, wing, color)
    fuse = (y > CHECKER_FUSE[0]) & (y < CHECKER_FUSE[1]) & (np.abs(nrm[:, 0]) > 0.6) & (z > -0.2) & (z < 0.45)
    color = checker(y - CHECKER_FUSE[0], z + 0.2, 0.28, fuse, color)
    # Glazing of the cockpit canopy and the gondola windows, dark blue-grey.
    glass = ((y < Y(250)) & (y > Y(500)) & (z > Z(122)) & (np.abs(x) < 0.5)) | \
            ((y < Y(470)) & (y > Y(520)) & (z < Z(290)) & (z > Z(305)) & (np.abs(nrm[:, 0]) > 0.6))
    color[glass] = (0.16, 0.20, 0.24)
    return color


def rivet_lines(Vector):
    lines, seams = [], []
    for y, top, bottom, half in FUSELAGE[1:-1]:
        mid = (top + bottom) / 2
        for sgn in (-1, 1):
            seams.append((Vector((sgn * half, y, mid + 0.30)), Vector((sgn * half, y, mid - 0.30))))
    return lines, seams
