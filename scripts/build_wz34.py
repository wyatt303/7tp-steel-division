"""Build the wz. 34 armoured car in High, Mid and Low versions.

  set AC_VARIANT=ckm   or   set AC_VARIANT=37
  blender --background --factory-startup --python build_wz34.py -- <output_dir>

Object names follow the game's own armoured cars (SdKfz 221, Humber): Chassis, Tourelle_01,
Axe_Canon_01, Canon_01, front steered wheels Roue_Droite_01 / Roue_Gauche_01 and the whole
rear axle as Roue_02. Wheels have no parent and their pivots sit on the wheel centres.
Wheeled vehicles have no tracks, no Fake and no Roue_Elev helpers.
"""

import math
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TK_SPEC", "spec_wz34")
import spec_wz34 as S  # noqa: E402
from build_tk import Builder, OUT, helper, material_main, place, unwrap  # noqa: E402

LODS = {
    "Low": {"detail": 0, "seg": 8, "limit": 700},
    "Mid": {"detail": 1, "seg": 8, "limit": 2000},
    "High": {"detail": 2, "seg": 24, "limit": 12000},
}


def arc_strip(b, guard, steps, thickness=0.012):
    cy, cz, r, a0, a1, x0, x1 = guard
    outer, inner = [], []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        outer.append((cy + r * math.cos(a), cz + r * math.sin(a)))
        inner.append((cy + (r - thickness) * math.cos(a), cz + (r - thickness) * math.sin(a)))
    b.prism(outer + inner[::-1], x0, x1)


def rect_ring(z, front, rear, half):
    return [(half, front, z), (-half, front, z), (-half, rear, z), (half, rear, z)]


