#!/usr/bin/env python3
"""Build the map search index of administrative place names from GeoAtlas."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen

from build_boundaries import MAIN_SOUTH_LIMIT, PROVINCES_URL, geographic_coord


GEOATLAS_URL = PROVINCES_URL.rsplit("/", 1)[0]
OUTPUT = Path(__file__).resolve().parents[1] / "app/shared/map-places.json"
DISTRICT_CHILDREN = {110000, 120000, 310000, 500000, 810000, 820000}
SHORT_PROVINCE_NAMES = {
    150000: "内蒙古",
    450000: "广西",
    540000: "西藏",
    640000: "宁夏",
    650000: "新疆",
}
NAME_SUFFIXES = ("特别行政区", "地区", "林区", "省", "市", "盟", "县")


def read_areas(adcode, source_dir):
    filename = f"{adcode}_full.json"
    if source_dir:
        data = json.loads((source_dir / filename).read_text(encoding="utf-8"))
    else:
        with urlopen(f"{GEOATLAS_URL}/{filename}", timeout=15) as response:
            data = json.load(response)
    return [feature["properties"] for feature in data["features"]]


def search_place(area, province=None):
    code = area["adcode"]
    name = area["name"]
    lon, lat = geographic_coord(area["center"])
    kind = "city" if province else "province"
    place = {"id": f"{kind}-{code}", "name": name, "kind": kind, "lon": round(lon, 6), "lat": round(lat, 6)}
    if province:
        place["subtitle"] = province
    suffix = next((ending for ending in NAME_SUFFIXES if name.endswith(ending)), "")
    short_name = SHORT_PROVINCE_NAMES.get(code, name)
    if short_name == name and not name.endswith("自治县"):
        short_name = name.removesuffix(suffix)
    if short_name != name and len(short_name) >= 2:
        place["aliases"] = [short_name]
    return place


def build(source_dir):
    provinces = [area for area in read_areas(100000, source_dir) if area.get("level") == "province"]
    results = [search_place(province) for province in provinces]
    city_parents = [
        province for province in provinces
        if province["childrenNum"] and province["adcode"] not in DISTRICT_CHILDREN
    ]

    with ThreadPoolExecutor(max_workers=6) as workers:
        city_lists = workers.map(lambda province: read_areas(province["adcode"], source_dir), city_parents)
        for province, cities in zip(city_parents, city_lists, strict=True):
            for city in cities:
                if city.get("level") != "city" or not city.get("center"):
                    continue
                place = search_place(city, province["name"])
                if place["lat"] >= MAIN_SOUTH_LIMIT:
                    results.append(place)
    return sorted(results, key=lambda place: place["id"].split("-")[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="directory containing saved GeoAtlas *_full.json inputs")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    places = build(args.source_dir)
    records = ",\n".join("  " + json.dumps(place, ensure_ascii=False, separators=(",", ":")) for place in places)
    args.output.write_text(f"[\n{records}\n]\n", encoding="utf-8")
    print(f"{args.output}: {len(places)} places")


if __name__ == "__main__":
    main()
