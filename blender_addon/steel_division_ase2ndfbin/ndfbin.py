"""Reader and writer for Eugen .Ase2NdfBin files (EUG0/CNDF container, NDF object graph).

The format was worked out from the files in Steel Division Modding Assets.
"""

import collections
import struct
import zlib

BOOL, INT, UINT, FLOAT, STRING, REF, VEC3, TRIPLE, MATRIX, LIST, MAP = 0, 2, 3, 5, 7, 9, 0xB, 0xE, 0xF, 0x11, 0x12
END = 0xABABABAB
OBJECT_REF = 0xBBBBBBBB
ORDER = ("OBJE", "TOPO", "CHNK", "CLAS", "PROP", "STRG", "TRAN", "IMPR", "EXPR")
FILE_STRING = 0x1C
FIXED = {BOOL: 1, 1: 1, INT: 4, UINT: 4, FLOAT: 4, 6: 8, STRING: 4, VEC3: 12, 0xC: 16, 0xD: 4, TRIPLE: 12, MATRIX: 64,
         0x18: 2, 0x19: 2, 0x1A: 16, FILE_STRING: 4}


class Obj:
    """One NDF object. Fields keep their order, zero values may simply be left out."""

    __slots__ = ("cls", "fields")

    def __init__(self, cls, *fields):
        self.cls = cls
        self.fields = list(fields)

    def add(self, name, kind, value):
        self.fields.append((name, kind, value))
        return self

    def get(self, name, default=None):
        for label, _, value in self.fields:
            if label == name:
                return value
        return default


def _children(kind, value):
    if kind == REF:
        yield value
    elif kind == LIST:
        for item_kind, item in value:
            yield from _children(item_kind, item)
    elif kind == MAP:
        for key_kind, key, value_kind, item in value:
            yield from _children(key_kind, key)
            yield from _children(value_kind, item)


def serialize(root):
    """Number objects breadth first, the order Eugen's exporter uses, and build every table."""
    order, ids, queue = [], {}, collections.deque([root])
    ids[id(root)] = 0
    while queue:
        obj = queue.popleft()
        order.append(obj)
        for _, kind, value in obj.fields:
            for child in _children(kind, value):
                if id(child) not in ids:
                    ids[id(child)] = len(ids)
                    queue.append(child)

    classes, props, strings = {}, {}, {}

    def class_id(name):
        return classes.setdefault(name, len(classes))

    def string_id(text):
        return strings.setdefault(text, len(strings))

    for obj in order:
        class_id(obj.cls)

    def encode(out, kind, value):
        if kind == BOOL:
            out += b"\x01" if value else b"\x00"
        elif kind == INT:
            out += struct.pack("<i", value)
        elif kind == UINT:
            out += struct.pack("<I", value)
        elif kind == FLOAT:
            out += struct.pack("<f", value)
        elif kind == STRING:
            out += struct.pack("<I", string_id(value))
        elif kind == VEC3:
            out += struct.pack("<3f", *value)
        elif kind == TRIPLE:
            out += struct.pack("<3I", *value)
        elif kind == MATRIX:
            out += struct.pack("<16f", *value)
        elif kind == REF:
            out += struct.pack("<III", OBJECT_REF, ids[id(value)], classes[value.cls])
        elif kind == LIST:
            out += struct.pack("<I", len(value))
            for item_kind, item in value:
                out += struct.pack("<I", item_kind)
                encode(out, item_kind, item)
        elif kind == MAP:
            out += struct.pack("<I", len(value))
            for key_kind, key, value_kind, item in value:
                out += struct.pack("<I", key_kind)
                encode(out, key_kind, key)
                out += struct.pack("<I", value_kind)
                encode(out, value_kind, item)
        else:
            raise ValueError("Cannot write NDF type 0x%X" % kind)

    objects = bytearray()
    for obj in order:
        objects += struct.pack("<I", classes[obj.cls])
        for name, kind, value in obj.fields:
            prop = props.setdefault((name, classes[obj.cls]), len(props))
            objects += struct.pack("<II", prop, kind)
            encode(objects, kind, value)
        objects += struct.pack("<I", END)

    def text_table(values):
        out = bytearray()
        for text in values:
            raw = text.encode("latin-1", "replace")
            out += struct.pack("<I", len(raw)) + raw
        return bytes(out)

    prop_table = bytearray()
    for name, owner in props:
        raw = name.encode("latin-1")
        prop_table += struct.pack("<I", len(raw)) + raw + struct.pack("<I", owner)

    return {
        "OBJE": bytes(objects),
        "TOPO": bytes(4),
        "CHNK": struct.pack("<II", 0, len(order)),
        "CLAS": text_table(classes),
        "PROP": bytes(prop_table),
        "STRG": text_table(strings),
        "TRAN": b"",
        "IMPR": b"",
        "EXPR": b"",
    }


