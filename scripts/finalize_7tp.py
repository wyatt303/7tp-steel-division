"""Make a textured 7TP model self-contained, so the add-on can export it as it stands.

Adds what the game needs but the model does not show: wheels on the Low model, lift helpers,
hidden mounts for unused weapon slots and the final texture names.

  set TP_VARIANT=jw
  blender --background --factory-startup --python finalize_7tp.py -- <model folder> <file stem>
"""

import math
import os
import sys

import addon_utils
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_7tp as S  # noqa: E402

ROOT, STEM = sys.argv[sys.argv.index("--") + 1:][:2]
ROOT = os.path.abspath(ROOT)
LODS = {"Low": "_LOW", "Mid": "_MID", "High": ""}


def place(obj, position, parent):
    position = Vector(position)
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = position - parent.matrix_world.translation
    bpy.context.view_layer.update()


def empty(name, position, parent, kind=None):
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if obj.name not in bpy.context.scene.objects:
        bpy.context.collection.objects.link(obj)
    obj.empty_display_type = "CUBE"
    obj.empty_display_size = 0.05
    if kind:
        obj["eug_helper_class"] = kind
    place(obj, position, parent)
    return obj


def mesh_object(name, points, faces, uv, material, position, parent):
    mesh = bpy.data.meshes.new(name)
    center = Vector(position)
    mesh.from_pydata([tuple(Vector(p) - center) for p in points], [], faces)
    mesh.update()
    layer = mesh.uv_layers.new(name="UVMap")
    offsets = ((0, 0), (0.002, 0), (0, 0.002))
    for polygon in mesh.polygons:
        for i, loop in enumerate(polygon.loop_indices):
            du, dv = offsets[i % 3]
            layer.data[loop].uv = (uv[0] + du, uv[1] + dv)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    place(obj, position, parent)
    return obj


def finish_scene(suffix):
    chassis = bpy.data.objects["Chassis"]
    main = bpy.data.materials["M_7TP"]
    track_uv = tuple(bpy.data.objects["Chenille_Droite_01"].data.uv_layers.active.data[0].uv)
    canon_uv = tuple(bpy.data.objects["Canon_01"].data.uv_layers.active.data[0].uv)

    for side, letter in ((1, "D"), (-1, "G")):
        for number, (y, z, radius) in enumerate(S.WHEELS, 1):
            center = (side * S.TRACK_X, y, z)
            elev = empty("Roue_Elev_%s%d" % (letter, number), center, chassis)
            wheel = "Roue_%s%d" % (letter, number)
            if wheel not in bpy.data.objects:
                x = side * (S.TRACK_X + S.TRACK_W / 2 + 0.006)
                ring = [(x, y + radius * math.cos(math.tau * i / 6), z + radius * math.sin(math.tau * i / 6)) for i in range(6)]
                if side < 0:
                    ring.reverse()
                mesh_object(wheel, ring, [(0, i, i + 1) for i in range(1, 5)], track_uv, main, center, elev)

    mount = S.EXTRA_MOUNT
    muzzle = (mount[0], S.EXTRA_MUZZLE_Y, mount[2])
    half = 1.5 / 203.0
    for slot in (s for s in (2, 3, 4) if s not in S.TURRETS):
        tourelle = empty("Tourelle_%02d" % slot, mount, bpy.data.objects["Tourelle_01"], "Dummy")
        axe = empty("Axe_Canon_%02d" % slot, mount, tourelle, "Dummy")
        corners = [(mount[0] + a * half, mount[1] + b * half, mount[2] + c * half)
                   for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
        quads = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
        canon = mesh_object("Canon_%02d" % slot, corners, quads, canon_uv, main, mount, axe)
        empty("Fx_tourelle%d_tir_01" % slot, muzzle, canon)

    for material in bpy.data.materials:
        for key, tag in (("eug_diffuse", ""), ("eug_glossiness", "_GLO"), ("eug_specular", "_SC"), ("eug_normal", "_NM"), ("eug_alpha", "_A")):
            if key in material:
                base = STEM + "_tracks" if material.name.startswith("M_Chenille") else STEM + suffix
                material[key] = base + tag + ".png"

    for image in list(bpy.data.images):
        # bpy.path.basename understands Blender's "//" prefix, os.path reads it as a network path.
        current = bpy.path.basename(image.filepath.replace("\\", "/"))
        if current.startswith("7TP"):
            name = STEM + current[3:]
            image.filepath = "//textures/" + name
            image.name = name
            image.reload()


addon_utils.enable("io_scene_fbx")
for lod, suffix in LODS.items():
    path = os.path.join(ROOT, "7TP_%s.blend" % lod)
    bpy.ops.wm.open_mainfile(filepath=path)
    bpy.context.preferences.filepaths.save_version = 0
    addon_utils.enable("io_scene_fbx")
    finish_scene(suffix)
    target = os.path.join(ROOT, "%s%s.blend" % (STEM, suffix))
    bpy.ops.wm.save_as_mainfile(filepath=target)
    bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT, "%s%s.fbx" % (STEM, suffix)), object_types={"MESH", "EMPTY"},
                             apply_unit_scale=True, bake_space_transform=False, axis_forward="Y", axis_up="Z",
                             mesh_smooth_type="FACE", use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
                             path_mode="RELATIVE")
    print("FINAL", S.VARIANT, lod, len(bpy.context.scene.objects))
print("FINAL_DONE")
