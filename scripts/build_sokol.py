"""Build the Sokół 1000 with sidecar and rkm wz. 28 in High, Mid and Low versions.

  blender --background --factory-startup --python build_sokol.py -- <output_dir>

Node layout copied from the game's BMW R75, see spec_sokol.py.
"""

import math
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_sokol"
import spec_sokol as S  # noqa: E402
import build_tk as T  # noqa: E402

Builder, helper, place = T.Builder, T.helper, T.place
OUT = T.OUT

LODS = {
    "Low": {"detail": 0, "seg": 5, "limit": 900},
    "Mid": {"detail": 1, "seg": 10, "limit": 2800},
    "High": {"detail": 2, "seg": 18, "limit": 12000},
}
BX = S.BIKE_X


def tube(b, a, c, r=0.022):
    b.strut(a, c, r * 2, r * 2)


def arc_strip(b, cy, cz, r, a0, a1, x0, x1, steps, thick=0.01):
    outer, inner = [], []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        outer.append((cy + r * math.cos(a), cz + r * math.sin(a)))
        inner.append((cy + (r - thick) * math.cos(a), cz + (r - thick) * math.sin(a)))
    b.prism(outer + inner[::-1], x0, x1)


def rounded_section(y, half, bottom, top, n):
    cz, hz = (top + bottom) / 2, (top - bottom) / 2
    pts = []
    for i in range(n):
        a = math.tau * i / n
        c, s = math.cos(a), math.sin(a)
        pts.append((S.SIDE_X + half * math.copysign(abs(c) ** 0.6, c), y, cz + hz * math.copysign(abs(s) ** 0.6, s)))
    return pts


