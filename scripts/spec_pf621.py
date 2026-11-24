"""Polski Fiat 621L 2.5 t military truck with a canvas tilt, in metres. Faces +Y, right +X.

Sources: data (length 5.78 m, width 2.07 m, height 2.62 m, wheelbase 3.65 m) from the
English Wikipedia and techno-science.net, and photographs on Wikimedia Commons viewed in a
browser (the restored military 621L "Polski Fiat 621L.jpg", a museum scale model with the
1936 camouflage, the fire engine "Polski Fiat 621 L Warsaw"). Overhangs, wheel size, track
and the cab, bonnet and cargo body heights are estimates that fit those figures.

Node layout follows the game's Opel Blitz (GER/Vehicule.zip): Chassis, front wheels
Roue_Droite_01 / Roue_Gauche_01, the whole rear axle Roue_02 (twin tyres), helpers Driver,
Remorque_1, Fx_Stress_01/02 and FX_Fumee_Roue_D1/G1. No turret.
"""

STEM = "PF621L"
VARIANT = "pf621"
TRACKED = False
DUST = 0.8

TYRE_R, TYRE_W, RIM_R = 0.43, 0.17, 0.25
ROAD_R = TYRE_R
WHEEL_Z = TYRE_R
FRONT_AXLE_Y = 2.14
REAR_AXLE_Y = FRONT_AXLE_Y - 3.65
FRONT_X = 0.80
REAR_X = (0.70, 0.89)

FRONT_Y, REAR_Y = 2.89, -2.89          # bumper and tailgate
FRAME_Z = (0.55, 0.72)

# Bonnet: (Y, bottom Z, top Z, half width) from the radiator back to the cowl.
BONNET = [(2.58, 0.80, 1.52, 0.40), (2.52, 0.78, 1.56, 0.42), (1.32, 0.78, 1.60, 0.44)]
CAB = (1.32, 0.05, 0.78, 2.20, 0.96)     # front Y, rear Y, bottom Z, roof Z, half width
WINDSCREEN_Z = (1.58, 2.07)
BODY = (-0.02, -2.86, 1.10, 1.72, 1.035)  # cargo body: front Y, rear Y, floor Z, side top Z, half width
TILT_TOP = 2.62
HEADLAMPS = [(0.55, 2.50, 1.28), (-0.55, 2.50, 1.28)]
FRONT_GUARD = (FRONT_AXLE_Y, WHEEL_Z, 0.53, 15, 175, FRONT_X - 0.16, FRONT_X + 0.16)
STEP = (1.30, 0.20, 0.60)                # running board from Y, to Y, Z

DRIVER = (-0.45, 0.70, 1.35)
TOW_HOOK = (0.0, REAR_Y - 0.06, 0.70)
MUFFLER = (0.45, -0.60, 0.48)
FX_STRESS = [(0.0, -1.5, 1.9), (0.3, 1.9, 1.3)]


def is_tyre(name):
    return name.startswith("Roue_")


UV_COPIES = {"Roue_Gauche_01": "Roue_Droite_01"}

RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (7.8, 8.0, 3.2), (0, 0.0, 1.2), 45),
    "tyl_3_4": ("PERSP", (-6.5, -8.8, 3.5), (0, -0.3, 1.2), 45),
    "bok": ("ORTHO", (14, 0, 1.35), (0, 0, 1.35), 6.6),
    "zblizenie": ("PERSP", (3.4, 5.4, 2.0), (0.0, 1.5, 1.3), 45),
}


def rivet_lines(Vector):
    """Panel seams of the cab and the plank lines of the wooden cargo body."""
    lines, seams = [], []
    by0, by1, floor, side_top, bh = BODY
    for side in (-1, 1):
        x = side * (bh + 0.001)
        for k in range(1, 4):
            z = floor + (side_top - floor) * k / 4
            seams.append((Vector((x, by0 - 0.05, z)), Vector((x, by1 + 0.05, z))))
        x = side * (CAB[4] + 0.001)
        seams.append((Vector((x, 0.30, CAB[2] + 0.10)), Vector((x, 0.30, CAB[3] - 0.15))))
        seams.append((Vector((x, 1.10, CAB[2] + 0.10)), Vector((x, 1.10, CAB[3] - 0.15))))
    return lines, seams


# Windscreen (two panes) and the cab side windows: (x0, x1, y0, y1, z0, z1).
GLASS_BOXES = [
    (-0.90, 0.90, CAB[0] - 0.02, CAB[0] + 0.05, WINDSCREEN_Z[0], WINDSCREEN_Z[1]),
    (-1.00, -0.90, 0.45, 1.20, 1.55, 2.05),
    (0.90, 1.00, 0.45, 1.20, 1.55, 2.05),
]
