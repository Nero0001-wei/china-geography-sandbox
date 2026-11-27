#!/usr/bin/env python3
"""Clip Natural Earth roads to the sand table and generalise shared road junctions together."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

import shapefile
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import unary_union
from shapely.prepared import prep


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://naturalearth.s3.amazonaws.com/5.0.0/10m_cultural/ne_10m_roads.zip"
SHA256 = "880b235383a1e1ccf33f4ea6f82b6755a2ffbce07e3974e412b43e88fe954ae9"
TIERS = ("expressway", "arterial", "secondary")
TOLERANCE_DEGREES = 0.004


def tier_for(record):
    if record.featurecla != "Road" or record.type in {"Track", "Ferry", "Trail"}:
        return None
    if record.expressway == 1:
        return "expressway"
    if record.type == "Major Highway" or record.scalerank <= 5:
        return "arterial"
    return "secondary"


def lines_of(geometry):
    if geometry.is_empty:
        return
    if geometry.geom_type == "LineString":
        yield geometry
    elif geometry.geom_type in {"MultiLineString", "GeometryCollection"}:
        for part in geometry.geoms:
            yield from lines_of(part)


def within_country(line, country, prepared):
    if prepared.covers(line):
        return [line]
    if prepared.intersects(line):
        return list(lines_of(line.intersection(country)))
    return []


def simplify(coords, vertex_uses):
    # Keep shared source vertices fixed so a side road still joins a simplified trunk.
    result = [coords[0]]
    start = 0
    for end in range(1, len(coords)):
        if end == len(coords) - 1 or vertex_uses[coords[end]] > 1:
            if end == start + 1:
                result.append(coords[end])
            else:
                segment = LineString(coords[start:end + 1])
                result.extend(list(segment.simplify(TOLERANCE_DEGREES).coords)[1:])
            start = end
    return LineString(result)


def build(archive, boundaries, output):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Road archive does not match the pinned Natural Earth 5.0.0 release")
    boundary = json.loads(boundaries.read_text())
    if boundary.get("crs") != "EPSG:4326":
        raise ValueError("Boundary polygons must use WGS84 longitude and latitude")
    country = unary_union([Polygon(shell, holes) for shell, *holes in boundary["areas"]])
    prepared = prep(country)
    roads = []
    vertex_uses = Counter()
    with shapefile.Reader(str(archive)) as source:
        for item in source.iterShapeRecords(bbox=country.bounds, fields=["type", "featurecla", "expressway", "scalerank"]):
            tier = tier_for(item.record)
            if not tier:
                continue
            for line in lines_of(shape(item.shape.__geo_interface__)):
                for clipped in within_country(line, country, prepared):
                    coords = list(clipped.coords)
                    vertex_uses.update(coords)
                    roads.append((tier, coords))

    tiers = {tier: [] for tier in TIERS}
    for tier, coords in roads:
        line = simplify(coords, vertex_uses)
        # A simplified bend beside a border or coastline can briefly leave the area.
        for clipped in within_country(line, country, prepared):
            points = []
            for lon, lat in clipped.coords:
                point = (round(lon, 4), round(lat, 4))
                if not points or point != points[-1]:
                    points.append(point)
            if len(points) >= 2:
                tiers[tier].append(points)

    data = {"version": 1, "tiers": [{"id": tier, "lines": lines} for tier, lines in tiers.items()]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, separators=(",", ":")) + "\n")
    for tier, lines in tiers.items():
        print(f"{tier}: {len(lines):,} lines, {sum(map(len, lines)):,} vertices")
    print(f"{output}: {output.stat().st_size:,} bytes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Use a local copy of ne_10m_roads.zip")
    parser.add_argument("--boundaries", type=Path, default=ROOT / "app/public/data/china-boundaries.json")
    parser.add_argument("--output", type=Path, default=ROOT / "app/public/data/roads/overview.json")
    args = parser.parse_args()
    with TemporaryDirectory() as temp:
        archive = args.archive or Path(temp) / "ne_10m_roads.zip"
        if args.archive is None:
            urlretrieve(SOURCE, archive)
        build(archive, args.boundaries, args.output)


if __name__ == "__main__":
    main()
