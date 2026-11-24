"""Build the PZL.37B Łoś in High, Mid and Low versions, plus the retractable gear file.

  blender --background --factory-startup --python build_los.py -- <output_dir>

Layout copied from the game's Ju 88 / Ju 188, see spec_los.py. Reuses the airfoil and
fuselage helpers of build_p11.py.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_los"
import spec_los as S  # noqa: E402
import build_tk as T  # noqa: E402
import build_p11 as P  # noqa: E402

P.S = S
Builder, helper = T.Builder, T.helper
OUT = T.OUT

LODS = {
    "Low": {"detail": 0, "ring": 6, "foil": 4, "seg": 6, "limit": 1200},
    "Mid": {"detail": 1, "ring": 10, "foil": 8, "seg": 10, "limit": 2600},
    "High": {"detail": 2, "ring": 18, "foil": 16, "seg": 18, "limit": 12000},
}


def build_wing(b, cfg):
    n = cfg["foil"]
    a0, a1, ail = S.AILERON
    eps = 0.003
    table = [row[0] for row in S.WING]
    spans = sorted(set(table + [a0, a0 + eps, a1, a1 + eps]))
    if cfg["detail"] == 0:
        spans = [table[0], table[1], a0, a0 + eps, a1, a1 + eps, table[-1]]
    rings = []
    for side in (-1, 1):
        for span in (spans if side > 0 else list(reversed(spans))):
            le, te, zc, t = P.wing_station(span)
            cut = a0 + eps * 0.5 <= span <= a1 + eps * 0.5
            rings.append(P.section(n, le, te, zc, t, 0.0, 1.0 - ail / (le - te) if cut else 1.0, pos=side * span))
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
    b.finish(name, mat, (side * (a0 + a1) / 2, te + ail, zc), chassis, sharp=50)


def vertical_section(n, x, z, le, te, t, f0, f1):
    return [(x + d, y, z) for d, y, _ in P.section(n, le, te, 0.0, t, f0, f1, camber=0.0, axis="Z", pos=z)]


def build_chassis(cfg, mat):
    d, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    b.loft([P.superellipse(y, top, bot, half, cfg["ring"]) for y, top, bot, half in S.FUSELAGE])
    build_wing(b, cfg)
    # Nacelles with the NACA cowling ring and the engine face.
    for side in (-1, 1):
        x = side * S.NACELLE_X
        center = (x, 0.0, S.NACELLE_Z)
        b.lathe(center, "Y", [(y, r) for y, r in reversed(S.NACELLE)], max(8, seg))
        if d >= 1:
            b.lathe((x, S.COWL_FRONT - 0.20, S.NACELLE_Z), "Y", [(-0.10, 0.12), (0.0, 0.28), (0.12, 0.24)], max(8, seg))
            for i in range(9 if d >= 2 else 0):
                a = math.tau * i / 9
                dv = Vector((math.cos(a), 0.0, math.sin(a)))
                base = Vector((x, S.COWL_FRONT - 0.20, S.NACELLE_Z))
                b.strut(base + dv * 0.24, base + dv * 0.56, 0.13, 0.13)
            b.lathe((x, S.COWL_FRONT, S.NACELLE_Z), "Y", [(-0.06, S.COWL_R - 0.12), (0.0, S.COWL_R - 0.04)], max(8, seg))
    # Tailplane and the fixed parts of the twin fins.
    n = max(4, cfg["foil"] - 2)
    rings = []
    for side in (-1, 1):
        for span, le, hinge, te in (S.TAILPLANE if side > 0 else list(reversed(S.TAILPLANE))):
            rings.append(P.section(n, le, te, S.TAIL_Z, 0.09, 0.0, (le - hinge) / (le - te), camber=0.0, pos=side * span))
    b.loft(rings)
    for side in (-1, 1):
        fin = []
        for z, le in S.FIN:
            te = S.HINGE_RUDDER - 0.30
            fin.append(vertical_section(n, side * S.FIN_X, z, le, te, 0.08, 0.0, (le - S.HINGE_RUDDER) / (le - te)))
        b.loft(fin)
    # Pilot's canopy on top of the fuselage, offset to the left, and the gun positions.
    cx, fy, ry, z0, z1, hw = S.COCKPIT
    if d >= 1:
        b.loft([[(cx + p[0], p[1], p[2]) for p in P.superellipse(y, top, z0, w, 8, p=2.2)] for y, top, w in
                ((fy + 0.10, z0 + 0.02, 0.10), (fy - 0.25, z1, hw), (ry + 0.30, z1, hw), (ry - 0.15, z0 + 0.05, 0.12))])
        dx, dy, dz = S.DORSAL
        b.lathe((dx, dy, dz - 0.05), "Z", [(0.0, 0.36), (0.06, 0.32)], max(8, seg))
        vx, vy, vz = S.VENTRAL
        b.box((vx, vy + 0.35, vz + 0.05), (0.80, 0.90, 0.20))
    if d >= 2:
        # Radio mast, landing light and wing root fillets.
        b.strut((0.0, 1.80, 1.00), (0.0, 1.70, 1.55), 0.04, 0.04)
        for side in (-1, 1):
            b.lathe((side * 6.0, 0.95, -0.36), "Y", [(-0.05, 0.08), (0.0, 0.10)], 8)
    return b.finish("Chassis", mat)


def build_controls(cfg, mat, chassis):
    build_aileron(cfg, mat, chassis, 1, "Aileron_D")
    build_aileron(cfg, mat, chassis, -1, "Aileron_G")
    n = max(4, cfg["foil"] // 2)
    for side, name in ((1, "Elevator_D"), (-1, "Elevator_G")):
        rings = [P.section(n, le, te, S.TAIL_Z, 0.09, min((le - hinge) / (le - te), 0.995), 1.0, camber=0.0, pos=side * span)
                 for span, le, hinge, te in S.TAILPLANE]
        b = Builder()
        b.loft(rings)
        b.finish(name, mat, (side * 1.6, S.TAILPLANE[0][2], S.TAIL_Z), chassis, sharp=50)
    # Both rudders in one mesh, as the game's twin-engine bombers have a single Rudder node.
    b = Builder()
    for side in (-1, 1):
        b.loft([vertical_section(n, side * S.FIN_X, z, S.HINGE_RUDDER + 0.02, te, 0.09, 0.0, 1.0) for z, te in S.RUDDER])
    b.finish("Rudder", mat, (0.0, S.HINGE_RUDDER, 0.45), chassis, sharp=50)


def build_engines(cfg, mat, chassis):
    seg = max(8, cfg["seg"])
    stations = 3 if cfg["detail"] == 0 else (5 if cfg["detail"] == 1 else 8)
    for number, side in ((1, -1), (2, 1)):
        hub = Vector((side * S.NACELLE_X, S.PROP_Y, S.NACELLE_Z))
        b = Builder()
        b.lathe(hub, "Y", [(-0.25, S.SPINNER_R), (0.0, S.SPINNER_R), (0.25, S.SPINNER_R * 0.6), (0.40, 0.02)], seg)
        moteur = b.finish("Bloc_Moteur_%d" % number, mat, hub, chassis, sharp=60)
        b = Builder()
        for k in range(3):
            phi = math.tau * k / 3
            rings = []
            for i in range(stations):
                r = 0.20 + (S.PROP_R - 0.20) * i / (stations - 1)
                t = i / (stations - 1)
                chord = 0.26 * (1 - t) + 0.20 * t if t < 0.85 else 0.20 - (t - 0.85) / 0.15 * 0.12
                thick = 0.06 * (1 - t) + 0.014 * t
                pitch = math.radians(40 - 25 * t)
                radial = Vector((math.cos(phi), 0.0, math.sin(phi)))
                tangent = Vector((-math.sin(phi), 0.0, math.cos(phi)))
                u = tangent * math.cos(pitch) + Vector((0, -1, 0)) * math.sin(pitch)
                v = tangent * -math.sin(pitch) + Vector((0, -1, 0)) * -math.cos(pitch)
                c = hub + radial * r
                rings.append([tuple(c + u * chord * 0.5), tuple(c + v * thick * 0.5), tuple(c - u * chord * 0.5),
                              tuple(c - v * thick * 0.5)])
            b.loft(rings)
        b.finish("Helice_LS_%d" % number, mat, hub, moteur, sharp=50)


def gun(cfg, mat, chassis, number, pivot, muzzle_y):
    pivot = Vector(pivot)
    sign = 1 if muzzle_y > pivot.y else -1
    b = Builder()
    b.lathe(pivot, "Z", [(-0.06, 0.06), (0.0, 0.05)], 6)
    tourelle = b.finish("Tourelle_%02d" % number, mat, pivot, chassis)
    b = Builder()
    b.box((pivot.x, pivot.y - sign * 0.05, pivot.z + 0.06), (0.07, 0.40, 0.10))
    if cfg["detail"]:
        b.lathe((pivot.x, pivot.y, pivot.z + 0.17), "X", [(-0.03, 0.09), (0.03, 0.09)], 8)
    axe = b.finish("Axe_Canon_%02d" % number, mat, pivot, tourelle)
    b = Builder()
    start = pivot.y + sign * 0.15
    b.lathe((pivot.x, start, pivot.z + 0.06), "Y", sorted([(0.0, 0.022), (muzzle_y - start, 0.014)]), 6 if cfg["detail"] else 4)
    canon = b.finish("Canon_%02d" % number, mat, pivot, axe)
    helper("Fx_tourelle%d_tir_01" % number, (pivot.x, muzzle_y + sign * 0.01, pivot.z + 0.06), canon)


def build(name, cfg):
    P.new_scene("%s_%s" % (S.STEM, name))
    main = T.material_main()
    chassis = build_chassis(cfg, main)
    build_controls(cfg, main, chassis)
    build_engines(cfg, main, chassis)
    gun(cfg, main, chassis, 1, S.NOSE_GUN, S.NOSE_MUZZLE_Y)
    gun(cfg, main, chassis, 2, S.DORSAL, S.DORSAL_MUZZLE_Y)
    gun(cfg, main, chassis, 3, S.VENTRAL, S.VENTRAL_MUZZLE_Y)
    for hname, pos in (("Pilot", S.PILOT), ("Pilot2", S.PILOT2), ("Pilot3", S.PILOT3),
                       ("FX_Vortex_D", S.VORTEX), ("FX_Vortex_G", (-S.VORTEX[0], S.VORTEX[1], S.VORTEX[2])),
                       ("Fx_Stress_01", (0.4, -2.5, 0.4)), ("Fx_Stress_02", (S.NACELLE_X, 2.0, S.NACELLE_Z))):
        helper(hname, pos, chassis)
    for i, pos in enumerate(S.BOMBS):
        helper("AS_%d_%d" % (i // 2 + 1, i % 2 + 1), pos, chassis)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap(meshes)
    P.report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


def build_train():
    """Retractable gear file, as Ju_88_S_train: Train (legs), Roue_Avant, Roue_Arriere."""
    P.new_scene("%s_train" % S.STEM)
    main = T.material_main()
    b = Builder()
    for side in (-1, 1):
        nx = side * S.NACELLE_X
        for x in S.WHEEL_X:
            pass
        for dx in (-0.14, 0.14):
            b.strut((nx + dx, S.WHEEL_Y + 0.10, S.NACELLE_Z - 0.40), (nx + dx, S.WHEEL_Y, S.WHEEL_Z + 0.05), 0.09, 0.09)
        b.strut((nx, S.WHEEL_Y - 0.55, S.NACELLE_Z - 0.35), (nx, S.WHEEL_Y, S.WHEEL_Z + 0.30), 0.06, 0.06)
        b.lathe((nx, S.WHEEL_Y, S.WHEEL_Z), "X", [(-0.30, 0.04), (0.30, 0.04)], 6)
    tx, ty, tz, tr = S.TAIL_WHEEL
    b.strut((tx, ty + 0.30, tz + 0.55), (tx, ty, tz), 0.06, 0.06)
    train = b.finish("Train", main, (0.0, S.WHEEL_Y, S.NACELLE_Z - 0.4), None)
    b = Builder()
    for side in (-1, 1):
        for x in S.WHEEL_X:
            c = (side * x, S.WHEEL_Y, S.WHEEL_Z)
            r, w = S.WHEEL_R, S.WHEEL_W
            b.lathe(c, "X", [(-w / 2, r * 0.5), (-w * 0.45, r * 0.92), (0.0, r), (w * 0.45, r * 0.92), (w / 2, r * 0.5)], 16)
    b.finish("Roue_Avant", main, (0.0, S.WHEEL_Y, S.WHEEL_Z), train, sharp=60)
    b = Builder()
    b.lathe((tx, ty, tz), "X", [(-0.05, tr * 0.5), (-0.045, tr), (0.045, tr), (0.05, tr * 0.5)], 12)
    b.finish("Roue_Arriere", main, (tx, ty, tz), train, sharp=60)
    helper("Train_Avant", S.TRAIN_AVANT, None)
    helper("Train_Arriere", S.TRAIN_ARRIERE, None)
    T.unwrap([o for o in bpy.context.scene.objects if o.type == "MESH"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_train.blend" % S.STEM))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        P.render_clay()
    build_train()
    print("BUILD_DONE")
