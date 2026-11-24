"""Build the TK-3 or TKS tankette in High, Mid and Low versions.

  set TK_VARIANT=tk3   or   set TK_VARIANT=tks
  blender --background --factory-startup --python build_tk.py -- <output_dir>

Same object names and hierarchy as the 7TP (see docs/WTYCZKA.md). The fixed machine gun
mount is Tourelle_01, so the game can traverse and elevate it within the unit's limits.
Wheels are numbered from the front drive sprocket (1) through four road wheels (2-5) to the
rear idler (6).
"""

import math
import os
import sys

import addon_utils
import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_tk as S  # noqa: E402

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
os.makedirs(OUT, exist_ok=True)

LODS = {
    "Low": {"wheels": False, "detail": 0, "seg": 5, "track": 12, "limit": 500},
    "Mid": {"wheels": True, "detail": 1, "seg": 8, "track": 30, "limit": 2000},
    "High": {"wheels": True, "detail": 2, "seg": 12, "track": 64, "limit": 7000},
}


def circle(axis, center, radius, seg, offset, phase=0.0):
    points = []
    for i in range(seg):
        a = phase + math.tau * i / seg
        u, v = radius * math.cos(a), radius * math.sin(a)
        if axis == "X":
            points.append((center[0] + offset, center[1] + u, center[2] + v))
        elif axis == "Y":
            points.append((center[0] + u, center[1] + offset, center[2] + v))
        else:
            points.append((center[0] + u, center[1] + v, center[2] + offset))
    return points


class Builder:
    def __init__(self):
        self.bm = bmesh.new()

    def loft(self, rings, closed=False):
        verts = [[self.bm.verts.new(p) for p in ring] for ring in rings]
        pairs = list(zip(verts, verts[1:]))
        if closed:
            pairs.append((verts[-1], verts[0]))
        for a, b in pairs:
            n = len(a)
            for i in range(n):
                j = (i + 1) % n
                self.bm.faces.new((a[i], a[j], b[j], b[i]))
        if not closed:
            self.bm.faces.new(verts[0])
            self.bm.faces.new(verts[-1])

    def lathe(self, center, axis, profile, seg, phase=0.0):
        self.loft([circle(axis, center, r, seg, off, phase) for off, r in profile])

    def box(self, center, size):
        x, y, z = center
        a, b, c = size[0] / 2, size[1] / 2, size[2] / 2
        rect = [(-a, -b), (a, -b), (a, b), (-a, b)]
        self.loft([[(x + p, y + q, z + h) for p, q in rect] for h in (-c, c)])

    def prism(self, points, x0, x1):
        self.loft([[(x, y, z) for y, z in points] for x in (x0, x1)])

    def strut(self, start, end, width, height=None):
        height = height or width
        a, b = Vector(start), Vector(end)
        direction = (b - a).normalized()
        helper_axis = Vector((1, 0, 0)) if abs(direction.x) < 0.9 else Vector((0, 0, 1))
        u = direction.cross(helper_axis).normalized() * width / 2
        v = direction.cross(u).normalized() * height / 2
        corners = [u + v, -u + v, -u - v, u - v]
        self.loft([[tuple(p + c) for c in corners] for p in (a, b)])

    def wheel_ring(self, center, radius, inner, width, teeth=0, seg=16):
        count = teeth * 2 if teeth else seg
        outer_ring = []
        for i in range(count):
            r = radius if not teeth or i % 2 == 0 else radius * 0.88
            a = math.tau * i / count
            outer_ring.append((r * math.cos(a), r * math.sin(a)))
        inner_ring = [(inner * math.cos(math.tau * i / count), inner * math.sin(math.tau * i / count))
                      for i in range(count)]
        w = width / 2
        rings = [[(center[0] + o, center[1] + u, center[2] + v) for u, v in profile]
                 for o, profile in ((-w, outer_ring), (w, outer_ring), (w, inner_ring), (-w, inner_ring))]
        self.loft(rings, closed=True)

    def finish(self, name, material, pivot=Vector(), parent=None, sharp=40):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        bmesh.ops.translate(self.bm, verts=self.bm.verts, vec=-Vector(pivot))
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        mesh.materials.append(material)
        mesh.shade_smooth()
        mesh.set_sharp_from_angle(angle=math.radians(sharp))
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        place(obj, pivot, parent)
        return obj


