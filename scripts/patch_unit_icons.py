"""Point the 7TP units of a battlegroup mod at their own interface icons.

  python patch_unit_icons.py <mod folder> <folder with the icons from make_unit_icons.py> <backup folder>

Run it after create_battlegroup.py, then run GenerateMod.bat. It replaces, in the 7TP entries only:
  - the label over the unit and the menu icon (Cromwell V and Stuart pictures) -> TP7_*_RTS.png,
  - the view from above (Cromwell V POL) -> TP7_*_TopView.png,
  - the weapon pictures in the unit panel (Stuart 37 mm, M1919) -> TP7_Bofors37_Weapon.png and
    TP7_CkmWz30_Weapon.png.
Every changed file is copied to the backup folder first. Running it twice changes nothing more.
"""

import os
import re
import shutil
import sys

MOD, ICONS, BACKUP = [os.path.abspath(p) for p in sys.argv[1:4]]
GAMEPLAY = os.path.join(MOD, "GameData", "Gameplay")
GENERATED = os.path.join(GAMEPLAY, "Gfx", "Generated")
LABELS = os.path.join(GAMEPLAY, "Gfx", "LabelDescripors.ndf")
MARKER = "// 7TP mod: interface icons from patch_unit_icons.py"
UNITS = ("TP7_JW_POL", "TP7_DW_POL")
OLD_RTS = ("~/Texture_RTS_H_Cromwell_V", "~/Texture_RTS_H_Stuart_M3A3")
WEAPONS = {
    "Ammo_Bofors_wz37_AP": "Texture_Interface_Weapon_TP7_Bofors37",
    "Ammo_Bofors_wz37_HE": "Texture_Interface_Weapon_TP7_Bofors37",
    "Ammo_ckm_wz30_vehicule": "Texture_Interface_Weapon_TP7_CkmWz30",
}
FILES = ["TP7_JW_RTS.png", "TP7_DW_RTS.png", "TP7_JW_TopView.png", "TP7_DW_TopView.png",
         "TP7_Bofors37_Weapon.png", "TP7_CkmWz30_Weapon.png"]


def read(path):
    with open(path, "rb") as handle:
        return handle.read().decode("latin-1")


def write(path, text):
    if read(path) == text:
        return False
    target = os.path.join(BACKUP, os.path.relpath(path, MOD))
    if not os.path.exists(target):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(path, target)
    with open(path, "wb") as handle:
        handle.write(text.encode("latin-1"))
    print("patched", os.path.relpath(path, MOD))
    return True


def texture(name, file_name):
    return "export %s is TUIResourceTexture_CommonModded\r\n(\r\n    FileName = '%s'\r\n)" % (name, file_name)


def edit_statements(text, wanted, change):
    """Apply change(name, block) to every top-level statement whose name wanted() accepts."""
    starts = [(m.start(), m.group(1)) for m in re.finditer(r"(?m)^(?:export\s+|private\s+)?(\w+)\s+is\b", text)]
    out, last = [], 0
    for k, (start, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(text)
        if wanted(name):
            out.append(text[last:start])
            out.append(change(name, text[start:end]))
            last = end
    out.append(text[last:])
    return "".join(out)


def unit_of(name):
    return next((u for u in UNITS if name.endswith(u)), None)


for file_name in FILES:
    shutil.copy2(os.path.join(ICONS, file_name), os.path.join(MOD, "AssetsModding", file_name))

WEAPON_TEXTURES = [texture("Texture_Interface_Weapon_TP7_Bofors37", "TP7_Bofors37_Weapon.png"),
                   texture("Texture_Interface_Weapon_TP7_CkmWz30", "TP7_CkmWz30_Weapon.png")]

# Unit textures: new RTS icons, and the top views pointed at our files. They live in
# LabelDescripors.ndf because units resolve textures in $/GFX/Everything and do not see new
# objects in the UI texture files.
text = read(LABELS)
for block in WEAPON_TEXTURES:  # an earlier version of this script put them here; ModGen rejected that
    text = text.replace("\r\n\r\n" + block, "")
blocks = [texture("Texture_RTS_" + u, u.replace("_POL", "") + "_RTS.png") for u in UNITS]
if MARKER not in text:
    text = text.rstrip() + "\r\n\r\n" + MARKER + "\r\n" + "\r\n\r\n".join(blocks) + "\r\n"
text = edit_statements(
    text, lambda n: n in ("Texture_TopView_" + u for u in UNITS),
    lambda n, b: texture(n, n.replace("Texture_TopView_", "").replace("_POL", "") + "_TopView.png") + "\r\n\r\n")
write(LABELS, text)

# Units and their wrecks: label and menu icons.
for path in (os.path.join(GENERATED, "UniteDescriptor.ndf"), os.path.join(GENERATED, "UniteCadavreDescriptor.ndf")):
    text = read(path)

    def swap(name, block):
        for old in OLD_RTS:
            block = re.sub(re.escape(old) + r"\b", "~/Texture_RTS_" + unit_of(name), block)
        return block

    write(path, edit_statements(text, unit_of, swap))

# Weapon pictures: ammunition does not see LabelDescripors.ndf (ModGen: "object not found"), so
# they go next to the game's own weapon pictures.
path = os.path.join(GAMEPLAY, "UI", "Resources", "Textures", "Generated", "WeaponTextures.ndf")
text = read(path)
if MARKER not in text:
    write(path, text.rstrip() + "\r\n\r\n" + MARKER + "\r\n" + "\r\n\r\n".join(WEAPON_TEXTURES) + "\r\n")

# Ammunition: the weapon pictures in the unit panel.
path = os.path.join(GENERATED, "Ammunition.ndf")
write(path, edit_statements(
    read(path), lambda n: n in WEAPONS,
    lambda n, b: re.sub(r"(InterfaceWeaponTexture\s*=\s*)\S+", lambda m: m.group(1) + "~/" + WEAPONS[n], b)))

# Check: no Cromwell or Stuart picture left in the 7TP entries.
for path in (os.path.join(GENERATED, "UniteDescriptor.ndf"), os.path.join(GENERATED, "UniteCadavreDescriptor.ndf"),
             os.path.join(GENERATED, "Ammunition.ndf"), LABELS):
    text = read(path)
    edit_statements(text, lambda n: unit_of(n) or n in WEAPONS,
                    lambda n, b: (_ for _ in ()).throw(RuntimeError("leftover in " + n))
                    if re.search(r"~/Texture_\w*(Cromwell_V|Stuart_M3A3|M6_37mmL_Stuart|M1919_7_62mm)\b|TopViews/Cromwell", b)
                    else b)
print("ICONS_PATCHED")
