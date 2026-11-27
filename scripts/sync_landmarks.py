#!/usr/bin/env python3
"""Publish the model inventory and web catalogue from the editable landmark records."""
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'data/landmarks'
WEB_MODELS = ROOT / 'app/public/models'
CATALOG = ROOT / 'app/shared/landmark-catalog.json'


def load(path):
    return json.loads(path.read_text())


def write(path, obj):
    text = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text() != text:
        path.write_text(text)


def verify_export(glb, model):
    data = glb.read_bytes()
    magic, version, total, json_size, kind = struct.unpack_from('<4sIII4s', data)
    if (magic, version, total, kind) != (b'glTF', 2, len(data), b'JSON'):
        raise ValueError(f'Invalid GLB: {glb}')
    scene = json.loads(data[20:20 + json_size])
    triangles = 0
    for mesh in scene['meshes']:
        for primitive in mesh['primitives']:
            if primitive.get('mode', 4) != 4:
                raise ValueError(f'Expected a triangulated mesh in {glb.name}')
            accessor = primitive.get('indices', primitive['attributes']['POSITION'])
            triangles += scene['accessors'][accessor]['count'] // 3
    if any('uri' in asset for asset in scene['buffers'] + scene.get('images', [])):
        raise ValueError(f'Expected embedded resources in {glb.name}')
    if (triangles, len(data), hashlib.sha256(data).hexdigest()) != (
            model['triangles'], model['bytes'], model['sha256']):
        raise ValueError(f'Stale model statistics: {glb.name}')


def sync():
    arrivals = load(ASSETS / 'arrival-points.json')
    stats = []
    sites = {}
    # These records retain their existing route and rotation definitions in landmarks.js.
    manual = {'zhongshan', 'huangshan', 'gugong'}
    allowed_types = {'nature', 'heritage', 'town-garden', 'urban', 'museum', 'theme-park'}
    required_keys = ('id', 'name', 'city', 'province', 'description', 'anchor',
                     'anchorSource', 'frontBearing', 'groundSpanMeters', 'type', 'tier')
    for record in sorted(ASSETS.glob('*/stats.json')):
        model = load(record)
        glb = WEB_MODELS / model['file']
        if model['id'] != record.parent.name or glb.name != model['id'] + '.glb':
            raise ValueError(f'Asset ID does not match its file: {glb.name}')
        verify_export(glb, model)
        stats.append(model)
        key = model['id']
        if key in manual:
            continue
        site = load(record.with_name('site.json'))
        if (site['id'] != key or site['anchorCrs'] != 'WGS84'
                or len(site['anchor']) != 2 or not all(map(math.isfinite, site['anchor']))
                or not math.isfinite(site['frontBearing']) or site['groundSpanMeters'] <= 0
                or site.get('type') not in allowed_types or site.get('tier') not in {'national', 'regional'}):
            raise ValueError(f'Incomplete landmark: {key}')
        # Published arrival points are optional for landmarks that support map exploration only.
        stops = arrivals.get(key, {})
        for stop in stops.values():
            if not stop['id'] or len(stop['location']) != 2 or not all(map(math.isfinite, stop['location'])):
                raise ValueError(f'Incomplete Amap arrival point: {key}')
        sites[key] = {**{k: site[k] for k in required_keys}, **stops}
    if arrivals.keys() - sites.keys():
        raise ValueError(f'Arrival points refer to unknown landmarks: {arrivals.keys() - sites.keys()}')
    ordered = list(dict.fromkeys([*arrivals, *sites]))
    write(WEB_MODELS / 'manifest.json', {'models': stats})
    write(CATALOG, [sites[key] for key in ordered])


if __name__ == '__main__':
    sync()
