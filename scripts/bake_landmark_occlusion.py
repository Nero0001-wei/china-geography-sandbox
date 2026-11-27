"""Bake short-range, cosine-weighted ambient occlusion for the web landmark meshes.

From the project root, run:
  blender --background --factory-startup --python-exit-code 1 --python scripts/bake_landmark_occlusion.py
The original GLBs stay editable and the website can load them without the optional sidecar.
"""
import json
import math
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import zlib

from mathutils import Vector
from mathutils.bvhtree import BVHTree

MODELS = Path(__file__).resolve().parents[1] / 'app/public/models'
SAMPLES = 32
GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))
HEMISPHERE = []
for k in range(SAMPLES):
    r = math.sqrt((k + 0.5) / SAMPLES)
    HEMISPHERE.append((r * math.cos(k * GOLDEN_ANGLE), r * math.sin(k * GOLDEN_ANGLE),
                       math.sqrt(1 - r * r)))


def accessor(doc, binary, index):
    a = doc['accessors'][index]
    view = doc['bufferViews'][a['bufferView']]
    component = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}[a['componentType']]
    row = struct.Struct('<' + component * {'SCALAR': 1, 'VEC3': 3}[a['type']])
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = view.get('byteStride', row.size)
    if stride == row.size:
        raw = binary[start:start + row.size * a['count']]
    else:
        raw = b''.join(binary[start + i * stride:start + i * stride + row.size] for i in range(a['count']))
    return list(row.iter_unpack(raw)), raw


def bake_mesh(doc, mesh, binary, weights):
    verts, triangles, parts = [], [], []
    for prim in mesh['primitives']:
        attrs = prim['attributes']
        pos, pos_bytes = accessor(doc, binary, attrs['POSITION'])
        normals, normal_bytes = accessor(doc, binary, attrs['NORMAL'])
        if 'indices' in prim:
            indices, index_bytes = accessor(doc, binary, prim['indices'])
            indices = [v[0] for v in indices]
        else:
            indices, index_bytes = list(range(len(pos))), b''
        if prim.get('mode', 4) != 4 or len(indices) % 3:
            raise ValueError('Expected triangulated landmark geometry')
        start = len(verts)
        triangles.extend(tuple(start + j for j in indices[i:i + 3]) for i in range(0, len(indices), 3))
        verts.extend(pos)
        checksum = zlib.crc32(index_bytes, zlib.crc32(normal_bytes, zlib.crc32(pos_bytes)))
        parts.append((pos, normals, checksum))
    tree = BVHTree.FromPolygons(verts, triangles, all_triangles=True)
    span = max(max(v[d] for v in verts) - min(v[d] for v in verts) for d in range(3))
    radius = span * 0.16
    epsilon = max(span * 0.00015, 1e-7)
    directions = {}
    memo = {}
    sections = []
    for pos, normals, checksum in parts:
        values = []
        for point, normal in zip(pos, normals):
            key = (point, normal)
            if key not in memo:
                n = Vector(normal).normalized()
                if not n.length_squared or radius <= epsilon:
                    memo[key] = 0
                else:
                    if normal not in directions:
                        tangent = n.orthogonal().normalized()
                        bitangent = n.cross(tangent)
                        directions[normal] = [tangent * x + bitangent * y + n * z for x, y, z in HEMISPHERE]
                    origin = Vector(point) + n * epsilon
                    blocked = 0.0
                    for direction in directions[normal]:
                        distance = tree.ray_cast(origin, direction, radius)[3]
                        if distance is not None:
                            blocked += (1 - distance / radius) ** 2
                    memo[key] = round(15 * blocked / SAMPLES)
            values.append(memo[key])
        sections.append([len(weights), len(values), checksum])
        if len(values) % 2:
            values.append(0)
        weights.extend(first | second << 4 for first, second in zip(values[::2], values[1::2]))
    return sections


def bake():
    index = {}
    weights = bytearray()
    for path in sorted(MODELS.glob('*.glb')):
        data = path.read_bytes()
        json_size = struct.unpack_from('<I', data, 12)[0]
        doc = json.loads(data[20:20 + json_size])
        binary = memoryview(data)[28 + json_size:]
        # Preserve authored vertex colours, including the baked AO in the Nanjing master.
        if any('COLOR_0' in p['attributes'] for mesh in doc['meshes'] for p in mesh['primitives']):
            continue
        index[path.stem] = [bake_mesh(doc, mesh, binary, weights) for mesh in doc['meshes']]
        print(f'Baked {path.stem}', flush=True)
    header = json.dumps(index, separators=(',', ':')).encode('utf-8')
    target = MODELS / 'vertex-occlusion.bin'
    packed = struct.pack('<4sI', b'LAO1', len(header)) + header + weights
    if not target.exists() or target.read_bytes() != packed:
        with TemporaryDirectory(dir=target.parent) as staging:
            replacement = Path(staging) / target.name
            replacement.write_bytes(packed)
            replacement.replace(target)
    print(f'{len(index)} landmarks, {len(packed):,} bytes')


if __name__ == '__main__':
    bake()
