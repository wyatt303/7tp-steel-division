"""Create the unit card images and the battlegroup art from the model renders.

  blender --background --factory-startup --python make_unit_cards.py -- <project folder> <mod AssetsModding folder>

Runs in Blender (numpy and bpy images only), so nothing has to be installed.

  TP7_JW_Button.png, TP7_DW_Button.png   256 x 144  card in the deck and the purchase bar
  TP7_JW_Visual.png, TP7_DW_Visual.png   512 x 288  large picture in the unit window
  TP7_Div_Portrait.png                   410 x 505  battlegroup portrait: the commander's photo
                                                    if portret_rowecki.png is present (never
                                                    published), otherwise the tank
  TP7_Div_Emblem.png                     256 x 256  an original white and red shield with a
                                                    tank outline, not a historical unit badge
"""

import os
import sys

import bpy
import numpy as np

ROOT, OUT = [os.path.abspath(p) for p in sys.argv[sys.argv.index("--") + 1:][:2]]
os.makedirs(OUT, exist_ok=True)
CARDS = (("7TP_jednowiezowy_Bofors", "TP7_JW"), ("7TP_dwuwiezowy_wz30", "TP7_DW"), ("TKS20", "TKS20"), ("P11C", "P11C"),
         ("WZ36_BOFORS", "WZ36_BOFORS"), ("PF621L", "PF621L"), ("PF621L_OPEN", "PF621L_OPEN"), ("C2P", "C2P"),
         ("../build/generated/B40WZ36", "B40WZ36"))
LUMA = np.array([0.299, 0.587, 0.114], np.float32)


def load(path):
    """RGB float array, top row first, in display (sRGB) values."""
    image = bpy.data.images.load(path)
    image.colorspace_settings.name = "Non-Color"
    w, h = image.size
    px = np.array(image.pixels[:], np.float32).reshape(h, w, 4)[::-1, :, :3].copy()
    bpy.data.images.remove(image)
    return px


def resize(px, width, height):
    """Area-average resize through a Blender image."""
    h, w = px.shape[:2]
    image = bpy.data.images.new("resize", w, h, alpha=True, float_buffer=True)
    image.colorspace_settings.name = "Non-Color"
    rgba = np.concatenate([px, np.ones((h, w, 1), np.float32)], -1)
    image.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    image.scale(width, height)
    out = np.array(image.pixels[:], np.float32).reshape(height, width, 4)[::-1, :, :3].copy()
    bpy.data.images.remove(image)
    return out


def save(px, name, alpha=None):
    h, w = px.shape[:2]
    a = np.ones((h, w, 1), np.float32) if alpha is None else alpha[..., None]
    image = bpy.data.images.new(name, w, h, alpha=True)
    image.colorspace_settings.name = "Non-Color"
    # These go straight into the mod's AssetsModding, which ModGen compiles as sRGB and the game
    # then shows darker; passing the colours through the sRGB curve cancels that (png_srgb.py).
    c = np.clip(px, 0, 1)
    c = np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
    rgba = np.concatenate([c, a], -1).astype(np.float32)
    image.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    image.filepath_raw = os.path.join(OUT, name)
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
    print("CARD", name, w, h)


def colour(px, factor):
    gray = (px @ LUMA)[..., None]
    return gray + factor * (px - gray)


def contrast(px, factor):
    mean = float((px @ LUMA).mean())
    return mean + factor * (px - mean)


def tank_crop(folder):
    render = load(os.path.join(ROOT, "models", folder, "renders", "render_przod_3_4.png"))
    crop = render[25:689, 90:1270] ** 0.58  # lift the dark render, as the game's cards are bright
    return np.clip(contrast(colour(crop, 1.12), 1.10), 0, 1)


for folder, stem in CARDS:
    crop = tank_crop(folder)
    # The small card is shown under a dark interface frame, so it needs extra light.
    save(resize(crop, 256, 144) * 1.35, stem + "_Button.png")
    save(resize(crop, 512, 288), stem + "_Visual.png")


