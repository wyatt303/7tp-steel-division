"""Create unit card images from the model renders.

  python make_unit_cards.py <7TP project folder> <mod AssetsModding folder>
Needs Pillow.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageEnhance

root, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
GAMMA = [round(255 * (value / 255) ** 0.58) for value in range(256)] * 3
for folder, stem in (("7TP_jednowiezowy_Bofors", "TP7_JW"), ("7TP_dwuwiezowy_wz30", "TP7_DW")):
    render = Image.open(os.path.join(root, "models", folder, "renders", "render_przod_3_4.png")).convert("RGB")
    crop = render.crop((90, 25, 1270, 689)).point(GAMMA)
    crop = ImageEnhance.Color(crop).enhance(1.12)
    crop = ImageEnhance.Contrast(crop).enhance(1.10)
    # The small card is shown under a dark interface frame, so it needs extra light.
    button = ImageEnhance.Brightness(crop.resize((256, 144), Image.LANCZOS)).enhance(1.35)
    button.convert("RGBA").save(os.path.join(out, stem + "_Button.png"))
    crop.resize((512, 288), Image.LANCZOS).convert("RGBA").save(os.path.join(out, stem + "_Visual.png"))
    print("cards", stem)


def make_portrait():
    """The commander's portrait if the user supplied one (never published), else the tank."""
    supplied = os.path.join(root, "portret_rowecki.png")
    if os.path.exists(supplied):
        photo = Image.open(supplied).convert("RGB")
        # Frame the face and collar, in the game's 82:101 portrait shape.
        width = round(photo.width * 0.77)
        height = round(width * 505 / 410)
        left = round(photo.width * 0.115)
        top = round(photo.height * 0.01)
        if top + height > photo.height:
            raise ValueError("Portrait is too short for the crop")
        framed = photo.crop((left, top, left + width, top + height)).resize((410, 505), Image.LANCZOS)
        ImageEnhance.Contrast(framed).enhance(1.08).convert("RGBA").save(os.path.join(out, "TP7_Div_Portrait.png"))
        return
    render = Image.open(os.path.join(root, "models", "7TP_jednowiezowy_Bofors", "renders", "render_przod_3_4.png")).convert("RGB")
    crop = render.crop((90, 25, 1270, 689)).point(GAMMA)
    crop = ImageEnhance.Color(crop).enhance(0.55)
    height = 448
    width = round(crop.width * height / crop.height)
    wide = crop.resize((width, height), Image.LANCZOS)
    left = (width - 400) // 2
    portrait = wide.crop((left, 0, left + 400, height))
    shade = Image.new("L", (400, height), 0)
    pixels = shade.load()
    for y in range(height):
        for x in range(400):
            distance = (((x - 200) / 230) ** 2 + ((y - 224) / 260) ** 2) ** 0.5
            pixels[x, y] = round(255 * max(0.22, min(1.0, 1.25 - distance)))
    dark = Image.new("RGB", (400, height), (24, 26, 20))
    Image.composite(portrait, dark, shade).convert("RGBA").save(os.path.join(out, "TP7_Div_Portrait.png"))


def make_emblem():
    """An original white and red shield with a tank outline, not a historical unit badge."""
    scale, size = 4, 256
    s = lambda *points: [(x * scale, y * scale) for x, y in points]
    shield = s((36, 22), (220, 22), (220, 130), (205, 175), (170, 208), (128, 236), (86, 208), (51, 175), (36, 130))
    mask = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(mask).polygon(shield, fill=255)
    art = Image.new("RGB", mask.size, (236, 232, 220))
    draw = ImageDraw.Draw(art)
    draw.rectangle((0, 128 * scale, size * scale, size * scale), fill=(176, 30, 40))
    ink = (24, 26, 22)
    draw.polygon(s((58, 134), (70, 118), (186, 118), (200, 134), (188, 158), (68, 158)), fill=ink)
    draw.polygon(s((98, 118), (106, 96), (150, 96), (158, 118)), fill=ink)
    draw.rectangle((150 * scale, 103 * scale, 204 * scale, 108 * scale), fill=ink)
    for x in range(82, 190, 23):
        draw.ellipse(((x - 8) * scale, 138 * scale, (x + 8) * scale, 154 * scale), fill=(236, 232, 220))
    draw.line(shield + shield[:1], fill=ink, width=5 * scale, joint="curve")
    art = art.convert("RGBA")
    art.putalpha(mask)
    art.resize((size, size), Image.LANCZOS).save(os.path.join(out, "TP7_Div_Emblem.png"))


make_portrait()
make_emblem()
print("division art")
