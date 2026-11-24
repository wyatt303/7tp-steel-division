"""Sokół 1000 (CWS M111) with sidecar and a Browning wz. 28 light machine gun, in metres.

Faces +Y, right +X, ground Z=0. The motorcycle sits on the left and the sidecar on the
right, as on the game's BMW R75, whose node layout this copies:
Chassis, Axis (steering: fork, handlebar, front mudguard, headlamp), Motard (rider),
Tourelle_01 -> Axe_Canon_01 -> Canon_01 (the gun on the sidecar mount), wheels
Roue_Droite_01 (front, steered), Roue_03 (rear), Roue_02 (sidecar) without parents,
helpers Roue_Gauche_01, Tireur, Fx_Stress_01/02 and FX_Fumee_Roue_D1/G1.

Sources: Kraków Museum of Engineering and Transport data for the CWS M111 with sidecar
(length 2230 mm, width 1680 mm, height 1230 mm), and photographs on Wikimedia Commons,
viewed in a browser, a three-view blueprint from the-blueprints.com with the 1464 mm
wheelbase dimension (supplied by the author, measured at 2.614 mm per pixel), a museum side view (Sokół1000 MSPO14 DSC02336), which gives the
wheelbase as about twice the wheel diameter and the tank, saddle, handlebar and headlamp
heights, and two period photos of the military version (Rkm wz.28 na motocyklu Sokół,
CWS M111 z ckm wz. 30) showing the tall gun pintle. The painting guide of a CWS M-111
model kit (front, rear, both sides and top views, supplied by the author) gives the
sidecar layout: cockpit in front, spare wheel lying flat on the rear deck, a can on the
sidecar frame and a pillion pad on the motorcycle's carrier.
"""

STEM = "SOKOL1000"
VARIANT = "rkm"
TRACKED = False
DUST = 0.4

BIKE_X = -0.52
SIDE_X = 0.30            # sidecar body centre line
SIDE_WHEEL_X = 0.74
FRONT_Y, REAR_Y, SIDE_WHEEL_Y = 0.732, -0.732, -0.20   # wheelbase 1464 mm
WHEEL_R, WHEEL_W = 0.345, 0.10                          # 4.40-19 tyres
SIDE_WHEEL_R = 0.34
ROAD_R = WHEEL_R

STEER_HEAD = (BIKE_X, 0.43, 0.84)    # Axis pivot, as on the R75
HANDLEBAR_Z, HANDLEBAR_HALF, GRIP_Y = 0.97, 0.35, 0.10
HEADLAMP = (BIKE_X, 0.55, 1.01)

# Sidecar body: plan stations (Y, half width, bottom Z, top Z), nose to tail.
SIDECAR = [(0.80, 0.04, 0.46, 0.54), (0.55, 0.20, 0.32, 0.68), (0.20, 0.29, 0.27, 0.73), (-0.30, 0.30, 0.27, 0.75),
           (-0.70, 0.27, 0.30, 0.73), (-0.88, 0.16, 0.38, 0.66)]
SEAT_OPENING = (0.30, -0.25)           # Y range of the sidecar cockpit

MOUNT = (SIDE_X + 0.06, 0.40, 1.00)    # gun pivot on the tall sidecar pintle
MUZZLE_Y = MOUNT[1] + 0.78
SPARE = (SIDE_X, -0.60, 0.81)          # spare wheel lying flat on the rear deck
TIREUR = (SIDE_X, -0.05, 0.55)
TURRETS = {1: {"center": MOUNT, "mount": MOUNT, "muzzle_y": MUZZLE_Y}}

MUFFLER = (BIKE_X + 0.14, -0.80, 0.16)

# Paint: Polish army khaki on the machine; rider in khaki uniform with a wz. 31 helmet.
PART_RIDER, PART_SKIN = 5, 6
PART_IDS = {"Motard": PART_RIDER}
KHAKI = (0.27, 0.27, 0.18)
UNIFORM = (0.33, 0.31, 0.21)
LEATHER = (0.12, 0.08, 0.05)
METAL = (0.22, 0.22, 0.21)


def is_tyre(name):
    if name in ("Roue_Droite_01", "Roue_03"):
        return WHEEL_R
    if name == "Roue_02":
        return SIDE_WHEEL_R
    return False


def paint_color(pos, nrm, np, part=None):
    color = np.tile(np.array(KHAKI, np.float32), (len(pos), 1))
    # Bare metal engine and exhaust area of the motorcycle.
    engine = (np.abs(pos[:, 0] - BIKE_X) < 0.16) & (pos[:, 2] < 0.60) & (pos[:, 2] > 0.14) & (np.abs(pos[:, 1]) < 0.36)
    color[engine] = METAL
    saddle = (np.abs(pos[:, 0] - BIKE_X) < 0.15) & (np.abs(pos[:, 1] + 0.23) < 0.16) & (pos[:, 2] > 0.72) & (pos[:, 2] < 0.82)
    color[saddle] = LEATHER
    bags = (np.abs(np.abs(pos[:, 0] - BIKE_X) - 0.17) < 0.06) & (np.abs(pos[:, 1] + 0.85) < 0.17) & (pos[:, 2] > 0.44) & (pos[:, 2] < 0.72)
    color[bags] = (0.40, 0.22, 0.10)
    pad = (np.abs(pos[:, 0] - BIKE_X) < 0.10) & (np.abs(pos[:, 1] + 0.85) < 0.14) & (pos[:, 2] > 0.85)
    color[pad] = LEATHER
    if part is not None:
        rider = part == PART_RIDER
        color[rider] = UNIFORM
        boots = rider & (pos[:, 2] < 0.42)
        color[boots] = LEATHER
        face = rider & (pos[:, 2] > 1.26) & (pos[:, 2] < 1.39) & (nrm[:, 1] > 0.3)
        color[face] = (0.62, 0.47, 0.37)
        hands = rider & (np.abs(pos[:, 1] - GRIP_Y) < 0.06) & (pos[:, 2] > 0.90) & (pos[:, 2] < 1.05)
        color[hands] = (0.62, 0.47, 0.37)
    return color


def rivet_lines(Vector):
    return [], []


RENDER_VIEWS = {
    "przod_3_4": ("PERSP", (3.2, 3.4, 1.7), (0.0, 0.0, 0.65), 45),
    "tyl_3_4": ("PERSP", (-2.8, -3.6, 1.8), (0.0, -0.1, 0.65), 45),
    "bok": ("ORTHO", (-8, -0.06, 0.72), (0.0, -0.06, 0.72), 2.7),
    "zblizenie": ("PERSP", (1.8, 2.2, 1.5), (0.2, 0.3, 0.85), 45),
}
