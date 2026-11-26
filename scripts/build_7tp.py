"""Build the 7TP from the dimensioned drawings, in two variants.

  set TP_VARIANT=jw   single turret, Bofors 37 mm
  set TP_VARIANT=dw   two turrets, one wz. 30 machine gun each
  blender --background --factory-startup --python build_7tp.py -- <output_dir>

Names and hierarchy follow the Modding Manual and the game's own tanks.
"""

import math
import os
import sys

import addon_utils
import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec_7tp import *  # noqa: E402,F401,F403
import spec_7tp as S  # noqa: E402

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
os.makedirs(OUT, exist_ok=True)

LODS = {
    "Low": {"wheels": False, "detail": 0, "seg": 5, "track": 14, "limit": 500},
    "Mid": {"wheels": True, "detail": 1, "seg": 7, "track": 28, "limit": 2000},
    "High": {"wheels": True, "detail": 2, "seg": 10, "track": 56, "limit": 7000},
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


def fender_profile(steps):
    outer, inner = [], []
    for center, start, end in ((S.FENDER_Y, 12, 90), (-S.FENDER_Y, 90, 168)):
        for i in range(steps + 1):
            a = math.radians(start + (end - start) * i / steps)
            outer.append((center + S.FENDER_R * math.cos(a), S.FENDER_Z + S.FENDER_R * math.sin(a)))
            inner.append((center + (S.FENDER_R - 0.018) * math.cos(a), S.FENDER_Z + (S.FENDER_R - 0.018) * math.sin(a)))
    return outer + inner[::-1]


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

    def spoked(self, center, radius, inner, width, spokes, teeth=0, seg=16):
        count = teeth * 2 if teeth else seg
        outer_ring = []
        for i in range(count):
            r = radius if not teeth or i % 2 == 0 else radius * 0.90
            a = math.tau * i / count
            outer_ring.append((r * math.cos(a), r * math.sin(a)))
        inner_ring = [(inner * math.cos(math.tau * i / count), inner * math.sin(math.tau * i / count))
                      for i in range(count)]
        w = width / 2
        rings = [[(center[0] + o, center[1] + u, center[2] + v) for u, v in profile]
                 for o, profile in ((-w, outer_ring), (w, outer_ring), (w, inner_ring), (-w, inner_ring))]
        self.loft(rings, closed=True)
        self.lathe(center, "X", [(-w * 1.5, 0.07), (w * 1.5, 0.07)], 8)
        for i in range(spokes):
            a = math.tau * (i + 0.5) / spokes
            d = Vector((0, math.cos(a), math.sin(a)))
            self.strut(Vector(center) + d * 0.055, Vector(center) + d * (inner + 0.005), 0.04, 0.028)

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


def helper(name, pivot, parent, size=0.06):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "CUBE"
    obj.empty_display_size = size
    bpy.context.collection.objects.link(obj)
    place(obj, pivot, parent)
    return obj


def material_main():
    mat = bpy.data.materials.new("M_7TP")
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
    circles = list(S.WHEELS) + [(y, S.RETURN_Z, S.RETURN_R) for y in S.RETURN_Y]
    samples = []
    for y, z, r in circles:
        for i in range(48):
            a = math.tau * i / 48
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
    return path


def build_track(name, side, count, material, parent, moving):
    path = track_path(count)
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
    for number in range(2, 10):
        groups[number] = track.vertex_groups.new(name="Roue_Elev_%s%d" % (letter, number))
    for vertex in track.data.vertices:
        target = "Fake"
        if vertex.co.z < 0.12:
            number, y = min(((n + 2, y) for n, y in enumerate(S.ROAD_Y)),
                            key=lambda item: abs(item[1] - vertex.co.y))
            if abs(y - vertex.co.y) <= 0.20:
                target = number
        groups[target].add([vertex.index], 1.0, "REPLACE")


def build_bogie(b, side, index):
    """Vickers bogie from the 7TP drawing.

    A carrier tube holds a heavy curved rocker running forward to one wheel truck and a
    quarter-elliptic leaf spring running to the other. Each truck is a cast link on the outer
    face of two twin road wheels.

    The two bogies are mirror images, as on the side drawing: the front bogie has its rocker
    forward and its spring rearward, the rear bogie the other way round, so both springs point
    to the middle of the tank. Shapes are written in u, the distance from the carrier tube
    towards the rocker.
    """
    x = side * S.TRACK_X
    yb = S.BOGIE_Y[index]
    w = S.ROAD_Y[index * 4:index * 4 + 4]
    pairs = ((w[0] + w[1]) / 2, (w[2] + w[3]) / 2)
    sign = 1 if index == 0 else -1
    front, rear = pairs if index == 0 else pairs[::-1]  # rocker pair, spring pair

    def y_of(u):
        return yb + sign * u

    def outline(points):
        """(u, z) outline to (y, z), keeping the winding when the bogie is mirrored."""
        out = [(y_of(u), z) for u, z in points]
        return out if sign > 0 else out[::-1]

    pin_z = S.ROAD_Z + 0.06

    # Carrier tube with its clamp, from the hull side to the rocker.
    tube = (side * 0.96, yb, 0.50)
    near, far = (-0.15, 0.02) if side > 0 else (-0.02, 0.15)
    profile = [(near, 0.058), (far, 0.058)] if side > 0 else [(near, 0.058), (far, 0.058)]
    collar = (0.03, 0.13) if side > 0 else (-0.13, -0.03)
    b.lathe(tube, "X", [profile[0], profile[1], (collar[0], 0.095), (collar[1], 0.095)] if side > 0 else
            [(collar[0], 0.095), (collar[1], 0.095), (near + 0.13, 0.058), (0.15, 0.058)], 8)

    # Rocker: heavy arched casting from the tube down to the outer truck.
    d = (front - yb) * sign
    rocker = [
        (-0.07, 0.535), (0.05, 0.585), (0.48 * d, 0.565), (0.80 * d, 0.45), (d + 0.03, pin_z + 0.05),
        (d - 0.03, pin_z - 0.01), (0.62 * d, 0.30), (0.28 * d, 0.40), (-0.05, 0.44),
    ]
    b.prism(outline(rocker), x - 0.058, x + 0.058)

    # Quarter-elliptic spring to the inner truck: longest leaf at the bottom, shorter above it.
    length = (yb - rear) * sign
    for k, fraction in enumerate((1.0, 0.76, 0.52)):
        z0 = 0.392 + k * 0.032
        tail = 0.09
        tip = -length * fraction
        mid = (tail + tip) / 2

        def drop(u):
            s = max(0.0, -u / length)
            return 0.11 * s * s
        leaf = [(tail, z0), (mid, z0 - drop(mid)), (tip, z0 - drop(tip)),
                (tip, z0 - drop(tip) + 0.03), (mid, z0 - drop(mid) + 0.03), (tail, z0 + 0.03)]
        b.prism(outline(leaf), x - 0.07, x + 0.07)
    b.strut((x, y_of(0.03), 0.375), (x, y_of(-length + 0.05), 0.27), 0.09, 0.016)
    b.box((x, y_of(-0.02), 0.47), (0.15, 0.10, 0.09))
    b.strut((x, rear, 0.30), (x, rear, pin_z), 0.05, 0.05)

    # Wheel trucks: cast links outside the wheels, with the central pivot raised.
    link_x = x + side * 0.118
    for first, second in ((w[0], w[1]), (w[2], w[3])):
        middle = (first + second) / 2
        link = [(first, S.ROAD_Z + 0.03), (middle, pin_z + 0.035), (second, S.ROAD_Z + 0.03),
                (second, S.ROAD_Z - 0.03), (middle, pin_z - 0.05), (first, S.ROAD_Z - 0.03)]
        b.prism(link, link_x - 0.014, link_x + 0.014)
        b.lathe((link_x, middle, pin_z), "X", [(-0.015, 0.036), (0.015, 0.036)], 6)


def return_roller(b, center, side, detail):
    """Disc roller under the top run of the track, as in the photographs: a rubber-rimmed
    wheel with a dished face and a raised hub on the outer side. Mid keeps a plain disc."""
    r, w = S.RETURN_R, 0.10
    if detail >= 2:
        profile = [(-w, r), (w * 0.8, r), (w, r * 0.86), (w - 0.022, r * 0.76), (w - 0.022, r * 0.34),
                   (w + 0.006, r * 0.27)]
        seg = 10
    else:
        profile = [(-w, r), (w, r)]
        seg = 8
    b.lathe(center, "X", [(side * offset, radius) for offset, radius in profile], seg)


def build_chassis(cfg, mat):
    detail = cfg["detail"]
    b = Builder()
    b.prism(S.HULL_LOWER, -S.HULL_HALF_WIDTH, S.HULL_HALF_WIDTH)
    b.prism(S.HULL_UPPER, -S.UPPER_HALF_WIDTH, S.UPPER_HALF_WIDTH)
    steps = {0: 1, 1: 3, 2: 4}[detail]
    for side in (-1, 1):
        x0, x1 = sorted((side * S.HULL_HALF_WIDTH, side * 1.20))
        b.prism(fender_profile(steps), x0, x1)

    if detail >= 1:
        b.prism([(1.02, 1.08), (0.90, 1.36), (0.72, S.HULL_TOP - 0.02), (0.72, 1.12)], 0.06, 0.72)
        for side in (-1, 1):
            b.lathe((side * 0.86, S.SPROCKET[0], S.SPROCKET[1]), "X", [(-0.04, 0.22), (0.04, 0.22)], 10)
            for y in S.RETURN_Y:
                return_roller(b, (side * S.TRACK_X, y, S.RETURN_Z), side, detail)
        for x in (-0.36, 0.36):
            y0, z0, y1, z1 = -1.76, 1.42, -1.90, 1.17
            b.prism([(y0, z0), (y0 - 0.02, z0 + 0.01), (y1 - 0.02, z1 + 0.01), (y1, z1)], x - 0.31, x + 0.31)
        b.lathe((-0.02, -2.13, 0.80), "X", [(-0.60, 0.05), (-0.56, 0.09), (0.56, 0.09), (0.60, 0.05)], max(7, cfg["seg"]))

    if detail >= 2:
        for side in (-1, 1):
            build_bogie(b, side, 0)
            build_bogie(b, side, 1)
            b.box((side * 0.42, 2.03, 0.70), (0.07, 0.07, 0.08))
            b.box((side * 0.42, -2.03, 0.62), (0.07, 0.07, 0.08))
            b.strut((side * S.UPPER_HALF_WIDTH, 0.40, 1.36), (side * 1.02, 0.02, 1.12), 0.028)
            b.strut((side * S.UPPER_HALF_WIDTH, -0.86, 1.40), (side * 1.02, -1.22, 1.12), 0.028)
        b.box((0.98, 1.68, 1.18), (0.035, 0.035, 0.10))
        b.lathe((0.98, 1.68, 1.28), "Y", [(-0.07, 0.04), (0.01, 0.06), (0.07, 0.055)], 8)
        for x in (-0.36, 0.36):
            for i in range(6):
                t = (i + 0.5) / 6
                y = -1.785 - 0.125 * t
                z = 1.40 - 0.22 * t
                b.strut((x - 0.28, y, z), (x + 0.28, y, z), 0.022, 0.03)
        b.prism([(0.98, 1.34), (0.79, HULL_TOP + 0.015), (0.76, HULL_TOP + 0.03), (0.95, 1.36)], 0.12, 0.66)
        b.box((0.39, 0.975, 1.20), (0.22, 0.03, 0.022))
        b.box((0.0, -0.98, HULL_TOP + 0.015), (1.10, 0.74, 0.03))
        b.box((0.0, -1.48, HULL_TOP + 0.015), (0.82, 0.30, 0.03))
    elif detail == 1:
        for side in (-1, 1):
            # Mirrored like in High: the arch rises towards the outer end of each bogie.
            for yb, sign in zip(S.BOGIE_Y, (1, -1)):
                arch = [(yb + sign * u, z) for u, z in
                        ((-0.42, 0.26), (-0.05, 0.43), (0.05, 0.57), (0.28, 0.50), (0.42, 0.27), (0.22, 0.34))]
                arch = arch if sign > 0 else arch[::-1]
                b.prism(arch, side * S.TRACK_X - 0.06, side * S.TRACK_X + 0.06)
    return b.finish("Chassis", mat)


def build_turret_jw(cfg, mat, chassis):
    detail = cfg["detail"]
    data = S.TURRETS[1]
    tx, ty, tz = data["center"]
    b = Builder()
    if detail >= 1:
        plan = S.turret_plan_jw(13 if detail >= 2 else 8)
        rings = []
        for z, scale, clamp in ((tz + 0.04, 0.96, True), (1.66, 1.0, True), (1.69, 1.0, False), (S.ROOF_Z_JW, 0.90, False)):
            rings.append([(tx + x * scale, ty + (max(y, -0.38) if clamp else y) * scale, z) for x, y in plan])
        b.loft(rings)
        b.lathe((tx, ty, tz), "Z", [(0.0, 0.56), (0.045, 0.56), (0.05, 0.50)], cfg["seg"] + (6 if detail >= 2 else 3))
        b.box((tx + 0.03, ty - 0.34, S.ROOF_Z_JW + 0.012), (0.46, 0.44, 0.025))
        b.lathe((tx - 0.20, ty + 0.14, S.ROOF_Z_JW), "Z", [(0.0, 0.085), (0.05, 0.085)], 8)
    else:
        plan = [(0.32, 0.46), (0.50, 0.10), (0.42, -0.84), (-0.42, -0.84), (-0.50, 0.10), (-0.32, 0.46)]
        b.loft([[(tx + x * s, ty + y * s, z) for x, y in plan] for z, s in ((tz, 1.0), (S.ROOF_Z_JW, 0.90))])
    if detail >= 2:
        b.lathe((tx - 0.20, ty + 0.14, S.ROOF_Z_JW + 0.05), "Z", [(0.0, 0.05), (0.09, 0.042)], 8)
        b.box((tx - 0.20, ty + 0.16, S.ROOF_Z_JW + 0.115), (0.09, 0.10, 0.06))
        b.prism([(ty + 0.40, S.ROOF_Z_JW), (ty + 0.25, S.ROOF_Z_JW + 0.055), (ty + 0.10, S.ROOF_Z_JW + 0.055), (ty + 0.05, S.ROOF_Z_JW)],
                tx + 0.08, tx + 0.34)
        for side in (-1, 1):
            b.box((tx + side * 0.385, ty - 0.60, 1.77), (0.02, 0.22, 0.018))
    return b.finish("Tourelle_01", mat, data["center"], chassis)


def build_gun_jw(cfg, mat, turret):
    detail = cfg["detail"]
    data = S.TURRETS[1]
    mount = Vector(data["mount"])
    b = Builder()
    # Gun and machine gun sit side by side in two round armoured sleeves on the mantlet, the
    # machine gun on the left, as in the photographs and the drawing of the turret front.
    mg = (mount.x - 0.16, mount.y, mount.z - 0.04)
    if detail >= 2:
        b.box((mount.x, mount.y - 0.03, mount.z), (0.66, 0.08, 0.50))
        b.lathe(mount, "Y", [(0.01, 0.092), (0.25, 0.092), (0.27, 0.082), (0.27, 0.05)], 14)
        b.lathe(mg, "Y", [(0.01, 0.085), (0.25, 0.085), (0.27, 0.076), (0.27, 0.034), (0.245, 0.026)], 14)
    elif detail == 1:
        b.box((mount.x, mount.y - 0.03, mount.z), (0.66, 0.08, 0.50))
        b.lathe(mount, "Y", [(0.01, 0.092), (0.27, 0.085)], 8)
        b.lathe(mg, "Y", [(0.01, 0.085), (0.27, 0.078)], 8)
    else:
        b.box((mount.x - 0.05, mount.y + 0.10, mount.z - 0.02), (0.46, 0.34, 0.30))
    axis = b.finish("Axe_Canon_01", mat, mount, turret)

    b = Builder()
    length = data["muzzle_y"] - mount.y
    if detail >= 2:
        profile = [(0.28, 0.042), (0.72, 0.038), (0.74, 0.031), (length - 0.15, 0.028), (length - 0.14, 0.046),
                   (length - 0.01, 0.046), (length, 0.034)]
    elif detail == 1:
        profile = [(0.28, 0.038), (length - 0.14, 0.029), (length - 0.13, 0.044), (length, 0.044)]
    else:
        profile = [(0.25, 0.04), (length, 0.034)]
    b.lathe(mount, "Y", profile, max(6, cfg["seg"] - 1))
    canon = b.finish("Canon_01", mat, mount, axis)
    helper("Fx_tourelle1_tir_01", (mount.x, data["muzzle_y"] + 0.01, mount.z), canon)


def build_turret_dw(cfg, mat, chassis, number):
    """Vickers-type MG turret: cylinder, flat gun-shield box and a hinged roof flap."""
    detail = cfg["detail"]
    data = S.TURRETS[number]
    tx, ty, tz = data["center"]
    side = -1 if number == 1 else 1
    seg = {0: 6, 1: 10, 2: 16}[detail]
    b = Builder()
    b.lathe((tx, ty, tz), "Z", [(0.0, 0.385), (0.04, 0.385), (0.045, 0.365), (0.56, 0.355)], seg)
    if detail >= 1:
        b.box((tx, ty + 0.34, 1.75), (0.40, 0.11, 0.34))
        b.box((tx + side * 0.03, ty - 0.20, tz + 0.568), (0.34, 0.22, 0.018))
    if detail >= 2:
        b.prism([(ty + 0.05, tz + 0.56), (ty + 0.25, tz + 0.66), (ty + 0.27, tz + 0.645), (ty + 0.07, tz + 0.56)],
                tx - 0.15, tx + 0.15)
        b.lathe((tx - side * 0.17, ty + 0.05, tz + 0.56), "Z", [(0.0, 0.035), (0.09, 0.03)], 6)
        b.box((tx + side * 0.36, ty + 0.02, 1.75), (0.012, 0.13, 0.025))
        b.box((tx - side * 0.36, ty + 0.02, 1.75), (0.012, 0.13, 0.025))
    turret = b.finish("Tourelle_%02d" % number, mat, data["center"], chassis)

    mount = Vector(data["mount"])
    b = Builder()
    if detail >= 1:
        b.lathe(mount, "Y", [(-0.09, 0.15), (-0.03, 0.15), (0.0, 0.11), (0.03, 0.08)], max(cfg["seg"], 8))
    else:
        b.lathe(mount, "Y", [(-0.10, 0.12), (0.02, 0.09)], 5)
    axis = b.finish("Axe_Canon_%02d" % number, mat, mount, turret)

    b = Builder()
    length = data["muzzle_y"] - mount.y
    if detail >= 2:
        profile = [(0.02, 0.058), (length - 0.15, 0.056), (length - 0.135, 0.062), (length - 0.12, 0.03),
                   (length - 0.11, 0.018), (length, 0.016)]
    elif detail == 1:
        profile = [(0.02, 0.056), (length - 0.12, 0.056), (length - 0.11, 0.018), (length, 0.016)]
    else:
        profile = [(0.02, 0.05), (length, 0.03)]
    b.lathe(mount, "Y", profile, max(6, cfg["seg"] - 2))
    canon = b.finish("Canon_%02d" % number, mat, mount, axis)
    helper("Fx_tourelle%d_tir_01" % number, (mount.x, data["muzzle_y"] + 0.01, mount.z), canon)
    return turret


def wheel_shape(b, center, kind, cfg):
    seg = cfg["seg"]
    high = cfg["detail"] >= 2
    if kind == "sprocket":
        if high:
            b.spoked(center, S.SPROCKET[2], S.SPROCKET[2] * 0.74, 0.09, 5, teeth=24)
        else:
            b.lathe(center, "X", [(-0.08, S.SPROCKET[2]), (0.08, S.SPROCKET[2])], seg + 1)
    elif kind == "idler":
        if high:
            b.spoked(center, S.IDLER[2], S.IDLER[2] * 0.80, 0.11, 5, seg=16)
        else:
            b.lathe(center, "X", [(-0.08, S.IDLER[2]), (0.08, S.IDLER[2])], seg + 1)
    elif high:
        # Twin wheels with rounded rubber tyres, as in the suspension drawing.
        r = S.ROAD_R
        rounded = [(-0.046, r * 0.70), (-0.024, r * 0.97), (0.024, r * 0.97), (0.046, r * 0.70)]
        simple = [(-0.046, r * 0.72), (0.0, r), (0.046, r * 0.72)]
        outer = 1 if center[0] > 0 else -1
        for offset, profile in ((0.060 * outer, rounded), (-0.060 * outer, simple)):
            b.lathe((center[0] + offset, center[1], center[2]), "X", profile, 9)
    else:
        b.lathe(center, "X", [(-0.09, S.ROAD_R), (0.09, S.ROAD_R)], seg)


def build_wheels(cfg, mat, chassis):
    kinds = ["sprocket"] + ["road"] * 8 + ["idler"]
    for side, letter in ((1, "D"), (-1, "G")):
        for number, (kind, wheel) in enumerate(zip(kinds, S.WHEELS), 1):
            center = Vector((side * S.TRACK_X, wheel[0], wheel[1]))
            elev = helper("Roue_Elev_%s%d" % (letter, number), center, chassis, 0.05)
            b = Builder()
            wheel_shape(b, center, kind, cfg)
            b.finish("Roue_%s%d" % (letter, number), mat, center, elev, sharp=62 if kind == "road" else 40)


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
    collection = bpy.data.collections.new("7TP_" + name)
    bpy.context.scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]

    main = material_main()
    moving = name == "High"
    mat_d = material_track("M_Chenille_D", "chenilledroite") if moving else main
    mat_g = material_track("M_Chenille_G", "chenillegauche") if moving else main

    chassis = build_chassis(cfg, main)
    if S.VARIANT == "dw":
        build_turret_dw(cfg, main, chassis, 1)
        build_turret_dw(cfg, main, chassis, 2)
        stress = Vector(S.TURRETS[1]["center"]) + Vector((0, -0.1, 0.62))
    else:
        turret = build_turret_jw(cfg, main, chassis)
        build_gun_jw(cfg, main, turret)
        stress = Vector(S.TURRETS[1]["center"]) + Vector((0, -0.2, 0.68))
    if cfg["wheels"]:
        build_wheels(cfg, main, chassis)
    track_d = build_track("Chenille_Droite_01", 1, cfg["track"], mat_d, chassis, moving)
    track_g = build_track("Chenille_Gauche_01", -1, cfg["track"], mat_g, chassis, moving)

    helper("Fake", (0, 0, 0.5), chassis)
    helper("Fx_Stress_01", (0, -1.05, S.HULL_TOP + 0.08), chassis)
    helper("Fx_Stress_02", stress, chassis)
    helper("FX_Fumee_Chenille_D1", (S.TRACK_X, -2.10, 0.08), chassis)
    helper("FX_Fumee_Chenille_G1", (-S.TRACK_X, -2.10, 0.08), chassis)
    if cfg["wheels"]:
        skin_track(track_d, "D")
        skin_track(track_g, "G")

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    unwrap([o for o in meshes if not (moving and o.name.startswith("Chenille"))])
    report(name, cfg["limit"])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "7TP_%s.blend" % name))


def render_clay():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("Preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.65, 0.7, 0.75, 1)
    scene.world = world
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.5
    sun = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    views = {"geo_przod": ("PERSP", (5.4, 5.6, 2.3), (0, 0.1, 0.95), 50), "geo_bok": ("ORTHO", (12, 0, 1.1), (0, 0, 1.1), 5.4),
             "geo_tyl": ("PERSP", (-4.6, -6.6, 2.5), (0, -0.1, 0.95), 50),
             "geo_wozek": ("PERSP", (3.3, 1.9, 0.62), (1.10, 0.86, 0.30), 62)}
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
render_clay()
print("BUILD_DONE")
