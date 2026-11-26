"""Build the 37 mm wz. 36 Bofors anti-tank gun in High, Mid and Low versions.

  blender --background --factory-startup --python build_wz36.py -- <output_dir>

Also writes Boites_<stem>.blend with the crew position helpers, as the game's PaK 36 has.
Node layout follows the game's guns; pivots of the animated nodes are the M3 37 mm's, see spec_wz36.py.
"""

import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_wz36"
import spec_wz36 as S  # noqa: E402
import build_tk as T  # noqa: E402
import build_p11 as P  # noqa: E402
import build_wz34 as W  # noqa: E402

S.TYRE_R, S.RIM_R = S.WHEEL_R, 0.23
W.S = S
P.S = S
Builder, helper = T.Builder, T.helper
OUT = T.OUT

LODS = {
    "Low": {"detail": 0, "seg": 6, "limit": 700},
    "Mid": {"detail": 1, "seg": 10, "limit": 1600},
    "High": {"detail": 2, "seg": 18, "limit": 6000},
}


def plate(b, x0, x1, z0, z1, y_at, t=0.012):
    """Flat armour plate between x0 and x1, its front face following y_at(x)."""
    front = [(x0, y_at(x0), z0), (x1, y_at(x1), z0), (x1, y_at(x1), z1), (x0, y_at(x0), z1)]
    back = [(x, y - t, z) for x, y, z in front]
    b.loft([front, back])


def shield_y(x, offset=0.0):
    return S.SHIELD_Y + offset - abs(x) * math.tan(math.radians(8))


