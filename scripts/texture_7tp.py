"""Generate Steel Division textures for the 7TP and connect them to the .blend files.

Run after build_7tp.py:
  blender --background --factory-startup --python texture_7tp.py -- <folder_with_blends>

Maps follow the bundled Sherman: diffuse, _GLO, _SC, _NM (DirectX green channel).
High: 2048 px plus separate 256 px tracks. Mid: 1024 px. Low: 256 px.

Paint: 1936 Polish three-tone scheme, olive green base with soft, mostly horizontal
greyish sand and dark brown patches. Exact shades are estimates, no RGB standard survives.
"""

import math
import os
import sys

import addon_utils
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
TEX = os.path.join(OUT, "Textures")
os.makedirs(TEX, exist_ok=True)

LODS = {"Low": (256, "_LOW"), "Mid": (1024, "_MID"), "High": (2048, "")}

OLIVE = np.array([68, 71, 46], np.float32) / 255
SAND = np.array([126, 117, 93], np.float32) / 255
BROWN = np.array([56, 48, 39], np.float32) / 255
DIRT = np.array([58, 49, 37], np.float32) / 255
STEEL = np.array([96, 91, 84], np.float32) / 255
RUBBER = np.array([23, 23, 22], np.float32) / 255
RUST = np.array([62, 40, 27], np.float32) / 255
TRACK_STEEL = np.array([52, 46, 40], np.float32) / 255

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_7tp as S  # noqa: E402

# Paint scheme. "1936": the generic soft three-tone scheme above. "cieszyn38": the twin-turret
# tank of the 3rd Armoured Battalion, Cieszyn, October 1938, after a colour plate: large patches
# of light sand (mostly on the lower hull), yellow green and brown (mostly on the turrets), with
# the battalion's white leaping greyhound on the outer side of each turret. Plate colours
# (214, 203, 168), (150, 152, 70) and (118, 94, 61) are scaled by 0.6, like the 1936 palette, because
# the printed plate is much lighter than paint seen in the game.
SCHEME = os.environ.get("TP_SCHEME", "cieszyn38" if S.VARIANT == "dw" else "1936")
SAND_38 = np.array([214, 203, 168], np.float32) / 255 * 0.60
GREEN_38 = np.array([150, 152, 70], np.float32) / 255 * 0.60
BROWN_38 = np.array([118, 94, 61], np.float32) / 255 * 0.60
EMBLEM_WHITE = np.array([214, 212, 200], np.float32) / 255 * 0.78
# Leaping greyhound, head forward (u = 1 is towards the front of the tank), v up, both 0..1.
GREYHOUND = [
    (1.00, 0.90), (0.93, 0.97), (0.86, 1.00), (0.82, 0.93), (0.66, 0.82), (0.48, 0.70), (0.32, 0.58),
    (0.20, 0.50), (0.08, 0.50), (0.00, 0.40), (0.07, 0.42), (0.17, 0.40), (0.12, 0.22), (0.02, 0.04),
    (0.10, 0.03), (0.26, 0.28), (0.40, 0.42), (0.56, 0.48), (0.74, 0.52), (0.97, 0.52), (0.98, 0.58),
    (0.78, 0.62), (0.84, 0.74), (0.94, 0.82),
]

TRACK_X = S.TRACK_X
ROAD_R = S.ROAD_R
RETURN_Y = np.array(S.RETURN_Y, np.float32)
RETURN_Z = S.RETURN_Z

TABLE = np.random.RandomState(1939).rand(65536).astype(np.float32)


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def noise3(p, seed):
    base = np.floor(p).astype(np.int64)
    f = (p - base).astype(np.float32)
    f = f * f * (3 - 2 * f)

    def corner(dx, dy, dz):
        index = ((base[:, 0] + dx) * 73856093) ^ ((base[:, 1] + dy) * 19349663) ^ ((base[:, 2] + dz) * 83492791) ^ seed
        return TABLE[index & 65535]

    x00 = corner(0, 0, 0) * (1 - f[:, 0]) + corner(1, 0, 0) * f[:, 0]
    x10 = corner(0, 1, 0) * (1 - f[:, 0]) + corner(1, 1, 0) * f[:, 0]
    x01 = corner(0, 0, 1) * (1 - f[:, 0]) + corner(1, 0, 1) * f[:, 0]
    x11 = corner(0, 1, 1) * (1 - f[:, 0]) + corner(1, 1, 1) * f[:, 0]
    y0 = x00 * (1 - f[:, 1]) + x10 * f[:, 1]
    y1 = x01 * (1 - f[:, 1]) + x11 * f[:, 1]
    return y0 * (1 - f[:, 2]) + y1 * f[:, 2]


def fbm(p, seed, octaves=3):
    total, amplitude, weight = 0, 1.0, 0.0
    for octave in range(octaves):
        total = total + noise3(p * (2 ** octave), seed + octave * 101) * amplitude
        weight += amplitude
        amplitude *= 0.5
    return total / weight


