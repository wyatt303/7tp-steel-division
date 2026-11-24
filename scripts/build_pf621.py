"""Build the Polski Fiat 621L truck in High, Mid and Low versions.

  blender --background --factory-startup --python build_pf621.py -- <output_dir>

Node layout copied from the game's Opel Blitz, see spec_pf621.py.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_pf621"
import spec_pf621 as S  # noqa: E402
import build_tk as T  # noqa: E402
import build_p11 as P  # noqa: E402
import build_wz34 as W  # noqa: E402

W.S = S
P.S = S
Builder, helper = T.Builder, T.helper
OUT = T.OUT

LODS = {
    "Low": {"detail": 0, "seg": 8, "limit": 700},
    "Mid": {"detail": 1, "seg": 10, "limit": 2000},
    "High": {"detail": 2, "seg": 20, "limit": 8000},
}


def ring(y, bottom, top, half, bevel=0.06):
    """Cross-section with bevelled upper corners, right side first."""
    return [(half, y, bottom), (half, y, top - bevel), (half - bevel, y, top), (-half + bevel, y, top),
            (-half, y, top - bevel), (-half, y, bottom)]


def build_chassis(cfg, mat):
    d, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    # Frame rails and the cross members.
    z0, z1 = S.FRAME_Z
    for side in (-1, 1):
        b.box((side * 0.42, (S.FRONT_Y + S.REAR_Y) / 2 + 0.05, (z0 + z1) / 2), (0.08, S.FRONT_Y - S.REAR_Y - 0.15, z1 - z0))
    # Bonnet with the radiator shell, and the closed cab.
    b.loft([ring(*r) for r in S.BONNET])
    fy, ry, cz0, cz1, ch = S.CAB
    b.loft([ring(fy, cz0, cz1, ch, 0.10), ring(ry, cz0, cz1, ch, 0.10)])
    # Cargo body: floor and sides, and the canvas tilt on its bows.
    by0, by1, floor, side_top, bh = S.BODY
    b.box((0.0, (by0 + by1) / 2, floor - 0.06), (2 * bh, by0 - by1, 0.12))
    # Body bearers between the frame and the floor.
    for side in (-1, 1):
        b.box((side * 0.42, (by0 + by1) / 2, (S.FRAME_Z[1] + floor - 0.12) / 2), (0.10, by0 - by1 - 0.05, floor - 0.12 - S.FRAME_Z[1]))
    for side in (-1, 1):
        b.box((side * (bh - 0.02), (by0 + by1) / 2, (floor + side_top) / 2), (0.04, by0 - by1, side_top - floor))
    b.box((0.0, by1 + 0.02, (floor + side_top) / 2), (2 * bh, 0.04, side_top - floor))
    b.box((0.0, by0 - 0.02, (floor + side_top) / 2), (2 * bh, 0.04, side_top - floor))
    tilt = [ring(y, side_top - 0.02, S.TILT_TOP, bh + 0.01, 0.25) for y in (by0 - 0.01, by1 + 0.01)]
    b.loft(tilt)
    # Front mudguards down to the running boards, rear mudguards over the twin wheels.
    steps = {0: 3, 1: 6, 2: 10}[d]
    for side in (-1, 1):
        cy, cz, r, a0, a1, x0, x1 = S.FRONT_GUARD
        lo, hi = sorted((side * x0, side * x1))
        W.arc_strip(b, (cy, cz, r, a0, a1, lo, hi), steps)
        sy0, sy1, sz = S.STEP
        b.box((side * (S.FRONT_X), (sy0 + sy1) / 2, sz), (0.30, sy0 - sy1, 0.03))
        b.box((side * (S.REAR_X[1] + 0.02), S.REAR_AXLE_Y, floor - 0.04), (0.30, 1.10, 0.03))
    # Bumper, headlamps and radiator grille.
    b.lathe((0.0, S.FRONT_Y - 0.05, 0.62), "X", [(-1.0, 0.05), (1.0, 0.05)], max(6, seg // 2))
    for x, y, z in S.HEADLAMPS:
        b.lathe((x, y, z), "Y", [(-0.10, 0.09), (0.0, 0.13), (0.03, 0.12)], max(8, seg))
        if d >= 1:
            b.strut((x, y - 0.05, z - 0.10), (x * 0.70, y - 0.05, 0.86), 0.03)
    if d >= 1:
        b.box((0.0, S.BONNET[0][0] + 0.012, 1.16), (0.62, 0.02, 0.62))
        for side in (-1, 1):
            # Bonnet side louvres, door handles and the canvas tie rails.
            for k in range(5 if d >= 2 else 2):
                y = 2.15 - k * 0.16
                b.box((side * (S.BONNET[2][3] + 0.005), y, 1.18), (0.012, 0.05, 0.30))
            b.box((side * (ch + 0.006), 0.70, 1.45), (0.012, 0.80, 0.02))
            b.box((side * (bh + 0.006), (by0 + by1) / 2, side_top - 0.05), (0.012, by0 - by1 - 0.1, 0.03))
        # Windscreen frame bar and the spare wheel under the body.
        b.box((0.0, fy + 0.012, (S.WINDSCREEN_Z[0] + S.WINDSCREEN_Z[1]) / 2), (0.03, 0.02, S.WINDSCREEN_Z[1] - S.WINDSCREEN_Z[0]))
        b.lathe((0.0, by0 - 0.65, floor - 0.30), "Z", [(-0.08, S.TYRE_R), (0.08, S.TYRE_R)], seg)
    if d >= 2:
        # Axles, leaf springs, fuel tank, exhaust and tow hooks.
        for axle in (S.FRONT_AXLE_Y, S.REAR_AXLE_Y):
            b.lathe((0.0, axle, S.WHEEL_Z), "X", [(-0.75, 0.05), (0.75, 0.05)], 8)
            for side in (-1, 1):
                b.box((side * 0.42, axle, S.WHEEL_Z + 0.12), (0.07, 1.10, 0.06))
        b.lathe((0.0, S.REAR_AXLE_Y, S.WHEEL_Z), "Y", [(-0.15, 0.10), (0.0, 0.17), (0.15, 0.10)], 10)
        b.lathe((-0.60, 0.20, 0.55), "Y", [(-0.30, 0.16), (0.30, 0.16)], 10)
        mx, my, mz = S.MUFFLER
        b.lathe((mx, my, mz), "Y", [(-0.30, 0.06), (0.30, 0.06)], 8)
        for side in (-1, 1):
            b.box((side * 0.30, S.FRONT_Y - 0.02, 0.50), (0.05, 0.10, 0.08))
        tx, ty, tz = S.TOW_HOOK
        b.box((tx, ty + 0.10, tz), (0.10, 0.20, 0.08))
        b.lathe((tx, ty, tz), "X", [(-0.02, 0.05), (0.02, 0.05)], 8)
    return b.finish("Chassis", mat)


def build_wheels(cfg, mat):
    seg, d = cfg["seg"], cfg["detail"]
    for name, side in (("Roue_Droite_01", 1), ("Roue_Gauche_01", -1)):
        c = Vector((side * S.FRONT_X, S.FRONT_AXLE_Y, S.WHEEL_Z))
        b = Builder()
        W.tyre(b, c, S.TYRE_W, seg, d, side)
        b.finish(name, mat, c, None, sharp=60)
    pivot = Vector((0.0, S.REAR_AXLE_Y, S.WHEEL_Z))
    b = Builder()
    for side in (-1, 1):
        for k, x in enumerate(S.REAR_X):
            W.tyre(b, (side * x, S.REAR_AXLE_Y, S.WHEEL_Z), S.TYRE_W, seg, d if k == 1 else min(d, 1), side)
    b.finish("Roue_02", mat, pivot, None, sharp=60)


def build(name, cfg):
    P.new_scene("%s_%s" % (S.STEM, name))
    main = T.material_main()
    chassis = build_chassis(cfg, main)
    build_wheels(cfg, main)
    helper("Driver", S.DRIVER, chassis)
    helper("Remorque_1", S.TOW_HOOK, chassis)
    helper("Fx_Stress_01", S.FX_STRESS[0], chassis)
    helper("Fx_Stress_02", S.FX_STRESS[1], chassis)
    for side, letter in ((1, "D"), (-1, "G")):
        helper("FX_Fumee_Roue_%s1" % letter, (side * S.REAR_X[1], S.REAR_AXLE_Y, 0.0), None)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap(meshes)
    P.report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        W.render_clay()
    print("BUILD_DONE")
