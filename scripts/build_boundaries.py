#!/usr/bin/env python3
"""Build the local teaching map's geographic overlays from the documented sources."""

import argparse
import hashlib
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

import shapefile
from shapely.geometry import LineString, MultiLineString, Polygon, box, shape
from shapely.ops import linemerge


OUTLINE_URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000.json"
PROVINCES_URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"
LAND_URL = "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
GEOGRAPHIC_CRS = "EPSG:4326"
SOUTH_SEA_BOUNDS = (103, 2, 124, 24.75)
MAIN_SOUTH_LIMIT = 17
SOURCES = {
    "administration": {
        "name": "阿里云 DataV.GeoAtlas / 高德开放平台",
        "outline": OUTLINE_URL,
        "provinces": PROVINCES_URL,
        "terms": "https://help.aliyun.com/en/datav/datav-7-0/user-guide/datav-geoatlas-widgets/",
        "usage": "学习交流",
        "inputCrs": "GCJ-02",
        "coordinateMethod": "用于全国尺度叠合的 GCJ-02 近似反算",
    },
    "coast": {
        "name": "Natural Earth 1:10m Land",
        "version": "5.1.1",
        "url": LAND_URL,
        "terms": "https://www.naturalearthdata.com/about/terms-of-use/",
        "usage": "Public Domain",
        "inputCrs": GEOGRAPHIC_CRS,
    },
    "reference": {
        "name": "自然资源部标准地图服务系统",
        "url": "https://bzdt.ch.mnr.gov.cn/",
        "rules": "https://ghzyj.gz.gov.cn/zwgk/newzcfg/ywly/content/mpost_9466245.html",
        "islandNames": "https://www.mfa.gov.cn/web/wjb_673085/zzjg_673183/bjhysws_674671/bhflfg/dtdmxgfl/202303/P020230313585088793886.pdf",
    },
}


def polygons(geometry):
    if geometry.geom_type == "Polygon" and not geometry.is_empty:
        yield geometry
    elif geometry.geom_type in ("MultiPolygon", "GeometryCollection"):
        for part in geometry.geoms:
            yield from polygons(part)


def gcj_offset(lon, lat):
    """Return the conventional GCJ-02 approximation's angular offset in degrees."""
    x = lon - 105
    y = lat - 35
    a = 6378245.0
    eccentricity_squared = 0.006693421622965943
    shift_lat = -100 + 2 * x + 3 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    shift_lon = 300 + x + 2 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    high_frequency = (20 * math.sin(6 * x * math.pi) + 20 * math.sin(2 * x * math.pi)) * 2 / 3
    shift_lat += high_frequency + (20 * math.sin(y * math.pi) + 40 * math.sin(y * math.pi / 3)) * 2 / 3
    shift_lat += (160 * math.sin(y * math.pi / 12) + 320 * math.sin(y * math.pi / 30)) * 2 / 3
    shift_lon += high_frequency + (20 * math.sin(x * math.pi) + 40 * math.sin(x * math.pi / 3)) * 2 / 3
    shift_lon += (150 * math.sin(x * math.pi / 12) + 300 * math.sin(x * math.pi / 30)) * 2 / 3
    latitude = math.radians(lat)
    curvature = 1 - eccentricity_squared * math.sin(latitude)**2
    d_lon = math.degrees(shift_lon * math.sqrt(curvature) / (a * math.cos(latitude)))
    d_lat = math.degrees(shift_lat * curvature**1.5 / (a * (1 - eccentricity_squared)))
    return d_lon, d_lat


def geographic_coord(coord):
    lon, lat = coord
    estimate_lon, estimate_lat = lon, lat
    for _ in range(3):
        d_lon, d_lat = gcj_offset(estimate_lon, estimate_lat)
        estimate_lon, estimate_lat = lon - d_lon, lat - d_lat
    return estimate_lon, estimate_lat


def quantized_line(coords):
    result = []
    for lon, lat in coords:
        point = [round(lon, 4), round(lat, 4)]
        if not result or point != result[-1]:
            result.append(point)
    return result


def quantized_polygon(geometry):
    rings = [quantized_line(ring.coords) for ring in (geometry.exterior, *geometry.interiors)]
    if len(rings[0]) < 4:
        return []
    return [ring for ring in rings if len(ring) >= 4]


def geographic_polygon(geometry):
    return Polygon(
        [geographic_coord(point) for point in geometry.exterior.coords],
        [[geographic_coord(point) for point in ring.coords] for ring in geometry.interiors],
    )


def province_lines(features):
    # GeoAtlas stores each internal border in both adjacent administrative rings.
    edges = Counter()
    for feature in features:
        local_edges = set()
        for polygon in polygons(shape(feature["geometry"])):
            for ring in (polygon.exterior, *polygon.interiors):
                endpoints = list(ring.coords)
                local_edges.update(tuple(sorted((start, end))) for start, end in zip(endpoints, endpoints[1:]))
        edges.update(local_edges)

    shared = MultiLineString([edge for edge, count in edges.items() if count > 1])
    borders = linemerge(shared)
    result = []
    for path in borders.geoms:
        line = LineString([geographic_coord(point) for point in path.coords])
        points = quantized_line(line.simplify(0.026).coords)
        if len(points) > 1 and line.length > 0.006:
            result.append(points)
    return result