def collect_triangles(objects):
    positions, normals, uvs, parts, centers = [], [], [], [], []
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        matrix = obj.matrix_world
        rotation = matrix.to_3x3()
        layer = mesh.uv_layers.active.data
        part = 2 if obj.name.startswith("Chenille") else 0
        if obj.name.startswith("Roue_") and obj.name[6:].isdigit() and 2 <= int(obj.name[6:]) <= 9:
            part = 1
        center = matrix.translation
        for tri in mesh.loop_triangles:
            positions.append([tuple(matrix @ mesh.vertices[v].co) for v in tri.vertices])
            normals.append(tuple((rotation @ tri.normal).normalized()))
            uvs.append([tuple(layer[l].uv) for l in tri.loops])
            parts.append(part)
            centers.append((center.y, center.z))
    return (np.array(positions, np.float32), np.array(normals, np.float32), np.array(uvs, np.float32),
            np.array(parts, np.int8), np.array(centers, np.float32))


def rasterize(res, tri_pos, tri_nrm, tri_uv):
    P = np.zeros((res, res, 3), np.float32)
    N = np.zeros((res, res, 3), np.float32)
    T = np.full((res, res), -1, np.int32)
    exact = np.zeros((res, res), bool)
    for t in range(len(tri_pos)):
        a, b, c = tri_uv[t] * res
        x0, x1 = max(int(min(a[0], b[0], c[0])) - 1, 0), min(int(max(a[0], b[0], c[0])) + 2, res)
        y0, y1 = max(int(min(a[1], b[1], c[1])) - 1, 0), min(int(max(a[1], b[1], c[1])) + 2, res)
        if x1 <= x0 or y1 <= y0:
            continue
        denom = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denom) < 1e-7:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w0 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / denom
        w1 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / denom
        w2 = 1 - w0 - w1
        epsilon = 0.8 / max(math.sqrt(abs(denom)), 1.0)
        loose = (w0 >= -epsilon) & (w1 >= -epsilon) & (w2 >= -epsilon)
        strict = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        window_exact = exact[y0:y1, x0:x1]
        write = strict | (loose & (T[y0:y1, x0:x1] < 0) & ~window_exact)
        if not write.any():
            continue
        points = (w0[..., None] * tri_pos[t, 0] + w1[..., None] * tri_pos[t, 1] + w2[..., None] * tri_pos[t, 2])
        P[y0:y1, x0:x1][write] = points[write]
        N[y0:y1, x0:x1][write] = tri_nrm[t]
        T[y0:y1, x0:x1][write] = t
        window_exact[strict] = True
    return P, N, T


def rivet_lines():
    lines, seams = [], []

    def row(a, b, spacing=0.09):
        lines.append((Vector(a), Vector(b), spacing))

    def seam(a, b):
        seams.append((Vector(a), Vector(b)))

    for s in (-1, 1):
        x = s * 0.76
        row((x, 1.10, 1.17), (x, -2.08, 1.17))
        row((x, 1.08, 1.36), (x, -0.36, 1.36))
        row((x, -0.44, 1.52), (x, -2.00, 1.52))
        for y in (1.02, 0.42, -0.38, -1.32, -1.98):
            top = 1.36 if y > -0.4 else 1.52
            row((x, y, 1.19), (x, y, top), 0.075)
            seam((x, y + 0.03, 1.13), (x, y + 0.03, top + 0.03))
        x = s * 0.84
        row((x, 1.58, 0.44), (x, -1.82, 0.44), 0.10)
        row((x, 1.96, 1.05), (x, -2.05, 1.05), 0.10)
        row((x, 1.55, 0.74), (x, -2.10, 0.74), 0.12)
        for y in (1.50, 0.60, -0.40, -1.40):
            row((x, y, 0.46), (x, y, 1.03), 0.09)
            seam((x, y + 0.03, 0.40), (x, y + 0.03, 1.10))
        row((s * 0.80, 2.16, 0.79), (s * 0.80, 1.24, 1.11), 0.08)
        row((s * 0.72, 1.08, 1.40), (s * 0.72, -0.36, 1.40), 0.09)
        row((s * 0.72, -0.44, 1.56), (s * 0.72, -1.98, 1.56), 0.09)
        row((s * 1.17, 1.70, 1.04), (s * 1.17, -1.70, 1.04), 0.16)
        row((s * 0.87, 1.70, 1.04), (s * 0.87, -1.70, 1.04), 0.16)
        seam((s * 0.80, 2.20, 0.77), (s * 0.80, 1.22, 1.13))

    row((-0.80, 2.21, 0.72), (0.80, 2.21, 0.72), 0.085)
    row((-0.80, 1.90, 0.87), (0.80, 1.90, 0.87), 0.095)
    row((-0.78, 1.24, 1.105), (0.02, 1.24, 1.105), 0.09)
    row((-0.70, 1.08, 1.40), (0.05, 1.08, 1.40), 0.09)
    row((-0.70, -0.36, 1.40), (0.70, -0.36, 1.40), 0.09)
    row((-0.70, -0.46, 1.56), (0.70, -0.46, 1.56), 0.09)
    row((-0.70, -1.98, 1.56), (0.70, -1.98, 1.56), 0.09)
    row((-0.72, -2.04, 1.53), (0.72, -2.04, 1.53), 0.08)
    row((-0.72, -2.16, 1.13), (0.72, -2.16, 1.13), 0.08)
    for x in (-0.72, 0.0, 0.72):
        row((x, -2.04, 1.53), (x, -2.15, 1.14), 0.07)
    row((-0.80, -2.19, 0.66), (0.80, -2.19, 0.66), 0.09)
    seam((-0.82, 1.90, 0.89), (0.82, 1.90, 0.89))
    seam((-0.74, -0.40, 1.40), (0.74, -0.40, 1.40))

    for x in (0.10, 0.68):
        row((x, 1.25, 1.37), (x, 0.94, 1.47), 0.07)
        row((x, 1.40, 1.08), (x, 1.27, 1.33), 0.07)
    row((0.10, 1.41, 1.09), (0.68, 1.41, 1.09), 0.08)
    row((0.10, 1.27, 1.34), (0.68, 1.27, 1.34), 0.08)

    count = len(TURRET_PLAN)

    def turret_point(index, t, z):
        ax, ay = TURRET_PLAN[index]
        bx, by = TURRET_PLAN[(index + 1) % count]
        scale = 1.0 + (0.93 - 1.0) * (z - 1.64) / (2.06 - 1.64)
        return ((TURRET[0] + (ax + (bx - ax) * t) * TURRET_WIDTH * scale),
                (TURRET[1] + (ay + (by - ay) * t) * scale), z)

    for i in range(count):
        ax, ay = TURRET_PLAN[i]
        bx, by = TURRET_PLAN[(i + 1) % count]
        length = math.hypot(bx - ax, by - ay)
        if length < 0.14:
            continue
        margin = min(0.25, 0.05 / length)
        row(turret_point(i, margin, 2.00), turret_point(i, 1 - margin, 2.00), 0.085)
        row(turret_point(i, margin, 1.70), turret_point(i, 1 - margin, 1.70), 0.085)
        row(turret_point(i, margin, 1.72), turret_point(i, margin, 1.98), 0.075)
        seam(turret_point(i, 0.0, 1.66), turret_point(i, 0.0, 2.05))
    return lines, seams