def place(obj, pivot, parent):
    pivot = Vector(pivot)
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.location = pivot - parent.matrix_world.translation
    else:
        obj.location = pivot
    bpy.context.view_layer.update()


def helper(name, pivot, parent, size=0.05):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "CUBE"
    obj.empty_display_size = size
    bpy.context.collection.objects.link(obj)
    place(obj, pivot, parent)
    return obj


def material_main():
    mat = bpy.data.materials.new("M_TK")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.13, 0.15, 0.07, 1)
    bsdf.inputs["Roughness"].default_value = 0.62
    return mat


def material_track(name, tag):
    mat = bpy.data.materials.new(name)
    mat["eug_tag"] = tag
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.035, 0.032, 0.03, 1)
    return mat


# ---------------------------------------------------------------- tracks

def convex_hull(points):
    points = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def half(sequence):
        out = []
        for p in sequence:
            while len(out) >= 2 and cross(out[-2], out[-1], p) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]

    return half(points) + half(reversed(points))


def track_path(count):
    samples = []
    for y, z, r in S.WHEELS:
        for i in range(64):
            a = math.tau * i / 64
            samples.append((y + (r + S.TRACK_T / 2) * math.cos(a), z + (r + S.TRACK_T / 2) * math.sin(a)))
    hull = convex_hull(samples)
    lengths = [math.dist(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]
    total = sum(lengths)
    path = []
    index, walked = 0, 0.0
    for k in range(count):
        target = total * k / count
        while walked + lengths[index] < target:
            walked += lengths[index]
            index += 1
        t = (target - walked) / lengths[index]
        a, b = hull[index], hull[(index + 1) % len(hull)]
        path.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return path, total


def build_track(name, side, count, material, parent, moving):
    path, _ = track_path(count)
    x = side * S.TRACK_X
    w = S.TRACK_W / 2
    rings = []
    for i, p in enumerate(path):
        prev, nxt = path[i - 1], path[(i + 1) % count]
        dy, dz = nxt[0] - prev[0], nxt[1] - prev[1]
        length = math.hypot(dy, dz)
        ny, nz = dz / length, -dy / length
        o = (p[0] + ny * S.TRACK_T / 2, p[1] + nz * S.TRACK_T / 2)
        n = (p[0] - ny * S.TRACK_T / 2, p[1] - nz * S.TRACK_T / 2)
        rings.append([(x - w, *o), (x + w, *o), (x + w, *n), (x - w, *n)])

    bm = bmesh.new()
    verts = [[bm.verts.new(v) for v in ring] for ring in rings]
    uv_layer = bm.loops.layers.uv.new("UVMap")
    # Game convention: U across the track, V along it, always inside 0-1. One tile spans two segments.
    strips = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.9), (0.9, 1.0)]
    for i in range(count):
        j = (i + 1) % count
        along0 = (i % 2) / 2
        along1 = along0 + 0.5
        for s in range(4):
            q = (s + 1) % 4
            face = bm.faces.new((verts[i][s], verts[j][s], verts[j][q], verts[i][q]))
            across0, across1 = strips[s]
            for loop, uv in zip(face.loops, ((across0, along0), (across0, along1), (across1, along1), (across1, along0))):
                loop[uv_layer].uv = uv
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    mesh.shade_smooth()
    mesh.set_sharp_from_angle(angle=math.radians(40))
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    place(obj, (0, 0, 0), parent)
    obj["moving_track"] = moving
    return obj


def skin_track(track, letter):
    """Rigid skin plan as vertex groups: road wheels at the bottom, Fake elsewhere."""
    groups = {"Fake": track.vertex_groups.new(name="Fake")}
    numbers = range(2, 2 + len(S.ROAD_Y))
    for number in numbers:
        groups[number] = track.vertex_groups.new(name="Roue_Elev_%s%d" % (letter, number))
    for vertex in track.data.vertices:
        target = "Fake"
        if vertex.co.z < 0.09:
            number, y = min(((n + 2, y) for n, y in enumerate(S.ROAD_Y)), key=lambda item: abs(item[1] - vertex.co.y))
            if abs(y - vertex.co.y) <= 0.17:
                target = number
        groups[target].add([vertex.index], 1.0, "REPLACE")


