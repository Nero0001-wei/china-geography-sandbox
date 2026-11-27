#!/usr/bin/env python3
"""Prepare the relief mesh, physical land mask, and a source comparison at 32°N."""

import argparse
from contextlib import ExitStack
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.features import rasterize
from rasterio.merge import merge
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject, transform, transform_bounds, transform_geom
from rasterio.windows import Window, bounds as window_bounds, from_bounds as window_from_bounds
import shapefile
from shapely.geometry import box, mapping, shape


# Extend the national grid by whole cells so its center, spacing and vertex
# alignment stay fixed for landmark placement, route profiles and the camera.
STEP_X = 6_300_000 / 383
STEP_Y = 4_900_000 / 287
PADDING_X, PADDING_Y = 80, 64
WIDTH = 384 + 2 * PADDING_X
HEIGHT = 288 + 2 * PADDING_Y
BOUNDS = (-3_350_000 - PADDING_X * STEP_X, 1_600_000 - PADDING_Y * STEP_Y,
          2_950_000 + PADDING_X * STEP_X, 6_500_000 + PADDING_Y * STEP_Y)
PROJECTION = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m +no_defs'
GEOGRAPHIC = CRS.from_epsg(4326)
PROJECTED = CRS.from_string(PROJECTION)
NO_DATA = -32768
PROFILE_LATITUDE = 32
PROFILE_REGIONS = (
    ('青藏高原', 85, 99),
    ('四川盆地北缘', 105, 108),
    ('长江中下游平原', 117, 121),
)
SOURCE_URL = 'https://topotools.cr.usgs.gov/gmted_viewer/gmted2010_global_grids.php'
SOURCE_DOWNLOAD = 'https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/topo/downloads/GMTED/Grid_ZipFiles/mn30_grd.zip'
LAND_URL = 'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/'

MIN_X, MIN_Y, MAX_X, MAX_Y = BOUNDS
# The advertised bounds are vertex coordinates, so put them on pixel centers.
GRID_TRANSFORM = from_origin(MIN_X - STEP_X / 2, MAX_Y + STEP_Y / 2, STEP_X, STEP_Y)
WEST, SOUTH, EAST, NORTH = transform_bounds(PROJECTED, GEOGRAPHIC, *BOUNDS, densify_pts=101)
SOURCE_BOUNDS = (WEST - 1, SOUTH - 1, EAST + 1, NORTH + 1)


def open_dem(stack, paths):
    datasets = [stack.enter_context(rasterio.open(path)) for path in paths]
    for dataset in datasets:
        if dataset.crs != GEOGRAPHIC or not np.allclose(dataset.res, 1 / 120, atol=1e-6, rtol=0):
            raise ValueError(f'Expected a GMTED2010 30″ WGS84 grid: {dataset.name}')
    if len(datasets) == 1:
        return datasets[0]

    reference = datasets[0].transform
    extent = window_from_bounds(*SOURCE_BOUNDS, transform=reference)
    col, row = math.floor(extent.col_off), math.floor(extent.row_off)
    window = Window(col, row, math.ceil(extent.col_off + extent.width) - col,
                    math.ceil(extent.row_off + extent.height) - row)
    aligned_bounds = window_bounds(window, reference)
    mosaic, affine = merge(datasets, bounds=aligned_bounds, nodata=NO_DATA, dtype='int16')
    memory = stack.enter_context(rasterio.MemoryFile())
    with memory.open(driver='GTiff', width=mosaic.shape[2], height=mosaic.shape[1], count=1,
                     crs=GEOGRAPHIC, transform=affine, dtype='int16', nodata=NO_DATA) as dataset:
        dataset.write(mosaic)
    return stack.enter_context(memory.open())


def reproject_elevation(source):
    destination = np.full((HEIGHT, WIDTH), NO_DATA, dtype=np.int16)
    reproject(source=rasterio.band(source, 1), destination=destination,
              dst_crs=PROJECTED, dst_transform=GRID_TRANSFORM, dst_nodata=NO_DATA,
              resampling=Resampling.average)
    return destination


def make_land_mask(shapefile_path):
    clip = box(*SOURCE_BOUNDS)
    shapes = []
    with shapefile.Reader(str(shapefile_path)) as reader:
        for feature in reader.iterShapes():
            if not clip.intersects(box(*feature.bbox)):
                continue
            clipped = shape(feature.__geo_interface__).intersection(clip)
            if not clipped.is_empty:
                shapes.append(transform_geom(GEOGRAPHIC, PROJECTED, mapping(clipped)))
    return rasterize(shapes, out_shape=(HEIGHT, WIDTH), transform=GRID_TRANSFORM, dtype='uint8')