def build_chassis(cfg, mat):
    d, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    # Frame after the blueprint: steering head, top tube, cradle under the engine, seat
    # tube and rear stays to the rear axle.
    hy, hz = S.STEER_HEAD[1], S.STEER_HEAD[2]
    tube(b, (BX, hy + 0.03, hz + 0.05), (BX, hy - 0.04, hz - 0.13), 0.03)
    tube(b, (BX, hy - 0.01, hz - 0.03), (BX, -0.16, 0.69))
    for side in ((-1, 1) if d else (1,)):
        x = BX + side * 0.06
        tube(b, (BX, hy - 0.04, hz - 0.12), (x, 0.26, 0.17))
        tube(b, (x, 0.26, 0.17), (x, -0.22, 0.15))
        tube(b, (x, -0.22, 0.15), (BX, -0.17, 0.70))
        tube(b, (x, -0.22, 0.15), (BX + side * 0.08, S.REAR_Y, S.WHEEL_R))
        if d:
            tube(b, (BX, -0.17, 0.68), (BX + side * 0.08, S.REAR_Y, S.WHEEL_R))
    # V-twin engine: crankcase, two finned cylinders at 45 degrees, gearbox, chain case.
    b.lathe((BX, 0.05, 0.29), "X", [(-0.09, 0.13), (0.09, 0.13)], max(8, seg))
    for start, end in (((BX, 0.10, 0.37), (BX, 0.24, 0.58)), ((BX, -0.01, 0.37), (BX, -0.14, 0.58))):
        b.strut(start, end, 0.11, 0.11)
        if d >= 1:
            fins = 5 if d >= 2 else 2
            for k in range(fins):
                t = 0.25 + 0.7 * k / max(1, fins - 1)
                p = Vector(start).lerp(Vector(end), t)
                q = p + (Vector(end) - Vector(start)).normalized() * 0.012
                b.strut(p, q, 0.15, 0.15)
    b.box((BX, -0.24, 0.30), (0.14, 0.18, 0.18))
    if d:
        b.prism([(0.02, 0.36), (-0.20, 0.36), (-0.36, 0.30), (-0.20, 0.22), (0.02, 0.24)], BX + 0.07, BX + 0.10)
    # Teardrop tank on the top tube and the sprung saddle.
    tank = [(0.37, 0.67, 0.82, 0.07), (0.30, 0.63, 0.84, 0.14), (0.10, 0.61, 0.85, 0.16), (-0.10, 0.62, 0.81, 0.14),
            (-0.20, 0.65, 0.75, 0.07)]
    n = 8 if d else 4
    b.loft([[(BX + h * math.cos(math.tau * i / n), y, (lo + hi) / 2 + (hi - lo) / 2 * math.sin(math.tau * i / n))
             for i in range(n)] for y, lo, hi, h in tank])
    b.prism([(-0.08, 0.76), (-0.14, 0.79), (-0.31, 0.80), (-0.38, 0.76), (-0.30, 0.73), (-0.12, 0.74)], BX - 0.14, BX + 0.14)
    if d >= 1:
        for side in (-1, 1):
            b.strut((BX + side * 0.08, -0.33, 0.74), (BX + side * 0.08, -0.36, 0.62), 0.03)
    # Rear mudguard, the tall carrier over it and the saddlebags.
    arc_strip(b, S.REAR_Y, S.WHEEL_R, S.WHEEL_R + 0.06, 0, 175, BX - 0.07, BX + 0.07, 4 + 2 * d)
    b.box((BX, -0.85, 0.84), (0.24, 0.62, 0.02))
    if d:
        for side in (-1, 1):
            tube(b, (BX + side * 0.12, -0.55, 0.84), (BX + side * 0.10, -0.62, 0.45), 0.012)
            tube(b, (BX + side * 0.12, -1.14, 0.84), (BX + side * 0.10, -1.05, 0.45), 0.012)
        tube(b, (BX, -0.52, 0.84), (BX, -0.48, 0.96), 0.012)
    for side in (-1, 1):
        b.box((BX + side * 0.17, -0.85, 0.58), (0.10, 0.30, 0.26))
    if d:
        # Carburettor air filter on the left and the tool box on the right.
        b.lathe((BX - 0.13, 0.09, 0.50), "X", [(-0.03, 0.08), (0.02, 0.08)], max(8, seg))
        b.box((BX + 0.12, -0.32, 0.46), (0.10, 0.16, 0.14))
    # Footboards, and the long exhaust pipe on the right to a muffler under the carrier.
    for side in (-1, 1):
        b.box((BX + side * 0.20, 0.38, 0.17), (0.12, 0.20, 0.02))
    mx, my, mz = S.MUFFLER
    if d:
        tube(b, (BX + 0.05, 0.22, 0.52), (mx, 0.30, 0.16), 0.022)
        tube(b, (BX + 0.05, -0.12, 0.52), (mx, 0.00, 0.16), 0.022)
    tube(b, (mx, 0.30, 0.16), (mx, my + 0.20, mz), 0.025)
    b.lathe((mx, my, mz), "Y", [(-0.25, 0.04), (0.15, 0.05), (0.20, 0.03)], max(6, seg // 2))

    # Sidecar: chassis tubes, boat body, mudguard, seat back and gun pintle.
    n = {0: 6, 1: 10, 2: 14}[d]
    b.loft([rounded_section(y, h, lo, hi, n) for y, h, lo, hi in S.SIDECAR])
    for y in (0.30, -0.50):
        tube(b, (BX + 0.08, y, 0.26), (S.SIDE_X - 0.15, y, 0.30), 0.022)
    tube(b, (S.SIDE_X + 0.10, S.SIDE_WHEEL_Y + 0.25, 0.30), (S.SIDE_WHEEL_X - 0.04, S.SIDE_WHEEL_Y, S.SIDE_WHEEL_R), 0.025)
    tube(b, (S.SIDE_X + 0.10, S.SIDE_WHEEL_Y - 0.30, 0.30), (S.SIDE_WHEEL_X - 0.04, S.SIDE_WHEEL_Y, S.SIDE_WHEEL_R), 0.025)
    arc_strip(b, S.SIDE_WHEEL_Y, S.SIDE_WHEEL_R, S.SIDE_WHEEL_R + 0.05, 10, 170, S.SIDE_WHEEL_X - 0.07,
              S.SIDE_WHEEL_X + 0.07, 4 + 2 * d)
    y0, y1 = S.SEAT_OPENING
    b.box((S.SIDE_X, y1 - 0.02, 0.90), (0.40, 0.05, 0.22))
    if d >= 1:
        # Coaming round the opening and a windscreen frame in front of it.
        b.box((S.SIDE_X, y0, 0.80), (0.52, 0.03, 0.04))
        for side in (-1, 1):
            b.box((S.SIDE_X + side * 0.26, (y0 + y1) / 2, 0.80), (0.03, y0 - y1, 0.04))
    mx, my, mz = S.MOUNT
    tube(b, (mx, my, 0.70), (mx, my, mz - 0.05), 0.022)
    # Spare wheel lying flat on the rear deck and a can on the sidecar frame (kit drawing).
    sx, sy, sz = S.SPARE
    if d:
        sec = [(-0.04, 0.24), (-0.05, 0.29), (0.0, 0.33), (0.05, 0.29), (0.04, 0.24)]
        b.loft([T.circle("Z", (sx, sy, sz), rr, seg + 2, off) for off, rr in sec], closed=True)
        b.lathe((sx, sy, sz), "Z", [(-0.04, 0.24), (0.0, 0.24)], seg + 2)
        b.lathe((S.SIDE_X + 0.36, 0.05, 0.36), "Y", [(-0.20, 0.07), (0.20, 0.07)], 8)
        # Pillion pad on the carrier.
        b.box((BX, -0.85, 0.87), (0.18, 0.26, 0.05))
    else:
        b.lathe((sx, sy, sz), "Z", [(-0.05, 0.33), (0.05, 0.33)], seg)
    if d >= 2:
        # Tool box on the sidecar tail, license plate and lamp.
        b.box((S.SIDE_X, -0.80, 0.78), (0.26, 0.10, 0.10))
        b.lathe((S.SIDE_X + 0.24, 0.62, 0.66), "Y", [(-0.03, 0.04), (0.02, 0.045)], 8)
        b.box((BX, -1.16, 0.62), (0.18, 0.012, 0.12))
    return b.finish("Chassis", mat)


def build_axis(cfg, mat, chassis):
    d, seg = cfg["detail"], cfg["seg"]
    hy, hz = S.STEER_HEAD[1], S.STEER_HEAD[2]
    b = Builder()
    # Girder fork from the head to the front axle, with links and the front springs.
    for side in (-1, 1):
        x = BX + side * 0.075
        tube(b, (x, hy + 0.06, hz + 0.08), (x, S.FRONT_Y, S.WHEEL_R), 0.018)
        if d:
            tube(b, (x, hy, hz + 0.06), (x, hy + 0.14, 0.40), 0.014)
            b.lathe((BX + side * 0.05, hy + 0.10, hz - 0.05), "Z", [(0.0, 0.025), (0.17, 0.025)], 6)
    b.box((BX, hy + 0.05, hz + 0.08), (0.17, 0.08, 0.04))
    if d:
        b.box((BX, hy + 0.02, hz - 0.06), (0.17, 0.08, 0.04))
    # Wide handlebar swept far back to the grips, as in the blueprint.
    gz, gh, gy = S.HANDLEBAR_Z, S.HANDLEBAR_HALF, S.GRIP_Y
    for side in (-1, 1):
        tube(b, (BX, hy + 0.02, hz + 0.10), (BX + side * gh * 0.55, hy - 0.06, gz + 0.04), 0.014)
        tube(b, (BX + side * gh * 0.55, hy - 0.06, gz + 0.04), (BX + side * gh, gy, gz), 0.014)
        if d:
            b.lathe((BX + side * (gh - 0.05), gy, gz), "X", [(-0.05, 0.02), (0.05, 0.02)], 6)
    # Drum headlamp above the fork springs and the deep front mudguard.
    lx, ly, lz = S.HEADLAMP
    b.lathe((lx, ly, lz), "Y", [(-0.09, 0.07), (0.0, 0.10), (0.04, 0.10), (0.05, 0.09)], max(8, seg))
    arc_strip(b, S.FRONT_Y, S.WHEEL_R, S.WHEEL_R + 0.05, 15, 175, BX - 0.08, BX + 0.08, 4 + 2 * d)
    if d:
        for side in (-1, 1):
            arc_strip(b, S.FRONT_Y, S.WHEEL_R, S.WHEEL_R + 0.05, 25, 165, BX + side * 0.08 - 0.004,
                      BX + side * 0.08 + 0.004, 4 + 2 * d, thick=0.07)
        b.box((BX, S.FRONT_Y + 0.30, 0.66), (0.16, 0.012, 0.10))
    return b.finish("Axis", mat, S.STEER_HEAD, chassis)


def wheel(b, center, r, w, cfg):
    d, seg = cfg["detail"], cfg["seg"]
    if d == 0:
        b.lathe(center, "X", [(-w / 2, r), (w / 2, r)], seg)
        return
    # Tyre and rim as an open ring (closed loft round the cross-section), so the spokes show.
    section = [(-w * 0.30, r * 0.74), (-w / 2, r * 0.82), (-w * 0.45, r * 0.95), (0.0, r), (w * 0.45, r * 0.95),
               (w / 2, r * 0.82), (w * 0.30, r * 0.74)]
    b.loft([T.circle("X", center, rr, seg + 4, off) for off, rr in section], closed=True)
    b.lathe(center, "X", [(-0.02, 0.05), (0.02, 0.05)], 8)
    b.lathe(center, "X", [(-0.035, 0.06), (-0.03, 0.04), (0.03, 0.04), (0.035, 0.06)], 8)
    if d >= 2:
        for i in range(16):
            a = math.tau * i / 16
            side = 0.035 if i % 2 else -0.035
            p = Vector((center[0] + side, center[1], center[2]))
            q = Vector((center[0], center[1] + math.cos(a) * r * 0.78, center[2] + math.sin(a) * r * 0.78))
            b.strut(p + (q - p).normalized() * 0.04, q, 0.006, 0.006)


def build_wheels(cfg, mat):
    for name, center, r in (("Roue_Droite_01", (BX, S.FRONT_Y, S.WHEEL_R), S.WHEEL_R),
                            ("Roue_03", (BX, S.REAR_Y, S.WHEEL_R), S.WHEEL_R),
                            ("Roue_02", (S.SIDE_WHEEL_X, S.SIDE_WHEEL_Y, S.SIDE_WHEEL_R), S.SIDE_WHEEL_R)):
        b = Builder()
        wheel(b, center, r, S.WHEEL_W, cfg)
        b.finish(name, mat, center, None, sharp=60)


def build_gun(cfg, mat, chassis):
    d = cfg["detail"]
    mount = Vector(S.MOUNT)
    b = Builder()
    b.lathe(mount, "Z", [(-0.05, 0.025), (0.0, 0.03)], 6)
    turret = b.finish("Tourelle_01", mat, mount, chassis)
    # Browning wz. 28: receiver, butt, pistol grip, magazine and folded bipod.
    b = Builder()
    b.box((mount.x, mount.y + 0.05, mount.z + 0.04), (0.05, 0.36, 0.08))
    b.prism([(mount.y - 0.13, mount.z + 0.06), (mount.y - 0.13, mount.z + 0.02), (mount.y - 0.50, mount.z - 0.03),
             (mount.y - 0.50, mount.z + 0.07)], mount.x - 0.022, mount.x + 0.022)
    b.box((mount.x, mount.y - 0.06, mount.z - 0.04), (0.03, 0.04, 0.09))
    b.box((mount.x, mount.y + 0.06, mount.z - 0.05), (0.03, 0.09, 0.10))
    if d >= 1:
        b.lathe((mount.x, mount.y + 0.23, mount.z + 0.015), "Y", [(0.0, 0.016), (0.25, 0.016)], 6)
        for side in (-1, 1):
            b.strut((mount.x + side * 0.01, mount.y + 0.45, mount.z + 0.0),
                    (mount.x + side * 0.03, mount.y + 0.10, mount.z - 0.02), 0.01)
    axe = b.finish("Axe_Canon_01", mat, mount, turret)
    b = Builder()
    length = S.MUZZLE_Y - mount.y
    profile = [(0.20, 0.018), (length - 0.07, 0.015), (length - 0.065, 0.022), (length, 0.020)] if d else \
        [(0.20, 0.018), (length, 0.016)]
    b.lathe((mount.x, mount.y, mount.z + 0.045), "Y", profile, 6 if d else 4)
    canon = b.finish("Canon_01", mat, mount, axe)
    helper("Fx_tourelle1_tir_01", (mount.x, S.MUZZLE_Y + 0.01, mount.z + 0.045), canon)
    helper("Roue_Gauche_01", (S.SIDE_X, 0.95, 0.32), canon)


def build_rider(cfg, mat, chassis):
    """Seated rider in a khaki uniform and a wz. 31 helmet, as the Motard mesh of the R75."""
    d = cfg["detail"]
    seg = 6 if d == 0 else (10 if d == 1 else 14)
    b = Builder()
    b.strut((BX, -0.22, 0.80), (BX, -0.10, 1.22), 0.34, 0.22)
    b.box((BX, -0.22, 0.83), (0.32, 0.26, 0.12))
    b.lathe((BX, -0.07, 1.22), "Z", [(0.0, 0.05), (0.06, 0.05)], 6)
    b.lathe((BX, -0.06, 1.26), "Z", [(0.0, 0.07), (0.06, 0.10), (0.13, 0.09), (0.16, 0.04)], seg)
    # wz. 31 helmet: dome with a short brim.
    b.lathe((BX, -0.06, 1.38), "Z", [(0.0, 0.17), (0.02, 0.15), (0.08, 0.14), (0.13, 0.09), (0.15, 0.02)], seg)
    for side in (-1, 1):
        shoulder = (BX + side * 0.19, -0.10, 1.18)
        elbow = (BX + side * 0.30, 0.02, 1.02)
        hand = (BX + side * (S.HANDLEBAR_HALF - 0.05), S.GRIP_Y, S.HANDLEBAR_Z)
        b.strut(shoulder, elbow, 0.09, 0.09)
        b.strut(elbow, hand, 0.08, 0.08)
        hip = (BX + side * 0.11, -0.20, 0.80)
        knee = (BX + side * 0.19, 0.16, 0.70)
        foot = (BX + side * 0.20, 0.36, 0.22)
        b.strut(hip, knee, 0.14, 0.14)
        b.strut(knee, foot, 0.11, 0.11)
        b.box((foot[0], foot[1] + 0.06, 0.20), (0.10, 0.24, 0.07))
    return b.finish("Motard", mat, (BX, -0.215, 0.0), chassis, sharp=50)


def report(name, limit):
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    size = [max(c[i] for c in corners) - min(c[i] for c in corners) for i in range(3)]
    total = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    print("REPORT %s %s tris=%d limit=%d objects=%d width=%.3f length=%.3f height=%.3f" % (
        S.STEM, name, total, limit, len(meshes), size[0], size[1], size[2]))


def build(name, cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_scene_fbx")
    bpy.context.scene.unit_settings.system = "METRIC"
    collection = bpy.data.collections.new("%s_%s" % (S.STEM, name))
    bpy.context.scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
    main = T.material_main()
    chassis = build_chassis(cfg, main)
    build_axis(cfg, main, chassis)
    build_rider(cfg, main, chassis)
    build_gun(cfg, main, chassis)
    build_wheels(cfg, main)
    helper("Tireur", S.TIREUR, chassis)
    helper("Fx_Stress_01", (S.SIDE_X, -0.70, 0.55), chassis)
    helper("Fx_Stress_02", (BX, 0.10, 0.70), chassis)
    helper("FX_Fumee_Roue_D1", (S.SIDE_WHEEL_X, S.SIDE_WHEEL_Y, 0.003), None)
    helper("FX_Fumee_Roue_G1", (BX, S.REAR_Y, 0.003), None)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap(meshes)
    report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        import build_wz34 as W
        W.S = S
        W.render_clay()
    print("BUILD_DONE")
