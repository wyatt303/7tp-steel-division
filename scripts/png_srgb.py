"""Pre-compensate interface pictures for the way ModGen compiles mod textures.

ModGen compiles every picture of a mod's AssetsModding folder as A8R8G8B8_SRGB (texture type
TSCInterfaceModding), while the game's own interface pictures are A8R8G8B8_LIN. The interface
then decodes our pictures from sRGB to linear once more and shows them much darker than the file
(found on 26 November 2026 with the 7TP and TKS cards). Writing the picture through the sRGB
encoding curve first cancels that: the game shows exactly the colours of the original file.

  compensate(source, target)   copy a PNG, with its colour channels passed through the curve

Pure Python (zlib only), so it runs with any Python. 8-bit greyscale, RGB, palette, grey+alpha
and RGBA PNGs are handled; anything else is copied unchanged with a note.
"""

import shutil
import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _encode(value):
    c = value / 255.0
    s = c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return max(0, min(255, round(s * 255)))


CURVE = bytes(_encode(v) for v in range(256))


def _chunks(data):
    pos = len(SIGNATURE)
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        yield kind, data[pos + 8:pos + 8 + length]
        pos += 12 + length


def _chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def _unfilter(raw, width, height, bpp):
    stride = width * bpp
    out = bytearray(stride * height)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if kind == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif kind == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif kind == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        elif kind != 0:
            raise ValueError("unknown PNG filter %d" % kind)
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out


def compensate(source, target):
    data = open(source, "rb").read()
    if data[:8] != SIGNATURE:
        raise ValueError("not a PNG: " + source)
    chunks = list(_chunks(data))
    header = dict(chunks)[b"IHDR"]
    width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", header)
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(colour)
    if depth != 8 or interlace or channels is None:
        print("note: %s is not an 8-bit plain PNG, copied without the sRGB correction" % source)
        shutil.copyfile(source, target)
        return
    out = [SIGNATURE]
    if colour == 3:
        # Palette: correct the palette entries, keep the pixel data.
        for kind, body in chunks:
            out.append(_chunk(kind, body.translate(CURVE) if kind == b"PLTE" else body))
        open(target, "wb").write(b"".join(out))
        return
    raw = zlib.decompress(b"".join(body for kind, body in chunks if kind == b"IDAT"))
    pixels = _unfilter(raw, width, height, channels)
    colour_channels = {1: 1, 2: 1, 3: 3, 4: 3}[channels]
    for c in range(colour_channels):
        pixels[c::channels] = pixels[c::channels].translate(CURVE)
    stride = width * channels
    rows = b"".join(b"\x00" + bytes(pixels[y * stride:(y + 1) * stride]) for y in range(height))
    out.append(_chunk(b"IHDR", header))
    out.append(_chunk(b"IDAT", zlib.compress(rows, 9)))
    out.append(_chunk(b"IEND", b""))
    open(target, "wb").write(b"".join(out))
