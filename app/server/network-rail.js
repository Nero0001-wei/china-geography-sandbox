// BRouter's rail profile can also use subways and trams. Inspect the actual way tags
// and match the train leg's own distance before displaying a railway-network reference.
const pools = new WeakMap()
const maxJobs = 4
const maxCached = 20

function validPoint(point) {
  return Array.isArray(point) && Number.isFinite(point[0]) && Number.isFinite(point[1]) &&
    point[0] >= 70 && point[0] <= 140 && point[1] >= 3 && point[1] <= 60
}

function meters(a, b) {
  const dx = (a[0] - b[0]) * 111320 * Math.cos((a[1] + b[1]) * Math.PI / 360)
  return Math.hypot(dx, (a[1] - b[1]) * 110574)
}

function stationPins(leg) {
  if (leg.type !== 'rail' || leg.unconfirmed || leg.geometry?.length >= 2 ||
      !(Number.isFinite(leg.distanceMeters) && leg.distanceMeters > 0)) return null
  const stops = [leg.from, ...(leg.viaStops || []), leg.to]
  if (stops.length > 32 || !stops.every(stop => stop?.name && validPoint(stop.location))) return null
  return stops.map(stop => stop.location)
}

function readTrack(response, pins) {
  const line = response?.features?.[0]
  const raw = line?.geometry?.coordinates
  const props = line?.properties
  const messages = props?.messages
  const tags = messages?.[0]?.indexOf('WayTags') ?? -1
  if (line?.geometry?.type !== 'LineString' || !Array.isArray(raw) || raw.length < 3 || raw.length > 50000 ||
      !raw.every(validPoint) || !Array.isArray(messages) || messages.length < 2 || tags < 0 ||
      !messages.slice(1).every(row => typeof row?.[tags] === 'string' && /(?:^|\s)railway=rail(?:\s|$)/u.test(row[tags]))) return null
  const geometry = raw.map(([lon, lat]) => [lon, lat])
  if (meters(geometry[0], pins[0]) > 750 || meters(geometry.at(-1), pins.at(-1)) > 750) return null

  let cursor = 0
  for (const station of pins.slice(1, -1)) {
    while (cursor < geometry.length && meters(geometry[cursor], station) > 750) cursor++
    if (cursor === geometry.length) return null
  }
  const length = geometry.slice(1).reduce((sum, point, i) => sum + meters(geometry[i], point), 0)
  const reported = Number(props['track-length'])
  if (!(reported > 0) || Math.abs(reported - length) > Math.max(100, reported * 0.02)) return null
  return { geometry, length }
}

async function requestTrack(pins, key, fetcher, timeout) {
  const url = new URL('https://brouter.de/brouter')
  url.search = new URLSearchParams({ lonlats: key, profile: 'rail', alternativeidx: '0', format: 'geojson' })
  try {
    const response = await fetcher(url, { signal: AbortSignal.timeout(timeout) })
    return response.ok ? readTrack(await response.json(), pins) : null
  } catch {
    return null
  }
}

function cachedTrack(pool, pins, fetcher, deadline) {
  const key = pins.map(p => p.map(v => v.toFixed(6)).join(',')).join('|')
  const cached = pool.cache.get(key)
  if (cached && cached.expires > Date.now()) return cached.track
  if (pool.pending.has(key)) return pool.pending.get(key)
  if (pool.pending.size >= maxJobs) return null
  // The public service gives short requests priority. Share in-flight requests and
  // send one at a time, even when several itinerary alternatives arrive together.
  const job = pool.tail.then(async () => {
    const remaining = deadline - Date.now()
    if (remaining <= 0) return null
    const track = await requestTrack(pins, key, fetcher, Math.min(5500, remaining))
    if (pool.cache.size >= maxCached) pool.cache.delete(pool.cache.keys().next().value)
    pool.cache.set(key, { track, expires: Date.now() + (track ? 30 * 60000 : 20000) })
    return track
  }).finally(() => pool.pending.delete(key))
  pool.pending.set(key, job)
  pool.tail = job.then(() => {}, () => {})
  return job
}

export async function enrichNetworkRailRoutes(routes, { fetcher = fetch } = {}) {
  if (!pools.has(fetcher)) pools.set(fetcher, { cache: new Map(), pending: new Map(), tail: Promise.resolve() })
  const pool = pools.get(fetcher)
  const deadline = Date.now() + 8500
  let attempts = 0
  const touched = new Set()
  for (const route of routes) {
    for (const leg of route.segments || []) {
      const pins = stationPins(leg)
      if (!pins || Date.now() >= deadline || attempts >= 5) continue
      attempts++
      const track = await cachedTrack(pool, pins, fetcher, deadline)
      if (!track || Math.abs(track.length - leg.distanceMeters) > Math.min(9000, leg.distanceMeters * 0.04)) continue
      leg.geometry = track.geometry
      leg.geometrySource = 'rail-network'
      touched.add(route)
    }
  }
  for (const route of touched) {
    route.geometry = [route.start?.location, ...route.segments.flatMap(s => [s.from?.location, ...s.geometry, s.to?.location]), route.end?.location]
      .filter(validPoint).filter((p, i, points) => i === 0 || p[0] !== points[i - 1][0] || p[1] !== points[i - 1][1])
  }
  return routes
}
