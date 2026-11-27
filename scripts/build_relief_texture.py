#!/usr/bin/env python3
"""Shade real elevations and satellite land color in the terrain's Albers grid."""

import argparse
from contextlib import ExitStack
import json
import math
from pathlib import Path
import warnings
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image
import rasterio
from rasterio.crs import CRS
from rasterio.errors import NotGeoreferencedWarning
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject, transform_bounds, transform_geom
from scipy.ndimage import distance_transform_edt, gaussian_filter, minimum_filter
import shapefile
from shapely.geometry import box, mapping, shape

from build_terrain import GEOGRAPHIC, open_dem


DATA = Path(__file__).resolve().parents[1] / 'app' / 'public' / 'data'


def target_grid(metadata, width):
    coordinates = metadata['bounds']
    min_x, min_y, max_x, max_y = (coordinates[key] for key in ('minX', 'minY', 'maxX', 'maxY'))
    height = 1 + round((width - 1) * (max_y - min_y) / (max_x - min_x))
    step_x = (max_x - min_x) / (width - 1)
    step_y = (max_y - min_y) / (height - 1)
    transform = from_origin(min_x - step_x / 2, max_y + step_y / 2, step_x, step_y)
    return (height, width), transform, CRS.from_string(metadata['projection'])


def open_imagery(stack, paths):
    stack.enter_context(warnings.catch_warnings())
    warnings.filterwarnings('ignore', category=NotGeoreferencedWarning)
    full_width, full_height, degrees_per_pixel = 43200, 21600, 1 / 240
    if len(paths) == 1:
        image = stack.enter_context(rasterio.open(paths[0]))
        if image.crs:
            return image
        if abs(image.width / image.height - 2) > 0.001 or image.count < 3:
            raise ValueError('Use a georeferenced GeoTIFF, the global 2:1 JPEG, or NASA C1 and D1 tiles')
        full_width, full_height = image.width, image.height
        degrees_per_pixel = 360 / full_width
        west = -180
        tiles = [(paths[0], 0, image.width, image.height)]
    elif len(paths) == 2:
        west = 0
        tiles = [(path, offset, 21600, 21600) for path, offset in zip(paths, (0, 21600), strict=True)]
        for path, _, width, height in tiles:
            with rasterio.open(path) as image:
                if (image.width, image.height) != (width, height) or image.count < 3:
                    raise ValueError('NASA Blue Marble tiles should be 21,600 square RGB images ordered C1 then D1')
    else:
        raise ValueError('Use one global image or the two Northern Hemisphere tiles C1 then D1')

    vrt = [f'<VRTDataset rasterXSize="{full_width}" rasterYSize="{full_height}">',
           '<SRS dataAxisToSRSAxisMapping="2,1">EPSG:4326</SRS>',
           f'<GeoTransform>{west},{degrees_per_pixel},0,90,0,{-degrees_per_pixel}</GeoTransform>']
    for band in range(1, 4):
        vrt.append(f'<VRTRasterBand dataType="Byte" band="{band}">')
        for path, offset, width, height in tiles:
            vrt.append(f'<SimpleSource><SourceFilename relativeToVRT="0">{escape(str(path.resolve()))}</SourceFilename>'
                       f'<SourceBand>{band}</SourceBand><SrcRect xOff="0" yOff="0" xSize="{width}" ySize="{height}"/>'
                       f'<DstRect xOff="{offset}" yOff="0" xSize="{width}" ySize="{height}"/></SimpleSource>')
        vrt.append('</VRTRasterBand>')
    vrt.append('</VRTDataset>')
    memory = stack.enter_context(rasterio.MemoryFile(''.join(vrt).encode(), ext='.vrt'))
    return stack.enter_context(memory.open())


def raster_layers(dimensions, affine, crs, land_path, border_path):
    west, south, east, north = transform_bounds(crs, GEOGRAPHIC, *rasterio.transform.array_bounds(*dimensions, affine), densify_pts=101)
    clip = box(west - 1, south - 1, east + 1, north + 1)
    shapes = []
    with shapefile.Reader(str(land_path)) as reader:
        for feature in reader.iterShapes():
            if clip.intersects(box(*feature.bbox)):
                polygon = shape(feature.__geo_interface__).intersection(clip)
                if not polygon.is_empty:
                    shapes.append(transform_geom(GEOGRAPHIC, crs, mapping(polygon)))
    land = rasterize(shapes, out_shape=dimensions, transform=affine, dtype='uint8')

    areas = json.loads(border_path.read_text(encoding='utf-8'))['areas']
    areas = [transform_geom(GEOGRAPHIC, crs, {'type': 'Polygon', 'coordinates': rings}) for rings in areas]
    country = rasterize(areas, out_shape=dimensions, transform=affine, dtype='uint8')
    return land, country