def rivet_lines():  # noqa: F811
    """Rivet rows and plate seams for the hull and turrets of the drawing-based model."""
    lines, seams = [], []

    def row(a, b, spacing=0.09):
        lines.append((Vector(a), Vector(b), spacing))

    def seam(a, b):
        seams.append((Vector(a), Vector(b)))

    top = S.HULL_TOP
    for s in (-1, 1):
        x = s * S.UPPER_HALF_WIDTH
        row((x, 0.76, 1.17), (x, -1.88, 1.17))
        row((x, 0.68, top - 0.04), (x, -1.70, top - 0.04))
        for y in (S.ROOF_FRONT_Y - 0.03, S.BULKHEAD_Y, S.ROOF_REAR_Y):
            row((x, y, 1.19), (x, y, top - 0.06), 0.075)
            seam((x, y + 0.03, 1.13), (x, y + 0.03, top))
        x = s * S.HULL_HALF_WIDTH
        row((x, 1.62, 0.44), (x, -1.40, 0.44), 0.10)
        row((x, 1.92, 1.08), (x, -1.88, 1.08), 0.10)
        row((x, 1.62, 0.76), (x, -1.90, 0.76), 0.12)
        for y in (1.56, S.ROOF_FRONT_Y, S.BULKHEAD_Y, -1.42):
            row((x, y, 0.46), (x, y, 1.05), 0.09)
            seam((x, y + 0.03, 0.40), (x, y + 0.03, 1.12))
        row((s * 0.77, 2.00, 0.90), (s * 0.77, 0.86, 1.12), 0.08)
        row((s * 0.74, 0.68, top), (s * 0.74, -1.70, top), 0.09)
        row((s * 1.17, 1.70, 1.12), (s * 1.17, -1.70, 1.12), 0.16)
        row((s * 0.85, 1.70, 1.12), (s * 0.85, -1.70, 1.12), 0.16)
        seam((s * 0.77, 2.03, 0.89), (s * 0.77, 0.84, 1.13))

    row((-0.76, 2.03, 0.77), (0.76, 2.03, 0.77), 0.085)
    row((-0.76, 1.70, 0.95), (0.76, 1.70, 0.95), 0.095)
    row((-0.76, 0.86, 1.11), (0.03, 0.86, 1.11), 0.09)
    row((-0.72, 0.66, top), (0.72, 0.66, top), 0.09)
    row((-0.72, S.BULKHEAD_Y, top), (0.72, S.BULKHEAD_Y, top), 0.09)
    row((-0.72, -1.69, top), (0.72, -1.69, top), 0.09)
    row((-0.75, -1.75, 1.43), (0.75, -1.75, 1.43), 0.08)
    row((-0.75, -1.91, 1.15), (0.75, -1.91, 1.15), 0.08)
    for x in (-0.75, 0.0, 0.75):
        row((x, -1.75, 1.43), (x, -1.90, 1.17), 0.07)
    row((-0.78, -1.99, 0.62), (0.78, -1.99, 0.62), 0.09)
    seam((-0.80, 1.70, 0.97), (0.80, 1.70, 0.97))
    seam((-0.77, S.BULKHEAD_Y, top), (0.77, S.BULKHEAD_Y, top))

    for x in (0.10, 0.68):
        row((x, 1.00, 1.10), (x, 0.91, 1.34), 0.07)
    row((0.10, 1.00, 1.11), (0.68, 1.00, 1.11), 0.08)

    for number, data in S.TURRETS.items():
        tx, ty, tz = data["center"]
        radius = 0.355 if S.VARIANT == "dw" else 0.48
        for z, r in ((tz + 0.13, radius), (tz + 0.52, radius - 0.02)):
            for i in range(28):
                a = math.tau * i / 28
                point = Vector((tx + r * math.cos(a), ty + r * math.sin(a), z))
                lines.append((point, point + Vector((0, 0, 0.0001)), 1.0))
        for i in range(6):
            a = math.tau * (i + 0.2) / 6
            bottom = Vector((tx + radius * math.cos(a), ty + radius * math.sin(a), tz + 0.16))
            upper = Vector((tx + (radius - 0.02) * math.cos(a), ty + (radius - 0.02) * math.sin(a), tz + 0.49))
            row(bottom, upper, 0.075)
            seam(bottom - Vector((0, 0, 0.08)), upper + Vector((0, 0, 0.05)))
        if S.VARIANT == "jw":
            for side in (-1, 1):
                row((tx + side * 0.41, ty - 0.42, 1.74), (tx + side * 0.40, ty - 0.78, 1.74), 0.07)
                row((tx + side * 0.39, ty - 0.42, 2.03), (tx + side * 0.38, ty - 0.74, 2.03), 0.07)
            row((tx - 0.36, ty - 0.82, 1.74), (tx + 0.36, ty - 0.82, 1.74), 0.08)
            row((tx - 0.34, ty - 0.76, 2.03), (tx + 0.34, ty - 0.76, 2.03), 0.08)
    return lines, seams


