"""Build the C2P artillery tractor in High, Mid and Low versions.

  blender --background --factory-startup --python build_c2p.py -- <output_dir>

The running gear, tracks and wheels come from the TKS build (build_tk.py) with the dimensions
of spec_c2p.py. Object names follow the game's Loyd Carrier, the tractor the unit is based on:
Chassis, Chenille_Droite_01 / Chenille_Gauche_01, wheels Roue_D1-D6 / Roue_G1-G6 on Roue_Elev
helpers, Fake, Driver and the tow hook Remorque_1. No weapon.
"""

import math
import os
import sys

import addon_utils
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["TK_SPEC"] = "spec_c2p"
import spec_c2p as S  # noqa: E402
import glass  # noqa: E402

sys.modules["spec_tk"] = S  # build_tk's running gear reads its dimensions from S
import build_tk as T  # noqa: E402
from build_tk import Builder, OUT, helper, material_main, material_track  # noqa: E402

LODS = {
    "Low": {"wheels": False, "detail": 0, "seg": 6, "track": 12, "limit": 700},
    "Mid": {"wheels": True, "detail": 1, "seg": 8, "track": 30, "limit": 2500},
    "High": {"wheels": True, "detail": 2, "seg": 16, "track": 92, "limit": 12000},
}


def tube_path(b, points, width):
    for a, c in zip(points, points[1:]):
        b.strut(a, c, width)


def bow(b, y, seg):
    """Inverted U bow of the tilt frame across the body, rounded at the top corners."""
    h, top, r = S.BOW_HALF, S.BOW_TOP, 0.12
    points = [(-h, y, S.DECK_Z)]
    for i in range(seg + 1):
        a = math.pi - (math.pi / 2) * i / seg
        points.append((-h + r + r * math.cos(a), y, top - r + r * math.sin(a)))
    for i in range(seg + 1):
        a = math.pi / 2 - (math.pi / 2) * i / seg
        points.append((h - r + r * math.cos(a), y, top - r + r * math.sin(a)))
    points.append((h, y, S.DECK_Z))
    tube_path(b, points, 0.03)


def build_body(b, cfg):
    detail = cfg["detail"]
    b.prism(S.HULL_LOWER, -S.HULL_HALF_WIDTH, S.HULL_HALF_WIDTH)
    inner = S.BODY_HALF - S.WALL
    # Decks between the side plates; touching faces would bake black.
    b.prism(S.FRONT_BLOCK, -inner + 0.002, inner - 0.002)
    b.prism(S.REAR_BLOCK, -inner + 0.002, inner - 0.002)
    # Side plates of the open compartment and the floor over the tracks.
    for side in (-1, 1):
        x0, x1 = sorted((side * inner, side * S.BODY_HALF))
        b.prism(S.SIDE, x0, x1)
    b.box((0, (S.FRONT_DECK_Y + S.REAR_DECK_Y) / 2, S.FLOOR_Z - 0.01),
          (2 * inner, S.FRONT_DECK_Y - S.REAR_DECK_Y, 0.02))

    # Engine cover and radiator box.
    ex, ez, er, ey0, ey1 = S.ENGINE
    seg = max(cfg["seg"], 8)
    b.lathe((ex, 0.0, ez), "Y", [(ey0, er), (ey1, er)], seg)
    center, size = S.RADIATOR
    b.box(center, size)

    # Windscreen: frame and panes.
    sy, sh = S.SCREEN_Y, S.SCREEN_HALF
    z0, z1 = S.SCREEN_Z
    frame = [(-sh, sy, z0), (-sh, sy, z1), (sh, sy, z1), (sh, sy, z0)]
    tube_path(b, frame, 0.035)
    b.strut((0, sy, z0), (0, sy, z1), 0.03)
    b.strut((-sh, sy, z0 + 0.04), (sh, sy, z0 + 0.04), 0.035)

    # Tilt bows.
    for y in S.BOWS_Y:
        bow(b, y, 1 if detail == 0 else 3)

    if detail >= 1:
        # Seats: cushions and backrests.
        for x, y in S.FRONT_SEATS:
            b.box((x, y, S.SEAT_Z - 0.04), (0.38, 0.38, 0.08))
            b.box((x, y - 0.21, S.SEAT_Z + 0.14), (0.38, 0.06, 0.34))
        for x, y in S.REAR_SEATS:
            b.box((x, y, S.SEAT_Z - 0.04), (0.30, 0.50, 0.08))
            side = 1 if x > 0 else -1
            b.box((side * (S.BODY_HALF - 0.06), y, S.SEAT_Z + 0.14), (0.06, 0.50, 0.30))
        # Steering wheel on its column and the dashboard under the windscreen.
        wx, wy, wz = S.STEERING
        b.lathe((wx, wy, wz), "Z", [(-0.012, 0.17), (0.012, 0.17)], max(cfg["seg"], 10))
        b.strut((wx, wy, wz), (wx, wy + 0.22, S.FLOOR_Z + 0.05), 0.04)
        b.box((0, sy - 0.06, 0.86), (2 * (S.BODY_HALF - 0.05), 0.10, 0.14))
        # Headlamps on the front deck.
        for x in (-0.55, 0.55):
            b.lathe((x, 1.20, 0.86), "Y", [(-0.05, 0.05), (0.03, 0.075), (0.045, 0.06)], 8)
            b.strut((x, 1.17, 0.78), (x, 1.17, 0.83), 0.03)
        # Tow hook on the rear plate.
        hx, hy, hz = S.TOW_HOOK
        b.box((hx, S.REAR - 0.03, hz), (0.18, 0.06, 0.12))
        b.lathe((hx, hy, hz), "X", [(-0.03, 0.04), (0.03, 0.04)], 8)
        # Final drive housings.
        for side in (-1, 1):
            sy_, sz, _ = S.SPROCKET
            b.lathe((side * (S.HULL_HALF_WIDTH + 0.04), sy_, sz), "X", [(-0.05, 0.085), (0.05, 0.075)], 8)
        for side in (-1, 1):
            T.build_suspension(b, side, detail)

    if detail >= 2:
        add_high_detail(b, cfg)