def warp_inputs(elevation_source, image_source, dimensions, affine, crs, image_resampling=Resampling.average):
    elevations = np.empty(dimensions, dtype=np.float32)
    satellite = np.empty((3, *dimensions), dtype=np.uint8)
    target = {'dst_crs': crs, 'dst_transform': affine, 'num_threads': 4, 'warp_mem_limit': 256}
    reproject(rasterio.band(elevation_source, 1), elevations, dst_nodata=-32768, resampling=Resampling.bilinear, **target)
    elevations[elevations == -32768] = 0
    reproject(rasterio.band(image_source, [1, 2, 3]), satellite, resampling=image_resampling, **target)
    return elevations, satellite


def warp_cover(source, dimensions, affine, crs):
    # prepare_worldcover.py maps classes to pigments before the area average.
    # Mixed pixels thus follow fractions of cropland, forest, water, etc.
    if source is None:
        return None
    cover = np.zeros((4, *dimensions), dtype=np.uint8)
    reproject(rasterio.band(source, [1, 2, 3, 4]), cover, dst_crs=crs, dst_transform=affine,
              src_nodata=0, dst_nodata=0, resampling=Resampling.average, num_threads=2, warp_mem_limit=128)
    return cover


def smoothstep(value, start, stop):
    t = np.clip((value - start) / (stop - start), 0, 1)
    return t * t * (3 - 2 * t)


def hill_light(south, east, exaggeration, altitude):
    # Image rows run south. Both scales use the same northwest light direction.
    east = east * exaggeration
    south = south * exaggeration
    norm = np.sqrt(1 + east ** 2 + south ** 2)
    azimuth, altitude = math.radians(318), math.radians(altitude)
    light_east = math.sin(azimuth) * math.cos(altitude)
    light_north = math.cos(azimuth) * math.cos(altitude)
    flat_light = math.sin(altitude)
    incidence = (-east * light_east + south * light_north + flat_light) / norm
    # Gradually roll into ambient light on faces turned away from the sun.
    difference = incidence - flat_light
    return 1 + np.where(difference >= 0, .31 * difference / (1 - flat_light),
                        .72 * np.tanh(1.35 * difference / flat_light))


def relief(elevation, dx, dy):
    fine = gaussian_filter(elevation, (max(.30, 270 / dy), max(.30, 270 / dx)))
    broad = gaussian_filter(elevation, (max(.65, 3400 / dy), max(.65, 3400 / dx)))
    south, east = np.gradient(fine, dy, dx)
    slope = np.hypot(south, east)
    shade = .70 * hill_light(south, east, 5.8, 37)
    south, east = np.gradient(broad, dy, dx)
    shade += .30 * hill_light(south, east, 5.3, 40)
    ridge = fine - broad
    # Highlight crests and deepen enclosed valleys in proportion to local relief.
    shade *= 1 + .075 * np.tanh(ridge / 220)
    return shade, slope, ridge


