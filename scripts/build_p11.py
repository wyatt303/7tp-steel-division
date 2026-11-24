"""Build the PZL P.11c fighter in High, Mid and Low versions, plus the landing gear file.

  blender --background --factory-startup --python build_p11.py -- <output_dir>

See spec_p11.py for the node layout, copied from the game's fixed-gear aircraft.
"""

import math
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["TK_SPEC"] = "spec_p11"
import spec_p11 as S  # noqa: E402
import build_tk as T  # noqa: E402

Builder, helper, place = T.Builder, T.helper, T.place
OUT = T.OUT

LODS = {
    "Low": {"detail": 0, "ring": 6, "foil": 4, "seg": 6, "limit": 700},
    "Mid": {"detail": 1, "ring": 10, "foil": 8, "seg": 10, "limit": 2000},
    "High": {"detail": 2, "ring": 20, "foil": 18, "seg": 20, "limit": 12000},
}


def lerp(a, b, t):
    return a + (b - a) * t


def interp(table, key):
    """Linear interpolation in a table of tuples sorted by the first column."""
    if key <= table[0][0]:
        return table[0]
    for a, b in zip(table, table[1:]):
        if a[0] <= key <= b[0]:
            t = (key - a[0]) / (b[0] - a[0])
            return tuple(lerp(p, q, t) for p, q in zip(a, b))
    return table[-1]


def thickness(f, t):
    """NACA four-digit half thickness at chord fraction f, for thickness ratio t."""
    f = max(f, 0.0)
    return 5 * t * (0.2969 * math.sqrt(f) - 0.126 * f - 0.3516 * f ** 2 + 0.2843 * f ** 3 - 0.1036 * f ** 4)


def foil_fractions(n, f0=0.0, f1=1.0):
    """Cosine-spaced chord fractions, n of them, between f0 and f1."""
    return [f0 + (f1 - f0) * (1 - math.cos(math.pi * i / (n - 1))) / 2 for i in range(n)]


def section(n, le, te, zc, t, f0, f1, camber=0.02, axis="X", pos=0.0):
    """Closed airfoil ring. Horizontal surfaces lie at X=pos, vertical ones (axis "Z") at Z=pos."""
    chord = le - te
    fr = foil_fractions(n, f0, f1)
    top = [(le - f * chord, thickness(f, t) * chord + camber * chord * 4 * f * (1 - f)) for f in reversed(fr)]
    bottom = [(le - f * chord, -thickness(f, t) * chord + camber * chord * 4 * f * (1 - f)) for f in fr[1:-1]]
    pts = top + bottom
    if axis == "X":
        return [(pos, y, zc + d) for y, d in pts]
    return [(d, y, pos) for y, d in pts]


def wing_station(span):
    s, le, te, zc, t = interp(S.WING, span)
    return le, te, zc, t


def build_wing(b, cfg):
    n = cfg["foil"]
    a0, a1, ail = S.AILERON
    eps = 0.003
    spans = [0.33, 0.95, 1.95, a0, a0 + eps, 3.7, a1, a1 + eps, 5.05, 5.25, 5.36]
    if cfg["detail"] == 0:
        spans = [0.33, 1.95, a0, a0 + eps, a1, a1 + eps, 5.36]
    elif cfg["detail"] == 1:
        spans = [0.33, 0.95, 1.95, a0, a0 + eps, a1, a1 + eps, 5.15, 5.36]
    rings = []
    for side in (-1, 1):
        order = spans if side > 0 else list(reversed(spans))
        for span in order:
            le, te, zc, t = wing_station(span)
            cut = a0 + eps * 0.5 <= span <= a1 + eps * 0.5
            f1 = 1.0 - ail / (le - te) if cut else 1.0
            rings.append(section(n, le, te, zc, t, 0.0, f1, pos=side * span))
    b.loft(rings)