# ---------------------------------------------------------------- hull

def fender_profile(steps):
    cy, cz, r = S.FENDER_ARC
    a0, a1 = S.FENDER_ARC_DEG
    outer = []
    for i in range(steps + 1):
        a = math.radians(a1 + (a0 - a1) * i / steps)
        outer.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    outer += S.FENDER_REAR
    inner = [(y, z - 0.014) for y, z in outer]
    return outer + inner[::-1]


def build_suspension(b, side, detail):
    """External girder carrying the leaf spring, the wheel pairs and the idler."""
    gx = side * S.GIRDER_X
    y0, y1 = S.GIRDER_Y
    gz = S.GIRDER_Z
    # Main girder, a flat bar on edge.
    b.prism([(y0, gz - 0.045), (y0, gz + 0.045), (y1, gz + 0.055), (y1, gz - 0.035)], gx - 0.016, gx + 0.016)
    # Idler arm from the girder end to the idler hub.
    iy, iz, _ = S.IDLER
    b.strut((gx, y1 + 0.05, gz), (gx, iy, iz), 0.03, 0.06)
    # Upper diagonal bar under the return run, with posts at both ends.
    (ry0, rz0), (ry1, rz1) = S.RAIL
    b.strut((gx, ry0, rz0), (gx, ry1, rz1), 0.03, 0.05)
    b.prism([(ry0 + 0.03, rz0 + 0.03), (ry0 + 0.06, gz - 0.04), (ry0 - 0.03, gz - 0.04), (ry0 - 0.05, rz0 + 0.03)],
            gx - 0.014, gx + 0.014)
    b.strut((gx, ry1, rz1), (gx, ry1 - 0.02, gz + 0.04), 0.03, 0.04)
    # Brackets tying the girder to the hull side above the tracks.
    inner = side * (S.HULL_HALF_WIDTH + 0.01)
    for y, z in ((ry0, rz0), (ry1, rz1)):
        b.strut((inner, y, z + 0.02), (gx, y, z), 0.04, 0.035)
    if detail < 2:
        return
    # Leaf spring between the wheel pairs, centre clamped to a bracket on the bar.
    w = S.ROAD_Y
    front, rear = (w[0] + w[1]) / 2, (w[2] + w[3]) / 2
    mid = (front + rear) / 2
    half = (front - rear) / 2
    for k, fraction in enumerate((1.0, 0.80, 0.60, 0.40)):
        z0 = 0.335 + k * 0.015
        span = half * fraction
        leaf = []
        for i in range(7):
            t = (-1 + 2 * i / 6) * fraction
            leaf.append((mid + half * t, z0 + 0.05 * (1 - t * t)))
        top = [(y, z + 0.014) for y, z in reversed(leaf)]
        b.prism(leaf + top, gx - 0.04, gx + 0.04)
    b.box((gx, mid, 0.42), (0.10, 0.07, 0.07))
    b.strut((gx, mid, 0.44), (gx, mid + 0.02, 0.50), 0.05, 0.05)
    for y in (mid - half, mid + half):
        b.strut((gx, y, 0.34), (gx, y, S.ROAD_Z + 0.04), 0.04, 0.04)
    # Wheel pairs: a link bar outside the wheels joining the two hubs.
    for a, c in S.WHEEL_PAIRS:
        ya, yc = w[a], w[c]
        link = side * (S.TRACK_X + 0.062)
        b.prism([(ya, S.ROAD_Z - 0.022), (ya, S.ROAD_Z + 0.022), ((ya + yc) / 2, S.ROAD_Z + 0.04),
                 (yc, S.ROAD_Z + 0.022), (yc, S.ROAD_Z - 0.022), ((ya + yc) / 2, S.ROAD_Z - 0.03)],
                link - 0.012, link + 0.012)
        b.box((side * (S.TRACK_X + 0.07), (ya + yc) / 2, S.ROAD_Z + 0.075), (0.05, 0.08, 0.07))


