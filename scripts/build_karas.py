"""Build the PZL.23B Karaś in High, Mid and Low versions, plus the landing gear file.

  blender --background --factory-startup --python build_karas.py -- <output_dir>

Reuses the wing, tail, engine, wheel and gun builders of build_p11.py with spec_karas.py.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_karas"
import spec_karas as S  # noqa: E402
import build_tk as T  # noqa: E402
import build_p11 as P  # noqa: E402

P.S = S
Builder, helper = T.Builder, T.helper
OUT = T.OUT

LODS = {
    "Low": {"detail": 0, "ring": 6, "foil": 4, "seg": 6, "limit": 900},
    "Mid": {"detail": 1, "ring": 10, "foil": 8, "seg": 10, "limit": 2200},
    "High": {"detail": 2, "ring": 18, "foil": 16, "seg": 18, "limit": 12000},
}


def build_wing(b, cfg):
    n = cfg["foil"]
    a0, a1, ail = S.AILERON
    eps = 0.003
    table = [row[0] for row in S.WING]
    spans = sorted(set(table + [a0, a0 + eps, a1, a1 + eps]))
    if cfg["detail"] == 0:
        spans = [table[0], 3.0, a0, a0 + eps, a1, a1 + eps, table[-1]]
    rings = []
    for side in (-1, 1):
        for span in (spans if side > 0 else list(reversed(spans))):
            le, te, zc, t = P.wing_station(span)
            cut = a0 + eps * 0.5 <= span <= a1 + eps * 0.5
            f1 = 1.0 - ail / (le - te) if cut else 1.0
            rings.append(P.section(n, le, te, zc, t, 0.0, f1, pos=side * span))
    b.loft(rings)


def build_aileron(cfg, mat, chassis, side, name):
    n = max(4, cfg["foil"] // 2)
    a0, a1, ail = S.AILERON
    rings = []
    for span in (a0 + 0.003, (a0 + a1) / 2, a1):
        le, te, zc, t = P.wing_station(span)
        rings.append(P.section(n, le, te, zc, t, 1.0 - ail / (le - te), 1.0, pos=side * span))
    le, te, zc, t = P.wing_station((a0 + a1) / 2)
    b = Builder()
    b.loft(rings)
    return b.finish(name, mat, (side * (a0 + a1) / 2, te + ail, zc), chassis, sharp=50)


def trouser(b, side, cfg):
    """Streamlined leg fairing and wheel spat, horizontal airfoil sections stacked down."""
    n = max(4, cfg["foil"] - 2)
    xc = side * S.WHEEL_X
    rings = []
    for z, le, te, t in ((S.Z(262), S.Y(292), S.Y(400), 0.30), (S.Z(330), S.Y(286), S.Y(405), 0.30),
                         (S.Z(380), S.Y(276), S.Y(410), 0.26), (S.Z(405), S.Y(290), S.Y(395), 0.20)):
        rings.append([(xc + d, y, z) for d, y, _ in P.section(n, le, te, 0.0, t, 0.0, 0.999, camber=0.0, axis="Z", pos=z)])
    b.loft(rings)


def build_chassis(cfg, mat):
    detail, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    b.loft([P.superellipse(y, top, bot, half, cfg["ring"]) for y, top, bot, half in S.FUSELAGE])
    # Ventral gondola under the rear of the wing.
    top = S.Z(272)
    b.loft([P.superellipse(y, top, bot, half, max(6, cfg["ring"] - 4), p=3.0) for y, bot, half in S.GONDOLA])
    # Engine cowling ring and engine face.
    front, rear, r = S.COWL_FRONT, S.COWL_REAR, S.COWL_R
    off = lambda y: y - rear  # noqa: E731
    if detail == 0:
        b.lathe((0, rear, -0.03), "Y", [(0.0, 0.62), (off(front), r), (off(front) - 0.10, r - 0.13)], 8)
    else:
        b.lathe((0, rear, -0.03), "Y", [(0.0, 0.64), (off(front) - 0.10, r), (off(front), r - 0.03), (off(front), r - 0.11),
                                        (off(front) - 0.12, r - 0.14), (0.08, 0.52)], seg + 2)
        cy = front - 0.20
        b.lathe((0, cy, -0.03), "Y", [(-0.12, 0.12), (0.0, 0.26), (0.10, 0.22)], max(8, seg))
        for i in range(9 if detail >= 2 else 0):
            a = math.tau * i / 9
            d = Vector((math.cos(a), 0.0, math.sin(a)))
            base = Vector((0, cy, -0.03))
            b.strut(base + d * 0.22, base + d * 0.54, 0.13, 0.13)
    build_wing(b, cfg)
    # Tailplane and fin (fixed parts).
    n = max(4, cfg["foil"] - 2)
    rings = []
    for side in (-1, 1):
        for span, le, hinge, te in (S.TAILPLANE if side > 0 else list(reversed(S.TAILPLANE))):
            rings.append(P.section(n, le, te, S.TAIL_Z, 0.08, 0.0, (le - hinge) / (le - te), camber=0.0, pos=side * span))
    b.loft(rings)
    fin = []
    for z, le in S.FIN:
        te = S.HINGE_RUDDER - 0.25
        fin.append(P.section(n, le, te, 0.0, 0.08, 0.0, min((le - S.HINGE_RUDDER) / (le - te), 0.999), camber=0.0,
                             axis="Z", pos=z))
    b.loft(fin)
    for side in (-1, 1):
        trouser(b, side, cfg)
    if detail >= 1:
        # Cockpit canopy and the long glazed top behind it.
        b.loft([P.superellipse(y, t, S.Z(140), w, 8, p=2.2) for y, t, w in
                ((S.Y(255), S.Z(146), 0.18), (S.Y(275), S.Z(110), 0.30), (S.Y(360), S.Z(107), 0.32),
                 (S.Y(500), S.Z(112), 0.30), (S.Y(520), S.Z(122), 0.26))])
        # Dorsal gun ring and bomb racks under the wing.
        dx, dy, dz = S.DORSAL
        b.lathe((dx, dy, dz - 0.03), "Z", [(0.0, 0.34), (0.05, 0.30)], max(8, seg))
        for x, y, z in S.BOMBS:
            b.box((x, y, z + 0.06), (0.10, 0.70, 0.08))
    if detail >= 2:
        # Long exhaust pipe on the left side and the radio mast.
        b.strut((-0.62, S.Y(196), S.Z(215)), (-0.60, S.Y(360), S.Z(215)), 0.07, 0.07)
        b.strut((-0.60, S.Y(360), S.Z(215)), (-0.50, S.Y(372), S.Z(235)), 0.07, 0.07)
        b.strut((0.0, S.Y(222), S.Z(140)), (0.0, S.Y(226), S.Z(122)), 0.03, 0.03)
    return b.finish("Chassis", mat)


def rear_gun(cfg, mat, chassis, number, pivot, muzzle_y):
    pivot = Vector(pivot)
    b = Builder()
    b.lathe(pivot, "Z", [(-0.06, 0.06), (0.0, 0.05)], 6)
    tourelle = b.finish("Tourelle_%02d" % number, mat, pivot, chassis)
    b = Builder()
    b.box((pivot.x, pivot.y + 0.05, pivot.z + 0.06), (0.07, 0.40, 0.10))
    if cfg["detail"]:
        b.lathe((pivot.x, pivot.y, pivot.z + 0.17), "X", [(-0.03, 0.09), (0.03, 0.09)], 8)
        b.box((pivot.x, pivot.y + 0.25, pivot.z + 0.02), (0.04, 0.10, 0.12))
    axe = b.finish("Axe_Canon_%02d" % number, mat, pivot, tourelle)
    b = Builder()
    length = pivot.y - muzzle_y
    b.lathe((pivot.x, pivot.y - 0.15, pivot.z + 0.06), "Y", [(-length + 0.15, 0.014), (0.0, 0.022)], 6 if cfg["detail"] else 4)
    canon = b.finish("Canon_%02d" % number, mat, pivot, axe)
    helper("Fx_tourelle%d_tir_01" % number, (pivot.x, muzzle_y - 0.01, pivot.z + 0.06), canon)


def build(name, cfg):
    P.new_scene("%s_%s" % (S.STEM, name))
    main = T.material_main()
    chassis = build_chassis(cfg, main)
    build_aileron(cfg, main, chassis, 1, "Aileron_D")
    build_aileron(cfg, main, chassis, -1, "Aileron_G")
    controls = P.build_controls
    # Reuse the tail control builders without the P.11 ailerons.
    saved, P.build_aileron = P.build_aileron, lambda *a, **k: None
    controls(cfg, main, chassis)
    P.build_aileron = saved
    P.build_engine(cfg, main, chassis)
    P.build_wheels(cfg, main, chassis)
    P.build_guns(cfg, main, chassis)
    rear_gun(cfg, main, chassis, 2, S.DORSAL, S.DORSAL_MUZZLE_Y)
    rear_gun(cfg, main, chassis, 3, S.VENTRAL, S.VENTRAL_MUZZLE_Y)
    for hname, pos in (("Pilot", S.PILOT), ("Pilot2", S.PILOT2), ("Pilot3", S.PILOT3),
                       ("FX_Vortex_D", S.VORTEX), ("FX_Vortex_G", (-S.VORTEX[0], S.VORTEX[1], S.VORTEX[2])),
                       ("Fx_Stress_01", (0.40, S.Y(450), 0.0)), ("Fx_Stress_02", (-0.35, S.Y(200), 0.0))):
        helper(hname, pos, chassis)
    for i, pos in enumerate(S.BOMBS):
        helper("AS_%d_%d" % (i // 2 + 1, i % 2 + 1), pos, chassis)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap(meshes)
    P.report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        P.render_clay()
    P.build_train()
    print("BUILD_DONE")