def write_container(sections):
    payload, entries, offset = bytearray(), [], 40
    for name in ORDER:
        block = sections[name]
        entries.append((name, offset, len(block)))
        payload += block
        offset += len(block)
    toc = bytearray(b"TOC0" + struct.pack("<I", len(entries)))
    for name, start, size in entries:
        toc += name.encode() + struct.pack("<IQQ", 0, start, size)
    body = bytes(payload + toc)
    compressor = zlib.compressobj(9)
    stream = compressor.compress(body) + compressor.flush(zlib.Z_SYNC_FLUSH)
    return b"EUG0" + bytes(4) + b"CNDF" + struct.pack("<IQQQI", 0x80, offset, 40, 40 + len(body), len(body)) + stream


def write_file(path, root):
    data = write_container(serialize(root))
    with open(path, "wb") as handle:
        handle.write(data)
    return len(data)


def read_container(raw):
    if raw[:4] != b"EUG0" or raw[8:12] != b"CNDF":
        raise ValueError("Not an Ase2NdfBin file")
    footer, header, _ = struct.unpack_from("<QQQ", raw, 0x10)
    inflater = zlib.decompressobj()
    body = inflater.decompress(raw[0x2C:]) + inflater.flush()
    pos = footer - header
    count = struct.unpack_from("<I", body, pos + 4)[0]
    sections = {}
    for i in range(count):
        name = body[pos + 8 + i * 24:pos + 12 + i * 24].decode()
        _, start, size = struct.unpack_from("<IQQ", body, pos + 12 + i * 24)
        sections[name] = body[start - header:start - header + size]
    return sections


def _table(block):
    out, p = [], 0
    while p + 4 <= len(block):
        n = struct.unpack_from("<I", block, p)[0]
        out.append(block[p + 4:p + 4 + n].decode("latin-1"))
        p += 4 + n
    return out


def read_objects(raw):
    """Return a list of Obj. References are replaced by the objects they point to."""
    sections = read_container(raw)
    classes, strings = _table(sections["CLAS"]), _table(sections["STRG"])
    block, p, props = sections["PROP"], 0, []
    while p < len(block):
        n = struct.unpack_from("<I", block, p)[0]
        props.append(block[p + 4:p + 4 + n].decode("latin-1"))
        p += 8 + n
    data, pos = sections["OBJE"], 0

    def u32():
        nonlocal pos
        value = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        return value

    def value(kind):
        nonlocal pos
        if kind in FIXED:
            raw_value = data[pos:pos + FIXED[kind]]
            pos += FIXED[kind]
            if kind == BOOL:
                return raw_value != b"\0"
            if kind == INT:
                return struct.unpack("<i", raw_value)[0]
            if kind == UINT:
                return struct.unpack("<I", raw_value)[0]
            if kind == FLOAT:
                return struct.unpack("<f", raw_value)[0]
            if kind in (STRING, FILE_STRING):
                index = struct.unpack("<I", raw_value)[0]
                return strings[index] if index < len(strings) else "<string %d>" % index
            if kind == VEC3:
                return struct.unpack("<3f", raw_value)
            if kind == TRIPLE:
                return struct.unpack("<3I", raw_value)
            if kind == MATRIX:
                return struct.unpack("<16f", raw_value)
            return raw_value
        if kind == 0x14:
            n = u32()
            blob = data[pos:pos + n]
            pos += n
            return blob
        if kind == REF:
            tag = u32()
            if tag == 0xAAAAAAAA:
                return ("external", u32())
            if tag != OBJECT_REF:
                raise ValueError("Unsupported reference tag %08X" % tag)
            index = u32()
            u32()
            return index
        if kind == LIST:
            items = []
            for _ in range(u32()):
                item_kind = u32()
                items.append((item_kind, value(item_kind)))
            return items
        if kind == MAP:
            items = []
            for _ in range(u32()):
                key_kind = u32()
                key = value(key_kind)
                value_kind = u32()
                items.append((key_kind, key, value_kind, value(value_kind)))
            return items
        raise ValueError("Unknown NDF type 0x%X" % kind)

    objects = []
    while pos < len(data):
        obj = Obj(classes[u32()])
        while True:
            prop = u32()
            if prop == END:
                break
            kind = u32()
            obj.fields.append((props[prop], kind, value(kind)))
        objects.append(obj)

    def link(kind, item):
        if kind == REF:
            return item if isinstance(item, tuple) else objects[item]
        if kind == LIST:
            return [(k, link(k, v)) for k, v in item]
        if kind == MAP:
            return [(a, link(a, b), c, link(c, d)) for a, b, c, d in item]
        return item

    for obj in objects:
        obj.fields = [(name, kind, link(kind, item)) for name, kind, item in obj.fields]
    return objects