def build_aileron(cfg, mat, chassis, side, name):
    n = max(4, cfg["foil"] // 2)
    a0, a1, ail = S.AILERON
    rings = []
    for span in (a0 + 0.003, (a0 + a1) / 2, a1):
        le, te, zc, t = wing_station(span)
        f0 = 1.0 - ail / (le - te)
        rings.append(section(n, le, te, zc, t, f0, 1.0, pos=side * span))
    le, te, zc, t = wing_station((a0 + a1) / 2)
    pivot = (side * (a0 + a1) / 2, te + ail, zc)
    b = Builder()
    b.loft(rings)
    return b.finish(name, mat, pivot, chassis, sharp=50)


def superellipse(cy, top, bottom, half, n, p=2.6):
    cz, hz = (top + bottom) / 2, (top - bottom) / 2
    pts = []
    for i in range(n):
        a = math.tau * i / n
        c, s = math.cos(a), math.sin(a)
        x = half * math.copysign(abs(c) ** (2 / p), c)
        z = cz + hz * math.copysign(abs(s) ** (2 / p), s)
        pts.append((x, cy, z))
    return pts


def build_chassis(cfg, mat):
    detail = cfg["detail"]
    seg = cfg["seg"]
    b = Builder()
    # Fuselage and cowling.
    b.loft([superellipse(y, top, bot, half, cfg["ring"]) for y, top, bot, half in S.FUSELAGE])
    front, rear, r = S.COWL_FRONT, S.COWL_REAR, S.COWL_R
    off = lambda y: y - rear  # noqa: E731
    if detail == 0:
        b.lathe((0, rear, -0.03), "Y", [(0.0, 0.60), (off(front), r), (off(front) - 0.10, r - 0.13)], 6)
    else:
        b.lathe((0, rear, -0.03), "Y", [(0.0, 0.60), (off(front) - 0.08, r), (off(front), r - 0.03), (off(front), r - 0.10),
                                        (off(front) - 0.10, r - 0.13), (0.08, 0.48)], seg + 2)
    build_wing(b, cfg)
    # Tailplane (fixed part) and fin.
    n = max(4, cfg["foil"] - 2)
    rings = []
    stations = [st for st in S.TAILPLANE]
    for side in (-1, 1):
        order = stations if side > 0 else list(reversed(stations))
        for span, le, hinge, te in order:
            f1 = (le - hinge) / (le - te)
            rings.append(section(n, le, te, S.TAIL_Z, 0.08, 0.0, f1, camber=0.0, pos=side * span))
    b.loft(rings)
    fin_rings = []
    for z, le in S.FIN:
        te = S.HINGE_RUDDER - 0.25
        f1 = (le - S.HINGE_RUDDER) / (le - te)
        fin_rings.append(section(n, le, te, 0.0, 0.08, 0.0, min(f1, 0.999), camber=0.0, axis="Z", pos=z))
    b.loft(fin_rings)
    # Main gear: oleo legs to the wing, rear braces and the split axle.
    wy, wz, wx = S.WHEEL_Y, S.WHEEL_Z, S.WHEEL_X
    for side in (-1, 1):
        axle = (side * (wx - 0.10), wy, wz)
        b.strut(axle, (side * 1.10, wy + 0.04, 0.78), 0.07, 0.10)
        if detail >= 1:
            b.strut(axle, (side * 0.30, S.Y(330), S.Z(330)), 0.05, 0.05)
            b.strut(axle, (side * 0.05, wy + 0.02, S.Z(345)), 0.05, 0.05)
    if detail >= 1:
        # Engine face behind the ring: crankcase and nine cylinders.
        cy = front - 0.18
        b.lathe((0, cy, -0.03), "Y", [(-0.12, 0.10), (0.0, 0.24), (0.10, 0.20)], max(8, seg))
        cyl = 9 if detail >= 2 else 0
        for i in range(cyl):
            a = math.tau * i / cyl
            d = Vector((math.cos(a), 0.0, math.sin(a)))
            base = Vector((0, cy, -0.03))
            b.strut(base + d * 0.20, base + d * 0.50, 0.11, 0.11)
        # Windscreen, cockpit coaming and headrest.
        top = S.Z(176)
        b.prism([(S.Y(425), top), (S.Y(432), top + 0.20), (S.Y(445), top + 0.20), (S.Y(440), top)], -0.17, 0.17)
        b.lathe((0, S.Y(465), top - 0.01), "Z", [(0.0, 0.33), (0.03, 0.30)], max(10, seg))
        b.loft([superellipse(y, top + h, top - 0.10, w, 8) for y, h, w in
                ((S.Y(500), 0.14, 0.14), (S.Y(560), 0.12, 0.11), (S.Y(650), 0.04, 0.07))])
    if detail >= 2:
        # Wing gun fairings, pitot tube, exhaust collector stubs and tail skid fairing.
        for x, y, z in S.MUZZLES[2:]:
            b.lathe((x, y - 0.10, z), "Y", [(-0.20, 0.03), (0.08, 0.025)], 6)
        b.lathe((3.8, S.Y(205), S.Z(150)), "Y", [(-0.30, 0.012), (0.20, 0.008)], 6)
        for side in (-1, 1):
            b.lathe((side * 0.45, rear - 0.06, -0.48), "Y", [(-0.30, 0.04), (0.0, 0.05)], 6)
            # Gear leg fairings near the wheel.
            b.box((side * (wx - 0.12), wy, wz + 0.25), (0.06, 0.16, 0.28))
    return b.finish("Chassis", mat)


def build_controls(cfg, mat, chassis):
    build_aileron(cfg, mat, chassis, 1, "Aileron_D")
    build_aileron(cfg, mat, chassis, -1, "Aileron_G")
    n = max(4, cfg["foil"] // 2)
    for side, name in ((1, "Elevator_D"), (-1, "Elevator_G")):
        rings = []
        for span, le, hinge, te in S.TAILPLANE:
            f0 = (le - hinge) / (le - te)
            rings.append(section(n, le, te, S.TAIL_Z, 0.08, min(f0, 0.995), 1.0, camber=0.0, pos=side * span))
        if side < 0:
            rings.reverse()
        b = Builder()
        b.loft(rings)
        b.finish(name, mat, (side * 0.8, S.TAILPLANE[0][2], S.TAIL_Z), chassis, sharp=50)
    rings = []
    for z, te in S.RUDDER:
        le = S.HINGE_RUDDER + 0.02
        rings.append(section(n, le, te, 0.0, 0.09, 0.0, 1.0, camber=0.0, axis="Z", pos=z))
    b = Builder()
    b.loft(rings)
    b.finish("Rudder", mat, (0.0, S.HINGE_RUDDER, (S.RUDDER[0][0] + S.RUDDER[-1][0]) / 2), chassis, sharp=50)


def build_engine(cfg, mat, chassis):
    seg = max(8, cfg["seg"])
    hub = Vector((0.0, S.PROP_Y, -0.03))
    b = Builder()
    tip = S.SPINNER_TIP - S.PROP_Y
    if cfg["detail"] == 0:
        b.lathe(hub, "Y", [(-0.10, S.SPINNER_R), (tip, 0.02)], 6)
    else:
        b.lathe(hub, "Y", [(-0.10, S.SPINNER_R), (0.05, S.SPINNER_R), (tip * 0.6, S.SPINNER_R * 0.7), (tip, 0.02)], seg)
    moteur = b.finish("Bloc_Moteur_1", mat, hub, chassis, sharp=60)

    b = Builder()
    stations = 3 if cfg["detail"] == 0 else (5 if cfg["detail"] == 1 else 8)
    for sign in (1, -1):
        rings = []
        for i in range(stations):
            r = lerp(0.18, S.PROP_R, i / (stations - 1))
            k = (r - 0.18) / (S.PROP_R - 0.18)
            chord = 0.20 * (1 - k) + 0.17 * k if k < 0.85 else 0.17 - (k - 0.85) / 0.15 * 0.10
            thick = 0.05 * (1 - k) + 0.012 * k
            pitch = math.radians(38 - 24 * k)
            u = Vector((math.cos(pitch), -math.sin(pitch), 0.0))
            v = Vector((math.sin(pitch), math.cos(pitch), 0.0))
            c = hub + Vector((0.0, 0.0, sign * r))
            pts = [c + u * chord * 0.5, c + v * thick * 0.5, c - u * chord * 0.5, c - v * thick * 0.5]
            if sign < 0:
                pts = [Vector((-(p.x - hub.x) + hub.x, p.y, p.z)) for p in pts]
            rings.append([tuple(p) for p in pts])
        b.loft(rings)
    b.finish("Helice_LS_1", mat, hub, moteur, sharp=50)


def build_wheels(cfg, mat, chassis):
    seg = cfg["seg"]
    r, w = S.WHEEL_R, S.WHEEL_W
    pivot = (0.0, S.WHEEL_Y, S.WHEEL_Z)
    b = Builder()
    for side in (-1, 1):
        c = (side * S.WHEEL_X, S.WHEEL_Y, S.WHEEL_Z)
        if cfg["detail"] >= 1:
            b.lathe(c, "X", [(-w / 2, r * 0.45), (-w * 0.48, r * 0.85), (-w * 0.3, r), (w * 0.3, r), (w * 0.48, r * 0.85),
                             (w / 2, r * 0.45)], seg)
            b.lathe((c[0] + side * w * 0.45, c[1], c[2]), "X", [(0.0, r * 0.45), (side * 0.03, 0.06)], max(8, seg // 2))
        else:
            b.lathe(c, "X", [(-w / 2, r), (w / 2, r)], seg)
    b.finish("Roue_Avant", mat, pivot, chassis, sharp=60)
    x, y, z = S.SKID
    b = Builder()
    b.strut((x, y + 0.15, z + 0.30), (x, y, z), 0.05, 0.05)
    b.box((x, y - 0.03, z - 0.01), (0.06, 0.18, 0.04))
    b.finish("Roue_Arriere", mat, (x, y, z), chassis, sharp=50)


def build_guns(cfg, mat, chassis):
    tourelle = helper("Tourelle_01", S.GUN_PIVOT, chassis)
    axe = helper("Axe_Canon_01", S.GUN_PIVOT, tourelle)
    b = Builder()
    for x, y, z in S.MUZZLES:
        b.lathe((x, y, z), "Y", [(-0.25, 0.014), (0.0, 0.012)], 5 if cfg["detail"] else 3)
    canon = b.finish("Canon_01", mat, S.GUN_PIVOT, axe, sharp=50)
    for i, (x, y, z) in enumerate(S.MUZZLES, 1):
        helper("Fx_tourelle1_tir_%02d" % i, (x, y + 0.01, z), canon)


def report(name, limit):
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    size = [max(c[i] for c in corners) - min(c[i] for c in corners) for i in range(3)]
    total = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    print("REPORT %s %s tris=%d limit=%d objects=%d span=%.3f length=%.3f height=%.3f" % (
        S.STEM, name, total, limit, len(meshes), size[0], size[1], size[2]))


def new_scene(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_scene_fbx")
    bpy.context.scene.unit_settings.system = "METRIC"
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]


def build(name, cfg):
    new_scene("%s_%s" % (S.STEM, name))
    main = T.material_main()
    chassis = build_chassis(cfg, main)
    build_controls(cfg, main, chassis)
    build_engine(cfg, main, chassis)
    build_wheels(cfg, main, chassis)
    build_guns(cfg, main, chassis)
    helper("Pilot", S.PILOT, chassis)
    helper("FX_Vortex_D", S.VORTEX, chassis)
    helper("FX_Vortex_G", (-S.VORTEX[0], S.VORTEX[1], S.VORTEX[2]), chassis)
    helper("Fx_Stress_01", (0.35, S.Y(420), 0.10), chassis)
    helper("Fx_Stress_02", (-0.30, S.Y(200), 0.0), chassis)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    T.unwrap(meshes)
    report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_%s.blend" % (S.STEM, name)))


def build_train():
    """Landing gear file: only the two ground contact helpers, as in Storch_train."""
    new_scene("%s_train" % S.STEM)
    for name, pos in (("Train_Avant", S.TRAIN_AVANT), ("Train_Arriere", S.TRAIN_ARRIERE)):
        helper(name, pos, None)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "%s_train.blend" % S.STEM))


def render_clay():
    import build_wz34 as W
    W.S = S
    W.render_clay()


if __name__ == "__main__":
    for lod_name, lod_cfg in LODS.items():
        build(lod_name, lod_cfg)
    if not os.environ.get("TK_NO_RENDER"):
        render_clay()
    build_train()
    print("BUILD_DONE")