def build_chassis(cfg, mat):
    detail = cfg["detail"]
    b = Builder()
    b.prism(S.HULL_LOWER, -S.HULL_HALF_WIDTH, S.HULL_HALF_WIDTH)
    steps = {0: 2, 1: 4, 2: 7}[detail]
    for side in (-1, 1):
        x0, x1 = sorted((side * (S.HULL_HALF_WIDTH - 0.01), side * S.FENDER_OUTER))
        b.prism(fender_profile(steps), x0, x1)
    b.loft([S.ring_points(plan, z) for z, plan in S.SUPER_RINGS])

    if detail >= 1:
        for side in (-1, 1):
            build_suspension(b, side, detail)
            # Final drive housing from the hull side to the sprocket.
            sy, sz, _ = S.SPROCKET
            b.lathe((side * (S.HULL_HALF_WIDTH + 0.04), sy, sz), "X", [(-0.05, 0.085), (0.05, 0.075)], 8)
        # Muffler across the rear with its exhaust pipe.
        mx, my, mz = S.MUFFLER
        seg = max(cfg["seg"], 8)
        b.lathe((mx, my, mz), "X", [(-0.17, 0.045), (-0.15, 0.085), (0.15, 0.085), (0.17, 0.05)], seg)
        b.strut((mx - 0.12, my + 0.02, mz - 0.07), (mx - 0.16, my + 0.12, S.SUPER_RINGS[2][0] - 0.01), 0.045)
        # Roof hatches, one per crew member.
        for x in (-0.28, 0.28):
            b.box((x, -0.05, S.ROOF_Z + 0.012), (0.36, 0.42, 0.024))

    if detail >= 2:
        mx, my, mz = S.MUFFLER
        for x in (mx - 0.10, mx + 0.10):
            b.strut((x, my, mz - 0.08), (x, my + 0.02, S.SUPER_RINGS[2][0] - 0.005), 0.02, 0.035)
        b.lathe((mx + 0.17, my, mz), "X", [(0.0, 0.03), (0.06, 0.028)], 6)
        # Tow eyes, front and rear.
        for side in (-1, 1):
            for y, z in ((1.25, 0.53), (-1.30, 0.52)):
                b.lathe((side * 0.62, y, z), "X", [(-0.012, 0.04), (0.012, 0.04)], 8)
            b.box((side * 0.58, 1.02, 0.74), (0.12, 0.08, 0.012))
        # Headlamp on the left front of the deck.
        b.lathe((-0.42, 1.03, DECK_LAMP_Z), "Y", [(-0.05, 0.05), (0.03, 0.065), (0.04, 0.05)], 8)
        # Engine deck: radiator grille and access hatch between the superstructure and the rear plate.
        rear_deck_y = S.SUPER_RINGS[2][1][-1][0]
        engine_z = S.SUPER_RINGS[1][0]
        if S.VARIANT == "tks":
            b.box((0.0, (rear_deck_y + S.SUPER_RINGS[1][1][-1][0]) / 2, S.SUPER_RINGS[2][0] + 0.012), (0.70, 0.16, 0.024))
            # Periscope on the driver's side of the roof.
            px, py = -0.28, 0.16
            b.box((px, py, S.ROOF_Z + 0.02), (0.12, 0.10, 0.04))
            b.prism([(py - 0.05, S.ROOF_Z + 0.04), (py + 0.05, S.ROOF_Z + 0.04), (py + 0.02, S.ROOF_Z + 0.05),
                     (py - 0.05, S.ROOF_Z + 0.05)], px - 0.06, px + 0.06)
        else:
            b.box((0.0, (rear_deck_y + S.SUPER_RINGS[0][1][-1][0]) / 2 - 0.02, engine_z + 0.035), (0.64, 0.18, 0.024))
            # Raised hatch rims on the TK-3 roof.
            for x in (-0.28, 0.28):
                b.box((x, 0.10, S.ROOF_Z + 0.035), (0.10, 0.06, 0.03))
        # Vision slits on the front plate.
        front = S.SUPER_RINGS[3][1][0][0]
        for x in (-0.30, 0.10):
            b.box((x, front + 0.012, S.SUPER_RINGS[3][0] - 0.06), (0.16, 0.03, 0.035))
    return b.finish("Chassis", mat)


