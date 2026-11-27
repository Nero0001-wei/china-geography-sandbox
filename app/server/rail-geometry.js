import { gcj02ToWgs84 } from '../shared/coordinates.js'
import corridors from './data/nanjing-huangshan-rail.json' with { type: 'json' }
import beijingLine from './data/nanjing-beijing-rail.json' with { type: 'json' }
import urumqiLine from './data/nanjing-urumqi-rail.json' with { type: 'json' }

// China Railway's stop sequences. The November 2026 renumbering retained the itineraries.
const beijingServices = new Map([
  [['Z282'], ['南京', '蚌埠', '徐州', '兖州', '德州', '沧州', '天津西', '广阳', '北京丰台']],
  [['Z281'], ['北京丰台', '天津西', '沧州', '徐州', '南京']],
  [['T110', 'N4'], ['南京', '徐州', '德州', '沧州', '天津西', '广阳', '北京']],
  [['T109', 'N3'], ['北京', '天津西', '德州', '徐州', '南京']],
].flatMap(([codes, stops]) => codes.map(code => [code, stops])))

const urumqiServices = new Map([
  [['Z240', 'Z241'], '南京 蚌埠 徐州 商丘 开封 郑州 洛阳 西安 宝鸡 天水 陇西 兰州 西宁 张掖西 酒泉南 嘉峪关南 柳园南 哈密 鄯善北 吐鲁番北 乌鲁木齐'],
  [['Z242', 'Z239'], '乌鲁木齐 吐鲁番北 鄯善北 哈密 柳园南 嘉峪关南 张掖西 西宁 兰州 定西 陇西 武山 甘谷 天水 宝鸡 西安 洛阳 郑州 徐州 蚌埠 南京'],
].flatMap(([codes, names]) => codes.map(code => [code, names.split(' ')])))

function text(value) {
  return typeof value === 'string' ? value.trim() : ''
}

function stationName(stop) {
  return text(stop?.name).replace(/站$/u, '')
}

function stationMatches(stop, name, endpoint) {
  if (stationName(stop) !== name) return false
  const raw = stop?.location
  const values = Array.isArray(raw) ? raw : text(raw).split(/[,\s]+/u)
  if (values.length !== 2 || values.some(value => typeof value !== 'number' && !text(value))) return false
  const [lon, lat] = gcj02ToWgs84(values.map(Number))
  const dx = (lon - endpoint[0]) * 111320 * Math.cos(lat * Math.PI / 180)
  return Math.hypot(dx, (lat - endpoint[1]) * 110574) <= 1000
}

function matchesStops(stops, railway) {
  const intermediate = railway.via_stops ?? railway.viastops ?? railway.via_stop
  if (intermediate == null) return true
  if (!Array.isArray(intermediate)) return false
  let last = 0
  for (const stop of intermediate) {
    const position = stops.indexOf(stationName(stop), last + 1)
    if (position < 0 || position >= stops.length - 1) return false
    last = position
  }
  return true
}

function railSection(line, stops, railway) {
  if (!stops) return null
  const from = stops.indexOf(stationName(railway.departure_stop))
  const to = stops.indexOf(stationName(railway.arrival_stop))
  if (from < 0 || from >= to) return null
  const first = line.stations[stops[from]]
  const last = line.stations[stops[to]]
  const geometry = line.geometry.slice(Math.min(first.index, last.index), Math.max(first.index, last.index) + 1)
  return {
    stops: stops.slice(from, to + 1), distanceMeters: Math.abs(last.meters - first.meters),
    geometry: first.index < last.index ? geometry : geometry.reverse(),
  }
}

// Routes with the same termini can run through different cities. Use the verified
// service, station locations, direction and distance before applying an offline alignment.
export function lookupRailGeometry(railway) {
  const trip = text(railway?.trip) || text(railway?.name).match(/^[A-Z]\d+(?=[(（\s]|$)/u)?.[0]
  const service = corridors.services.find(item => item.trip === trip)
    ?? railSection(beijingLine, beijingServices.get(trip), railway)
    ?? railSection(urumqiLine, urumqiServices.get(trip), railway)
  if (!service) return []
  const { stops, geometry, distanceMeters } = service
  const distance = Number(railway.distance)
  if (!Number.isFinite(distance) || Math.abs(distanceMeters - distance) > distanceMeters * 0.03) return []
  if (!stationMatches(railway.departure_stop, stops[0], geometry[0]) ||
      !stationMatches(railway.arrival_stop, stops.at(-1), geometry.at(-1)) ||
      !matchesStops(stops, railway)) return []
  return geometry
}
