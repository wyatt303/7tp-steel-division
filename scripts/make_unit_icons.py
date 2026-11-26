"""Render the in-game interface icons of the 7TP units from the models.

  blender --background --factory-startup --python make_unit_icons.py -- <7TP project folder> <mod AssetsModding folder>

The sizes and styles copy the game's own images (read from vfxbank_gfxeverything.ppk):

  TP7_JW_RTS.png, TP7_DW_RTS.png      42 x 26  label over the unit and menu icon: a white
                                               silhouette with a black outline, front to the left
                                               (Texture_RTS_H_*). The game tints it with the
                                               player colour.
  TP7_JW_TopView.png, TP7_DW_TopView.png
                                     100 x 75  textured view from above, front to the right
  TP7_Bofors37_Weapon.png            132 x 50  weapon picture in the unit panel: the 7TP turret
                                               with the 37 mm gun, from the side, muzzle right
  TP7_CkmWz30_Weapon.png             132 x 50  the same for the ckm wz. 30 machine gun, built
                                               here from simple shapes
"""

import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

ROOT, OUT = [os.path.abspath(p) for p in sys.argv[sys.argv.index("--") + 1:][:2]]
os.makedirs(OUT, exist_ok=True)
MODELS = {"TP7_JW": "7TP_jednowiezowy_Bofors", "TP7_DW": "7TP_dwuwiezowy_wz30", "TKS20": "TKS20"}
# Main gun pictures: the mount with its gun (Tourelle_01, Axe_Canon_01, Canon_01), as the game
# shows the turret of its tanks for their main gun.
GUN_PICTURES = {"TP7_JW": "TP7_Bofors37_Weapon.png", "TKS20": "TKS20_Nkm20_Weapon.png"}
SUPER = 8  # supersampling for the small images


def open_model(stem):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "models", MODELS[stem], stem + ".blend"))
    for mat in bpy.data.materials:
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image and not node.image.filepath.lower().endswith(
                        ("_glo.png", "_sc.png", "_nm.png", "_a.png")):
                    mat.node_tree.nodes.active = node
                    break


def bounds(objects):
    pts = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def visible_meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_render and max(o.dimensions) > 0.05]


def render(width, height, view, scale, center, colour="TEXTURE", light="STUDIO"):
    """Orthographic Workbench render on a transparent background; returns RGBA, top row first."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    shading = scene.display.shading
    shading.light = light
    shading.color_type = colour
    shading.single_color = (1.0, 1.0, 1.0)
    shading.show_cavity = colour != "SINGLE"
    shading.show_shadows = False
    shading.show_object_outline = False
    cam_data = bpy.data.cameras.new("icon")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = scale
    cam = bpy.data.objects.new("icon", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    direction = {"left_side": Vector((1, 0, 0)), "right_side": Vector((-1, 0, 0)), "top": Vector((0, 0, -1))}[view]
    cam.location = Vector(center) - direction * 30
    if view == "top":
        cam.rotation_euler = (0.0, 0.0, math.pi / 2)  # +Y (the front) to the right of the image
    else:
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    path = os.path.join(bpy.app.tempdir, "icon.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    px = np.array(image.pixels[:], np.float32).reshape(height, width, 4)[::-1].copy()
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    return px


def downsample(px, k):
    h, w = px.shape[0] // k, px.shape[1] // k
    px = px[:h * k, :w * k].reshape(h, k, w, k, 4)
    alpha = px[..., 3].mean((1, 3))
    rgb = (px[..., :3] * px[..., 3:4]).sum((1, 3)) / np.maximum(px[..., 3].sum((1, 3)), 1e-6)[..., None]
    return np.concatenate([rgb, alpha[..., None]], -1)


def save(px, name):
    h, w = px.shape[:2]
    image = bpy.data.images.new(name, w, h, alpha=True)
    image.pixels.foreach_set(np.ascontiguousarray(np.clip(px, 0, 1)[::-1]).astype(np.float32).ravel())
    image.filepath_raw = os.path.join(OUT, name)
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
    print("ICON", name, w, h)


def fit(objects, view, width, height, margin_x, margin_y):
    """Ortho scale and centre that fit the objects into the image, keeping the aspect."""
    lo, hi = bounds(objects)
    size = hi - lo
    across, up = (size.y, size.z) if view != "top" else (size.y, size.x)
    scale = max(across / (width - 2 * margin_x) * width, up / (height - 2 * margin_y) * width)
    return scale, (lo + hi) / 2


def rts_icon(stem):
    """White silhouette, front to the left, black outline; a grey band with dark wheels below."""
    w, h = 42, 26
    objects = visible_meshes()
    scale, center = fit(objects, "left_side", w, h, 7, 4)
    px = render(w * SUPER, h * SUPER, "left_side", scale, center, colour="SINGLE", light="FLAT")
    lo, hi = bounds(objects)
    # Push the silhouette to sit low in the frame like the game's icons (bottom 3 px free).
    small = downsample(px, SUPER)
    alpha = small[..., 3]
    rows = np.where(alpha.max(1) > 0.3)[0]
    shift = (h - 3) - (rows.max() + 1)
    alpha = np.roll(alpha, shift, 0)
    if shift > 0:
        alpha[:shift] = 0
    # Running gear band: the lowest 30 % of the silhouette, light grey with darker wheel dots.
    rows = np.where(alpha.max(1) > 0.3)[0]
    top, bottom = rows.min(), rows.max()
    band = int(round(bottom - (bottom - top) * 0.30))
    shade = np.ones_like(alpha)
    shade[band:bottom + 1] = 0.82
    cols = np.where(alpha[bottom - 1] > 0.5)[0]
    if len(cols):
        for x in range(cols.min() + 2, cols.max() - 1, 3):
            shade[bottom - 2, x] = 0.35
    shade[band] = np.where(alpha[band] > 0.5, 0.55, shade[band])
    # One pixel black outline outside the shape.
    grown = alpha.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            grown = np.maximum(grown, np.roll(np.roll(alpha, dy, 0), dx, 1))
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = (shade * alpha)[..., None]
    out[..., 3] = grown
    save(out, stem + "_RTS.png")


def top_view(stem):
    w, h = 100, 75
    objects = visible_meshes()
    scale, center = fit(objects, "top", w, h, 8, 8)
    px = render(w * 4, h * 4, "top", scale, center)
    small = downsample(px, 4)
    small[..., :3] = np.clip(small[..., :3] * 1.15, 0, 1)
    save(small, stem + "_TopView.png")


def gun_picture(stem, file_name):
    """The mount and its gun from the right side, muzzle to the right, as on the game's cards."""
    open_model(stem)
    keep = {"Tourelle_01", "Axe_Canon_01", "Canon_01"}
    for o in bpy.context.scene.objects:
        if o.type == "MESH" and o.name not in keep:
            o.hide_render = True
    objects = [bpy.data.objects[n] for n in keep]
    w, h = 132, 50
    scale, center = fit(objects, "right_side", w, h, 3, 6)
    px = render(w * 4, h * 4, "right_side", scale, center)
    small = downsample(px, 4)
    small[..., :3] = np.clip(small[..., :3] * 1.25, 0, 1)
    save(small, file_name)


