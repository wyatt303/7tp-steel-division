"""Build the 40 mm wz. 36 Bofors anti-aircraft gun from the game's Bofors 40 mm (QF Mk I/III).

  blender --background --factory-startup --python build_bofors40.py -- <output folder>

The Polish wz. 36 is the same Swedish 40 mm L/60 Bofors on the same two-axle carriage, so the
game's model (Steel Division Modding Assets, USA/Canon.zip, Canon/Bofors_40mm) is used as it is
and only repainted in the Polish 1936 camouflage:
- High, Mid and Low are imported with import_ase2ndfbin.py, keeping the node names, pivots and
  their order, so the game's Bofors animations (USA/Canon/Bofors_40mm) still fit;
- the diffuse texture of each version is repainted: where the original shows the olive paint, the
  1936 olive / sand / brown camouflage of our models (as texture_tk.py, sampled at the 3D position
  of every texel) replaces the colour, while the original shading and details are kept; rubber,
  metal, brass and markings stay as they are;
- the normal, specular, glossiness and alpha textures are copied unchanged.

Everything this script writes comes from game files, so it goes to build/ and is made again on
every install (zainstaluj_mod.ps1); none of it belongs in the repository.

Output: <stem>.blend, <stem>_MID.blend, <stem>_LOW.blend, Boites_<stem>.blend, their textures
and renders/render_przod_3_4.png for the unit cards.
"""

import math
import os
import shutil
import sys
import zipfile

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import import_ase2ndfbin as IMP  # noqa: E402

STEM = "B40WZ36"
ASSETS = os.environ.get("SD44_MODDING_ASSETS",
                        r"D:\SteamLibrary\steamapps\common\Steel Division Modding Assets\Mods\Assets\3D\Units")
ZIP = os.path.join(ASSETS, "USA", "Canon.zip")
SOURCES = [("Canon/Bofors_40mm/Bofors_40mm", ""), ("Canon/Bofors_40mm_MID/Bofors_40mm_MID", "_MID"),
           ("Canon/LODS/Bofors_40mm_LOW", "_LOW")]
BOXES = "Canon/Bofors_40mm/Boites_Bofors_40mm"
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])

# 1936 camouflage colours of our models (texture_tk.py).
OLIVE = np.array([68, 71, 46], np.float32) / 255
SAND = np.array([126, 117, 93], np.float32) / 255
BROWN = np.array([56, 48, 39], np.float32) / 255
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


def texel_positions(objects, w, h):
    """3D position (Blender metres) of every texel covered by a triangle, -inf elsewhere."""
    P = np.full((h, w, 3), np.nan, np.float32)
    for obj in objects:
        me = obj.data
        me.calc_loop_triangles()
        uv = me.uv_layers.active.data
        mw = obj.matrix_world
        co = [mw @ v.co for v in me.vertices]
        for tri in me.loop_triangles:
            a, b, c = [Vector(uv[l].uv) for l in tri.loops]
            pa, pb, pc = [np.array(co[v], np.float32) for v in tri.vertices]
            A, B, C = (a.x * w, a.y * h), (b.x * w, b.y * h), (c.x * w, c.y * h)
            x0, x1 = max(int(min(A[0], B[0], C[0])) - 1, 0), min(int(max(A[0], B[0], C[0])) + 2, w)
            y0, y1 = max(int(min(A[1], B[1], C[1])) - 1, 0), min(int(max(A[1], B[1], C[1])) + 2, h)
            if x1 <= x0 or y1 <= y0:
                continue
            d = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
            if abs(d) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
            w0 = ((B[1] - C[1]) * (X - C[0]) + (C[0] - B[0]) * (Y - C[1])) / d
            w1 = ((C[1] - A[1]) * (X - C[0]) + (A[0] - C[0]) * (Y - C[1])) / d
            w2 = 1 - w0 - w1
            eps = 0.8 / max(math.sqrt(abs(d)), 1.0)
            inside = (w0 >= -eps) & (w1 >= -eps) & (w2 >= -eps)
            if not inside.any():
                continue
            pts = w0[..., None] * pa + w1[..., None] * pb + w2[..., None] * pc
            window = P[y0:y1, x0:x1]
            window[inside] = pts[inside]
    return P