def tyre(b, center, width, seg, detail, outer_side):
    r, rim = S.TYRE_R, S.RIM_R
    w = width / 2
    if detail >= 1:
        b.lathe(center, "X", [(-w, rim * 1.02), (-w * 0.98, r * 0.86), (-w * 0.72, r), (w * 0.72, r),
                              (w * 0.98, r * 0.86), (w, rim * 1.02)], seg)
    else:
        b.lathe(center, "X", [(-w, r), (w, r)], seg)
        return
    # Dished steel disc wheel with hub and six nuts on the outer face.
    disc_x = center[0] + outer_side * (w - 0.01)
    b.lathe((disc_x, center[1], center[2]), "X",
            [(-outer_side * 0.0, rim), (-outer_side * 0.03, rim * 0.80), (-outer_side * 0.035, 0.07)],
            max(12, seg // 2))
    if detail >= 2:
        hub = (disc_x - outer_side * 0.03, center[1], center[2])
        b.lathe(hub, "X", [(0.0, 0.065), (outer_side * 0.05, 0.05), (outer_side * 0.06, 0.03)], 10)
        for i in range(6):
            a = math.tau * i / 6
            p = (hub[0] + outer_side * 0.005, center[1] + 0.095 * math.cos(a), center[2] + 0.095 * math.sin(a))
            b.lathe(p, "X", [(0.0, 0.011), (outer_side * 0.015, 0.009)] if outer_side > 0
                    else [(-0.015, 0.009), (0.0, 0.011)], 6)


def build_wheels(cfg, mat):
    seg = cfg["seg"]
    detail = cfg["detail"]
    for name, side in (("Roue_Droite_01", 1), ("Roue_Gauche_01", -1)):
        center = Vector((side * S.FRONT_X, S.FRONT_AXLE_Y, S.WHEEL_Z))
        b = Builder()
        tyre(b, center, S.TYRE_W, seg, detail, side)
        b.finish(name, mat, center, None, sharp=60)
    pivot = Vector((0.0, S.REAR_AXLE_Y, S.WHEEL_Z))
    b = Builder()
    for side in (-1, 1):
        for k, x in enumerate(S.REAR_X):
            # Twin tyres: only the outer one shows its disc face.
            tyre(b, (side * x, S.REAR_AXLE_Y, S.WHEEL_Z), S.TYRE_W, seg, detail if k == 1 else min(detail, 1), side)
    b.finish("Roue_02", mat, pivot, None, sharp=60)


def build_chassis(cfg, mat):
    detail = cfg["detail"]
    seg = cfg["seg"]
    b = Builder()
    b.prism(S.BONNET, -S.BONNET_HALF, S.BONNET_HALF)
    b.prism(S.CAB_LOWER, -S.CAB_HALF, S.CAB_HALF)
    b.loft([rect_ring(z, f, r, h) for z, f, r, h in S.CAB_UPPER])
    steps = {0: 3, 1: 6, 2: 12}[detail]
    for side in (-1, 1):
        for guard in (S.FRONT_GUARD, S.REAR_GUARD):
            cy, cz, r, a0, a1, x0, x1 = guard
            arc_strip(b, (cy, cz, r, a0, a1, side * x0, side * x1) if side > 0 else (cy, cz, r, a0, a1, -x1, -x0), steps)

    if detail >= 1:
        # Rear mudguard outer skirts, as seen from the rear.
        cy, cz, r, a0, a1, x0, x1 = S.REAR_GUARD
        steps = {1: 6, 2: 12}[detail]
        for side in (-1, 1):
            x = side * (x1 - 0.006)
            arc_strip(b, (cy, cz, r, a0, a1, x - 0.006, x + 0.006), steps, thickness=0.10)
        # Axles, leaf springs, frame rails and propeller shaft.
        b.lathe((0.0, S.FRONT_AXLE_Y, S.WHEEL_Z - 0.04), "X", [(-0.60, 0.035), (0.60, 0.035)], 6)
        b.lathe((0.0, S.REAR_AXLE_Y, S.WHEEL_Z), "X", [(-0.62, 0.05), (-0.18, 0.06), (0.18, 0.06), (0.62, 0.05)], 8)
        b.lathe((0.0, S.REAR_AXLE_Y, S.WHEEL_Z), "Y", [(-0.13, 0.08), (0.0, 0.14), (0.13, 0.08)], 10)
        b.lathe((0.0, S.REAR_AXLE_Y + 0.14, S.WHEEL_Z + 0.02), "Y", [(0.0, 0.03), (1.0, 0.03)], 6)
        for side in (-1, 1):
            x = side * 0.40
            for axle, z in ((S.FRONT_AXLE_Y, 0.40), (S.REAR_AXLE_Y, 0.46)):
                b.prism([(axle + 0.45, z + 0.03), (axle, z - 0.02), (axle - 0.45, z + 0.03), (axle - 0.45, z + 0.06),
                         (axle, z + 0.02), (axle + 0.45, z + 0.06)], x - 0.03, x + 0.03)
            b.box((x, 0.0, 0.42), (0.06, 3.2, 0.08))
        # Spare wheel on the right side.
        sx, sy, sz = S.SPARE
        b.lathe((sx, sy, sz), "X", [(-0.06, S.RIM_R), (-0.055, S.TYRE_R * 0.9), (-0.035, S.TYRE_R),
                                    (0.035, S.TYRE_R), (0.055, S.TYRE_R * 0.9), (0.06, S.RIM_R)], seg)
        b.lathe((sx + 0.05, sy, sz), "X", [(0.0, S.RIM_R), (0.02, 0.07)], max(8, seg // 2))
        # Headlamp on the left of the sloped front plate.
        hx, hy, hz = S.HEADLAMP
        b.lathe((hx, hy, hz), "Y", [(-0.06, 0.05), (0.03, 0.085), (0.05, 0.075)], max(8, seg // 2))
        b.strut((hx, hy - 0.05, hz - 0.03), (hx + 0.06, hy - 0.10, hz - 0.12), 0.025)
        # Tow hook at the rear.
        tx, ty, tz = S.TOW_HOOK
        b.box((tx, ty + 0.17, tz), (0.10, 0.34, 0.06))
        b.lathe((tx, ty, tz), "X", [(-0.02, 0.05), (0.02, 0.05)], 8)
        # Muffler under the rear.
        mx, my, mz = S.MUFFLER
        b.lathe((mx, my, mz), "Y", [(-0.25, 0.05), (-0.22, 0.07), (0.22, 0.07), (0.25, 0.04)], 8)

    if detail >= 2:
        add_high_detail(b)
    return b.finish("Chassis", mat)


def add_high_detail(b):
    half_b, half_c = S.BONNET_HALF, S.CAB_HALF
    # Bonnet: louvres on both sides, top hatch hinges, radiator door and starting-handle hole.
    for side in (-1, 1):
        x = side * (half_b + 0.006)
        for k in range(3):
            y = 0.92 - k * 0.09
            b.box((x, y, 0.99), (0.012, 0.035, 0.14))
        for y in (1.12, 0.62):
            b.box((side * (half_b - 0.04), y, 1.22), (0.08, 0.05, 0.02))
        # Side hatch on the bonnet with handles.
        b.box((x, 0.45, 0.78), (0.01, 0.42, 0.26))
        for y in (0.30, 0.62):
            b.box((x + side * 0.01, y, 0.93), (0.01, 0.06, 0.03))
        # Compartment door hinges and handles.
        xc = side * (half_c + 0.006)
        for z in (0.62, 1.05):
            b.box((xc, -0.14, z), (0.014, 0.06, 0.05))
        b.box((xc + side * 0.01, -0.58, 0.85), (0.012, 0.025, 0.12))
        # Grab handles under the roof line and pennant brackets.
        b.strut((xc, -0.70, 1.20), (xc + side * 0.03, -0.70, 1.20), 0.012)
        b.strut((xc, -1.05, 1.20), (xc + side * 0.03, -1.05, 1.20), 0.012)
        b.strut((xc + side * 0.03, -0.70, 1.20), (xc + side * 0.03, -1.05, 1.20), 0.012)
        # Mudguard stays from the guards to the hull.
        b.strut((side * half_b, 1.20, 0.80), (side * S.FRONT_X, 1.45, 0.82), 0.02)
        b.strut((side * half_c, -0.80, 0.80), (side * 0.70, -0.90, 0.88), 0.02)
        b.strut((side * half_c, -1.40, 0.70), (side * 0.70, -1.50, 0.80), 0.02)
    # Front: armoured radiator doors and a bumper bar.
    b.box((0.0, 1.386, 0.86), (0.80, 0.016, 0.46))
    b.box((0.0, 1.396, 0.86), (0.02, 0.012, 0.44))
    b.lathe((0.0, 1.39, 0.70), "Y", [(0.0, 0.03), (0.03, 0.025)], 8)
    b.box((0.0, 1.50, 0.50), (1.05, 0.05, 0.07))
    for x in (-0.40, 0.40):
        b.box((x, 1.43, 0.53), (0.05, 0.14, 0.05))
    # Driver's vision plate on the sloped front, with its two flaps.
    lo, hi = S.CAB_UPPER
    zf = (lo[0] + hi[0]) / 2 + 0.06
    yf = lo[1] + (hi[1] - lo[1]) * (zf - lo[0]) / (hi[0] - lo[0])
    b.box((-0.18, yf + 0.012, zf), (0.34, 0.02, 0.12))
    b.box((0.18, yf + 0.012, zf), (0.30, 0.02, 0.10))
    # Rear door with hinges and the rear plate handle.
    b.box((0.0, -1.49, 0.95), (0.46, 0.014, 0.52))
    for z in (0.78, 1.12):
        b.box((-0.23, -1.50, z), (0.06, 0.016, 0.05))
    b.box((0.12, -1.505, 0.96), (0.10, 0.012, 0.025))
    # Roof ventilator.
    b.lathe((0.30, -0.30, S.ROOF_Z), "Z", [(0.0, 0.07), (0.05, 0.06)], 8)


def build_turret(cfg, mat, chassis):
    detail = cfg["detail"]
    cx, cy, cz = S.TURRET_C
    b = Builder()
    rings = S.TURRET_RINGS if detail >= 1 else [S.TURRET_RINGS[0], S.TURRET_RINGS[-1]]
    b.loft([S.chamfer_ring(cx, cy, z, hl, hw, c) for z, hl, hw, c in rings])
    ux, uy = S.CUPOLA_C
    b.loft([S.hexagon(ux, uy, z, r) for z, r in S.CUPOLA])
    if detail >= 1:
        top = S.CUPOLA[-1][0]
        r = S.CUPOLA[-1][1]
        # Two hinged hood covers over the hexagonal roof opening.
        for side in (-1, 1):
            b.box((ux + side * r * 0.42, uy, top + 0.012), (r * 0.80, r * 1.55, 0.02))
    if detail >= 2:
        top = S.CUPOLA[-1][0]
        # Pennant rail and hinges, vision slits and side hatch.
        for side in (-1, 1):
            b.strut((ux + side * 0.17, uy + 0.12, top + 0.04), (ux + side * 0.17, uy - 0.12, top + 0.04), 0.012)
            for y in (uy + 0.12, uy - 0.12):
                b.strut((ux + side * 0.17, y, top), (ux + side * 0.17, y, top + 0.04), 0.012)
            hl, hw = S.TURRET_RINGS[1][1], S.TURRET_RINGS[1][2]
            b.box((cx + side * (hw - 0.03), cy - 0.05, cz + 0.20), (0.03, 0.30, 0.18))
            b.box((cx + side * (hw - 0.015), cy - 0.05, cz + 0.27), (0.02, 0.12, 0.012))
        b.box((cx, cy - S.TURRET_RINGS[1][1] + 0.035, cz + 0.20), (0.28, 0.03, 0.012))
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
    return turret, canon


def dummy_slots(turret, mat):
    """Hidden weapon slots 2-4, as on the tanks: Dummy empties and a 1.5 cm cube barrel."""
    mount = Vector(S.MOUNT)
    half = 1.5 / 203.0
    for slot in (2, 3, 4):
        t = helper("Tourelle_%02d" % slot, mount, turret)
        t["eug_helper_class"] = "Dummy"
        a = helper("Axe_Canon_%02d" % slot, mount, t)
        a["eug_helper_class"] = "Dummy"
        b = Builder()
        b.box(mount, (2 * half, 2 * half, 2 * half))
        canon = b.finish("Canon_%02d" % slot, mat, mount, a)
        helper("Fx_tourelle%d_tir_01" % slot, (mount.x, S.MUZZLE_Y, mount.z), canon)


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

    main = material_main()
    chassis = build_chassis(cfg, main)
    turret, _ = build_turret(cfg, main, chassis)
    dummy_slots(turret, main)
    build_wheels(cfg, main)

    helper("Fx_Stress_01", (0.0, -0.40, S.ROOF_Z + 0.05), chassis)
    helper("Fx_Stress_02", (0.0, 0.80, 1.26), chassis)
    for side, letter in ((1, "D"), (-1, "G")):
        obj = helper("FX_Fumee_Roue_%s1" % letter, (side * S.REAR_X[1], S.REAR_AXLE_Y - 0.25, 0.0), chassis)
        obj.parent = None
        place(obj, (side * S.REAR_X[1], S.REAR_AXLE_Y - 0.25, 0.0), None)

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    unwrap(meshes)
    report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


def render_clay():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("Preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.65, 0.7, 0.75, 1)
    scene.world = world
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, getattr(S, "GROUND_Z", 0.0)))
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.5
    sun = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    views = {"geo_" + k: v for k, v in S.RENDER_VIEWS.items() if k != "zblizenie"}
    for name, (kind, location, target, value) in views.items():
        data.type = kind
        if kind == "ORTHO":
            data.ortho_scale = value
        else:
            data.lens = value
        camera.location = location
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(OUT, "%s.png" % name)
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        render_clay()
    print("BUILD_DONE")