def ckm_weapon():
    """A simple ckm wz. 30 (water-cooled Browning type): receiver, jacket, muzzle, grips."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    metal = bpy.data.materials.new("metal")
    metal.diffuse_color = (0.20, 0.20, 0.19, 1.0)
    jacket_mat = bpy.data.materials.new("jacket")
    jacket_mat.diffuse_color = (0.30, 0.30, 0.27, 1.0)

    def box(name, location, size, mat):
        bpy.ops.mesh.primitive_cube_add(location=location)
        o = bpy.context.object
        o.name, o.scale = name, (size[0] / 2, size[1] / 2, size[2] / 2)
        o.data.materials.append(mat)
        return o

    def tube(name, y0, y1, radius, z, mat, vertices=24):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=y1 - y0,
                                            location=(0, (y0 + y1) / 2, z), rotation=(math.pi / 2, 0, 0))
        o = bpy.context.object
        o.name = name
        o.data.materials.append(mat)
        return o

    box("receiver", (0, -0.12, 0.0), (0.06, 0.34, 0.12), metal)
    box("top_cover", (0, -0.08, 0.07), (0.055, 0.22, 0.03), metal)
    box("grip", (0, -0.31, -0.03), (0.03, 0.05, 0.10), metal)
    box("feed", (0.045, -0.06, 0.01), (0.04, 0.06, 0.05), metal)
    tube("trunnion", 0.03, 0.08, 0.045, 0.0, metal)
    tube("jacket", 0.08, 0.50, 0.040, 0.0, jacket_mat)
    for y in (0.12, 0.30, 0.47):
        tube("band", y - 0.008, y + 0.008, 0.044, 0.0, metal)
    tube("plug", 0.20, 0.23, 0.012, 0.045, metal, 12)
    tube("muzzle", 0.50, 0.58, 0.016, 0.0, metal, 16)
    tube("booster", 0.56, 0.60, 0.022, 0.0, metal, 16)
    objects = visible_meshes()
    w, h = 132, 50
    scale, center = fit(objects, "right_side", w, h, 4, 12)
    px = render(w * 4, h * 4, "right_side", scale, center, colour="MATERIAL")
    small = downsample(px, 4)
    rgb = small[..., :3]
    small[..., :3] = np.clip((rgb - 0.45) * 1.8 + 0.30, 0, 1) * np.array([1.12, 1.04, 0.86], np.float32)
    save(small, "TP7_CkmWz30_Weapon.png")


for stem in MODELS:
    open_model(stem)
    rts_icon(stem)
    open_model(stem)
    top_view(stem)
for stem, file_name in GUN_PICTURES.items():
    gun_picture(stem, file_name)
ckm_weapon()
print("ICONS_DONE")