def make_portrait():
    supplied = os.path.join(ROOT, "portret_rowecki.png")
    if os.path.exists(supplied):
        photo = load(supplied)
        ph, pw = photo.shape[:2]
        # Frame the face and collar, in the game's 82:101 portrait shape.
        width = round(pw * 0.77)
        height = round(width * 505 / 410)
        left, top = round(pw * 0.115), round(ph * 0.01)
        if top + height > ph:
            raise ValueError("Portrait is too short for the crop")
        framed = resize(photo[top:top + height, left:left + width], 410, 505)
        save(contrast(framed, 1.08), "TP7_Div_Portrait.png")
        return
    crop = colour(tank_crop(CARDS[0][0]), 0.55 / 1.12)
    height = 448
    width = round(crop.shape[1] * height / crop.shape[0])
    wide = resize(crop, width, height)
    left = (width - 400) // 2
    portrait = wide[:, left:left + 400]
    yy, xx = np.mgrid[0:height, 0:400]
    distance = np.sqrt(((xx - 200) / 230) ** 2 + ((yy - 224) / 260) ** 2)
    shade = np.clip(1.25 - distance, 0.22, 1.0)[..., None]
    dark = np.array([24, 26, 20], np.float32) / 255
    save(portrait * shade + dark * (1 - shade), "TP7_Div_Portrait.png")


def inside(points, xx, yy):
    result = np.zeros(xx.shape, bool)
    for i in range(len(points)):
        (x1, y1), (x2, y2) = points[i], points[(i + 1) % len(points)]
        crosses = (y1 > yy) != (y2 > yy)
        result ^= crosses & (xx < (x2 - x1) * (yy - y1) / (y2 - y1 + 1e-12) + x1)
    return result


def near_outline(points, xx, yy, width):
    best = np.full(xx.shape, 1e9, np.float32)
    for i in range(len(points)):
        (x1, y1), (x2, y2) = points[i], points[(i + 1) % len(points)]
        dx, dy = x2 - x1, y2 - y1
        t = np.clip(((xx - x1) * dx + (yy - y1) * dy) / (dx * dx + dy * dy), 0, 1)
        best = np.minimum(best, np.hypot(xx - (x1 + t * dx), yy - (y1 + t * dy)))
    return best <= width / 2


def make_emblem():
    """Drawn at 4x on a 256 grid and averaged down."""
    scale, size = 4, 256
    yy, xx = (np.mgrid[0:size * scale, 0:size * scale] + 0.5) / scale
    shield = [(36, 22), (220, 22), (220, 130), (205, 175), (170, 208), (128, 236), (86, 208), (51, 175), (36, 130)]
    paper = np.array([236, 232, 220], np.float32) / 255
    ink = np.array([24, 26, 22], np.float32) / 255
    art = np.empty(xx.shape + (3,), np.float32)
    art[:] = paper
    art[yy >= 128] = np.array([176, 30, 40], np.float32) / 255
    art[inside([(58, 134), (70, 118), (186, 118), (200, 134), (188, 158), (68, 158)], xx, yy)] = ink
    art[inside([(98, 118), (106, 96), (150, 96), (158, 118)], xx, yy)] = ink
    art[(xx >= 150) & (xx <= 204) & (yy >= 103) & (yy <= 108)] = ink
    for x in range(82, 190, 23):
        art[((xx - x) / 8) ** 2 + ((yy - 146) / 8) ** 2 <= 1] = paper
    art[near_outline(shield, xx, yy, 5)] = ink
    alpha = (inside(shield, xx, yy) | near_outline(shield, xx, yy, 5)).astype(np.float32)
    small = art.reshape(size, scale, size, scale, 3).mean((1, 3))
    small_alpha = alpha.reshape(size, scale, size, scale).mean((1, 3))
    save(small, "TP7_Div_Emblem.png", small_alpha)


make_portrait()
make_emblem()
print("CARDS_DONE")
