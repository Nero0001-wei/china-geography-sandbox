import { gcj02ToWgs84 } from '../shared/coordinates.js'
import { isCoachService } from '../shared/coach-service.js'
import { lookupRailGeometry } from './rail-geometry.js'

export function readLocation(value) {
  const fields = typeof value === 'string'
    ? (value.includes(',') ? value.split(',') : value.trim().split(/\s+/u))
    : value
  if (!Array.isArray(fields) || fields.length !== 2) return null
  if (fields.some((part) => typeof part !== 'number' && (typeof part !== 'string' || !part.trim()))) return null
  const [lon, lat] = fields.map(Number)
  return lon >= 70 && lon <= 140 && lat >= 3 && lat <= 60 ? [lon, lat] : null
}

export function formatLocation(point) {
  return point.map((number) => number.toFixed(6)).join(',')
}

export function cleanText(value, max = 180) {
  return typeof value === 'string' ? value.trim().slice(0, max) : ''
}

function wgs84(value) {
  const point = readLocation(value)
  return point ? gcj02ToWgs84(point) : null
}

function samePoint(a, b) {
  return Boolean(a && b && a[0] === b[0] && a[1] === b[1])
}

function polyline(value) {
  // Transit v5 wraps the coordinate string in a polyline object. Driving v5 returns the string directly.
  const text = typeof value === 'string' ? value : value?.polyline
  if (typeof text !== 'string') return []
  const points = []
  for (const piece of text.split(';')) {
    if (!piece.trim()) continue
    const point = wgs84(piece)
    if (!point) return []
    if (!samePoint(points.at(-1), point)) points.push(point)
  }
  return points
}

function distanceBetween(a, b) {
  const longitudeMeters = (a[0] - b[0]) * Math.cos(a[1] * Math.PI / 180) * 111_320
  const latitudeMeters = (a[1] - b[1]) * 110_554
  return Math.hypot(longitudeMeters, latitudeMeters)
}

function stepTracks(steps, maximumGap = 25) {
  const tracks = []
  for (const step of steps) {
    const geometry = polyline(step?.polyline)
    const previous = tracks.at(-1)
    if (!previous || Boolean(previous.geometry.length) !== Boolean(geometry.length) ||
      (geometry.length && distanceBetween(previous.geometry.at(-1), geometry[0]) > maximumGap)) {
      tracks.push({ geometry, steps: [step] })
      continue
    }
    const sharedPoint = samePoint(previous.geometry.at(-1), geometry[0])
    previous.geometry.push(...(sharedPoint ? geometry.slice(1) : geometry))
    previous.steps.push(step)
  }
  return tracks
}

function metric(value) {
  if (typeof value !== 'number' && (typeof value !== 'string' || !value.trim())) return null
  const amount = Number(value)
  return Number.isFinite(amount) && amount >= 0 ? amount : null
}

function sumMetrics(values) {
  return values.length && values.every((value) => value !== null)
    ? values.reduce((total, value) => total + value, 0)
    : null
}

function stop(name, location = null) {
  return { name: cleanText(name), location }
}

function station(value) {
  const result = stop(value?.name, wgs84(value?.location))
  const cityCode = cleanText(value?.citycode || value?.cityCode)
  const adcode = cleanText(value?.adcode)
  const city = cleanText(value?.cityname ?? value?.city)
  if (/^\d{3,4}$/.test(cityCode)) result.cityCode = cityCode
  if (/^\d{6}$/.test(adcode)) result.adcode = adcode
  if (city && !/^\d+$/.test(city)) result.city = city
  return result
}

function waypoint(place) {
  return { ...place, gcj02: place.location, location: gcj02ToWgs84(place.location) }
}

function segment(type, name, info) {
  return { type, name, ...info, geometry: info.geometry.length > 1 ? info.geometry : [] }
}

function trackSegments(tracks, type, name, from, to, totals) {
  if (!tracks.length) return [segment(type, name, { ...totals, from, to, geometry: [] })]
  return tracks.map(({ steps, geometry }, index) => segment(type, name, {
    distanceMeters: tracks.length === 1 ? totals.distanceMeters : sumMetrics(steps.map((step) => metric(step?.step_distance ?? step?.distance))),
    durationSeconds: tracks.length === 1 ? totals.durationSeconds : sumMetrics(steps.map((step) => metric(step?.cost?.duration ?? step?.duration))),
    from: index === 0 ? from : stop('', geometry[0]),
    to: index === tracks.length - 1 ? to : stop('', geometry.at(-1)),
    geometry,
  }))
}

function walkSegments(walk) {
  const steps = Array.isArray(walk?.steps) ? walk.steps : []
  const distanceMeters = metric(walk?.distance)
  if (!steps.length && !distanceMeters && !metric(walk?.cost?.duration ?? walk?.duration)) return []
  const tracks = stepTracks(steps)
  return trackSegments(tracks, 'walk', '步行', stop('', wgs84(walk.origin)), stop('', wgs84(walk.destination)), {
    distanceMeters: distanceMeters ?? sumMetrics(steps.map((step) => metric(step?.distance))),
    durationSeconds: metric(walk.cost?.duration ?? walk.duration) ?? sumMetrics(steps.map((step) => metric(step?.duration))),
  })
}