def sample_mesh(elevation, longitude, latitude):
    eastings, northings = transform(GEOGRAPHIC, PROJECTED, longitude, latitude)
    col = (np.asarray(eastings) - MIN_X) / STEP_X
    row = (MAX_Y - np.asarray(northings)) / STEP_Y
    left = np.floor(col).astype(int)
    top = np.floor(row).astype(int)
    dx = col - left
    dy = row - top
    a = elevation[top, left]
    b = elevation[top, left + 1]
    c = elevation[top + 1, left]
    d = elevation[top + 1, left + 1]
    # Use the same northeast–southwest diagonal as the rendered mesh.
    heights = np.where(dx + dy <= 1,
                       a + (b - a) * dx + (c - a) * dy,
                       d + (c - d) * (1 - dx) + (b - d) * (1 - dy))
    return np.where((a == NO_DATA) | (b == NO_DATA) | (c == NO_DATA) | (d == NO_DATA), np.nan, heights)


def measure_profile(source, elevation):
    longitudes = np.arange(790, 1221, dtype=float) / 10
    latitudes = np.full(longitudes.shape, PROFILE_LATITUDE)
    source_points = source.sample(zip(longitudes, latitudes), masked=True)
    source_heights = np.array([np.nan if np.ma.is_masked(value[0]) else float(value[0]) for value in source_points])
    mesh_heights = sample_mesh(elevation, longitudes, latitudes)
    if not np.all(np.isfinite(source_heights) & np.isfinite(mesh_heights)):
        raise ValueError('Elevation source and reprojected mesh must both cover the latitude profile')

    regions = []
    for name, west, east in PROFILE_REGIONS:
        selection = (longitudes >= west) & (longitudes <= east)
        regions.append({'name': name, 'west': west, 'east': east,
                        'sourceMean': round(float(source_heights[selection].mean())),
                        'meshMean': round(float(mesh_heights[selection].mean()))})
    for field in ('sourceMean', 'meshMean'):
        plateau, basin, plain = [region[field] for region in regions]
        if not (3500 < plateau < 6500 and 200 < basin < 1800 and -10 < plain < 200 and plateau > basin > plain):
            raise ValueError(f'Unexpected west-to-east profile: {regions}')

    return {
        'latitude': PROFILE_LATITUDE,
        'verticalUnit': 'm',
        'meanAbsoluteError': round(float(np.abs(source_heights - mesh_heights).mean())),
        'regions': regions,
        'samples': [{'longitude': float(lon), 'source': round(float(actual)), 'mesh': round(float(mesh))}
                    for lon, actual, mesh in zip(longitudes, source_heights, mesh_heights, strict=True)],
    }


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dem', required=True, nargs='+', type=Path, help='USGS ArcGrid directory or GMTED2010 GeoTIFF tiles')
    parser.add_argument('--land', required=True, type=Path, help='Natural Earth ne_10m_land.shp (unpacked)')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'app' / 'public' / 'data')
    arguments = parser.parse_args()

    with ExitStack() as stack:
        source = open_dem(stack, arguments.dem)
        elevation = reproject_elevation(source)
        profile = measure_profile(source, elevation)

    land = make_land_mask(arguments.land)
    valid_land = (land == 1) & (elevation != NO_DATA)
    if valid_land.sum() < 40_000 or np.count_nonzero(land == 0) < 5_000:
        raise ValueError('Insufficient elevation or physical land coverage')
    output = arguments.output
    output.mkdir(parents=True, exist_ok=True)
    elevation.astype('<i2', copy=False).tofile(output / 'elevation.i16')
    land.tofile(output / 'land.u8')
    write_json(output / 'terrain.json', {
        'width': WIDTH,
        'height': HEIGHT,
        'bounds': dict(zip(('minX', 'minY', 'maxX', 'maxY'), BOUNDS, strict=True)),
        'projection': PROJECTION,
        'horizontalUnit': 'm',
        'verticalUnit': 'm',
        'scale': 1,
        'noData': NO_DATA,
        'elevationEncoding': 'int16-le',
        'landEncoding': 'uint8',
        'rowOrder': 'north-to-south',
        'boundsReference': 'sample centers',
        'elevationRange': [int(elevation[valid_land].min()), int(elevation[valid_land].max())],
        'source': {'name': 'GMTED2010', 'credit': 'USGS / NGA', 'resolutionArcSeconds': 30,
                   'statistic': 'mean', 'verticalDatum': 'EGM96', 'url': SOURCE_URL, 'download': SOURCE_DOWNLOAD},
        'landSource': {'name': 'Natural Earth 1:10m Land', 'version': '5.1.1', 'url': LAND_URL},
        'resampling': 'average',
    })
    write_json(output / 'profile-32n.json', profile)
    print(f'{WIDTH} × {HEIGHT} elevation and land samples written to {output}')
    for region in profile['regions']:
        print(f"{region['name']}：源 {region['sourceMean']} m，网格 {region['meshMean']} m")
    print(f"剖面逐点平均绝对差 {profile['meanAbsoluteError']} m")


if __name__ == '__main__':
    main()
