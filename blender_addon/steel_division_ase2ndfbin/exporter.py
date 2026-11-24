# SPDX-License-Identifier: GPL-3.0-or-later
"""Convert a Blender tank scene to Eugen's Ase2NdfBin.

Scene rules are described in docs/WTYCZKA.md. In short: the tank faces +Y in Blender, right
side +X, Z up, 1 unit = 1 m. The game uses X forward, Y left, Z up, so (x, y, z) -> (y, -x, z).
"""

import os
import re
import shutil

import bpy

from .ndfbin import BOOL, FLOAT, INT, LIST, MAP, MATRIX, REF, STRING, TRIPLE, VEC3, Obj, write_file

DEFAULT_SCALE = 203.0
IDENTITY = (1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0)
ELEV = re.compile(r"Roue_Elev_([DG])(\d+)$")
CANON = re.compile(r"Canon_0\d$")
TRACKS = {"Chenille_Droite_01": "D", "Chenille_Gauche_01": "G"}
TRIANGLE_WARNING = 7000


class ExportProblem(Exception):
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors


def natural(name):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def validate(objects):
    """Catch the mistakes known to crash the game or the mod generator."""
    errors, warnings = [], []
    by_name = {o.name: o for o in objects}
    if not any(o.type == "MESH" for o in objects) or ("Chassis" not in by_name and "Train_Avant" in by_name):
        # Aircraft landing gear files (<name>_train): only the Train_Avant / Train_Arriere
        # helpers, or for retractable gear also the Train, Roue_Avant and Roue_Arriere meshes.
        # They carry no Chassis, weapons or tracks.
        for obj in objects:
            if obj.type == "MESH" and obj.data.uv_layers.active is None:
                errors.append("%s has no UV map" % obj.name)
        return errors, warnings
    if by_name.get("Chassis") is None or by_name["Chassis"].type != "MESH":
        errors.append("The scene needs a mesh named Chassis")
    if "Tourelle_01" not in by_name:
        warnings.append("No Tourelle_01. Turreted units expect Tourelle_01 to Tourelle_04")
    for number in range(1, 5):
        tag = "%02d" % number
        if "Tourelle_" + tag in by_name:
            for needed in ("Axe_Canon_" + tag, "Canon_" + tag, "Fx_tourelle%d_tir_01" % number):
                if needed not in by_name:
                    errors.append("%s is missing for Tourelle_%s" % (needed, tag))
    for obj in objects:
        if CANON.match(obj.name) and obj.type != "MESH":
            errors.append("%s must be a mesh, not an empty" % obj.name)
        if obj.type != "MESH":
            continue
        if any(abs(s - 1) > 1e-5 for s in obj.matrix_world.to_scale()):
            errors.append("%s has an unapplied scale" % obj.name)
        if not obj.data.uv_layers.active:
            errors.append("%s has no UV map" % obj.name)
            continue
        if not obj.data.materials or obj.data.materials[0] is None:
            errors.append("%s has no material" % obj.name)
        values = [c for item in obj.data.uv_layers.active.data for c in item.uv]
        if values and (min(values) < -0.001 or max(values) > 1.001):
            errors.append("%s has UVs outside 0-1. This crashed the game in testing" % obj.name)
    for name in TRACKS:
        if name not in by_name:
            warnings.append("%s not found" % name)
    return errors, warnings


def materials_of(meshes):
    found = []
    for obj in meshes:
        material = obj.data.materials[0]
        if material not in found:
            found.append(material)
    order = {"chenilledroite": 1, "chenillegauche": 2}
    return sorted(found, key=lambda m: order.get(m.get("eug_tag"), 0))


def eug_value(cls, value=None):
    obj = Obj(cls)
    if cls == "TEugBInteger" and value:
        obj.add("Value", INT, value)
    elif cls == "TEugBBoolean" and value:
        obj.add("Value", BOOL, True)
    elif cls == "TEugBString":
        obj.add("Value", STRING, value)
    return obj


