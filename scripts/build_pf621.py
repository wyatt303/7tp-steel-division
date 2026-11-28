"""Build the Polski Fiat 621L truck in High, Mid and Low versions.

  set TK_SPEC=spec_pf621        (with the canvas tilt, PF621L)
  set TK_SPEC=spec_pf621_open   (open cargo body, PF621L_OPEN)
  blender --background --factory-startup --python build_pf621.py -- <output_dir>

Node layout copied from the game's Opel Blitz, see spec_pf621.py.
"""

import importlib
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TK_SPEC", "spec_pf621")
S = importlib.import_module(os.environ["TK_SPEC"])
import build_tk as T  # noqa: E402
import build_p11 as P  # noqa: E402
import build_wz34 as W  # noqa: E402
import glass  # noqa: E402

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


def tilt_ring(y, bottom, top, half, rise=0.32, steps=6):
    """Canvas tilt section: straight sides and a rounded top over the bows."""
    pts = [(half, y, bottom)]
    for i in range(steps + 1):
        a = math.pi * i / steps
        pts.append((half * math.cos(a), y, top - rise + rise * math.sin(a)))
    pts.append((-half, y, bottom))
    return pts


def plan_ring(z, front, rear, half, c=0.06):
    """Horizontal section of the cab with cut corners."""
    return [(half, front - c, z), (half - c, front, z), (-half + c, front, z), (-half, front - c, z),
            (-half, rear + c, z), (-half + c, rear, z), (half - c, rear, z), (half, rear + c, z)]


