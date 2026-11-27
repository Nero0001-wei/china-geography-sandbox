#!/usr/bin/env python3
"""Bake the close-up relief directly on a finer, center-aligned national grid."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image
import rasterio
from rasterio.features import rasterize
from rasterio.shutil import copy as copy_raster
from rasterio.transform import Affine, array_bounds, from_origin
from rasterio.warp import Resampling, transform_geom
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box, shape
from shapely.ops import unary_union

from build_relief_texture import DATA, grade_land, open_imagery, relief, warp_cover, warp_inputs
from detail_hydro import DetailHydro
from pack_atlas import INLAND_WATER, SEA_STOPS, shelf_tones


# Each intermediate tile is cut at mesh vertices into 4 × 4 smaller patches.
# The finer geographic grid has the same endpoint centers as the base atlas.
SUBDIVISIONS = 4
GUTTER = 8
BORDER_FADE_METERS = 18_000
# Covers the fade as well as four sigmas of the broadest relief filter (3.4 km).
HALO_METERS = 21_000


def sample_image(image, size, crop):
    """Sample a rectangle on the fine grid using the original pixel centers."""
    sx = (image.width - 1) / (size[0] - 1)
    sy = (image.height - 1) / (size[1] - 1)
    x, y, w, h = crop
    return image.transform((w, h), Image.Transform.AFFINE,
                           (sx, 0, sx * x + (1 - sx) / 2, 0, sy, sy * y + (1 - sy) / 2),
                           resample=Image.Resampling.BILINEAR)


def detail_entries(parents, size, grid_shape, transform, footprint):
    cols, rows = grid_shape[0] - 1, grid_shape[1] - 1
    w, h = size
    for parent in parents:
        c0, r0, c1, r1 = parent['cells']
        columns = [c0 + (c1 - c0) * i // SUBDIVISIONS for i in range(SUBDIVISIONS + 1)]
        lines = [r0 + (r1 - r0) * i // SUBDIVISIONS for i in range(SUBDIVISIONS + 1)]
        for top, bottom in zip(lines, lines[1:]):
            for left, right in zip(columns, columns[1:]):
                x0 = max(0, math.floor(left / cols * (w - 1)) - GUTTER)
                x1 = min(w, math.ceil(right / cols * (w - 1)) + GUTTER + 1)
                y0 = max(0, math.floor(top / rows * (h - 1)) - GUTTER)
                y1 = min(h, math.ceil(bottom / rows * (h - 1)) + GUTTER + 1)
                area = box(*array_bounds(y1 - y0, x1 - x0, transform * Affine.translation(x0, y0)))
                if footprint.intersects(area):
                    yield {'file': f'detail/{top}-{left}.webp', 'cells': [left, top, right, bottom],
                           'crop': [x0, y0, x1 - x0, y1 - y0]}


def build(args):
    atlas_file = args.atlas / 'atlas.json'
    atlas = json.loads(atlas_file.read_text())
    metadata = json.loads(args.terrain.read_text())
    size = tuple((atlas[k] - 1) * SUBDIVISIONS + 1 for k in ('width', 'height'))
    bounds = metadata['bounds']
    dx = (bounds['maxX'] - bounds['minX']) / (size[0] - 1)
    dy = (bounds['maxY'] - bounds['minY']) / (size[1] - 1)
    transform = from_origin(bounds['minX'] - dx / 2, bounds['maxY'] + dy / 2, dx, dy)
    crs = metadata['projection']
    polygons = json.loads(args.boundaries.read_text())['areas']
    country = unary_union([shape(transform_geom('EPSG:4326', crs, {'type': 'Polygon', 'coordinates': rings}))
                           for rings in polygons])
    footprint = country.buffer(BORDER_FADE_METERS)
    entries = list(detail_entries(atlas['tiles'], size, (metadata['width'], metadata['height']),
                                  transform, footprint))
    hydro = DetailHydro(metadata, args.cache)
    with Image.open(args.hydro) as source:
        depth = shelf_tones(source, bounds).getchannel('B')
    with Image.open(args.base) as source:
        base = source.convert('RGB')
    if base.size != (atlas['width'], atlas['height']):
        raise ValueError('Base composite and intermediate atlas sizes must agree')
    levels, colors = zip(*SEA_STOPS)
    sea = np.column_stack([np.interp(np.arange(256), levels, channel)
                           for channel in zip(*colors)]).round().astype(np.uint8)
    (args.atlas / 'detail').mkdir(exist_ok=True)

    with ExitStack() as stack:
        # JPEG source tiles are scanline compressed. Convert them once for random windows.
        imagery = open_imagery(stack, args.imagery)
        if len(args.imagery) == 1 and imagery.driver == 'GTiff' and imagery.is_tiled:
            imagery_path = args.imagery[0]
        else:
            imagery_path = Path(stack.enter_context(TemporaryDirectory(prefix='detail-color-'))) / 'color.tif'
            copy_raster(imagery, imagery_path, driver='GTiff', tiled=True, blockxsize=512, blockysize=512)

        def render(entry):
            x, y, w, h = entry['crop']
            pad = math.ceil(HALO_METERS / min(dx, dy))
            local = transform * Affine.translation(x - pad, y - pad)
            dims = h + pad * 2, w + pad * 2
            # Each worker uses its own GDAL dataset handles.
            with rasterio.open(args.dem) as dem, rasterio.open(imagery_path) as sat, rasterio.open(args.cover) as cover:
                # The 500 m satellite color is coarser than this layer, unlike the
                # elevation and land-cover sources that supply the close-up detail.
                elevation, satellite = warp_inputs(dem, sat, dims, local, crs, Resampling.bilinear)
                land_cover = warp_cover(cover, dims, local, crs)
            land, freshwater = hydro.coverage(dims, local)
            extent = box(*array_bounds(*dims, local))
            interior = rasterize([country.intersection(extent)], out_shape=dims, transform=local, dtype='uint8')
            binary_land = (land >= 128).astype(np.uint8)
            shade, slope, ridge = relief(elevation, dx, dy)
            color = grade_land(satellite, elevation, binary_land, interior, shade, slope, ridge, dx, cover=land_cover)
            crop = np.s_[pad:pad + h, pad:pad + w]
            rgb = color[crop].astype(np.float32)
            streams = freshwater[crop][..., None]
            rgb += (INLAND_WATER - rgb) * (streams.astype(np.float32) * (.86 / 255))
            ocean = sea[np.asarray(sample_image(depth, size, entry['crop']))]
            rgb = ocean + (rgb - ocean) * (land[crop][..., None].astype(np.float32) / 255)

            # Beyond the border, match the surrounding intermediate map exactly at the
            # outer limit of detail coverage. A tile boundary never defines a color edge.
            if not interior[crop].all():
                distance = distance_transform_edt(interior == 0, sampling=(dy, dx))[crop]
                t = np.clip(distance / BORDER_FADE_METERS, 0, 1).astype(np.float32)
                weight = (t * t * (3 - 2 * t))[..., None]
                parent = np.asarray(sample_image(base, size, entry['crop']))
                rgb += (parent - rgb) * weight
            tile = Image.fromarray(np.rint(rgb).clip(0, 255).astype(np.uint8))
            tile.save(args.atlas / entry['file'], quality=92, method=4)

        print(f'{len(entries)} detail tiles at {dx:.1f} m/pixel', flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for number, _ in enumerate(pool.map(render, entries), 1):
                if number % 10 == 0:
                    print(f'{number}/{len(entries)}', flush=True)
    atlas['detail'] = {'width': size[0], 'height': size[1], 'tiles': entries}
    atlas_file.write_text(json.dumps(atlas, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas', type=Path, default=DATA / 'atlas', help='Packed intermediate atlas directory')
    parser.add_argument('--terrain', type=Path, default=DATA / 'terrain.json')
    parser.add_argument('--boundaries', type=Path, default=DATA / 'china-boundaries.json')
    parser.add_argument('--base', type=Path, required=True, help='Full composite exported by pack_atlas.py')
    parser.add_argument('--hydro', type=Path, required=True, help='Intermediate RGB hydrography WebP')
    parser.add_argument('--cache', type=Path, required=True, help='Natural Earth archive cache used by build_hydrography.py')
    parser.add_argument('--dem', type=Path, required=True, help='GMTED2010 7.5 arc-second mean DEM mosaic')
    parser.add_argument('--cover', type=Path, required=True, help='ESA WorldCover color correction VRT')
    parser.add_argument('--imagery', type=Path, required=True, nargs='+')
    parser.add_argument('--workers', type=int, default=3)
    with rasterio.Env(GDAL_CACHEMAX=256 * 1024 * 1024):
        build(parser.parse_args())
