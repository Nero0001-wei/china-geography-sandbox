"""Extract the connected railway used for Nanjing–Ürümqi route references."""
import argparse
import json
from pathlib import Path

import networkx as nx
import osmium

from build_beijing_rail import simplify
from build_nanjing_rail import distance

# Passenger station node, then a surveyed OSM node on the corresponding main track.
# The union of both 12306 stop sequences includes three additional eastbound stops.
STATIONS = {
    "南京": (267225237, 14387270774), "蚌埠": (5369761769, 14387270742),
    "徐州": (5570292382, 14394634168), "商丘": (1775221285, 14394634178),
    "开封": (3476981835, 14394634171), "郑州": (269806844, 14383563571),
    "洛阳": (1577895082, 9631213007), "西安": (9620122767, 14377454166),
    "宝鸡": (7728028162, 14377454051), "天水": (770448206, 14361478072),
    "甘谷": (2953819421, 14359127991), "武山": (3182220016, 14359127984),
    "陇西": (4438875617, 11918031183), "定西": (3840316912, 14359127987),
    "兰州": (269826006, 11698233866), "西宁": (307345596, 14370279338),
    "张掖西": (2987122176, 11830887134), "酒泉南": (2987125725, 8014125938),
    "嘉峪关南": (2987127367, 13507862778), "柳园南": (2987130068, 13451445288),
    "哈密": (7276635778, 3188159166), "鄯善北": (2987138033, 1955796776),
    "吐鲁番北": (2987139656, 14358227623), "乌鲁木齐": (2987146433, 14358227916),
}
MAIN_LINES = {"京沪线", "陇海线", "兰新客专线"}
LANZHOU_EAST = {"夏官营客车联络线", "兰渝线"}
LANZHOU_WEST = "兰州西普高联络线"
# Station tracks connecting the conventional and high-speed passenger lines at Lanzhou West.
LANZHOU_STATION_TRACKS = {1218950745, 588216390, 588216393, 588216350, 588216344, 588216343}


def read_railways(files):
    graph = nx.Graph()
    locations = {}
    timestamps = set()
    station_names = {ids[0]: name for name, ids in STATIONS.items()}
    lines = MAIN_LINES | LANZHOU_EAST | {LANZHOU_WEST}
    for path in sorted(files):
        with osmium.io.Reader(str(path)) as reader:
            timestamps.add(reader.header().get("osmosis_replication_timestamp"))
        for obj in osmium.FileProcessor(str(path)).with_locations().with_filter(osmium.filter.KeyFilter("railway")):
            if obj.is_node() and obj.id in station_names and obj.tags.get("railway") == "station":
                locations[station_names[obj.id]] = (obj.location.lon, obj.location.lat)
            if not obj.is_way() or obj.tags.get("railway") != "rail":
                continue
            name = obj.tags.get("name:zh", obj.tags.get("name", ""))
            crossing = obj.tags.get("service") == "crossover"
            station_track = obj.id in LANZHOU_STATION_TRACKS and obj.tags.get("service") == "siding"
            if name not in lines and not crossing and not station_track:
                continue
            nodes = [(node.ref, (node.lon, node.lat)) for node in obj.nodes]
            for node, xy in nodes:
                graph.add_node(node, xy=xy)
            for (a, p), (b, q) in zip(nodes, nodes[1:]):
                graph.add_edge(a, b, length=distance(p, q), name=name, crossing=crossing, station_track=station_track)
    if len(timestamps) != 1 or not all(timestamps) or locations.keys() != STATIONS.keys():
        raise ValueError("Missing stations or incompatible OSM snapshot dates.")
    for station, (_, node) in STATIONS.items():
        if node not in graph or distance(graph.nodes[node]["xy"], locations[station]) > 600:
            raise ValueError(f"Main-line node is missing or outside the station area at {station}.")
    return graph, timestamps.pop()


def extract(files):
    graph, timestamp = read_railways(files)
    stops = list(STATIONS)
    indices = {stops[0]: 0}
    nodes = [STATIONS[stops[0]][1]]
    main = "京沪线"
    for start, end in zip(stops, stops[1:]):
        if start == "徐州":
            main = "陇海线"
        if start == "兰州":
            main = "兰新客专线"

        def weight(_a, _b, edge):
            if edge["name"] == main or start == "定西" and edge["name"] in LANZHOU_EAST:
                factor = 1
            elif edge["crossing"]:
                factor = 1.5
            elif edge["name"] in MAIN_LINES:
                factor = 1.7
            elif edge["station_track"]:
                factor = 6
            elif edge["name"] == LANZHOU_WEST:
                factor = 10
            else:
                return None
            return edge["length"] * factor

        section = nx.shortest_path(graph, STATIONS[start][1], STATIONS[end][1], weight=weight)
        nodes.extend(section[1:])
        indices[end] = len(nodes) - 1
    if len(set(nodes)) != len(nodes):
        raise ValueError("Unexpected backtracking between passenger stations.")
    points = [graph.nodes[node]["xy"] for node in nodes]
    lengths = [0]
    for a, b in zip(points, points[1:]):
        lengths.append(lengths[-1] + distance(a, b))
    if abs(lengths[-1] - 3617478) > 5000:
        raise ValueError("The traced corridor diverges from the AMap Nanjing–Ürümqi itinerary distance.")
    keep = set(indices.values())
    for start, end in zip(stops, stops[1:]):
        simplify(points, indices[start], indices[end], keep)
    kept = sorted(keep)
    reverse = {source: index for index, source in enumerate(kept)}
    return {
        "attribution": "© OpenStreetMap contributors", "license": "https://opendatacommons.org/licenses/odbl/1-0/",
        "osmTimestamp": timestamp, "sourcePointCount": len(nodes),
        "stations": {name: {"index": reverse[i], "meters": round(lengths[i])} for name, i in indices.items()},
        "geometry": [[round(v, 6) for v in points[i]] for i in kept],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pbf", type=Path, nargs="+", help="Geofabrik China regional extracts from the same snapshot")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "app/server/data/nanjing-urumqi-rail.json")
    args = parser.parse_args()
    result = extract(args.pbf)
    args.output.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(result["sourcePointCount"], len(result["geometry"]), result["stations"]["乌鲁木齐"]["meters"])