def build_material(material, index, folder, errors):
    names = {key: material.get("eug_" + key) for key in ("diffuse", "specular", "glossiness", "normal")}
    for key, value in names.items():
        if not value:
            errors.append("Material %s needs the custom property eug_%s" % (material.name, key))
    if any(not value for value in names.values()):
        return None
    tag = material.get("eug_tag")
    alpha = material.get("eug_alpha")
    params = []

    def param(key, cls, value=None):
        params.append((STRING, key, REF, eug_value(cls, value)))

    for key in ("DiffuseTextureChannel", "VideoTextureChannel"):
        param(key, "TEugBInteger", 1)
    param("twoSided", "TEugBBoolean")
    for key in ("SpecularTextureChannel", "GlossinessTextureChannel", "NormalTextureChannel", "OpacityTextureChannel"):
        param(key, "TEugBInteger", 1)
    param("transparency", "TEugBBoolean")
    for key in ("CampTextureChannel", "EmissiveTextureChannel"):
        param(key, "TEugBInteger", 1)
    param("FaceCam", "TEugBBoolean")
    if tag:
        param(tag, "TEugBBoolean", True)
    param("useshaderfx", "TEugBBoolean")
    param("renderEnabled", "TEugBBoolean")
    param("technique", "TEugBInteger")
    base = folder.replace("\\", "/") + "/"
    param("DiffuseTexture", "TEugBString", base + names["diffuse"])
    param("SpecularTexture", "TEugBString", base + names["specular"])
    param("GlossinessTexture", "TEugBString", base + names["glossiness"])
    param("NormalTexture", "TEugBString", base + names["normal"])
    if alpha:
        param("OpacityTexture", "TEugBString", base + alpha)
    label = {"chenilledroite": "Droite", "chenillegauche": "Gauche"}.get(tag, "EugMaterialSurface")
    first = Obj("TMemASEMaterial1", ("Name", STRING, label), ("Classe", STRING, "EugMaterialSurface"),
                ("Ambient", VEC3, (0.588, 0.588, 0.588)), ("Diffuse", VEC3, (0.588, 0.588, 0.588)),
                ("Specular", VEC3, (0.9, 0.9, 0.9)), ("Shine", FLOAT, 0.1), ("ShineStrength", FLOAT, 0.3),
                ("WireSize", FLOAT, 1.0), ("DX9ShaderEffectEnable", BOOL, True),
                ("DX9ShaderEffectName", STRING, "EugSurfaceMaterial"),
                ("DX9ShaderTechniqueName", STRING, "SurfaceStandard"), ("DX9ShaderParams", MAP, params))
    out = Obj("TMemASEMaterial", ("Material1", REF, first), ("XTypeAfter", REF, Obj("TMemASEMaterialXTypeAfter")))
    if index:
        out.add("MaterialID", INT, index)
    return out.add("SubNo", INT, -1)


def copy_material_textures(materials, folder):
    wanted = set()
    for material in materials:
        for key in ("diffuse", "specular", "glossiness", "normal", "alpha"):
            if material.get("eug_" + key):
                wanted.add(material["eug_" + key])
    sources = {}
    for image in bpy.data.images:
        if image.filepath:
            path = bpy.path.abspath(image.filepath)
            sources[os.path.basename(path)] = path
    missing = []
    for name in sorted(wanted):
        source = sources.get(name)
        target = os.path.join(folder, name)
        if source and os.path.isfile(source):
            if os.path.abspath(source) != os.path.abspath(target):
                shutil.copy2(source, target)
        elif not os.path.isfile(target):
            missing.append(name)
    return missing


