import { isCoachService } from '../shared/coach-service.js'

const TRAVEL_SECONDS = 18
const MIN_RUN_SECONDS = 2
const GAP_SECONDS = 0.75
const HEADING_WINDOW_SECONDS = 0.07
const JOIN_EPSILON = 1e-7

const vehiclesByType = new Map([
  ['drive', 'car'],
  ['flight', 'plane'],
  ['high-speed-rail', 'high-speed-rail'],
  ['intercity-rail', 'intercity-rail'],
  ['coach', 'coach'],
])

function cityAdcode(place) {
  const code = String(place?.adcode ?? '')
  if (!/^\d{6}$/.test(code)) return ''
  if (/^(11|12|31|50)/.test(code)) return code.slice(0, 2)
  if (code.endsWith('0000')) return ''
  return code.slice(2, 4) === '90' ? code : code.slice(0, 4)
}

function cityName(place) {
  const name = place?.city
  return typeof name === 'string' && name !== '市辖区' ? name.trim().replace(/市$/u, '') : ''
}

export function sameJourneyCity(a, b) {
  const codeA = cityAdcode(a), codeB = cityAdcode(b)
  if (codeA && codeB) return codeA === codeB
  const nameA = cityName(a), nameB = cityName(b)
  if (nameA && nameB) return nameA === nameB
  const areaA = a?.cityCode, areaB = b?.cityCode
  return areaA && areaB ? Number(areaA) === Number(areaB) : null
}

function distanceKm(a, b) {
  if (![a?.[0], a?.[1], b?.[0], b?.[1]].every(Number.isFinite)) return Infinity
  const longitudeScale = Math.cos((a[1] + b[1]) * Math.PI / 360)
  return Math.hypot((a[0] - b[0]) * longitudeScale, a[1] - b[1]) * 111.32
}

function intercityFerry(segment, route) {
  if (sameJourneyCity(segment.from, segment.to) === false || /城际|跨市|省际|跨省/u.test(segment.name ?? '')) return true
  if (sameJourneyCity(route?.start, route?.end) !== false) return false
  const start = route.start, end = route.end
  const origin = cityName(start), destination = cityName(end)
  const label = [segment.name, segment.from?.name, segment.to?.name].join(' ')
  if (origin && destination && label.includes(origin) && label.includes(destination)) return true
  const span = distanceKm(start.location, end.location)
  if (!Number.isFinite(span)) return false
  const radius = Math.min(30, span * 0.25)
  return distanceKm(segment.from?.location ?? segment.geometry?.[0], start.location) <= radius &&
    distanceKm(segment.to?.location ?? segment.geometry?.at(-1), end.location) <= radius
}

export function railVehicleForService(segment) {
  const name = [segment.trip, segment.name].filter(Boolean).join(' ').normalize('NFKC')
  const service = name.match(/(?:^|[^a-z0-9])([GDCZTKYSL])\s*\d+/iu)?.[1].toUpperCase()
  if (service) {
    if (service === 'C') return 'intercity-rail'
    if (service === 'G' || service === 'D') return 'high-speed-rail'
    return service === 'S' ? null : 'train'
  }
  if (/市域|市郊/u.test(name)) return null
  if (/城际/u.test(name)) return 'intercity-rail'
  return /高铁|高速铁路|动车/u.test(name) ? 'high-speed-rail' : 'train'
}

export function vehicleForSegment(segment, route) {
  if (!segment || segment.unconfirmed || segment.schematic || segment.unavailable ||
    segment.localTransfer || sameJourneyCity(segment.from, segment.to) === true) return null
  if (segment.type === 'rail') return railVehicleForService(segment)
  if (segment.type === 'ferry') return intercityFerry(segment, route) ? 'ferry' : null
  if (segment.type === 'bus') return isCoachService(segment.name) ? 'coach' : null
  return vehiclesByType.get(segment.type) ?? null
}

function pointsMeet(left, a, right, b) {
  return Math.hypot(left[a] - right[b], left[a + 1] - right[b + 1], left[a + 2] - right[b + 2]) <= JOIN_EPSILON
}

