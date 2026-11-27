#!/usr/bin/env python3
"""Download the nine USGS GMTED2010 7.5″ mean-elevation tiles and index them in a VRT."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import time
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

import rasterio
from rasterio.crs import CRS
from rasterio.windows import Window


BASE_URL = ('https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/topo/downloads/'
            'GMTED/Global_tiles_GMTED/075darcsec/mea')
CHUNK_SIZE = 8 * 1024 * 1024
GRID = [(lon, lat) for lat in (10, 30, 50) for lon in (60, 90, 120)]
TILE_WIDTH, TILE_HEIGHT = 14400, 9600
RESOLUTION = 1 / 480


def source_name(lon, lat):
    return f'{lat:02d}N{lon:03d}E_20101117_gmted_mea075.tif'


def read_range(url, target, start, stop, total):
    """Cache only complete chunks. A range-specific URL also works with caching proxies."""
    part = target / f'{start}.part'
    if part.exists() and part.stat().st_size == stop - start:
        return
    expected = f'bytes {start}-{stop - 1}/{total}'
    request = Request(f'{url}?range={start}-{stop - 1}', headers={'Range': f'bytes={start}-{stop - 1}'})
    temp = part.with_suffix('.partial')
    for attempt in range(4):
        try:
            with urlopen(request, timeout=120) as response:
                if response.status != 206 or response.headers.get('Content-Range') != expected:
                    raise ValueError(f'{url} returned an invalid byte range (expected {expected})')
                with temp.open('wb') as output:
                    shutil.copyfileobj(response, output, length=256 * 1024)
            if temp.stat().st_size != stop - start:
                raise OSError(f'Incomplete range from {url}')
            temp.replace(part)
            return
        except (OSError, ValueError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def validate_tile(path, lon, lat):
    with rasterio.open(path) as tile:
        expected = (lon, lat, lon + 30, lat + 20)
        # The GMTED western and northern bounds are shifted by 0.5 arc-seconds.
        if (tile.crs != CRS.from_epsg(4326) or tile.shape != (TILE_HEIGHT, TILE_WIDTH)
            or tile.dtypes != ('int16',) or tile.nodata is None
            or any(abs(a - b) > RESOLUTION / 2 for a, b in zip(tile.bounds, expected))
            or any(abs(r - RESOLUTION) > 1e-10 for r in tile.res)):
            raise ValueError(f'Unexpected GMTED2010 tile grid in {path}: {tile.profile}, {tile.bounds}')
        tile.read(1, window=Window(tile.width - 2, tile.height - 2, 2, 2))
        return tile.bounds, int(tile.nodata)


def prepare(output, workers):
    directory = output.parent / 'dem'
    directory.mkdir(parents=True, exist_ok=True)
    downloads, work = [], []
    for lon, lat in GRID:
        name = source_name(lon, lat)
        path = directory / name
        if path.is_file():
            validate_tile(path, lon, lat)
            continue
        url = f'{BASE_URL}/E{lon:03d}/{name}'
        with urlopen(Request(url, method='HEAD'), timeout=30) as head:
            size = int(head.headers['Content-Length'])
        chunks = directory / (name + '.chunks')
        chunks.mkdir(exist_ok=True)
        starts = list(range(0, size, CHUNK_SIZE))
        downloads.append((lon, lat, path, chunks, starts))
        work.extend((url, chunks, start, min(start + CHUNK_SIZE, size), size) for start in starts)
    print(f'{len(downloads)} source files, {len(work)} byte ranges, {workers} connections', flush=True)
    # Surface errors from every worker; keep completed chunks if a run is interrupted.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in [pool.submit(read_range, *args) for args in work]:
            future.result()
    for lon, lat, path, chunks, starts in downloads:
        temp = path.with_suffix('.partial.tif')
        with temp.open('wb') as out:
            for start in starts:
                with (chunks / f'{start}.part').open('rb') as part:
                    shutil.copyfileobj(part, out, length=1024 * 1024)
        validate_tile(temp, lon, lat)
        temp.replace(path)
        shutil.rmtree(chunks)

    # Preserve USGS's actual transform (including its small common offset).
    north_west, nodata = validate_tile(directory / source_name(60, 50), 60, 50)
    vrt = ET.Element('VRTDataset', rasterXSize=str(3 * TILE_WIDTH), rasterYSize=str(3 * TILE_HEIGHT))
    ET.SubElement(vrt, 'SRS', dataAxisToSRSAxisMapping='2,1').text = 'EPSG:4326'
    ET.SubElement(vrt, 'GeoTransform').text = f'{north_west.left},{RESOLUTION},0,{north_west.top},0,{-RESOLUTION}'
    band = ET.SubElement(vrt, 'VRTRasterBand', dataType='Int16', band='1')
    ET.SubElement(band, 'NoDataValue').text = str(nodata)
    for lon, lat in GRID:
        path = directory / source_name(lon, lat)
        bounds, tile_nodata = validate_tile(path, lon, lat)
        x_offset = (bounds.left - north_west.left) / RESOLUTION
        y_offset = (north_west.top - bounds.top) / RESOLUTION
        if (tile_nodata != nodata or abs(x_offset - round(x_offset)) > 1e-6
            or abs(y_offset - round(y_offset)) > 1e-6):
            raise ValueError(f'Tile grid does not align: {path}')
        source = ET.SubElement(band, 'SimpleSource')
        ET.SubElement(source, 'SourceFilename', relativeToVRT='1').text = os.path.relpath(path, output.parent)
        ET.SubElement(source, 'SourceBand').text = '1'
        for node, col, row in [('SrcRect', 0, 0), ('DstRect', round(x_offset), round(y_offset))]:
            ET.SubElement(source, node, xOff=str(col), yOff=str(row), xSize=str(TILE_WIDTH), ySize=str(TILE_HEIGHT))
    ET.indent(vrt)
    temp = output.with_suffix('.partial.vrt')
    ET.ElementTree(vrt).write(temp, encoding='utf-8', xml_declaration=True)
    with rasterio.open(temp) as mosaic:
        points = [(87.62, 43.83), (121.47, 31.23), (91.13, 29.65), (126.63, 45.75), (110.32, 20.04)]
        if any(sample[0] == nodata for sample in mosaic.sample(points)):
            raise ValueError('Missing elevation at one or more mainland/Hainan verification points')
        print(f'{output}: {mosaic.width} × {mosaic.height}, bounds {mosaic.bounds}', flush=True)
    temp.replace(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='Output VRT. Source TIFFs are cached in dem/ beside it.')
    parser.add_argument('--workers', type=int, default=12)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    prepare(args.output.resolve(), args.workers)
