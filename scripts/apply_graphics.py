"""Copy hand-made interface graphics from graphic/ into a mod, over the generated ones.

  python apply_graphics.py <project folder> <mod folder>

Layout of graphic/ (any file may be missing; then the generated picture stays):

  graphic/<STEM>/RTS.png        42 x 26   label over the unit and menu icon  -> <STEM>_RTS.png
  graphic/<STEM>/TopView.png   100 x 75   view from above                    -> <STEM>_TopView.png
  graphic/<STEM>/Button.png    160 x 82   card in the deck and purchase bar  -> <STEM>_Button.png
  graphic/<STEM>/Visual.png    388 x 224  large picture in the unit window   -> <STEM>_Visual.png
  graphic/<STEM>/Turret.png    132 x 50   the turret with its main gun, shown for the main gun in
                                          the unit panel, as the game does for its tanks
                                          -> see TURRET_FILES
  graphic/weapons/<WEAPON>.png 132 x 50   weapon picture in the unit panel   -> see WEAPON_FILES
  graphic/battlegroup/Emblem.png    256 x 256                                -> TP7_Div_Emblem.png
  graphic/battlegroup/Portrait.png  410 x 505                                -> TP7_Div_Portrait.png

<STEM> is the file name of the model in models/ (TP7_JW, TP7_DW, TKS, ...). The sizes are those
of the game's own pictures; another size only gives a warning, because the game scales them.
Everything lands in the mod's AssetsModding folder under the names the mod's NDF files already
use, so no NDF file changes. Run GenerateMod.bat afterwards.
"""

import os
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import png_srgb  # noqa: E402  (ModGen shows mod pictures darker; see png_srgb.py)

ROOT, MOD = [os.path.abspath(p) for p in sys.argv[1:3]]
GRAPHIC = os.path.join(ROOT, "graphic")
ASSETS = os.path.join(MOD, "AssetsModding")

UNIT_FILES = {"RTS.png": ("RTS", (42, 26)), "TopView.png": ("TopView", (100, 75)),
              "Button.png": ("Button", (160, 82)), "Visual.png": ("Visual", (388, 224))}
# Unit -> picture file of its main gun (the panel shows the turret for it).
TURRET_FILES = {"TP7_JW": "TP7_Bofors37_Weapon.png", "TKS20": "TKS20_Nkm20_Weapon.png",
                "WZ36_BOFORS": "WZ36_Bofors37_Weapon.png"}  # towed gun: the whole gun
# Weapon name (as in create_battlegroup.py) -> picture file used by the mod, for weapons shown
# on their own, such as machine guns.
WEAPON_FILES = {"CkmWz30": "TP7_CkmWz30_Weapon.png"}
BATTLEGROUP_FILES = {"Emblem.png": ("TP7_Div_Emblem.png", (256, 256)),
                     "Portrait.png": ("TP7_Div_Portrait.png", (410, 505))}


def png_size(path):
    with open(path, "rb") as handle:
        head = handle.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def place(source, target_name, size, used):
    actual = png_size(source)
    rel = os.path.relpath(source, ROOT)
    if actual is None:
        print("SKIP %s: not a PNG file" % rel)
        return
    if actual != size:
        print("WARN %s is %dx%d, the game's own pictures are %dx%d" % (rel, actual[0], actual[1], size[0], size[1]))
    png_srgb.compensate(source, os.path.join(ASSETS, target_name))
    used.append(rel)
    print("GRAPHIC %s -> AssetsModding/%s" % (rel, target_name))


if not os.path.isdir(ASSETS):
    sys.exit("No AssetsModding folder in " + MOD)
used, unknown = [], []
if os.path.isdir(GRAPHIC):
    for entry in sorted(os.listdir(GRAPHIC)):
        folder = os.path.join(GRAPHIC, entry)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            source = os.path.join(folder, name)
            if not name.lower().endswith(".png"):
                continue
            if entry == "weapons":
                weapon = os.path.splitext(name)[0]
                if weapon in WEAPON_FILES:
                    place(source, WEAPON_FILES[weapon], (132, 50), used)
                else:
                    unknown.append(os.path.relpath(source, ROOT))
            elif entry == "battlegroup":
                if name in BATTLEGROUP_FILES:
                    target, size = BATTLEGROUP_FILES[name]
                    place(source, target, size, used)
                else:
                    unknown.append(os.path.relpath(source, ROOT))
            elif name == "Turret.png":
                if entry in TURRET_FILES:
                    place(source, TURRET_FILES[entry], (132, 50), used)
                else:
                    unknown.append(os.path.relpath(source, ROOT) + " (no main gun picture for " + entry + ")")
            elif name in UNIT_FILES:
                kind, size = UNIT_FILES[name]
                target = "%s_%s.png" % (entry, kind)
                if not os.path.exists(os.path.join(ASSETS, target)):
                    # No unit uses this picture yet (the model is not in the battlegroup).
                    unknown.append(os.path.relpath(source, ROOT) + " (no unit " + entry + " in the mod)")
                    continue
                place(source, target, size, used)
            else:
                unknown.append(os.path.relpath(source, ROOT))
for item in unknown:
    print("UNUSED %s" % item)
print("GRAPHICS_DONE %d own files" % len(used))