function passengerMode(category, name) {
  // Stop names in parentheses often mention a ferry terminal or a coach station on an ordinary bus line.
  const service = cleanText(name).split(/[（(]/u)[0]
  const kind = cleanText(category)
  if (/地铁|城市轨道|有轨电车|轻轨/u.test(kind)) return 'metro'
  if (/轮渡|客轮|客船|水上客运/u.test(kind) || /(?:客轮|客船|轮渡|客运航线)(?:航线|专线)?$/u.test(service)) return 'ferry'
  if (isCoachService(kind) || isCoachService(service)) return 'coach'
  return null
}

function busSegment(bus) {
  // Lines inside one bus leg are alternatives. Display the first applicable option in Amap's order.
  const line = Array.isArray(bus?.buslines) ? bus.buslines.find((candidate) => cleanText(candidate?.name)) : null
  if (!line) return null
  const type = passengerMode(line.type, line.name) || 'bus'
  return segment(type, cleanText(line.name), {
    distanceMeters: metric(line.distance), durationSeconds: metric(line.cost?.duration ?? line.duration),
    from: station(line.departure_stop), to: station(line.arrival_stop), geometry: polyline(line.polyline),
  })
}

function railwaySegment(railway) {
  const name = cleanText(railway?.name) || cleanText(railway?.trip)
  if (!name) return null
  const from = station(railway.departure_stop)
  const to = station(railway.arrival_stop)
  const intermediate = railway.via_stops ?? railway.viastops ?? railway.via_stop
  const providerTrack = polyline(railway.polyline)
  const type = passengerMode(railway.type, name) || 'rail'
  const mappedTrack = type === 'rail' && providerTrack.length < 2 ? lookupRailGeometry(railway) : []
  return segment(type, name, {
    ...(cleanText(railway.trip) ? { trip: cleanText(railway.trip) } : {}),
    distanceMeters: metric(railway.distance), durationSeconds: metric(railway.cost?.duration ?? railway.duration ?? railway.time),
    from, to, geometry: mappedTrack.length ? mappedTrack : providerTrack,
    ...(Array.isArray(intermediate) && intermediate.length ? { viaStops: intermediate.map(station) } : {}),
    ...(mappedTrack.length ? { geometrySource: 'osm' } : {}),
  })
}

export function missingTaxiEndpoints(taxi) {
  if (!taxi || polyline(taxi.polyline).length > 1) return null
  const from = readLocation(taxi.startpoint)
  const to = readLocation(taxi.endpoint)
  if (!from || !to || samePoint(from, to)) return null
  return { origin: formatLocation(from), destination: formatLocation(to) }
}

export function matchedRoadGeometry(path, { origin, destination }) {
  if (!Array.isArray(path?.steps)) return []
  // Adjacent driving instructions sometimes snap to opposite sides of a junction.
  const tracks = stepTracks(path.steps, 35)
  if (tracks.length !== 1) return []
  const geometry = tracks[0].geometry
  if (geometry.length < 2 || distanceBetween(geometry[0], wgs84(origin)) > 150 ||
      distanceBetween(geometry.at(-1), wgs84(destination)) > 150) return []
  return geometry
}

function taxiSegment(taxi, supplemental) {
  if (!taxi || !(readLocation(taxi.startpoint) || readLocation(taxi.endpoint) || metric(taxi.distance))) return null
  return segment('taxi', '出租车', {
    distanceMeters: metric(taxi.distance), durationSeconds: metric(taxi.drivetime),
    from: stop(taxi.startname, wgs84(taxi.startpoint)), to: stop(taxi.endname, wgs84(taxi.endpoint)),
    geometry: supplemental || polyline(taxi.polyline),
    ...(supplemental ? { geometrySource: 'amap-driving' } : {}),
  })
}

function route(segments, start, end, totals) {
  // For viewport framing only. Render the independently sourced segment geometries instead.
  const geometry = [start.location, ...segments.flatMap((part) => [part.from.location, ...part.geometry, part.to.location]), end.location]
    .filter((point) => point !== null)
    .filter((point, index, points) => !samePoint(points[index - 1], point))
  return { ...totals, geometry, start, end, source: 'amap', segments }
}

export function drivingRoutes(paths, origin, destination) {
  const start = waypoint(origin)
  const end = waypoint(destination)
  return paths.flatMap((path) => {
    const steps = Array.isArray(path?.steps) ? path.steps : []
    const totals = {
      distanceMeters: metric(path?.distance),
      durationSeconds: metric(path?.cost?.duration) ?? sumMetrics(steps.map((step) => metric(step?.cost?.duration))),
    }
    if (totals.distanceMeters === null && totals.durationSeconds === null && !steps.length) return []
    const tracks = stepTracks(steps)
    const segments = trackSegments(tracks, 'drive', '驾车', stop(start.name, start.location), stop(end.name, end.location), totals)
    return [route(segments, start, end, totals)]
  })
}

export function transitRoutes(transits, origin, destination, taxiRoads = new Map()) {
  const start = waypoint(origin)
  const end = waypoint(destination)
  return transits.flatMap((transit) => {
    if (!Array.isArray(transit?.segments)) return []
    const segments = transit.segments.flatMap((item) => [
      ...walkSegments(item?.walking), busSegment(item?.bus), railwaySegment(item?.railway), taxiSegment(item?.taxi, taxiRoads.get(item?.taxi)),
    ].filter(Boolean))
    if (!segments.length) return []
    const totals = {
      distanceMeters: metric(transit.distance) ?? sumMetrics(segments.map((part) => part.distanceMeters)),
      durationSeconds: metric(transit.cost?.duration ?? transit.duration),
    }
    return [route(segments, start, end, totals)]
  })
}