def dash_centerline(polygon):
    # The source encodes each stroke as a thin filled polygon. Sample the middle
    # of cross sections along its long axis to retain bends in the original stroke.
    pairs = combinations(polygon.exterior.coords, 2)
    start, end = max(pairs, key=lambda edge: math.dist(*edge))
    length = math.dist(start, end)
    ux = (end[0] - start[0]) / length
    uy = (end[1] - start[1]) / length
    sample_count = math.ceil(length / 0.045)
    points = []
    for index in range(sample_count + 1):
        along = 0.005 + (length - 0.01) * index / sample_count
        lon, lat = start[0] + ux * along, start[1] + uy * along
        cross_section = LineString([(lon - uy, lat + ux), (lon + uy, lat - ux)])
        fill = polygon.intersection(cross_section)
        if not fill.is_empty:
            points.append(geographic_coord((fill.centroid.x, fill.centroid.y)))
    return quantized_line(LineString(points).simplify(0.008).coords)


def south_sea_land(land_zip):
    area = box(*SOUTH_SEA_BOUNDS)
    result = []
    with shapefile.Reader(str(land_zip)) as land:
        for record in land.iterShapes():
            if not box(*record.bbox).intersects(area):
                continue
            for polygon in polygons(shape(record.__geo_interface__)):
                if not polygon.intersects(area):
                    continue
                for part in polygons(polygon.intersection(area).simplify(0.045)):
                    rings = quantized_polygon(part)
                    if rings:
                        result.append(rings)
    return result


def feature(name, lon, lat, kind="feature"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind}


def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def build(outline_path, provinces_path, land_path, output):
    outline_features = json.loads(outline_path.read_text())["features"]
    provincial_features = json.loads(provinces_path.read_text())["features"]
    maritime_feature = next(item for item in provincial_features if item["properties"]["adcode"] == "100000_JD")
    administrative = [item for item in provincial_features if item is not maritime_feature]
    dash_polygons = list(polygons(shape(maritime_feature["geometry"])))
    national_parts = [
        polygon for polygon in polygons(shape(outline_features[0]["geometry"]))
        if all(dash.distance(polygon.centroid) > 0.02 for dash in dash_polygons)
    ]
    main_shapes = [geographic_polygon(polygon) for polygon in national_parts if polygon.centroid.y >= MAIN_SOUTH_LIMIT]
    main_shapes.sort(key=lambda polygon: polygon.area, reverse=True)

    areas = []
    country = []
    islands = []
    for polygon in main_shapes:
        rings = quantized_polygon(polygon.simplify(0.021 if polygon.area > 0.05 else 0.008))
        if rings:
            areas.append(rings)
            layer = country if polygon.area > 0.05 else islands
            layer.extend(rings)

    reef_area = box(107, 2, 119, 18)
    reefs = [
        quantized_line(geographic_polygon(polygon).simplify(0.015).exterior.coords)
        for polygon in national_parts if polygon.area < 0.075 and reef_area.contains(polygon.centroid)
    ]
    sources = {
        **SOURCES,
        "sha256": {
            "outline": sha256(outline_path),
            "provinces": sha256(provinces_path),
            "land": sha256(land_path),
        },
    }
    layers = {
        "china-boundaries.json": {
            "crs": GEOGRAPHIC_CRS,
            "sources": sources,
            "areas": areas,
            "country": country,
            "provinces": province_lines(administrative),
            "islands": islands,
            "islandLabels": [feature("钓鱼岛", 123.475, 25.745), feature("赤尾屿", 124.564, 25.921)],
        },
        "south-china-sea.json": {
            "crs": GEOGRAPHIC_CRS,
            "bounds": SOUTH_SEA_BOUNDS,
            "land": south_sea_land(land_path),
            "reefs": [ring for ring in reefs if len(ring) >= 4],
            "maritime": [dash_centerline(polygon) for polygon in dash_polygons],
            "labels": [
                feature("东沙群岛", 116.72, 20.70),
                feature("西沙群岛", 112.18, 16.55),
                feature("中沙群岛", 114.45, 15.77),
                feature("黄岩岛", 117.75, 15.14),
                feature("南沙群岛", 114.10, 9.88),
                feature("曾母暗沙", 112.2814, 3.9722),
                feature("海南岛", 109.71, 19.18, "context"),
                feature("台湾岛", 120.81, 23.64, "context"),
                feature("河内", 105.83, 21.03, "context"),
                feature("马尼拉", 120.98, 14.59, "context"),
            ],
        },
    }

    output.mkdir(parents=True, exist_ok=True)
    for name, payload in layers.items():
        (output / name).write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("app/public/data"))
    parser.add_argument("--outline", type=Path)
    parser.add_argument("--provinces", type=Path)
    parser.add_argument("--land", type=Path)
    args = parser.parse_args()

    with TemporaryDirectory(prefix="china-boundaries-") as temporary_directory:
        temporary = Path(temporary_directory)
        paths = []
        for supplied, url in ((args.outline, OUTLINE_URL), (args.provinces, PROVINCES_URL), (args.land, LAND_URL)):
            path = supplied or temporary / url.rsplit("/", 1)[-1]
            if supplied is None:
                urlretrieve(url, path)
            paths.append(path)
        build(*paths, args.output)


if __name__ == "__main__":
    main()