def bonnet_half(y):
    """Half width of the bonnet at y (between the radiator and the cowl)."""
    pts = sorted((r[0], r[3]) for r in S.BONNET)
    if y <= pts[0][0]:
        return pts[0][1]
    for (y0, h0), (y1, h1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return h0 + (h1 - h0) * (y - y0) / (y1 - y0)
    return pts[-1][1]


def front_guard_profile(a0, steps, thickness=0.012):
    """Side profile (Y, Z) of the front mudguard, as on the drawing: an arc over the wheel from
    angle a0 back to 150 degrees, a straight run down to the running board, and the panel
    behind the wheel filled down to the running board, leaving the wheel arch open."""
    cy, cz, r = S.FRONT_AXLE_Y, S.WHEEL_Z, S.FRONT_GUARD_R
    ri = r - thickness
    ey, ez = S.FRONT_GUARD_END
    outer = []
    for i in range(steps + 1):
        a = math.radians(a0 + (150 - a0) * i / steps)
        outer.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    outer.append((ey, ez))
    # Where the running-board line meets the wheel arch, then the arch back to the front.
    a_end = math.pi + math.asin((cz - ez) / ri)
    back = (cy + ri * math.cos(a_end), ez)
    inner = []
    for i in range(steps + 1):
        a = a_end + (math.radians(a0) - a_end) * i / steps
        inner.append((cy + ri * math.cos(a), cz + ri * math.sin(a)))
    return outer + [back] + inner[1:]


def build_chassis(cfg, mat):
    d, seg = cfg["detail"], cfg["seg"]
    b = Builder()
    # Frame rails.
    z0, z1 = S.FRAME_Z
    for side in (-1, 1):
        b.box((side * 0.42, (S.FRONT_Y + S.REAR_Y) / 2 - 0.05, (z0 + z1) / 2), (0.08, S.FRONT_Y - S.REAR_Y - 0.25, z1 - z0))
    # Bonnet from the radiator shell back to the cowl, which widens and rises into the cab.
    b.loft([ring(y, bottom, top, half, 0.10) for y, bottom, top, half in S.BONNET + S.COWL[1:]])
    # Radiator shell with a rounded top and the grille in front of it.
    gh, gz0, gz1 = S.GRILLE
    ry = S.RADIATOR_Y
    b.loft([ring(ry + 0.04, gz0 - 0.03, gz1 + 0.03, gh + 0.03, 0.10), ring(ry, gz0 - 0.03, gz1 + 0.03, gh + 0.03, 0.10)])
    # Cab: horizontal sections, vertical below the cowl line and leaning back above it, with a
    # rounded roof edge and the short visor over the windscreen.
    cz0, cz1, cz2 = S.CAB_Z
    h, rear = S.CAB_HALF, S.CAB_REAR
    build_cab(b, d, seg)
    top_front = S.cab_front(cz2)
    b.box((0.0, top_front + S.VISOR / 2, cz2 - 0.025), (2 * h - 0.10, S.VISOR + 0.02, 0.04))
    # Cargo body: floor, sides, front and rear boards.
    by0, by1, floor, side_top, bh = S.BODY
    b.box((0.0, (by0 + by1) / 2, floor - 0.05), (2 * bh, by0 - by1, 0.10))
    for k in range(4 if d >= 1 else 2):
        y = by0 - 0.25 - k * (by0 - by1 - 0.50) / (3 if d >= 1 else 1)
        b.box((0.0, y, (S.FRAME_Z[1] + floor - 0.10) / 2), (2 * bh - 0.10, 0.08, floor - 0.10 - S.FRAME_Z[1]))
    for side in (-1, 1):
        b.box((side * (bh - 0.02), (by0 + by1) / 2, (floor + side_top) / 2), (0.04, by0 - by1, side_top - floor))
    # Front and tail boards between the sides (flush ends would flicker in the game).
    b.box((0.0, by1 + 0.02, (floor + side_top) / 2), (2 * bh - 0.08, 0.04, side_top - floor))
    b.box((0.0, by0 - 0.02, (floor + side_top) / 2), (2 * bh - 0.08, 0.04, side_top - floor))
    if S.TILT:
        steps = {0: 3, 1: 5, 2: 8}[d]
        b.loft([tilt_ring(y, side_top - 0.02, S.TILT_TOP, bh + 0.01, steps=steps) for y in (by0 - 0.01, by1 + 0.01)])
    # Front mudguards with their inner aprons, rear mudguards over the twin wheels, running boards.
    for side in (-1, 1):
        x0, x1 = S.FRONT_GUARD_X
        lo, hi = sorted((side * x0, side * x1))
        steps = {0: 4, 1: 7, 2: 10}[d]
        b.prism(front_guard_profile(30, steps), lo, hi)
        lo, hi = sorted((side * (bonnet_half(S.FRONT_AXLE_Y) - 0.01), side * x0))
        b.prism(front_guard_profile(60, steps), lo, hi)
        cy, cz, r, a0, a1, rx0, rx1 = S.REAR_GUARD
        lo, hi = sorted((side * rx0, side * rx1))
        W.arc_strip(b, (cy, cz, r, a0, a1, lo, hi), {0: 3, 1: 6, 2: 10}[d])
        sy0, sy1, sz = S.STEP
        sx0, sx1 = S.STEP_X
        b.box((side * (sx0 + sx1) / 2, (sy0 + sy1) / 2, sz), (sx1 - sx0, sy0 - sy1, 0.03))
    # Toolbox and fuel tank under the front of the cargo body, behind the cab.
    tx, ty, tz, sx, sy, sz = S.TOOLBOX
    b.box((tx, ty, tz), (sx, sy, sz))
    fx, fy_, fz = S.FUEL_TANK
    b.lathe((fx, fy_, fz), "Y", [(-0.28, 0.15), (0.28, 0.15)], max(6, seg // 2))
    # Tubular bumper with short horns at its ends, headlamps.
    yb, zb, lb = S.BUMPER
    b.lathe((0.0, yb, zb), "X", [(-lb, 0.045), (lb, 0.045)], max(6, seg // 2))
    for x, y, z in S.HEADLAMPS:
        b.lathe((x, y, z), "Y", [(-0.10, 0.08), (0.0, S.HEADLAMP_R), (0.03, S.HEADLAMP_R - 0.01)], max(8, seg))
    if d >= 1:
        for side in (-1, 1):
            b.lathe((side * (lb - 0.06), yb, zb), "Y", [(0.0, 0.04), (0.14, 0.04)], 8)
            b.box((side * 0.42, (yb + S.FRONT_AXLE_Y + 0.30) / 2, zb + 0.02), (0.05, yb - S.FRONT_AXLE_Y - 0.30, 0.06))
        for x, y, z in S.HEADLAMPS:
            b.strut((x, y - 0.06, z - 0.08), (x * 0.70, y - 0.10, 0.74), 0.03)
        # Grille bars, the windscreen centre bar, door handles.
        n = 9 if d >= 2 else 5
        for k in range(n):
            x = -gh + 0.03 + k * (2 * gh - 0.06) / (n - 1)
            b.box((x, ry + 0.045, (gz0 + gz1) / 2), (0.014, 0.012, gz1 - gz0 - 0.06))
        wz0, wz1 = S.WINDSCREEN_Z
        zm = (wz0 + wz1) / 2
        b.box((0.0, S.cab_front(zm) + 0.012, zm), (0.04, 0.02, wz1 - wz0))
        for side in (-1, 1):
            b.box((side * (h + 0.006), S.SIDE_WINDOW[1] + 0.06, 1.30), (0.012, 0.14, 0.025))
            # Bonnet louvres: two rows on each side.
            n = 7 if d >= 2 else 3
            ly0, ly1 = S.LOUVRE_Y
            for lz0, lz1 in S.LOUVRES:
                for k in range(n):
                    y = ly0 - k * (ly0 - ly1) / (n - 1)
                    b.box((side * (bonnet_half(y) + 0.006), y, (lz0 + lz1) / 2), (0.012, 0.035, lz1 - lz0))
            # Rope rail under the top of the cargo sides.
            b.box((side * (bh + 0.006), (by0 + by1) / 2, side_top - 0.05), (0.012, by0 - by1 - 0.1, 0.03))
            # Frames of the small tilt windows (High only; Mid keeps the painted panes).
            if S.TILT and d >= 2:
                tz0, tz1 = S.TILT_WINDOW_Z
                for y0, y1 in S.TILT_WINDOWS:
                    for zz in (tz0, tz1):
                        b.box((side * (bh + 0.02), (y0 + y1) / 2, zz), (0.012, abs(y0 - y1) + 0.03, 0.025))
                    for yy in (y0, y1):
                        b.box((side * (bh + 0.02), yy, (tz0 + tz1) / 2), (0.012, 0.025, tz1 - tz0))
        # Spare wheel under the rear of the cargo body.
        b.lathe((0.0, by1 + 0.50, floor - 0.30), "Z", [(-0.08, S.TYRE_R), (0.08, S.TYRE_R)], seg)
    if d >= 2:
        # Axles, leaf springs, differential, exhaust, tow hook, stakes on the cargo sides.
        for axle in (S.FRONT_AXLE_Y, S.REAR_AXLE_Y):
            b.lathe((0.0, axle, S.WHEEL_Z), "X", [(-0.75, 0.05), (0.75, 0.05)], 8)
            for side in (-1, 1):
                b.box((side * 0.42, axle, S.WHEEL_Z + 0.08), (0.07, 1.10, 0.06))
        b.lathe((0.0, S.REAR_AXLE_Y, S.WHEEL_Z), "Y", [(-0.15, 0.10), (0.0, 0.17), (0.15, 0.10)], 10)
        mx, my, mz = S.MUFFLER
        b.lathe((mx, my, mz), "Y", [(-0.30, 0.06), (0.30, 0.06)], 8)
        for side in (-1, 1):
            for k in range(4):
                y = by0 - 0.10 - k * (by0 - by1 - 0.20) / 3
                b.box((side * (bh + 0.008), y, (floor + side_top) / 2), (0.016, 0.07, side_top - floor))
        tx, ty, tz = S.TOW_HOOK
        b.box((tx, ty + 0.10, tz), (0.10, 0.20, 0.08))
        b.lathe((tx, ty, tz), "X", [(-0.02, 0.05), (0.02, 0.05)], 8)
    return b.finish("Chassis", mat)


def build_cab(b, d, seg):
    """Hollow cab: solid below the floor, walls up to the window line, pillars and window frames,
    roof; bench, dashboard and steering wheel inside. Pieces overlap by a centimetre so that no
    two faces lie in one plane (those bake black)."""
    cz0, cz1, cz2 = S.CAB_Z
    h, rear, w, floor, roof = S.CAB_HALF, S.CAB_REAR, S.CAB_WALL, S.CAB_FLOOR, S.ROOF_IN_Z
    front = S.cab_front
    b.loft([plan_ring(z, front(z), rear, h) for z in (cz0, floor - 0.003)])
    # Walls from the floor to the window line, as a closed ring with an inner face.
    outer = [plan_ring(z, front(z), rear, h) for z in (floor, cz1)]
    inner = [plan_ring(z, front(z) - w, rear + w, h - w, 0.04) for z in (cz1, floor)]
    b.loft(outer + inner, closed=True)
    # Roof from just above the windows.
    levels = [(roof, h, 0.0), (cz2 - 0.07, h, 0.0), (cz2, h - 0.06, 0.05)]
    b.loft([plan_ring(z, front(z) - inset, rear + inset, half) for z, half, inset in levels])
    z0, z1 = cz1 - 0.01, roof + 0.01

    def front_piece(x0, x1, za, zb):
        """Part of the leaning front between za and zb, wall thick."""
        b.prism([(front(za), za), (front(za) - w, za), (front(zb) - w, zb), (front(zb), zb)], x0, x1)

    wz0, wz1 = S.WINDSCREEN_Z
    px = S.WINDSCREEN_PANES[1][1]
    for side in (-1, 1):
        lo, hi = sorted((side * px, side * (h - 0.05)))
        front_piece(lo, hi, z0, z1)                                  # windscreen pillar
        lo, hi = sorted((side * (h - w), side * h))
        sy0, sy1, sz0, sz1 = S.SIDE_WINDOW
        b.prism([(sy0, z0), (front(z0) - 0.05, z0), (front(z1) - 0.05, z1), (sy0, z1)], lo, hi)  # front of door
        b.box((side * (h - w / 2), (sy1 + rear + 0.05) / 2, (z0 + z1) / 2), (w, sy1 - rear - 0.05, z1 - z0))
        b.box((side * (h - w / 2), (sy0 + sy1) / 2, (sz1 + z1) / 2), (w, sy0 - sy1, z1 - sz1))  # over the window
        # Corner posts in the cut corners of the plan.
        b.strut((side * (h - 0.025), front(z0) - 0.025, z0), (side * (h - 0.025), front(z1) - 0.025, z1), 0.05)
        b.strut((side * (h - 0.025), rear + 0.025, z0), (side * (h - 0.025), rear + 0.025, z1), 0.05)
    front_piece(-px, px, z0, wz0)                                    # under the windscreen
    front_piece(-px, px, wz1, z1)                                    # over the windscreen
    b.box((0.0, rear + w / 2, (z0 + z1) / 2), (2 * (h - 0.05), w, z1 - z0))  # rear wall
    # Inside: bench with its back, dashboard, steering wheel on the left.
    b.box((0.0, rear + 0.42, floor + 0.18), (2 * (h - w) - 0.04, 0.46, 0.12))
    b.box((0.0, rear + 0.11, floor + 0.47), (2 * (h - w) - 0.04, 0.10, 0.50))
    b.box((0.0, S.CAB_FRONT - w - 0.07, cz1 - 0.10), (2 * (h - w) - 0.04, 0.14, 0.18))
    if d >= 1:
        wx, wy, wz = S.STEERING
        b.lathe((wx, wy, wz), "Y", [(-0.012, 0.20), (0.012, 0.20)], max(10, seg))
        b.strut((wx, wy, wz), (wx, S.CAB_FRONT - w - 0.10, cz1 - 0.12), 0.04)


def panes(chassis):
    """See-through windscreen (two panes leaning with the cab front) and cab side windows."""
    vitre = glass.material(S.STEM, os.path.join(OUT, "textures"))
    wz0, wz1 = S.WINDSCREEN_Z
    inset = S.CAB_WALL / 2
    quads = []
    for x0, x1 in S.WINDSCREEN_PANES:
        y0, y1 = S.cab_front(wz0) - inset, S.cab_front(wz1) - inset
        quads.append([(x1, y0, wz0), (x0, y0, wz0), (x0, y1, wz1), (x1, y1, wz1)])  # faces forward
    sy0, sy1, _, sz1 = S.SIDE_WINDOW
    for side, facing in ((1, "+X"), (-1, "-X")):
        x = side * (S.CAB_HALF - inset)
        quads.append(glass.rect(x, x, sy1, sy0, S.CAB_Z[1], sz1, facing))
    glass.add_panes("Cabine", quads, vitre, chassis)


def build_wheels(cfg, mat):
    seg, d = cfg["seg"], cfg["detail"]
    for name, side in (("Roue_Droite_01", 1), ("Roue_Gauche_01", -1)):
        c = Vector((side * S.FRONT_X, S.FRONT_AXLE_Y, S.WHEEL_Z))
        b = Builder()
        W.tyre(b, c, S.TYRE_W, seg, d, side)
        b.finish(name, mat, c, None, sharp=60)
    # Rear axle: twin tyres on each side, the outer one with the visible disc and hub.
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
    panes(chassis)
    build_wheels(cfg, main)
    helper("Driver", S.DRIVER, chassis)
    helper("Remorque_1", S.TOW_HOOK, chassis)
    helper("Fx_Stress_01", S.FX_STRESS[0], chassis)
    helper("Fx_Stress_02", S.FX_STRESS[1], chassis)
    for side, letter in ((1, "D"), (-1, "G")):
        helper("FX_Fumee_Roue_%s1" % letter, (side * S.REAR_X[1], S.REAR_AXLE_Y, 0.0), None)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not glass.is_glass(o)]
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