def repaint(image, objects, target):
    w, h = image.size
    px = np.array(image.pixels[:], np.float32).reshape(h, w, 4)
    rgb = px[..., :3]
    P = texel_positions(objects, w, h)
    covered = ~np.isnan(P[..., 0])
    # Paint mask: greenish olive, moderately saturated, not too dark (rubber) nor bright (brass,
    # markings). Measured on the texture itself.
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    greenish = (g >= r * 0.92) & (g >= b * 1.02)
    paint = covered & greenish & (mx > 0.06) & (mx < 0.75) & (sat > 0.06) & (sat < 0.65)
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    base = float(np.median(lum[paint])) if paint.any() else 0.25
    pos = P[paint].astype(np.float64)
    q = pos * np.array([0.72, 0.46, 1.65])
    sand_f = fbm(q + 11.3, 3, 3)
    brown_f = fbm(q + np.array([41.7, 5.2, 19.9]), 77, 3)
    sand_cut, brown_cut = np.percentile(sand_f, 70), np.percentile(brown_f, 74)
    es, eb = sand_f.std() * 0.17, brown_f.std() * 0.17
    sand = smooth(sand_cut - es, sand_cut + es, sand_f)[..., None]
    brown = smooth(brown_cut - eb, brown_cut + eb, brown_f)[..., None]
    camo = OLIVE * (1 - sand) + SAND * sand
    camo = camo * (1 - brown) + BROWN * brown
    # Keep the original shading, edges and dirt: scale the camouflage by the texel's brightness
    # against the typical paint brightness.
    detail = np.clip(lum[paint] / base, 0.35, 1.8)[..., None]
    out = rgb.copy()
    # Olive patches keep the brightness of the original paint; sand and brown follow from it.
    olive_lum = float(OLIVE @ np.array([0.299, 0.587, 0.114], np.float32))
    out[paint] = np.clip(camo * detail * (base / olive_lum), 0, 1)
    px[..., :3] = out
    new = bpy.data.images.new(os.path.basename(target), w, h, alpha=True)
    new.colorspace_settings.name = image.colorspace_settings.name
    new.pixels.foreach_set(px.ravel())
    new.filepath_raw = target
    new.file_format = "PNG"
    new.save()
    print("REPAINTED", os.path.basename(target), w, h, "paint texels %.0f%%" % (100.0 * paint.sum() / max(covered.sum(), 1)))
    return new


def extract(names):
    src = os.path.join(OUT, "src")
    with zipfile.ZipFile(ZIP) as z:
        for member in z.namelist():
            if any(member.startswith(n.rsplit("/", 1)[0] + "/" + n.rsplit("/", 1)[1]) for n in names):
                z.extract(member, src)
    return src


def render_card(path):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light, sh.color_type, sh.show_cavity = "STUDIO", "TEXTURE", True
    scene.render.film_transparent = False
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    scene.world = world
    world.color = (0.75, 0.76, 0.74)
    pts = [o.matrix_world @ Vector(c) for o in scene.objects if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (lo + hi) / 2
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.lens = 40
    cam.location = c + Vector((5.4, 6.6, 3.1))
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def main():
    os.makedirs(OUT, exist_ok=True)
    src = extract([s for s, _ in SOURCES] + [BOXES])
    for source, suffix in SOURCES:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        created, order, materials, problems = IMP.import_file(os.path.join(src, *source.split("/")) + ".Ase2NdfBin")
        if problems:
            raise RuntimeError("Faces lost in " + ", ".join(problems))
        meshes = [o for o in created.values() if o.type == "MESH"]
        # The game's Low model has a few UVs a hair outside 0-1 (up to 1.0018); our exporter
        # refuses those, as they crashed the game with our own models.
        for obj in meshes:
            for loop in obj.data.uv_layers.active.data:
                loop.uv = (min(max(loop.uv[0], 0.0), 1.0), min(max(loop.uv[1], 0.0), 1.0))
        folder = os.path.dirname(os.path.join(src, *source.split("/")))
        for mat in materials:
            renamed = {}
            for key in ("diffuse", "specular", "glossiness", "normal", "alpha"):
                old = mat.get("eug_" + key)
                if not old:
                    continue
                tail = os.path.splitext(old)[0][len(os.path.basename(source)):]  # "", "_NM", "_SC"...
                new_name = STEM + suffix + tail + ".png"
                renamed[key] = new_name
                target = os.path.join(OUT, new_name)
                if key == "diffuse":
                    image = next(i for i in bpy.data.images if os.path.basename(i.filepath) == old)
                    new = repaint(image, meshes, target)
                    for node in mat.node_tree.nodes:
                        if node.type == "TEX_IMAGE" and node.image == image:
                            node.image = bpy.data.images.load(target)
                    bpy.data.images.remove(new)
                else:
                    shutil.copyfile(os.path.join(folder, old), target)
                    for image in bpy.data.images:
                        if os.path.basename(image.filepath) == old:
                            image.filepath = target
            for key, name in renamed.items():
                mat["eug_" + key] = name
        # The game's Bofors animations address the nodes in this order.
        bpy.context.scene["eug_node_order"] = ",".join(order)
        bpy.context.preferences.filepaths.save_version = 0
        if not suffix:
            render_card(os.path.join(OUT, "renders", "render_przod_3_4.png"))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, STEM + suffix + ".blend"))
        tris = sum(len(o.data.polygons) for o in meshes)
        print("BUILT", STEM + suffix, "nodes", len(order), "triangles", tris)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    created, order, _, _ = IMP.import_file(os.path.join(src, *BOXES.split("/")) + ".Ase2NdfBin")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Boites_" + STEM + ".blend"))
    print("BUILT Boites_" + STEM, sorted(created))
    print("BOFORS40_DONE")


main()
