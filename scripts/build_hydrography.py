#!/usr/bin/env python3
"""Rasterize physical coastlines, freshwater and generalized ocean bathymetry."""

import argparse
from dataclasses import dataclass
from hashlib import file_digest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageFilter
from rasterio.crs import CRS
from rasterio.features import rasterize
from rasterio.transform import Affine, from_origin
from rasterio.warp import transform_bounds, transform_geom
import shapefile
from shapely.geometry import box, mapping, shape


GEOGRAPHIC = CRS.from_epsg(4326)
SOURCE_BASE = 'https://naturalearth.s3.amazonaws.com/10m_physical/'
SOURCE_NAMES = {
    'land': 'ne_10m_land.zip',
    'lakes': 'ne_10m_lakes.zip',
    'rivers': 'ne_10m_rivers_lake_centerlines.zip',
    'depth': 'ne_10m_bathymetry_all.zip',
}
DEPTH_TONES = {200: 55, 1_000: 110, 2_000: 160, 3_000: 198, 4_000: 229, 5_000: 255}
SUPERSAMPLE = 3


@dataclass(frozen=True)
class Grid:
    width: int
    height: int
    crs: CRS
    transform: Affine

    @property
    def shape(self):
        return self.height, self.width

    def supersampled(self):
        return Grid(self.width * SUPERSAMPLE, self.height * SUPERSAMPLE,
                    self.crs, self.transform * Affine.scale(1 / SUPERSAMPLE))


def make_grid(metadata, width):
    bounds = metadata['bounds']
    min_x, min_y = bounds['minX'], bounds['minY']
    max_x, max_y = bounds['maxX'], bounds['maxY']
    step_x = (max_x - min_x) / (width - 1)
    height = round((max_y - min_y) / step_x) + 1
    step_y = (max_y - min_y) / (height - 1)
    transform = from_origin(min_x - step_x / 2, max_y + step_y / 2, step_x, step_y)
    grid = Grid(width, height, CRS.from_string(metadata['projection']), transform)
    west, south, east, north = transform_bounds(grid.crs, GEOGRAPHIC, min_x, min_y, max_x, max_y, densify_pts=101)
    clip = box(west - 0.5, south - 0.5, east + 0.5, north + 0.5)
    return grid, clip


def projected_features(path, clip, target_crs, river=False, river_scale=1.0):
    with shapefile.Reader(str(path)) as reader:
        records = (reader.iterShapeRecords(fields=['scalerank', 'featurecla'])
                   if river else reader.iterShapes())
        for record in records:
            feature = record.shape if river else record
            if not clip.intersects(box(*feature.bbox)):
                continue
            if river and 'centerline' in record.record['featurecla'].lower():
                continue
            clipped = shape(feature.__geo_interface__).intersection(clip)
            if clipped.is_empty:
                continue
            geometry = transform_geom(GEOGRAPHIC, target_crs, mapping(clipped))
            if river:
                # River centerlines acquire a cartographic stroke, with larger rivers wider.
                rank = record.record['scalerank']
                radius = (650 + (9 - min(rank, 9)) * 180) * river_scale
                geometry = mapping(shape(geometry).buffer(radius, quad_segs=3))
            yield geometry


def coverage(geometries, grid):
    detailed_grid = grid.supersampled()
    detailed = rasterize(geometries, out_shape=detailed_grid.shape,
                         transform=detailed_grid.transform, default_value=255, dtype='uint8')
    image = Image.fromarray(detailed)
    return image.resize((grid.width, grid.height), Image.Resampling.BOX)


def sea_depth(path, grid, clip):
    geometries = []
    with ZipFile(path) as collection, TemporaryDirectory(prefix='atlas-depth-') as directory:
        layers = sorted((int(Path(item).stem.rsplit('_', 1)[-1]), item)
                        for item in collection.namelist() if item.endswith('.shp'))
        for depth, layer in layers:
            if depth not in DEPTH_TONES:
                continue
            shp = Path(layer)
            for suffix in ('.shp', '.shx', '.dbf'):
                name = str(shp.with_suffix(suffix))
                destination = Path(directory) / shp.with_suffix(suffix).name
                destination.write_bytes(collection.read(name))
            geometries.extend((part, DEPTH_TONES[depth]) for part in
                              projected_features(Path(directory) / shp.name, clip, grid.crs))

    depth = rasterize(geometries, out_shape=grid.shape, transform=grid.transform, dtype='uint8')
    return Image.fromarray(depth).filter(ImageFilter.GaussianBlur(radius=9_000 / grid.transform.a))


def source_paths(cache, layers=SOURCE_NAMES):
    cache.mkdir(parents=True, exist_ok=True)
    sources = {}
    for layer in layers:
        name = SOURCE_NAMES[layer]
        archive = cache / name
        if not archive.exists():
            pending = archive.with_suffix('.tmp')
            urlretrieve(SOURCE_BASE + name, pending)
            pending.replace(archive)
        sources[layer] = archive
    return sources


def source_metadata(paths):
    layers = {}
    for layer, path in paths.items():
        with path.open('rb') as source:
            digest = file_digest(source, 'sha256').hexdigest()
        layers[layer] = {'download': SOURCE_BASE + path.name, 'sha256': digest}
    return layers


def generate(terrain, cache, output, width):
    metadata = json.loads(terrain.read_text(encoding='utf-8'))
    grid, clip = make_grid(metadata, width)
    paths = source_paths(cache)
    land = coverage(projected_features(paths['land'], clip, grid.crs), grid)
    lakes = list(projected_features(paths['lakes'], clip, grid.crs))
    streams = list(projected_features(paths['rivers'], clip, grid.crs, river=True))
    freshwater = coverage(lakes + streams, grid)
    depth = sea_depth(paths['depth'], grid, clip)
    depth_array = np.array(depth)
    depth_array[np.asarray(land) >= 128] = 0
    depth = Image.fromarray(depth_array)

    output.parent.mkdir(parents=True, exist_ok=True)
    Image.merge('RGB', (land, freshwater, depth)).save(output, format='WEBP', lossless=True, method=6)
    output.with_suffix('.json').write_text(json.dumps({
        'width': grid.width,
        'height': grid.height,
        'bounds': metadata['bounds'],
        'projection': metadata['projection'],
        'boundsReference': 'sample centers',
        'rowOrder': 'north-to-south',
        'encoding': 'RGB WebP lossless',
        'channels': {'r': 'physical land coverage', 'g': 'freshwater coverage', 'b': 'ocean depth tone'},
        'depthTones': DEPTH_TONES,
        'sources': source_metadata(paths),
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{grid.width} × {grid.height}, {len(lakes)} lakes, {len(streams)} rivers: {output}')


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terrain', type=Path, default=root / 'app/public/data/terrain.json')
    parser.add_argument('--cache', type=Path, required=True, help='Directory for original Natural Earth archives')
    parser.add_argument('--output', type=Path, required=True, help='Path to the intermediate lossless RGB WebP')
    parser.add_argument('--width', type=int, default=5806)
    arguments = parser.parse_args()
    if arguments.width < 2:
        parser.error('--width must be at least 2')
    generate(arguments.terrain, arguments.cache, arguments.output, arguments.width)


if __name__ == '__main__':
    main()
