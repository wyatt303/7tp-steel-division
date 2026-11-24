"""Build the wz. 28 half-track armoured car in High, Mid and Low versions.

  set AC_VARIANT=ckm   or   set AC_VARIANT=37
  blender --background --factory-startup --python build_wz28.py -- <output_dir>

Layout follows the game's half-tracks (SdKfz 250): a tank-style track system (Chenille_*,
Roue_D1-6 / Roue_G1-6 under Roue_Elev helpers, Fake) plus steered front wheels
Roue_Droite_01 / Roue_Gauche_01 without a parent. Track wheels: 1 front drum, 2-5 road
wheels, 6 rear drive wheel. The shared track code comes from build_tk.py.
"""

import math
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_wz28"
import spec_wz28 as S  # noqa: E402
import build_tk as T  # noqa: E402
import build_wz34 as W  # noqa: E402
import spec_wz34  # noqa: E402

T.S = S
W.S = S
Builder, helper, place = T.Builder, T.helper, T.place
OUT = T.OUT

LODS = {
    "Low": {"wheels": False, "detail": 0, "seg": 8, "track": 12, "limit": 700},
    "Mid": {"wheels": True, "detail": 1, "seg": 8, "track": 30, "limit": 2000},
    "High": {"wheels": True, "detail": 2, "seg": 20, "track": 70, "limit": 12000},
}


def bonnet_ring(y, bottom, top, half):
    return [(half, y, bottom), (half, y, top), (0.0, y, top + S.RIDGE), (-half, y, top), (-half, y, bottom)]


def build_chassis(cfg, mat):
    detail = cfg["detail"]
    b = Builder()
    b.loft([bonnet_ring(*r) for r in S.BONNET])
    b.loft([S.body_ring(*r) for r in S.BODY])
    # Lower hull between the tracks.
    b.box((0.0, -0.78, (S.DECK_Z + 0.28) / 2), (0.86, 1.70, S.DECK_Z - 0.28))
    for x, y0, y1, z0, z1 in S.LOCKERS:
        for side in (-1, 1):
            b.box((side * x, (y0 + y1) / 2, (z0 + z1) / 2), (0.10, y1 - y0, z1 - z0))

    if detail >= 1:
        # Front axle with leaf springs and the radiator door.
        b.lathe((0.0, S.FRONT_AXLE_Y, S.WHEEL_Z - 0.03), "X", [(-0.58, 0.03), (0.58, 0.03)], 6)
        for side in (-1, 1):
            x = side * 0.27
            y = S.FRONT_AXLE_Y
            b.prism([(y + 0.30, 0.47), (y, 0.40), (y - 0.30, 0.47), (y - 0.30, 0.50), (y, 0.43), (y + 0.30, 0.50)],
                    x - 0.03, x + 0.03)
        b.box((0.0, 1.325, 0.86), (0.48, 0.016, 0.40))
        # Track unit: frame between the drums, springs and the drive shaft housing.
        for side in (-1, 1):
            x = side * (S.TRACK_X - 0.02)
            fy, fz, _ = S.FRONT_DRUM
            ry, rz, _ = S.REAR_DRIVE
            b.strut((x, fy, fz), (x, ry, rz), 0.035, 0.06)
            b.strut((side * 0.43, -1.41, rz), (x, ry, rz), 0.07, 0.07)
            b.box((x, -0.80, 0.24), (0.04, 0.50, 0.07))
            if detail >= 2:
                for y in (-0.62, -1.02):
                    b.lathe((x, y, 0.30), "Z", [(0.0, 0.03), (0.10, 0.03)], 6)
                b.box((x, -0.82, 0.36), (0.05, 0.30, 0.05))
        tx, ty, tz = S.TOW_HOOK
        b.box((tx, ty + 0.06, tz), (0.10, 0.12, 0.06))
        b.lathe((tx, ty, tz), "X", [(-0.02, 0.045), (0.02, 0.045)], 8)
        # Roof hatches on the compartment and vision flaps.
        for side in (-1, 1):
            b.box((side * (S.BODY_HALF + 0.006), -0.55, 1.30), (0.012, 0.26, 0.22))

    if detail >= 2:
        for side in (-1, 1):
            # Bonnet louvres and side access panel.
            for k in range(3):
                y = 0.90 - k * 0.07
                half = 0.335 + (0.36 - 0.335) * (0.98 - y) / 0.18
                b.box((side * (half + 0.004), y, 1.00), (0.01, 0.045, 0.17))
            b.box((side * (0.40 + 0.006), 0.25, 0.80), (0.01, 0.42, 0.30))
            # Compartment door hinges and handle.
            xc = side * (S.BODY_HALF + 0.006)
            for z in (0.75, 1.30):
                b.box((xc, -0.82, z), (0.014, 0.05, 0.05))
            b.box((xc + side * 0.008, -1.10, 1.00), (0.012, 0.02, 0.10))
            # Locker lids and hasps.
            for lx, y0, y1, z0, z1 in S.LOCKERS:
                b.box((side * (lx + 0.052), (y0 + y1) / 2, z1 - 0.06), (0.008, y1 - y0 - 0.04, 0.03))
        # Radiator door hinges, starting handle, front lamp brackets.
        for z in (0.72, 1.00):
            b.box((0.0, 1.335, z), (0.04, 0.012, 0.04))
        b.strut((0.0, 1.33, 0.55), (0.0, 1.42, 0.50), 0.025)
        b.strut((0.0, 1.42, 0.50), (0.06, 1.46, 0.50), 0.025)
        for side in (-1, 1):
            b.lathe((side * 0.20, 1.34, 1.18), "Y", [(-0.04, 0.045), (0.04, 0.06), (0.05, 0.05)], 8)
        # Rear door in the sloped rear plate.
        b.box((0.0, -1.62, 0.95), (0.42, 0.02, 0.48))
        # Muffler under the left side of the bonnet.
        mx, my, mz = S.MUFFLER
        b.lathe((mx, my, mz), "Y", [(-0.22, 0.04), (-0.20, 0.06), (0.20, 0.06), (0.22, 0.04)], 8)
    return b.finish("Chassis", mat)


