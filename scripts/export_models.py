"""Export the battlegroup's models from models/ into a mod with our Blender add-on.

  blender --background --factory-startup --python export_models.py -- <project folder> <mod folder>

Each model goes to GameData/Assets/3D/Units/<nation>/<kind>/<stem>/ as <stem>.Ase2NdfBin,
<stem>_MID.Ase2NdfBin and <stem>_LOW.Ase2NdfBin, with its textures copied next to them.
Only the models that create_battlegroup.py turns into units are listed.
"""

import os
import sys

import bpy

ROOT, MOD = [os.path.abspath(p) for p in sys.argv[sys.argv.index("--") + 1:][:2]]
sys.path.insert(0, os.path.join(ROOT, "blender_addon"))
from steel_division_ase2ndfbin import exporter  # noqa: E402

# stem: (folder in models/, folder in the game's asset tree)
MODELS = {
    "TP7_JW": ("7TP_jednowiezowy_Bofors", "POL/Char"),
    "TP7_DW": ("7TP_dwuwiezowy_wz30", "POL/Char"),
    "TKS20": ("TKS20", "POL/Char"),
}

failed = 0
for stem, (folder, kind) in MODELS.items():
    target = os.path.join(MOD, "GameData", "Assets", "3D", "Units", *kind.split("/"), stem)
    os.makedirs(target, exist_ok=True)
    for suffix in ("", "_MID", "_LOW"):
        source = os.path.join(ROOT, "models", folder, stem + suffix + ".blend")
        bpy.ops.wm.open_mainfile(filepath=source)
        try:
            result = exporter.export_scene(bpy.context.scene, os.path.join(target, stem + suffix + ".Ase2NdfBin"),
                                           exporter.DEFAULT_SCALE, True)
        except exporter.ExportProblem as problem:
            failed += 1
            print("EXPORT_FAILED", stem + suffix, "; ".join(problem.errors))
            continue
        print("EXPORTED", stem + suffix, result["triangles"], "triangles", "; ".join(result["warnings"]))
print("EXPORT_DONE" if not failed else "EXPORT_ERRORS %d" % failed)
