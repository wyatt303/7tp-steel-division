"""Remove local paths from model files before publishing.

Blender part, re-saves every .blend and .fbx from their current folder:
  blender --background --factory-startup --python sanitize_for_publish.py -- models

Python part, strips text metadata from PNG files without touching pixels:
  python sanitize_for_publish.py models
"""

import os
import sys


def strip_png(path):
    data = open(path, "rb").read()
    out, pos, removed = bytearray(data[:8]), 8, 0
    while pos + 8 <= len(data):
        size = int.from_bytes(data[pos:pos + 4], "big")
        kind = data[pos + 4:pos + 8]
        end = pos + 12 + size
        if kind in (b"tEXt", b"zTXt", b"iTXt", b"tIME"):
            removed += 1
        else:
            out += data[pos:end]
        pos = end
    if removed:
        with open(path, "wb") as handle:
            handle.write(out)
    return removed


def walk(root, extension):
    for folder, _, files in os.walk(root):
        for name in sorted(files):
            if name.lower().endswith(extension):
                yield os.path.join(folder, name)


if "--" in sys.argv:
    import addon_utils
    import bpy

    root = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
    for path in list(walk(root, ".blend")):
        bpy.ops.wm.open_mainfile(filepath=path)
        bpy.context.preferences.filepaths.save_version = 0
        addon_utils.enable("io_scene_fbx")
        for scene in bpy.data.scenes:
            scene.render.filepath = "//renders/"
        bpy.ops.wm.save_as_mainfile(filepath=path, compress=False, relative_remap=True)
        bpy.ops.export_scene.fbx(filepath=os.path.splitext(path)[0] + ".fbx", object_types={"MESH", "EMPTY"},
                                 apply_unit_scale=True, bake_space_transform=False, axis_forward="Y", axis_up="Z",
                                 mesh_smooth_type="FACE", use_mesh_modifiers=True, add_leaf_bones=False,
                                 bake_anim=False, path_mode="RELATIVE")
        print("SANITIZED", os.path.basename(path))
else:
    root = os.path.abspath(sys.argv[1])
    count = sum(1 for path in walk(root, ".png") if strip_png(path))
    print("PNG cleaned", count)
    # Blender keeps the default documents folder in each file, so mask the Windows user name.
    user = os.environ.get("USERNAME", "").encode()
    if user:
        for path in walk(root, ".blend"):
            data = open(path, "rb").read()
            if user in data:
                with open(path, "wb") as handle:
                    handle.write(data.replace(user, b"u" * len(user)))
