"""Import an Eugen .Ase2NdfBin model (Steel Division Modding Assets) into Blender.

  blender --background --factory-startup --python import_ase2ndfbin.py -- <model.Ase2NdfBin> <out.blend>

The reverse of our exporter (blender_addon/steel_division_ase2ndfbin/exporter.py):
- vertices are stored in the model's space in game units (X forward, Y left, Z up, 203 per
  metre); they become Blender metres with +Y forward and +X right;
- each node (mesh or helper) gets its origin at TM_POS from its NodeTM and its parent from
  NodeParent; rotations in NodeTM are not applied (the vertices are already in model space),
  they are kept in the custom property eug_tm;
- triangles keep their UVs (TFaceMap / TVertexMap) and their corner normals as custom normals;
- materials get an image texture node with the diffuse texture found next to the file, and the
  custom properties eug_diffuse / eug_specular / eug_glossiness / eug_normal / eug_alpha that our
  exporter reads, so an imported model can be exported again;
- helpers become empties with eug_helper_class.

Models from the game are only for reference and for building mod models from; the imported
files belong in build/ (ignored by git) and must not be published.
"""

import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "blender_addon", "steel_division_ase2ndfbin"))
import ndfbin  # noqa: E402

SCALE = 203.0
IMAGE_EXT = (".png", ".tga", ".dds")


def fields(obj):
    return {f[0]: f[-1] for f in obj.fields}


def items(value):
    """Objects of a list field, whatever the reader wrapped them in."""
    out = []
    for item in value or []:
        if isinstance(item, ndfbin.Obj):
            out.append(item)
        elif isinstance(item, (list, tuple)) and item and isinstance(item[-1], ndfbin.Obj):
            out.append(item[-1])
    return out


def map_list(value):
    """The list stored under key 1 of a TFaceMap / TVertexMap field."""
    for entry in value or []:
        if isinstance(entry, (list, tuple)) and isinstance(entry[-1], list):
            return items(entry[-1])
    return []


def to_blender(p):
    gx, gy, gz = p
    return Vector((-gy / SCALE, gx / SCALE, gz / SCALE))


def to_blender_dir(n):
    nx, ny, nz = n
    return Vector((-ny, nx, nz)).normalized()


def strings(value, found):
    if isinstance(value, ndfbin.Obj):
        for f in value.fields:
            strings(f[-1], found)
    elif isinstance(value, (list, tuple)):
        for x in value:
            strings(x, found)
    elif isinstance(value, str):
        found.append(value)
    return found


def make_material(index, mat_obj, folder):
    images = [s for s in strings(mat_obj, []) if s.lower().endswith(IMAGE_EXT)]
    names = [os.path.basename(s.replace("\\", "/")) for s in images]
    role = {}
    for name in names:
        stem = os.path.splitext(name)[0].upper()
        key = ("normal" if stem.endswith("_NM") else "specular" if stem.endswith("_SC") else
               "glossiness" if stem.endswith("_GLO") else "alpha" if stem.endswith("_A") else "diffuse")
        role.setdefault(key, name)
    mat = bpy.data.materials.new("M_%d_%s" % (index, os.path.splitext(role.get("diffuse", "material"))[0]))
    for key, name in role.items():
        mat["eug_" + key] = name
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    # Every texture is loaded, so the exporter finds and copies them all.
    for key, name in role.items():
        path = os.path.join(folder, name)
        if key not in ("diffuse", "alpha") and os.path.exists(path):
            image = bpy.data.images.load(path)
            image.colorspace_settings.name = "Non-Color"
            image.use_fake_user = True  # not used by a node; kept in the saved file for the exporter
    diffuse = role.get("diffuse")
    if diffuse and os.path.exists(os.path.join(folder, diffuse)):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.join(folder, diffuse))
        mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        nodes.active = tex
        alpha = role.get("alpha")
        if alpha and os.path.exists(os.path.join(folder, alpha)):
            atex = nodes.new("ShaderNodeTexImage")
            atex.image = bpy.data.images.load(os.path.join(folder, alpha))
            atex.image.colorspace_settings.name = "Non-Color"
            mat.node_tree.links.new(atex.outputs["Color"], bsdf.inputs["Alpha"])
    return mat