class Painter:
    def __init__(self, res, tri_pos, tri_nrm, tri_uv, P, N, T):
        self.res, self.tri_pos, self.tri_uv, self.P, self.N, self.T = res, tri_pos, tri_uv, P, N, T
        self.mask = T >= 0
        self.H = np.zeros((res, res), np.float32)
        self.W = np.zeros((res, res), np.float32)
        verts = tri_pos.reshape(-1, 3).tolist()
        polygons = [(i * 3, i * 3 + 1, i * 3 + 2) for i in range(len(tri_pos))]
        self.bvh = BVHTree.FromPolygons(verts, polygons, all_triangles=True, epsilon=0.0)
        world = np.linalg.norm(np.cross(tri_pos[:, 1] - tri_pos[:, 0], tri_pos[:, 2] - tri_pos[:, 0]), axis=1) / 2
        uv = np.abs(np.cross(tri_uv[:, 1] - tri_uv[:, 0], tri_uv[:, 2] - tri_uv[:, 0])) / 2 * res * res
        self.tri_density = np.sqrt(uv / np.maximum(world, 1e-9))
        self.density = float(np.sqrt(uv.sum() / world.sum()))

    def stamp(self, point, radius, height, groove=False):
        location, normal, index, distance = self.bvh.find_nearest(point)
        if location is None or distance > 0.035:
            return 0
        a, b, c = self.tri_pos[index]
        v0, v1 = b - a, c - a
        v2 = np.array(location, np.float32) - a
        d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
        denom = d00 * d11 - d01 * d01
        if abs(denom) < 1e-12:
            return 0
        w1, w2 = (d11 * d20 - d01 * d21) / denom, (d00 * d21 - d01 * d20) / denom
        uv = self.tri_uv[index, 0] * (1 - w1 - w2) + self.tri_uv[index, 1] * w1 + self.tri_uv[index, 2] * w2
        col, row = uv * self.res
        span = max(int(math.ceil(radius * self.tri_density[index])) + 1, 2)
        r0, r1 = max(int(row) - span, 0), min(int(row) + span + 1, self.res)
        c0, c1 = max(int(col) - span, 0), min(int(col) + span + 1, self.res)
        if r1 <= r0 or c1 <= c0:
            return 0
        center = np.array(location, np.float32)
        d = np.linalg.norm(self.P[r0:r1, c0:c1] - center, axis=2) / radius
        facing = self.N[r0:r1, c0:c1] @ np.array(normal, np.float32)
        selected = self.mask[r0:r1, c0:c1] & (d < 1) & (facing > 0.5)
        if not selected.any():
            return 0
        if groove:
            value = -height * (1 - d)
            self.H[r0:r1, c0:c1][selected] = np.minimum(self.H[r0:r1, c0:c1][selected], value[selected])
        else:
            value = height * np.sqrt(np.clip(1 - d * d, 0, 1))
            self.H[r0:r1, c0:c1][selected] = np.maximum(self.H[r0:r1, c0:c1][selected], value[selected])
            ring = np.clip(1 - np.abs(d - 0.75) * 3, 0, 1)
            self.W[r0:r1, c0:c1][selected] = np.maximum(self.W[r0:r1, c0:c1][selected], ring[selected])
        return 1

    def draw_details(self):
        lines, seams = rivet_lines()
        rivets = 0
        for a, b, spacing in lines:
            length = (b - a).length
            count = max(int(round(length / spacing)), 1)
            for i in range(count + 1):
                rivets += self.stamp(a.lerp(b, i / count), 0.0135, 0.0065)
        step = max(1.2 / self.density, 0.003)
        for a, b in seams:
            count = max(int((b - a).length / step), 1)
            for i in range(count + 1):
                self.stamp(a.lerp(b, i / count), 0.006, 0.004, groove=True)
        return rivets


def bake_ao(res, objects, material):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = False
    world = bpy.data.worlds.new("BakeWorld")
    world.light_settings.distance = 0.7
    scene.world = world
    scene.render.bake.margin = 4
    scene.render.bake.use_clear = True

    image = bpy.data.images.new("AO_tmp", res, res, alpha=False)
    image.colorspace_settings.name = "Non-Color"
    node = material.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    material.node_tree.nodes.active = node
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.bake(type="AO", use_selected_to_active=False)
    pixels = np.empty(res * res * 4, np.float32)
    image.pixels.foreach_get(pixels)
    ao = pixels[0::4].reshape(res, res).copy()
    material.node_tree.nodes.remove(node)
    bpy.data.images.remove(image)
    scene.world = None
    bpy.data.worlds.remove(world)
    return ao