DECK_LAMP_Z = S.DECK_Z + 0.07


# ---------------------------------------------------------------- gun

def build_gun(cfg, mat, chassis):
    detail = cfg["detail"]
    mount = Vector(S.MOUNT)
    seg = max(cfg["seg"], 6)
    b = Builder()
    if S.MANTLET == "ball":
        if detail >= 1:
            b.lathe(mount, "Y", [(-0.05, 0.06), (-0.03, 0.095), (0.0, 0.105), (0.03, 0.095), (0.055, 0.06)], seg)
            b.lathe(mount, "Y", [(-0.03, 0.14), (0.0, 0.14)], seg)
        else:
            b.lathe(mount, "Y", [(-0.04, 0.10), (0.05, 0.07)], 5)
    else:
        if detail >= 1:
            b.box((mount.x, mount.y - 0.01, mount.z - 0.03), (0.22, 0.12, 0.30))
            b.lathe((mount.x, mount.y + 0.05, mount.z), "Y", [(0.0, 0.07), (0.03, 0.06)], seg)
        else:
            b.box((mount.x, mount.y, mount.z - 0.03), (0.22, 0.12, 0.28))
    turret = b.finish("Tourelle_01", mat, mount, chassis)

    b = Builder()
    if detail >= 1:
        b.lathe(mount, "Y", [(0.02, 0.045), (0.06, 0.04)], seg)
        sight = Vector((mount.x, mount.y, mount.z - 0.06))
        b.lathe(sight, "Y", [(0.04, 0.018), (0.30, 0.018), (0.31, 0.024), (0.34, 0.024)], 6)
        b.strut((mount.x, mount.y + 0.10, mount.z - 0.03), (mount.x, mount.y + 0.10, mount.z - 0.05), 0.02)
    else:
        b.box((mount.x, mount.y + 0.04, mount.z), (0.06, 0.05, 0.06))
    axis = b.finish("Axe_Canon_01", mat, mount, turret)

    b = Builder()
    length = S.MUZZLE_Y - mount.y
    if detail >= 2:
        profile = [(0.04, 0.032), (0.10, 0.032), (0.11, 0.026), (0.13, 0.032), (0.16, 0.026), (0.18, 0.032),
                   (0.21, 0.026), (0.23, 0.032), (0.26, 0.032), (0.27, 0.015), (length - 0.09, 0.013),
                   (length - 0.085, 0.021), (length - 0.05, 0.021), (length - 0.045, 0.013), (length, 0.013)]
    elif detail == 1:
        profile = [(0.04, 0.03), (0.26, 0.03), (0.27, 0.015), (length, 0.013)]
    else:
        profile = [(0.04, 0.026), (length, 0.014)]
    b.lathe(mount, "Y", profile, max(5, cfg["seg"] - 4))
    canon = b.finish("Canon_01", mat, mount, axis)
    helper("Fx_tourelle1_tir_01", (mount.x, S.MUZZLE_Y + 0.01, mount.z), canon)
    return turret


# ---------------------------------------------------------------- wheels

