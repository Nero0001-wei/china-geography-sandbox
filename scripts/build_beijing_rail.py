"""Extract the conventional Beijing–Shanghai main line between Nanjing and Beijing."""
import argparse
import json
from pathlib import Path

import networkx as nx
import osmium

from build_nanjing_rail import distance, difference

# Reviewed railway=station nodes with passenger service on the two verified itineraries.
STATIONS = {
    267225237: "南京", 5369761769: "蚌埠", 5570292382: "徐州", 8452913704: "兖州",
    6198704798: "德州", 12495257433: "沧州", 4126740846: "天津西",
    7733885006: "广阳", 124205138: "北京丰台", 269996666: "北京",
}
# Nodes on OSM ways tagged with the conventional line's name, inside the passenger station.
TERMINALS = [14387270774, 6597147665]


def simplify(points, start, end, keep):
    """Ramer–Douglas–Peucker in local metres, retaining the original OSM vertices."""
    a, b = points[start], points[end]
    latitude = (a[1] + b[1]) / 2
    dx, dy = difference(b, a, latitude)
    length2 = dx * dx + dy * dy
    worst, split = 0, None
    for i in range(start + 1, end):
        px, py = difference(points[i], a, latitude)
        t = min(1, max(0, (px * dx + py * dy) / length2)) if length2 else 0
        error2 = (px - t * dx) ** 2 + (py - t * dy) ** 2
        if error2 > worst:
            worst, split = error2, i
    if worst > 10 ** 2:
        keep.add(split)
        simplify(points, start, split, keep)
        simplify(points, split, end, keep)


def build(files):
    graph, stations, times = nx.Graph(), {}, set()
    for path in sorted(files):
        with osmium.io.Reader(str(path)) as reader:
            times.add(reader.header().get("osmosis_replication_timestamp"))
        for obj in osmium.FileProcessor(str(path)).with_locations().with_filter(osmium.filter.KeyFilter("railway")):
            if obj.is_node() and obj.id in STATIONS:
                stations[STATIONS[obj.id]] = [obj.location.lon, obj.location.lat]
            if not obj.is_way() or obj.tags.get("railway") != "rail":
                continue
            main = obj.tags.get("name") == "京沪线"
            if not main and (obj.tags.get("name") or obj.tags.get("service") != "crossover"):
                continue
            vertices = [(n.ref, (n.lon, n.lat)) for n in obj.nodes]
            for node, location in vertices:
                graph.add_node(node, point=location)
            for (a, p), (b, q) in zip(vertices, vertices[1:]):
                graph.add_edge(a, b, weight=distance(p, q) * (1 if main else 7))
    if len(times) != 1 or len(stations) != len(STATIONS):
        raise ValueError("Missing station or conflicting OSM snapshot timestamps.")
    nodes = nx.shortest_path(graph, *TERMINALS, weight="weight")
    pts = [graph.nodes[n]["point"] for n in nodes]
    lengths = [0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + distance(a, b))
    indices = {}
    for name in STATIONS.values():
        gap, index = min((distance(p, stations[name]), i) for i, p in enumerate(pts))
        if gap > 200 or index <= max(indices.values(), default=-1):
            raise ValueError(f"Track failed station check at {name}.")
        indices[name] = index
    keep = set(indices.values())
    for first, last in zip(indices.values(), list(indices.values())[1:]):
        simplify(pts, first, last, keep)
    kept = sorted(keep)
    points = [[round(v, 6) for v in pts[i]] for i in kept]
    return {
        "attribution": "© OpenStreetMap contributors", "license": "https://opendatacommons.org/licenses/odbl/1-0/",
        "osmTimestamp": times.pop(), "sourcePointCount": len(pts),
        "stations": {name: {"index": kept.index(i), "meters": round(lengths[i])} for name, i in indices.items()},
        "geometry": points,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pbf", type=Path, nargs=6, help="Geofabrik Jiangsu, Anhui, Shandong, Hebei, Tianjin and Beijing OSM PBF files")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "app/server/data/nanjing-beijing-rail.json")
    args = parser.parse_args()
    data = build(args.pbf)
    args.output.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(data["sourcePointCount"], len(data["geometry"]), data["stations"])