def add_high_detail(b, cfg):
    """Small parts from the side plate, the card model sheet and the photographs."""
    ex, ez, er, ey0, ey1 = S.ENGINE
    # Bands and filler cap on the engine cover, grille bars on the radiator box.
    for y in (ey0 - 0.04, (ey0 + ey1) / 2, ey1 + 0.04):
        b.lathe((ex, y, ez), "Y", [(-0.015, er + 0.008), (0.015, er + 0.008)], 16)
    b.lathe((ex + 0.10, -0.20, ez + er - 0.02), "Z", [(0.0, 0.04), (0.05, 0.04)], 8)
    (cx, cy, cz), (sx, sy, sz) = S.RADIATOR
    for i in range(9):
        x = cx - sx / 2 + 0.06 + i * (sx - 0.12) / 8
        b.box((x, cy, cz + sz / 2 + 0.008), (0.025, sy - 0.06, 0.016))
    for i in range(6):
        z = cz - sz / 2 + 0.04 + i * (sz - 0.08) / 5
        b.box((cx, cy + sy / 2 + 0.006, z), (sx - 0.08, 0.012, 0.018))
    # Fire extinguisher and three rifles in the rack on the right, behind the bow.
    b.lathe((0.62, -0.30, 0.80), "Z", [(0.0, 0.05), (0.38, 0.05), (0.42, 0.03), (0.46, 0.02)], 10)
    for i, y in enumerate((-0.44, -0.52, -0.60)):
        b.strut((0.74, y, 0.80), (0.74, y, 1.24), 0.025)
        b.box((0.74, y, 0.86), (0.04, 0.05, 0.12))
    b.strut((0.74, -0.40, 1.08), (0.74, -0.64, 1.08), 0.02)
    # Round tail lamp and number plate on the rear plate, tow eyes at the front.
    b.lathe((0.55, S.REAR - 0.01, 0.66), "Y", [(-0.03, 0.10), (0.0, 0.10)], 14)
    b.box((-0.40, S.REAR - 0.01, 0.62), (0.30, 0.012, 0.12))
    for side in (-1, 1):
        b.lathe((side * 0.45, S.FRONT - 0.02, 0.62), "X", [(-0.012, 0.045), (0.012, 0.045)], 8)
    # Small spotlight on the windscreen post and side mirror.
    b.lathe((-S.SCREEN_HALF, S.SCREEN_Y + 0.03, 1.30), "Y", [(-0.04, 0.04), (0.04, 0.06)], 8)
    # Hand grips along the top of the sides.
    for side in (-1, 1):
        x = side * (S.BODY_HALF + 0.015)
        for y0, y1 in ((0.30, -0.05), (-0.55, -0.95)):
            b.strut((x - side * 0.015, y0, 0.72), (x, y0, 0.72), 0.014)
            b.strut((x - side * 0.015, y1, 0.72), (x, y1, 0.72), 0.014)
            b.strut((x, y0, 0.72), (x, y1, 0.72), 0.014)
    # Shovel on the left front deck.
    b.box((-0.70, 1.15, 0.78), (0.12, 0.22, 0.012))
    b.strut((-0.70, 1.04, 0.775), (-0.70, 1.40, 0.745), 0.025)


def build(name, cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_scene_fbx")
    bpy.context.scene.unit_settings.system = "METRIC"
    collection = bpy.data.collections.new("%s_%s" % (S.STEM, name))
    bpy.context.scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]

    main = material_main()
    moving = name == "High"
    mat_d = material_track("M_Chenille_D", "chenilledroite") if moving else main
    mat_g = material_track("M_Chenille_G", "chenillegauche") if moving else main

    b = Builder()
    build_body(b, cfg)
    chassis = b.finish("Chassis", main)
    vitre = glass.material(S.STEM, os.path.join(OUT, "textures"))
    glass.add_panes("Pare_brise", [glass.rect(x0, x1, S.SCREEN_Y, S.SCREEN_Y, z0, z1, "+Y")
                                   for x0, x1, z0, z1 in S.SCREEN_PANES], vitre, chassis)
    if cfg["wheels"]:
        T.build_wheels(cfg, main, chassis)
    track_d = T.build_track("Chenille_Droite_01", 1, cfg["track"], mat_d, chassis, moving)
    track_g = T.build_track("Chenille_Gauche_01", -1, cfg["track"], mat_g, chassis, moving)

    helper("Fake", (0, 0, 0.4), chassis)
    helper("Fx_Stress_01", (0, -0.9, 1.15), chassis)
    helper("Fx_Stress_02", (0.4, 0.9, 0.95), chassis)
    helper("FX_Fumee_Chenille_D1", (S.TRACK_X, -1.20, 0.06), chassis)
    helper("FX_Fumee_Chenille_G1", (-S.TRACK_X, -1.20, 0.06), chassis)
    helper("Driver", S.DRIVER, chassis)
    helper("Remorque_1", S.TOW_HOOK, chassis)
    if cfg["wheels"]:
        T.skin_track(track_d, "D")
        T.skin_track(track_g, "G")

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not glass.is_glass(o)]
    T.unwrap([o for o in meshes if not (moving and o.name.startswith("Chenille"))])
    T.report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    print("BUILD_DONE")