def wheel_shape(b, center, kind, cfg):
    seg = cfg["seg"]
    high = cfg["detail"] >= 2
    outer = 1 if center[0] > 0 else -1
    if kind == "sprocket":
        r = S.SPROCKET[2]
        if high:
            b.wheel_ring(center, r, 0.07, 0.05, teeth=13)
            b.lathe(center, "X", [(-0.05, 0.07), (0.05, 0.07)], 10)
            b.lathe((center[0] + outer * 0.04, center[1], center[2]), "X", [(-0.02, 0.055), (0.02, 0.04)], 8)
        else:
            b.lathe(center, "X", [(-0.03, r), (0.03, r)], seg + 2)
    elif kind == "idler":
        r = S.IDLER[2]
        if high:
            b.wheel_ring(center, r, r * 0.84, 0.05, seg=20)
            b.lathe(center, "X", [(-0.04, 0.045), (0.04, 0.045)], 8)
            for i in range(8):
                a = math.tau * (i + 0.5) / 8
                d = Vector((0, math.cos(a), math.sin(a)))
                b.strut(Vector(center) + d * 0.04, Vector(center) + d * (r * 0.84 + 0.004), 0.018, 0.014)
        else:
            b.lathe(center, "X", [(-0.03, r), (0.03, r)], seg + 2)
    elif high:
        r = S.ROAD_R
        b.lathe(center, "X", [(-0.042, r * 0.62), (-0.036, r * 0.95), (0.0, r), (0.036, r * 0.95),
                               (0.042, r * 0.62)], 14)
        b.lathe((center[0] + outer * 0.045, center[1], center[2]), "X", [(-0.005, 0.045), (0.02, 0.03)], 8)
    else:
        b.lathe(center, "X", [(-0.042, S.ROAD_R), (0.042, S.ROAD_R)], seg)


def build_wheels(cfg, mat, chassis):
    kinds = ["sprocket"] + ["road"] * len(S.ROAD_Y) + ["idler"]
    for side, letter in ((1, "D"), (-1, "G")):
        for number, (kind, wheel) in enumerate(zip(kinds, S.WHEELS), 1):
            center = Vector((side * S.TRACK_X, wheel[0], wheel[1]))
            elev = helper("Roue_Elev_%s%d" % (letter, number), center, chassis, 0.04)
            b = Builder()
            wheel_shape(b, center, kind, cfg)
            b.finish("Roue_%s%d" % (letter, number), mat, center, elev, sharp=62 if kind == "road" else 40)


# ---------------------------------------------------------------- scene

def unwrap(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")


def report(name, limit):
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    size = [max(c[i] for c in corners) - min(c[i] for c in corners) for i in range(3)]
    total = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    print("REPORT %s %s tris=%d limit=%d objects=%d width=%.3f length=%.3f height=%.3f" % (
        S.VARIANT, name, total, limit, len(meshes), size[0], size[1], size[2]))


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

    chassis = build_chassis(cfg, main)
    build_gun(cfg, main, chassis)
    if cfg["wheels"]:
        build_wheels(cfg, main, chassis)
    track_d = build_track("Chenille_Droite_01", 1, cfg["track"], mat_d, chassis, moving)
    track_g = build_track("Chenille_Gauche_01", -1, cfg["track"], mat_g, chassis, moving)

    helper("Fake", (0, 0, 0.4), chassis)
    helper("Fx_Stress_01", (0, -0.1, S.ROOF_Z + 0.06), chassis)
    helper("Fx_Stress_02", (S.MOUNT[0], S.MOUNT[1] - 0.1, S.MOUNT[2] + 0.15), chassis)
    helper("FX_Fumee_Chenille_D1", (S.TRACK_X, -1.25, 0.06), chassis)
    helper("FX_Fumee_Chenille_G1", (-S.TRACK_X, -1.25, 0.06), chassis)
    if cfg["wheels"]:
        skin_track(track_d, "D")
        skin_track(track_g, "G")

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    unwrap([o for o in meshes if not (moving and o.name.startswith("Chenille"))])
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
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.5
    sun = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    views = {"geo_przod": ("PERSP", (3.5, 3.7, 1.6), (0, 0.1, 0.62), 50),
             "geo_bok": ("ORTHO", (8, 0, 0.66), (0, 0, 0.66), 3.0),
             "geo_tyl": ("PERSP", (-3.0, -4.0, 1.8), (0, -0.1, 0.62), 50),
             "geo_wozek": ("PERSP", (2.4, 0.6, 0.45), (0.85, -0.05, 0.28), 40)}
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


for lod_name, lod_cfg in LODS.items():
    build(lod_name, lod_cfg)
if not os.environ.get("TK_NO_RENDER"):
    render_clay()
print("BUILD_DONE")
