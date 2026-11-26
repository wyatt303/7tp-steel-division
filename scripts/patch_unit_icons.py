"""Point our units of a battlegroup mod at their own interface icons.

  python patch_unit_icons.py <mod folder> <folder with the icons from make_unit_icons.py> <backup folder>

Run it after create_battlegroup.py, then run GenerateMod.bat. It replaces, in our entries only
(the units of data/units.toml and their ammunition):
  - the label over the unit and the menu icon (Cromwell V and Stuart pictures) -> <model>_RTS.png,
  - the view from above -> <model>_TopView.png,
  - the weapon pictures in the unit panel -> TP7_Bofors37_Weapon.png, TP7_CkmWz30_Weapon.png,
    TKS20_Nkm20_Weapon.png.
Every changed file is copied to the backup folder first. Running it twice changes nothing more.
"""

import os
import re
import shutil
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import png_srgb  # noqa: E402  (ModGen shows mod pictures darker; see png_srgb.py)

MOD, ICONS, BACKUP = [os.path.abspath(p) for p in sys.argv[1:4]]
GAMEPLAY = os.path.join(MOD, "GameData", "Gameplay")
GENERATED = os.path.join(GAMEPLAY, "Gfx", "Generated")
LABELS = os.path.join(GAMEPLAY, "Gfx", "LabelDescripors.ndf")
MARKER = "// 7TP mod: interface icons from patch_unit_icons.py"
SETTINGS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "units.toml")
with open(SETTINGS, "rb") as _handle:
    UNITS = {name: info["model"] for name, info in tomllib.load(_handle)["units"].items()}  # unit -> model stem
OLD_RTS = ("~/Texture_RTS_H_Cromwell_V", "~/Texture_RTS_H_Stuart_M3A3")
WEAPON_PICTURES = {  # texture -> picture file
    "Texture_Interface_Weapon_TP7_Bofors37": "TP7_Bofors37_Weapon.png",
    "Texture_Interface_Weapon_TP7_CkmWz30": "TP7_CkmWz30_Weapon.png",
    "Texture_Interface_Weapon_TKS20_Nkm20": "TKS20_Nkm20_Weapon.png",
}
WEAPONS = {  # ammunition -> texture
    "Ammo_Bofors_wz37_AP": "Texture_Interface_Weapon_TP7_Bofors37",
    "Ammo_Bofors_wz37_HE": "Texture_Interface_Weapon_TP7_Bofors37",
    "Ammo_ckm_wz30_vehicule": "Texture_Interface_Weapon_TP7_CkmWz30",
    "Ammo_nkm_wz38_AP": "Texture_Interface_Weapon_TKS20_Nkm20",
    "Ammo_nkm_wz38_HE": "Texture_Interface_Weapon_TKS20_Nkm20",
}
FILES = ([stem + "_RTS.png" for stem in UNITS.values()] + [stem + "_TopView.png" for stem in UNITS.values()]
         + list(WEAPON_PICTURES.values()))


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
    png_srgb.compensate(os.path.join(ICONS, file_name), os.path.join(MOD, "AssetsModding", file_name))

WEAPON_TEXTURES = [texture(name, file_name) for name, file_name in WEAPON_PICTURES.items()]

# Unit textures: new RTS icons, and the top views pointed at our files. They live in
# LabelDescripors.ndf because units resolve textures in $/GFX/Everything and do not see new
# objects in the UI texture files.
text = read(LABELS)
for block in WEAPON_TEXTURES:  # an earlier version of this script put them here; ModGen rejected that
    text = text.replace("\r\n\r\n" + block, "")
blocks = [texture("Texture_RTS_" + u, stem + "_RTS.png") for u, stem in UNITS.items()]
if MARKER not in text:
    text = text.rstrip() + "\r\n\r\n" + MARKER + "\r\n" + "\r\n\r\n".join(blocks) + "\r\n"
text = edit_statements(
    text, lambda n: n in ("Texture_TopView_" + u for u in UNITS),
    lambda n, b: texture(n, UNITS[n.replace("Texture_TopView_", "")] + "_TopView.png") + "\r\n\r\n")
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

# Check: no picture of the copied game units left in our entries.
for path in (os.path.join(GENERATED, "UniteDescriptor.ndf"), os.path.join(GENERATED, "UniteCadavreDescriptor.ndf"),
             os.path.join(GENERATED, "Ammunition.ndf"), LABELS):
    text = read(path)
    edit_statements(text, lambda n: unit_of(n) or n in WEAPONS,
                    lambda n, b: (_ for _ in ()).throw(RuntimeError("leftover in " + n))
                    if re.search(r"~/Texture_\w*(Cromwell_V|Stuart_M3A3|M6_37mmL_Stuart|M1919_7_62mm|KwK_38L55_20mm\w*)\b"
                                 r"|TopViews/(Cromwell|Stuart)", b)
                    else b)
print("ICONS_PATCHED")
