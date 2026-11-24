"""Repaint the game's Polish riflemen (1944, British battledress) into September 1939 colours.

  blender --background --factory-startup --python retexture_infantry.py -- <extracted POL Infanterie folder> <output folder>

The input folder is POL/Infanterie.zip from Steel Division Modding Assets, unpacked (it holds
Polish_Rifle/ and LODS/). The meshes, skeleton and skin weights stay exactly as they are, so
the game's infantry animations keep working; only the textures change:

  - battledress brown -> greener wz. 36 khaki,
  - light British webbing -> brown leather belts and pouches,
  - the helmet with its camouflage net -> plain olive paint, no badge,
  - the red POLAND shoulder title -> uniform cloth,
  - equipment texture: canvas and webbing -> brown canvas and leather.

The helmet shape stays British; changing it needs mesh edits (see docs/PIECHOTA_1939.md).
Each mesh is copied with its texture names rewritten in the string table (STRG) of the
Ase2NdfBin; every other byte section is kept.

The output is derived from Eugen's game data: keep it out of the repository.
"""

import os
import struct
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blender_addon",
                                "steel_division_ase2ndfbin"))
import ndfbin  # noqa: E402

SRC, OUT = [os.path.abspath(p) for p in sys.argv[sys.argv.index("--") + 1:][:2]]
os.makedirs(OUT, exist_ok=True)

PREFIX_OLD, PREFIX_NEW = "Polish_", "POL39_"
MODELS = [  # mesh, its textures (diffuse stems) and whether the stem is the main uniform atlas
    ("Polish_Rifle/Polish_Rifle", ["Polish_Rifle"]),
    ("Polish_Rifle/Polish_Rifle_2", ["Polish_Rifle_2", "Polish_Rifle_2_equipment"]),
    ("LODS/Polish_Rifle_LOW", ["Polish_Rifle_LOW"]),
    ("LODS/Polish_Rifle_2_LOW", ["Polish_Rifle_2_LOW", "Polish_Rifle_2_equipment_LOW"]),
]
HELMET = (0.527, 0.894, 0.106)   # centre (u, v from the top) and radius of the helmet island
TITLE = (0.72, 0.94, 0.83, 0.995)  # area of the red POLAND shoulder title (u0, v0, u1, v1, from the top)

KHAKI_SHIFT = 8.0       # degrees of hue towards green
LEATHER = np.array([0.27, 0.17, 0.09], np.float32)
HELMET_PAINT = np.array([0.30, 0.31, 0.21], np.float32)
CANVAS = np.array([0.29, 0.26, 0.17], np.float32)


def load(path):
    image = bpy.data.images.load(path)
    w, h = image.size
    px = np.array(image.pixels[:], np.float32).reshape(h, w, 4)[::-1].copy()  # top-down
    bpy.data.images.remove(image)
    return px