// LineSegmentsGeometry stores independent XYZ→XYZ pairs. Clipping a route at
// the terrain boundary can produce more than one visible run inside a drawing.
function appendRuns(runs, positions, segmentIndex, vehicle) {
  let run = null
  for (let offset = 0; offset + 5 < positions.length; offset += 6) {
    const dx = positions[offset + 3] - positions[offset]
    const dy = positions[offset + 4] - positions[offset + 1]
    const dz = positions[offset + 5] - positions[offset + 2]
    const length = Math.hypot(dx, dy, dz)
    if (!Number.isFinite(length) || length === 0) continue
    if (!run || !pointsMeet(positions, run.edges.at(-1).offset + 3, positions, offset)) {
      run = { positions, segmentIndex, vehicle, edges: [], length: 0 }
      runs.push(run)
    }
    run.length += length
    run.edges.push({ offset, endDistance: run.length })
  }
}

export function createVehicleJourney(route, drawings) {
  if (!route || !drawings?.length || sameJourneyCity(route.start, route.end) === true) return null
  const segments = route.segments ?? (route.mode === 'transit' ? [] : [{ type: 'drive' }])
  const runs = []
  for (const { segmentIndex, positions, airportPreview } of drawings) {
    const segment = segments[segmentIndex]
    // The route layer emits this flag only for an explicitly enabled airport preview.
    const source = airportPreview === true && segment?.type === 'flight'
      ? { ...segment, unconfirmed: false, schematic: false } : segment
    const vehicle = vehicleForSegment(source, route)
    if (vehicle && positions?.length) appendRuns(runs, positions, segmentIndex, vehicle)
  }
  if (!runs.length) return null
  const length = runs.reduce((sum, run) => sum + run.length, 0)
  let elapsed = 0
  let previous = null
  for (const run of runs) {
    if (previous && (run.segmentIndex > previous.segmentIndex + 1 ||
      !pointsMeet(previous.positions, previous.edges.at(-1).offset + 3, run.positions, run.edges[0].offset))) {
      elapsed += GAP_SECONDS
    }
    run.startSeconds = elapsed
    elapsed += Math.max(MIN_RUN_SECONDS, TRAVEL_SECONDS * run.length / length)
    run.endSeconds = elapsed
    previous = run
  }
  // A short disappearance at the end also separates the return to the origin.
  const vehicles = [...new Set(runs.map(run => run.vehicle))]
  return { runs, vehicles, durationSeconds: elapsed + GAP_SECONDS }
}

function pointOnRun(run, distance) {
  let low = 0
  let high = run.edges.length - 1
  while (low < high) {
    const mid = (low + high) >>> 1
    if (run.edges[mid].endDistance <= distance) low = mid + 1
    else high = mid
  }
  const { offset, endDistance } = run.edges[low]
  const startDistance = low ? run.edges[low - 1].endDistance : 0
  const fraction = (distance - startDistance) / (endDistance - startDistance)
  const p = run.positions
  const dx = p[offset + 3] - p[offset]
  const dz = p[offset + 5] - p[offset + 2]
  return {
    x: p[offset] + dx * fraction,
    y: p[offset + 1] + (p[offset + 4] - p[offset + 1]) * fraction,
    z: p[offset + 2] + dz * fraction,
    heading: Math.atan2(dx, dz),
  }
}

export function sampleVehicleJourney(journey, elapsedSeconds) {
  if (!journey || !Number.isFinite(elapsedSeconds)) return null
  const time = Math.max(0, elapsedSeconds) % journey.durationSeconds
  const run = journey.runs.find(part => time >= part.startSeconds && time < part.endSeconds)
  if (!run) return null
  const speed = run.length / (run.endSeconds - run.startSeconds)
  const distance = (time - run.startSeconds) * speed
  const point = pointOnRun(run, distance)
  const window = HEADING_WINDOW_SECONDS * speed
  const before = pointOnRun(run, Math.max(0, distance - window))
  const after = pointOnRun(run, Math.min(run.length, distance + window))
  const dx = after.x - before.x
  const dz = after.z - before.z
  if (Math.hypot(dx, dz) > 1e-10) point.heading = Math.atan2(dx, dz)
  return { vehicle: run.vehicle, ...point }
}
