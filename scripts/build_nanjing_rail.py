"""Build the two reviewed Nanjing–Huangshan railway alignments from Geofabrik OSM PBFs."""
import argparse
import json
import math
from pathlib import Path

import networkx as nx
import osmium


# OSM railway nodes on the track through the passenger platforms. Both itineraries leave
# Nanjing South to the west. G7207 enters Chizhou station and reverses towards Jiuhuashan.
NANJING_START = 2833128598
APPROACH = 1693620565
SERVICES = {
    "G7207": {
        "stops": ["南京南", "马鞍山东", "芜湖", "池州", "九华山", "黄山西"],
        "lines": {"宁安客专线", "池黄高速线"},
        "nodes": [NANJING_START, 10913992254, 10667605780],
        "beyond": 10667605773,
    },
    "G8965": {
        "stops": ["南京南", "马鞍山东", "芜湖", "宣城", "黄山北"],
        "lines": {"宁安客专线", "合杭高速线", "宣绩高速线", "绩溪北联络线", "合福高速线"},
        "nodes": [NANJING_START, 5283380025],
        "beyond": 8176135762,
    },
}
# Railway station nodes (not the metro stations or the entrances).
STATIONS = {
    2483530943: "南京南", 3798940125: "马鞍山东", 9235207765: "芜湖",
    9242148039: "池州", 10667605849: "九华山", 10667605781: "黄山西",
    6240058953: "宣城", 3656291049: "黄山北",
}


def difference(a, b, at_latitude):
    return ((a[0] - b[0]) * 111320 * math.cos(math.radians(at_latitude)), (a[1] - b[1]) * 110574)


def distance(a, b):
    return math.hypot(*difference(a, b, (a[1] + b[1]) / 2))


def nearest_point(points, location):
    """Find the closest point on the mapped rails, interpolating only along OSM edges."""
    candidates = []
    for index, (a, b) in enumerate(zip(points, points[1:])):
        dx, dy = difference(b, a, location[1])
        px, py = difference(location, a, location[1])
        length_squared = dx * dx + dy * dy
        fraction = max(0, min(1, (px * dx + py * dy) / length_squared)) if length_squared else 0
        point = [a[i] + (b[i] - a[i]) * fraction for i in range(2)]
        candidates.append((distance(location, point), index, point))
    return min(candidates)


def load(paths):
    graph, stations, timestamps = nx.Graph(), {}, set()
    for file in sorted(paths):
        with osmium.io.Reader(str(file)) as reader:
            timestamps.add(reader.header().get("osmosis_replication_timestamp"))
        processor = osmium.FileProcessor(str(file)).with_locations().with_filter(osmium.filter.KeyFilter("railway"))
        for obj in processor:
            if obj.is_node() and obj.id in STATIONS:
                stations[STATIONS[obj.id]] = (obj.location.lon, obj.location.lat)
            if not obj.is_way() or obj.tags.get("railway") != "rail":
                continue
            nodes = list(obj.nodes)
            if not nodes or not (117.4 < nodes[0].lon < 119.1 and 29.72 < nodes[0].lat < 32.09):
                continue
            coords = [(node.ref, (node.lon, node.lat)) for node in nodes]
            for node, point in coords:
                graph.add_node(node, point=point)
            for (a, p), (b, q) in zip(coords, coords[1:]):
                graph.add_edge(a, b, meters=distance(p, q), name=obj.tags.get("name", ""), service=obj.tags.get("service", ""))
    if len(timestamps) != 1:
        raise ValueError("Use extracts from the same OSM snapshot.")
    return graph, stations, timestamps.pop()


def alignment(graph, stations, spec):
    def cost(a, b, edge):
        if edge["name"] in spec["lines"]:
            return edge["meters"]
        if not edge["name"] and edge["service"] in {"yard", "crossover", "siding", ""}:
            return edge["meters"] * 5  # Prefer named main tracks while permitting mapped station switches.
        return None

    nodes = [APPROACH, spec["nodes"][0]]
    for start, end in zip(spec["nodes"], spec["nodes"][1:]):
        nodes.extend(nx.shortest_path(graph, start, end, weight=cost)[1:])
    nodes.append(spec["beyond"])
    assert all(graph.has_edge(a, b) for a, b in zip(nodes, nodes[1:]))
    points = [graph.nodes[n]["point"] for n in nodes]
    stops = spec["stops"]
    start_distance, first, start = nearest_point(points, stations[stops[0]])
    end_distance, last, end = nearest_point(points, stations[stops[-1]])
    if max(start_distance, end_distance) > 200 or first >= last:
        raise ValueError("Terminal station no longer matches the mapped track.")
    points = [start, *points[first + 1:last + 1], end]
    last_index = -1
    for name in stops:
        separation, index, _ = nearest_point(points, stations[name])
        if separation > 500 or index < last_index:
            raise ValueError(f"Track no longer runs through {name} in timetable order.")
        last_index = index
    length = round(sum(distance(a, b) for a, b in zip(points, points[1:])))
    return {"stops": stops, "distanceMeters": length, "geometry": [[round(x, 6), round(y, 6)] for x, y in points]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pbf", type=Path, nargs=2, help="Anhui and Jiangsu OSM PBF extracts")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "app/server/data/nanjing-huangshan-rail.json")
    args = parser.parse_args()
    graph, stations, timestamp = load(args.pbf)
    data = {"attribution": "© OpenStreetMap contributors", "license": "https://opendatacommons.org/licenses/odbl/1-0/",
            "osmTimestamp": timestamp, "services": []}
    for train, spec in SERVICES.items():
        route = alignment(graph, stations, spec)
        print(train, len(route["geometry"]), route["distanceMeters"])
        data["services"].append({"trip": train, **route})
    args.output.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