def save(path, px):
    h, w = px.shape[:2]
    image = bpy.data.images.new("out", w, h, alpha=True)
    image.pixels.foreach_set(np.ascontiguousarray(px[::-1]).ravel())
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn + 1e-6
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 1e-4, (mx - mn) / (mx + 1e-6), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c
    z = np.zeros_like(h)
    seg = (h // 60).astype(int) % 6
    r = np.choose(seg, [c, x, z, z, x, c])
    g = np.choose(seg, [x, c, c, x, z, z])
    b = np.choose(seg, [z, z, x, c, c, x])
    return np.stack([r + m, g + m, b + m], -1)


def blur(a, radius):
    k = max(1, int(radius))
    out = a.copy()
    for axis in (0, 1):
        acc = np.zeros_like(out)
        for d in range(-k, k + 1):
            acc += np.roll(out, d, axis)
        out = acc / (2 * k + 1)
    return out


def repaint_uniform(px):
    rgb = px[..., :3]
    h, s, v = rgb_to_hsv(rgb)
    hh, ww = v.shape
    vv, uu = np.mgrid[0:hh, 0:ww]
    u, w_ = (uu + 0.5) / ww, (vv + 0.5) / hh
    skin = (h < 30) & (s > 0.22) & (v > 0.35)
    # Classify webbing on a blurred copy, so whole straps and pouches change, not speckles.
    bh, bs, bv = rgb_to_hsv(np.stack([blur(rgb[..., c], 3) for c in range(3)], -1))
    webbing = (bh > 46) & (bh < 75) & (bv > 0.28) & (bs > 0.16)
    cloth = (h >= 25) & (h <= 50) & (s > 0.15) & ~skin & ~webbing
    out = rgb.copy()
    # Battledress -> greener, slightly greyer khaki, detail kept in value.
    nh = np.clip(h + KHAKI_SHIFT, 0, 359)
    out[cloth] = hsv_to_rgb(nh[cloth], s[cloth] * 0.88, v[cloth] * 1.04)
    # Webbing -> leather, value detail kept.
    lum = v[webbing] / max(float(v[webbing].mean()) if webbing.any() else 1.0, 1e-3)
    out[webbing] = LEATHER * np.clip(lum, 0.6, 1.25)[:, None]
    # POLAND title -> cloth colour taken from just above it.
    u0, v0, u1, v1 = TITLE
    box = (u > u0) & (u < u1) & (w_ > v0) & (w_ < v1)
    red = box & ((h < 22) | (h > 330) | (v > 0.6)) & (s > 0.2) | (box & (v > 0.55))
    above = (u > u0) & (u < u1) & (w_ > v0 - 0.05) & (w_ < v0 - 0.01) & cloth
    if above.any():
        out[red] = out[above].mean(0)
    # Helmet island -> plain olive with soft shading from the blurred original.
    cu, cv, r = HELMET
    helmet = (u - cu) ** 2 + (w_ - cv) ** 2 < r ** 2
    shade = blur(v, max(4, hh // 40))
    shade = shade / max(float(shade[helmet].mean()), 1e-3)
    grain = blur(np.random.RandomState(31).rand(hh, ww).astype(np.float32), 1) * 0.10 + 0.95
    out[helmet] = HELMET_PAINT * (np.clip(shade[helmet], 0.88, 1.10) * grain[helmet])[:, None]
    px[..., :3] = np.clip(out, 0, 1)
    return px


def repaint_equipment(px):
    rgb = px[..., :3]
    h, s, v = rgb_to_hsv(rgb)
    gear = (h > 35) & (h < 120) & (v > 0.12) & (s > 0.10)
    lum = v / max(float(v[gear].mean()) if gear.any() else 1.0, 1e-3)
    out = rgb.copy()
    narrow = gear & (v < np.percentile(v[gear], 45) if gear.any() else gear)
    out[gear] = CANVAS * np.clip(lum[gear], 0.55, 1.3)[:, None]
    out[narrow] = LEATHER * np.clip(lum[narrow], 0.55, 1.3)[:, None]
    px[..., :3] = np.clip(out, 0, 1)
    return px


def rewrite_strings(src, dst, renames):
    raw = open(src, "rb").read()
    sections = ndfbin.read_container(raw)
    strings = ndfbin._table(sections["STRG"])
    changed = 0
    for i, text in enumerate(strings):
        base = text.replace("\\", "/").split("/")[-1]
        if base in renames:
            strings[i] = renames[base]
            changed += 1
    sections["STRG"] = b"".join(struct.pack("<I", len(t.encode("latin-1"))) + t.encode("latin-1") for t in strings)
    with open(dst, "wb") as handle:
        handle.write(ndfbin.write_container(sections))
    return changed


for mesh, stems in MODELS:
    renames = {}
    for stem in stems:
        for tag in ("", "_SC", "_GLO"):
            old = "%s%s.png" % (stem, tag)
            new = old.replace(PREFIX_OLD, PREFIX_NEW, 1)
            folder = os.path.dirname(mesh)
            src = os.path.join(SRC, folder, old)
            if not os.path.isfile(src):
                continue
            px = load(src)
            if tag == "":
                px = repaint_equipment(px) if "equipment" in stem else repaint_uniform(px)
            save(os.path.join(OUT, new), px)
            renames[old] = new
    name = os.path.basename(mesh).replace(PREFIX_OLD, PREFIX_NEW, 1)
    changed = rewrite_strings(os.path.join(SRC, mesh + ".Ase2NdfBin"), os.path.join(OUT, name + ".Ase2NdfBin"), renames)
    check = ndfbin.read_objects(open(os.path.join(OUT, name + ".Ase2NdfBin"), "rb").read())
    geoms = sum(len(o.get("GeomObjectList")) for o in check if o.cls == "TMemASE")
    print("RETEX %s textures=%d strings=%d geoms=%d" % (name, len(renames), changed, geoms))
print("RETEX_DONE")
