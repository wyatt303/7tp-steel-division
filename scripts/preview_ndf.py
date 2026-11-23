"""Render an .Ase2NdfBin with its diffuse texture, to check axes, winding and UV direction.

blender --background --factory-startup --python preview_ndf.py -- <mesh> <diffuse.png> <output.png>
"""

import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blender_addon", "steel_division_ase2ndfbin"))
import ndfbin  # noqa: E402

mesh_path, texture_path, output = sys.argv[sys.argv.index("--") + 1:][:3]
objects = ndfbin.read_objects(open(mesh_path, "rb").read())
bpy.ops.wm.read_factory_settings(use_empty=True)

material = bpy.data.materials.new("Preview")
material.use_nodes = True
tree = material.node_tree
bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Roughness"].default_value = 0.7
image_node = tree.nodes.new("ShaderNodeTexImage")
image_node.image = bpy.data.images.load(texture_path)
tree.links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])

positive, total, corners = 0, 0, []
for obj in objects:
    if obj.cls != "TMemASEGeomObject":
        continue
    source = obj.get("Mesh")
    points = [v.get("Vector", (0, 0, 0)) for _, v in source.get("VertexList")]
    faces, smooth_normals = [], []
    for _, face in source.get("FaceList"):
        faces.append((face.get("A", 0), face.get("B", 0), face.get("C", 0)))
    for (a, b, c), (_, normal) in zip(faces, source.get("NormalsList")):
        expected = Vector(normal.get("FaceNormal").get("Vector", (0, 0, 0)))
        cross = (Vector(points[b]) - Vector(points[a])).cross(Vector(points[c]) - Vector(points[a]))
        if cross.length > 1e-6 and expected.length > 0:
            total += 1
            positive += cross.dot(expected) > 0
    mesh = bpy.data.meshes.new(obj.get("NodeName"))
    mesh.from_pydata([tuple(c / 100 for c in p) for p in points], [], faces)
    mesh.update()
    t_faces = source.get("TFaceMap")[0][3]
    t_verts = [v.get("Vector", (0, 0, 0)) for _, v in source.get("TVertexMap")[0][3]]
    layer = mesh.uv_layers.new(name="UVMap")
    for polygon, (_, t_face) in zip(mesh.polygons, t_faces):
        indices = t_face.get("TripleInteger", (0, 0, 0))
        for loop, index in zip(polygon.loop_indices, indices):
            layer.data[loop].uv = t_verts[index][:2]
    mesh.materials.append(material)
    item = bpy.data.objects.new(obj.get("NodeName"), mesh)
    bpy.context.scene.collection.objects.link(item)
    corners.extend(tuple(c / 100 for c in p) for p in points)

print("WINDING faces=%d aligned_with_normal=%.1f%%" % (total, 100 * positive / max(total, 1)))
low = [min(c[i] for c in corners) for i in range(3)]
high = [max(c[i] for c in corners) for i in range(3)]
center = Vector([(a + b) / 2 for a, b in zip(low, high)])
span = max(b - a for a, b in zip(low, high))

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.78, 0.82, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.4
scene.world = world
sun_data = bpy.data.lights.new("Sun", "SUN")
sun_data.energy = 4
sun = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(40))
camera_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
# Game space: front is +X, left is +Y. View from the front right.
camera.location = center + Vector((1.15, -1.05, 0.62)) * span * 1.15
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.lens = 45
scene.render.filepath = output
bpy.ops.render.render(write_still=True)
print("PREVIEW_DONE", output)