def build_turret(cfg, mat, chassis):
    detail = cfg["detail"]
    cx = S.TURRET_C[0]
    b = Builder()
    rings = S.TURRET_RINGS if detail >= 1 else [S.TURRET_RINGS[0], S.TURRET_RINGS[-1]]
    b.loft([S.chamfer_ring(cx, cy, z, hl, hw, c) for z, cy, hl, hw, c in rings])
    ux, uy = S.CUPOLA_C
    b.loft([spec_wz34.hexagon(ux, uy, z, r) for z, r in S.CUPOLA])
    top = S.CUPOLA[-1][0]
    r = S.CUPOLA[-1][1]
    if detail >= 1:
        for side in (-1, 1):
            b.box((ux + side * r * 0.42, uy, top + 0.012), (r * 0.80, r * 1.55, 0.02))
    if detail >= 2:
        z, cy, hl, hw, c = S.TURRET_RINGS[1]
        for side in (-1, 1):
            b.box((cx + side * (hw - 0.05), cy - 0.05, z + 0.17), (0.03, 0.26, 0.15))
            b.box((cx + side * (hw - 0.035), cy + 0.12, z + 0.25), (0.02, 0.12, 0.012))
    turret = b.finish("Tourelle_01", mat, S.TURRET_C, chassis)

    mount = Vector(S.MOUNT)
    seg = max(6, cfg["seg"] // 2)
    b = Builder()
    if S.MANTLET == "ball":
        if detail >= 1:
            b.lathe(mount, "Y", [(-0.07, 0.07), (-0.04, 0.10), (0.0, 0.11), (0.04, 0.10), (0.07, 0.06)], seg + 2)
        else:
            b.lathe(mount, "Y", [(-0.05, 0.10), (0.06, 0.07)], 6)
    else:
        b.box((mount.x, mount.y - 0.02, mount.z), (0.26, 0.10, 0.24))
        if detail >= 1:
            b.box((mount.x, mount.y + 0.04, mount.z), (0.20, 0.04, 0.18))
            b.lathe((mount.x, mount.y, mount.z - 0.075), "Y", [(0.04, 0.03), (0.30, 0.03), (0.31, 0.022)], seg)
    axis = b.finish("Axe_Canon_01", mat, mount, turret)

    b = Builder()
    length = S.MUZZLE_Y - mount.y
    if S.VARIANT == "ckm":
        if detail >= 2:
            profile = [(0.06, 0.032), (0.10, 0.032), (0.11, 0.026), (0.13, 0.032), (0.16, 0.026), (0.18, 0.032),
                       (0.21, 0.026), (0.23, 0.032), (0.26, 0.032), (0.27, 0.015), (length - 0.09, 0.013),
                       (length - 0.085, 0.021), (length - 0.05, 0.021), (length - 0.045, 0.013), (length, 0.013)]
        elif detail == 1:
            profile = [(0.06, 0.03), (0.26, 0.03), (0.27, 0.015), (length, 0.013)]
        else:
            profile = [(0.06, 0.026), (length, 0.014)]
    else:
        if detail >= 2:
            profile = [(0.05, 0.05), (0.14, 0.05), (0.15, 0.042), (length - 0.05, 0.040), (length - 0.045, 0.048),
                       (length, 0.048)]
        elif detail == 1:
            profile = [(0.05, 0.05), (0.14, 0.05), (0.15, 0.04), (length, 0.042)]
        else:
            profile = [(0.05, 0.045), (length, 0.04)]
    b.lathe(mount, "Y", profile, max(6, seg))
    canon = b.finish("Canon_01", mat, mount, axis)
    helper("Fx_tourelle1_tir_01", (mount.x, S.MUZZLE_Y + 0.01, mount.z), canon)
    return turret


def track_wheel(b, center, kind, cfg):
    seg = cfg["seg"]
    high = cfg["detail"] >= 2
    outer = 1 if center[0] > 0 else -1
    if kind == "front":
        r = S.FRONT_DRUM[2]
        b.lathe(center, "X", [(-0.07, r * 0.9), (-0.06, r), (0.06, r), (0.07, r * 0.9)], seg)
        if high:
            face = (center[0] + outer * 0.07, center[1], center[2])
            b.lathe(face, "X", [(0.0, r * 0.85), (outer * 0.012, r * 0.80), (outer * 0.015, 0.07)], 12)
            b.lathe(face, "X", [(outer * 0.015, 0.06), (outer * 0.045, 0.04)], 8)
    elif kind == "drive":
        r = S.REAR_DRIVE[2]
        if high:
            b.wheel_ring(center, r, r * 0.78, 0.13, teeth=0, seg=20)
            b.lathe(center, "X", [(-0.06, 0.05), (0.06, 0.05)], 8)
            for i in range(8):
                a = math.tau * (i + 0.5) / 8
                p = Vector(center) + Vector((outer * 0.02, math.cos(a) * r * 0.55, math.sin(a) * r * 0.55))
                b.lathe(p, "X", [(-0.02, 0.035), (0.02, 0.035)], 6)
            for i in range(6):
                a = math.tau * i / 6
                d = Vector((0, math.cos(a), math.sin(a)))
                b.strut(Vector(center) + d * 0.04, Vector(center) + d * (r * 0.78 + 0.004), 0.03, 0.02)
        else:
            b.lathe(center, "X", [(-0.065, r), (0.065, r)], seg)
    else:
        r = S.ROAD_R
        if high:
            b.lathe(center, "X", [(-0.07, r * 0.6), (-0.065, r), (0.065, r), (0.07, r * 0.6)], 12)
            b.lathe((center[0] + outer * 0.07, center[1], center[2]), "X", [(0.0, 0.04), (outer * 0.015, 0.03)], 6)
        else:
            b.lathe(center, "X", [(-0.07, r), (0.07, r)], max(6, seg - 2))


def build_track_wheels(cfg, mat, chassis):
    kinds = ["front"] + ["road"] * len(S.ROAD_Y) + ["drive"]
    for side, letter in ((1, "D"), (-1, "G")):
        for number, (kind, wheel) in enumerate(zip(kinds, S.WHEELS), 1):
            center = Vector((side * S.TRACK_X, wheel[0], wheel[1]))
            elev = helper("Roue_Elev_%s%d" % (letter, number), center, chassis, 0.04)
            b = Builder()
            track_wheel(b, center, kind, cfg)
            b.finish("Roue_%s%d" % (letter, number), mat, center, elev, sharp=60)


def build_front_wheels(cfg, mat):
    for name, side in (("Roue_Droite_01", 1), ("Roue_Gauche_01", -1)):
        center = Vector((side * S.FRONT_X, S.FRONT_AXLE_Y, S.WHEEL_Z))
        b = Builder()
        W.tyre(b, center, S.TYRE_W, cfg["seg"], cfg["detail"], side)
        b.finish(name, mat, center, None, sharp=60)


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
    moving = name == "High"
    mat_d = T.material_track("M_Chenille_D", "chenilledroite") if moving else main
    mat_g = T.material_track("M_Chenille_G", "chenillegauche") if moving else main

    chassis = build_chassis(cfg, main)
    build_turret(cfg, main, chassis)
    build_front_wheels(cfg, main)
    if cfg["wheels"]:
        build_track_wheels(cfg, main, chassis)
    track_d = T.build_track("Chenille_Droite_01", 1, cfg["track"], mat_d, chassis, moving)
    track_g = T.build_track("Chenille_Gauche_01", -1, cfg["track"], mat_g, chassis, moving)

    helper("Fake", (0, -0.8, 0.4), chassis)
    helper("Fx_Stress_01", (0.0, -0.60, S.ROOF_Z + 0.05), chassis)
    helper("Fx_Stress_02", (0.0, 0.70, 1.25), chassis)
    helper("FX_Fumee_Chenille_D1", (S.TRACK_X, -1.60, 0.05), chassis)
    helper("FX_Fumee_Chenille_G1", (-S.TRACK_X, -1.60, 0.05), chassis)
    helper("Remorque_1", S.TOW_HOOK, chassis)
    if cfg["wheels"]:
        T.skin_track(track_d, "D")
        T.skin_track(track_g, "G")

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap([o for o in meshes if not (moving and o.name.startswith("Chenille"))])
    report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        W.render_clay()
    print("BUILD_DONE")
