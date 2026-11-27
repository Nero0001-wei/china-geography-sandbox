"""Compose registered physical-map rasters and cut overlapping WebP tiles for the terrain mesh."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from rasterio.warp import transform
from scipy.ndimage import distance_transform_edt

PAPER = (235, 232, 223)
SEA_STOPS = [
    (0, (201, 223, 225)),
    (40, (180, 210, 226)),
    (100, (153, 189, 221)),
    (183, (116, 153, 206)),
    (255, (94, 122, 182)),
]
INLAND_WATER = (147, 190, 209)
DATA = Path(__file__).resolve().parents[1] / 'data'
LOCAL_COASTS = (
    '香港竹篙湾海岸.geojson',
    '福建鼓浪屿海岸.geojson',
    '海南天涯海角海岸.geojson',
    '山东青岛栈桥海岸.geojson',
)


def local_land(metadata):
    b = metadata['bounds']
    patches = []
    for name in LOCAL_COASTS:
        ring = json.loads((DATA / name).read_text())['geometry']['coordinates'][0]
        xs, ys = transform('EPSG:4326', metadata['projection'], *zip(*ring))
        patches.append([[round((x - b['minX']) / (b['maxX'] - b['minX']), 10),
                         round((b['maxY'] - y) / (b['maxY'] - b['minY']), 10)] for x, y in zip(xs, ys)])
    return patches


def add_local_coast(hydro, ring):
    width, height = hydro.size
    xy = [(u * (width - 1), v * (height - 1)) for u, v in ring]
    left, top = math.floor(min(x for x, y in xy)), math.floor(min(y for x, y in xy))
    w = math.ceil(max(x for x, y in xy)) - left + 1
    h = math.ceil(max(y for x, y in xy)) - top + 1
    # Subpixel coastline coverage in the same center-aligned grid used by the GL texture.
    factor = 32
    patch = Image.new('L', (w * factor, h * factor))
    ImageDraw.Draw(patch).polygon([((x - left + .5) * factor, (y - top + .5) * factor)
                                   for x, y in xy], fill=255)
    box = (left, top, left + w, top + h)
    local = hydro.crop(box)
    land = ImageChops.lighter(local.getchannel('R'), patch.resize((w, h), Image.Resampling.BOX))
    hydro.paste(Image.merge('RGB', (land, local.getchannel('G'), local.getchannel('B'))), box)


def align_centers(image, size):
    scale_x = (image.width - 1) / (size[0] - 1)
    scale_y = (image.height - 1) / (size[1] - 1)
    return image.transform(size, Image.Transform.AFFINE,
                           (scale_x, 0, (1 - scale_x) / 2, 0, scale_y, (1 - scale_y) / 2),
                           resample=Image.Resampling.BILINEAR)


def write_land_runs(channel, path):
    # Each row begins in water. Crossing any stored column toggles land/water.
    transitions = np.diff(np.asarray(channel) >= 128, axis=1, prepend=False)
    counts = transitions.sum(axis=1, dtype=np.uint32)
    offsets = np.concatenate(([0], np.cumsum(counts))).astype('<u4')
    edges = np.nonzero(transitions)[1].astype('<u2')
    path.write_bytes(offsets.tobytes() + edges.tobytes())


def shelf_tones(hydro, bounds):
    # Within broad depth bands use distance to the coast for a soft shelf wash.
    shore = np.asarray(hydro.getchannel('R')) >= 128
    dx = (bounds['maxX'] - bounds['minX']) / (hydro.width - 1)
    dy = (bounds['maxY'] - bounds['minY']) / (hydro.height - 1)
    distance = distance_transform_edt(~shore, sampling=(dy, dx)).astype(np.float32)
    depth = np.asarray(hydro.getchannel('B')).astype(np.float32)
    depth += 74 * (1 - np.exp(-distance / 68_000)) * (1 - depth / 255) ** 1.8
    return Image.merge('RGB', (hydro.getchannel('R'), hydro.getchannel('G'),
                               Image.fromarray(np.rint(depth).astype(np.uint8))))


def compose(relief, hydro, additional_land, bounds):
    width, height = relief.size
    hydro = align_centers(hydro, relief.size)
    for ring in additional_land:
        add_local_coast(hydro, ring)
    combined = Image.new('RGB', relief.size)
    levels, colors = zip(*SEA_STOPS)
    water = np.column_stack([np.interp(np.arange(256), levels, channel)
                             for channel in zip(*colors)]).astype(np.float32)
    paper = np.array(PAPER, dtype=np.float32)
    x_edge = np.minimum(np.arange(width), np.arange(width)[::-1])
    pixel_size = (bounds['maxX'] - bounds['minX']) / (width - 1)
    for row in range(0, height, 160):
        end = min(height, row + 160)
        box = (0, row, width, end)
        base = np.asarray(relief.crop(box), dtype=np.float32)
        r, g, b = np.asarray(hydro.crop(box)).transpose(2, 0, 1)
        river = (g.astype(np.float32) / 255 * 0.86)[:, :, None]
        base += (INLAND_WATER - base) * river
        ocean = water[b]
        land = r[:, :, None].astype(np.float32) / 255
        surface = ocean + (base - ocean) * land
        y_edge = np.minimum(np.arange(row, end), height - 1 - np.arange(row, end))
        distance = np.minimum(x_edge[None, :], y_edge[:, None])
        t = np.clip(distance * pixel_size / 255_000, 0, 1).astype(np.float32)
        fade = (t * t * (3 - 2 * t))[:, :, None]
        rgb = paper + (surface - paper) * fade
        combined.paste(Image.fromarray(np.rint(rgb).clip(0, 255).astype(np.uint8)), (0, row))
    return combined


def pack(relief_file, hydro_file, target, metadata_file, export):
    target.mkdir(parents=True, exist_ok=True)
    metadata = json.loads(metadata_file.read_text())
    relief = Image.open(relief_file).convert('RGB')
    hydro = Image.open(hydro_file).convert('RGB')
    write_land_runs(hydro.getchannel('R'), target / 'coast.runs')
    hydro = shelf_tones(hydro, metadata['bounds'])
    additional_land = local_land(metadata)
    combined = compose(relief, hydro, additional_land, metadata['bounds']).filter(
        ImageFilter.UnsharpMask(radius=1.3, percent=32, threshold=3))
    if export:
        export.parent.mkdir(parents=True, exist_ok=True)
        combined.save(export, quality=95, method=5)
    width, height = combined.size
    overview_width = round(width / 3)
    preview = combined.resize((overview_width, round(overview_width * height / width)), Image.Resampling.LANCZOS)
    preview = preview.filter(ImageFilter.UnsharpMask(radius=1.1, percent=55, threshold=3))
    preview.save(target / 'overview.webp', quality=91, method=5)
    atlas = {'width': width, 'height': height, 'coastSize': hydro.size, 'paper': PAPER,
             'additionalLand': additional_land, 'tiles': []}
    # Mesh groups end on existing vertices so the elevation triangles and picking stay identical.
    cols, rows = metadata['width'] - 1, metadata['height'] - 1
    tile_cols, tile_rows = math.ceil(width / 1600), math.ceil(height / 1600)
    for ty in range(tile_rows):
        for tx in range(tile_cols):
            c0, c1 = tx * cols // tile_cols, (tx + 1) * cols // tile_cols
            r0, r1 = ty * rows // tile_rows, (ty + 1) * rows // tile_rows
            left = max(0, math.floor(c0 / cols * (width - 1)) - 8)
            top = max(0, math.floor(r0 / rows * (height - 1)) - 8)
            right = min(width, math.ceil(c1 / cols * (width - 1)) + 9)
            bottom = min(height, math.ceil(r1 / rows * (height - 1)) + 9)
            tile = combined.crop((left, top, right, bottom))
            filename = f'{ty}-{tx}.webp'
            tile.save(target / filename, quality=91, method=5)
            atlas['tiles'].append({'file': filename, 'cells': [c0, r0, c1, r1],
                                   'crop': [left, top, tile.width, tile.height]})
    (target / 'atlas.json').write_text(json.dumps(atlas, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--relief', type=Path, required=True)
    parser.add_argument('--hydro', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('app/public/data/atlas'))
    parser.add_argument('--terrain', type=Path, default=Path('app/public/data/terrain.json'))
    parser.add_argument('--export', type=Path, help='Optional full-resolution composite WebP')
    args = parser.parse_args()
    pack(args.relief, args.hydro, args.output, args.terrain, args.export)