def export_scene(scene, filepath, scale=DEFAULT_SCALE, copy_textures=True):
    objects = sorted((o for o in scene.objects if o.type in {"MESH", "EMPTY"}), key=lambda o: natural(o.name))
    errors, warnings = validate(objects)
    if errors:
        raise ExportProblem(errors)

    def game(point):
        return (scale * point[1], -scale * point[0], scale * point[2])

    def direction(normal):
        return (normal[1], -normal[0], normal[2])

    def vector(value):
        return Obj("TMemASEMeshVertex", ("Vector", VEC3, value))

    def normal_obj(value):
        return Obj("TMemASEMeshVertexNormal", ("Vector", VEC3, value))

    def node_tm(name, position):
        tm = Obj("TMemASENodeTM", ("NODE_NAME", STRING, name), ("TM_ROW0", VEC3, (1.0, 0.0, 0.0)),
                 ("TM_ROW1", VEC3, (0.0, 1.0, 0.0)), ("TM_ROW2", VEC3, (0.0, 0.0, 1.0)))
        if any(abs(c) > 1e-6 for c in position):
            tm.add("TM_ROW3", VEC3, position).add("TM_POS", VEC3, position)
        return tm.add("TM_SCALE", VEC3, (1.0, 1.0, 1.0))

    last_wheel = {"D": 0, "G": 0}
    elevators = {"D": [], "G": []}
    for obj in objects:
        match = ELEV.match(obj.name)
        if match:
            last_wheel[match[1]] = max(last_wheel[match[1]], int(match[2]))
            elevators[match[1]].append((int(match[2]), obj))

    def parent_of(obj):
        if obj.name in TRACKS or obj.name.startswith("FX_Fumee"):
            return None
        match = ELEV.match(obj.name)
        if match:
            # In the game's tanks only the sprocket and idler lifts are linked to the hull.
            return "Chassis" if int(match[2]) in (1, last_wheel[match[1]]) else None
        return obj.parent.name if obj.parent else None

    def build_mesh(obj):
        data = obj.data
        data.calc_loop_triangles()
        matrix = obj.matrix_world
        rotation = matrix.to_3x3()
        layer = data.uv_layers.active.data
        corner_normals = data.corner_normals
        faces, normals, t_faces, t_verts, uv_index = [], [], [], [], {}
        for tri in data.loop_triangles:
            face = Obj("TMemASEMeshFace")
            for label, value in zip("ABC", tri.vertices):
                if value:
                    face.add(label, INT, value)
            face.add("AB", INT, 1).add("BC", INT, 1).add("MESH_SMOOTHINGIntegerList", LIST, [(INT, 1)])
            faces.append((REF, face))
            corner = [direction((rotation @ corner_normals[l].vector).normalized()) for l in tri.loops]
            normals.append((REF, Obj("TMemASEMeshNormal",
                                     ("FaceNormal", REF, normal_obj(direction((rotation @ tri.normal).normalized()))),
                                     ("NormalList", LIST, [(REF, normal_obj(n)) for n in corner]))))
            indices = []
            for loop in tri.loops:
                key = (round(layer[loop].uv[0], 6), round(layer[loop].uv[1], 6))
                if key not in uv_index:
                    uv_index[key] = len(t_verts)
                    t_verts.append((REF, vector((key[0], key[1], 0.0))))
                indices.append(uv_index[key])
            t_faces.append((REF, Obj("TMemASEMeshTFace", ("TripleInteger", TRIPLE, tuple(indices)))))
        points = [(REF, vector(game(matrix @ v.co))) for v in data.vertices]
        mesh = Obj("TMemASEMesh", ("VertexList", LIST, points), ("FaceList", LIST, faces), ("NormalsList", LIST, normals),
                   ("TFaceMap", MAP, [(0x3, 1, LIST, t_faces)]), ("TVertexMap", MAP, [(0x3, 1, LIST, t_verts)]))
        return mesh, len(faces)

    def animation(name):
        samples = []
        for frame in range(101):
            sample = Obj("TMemASEControlMatrixSample", ("Matrix", MATRIX, IDENTITY))
            if frame:
                sample.add("Index", INT, frame * 160)
            samples.append((REF, sample))
        return Obj("TMemASETMAnimation", ("NodeName", STRING, name), ("ControlMatrixSampleList", LIST, samples))

    def physique(track, letter):
        groups = {g.index: g.name for g in track.vertex_groups}
        road = [(n, obj.matrix_world.translation.y) for n, obj in elevators[letter] if 1 < n < last_wheel[letter]]
        vertices = []
        for vertex in track.data.vertices:
            name = groups[max(vertex.groups, key=lambda g: g.weight).group] if vertex.groups else None
            if not name:
                name = "Fake"
                if vertex.co.z < 0.12 and road:
                    number, y = min(road, key=lambda item: abs(item[1] - vertex.co.y))
                    if abs(y - vertex.co.y) <= 0.20:
                        name = "Roue_Elev_%s%d" % (letter, number)
            link = Obj("TMemASEPhysiqueLinkAndWeight", ("LinkNodeName", STRING, name), ("Weight", FLOAT, 1.0))
            vertices.append((REF, Obj("TMemASEPhysiqueVertex", ("PhysiqueLinkAndWeightList", LIST, [(REF, link)]))))
        poses = [(STRING, "Fake", REF, Obj("TMemASEMatrixWrapper", ("Matrix", MATRIX, IDENTITY)))]
        for number, obj in sorted(elevators[letter], key=lambda item: item[0]):
            x, y, z = game(obj.matrix_world.translation)
            matrix = (1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, x, -y, z, 1.0)  # Eugen stores this pose with Y negated.
            poses.append((STRING, obj.name, REF, Obj("TMemASEMatrixWrapper", ("Matrix", MATRIX, matrix))))
        return Obj("TMemASEPhysiqueModifier", ("TargetNodeName", STRING, track.name), ("PhysiqueVertices", LIST, vertices),
                   ("NodeNameToPoseMatrix", REF, Obj("TMemASEMatrixDico", ("Dico", MAP, poses))))

    folder = os.path.dirname(os.path.abspath(filepath))
    meshes = [o for o in objects if o.type == "MESH"]
    used = materials_of(meshes)
    material_errors = []
    materials = [build_material(m, i, folder, material_errors) for i, m in enumerate(used)]
    if material_errors:
        raise ExportProblem(material_errors)

    geoms, helpers, modifiers, triangles = [], [], [], 0
    for obj in meshes:
        mesh, count = build_mesh(obj)
        triangles += count
        geom = Obj("TMemASEGeomObject", ("NodeName", STRING, obj.name))
        parent = parent_of(obj)
        if parent:
            geom.add("NodeParent", STRING, parent)
        geom.add("NodeTM", REF, node_tm(obj.name, game(obj.matrix_world.translation)))
        if obj.name in TRACKS:
            geom.add("TMAnimation", REF, animation(obj.name))
        geom.add("Mesh", REF, mesh).add("CastShadow", INT, 1).add("RecVShadow", INT, 1)
        index = used.index(obj.data.materials[0])
        if index:
            geom.add("MaterialRef", INT, index)
        geoms.append((REF, geom))
        if obj.name in TRACKS:
            modifiers.append((REF, physique(obj, TRACKS[obj.name])))

    for obj in (o for o in objects if o.type == "EMPTY"):
        kind = obj.get("eug_helper_class", "PointHelper")
        size = 8.0 if kind == "Dummy" else 0.01
        position = game(obj.matrix_world.translation)
        helper = Obj("TMemASEHelperObject", ("NodeName", STRING, obj.name))
        parent = parent_of(obj)
        if parent:
            helper.add("NodeParent", STRING, parent)
        helper.add("NodeTM", REF, node_tm(obj.name, position))
        helper.add("BoundingBox_Min", VEC3, tuple(c - size for c in position))
        helper.add("BoundingBox_Max", VEC3, tuple(c + size for c in position))
        helper.add("HelperClass", STRING, kind)
        helpers.append((REF, helper))

    if triangles > TRIANGLE_WARNING:
        warnings.append("%d triangles is above the manual's limit of about %d" % (triangles, TRIANGLE_WARNING))

    stem = os.path.splitext(os.path.basename(filepath))[0]
    root = Obj("TMemASE",
               ("Scene", REF, Obj("TMemASEScene", ("FileName", STRING, stem + ".max"), ("LastFrame", INT, 100),
                                  ("FrameSpeed", INT, 160), ("TicksPerFrame", INT, 160),
                                  ("AmbientStatic", VEC3, (0.4, 0.4, 0.4)), ("Version", INT, 1000))),
               ("MaterialList", LIST, [(REF, m) for m in materials]),
               ("GeomObjectList", LIST, geoms), ("HelperObjectList", LIST, helpers),
               ("PhysiqueModifierList", LIST, modifiers),
               ("BoneListList", LIST, [(REF, Obj("TMemASEBoneList")) for _ in modifiers]),
               ("MapSearchPathList", LIST, [(STRING, folder.replace("\\", "/"))]),
               ("VersionMessage", STRING, "Exported from Blender by Steel Division Ase2NdfBin Exporter\n"),
               ("ForceRigidSkinning", BOOL, True))
    os.makedirs(folder, exist_ok=True)
    size = write_file(filepath, root)
    if copy_textures:
        missing = copy_material_textures(used, folder)
        if missing:
            warnings.append("Textures not found: " + ", ".join(missing))
    return {"bytes": size, "triangles": triangles, "nodes": len(geoms) + len(helpers), "warnings": warnings}
