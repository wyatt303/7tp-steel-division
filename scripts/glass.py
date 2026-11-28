"""See-through glass for vehicle windows, made the way the game's own vehicles do it.

In the game's Opel Blitz, Jeep, Kubelwagen, Bedford, GMC and M5A1 the windows are a second
sub-material of the Chassis mesh (Multi\\Sub-Object material, the window triangles carry
MESH_MTLID 1). That sub-material has transparency on, an opacity map in place of the normal map
and four plain one-colour textures: black colour, opacity 76/255 (about 30 %), glossiness 246 and
specular 76. Windows are single planes without thickness, facing out, and the cab behind them
has an inside.

Here the panes are built as separate objects named Vitre_* with the glass material, so that the
texture pass (texture_tk.py) neither paints nor bakes them; finalize_tk.py joins them into the
Chassis, where they become the second material slot. Our exporter writes a mesh with two slots
as Eugen's Multi\\Sub-Object material.

The four textures are our own 4 x 4 pictures with those values, written into the model's
textures folder as <STEM>_Vitre.png, _Vitre_SC, _Vitre_GLO and _Vitre_A.
"""

import os

import bmesh
import bpy
from mathutils import Matrix, Vector

PREFIX = "Vitre_"
VALUES = {"": (0, 0, 0), "_SC": (76, 76, 76), "_GLO": (246, 246, 246), "_A": (76, 76, 76)}


def texture_names(stem):
    return {suffix: "%s_Vitre%s.png" % (stem, suffix) for suffix in VALUES}


def write_textures(folder, stem):
    os.makedirs(folder, exist_ok=True)
    for suffix, name in texture_names(stem).items():
        image = bpy.data.images.new("tmp_" + name, 4, 4, alpha=False)
        image.colorspace_settings.name = "Non-Color"
        r, g, b = (c / 255.0 for c in VALUES[suffix])
        image.pixels[:] = [r, g, b, 1.0] * 16
        image.filepath_raw = os.path.join(folder, name)
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)


def material(stem, folder):
    """Glass material with the custom properties the exporter reads (eug_transparent on)."""
    names = texture_names(stem)
    write_textures(folder, stem)
    mat = bpy.data.materials.get("M_Vitre")
    if mat:
        return mat
    mat = bpy.data.materials.new("M_Vitre")
    mat["eug_diffuse"] = names[""]
    mat["eug_specular"] = names["_SC"]
    mat["eug_glossiness"] = names["_GLO"]
    mat["eug_alpha"] = names["_A"]
    mat["eug_transparent"] = True
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Alpha"].default_value = 76 / 255.0
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    # Keep the pictures in the .blend so that the exporter finds and copies them.
    for name in names.values():
        image = bpy.data.images.load(os.path.join(folder, name), check_existing=True)
        image.colorspace_settings.name = "Non-Color"
        image.filepath = "//textures/" + name
        image.use_fake_user = True
    return mat


def add_panes(name, quads, mat, parent):
    """One object holding flat panes. Each quad is four corners (Blender metres) listed
    counter-clockwise as seen from outside, so the pane faces out."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    for quad in quads:
        face = bm.faces.new([bm.verts.new(p) for p in quad])
        for loop, coords in zip(face.loops, ((0.02, 0.02), (0.98, 0.02), (0.98, 0.98), (0.02, 0.98))):
            loop[uv].uv = coords
    mesh = bpy.data.meshes.new(PREFIX + name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(PREFIX + name, mesh)
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.location = -parent.matrix_world.translation
    bpy.context.view_layer.update()
    return obj


def rect(x0, x1, y0, y1, z0, z1, facing):
    """Axis-aligned pane: facing is "+X", "-X", "+Y" or "-Y" (the outward direction)."""
    if facing in ("+Y", "-Y"):
        y = y0
        quad = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
        return quad if facing == "-Y" else quad[::-1]
    x = x0
    quad = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    return quad if facing == "+X" else quad[::-1]


def is_glass(obj):
    return obj.type == "MESH" and obj.name.startswith(PREFIX)


def join_into_chassis():
    """Merge the Vitre_* panes into the Chassis mesh as its second material slot."""
    panes = [o for o in bpy.context.scene.objects if is_glass(o)]
    chassis = bpy.data.objects.get("Chassis")
    if not panes or chassis is None:
        return 0
    count = sum(len(o.data.polygons) for o in panes)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in panes:
        obj.select_set(True)
    chassis.select_set(True)
    bpy.context.view_layer.objects.active = chassis
    bpy.ops.object.join()
    bpy.ops.object.select_all(action="DESELECT")
    # The join adds the glass slot after the paint; keep the paint as slot 0.
    names = [m.name for m in chassis.data.materials]
    assert names[0] != "M_Vitre", names
    return count


def hide_for_bake(hidden):
    for obj in bpy.context.scene.objects:
        if is_glass(obj):
            obj.hide_render = hidden
