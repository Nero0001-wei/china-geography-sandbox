"""Cache ESA WorldCover 2021 COG overviews intersecting China and build the tint raster."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
from xml.etree import ElementTree as ET

import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = ('https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/'
              'ESA_WorldCover_10m_2021_v200_{tile}_Map.tif')
SIZE = 2250  # the 16x categorical overview of each 36,000-square 3-degree COG
# Signed sRGB pigment corrections and water fraction in percent, by ESA class.
# VRT stores the three corrections biased by 64, and water biased by one, so
# zero in all four bands remains available for missing source data.
CLASSES = {
    10: (-16, -8, -3, 0),   # tree cover
    20: (-5, -1, -2, 0),    # shrubland
    30: (1, 3, -1, 0),      # grassland
    40: (5, 3, -4, 0),      # cropland
    50: (18, 10, 13, 0),    # built-up
    60: (3, 1, -1, 0),      # bare / sparse vegetation
    70: (0, 0, 0, 0),       # snow / ice
    80: (0, 0, 0, 100),     # permanent water
    90: (-6, 3, 4, 0),      # herbaceous wetland
    95: (-9, 1, 3, 0),      # mangroves
    100: (0, 1, 0, 0),      # moss and lichen
}


def cache_tile(task):
    lon, lat, folder = task
    tile = f'N{lat:02}E{lon:03}'
    path = folder / f'{tile}.tif'
    if path.exists():
        return lon, lat, path
    temporary = path.with_suffix('.part.tif')
    for attempt in range(3):
        try:
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='40',
                              CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif'), rasterio.open(SOURCE_URL.format(tile=tile)) as src:
                classes = src.read(1, out_shape=(SIZE, SIZE))
            with rasterio.open(temporary, 'w', driver='GTiff', width=SIZE, height=SIZE, count=1, dtype='uint8',
                               crs='EPSG:4326', transform=from_origin(lon, lat + 3, 3 / SIZE, 3 / SIZE),
                               nodata=0, tiled=True, compress='deflate') as dst:
                dst.write(classes, 1)
            temporary.replace(path)
            return lon, lat, path
        except rasterio.errors.RasterioIOError:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def write_vrt(tiles, destination):
    west = min(x for x, _, _ in tiles)
    north = max(y for _, y, _ in tiles) + 3
    width = (max(x for x, _, _ in tiles) + 3 - west) * SIZE // 3
    height = (north - min(y for _, y, _ in tiles)) * SIZE // 3
    vrt = ET.Element('VRTDataset', rasterXSize=str(width), rasterYSize=str(height))
    ET.SubElement(vrt, 'SRS', dataAxisToSRSAxisMapping='2,1').text = 'EPSG:4326'
    ET.SubElement(vrt, 'GeoTransform').text = f'{west},{3 / SIZE},0,{north},0,{-3 / SIZE}'
    for index, bias in enumerate((64, 64, 64, 1)):
        band = ET.SubElement(vrt, 'VRTRasterBand', dataType='Byte', band=str(index + 1))
        ET.SubElement(band, 'NoDataValue').text = '0'
        lut = ','.join(f'{code}:{values[index] + bias}' for code, values in CLASSES.items())
        for lon, lat, path in tiles:
            source = ET.SubElement(band, 'ComplexSource')
            ET.SubElement(source, 'SourceFilename', relativeToVRT='1').text = str(path.relative_to(destination.parent))
            ET.SubElement(source, 'SourceBand').text = '1'
            ET.SubElement(source, 'SrcRect', xOff='0', yOff='0', xSize=str(SIZE), ySize=str(SIZE))
            ET.SubElement(source, 'DstRect', xOff=str((lon - west) * SIZE // 3),
                          yOff=str((north - lat - 3) * SIZE // 3), xSize=str(SIZE), ySize=str(SIZE))
            ET.SubElement(source, 'NODATA').text = '0'
            ET.SubElement(source, 'LUT').text = lut
    ET.ElementTree(vrt).write(destination.with_suffix('.tmp'), encoding='utf-8')
    destination.with_suffix('.tmp').replace(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--boundaries', type=Path, default=ROOT / 'app/public/data/china-boundaries.json')
    parser.add_argument('--output', type=Path, required=True, help='Destination .vrt, with a sibling tile cache')
    parser.add_argument('--workers', type=int, default=10)
    args = parser.parse_args()
    areas = json.loads(args.boundaries.read_text())['areas']
    region = unary_union([shape({'type': 'Polygon', 'coordinates': rings}) for rings in areas])
    west, south, east, north = (int(v // 3) * 3 for v in region.bounds)
    folder = args.output.parent / 'worldcover-2021-v200-16x'
    folder.mkdir(exist_ok=True, parents=True)
    jobs = [(lon, lat, folder) for lat in range(south, north + 1, 3) for lon in range(west, east + 1, 3)
            if region.intersects(box(lon, lat, lon + 3, lat + 3))]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        tiles = list(pool.map(cache_tile, jobs))
    write_vrt(tiles, args.output)
    print(f'{len(tiles)} WorldCover overviews registered in {args.output}')


if __name__ == '__main__':
    main()