def tm_of(node):
    tm = fields(node).get("NodeTM")
    if not isinstance(tm, ndfbin.Obj):
        return Vector(), None
    t = fields(tm)
    pos = t.get("TM_POS") or t.get("TM_ROW3") or (0.0, 0.0, 0.0)
    rows = [t.get(k) for k in ("TM_ROW0", "TM_ROW1", "TM_ROW2")]
    return to_blender(pos), rows


def build_mesh(name, mesh_obj, origin, material):
    m = fields(mesh_obj)
    verts = [to_blender(fields(v)["Vector"]) - origin for v in items(m.get("VertexList"))]
    faces = []
    for face in items(m.get("FaceList")):
        f = fields(face)
        faces.append((f.get("A", 0), f.get("B", 0), f.get("C", 0)))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    ok = len(me.polygons) == len(faces)
    # UVs: one triple of TVertex indices per face.
    t_faces = [fields(t)["TripleInteger"] for t in map_list(m.get("TFaceMap"))]
    t_verts = [fields(t)["Vector"] for t in map_list(m.get("TVertexMap"))]
    if ok and t_faces and len(t_faces) == len(faces):
        layer = me.uv_layers.new(name="UVMap")
        for poly, triple in zip(me.polygons, t_faces):
            for loop, ti in zip(poly.loop_indices, triple):
                u, v = t_verts[ti][0], t_verts[ti][1]
                layer.data[loop].uv = (u, v)
    # Corner normals as custom normals.
    normals = items(m.get("NormalsList"))
    if ok and len(normals) == len(faces):
        corner = []
        for poly, n in zip(me.polygons, normals):
            listed = [to_blender_dir(fields(x)["Vector"]) for x in items(fields(n).get("NormalList"))]
            if len(listed) != 3:
                listed = [Vector((0, 0, 1))] * 3
            corner.extend(listed)
        try:
            me.normals_split_custom_set(corner)
        except Exception as problem:  # noqa: BLE001
            print("NOTE custom normals not set on", name, problem)
    if material:
        me.materials.append(material)
    return me, ok


def import_file(source):
    """Build the model of `source` in the current scene. Returns (objects by name, node names in
    the file's order, materials, names of meshes whose faces Blender dropped)."""
    folder = os.path.dirname(source)
    objs = ndfbin.read_objects(open(source, "rb").read())
    root = next(o for o in objs if o.cls == "TMemASE")
    r = fields(root)
    materials = [make_material(i, m, folder) for i, m in enumerate(items(r.get("MaterialList")))]
    created, parents, problems = {}, {}, []
    for geom in items(r.get("GeomObjectList")):
        g = fields(geom)
        name = g["NodeName"]
        origin, rows = tm_of(geom)
        mat_index = g.get("MaterialRef", 0) or 0
        material = materials[mat_index] if mat_index < len(materials) else None
        me, ok = build_mesh(name, g["Mesh"], origin, material)
        if not ok:
            problems.append(name)
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        ob.location = origin
        if rows:
            ob["eug_tm"] = [c for row in rows if row for c in row]
        created[name] = ob
        if g.get("NodeParent"):
            parents[name] = g["NodeParent"]
    for helper in items(r.get("HelperObjectList")):
        h = fields(helper)
        name = h["NodeName"]
        origin, _ = tm_of(helper)
        ob = bpy.data.objects.new(name, None)
        ob.empty_display_type = "CUBE"
        ob.empty_display_size = 0.04
        ob["eug_helper_class"] = h.get("HelperClass", "PointHelper")
        bpy.context.collection.objects.link(ob)
        ob.location = origin
        created[name] = ob
        if h.get("NodeParent"):
            parents[name] = h["NodeParent"]
    bpy.context.view_layer.update()
    for child, parent in parents.items():
        if parent in created:
            ob = created[child]
            world = ob.matrix_world.copy()
            ob.parent = created[parent]
            ob.matrix_world = world
    return created, list(created), materials, problems


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    source, target = os.path.abspath(args[0]), os.path.abspath(args[1])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    created, order, materials, problems = import_file(source)
    # Keep the file's node order for a later export (animations of game models need it).
    bpy.context.scene["eug_node_order"] = ",".join(order)
    tris = sum(len(o.data.polygons) for o in created.values() if o.type == "MESH")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=target)
    print("IMPORTED %s nodes=%d triangles=%d materials=%d -> %s" % (os.path.basename(source), len(created), tris,
                                                                   len(materials), target))
    if problems:
        print("NOTE faces dropped by Blender in:", ", ".join(problems))
    print("IMPORT_DONE")


if __name__ == "__main__":
    main()
