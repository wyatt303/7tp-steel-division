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
    "P11C": ("P11C", "POL/Avion"),  # with P11C_train (landing-gear points)
    "WZ36_BOFORS": ("WZ36_BOFORS", "POL/Canon"),  # with Boites_WZ36_BOFORS (crew positions)
    "PF621L": ("PF621L", "POL/Vehicule"),  # Polski Fiat 621L with the tilt (tractor of the wz. 36)
    "PF621L_OPEN": ("PF621L_OPEN", "POL/Vehicule"),  # without the tilt (tractor of the 40 mm wz. 36)
    "C2P": ("C2P", "POL/Vehicule"),  # C2P tracked tractor (tows the 40 mm wz. 36)
    # 40 mm wz. 36 Bofors: made from the game's Bofors by build_bofors40.py, kept in build/ (game data).
    "B40WZ36": ("../build/generated/B40WZ36", "POL/Canon"),  # with Boites_B40WZ36
}

failed = 0
for stem, (folder, kind) in MODELS.items():
    target = os.path.join(MOD, "GameData", "Assets", "3D", "Units", *kind.split("/"), stem)
    os.makedirs(target, exist_ok=True)
    suffixes = ["", "_MID", "_LOW"]
    if os.path.exists(os.path.join(ROOT, "models", folder, stem + "_train.blend")):
        suffixes.append("_train")  # aircraft landing-gear file (see create_battlegroup.py, train_model)
    files = [stem + suffix for suffix in suffixes]
    if os.path.exists(os.path.join(ROOT, "models", folder, "Boites_" + stem + ".blend")):
        files.append("Boites_" + stem)  # towed gun: crew positions (see create_battlegroup.py, gun_depiction)
    for file_stem in files:
        source = os.path.join(ROOT, "models", folder, file_stem + ".blend")
        bpy.ops.wm.open_mainfile(filepath=source)
        try:
            result = exporter.export_scene(bpy.context.scene, os.path.join(target, file_stem + ".Ase2NdfBin"),
                                           exporter.DEFAULT_SCALE, True)
        except exporter.ExportProblem as problem:
            failed += 1
            print("EXPORT_FAILED", file_stem, "; ".join(problem.errors))
            continue
        print("EXPORTED", file_stem, result["triangles"], "triangles", "; ".join(result["warnings"]))
print("EXPORT_DONE" if not failed else "EXPORT_ERRORS %d" % failed)