def grade_land(satellite, elevation, land, country, shade, slope, ridge, pixel_size, cover=None):
    height, width = land.shape
    # Satellite ocean has a blue signal. Use a nearby terrestrial color when the
    # satellite and vector coastlines differ by a few pixels.
    nearest = None
    if not land.all():
        coast_radius = max(1, math.ceil(2200 / pixel_size))
        inland = minimum_filter(land, size=2 * coast_radius + 1)
        natural_color = (land == 1) & ((inland == 1) | ((satellite[2].astype(np.int16) - satellite[0]) < 12))
        nearest = distance_transform_edt(~natural_color, return_distances=False, return_indices=True)
    inside = gaussian_filter(country.astype(np.float32), max(.45, 450 / pixel_size))
    result = np.empty((height, width, 3), dtype=np.uint8)

    open_field = np.array([198, 190, 123], dtype=np.float32)
    leafy_field = np.array([86, 126, 55], dtype=np.float32)
    sand_highlight = np.array([247, 215, 151], dtype=np.float32)
    dry_shadow = np.array([130, 120, 89], dtype=np.float32)
    dry_mid = np.array([206, 185, 135], dtype=np.float32)
    forest_shadow = np.array([63, 93, 42], dtype=np.float32)
    forest_highlight = np.array([153, 169, 89], dtype=np.float32)
    freshwater = np.array([132, 177, 192], dtype=np.float32)
    neutral = np.array([224, 220, 211], dtype=np.float32)

    for begin in range(0, height, 256):
        end = min(begin + 256, height)
        rows = slice(begin, end)
        pixels = satellite[:, rows] if nearest is None else satellite[:, nearest[0, rows], nearest[1, rows]]
        red, green, blue = pixels.astype(np.float32) / 255
        brightness = .3 * red + .58 * green + .12 * blue
        greenness = (green - red) / np.maximum(green + red, .08)
        vegetation = smoothstep(greenness, -.085, .145)
        highland = smoothstep(elevation[rows], 2550, 4350)
        sand = smoothstep(brightness, .28, .63) * (.60 + .40 * (1 - vegetation)) * (1 - .77 * highland)
        lowland = (1 - smoothstep(elevation[rows], 150, 1150)) * (1 - smoothstep(slope[rows], .008, .044))
        dry_brightness = smoothstep(brightness, .14, .57)
        forest_brightness = smoothstep(brightness, .09, .38)
        # The August imagery preserves regional variation even in very flat terrain.
        # Keep the full red/green response of croplands along with their reflectance.
        field_density = (.67 * smoothstep(greenness, -.045, .225)
                         + .33 * (1 - smoothstep(brightness, .13, .36)))
        field_weight = lowland * smoothstep(greenness, -.085, .045)
        snow_from_color = smoothstep(brightness, .55, .79) * smoothstep(blue / np.maximum(red, .1), .75, .95)
        snow_from_topography = (smoothstep(elevation[rows], 4550, 6220) *
                                (.10 + .90 * smoothstep(ridge[rows], 40, 290)))
        snow = np.clip(np.maximum(snow_from_color, snow_from_topography), 0, .96)
        saturation = inside[rows]
        light = shade[rows]
        if cover is not None:
            valid_cover = cover[0, rows] != 0
            water = .0075 * np.maximum(cover[3, rows].astype(np.float32) - 1, 0)
        for channel in range(3):
            dry = dry_shadow[channel] + (dry_mid[channel] - dry_shadow[channel]) * dry_brightness
            dry += (sand_highlight[channel] - dry) * sand
            dry *= 1 - .075 * highland
            green_tone = forest_shadow[channel] + (forest_highlight[channel] - forest_shadow[channel]) * forest_brightness
            color = dry + (green_tone - dry) * vegetation
            field = open_field[channel] + (leafy_field[channel] - open_field[channel]) * field_density
            color += (field - color) * field_weight
            if cover is not None:
                color += (cover[channel, rows].astype(np.float32) - 64) * valid_cover
                color += (freshwater[channel] - color) * water
            color += (249 - color) * snow
            context = neutral[channel] + 17 * snow
            color = ((context + (color - context) * saturation) * light)
            result[rows, :, channel] = np.clip(color + .5, 0, 255).astype(np.uint8)

    # Extend actual edge color below the separate coastline alpha, so texture
    # filtering cannot draw a colored fringe where the water layer starts.
    if nearest is not None:
        del nearest
        nearest = distance_transform_edt(land == 0, return_distances=False, return_indices=True)
        for begin in range(0, height, 256):
            rows = slice(begin, min(begin + 256, height))
            result[rows] = result[nearest[0, rows], nearest[1, rows]]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dem', type=Path, required=True, nargs='+', help='GMTED2010 30″ mean ArcGrid or GeoTIFF tiles')
    parser.add_argument('--imagery', type=Path, required=True, nargs='+', help='NASA Blue Marble global image or August tiles C1 then D1')
    parser.add_argument('--land', type=Path, required=True, help='Unpacked Natural Earth 1:10m land shapefile')
    parser.add_argument('--cover', type=Path, help='Pigment VRT from prepare_worldcover.py')
    parser.add_argument('--terrain', type=Path, default=DATA / 'terrain.json')
    parser.add_argument('--boundaries', type=Path, default=DATA / 'china-boundaries.json')
    parser.add_argument('--output', type=Path, required=True, help='Destination WebP texture')
    parser.add_argument('--width', type=int, default=8710)
    arguments = parser.parse_args()
    if arguments.width < 16:
        parser.error('--width must be at least 16 pixels')

    metadata = json.loads(arguments.terrain.read_text(encoding='utf-8'))
    dimensions, affine, crs = target_grid(metadata, arguments.width)
    print(f'Projecting GMTED2010 and Blue Marble to {dimensions[1]} × {dimensions[0]}', flush=True)
    with ExitStack() as stack:
        stack.enter_context(rasterio.Env(GDAL_CACHEMAX=256 * 1024 * 1024))
        dem = open_dem(stack, arguments.dem)
        imagery = open_imagery(stack, arguments.imagery)
        elevation, satellite = warp_inputs(dem, imagery, dimensions, affine, crs)
        cover_source = stack.enter_context(rasterio.open(arguments.cover)) if arguments.cover else None
        cover = warp_cover(cover_source, dimensions, affine, crs)

    print('Rasterizing boundaries and shading terrain', flush=True)
    land, country = raster_layers(dimensions, affine, crs, arguments.land, arguments.boundaries)
    shade, slope, ridge = relief(elevation, affine.a, -affine.e)
    output = grade_land(satellite, elevation, land, country, shade, slope, ridge, affine.a, cover)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output).save(arguments.output, format='WEBP', quality=94, method=4)
    print(f'Wrote {arguments.output}', flush=True)


if __name__ == '__main__':
    main()
