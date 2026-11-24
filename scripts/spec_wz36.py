"""37 mm armata przeciwpancerna wz. 36 (Bofors), in metres. Muzzle +Y, right +X, ground Z=0.

Sources: data from the English and Polish Wikipedia and valka.cz (length in firing position
3.05 m, width 1.22 m, height 1.01 m, barrel L/45 = 1.665 m, line of fire 0.62 m, split
trail spreading to ±25 degrees, steel wheels with rubber tyres, 5 mm shield with a folding
lower part, small muzzle brake) and museum photographs on Wikimedia Commons, viewed in a
browser (Parola museum, Finnish museum). Wheel size, track and trail length are estimates
that fit the overall dimensions.

Node layout follows the game's PaK 36 (GER/Canon.zip): Chassis (the axle), Tourelle_01
(upper carriage and shield), Axe_Canon_01 (cradle and breech), Canon_01 (barrel),
Bras_Gauche / Bras_Droit (trails, spread as in firing position), Roue_D1 / Roue_G1 under the
Chassis, Remorque_2 at the end of the right trail, Fx_Stress_01/02, FX_Fumee_Roue_D1/G1.
The crew positions go into a Boites_<stem> file with Canon_AT, servant_G and servant_D.
"""

STEM = "WZ36_BOFORS"
VARIANT = "wz36"
TRACKED = False
DUST = 0.5

WHEEL_R, WHEEL_W, WHEEL_X = 0.30, 0.12, 0.55
AXLE = (0.0, 0.0, WHEEL_R)
FIRE_Z = 0.62                         # line of fire
TRUNNION = (0.0, -0.05, FIRE_Z)       # Axe_Canon_01 pivot
BREECH_Y = -0.38                      # Canon_01 pivot, rear of the barrel
BARREL = 1.665
MUZZLE_Y = BREECH_Y + BARREL + 0.10   # including the muzzle brake
TURRET = (0.0, -0.02, 0.42)           # Tourelle_01 pivot, upper carriage

# Shield: upper plates (two halves angled back by 8 degrees) and folding lower plates.
SHIELD_Y = 0.22
SHIELD_HALF = 0.60
SHIELD_UPPER = (0.56, 1.01)            # Z range
SHIELD_LOWER = (0.14, 0.55)
SIGHT_HOLE_X = 0.20

TRAIL_HINGE = (0.15, -0.22, 0.32)     # right trail hinge; the left one mirrors it
TRAIL_LEN = 1.55
TRAIL_SPREAD = 25.0                   # degrees from the centre line

FX_STRESS = [(0.0, 0.05, 0.85), (0.30, -0.30, 0.40)]
CREW = {"Canon_AT": (0.0, 0.11, 0.0), "servant_G": (-0.92, -1.09, 0.0), "servant_D": (0.82, -1.10, 0.0)}

ROAD_R = WHEEL_R
MUFFLER = (99.0, 99.0, 99.0)


def is_tyre(name):
    return WHEEL_R if name in ("Roue_D1", "Roue_G1") else False


def rivet_lines(Vector):
    """Rivet rows round the shield plates."""
    lines, seams = [], []
    for side in (-1, 1):
        for z0, z1 in (SHIELD_UPPER, SHIELD_LOWER):
            x0, x1 = side * 0.04, side * (SHIELD_HALF - 0.04)
            y0 = SHIELD_Y - 0.012
            y1 = SHIELD_Y - abs(x1) * 0.14 - 0.012
            lines.append((Vector((x0, y0, z1 - 0.03)), Vector((x1, y1, z1 - 0.03)), 0.07))
            lines.append((Vector((x0, y0, z0 + 0.03)), Vector((x1, y1, z0 + 0.03)), 0.07))
    return lines, seams


RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (3.0, 3.6, 1.6), (0.0, -0.1, 0.45), 45),
    "tyl_3_4": ("PERSP", (-2.6, -3.8, 1.9), (0.0, -0.3, 0.45), 45),
    "bok": ("ORTHO", (8, -0.15, 0.55), (0.0, -0.15, 0.55), 3.5),
    "zblizenie": ("PERSP", (1.6, -1.8, 1.4), (0.0, -0.2, 0.55), 45),
}