def bleed(array, mask, iterations):
    """Extend painted texels into empty atlas space so mip maps do not pull in background."""
    filled = mask.copy()
    data = array if array.ndim == 3 else array[..., None]
    for _ in range(iterations):
        weight = np.zeros(filled.shape, np.float32)
        total = np.zeros(data.shape, np.float32)
        for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
            f = np.roll(filled, shift, axis)
            weight += f
            total += np.roll(data, shift, axis) * f[..., None]
        grow = ~filled & (weight > 0)
        if not grow.any():
            break
        data[grow] = total[grow] / weight[grow][..., None]
        filled |= grow
    return array


def save_png(path, rgb, alpha=None):
    height, width = rgb.shape[:2]
    if rgb.ndim == 2:
        rgb = np.repeat(rgb[..., None], 3, axis=2)
    image = bpy.data.images.new("save_tmp", width, height, alpha=True)
    a = np.ones((height, width), np.float32) if alpha is None else alpha
    pixels = np.dstack((np.clip(rgb, 0, 1), np.clip(a, 0, 1))).astype(np.float32).ravel()
    image.pixels.foreach_set(pixels)
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def normal_from_height(H, density, wrap=False):
    if wrap:
        d_col = (np.roll(H, -1, 1) - np.roll(H, 1, 1)) * 0.5 * density
        d_row = (np.roll(H, -1, 0) - np.roll(H, 1, 0)) * 0.5 * density
    else:
        d_row, d_col = np.gradient(H)
        d_row, d_col = d_row * density, d_col * density
    # Blender rows run with +V. Green stores DirectX style Y, matching the Sherman example.
    n = np.dstack((-d_col, d_row, np.ones_like(H)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def camouflage_cieszyn(pos, nrm):
    """Large, fairly hard-edged patches: sand low on the hull, brown high on the turrets."""
    q = pos * np.array([0.50, 0.34, 0.95])
    z = pos[:, 2]
    sand_field = fbm(q + 3.7, 13, 3)
    brown_field = fbm(q + np.array([17.1, 31.4, 7.7]), 59, 3)
    sand_field = (sand_field - sand_field.mean()) / sand_field.std() + 2.2 * smooth(1.30, 0.62, z)
    brown_field = (brown_field - brown_field.mean()) / brown_field.std() + 0.8 * smooth(1.50, 1.95, z)
    sand_cut, brown_cut = np.percentile(sand_field, 55), np.percentile(brown_field, 82)
    sand = smooth(sand_cut - 0.07, sand_cut + 0.07, sand_field)[..., None]
    brown = smooth(brown_cut - 0.07, brown_cut + 0.07, brown_field)[..., None]
    color = GREEN_38 * (1 - sand) + SAND_38 * sand
    return color * (1 - brown) + BROWN_38 * brown


def inside_polygon(u, v, polygon):
    result = np.zeros(len(u), bool)
    for i in range(len(polygon)):
        (x1, y1), (x2, y2) = polygon[i], polygon[(i + 1) % len(polygon)]
        crosses = (y1 > v) != (y2 > v)
        result ^= crosses & (u < (x2 - x1) * (v - y1) / (y2 - y1 + 1e-12) + x1)
    return result


def paint_emblems(color, pos, part):
    """White greyhound on the outer side of each turret, 0.30 m long, as on the plate."""
    for data in S.TURRETS.values():
        cx, cy, base = data["center"]
        side = 1.0 if cx >= 0 else -1.0
        dx, dy = pos[:, 0] - cx, pos[:, 1] - cy
        on_side = (part == 0) & (side * dx > 0.24) & (np.hypot(dx, dy) > 0.28) & (np.hypot(dx, dy) < 0.42)
        u = (pos[:, 1] - (cy - 0.17)) / 0.30
        v = (pos[:, 2] - (base + 0.17)) / 0.22
        hit = on_side & (u > 0) & (u < 1) & (v > 0) & (v < 1)
        if hit.any():
            selected = np.flatnonzero(hit)
            mark = inside_polygon(u[selected], v[selected], GREYHOUND)
            color[selected[mark]] = EMBLEM_WHITE


def paint_atlas(res, suffix, objects, material):
    atlas = [o for o in objects if res < 2048 or not o.name.startswith("Chenille")]
    tri_pos, tri_nrm, tri_uv, parts, centers = collect_triangles(atlas)
    P, N, T = rasterize(res, tri_pos, tri_nrm, tri_uv)
    painter = Painter(res, tri_pos, tri_nrm, tri_uv, P, N, T)
    rivets = painter.draw_details() if res >= 1024 else 0
    ao_map = bake_ao(res, atlas, material)

    mask = painter.mask
    pos = P[mask].astype(np.float64)
    nrm = N[mask]
    part = parts[T[mask]]
    center = centers[T[mask]]
    ao = np.clip(ao_map[mask], 0, 1)
    height = painter.H[mask]
    wear_ring = painter.W[mask]

    if SCHEME == "cieszyn38":
        color = camouflage_cieszyn(pos, nrm)
        paint_emblems(color, pos, part)
    else:
        # Camouflage: elongated horizontally, soft sprayed edges, well-lit surfaces get darker paint.
        q = pos * np.array([0.72, 0.46, 1.65])
        sand_field = fbm(q + 11.3, 3, 3) - 0.035 * nrm[:, 2]
        brown_field = fbm(q + np.array([41.7, 5.2, 19.9]), 77, 3) + 0.035 * nrm[:, 2]
        sand_cut, brown_cut = np.percentile(sand_field, 70), np.percentile(brown_field, 74)
        edge_s, edge_b = sand_field.std() * 0.17, brown_field.std() * 0.17
        sand = smooth(sand_cut - edge_s, sand_cut + edge_s, sand_field)[..., None]
        brown = smooth(brown_cut - edge_b, brown_cut + edge_b, brown_field)[..., None]
        color = OLIVE * (1 - sand) + SAND * sand
        color = color * (1 - brown) + BROWN * brown

    mottle = fbm(pos * 9.0, 201, 4)
    grain = noise3(pos * 150.0, 303)
    color = color * (0.82 + 0.36 * mottle)[..., None] * (0.96 + 0.08 * grain)[..., None]

    # Road dust rising from the tracks and vertical rain streaks.
    dust = smooth(1.05, 0.12, pos[:, 2]) * (0.35 + 0.9 * fbm(pos * np.array([3.0, 3.0, 5.0]), 404, 3))
    dust = np.clip(dust, 0, 0.72).astype(np.float32)
    if SCHEME == "cieszyn38":
        dust *= 0.4  # the plate shows a clean, freshly painted tank; keep the light sand visible
    streak = fbm(pos * np.array([16.0, 16.0, 1.3]), 505, 3)
    vertical = 1 - smooth(0.45, 0.8, np.abs(nrm[:, 2]))
    color *= (1 - vertical * smooth(0.52, 0.72, streak) * 0.22)[..., None]
    color = color * (1 - dust[..., None]) + DIRT * dust[..., None]

    # Chipped paint around rivets, scratches near lower hull and on walkways.
    chip_noise = fbm(pos * 42.0, 606, 3)
    chip = wear_ring * smooth(0.50, 0.62, chip_noise)
    walkway = smooth(0.8, 0.95, nrm[:, 2]) * smooth(0.76, 0.80, fbm(pos * 58.0, 707, 3)) * 0.30
    wear = np.clip(chip + walkway, 0, 1).astype(np.float32)
    color = color * (1 - wear[..., None]) + STEEL * wear[..., None]

    # Component colours.
    gloss_adjust = np.zeros(len(pos), np.float32)
    road = part == 1
    if road.any():
        radial = np.hypot(pos[road, 1] - center[road, 0], pos[road, 2] - center[road, 1])
        rubber = smooth(ROAD_R * 0.56, ROAD_R * 0.61, radial)
        selected = np.flatnonzero(road)
        color[selected] = color[selected] * (1 - rubber[..., None]) + RUBBER * rubber[..., None]
        gloss_adjust[selected] -= 0.08 * rubber
    near_roller = np.abs(np.abs(pos[:, 0]) - TRACK_X) < 0.105
    if near_roller.any():
        selected = np.flatnonzero(near_roller & (part == 0))
        distance = np.sqrt(np.min((pos[selected, 1, None] - RETURN_Y) ** 2, axis=1) + (pos[selected, 2] - RETURN_Z) ** 2)
        # Rubber only on the rim of the return rollers; the dished face and hub keep the paint.
        r = S.RETURN_R
        rubber = smooth(0.80 * r, 0.84 * r, distance) * (1 - smooth(r + 0.004, r + 0.010, distance))
        color[selected] = color[selected] * (1 - rubber[..., None]) + RUBBER * rubber[..., None]
    muffler = (pos[:, 1] < -2.05) & (np.abs(pos[:, 2] - 0.80) < 0.095) & (np.abs(pos[:, 0] + 0.02) < 0.61)
    if muffler.any():
        amount = 0.45 + 0.45 * fbm(pos[muffler] * 18.0, 808, 3)
        color[muffler] = color[muffler] * (1 - amount[..., None]) + RUST * amount[..., None]
    track = part == 2
    if track.any():
        stripes = 0.65 + 0.35 * (np.sin(pos[track, 1] * math.tau / 0.0975) > -0.3)
        color[track] = TRACK_STEEL * stripes[..., None]
        gloss_adjust[track] += 0.05

    cavity = np.clip(-height / 0.004, 0, 1)
    color *= (1 - 0.55 * cavity)[..., None]
    color *= (0.32 + 0.68 * ao ** 1.15)[..., None]

    gloss = (0.075 + 0.075 * mottle + 0.38 * wear - 0.05 * dust + gloss_adjust) * (0.45 + 0.55 * ao)
    spec = (0.055 + 0.045 * mottle + 0.22 * wear - 0.025 * dust) * (0.45 + 0.55 * ao)

    def expand(values, fill):
        out = np.full((res, res) + values.shape[1:], fill, np.float32)
        out[mask] = values
        return out

    iterations = {2048: 16, 1024: 8, 256: 4}[res]
    diffuse = bleed(expand(np.clip(color, 0, 1), 0.12), mask, iterations)
    glo = bleed(expand(np.clip(gloss, 0, 1), 0.08), mask, iterations)
    sc = bleed(expand(np.clip(spec, 0, 1), 0.05), mask, iterations)

    grain_height = np.zeros((res, res), np.float32)
    if res >= 1024:
        grain_height[mask] = (fbm(pos * 70.0, 909, 2) - 0.5) * 0.0011
    nm = normal_from_height(painter.H + grain_height, painter.density)
    outside = ~mask
    nm[outside] = (0.5, 0.5, 1.0)
    nm = bleed(nm, mask, iterations)

    names = {}
    for key, tag, data in (("diffuse", "", diffuse), ("glo", "_GLO", glo), ("sc", "_SC", sc), ("nm", "_NM", nm)):
        name = "7TP%s%s.png" % (suffix, tag)
        save_png(os.path.join(TEX, name), data)
        names[key] = name
    coverage = mask.mean() * 100
    print("TEX %s res=%d rivets=%d density=%.0f px/m coverage=%.1f%% diffuse_mean=%.0f" % (
        suffix or "_HIGH", res, rivets, painter.density, coverage, np.mean(diffuse[mask]) * 255))
    return names


def paint_tracks():
    """256 px track as in the game's own tanks: texture U runs across the track, V along it.

    Across: outer 0-0.5, side, inner 0.6-0.9, side. Four links per tile, 28 tiles per track.
    Below, `V` is the across coordinate and `U` the along coordinate.
    """
    res = 256
    col = (np.arange(res) + 0.5) / res
    row = (np.arange(res) + 0.5) / res
    V, U = np.meshgrid(col, row)
    phase = (U * 4) % 1

    H = np.zeros((res, res), np.float32)
    alpha = np.ones((res, res), np.float32)
    outer = V < 0.5
    side_a = (V >= 0.5) & (V < 0.6)
    inner = (V >= 0.6) & (V < 0.9)
    side_b = V >= 0.9

    t = V[outer] / 0.5
    grouser = np.exp(-((phase[outer] - 0.5) / 0.13) ** 2) * (1 - smooth(0.42, 0.5, np.abs(t - 0.5)))
    pin = np.exp(-(np.minimum(phase[outer], 1 - phase[outer]) / 0.07) ** 2)
    H[outer] = 0.85 * grouser - 0.55 * pin
    t = (V[inner] - 0.6) / 0.3
    horn = np.exp(-((phase[inner] - 0.5) / 0.20) ** 2) * np.exp(-((t - 0.5) / 0.12) ** 2)
    pads = np.exp(-((np.abs(t - 0.5) - 0.28) / 0.14) ** 2) * (1 - np.exp(-(np.minimum(phase[inner], 1 - phase[inner]) / 0.1) ** 2))
    H[inner] = 1.0 * horn + 0.45 * pads
    for strip in (side_a, side_b):
        knuckle = np.exp(-((phase[strip] - 0.5) / 0.28) ** 2)
        H[strip] = 0.55 * knuckle
        gap = np.minimum(phase[strip], 1 - phase[strip]) < 0.04
        alpha[strip] = (~gap).astype(np.float32)

    p = np.column_stack((np.cos(U.ravel() * math.tau) * 2.5, np.sin(U.ravel() * math.tau) * 2.5, V.ravel() * 6.0))
    rust = fbm(p, 1111, 4).reshape(res, res)
    fine = fbm(p * 5.0, 1212, 2).reshape(res, res)
    base = TRACK_STEEL * (0.62 + 0.6 * fine)[..., None]
    rust_mask = smooth(0.42, 0.68, rust)[..., None] * 0.7
    color = base * (1 - rust_mask) + RUST * rust_mask
    contact = np.zeros((res, res), np.float32)
    contact[outer] = smooth(0.45, 0.85, H[outer])
    contact[inner] = smooth(0.35, 0.8, H[inner]) * 0.8
    color = color * (1 - contact[..., None]) + np.array([112, 106, 98], np.float32) / 255 * contact[..., None]
    shade = 0.42 + 0.58 * smooth(-0.55, 0.45, H)
    shade[side_a | side_b] *= 0.62
    color *= shade[..., None]

    nm = normal_from_height(H * 1.4, 1.0, wrap=True)
    glo = np.clip(0.20 + 0.18 * fine + 0.33 * contact - 0.10 * rust_mask[..., 0], 0, 1) * shade
    sc = np.clip(0.17 + 0.10 * fine + 0.22 * contact, 0, 1) * shade
    save_png(os.path.join(TEX, "7TP_tracks.png"), color)
    save_png(os.path.join(TEX, "7TP_tracks_A.png"), alpha)
    save_png(os.path.join(TEX, "7TP_tracks_GLO.png"), glo)
    save_png(os.path.join(TEX, "7TP_tracks_SC.png"), sc)
    save_png(os.path.join(TEX, "7TP_tracks_NM.png"), nm)
    print("TEX tracks res=256 alpha_cut=%.1f%%" % ((alpha == 0).mean() * 100))
    return {"diffuse": "7TP_tracks.png", "alpha": "7TP_tracks_A.png", "glo": "7TP_tracks_GLO.png",
            "sc": "7TP_tracks_SC.png", "nm": "7TP_tracks_NM.png"}


def load(name, data=False):
    image = bpy.data.images.load(os.path.join(TEX, name), check_existing=True)
    image.colorspace_settings.name = "Non-Color" if data else "sRGB"
    image.filepath = "//Textures/" + name
    return image


def connect(material, names):
    material["eug_diffuse"] = names["diffuse"]
    material["eug_glossiness"] = names["glo"]
    material["eug_specular"] = names["sc"]
    material["eug_normal"] = names["nm"]
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tree.links.new(bsdf.outputs[0], output.inputs["Surface"])

    def texture(name, data=False):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = load(name, data)
        return node

    diffuse = texture(names["diffuse"])
    tree.links.new(diffuse.outputs["Color"], bsdf.inputs["Base Color"])
    glo = texture(names["glo"], True)
    rough = tree.nodes.new("ShaderNodeMath")
    rough.operation = "SUBTRACT"
    rough.use_clamp = True
    rough.inputs[0].default_value = 0.92
    tree.links.new(glo.outputs["Color"], rough.inputs[1])
    tree.links.new(rough.outputs[0], bsdf.inputs["Roughness"])
    sc = texture(names["sc"], True)
    tree.links.new(sc.outputs["Color"], bsdf.inputs["Specular IOR Level"])
    bsdf.inputs["Metallic"].default_value = 0.0

    nm = texture(names["nm"], True)
    separate = tree.nodes.new("ShaderNodeSeparateColor")
    combine = tree.nodes.new("ShaderNodeCombineColor")
    flip = tree.nodes.new("ShaderNodeMath")
    flip.operation = "SUBTRACT"
    flip.inputs[0].default_value = 1.0
    normal = tree.nodes.new("ShaderNodeNormalMap")
    tree.links.new(nm.outputs["Color"], separate.inputs[0])
    tree.links.new(separate.outputs[0], combine.inputs[0])
    tree.links.new(separate.outputs[1], flip.inputs[1])
    tree.links.new(flip.outputs[0], combine.inputs[1])
    tree.links.new(separate.outputs[2], combine.inputs[2])
    tree.links.new(combine.outputs[0], normal.inputs["Color"])
    tree.links.new(normal.outputs[0], bsdf.inputs["Normal"])
    if "alpha" in names:
        material["eug_alpha"] = names["alpha"]
        alpha = texture(names["alpha"], True)
        tree.links.new(alpha.outputs["Color"], bsdf.inputs["Alpha"])


def stack_uvs(meshes):
    """Unwrap one wheel of each kind, then give its identical copies the same UVs."""
    by_name = {o.name: o for o in meshes}
    copies = {}
    for number in range(2, 10):
        for letter in "DG":
            name = "Roue_%s%d" % (letter, number)
            if name in by_name and name != "Roue_D2":
                copies[name] = "Roue_D2"
    for number in (1, 10):
        name = "Roue_G%d" % number
        if name in by_name:
            copies[name] = "Roue_D%d" % number

    moving = bpy.data.materials.get("M_Chenille_D") is not None
    unique = [o for o in meshes if o.name not in copies]
    packed = [o for o in unique if not (moving and o.name.startswith("Chenille"))]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in packed:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = packed[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    for name, master in copies.items():
        source = by_name[master].data.uv_layers.active.data
        target = by_name[name].data.uv_layers.active.data
        if len(source) != len(target):
            raise RuntimeError("Different topology: %s / %s" % (name, master))
        values = np.empty(len(source) * 2, np.float32)
        source.foreach_get("uv", values)
        target.foreach_set("uv", values)
    return unique


def look_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_views():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("Preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.68, 0.74, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    scene.world = world
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    ground = bpy.context.object
    ground_mat = bpy.data.materials.new("Ground")
    ground_mat.use_nodes = True
    bsdf = next(n for n in ground_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.36, 0.35, 0.31, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    ground.data.materials.append(ground_mat)
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 5.0
    sun_data.angle = math.radians(8)
    sun = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    cam_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    views = {
        "przod_3_4": ("PERSP", (5.4, 5.6, 2.1), (0, 0.1, 0.9), 50),
        "tyl_3_4": ("PERSP", (-4.6, -6.6, 2.4), (0, -0.1, 0.95), 50),
        "bok": ("ORTHO", (12, 0, 1.1), (0, 0, 1.1), 5.4),
        "zblizenie": ("PERSP", (3.0, 3.0, 2.1), (-0.05, 0.45, 1.35), 50),
    }
    for name, (kind, location, target, value) in views.items():
        cam_data.type = kind
        if kind == "ORTHO":
            cam_data.ortho_scale = value
        else:
            cam_data.lens = value
        camera.location = location
        look_at(camera, target)
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(OUT, "render_%s.png" % name)
        bpy.ops.render.render(write_still=True)
        print("RENDERED", name)


track_names = paint_tracks()
if os.environ.get("TRACKS_ONLY"):
    print("TRACKS_DONE")
    sys.exit(0)
for lod, (resolution, suffix) in LODS.items():
    blend = os.path.join(OUT, "7TP_%s.blend" % lod)
    bpy.ops.wm.open_mainfile(filepath=blend)
    addon_utils.enable("io_scene_fbx")
    bpy.context.preferences.filepaths.save_version = 0
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    main = bpy.data.materials["M_7TP"]
    unique_meshes = stack_uvs(meshes)
    atlas_names = paint_atlas(resolution, suffix, unique_meshes, main)
    connect(main, atlas_names)
    if lod == "High":
        connect(bpy.data.materials["M_Chenille_D"], track_names)
        connect(bpy.data.materials["M_Chenille_G"], track_names)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, "7TP_%s.fbx" % lod),
        object_types={"MESH", "EMPTY"},
        apply_unit_scale=True,
        bake_space_transform=False,
        axis_forward="Y",
        axis_up="Z",
        mesh_smooth_type="FACE",
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="RELATIVE",
    )
    print("SAVED", lod)

render_views()
print("TEXTURE_DONE")