def build_chassis(cfg, mat):
    d, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    b.lathe(S.AXLE, "X", [(-S.WHEEL_X + 0.05, 0.035), (S.WHEEL_X - 0.05, 0.035)], max(6, seg // 2))
    if d >= 1:
        for side in (-1, 1):
            b.box((side * 0.30, 0.0, S.WHEEL_R + 0.05), (0.06, 0.40, 0.05))
            b.lathe((side * (S.WHEEL_X - 0.08), 0.0, S.WHEEL_R), "X", [(-0.03, 0.06), (0.03, 0.06)], 8)
        b.box((0.0, -0.10, S.WHEEL_R + 0.02), (0.36, 0.24, 0.10))
    return b.finish("Chassis", mat, S.AXLE, None)


def build_turret(cfg, mat, chassis):
    d, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    # Upper carriage and the shield: two upper halves angled back and the folding lower plates.
    b.box((0.0, -0.08, 0.47), (0.30, 0.46, 0.12))
    for side in (-1, 1):
        x0, x1 = side * 0.004, side * S.SHIELD_HALF
        lo, hi = sorted((x0, x1))
        plate(b, lo, hi, S.SHIELD_UPPER[0], S.SHIELD_UPPER[1], shield_y)
        plate(b, lo, hi, S.SHIELD_LOWER[0], S.SHIELD_LOWER[1], lambda x: shield_y(x, 0.03))
    if d >= 1:
        for side in (-1, 1):
            b.strut((side * 0.12, -0.05, 0.50), (side * 0.40, shield_y(0.40) - 0.02, 0.70), 0.03)
            # Hinges between the upper and lower plates.
            b.lathe((side * 0.30, shield_y(0.30) + 0.01, S.SHIELD_UPPER[0] - 0.005), "X", [(-0.04, 0.012), (0.04, 0.012)], 6)
        # Sight hole frame on the right half.
        b.box((S.SIGHT_HOLE_X, shield_y(S.SIGHT_HOLE_X) + 0.004, 0.86), (0.07, 0.012, 0.12))
    return b.finish("Tourelle_01", mat, S.TURRET, chassis)


def build_gun(cfg, mat, turret):
    d, seg = cfg["detail"], cfg["seg"]
    z = S.FIRE_Z
    b = Builder()
    # Cradle with the recoil cylinder under the barrel, breech ring and block, elevation and
    # traverse handwheels on the left, sight on the right.
    b.lathe((0.0, 0.0, z - 0.065), "Y", [(S.BREECH_Y + 0.10, 0.045), (0.42, 0.040)], max(6, seg // 2))
    b.box((0.0, S.BREECH_Y - 0.06, z), (0.15, 0.22, 0.15))
    if d >= 1:
        b.lathe((-0.20, -0.30, z - 0.12), "X", [(-0.01, 0.07), (0.01, 0.07)], 10)
        b.strut((-0.20, -0.30, z - 0.12), (-0.07, -0.20, z - 0.08), 0.02)
        b.lathe((-0.20, -0.48, z - 0.04), "X", [(-0.01, 0.06), (0.01, 0.06)], 10)
        b.lathe((0.13, -0.10, z + 0.09), "Y", [(-0.15, 0.025), (0.10, 0.025), (0.12, 0.032)], 8)
        b.box((0.11, -0.12, z + 0.04), (0.04, 0.06, 0.08))
    axe = b.finish("Axe_Canon_01", mat, S.TRUNNION, turret)
    b = Builder()
    length = S.BARREL
    if d >= 2:
        profile = [(0.0, 0.040), (0.30, 0.038), (0.32, 0.031), (length - 0.30, 0.026), (length, 0.024),
                   (length + 0.002, 0.036), (length + 0.10, 0.036), (length + 0.102, 0.024)]
    elif d == 1:
        profile = [(0.0, 0.038), (0.30, 0.031), (length, 0.024), (length + 0.002, 0.035), (length + 0.10, 0.035)]
    else:
        profile = [(0.0, 0.036), (length + 0.10, 0.028)]
    b.lathe((0.0, S.BREECH_Y, z), "Y", profile, max(6, seg - 2))
    canon = b.finish("Canon_01", mat, (0.0, S.BREECH_Y, z), axe)
    helper("Fx_tourelle1_tir_01", (0.0, S.MUZZLE_Y + 0.01, z), canon)


def trail_end(side):
    hx, hy, hz = S.TRAIL_HINGE
    a = math.radians(S.TRAIL_SPREAD)
    return Vector((side * (hx + S.TRAIL_LEN * math.sin(a)), hy - S.TRAIL_LEN * math.cos(a), 0.06))


def build_trails(cfg, mat, chassis):
    d = cfg["detail"]
    hx, hy, hz = S.TRAIL_HINGE
    for side, name in ((1, "Bras_Droit"), (-1, "Bras_Gauche")):
        hinge = Vector((side * hx, hy, hz))
        end = trail_end(side)
        b = Builder()
        b.strut(hinge, end, 0.07, 0.08)
        direction = (end - hinge).normalized()
        # Spade and the broad trail plate near the end, as on the museum guns.
        plate_c = end - direction * 0.25
        b.box((plate_c.x, plate_c.y, 0.11), (0.34, 0.36, 0.02))
        if d >= 1:
            b.prism([(end.y + 0.02, 0.02), (end.y - 0.10, 0.02), (end.y - 0.08, 0.14), (end.y + 0.02, 0.12)],
                    end.x - 0.14, end.x + 0.14)
            b.strut(end + Vector((0, 0.10, 0.08)), end + Vector((side * 0.10, 0.25, 0.20)), 0.02)
        if side > 0:
            b.lathe(tuple(end + Vector((0, -0.06, 0.06))), "X", [(-0.01, 0.05), (0.01, 0.05)], 8)
        trail = b.finish(name, mat, hinge, chassis, sharp=50)
        if side > 0:
            helper("Remorque_2", tuple(end + Vector((0, -0.06, 0.06))), trail)


def build_wheels(cfg, mat, chassis):
    for name, side in (("Roue_D1", 1), ("Roue_G1", -1)):
        center = Vector((side * S.WHEEL_X, 0.0, S.WHEEL_R))
        b = Builder()
        W.tyre(b, center, S.WHEEL_W, cfg["seg"] + 2, cfg["detail"], side)
        b.finish(name, mat, center, chassis, sharp=60)


def fit_to_m3():
    """Move the gun forward by SHIFT_Y and put the animated nodes' pivots where the M3 37 mm
    has them (spec_wz36.PIVOTS), leaving every vertex where it is."""
    scene = bpy.context.scene
    for obj in scene.objects:
        if obj.parent is None:
            obj.location.y += S.SHIFT_Y
    bpy.context.view_layer.update()
    world = {obj.name: obj.matrix_world.copy() for obj in scene.objects}
    for name, (gx, gy, gz) in S.PIVOTS.items():
        obj = bpy.data.objects[name]
        old = world[name].translation.copy()
        new = Vector((-gy / 203.0, gx / 203.0, gz / 203.0))  # game (X fwd, Y left) -> Blender (Y fwd, X right)
        obj.data.transform(Matrix.Translation(old - new))
        world[name] = Matrix.Translation(new)
    # Parents first, so every object gets back its own place in the world.
    def depth(obj):
        return 0 if obj.parent is None else 1 + depth(obj.parent)
    for obj in sorted(scene.objects, key=depth):
        obj.matrix_world = world[obj.name]
        bpy.context.view_layer.update()


def build(name, cfg):
    P.new_scene("%s_%s" % (S.STEM, name))
    main = T.material_main()
    chassis = build_chassis(cfg, main)
    turret = build_turret(cfg, main, chassis)
    build_gun(cfg, main, turret)
    build_trails(cfg, main, chassis)
    build_wheels(cfg, main, chassis)
    helper("Fx_Stress_01", S.FX_STRESS[0], chassis)  # the M3 has only this one; no Fx_Stress_02
    helper("FX_Fumee_Roue_D1", (S.WHEEL_X, 0.0, 0.0), None)
    helper("FX_Fumee_Roue_G1", (-S.WHEEL_X, 0.0, 0.0), None)
    fit_to_m3()
    # The M3's animation files are played on this model: export the nodes in the M3's order
    # (read by the add-on's exporter).
    bpy.context.scene["eug_node_order"] = ",".join(S.NODE_ORDER)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap(meshes)
    P.report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


def build_crew():
    """Boites_<stem>: crew positions only, as Boites_PaK_36."""
    P.new_scene("Boites_%s" % S.STEM)
    for name, pos in S.CREW.items():
        helper(name, pos, None)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Boites_%s.blend" % S.STEM))


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        W.render_clay()
    build_crew()
    print("BUILD_DONE")
