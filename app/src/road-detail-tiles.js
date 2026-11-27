import { VectorTile } from '@mapbox/vector-tile'
import { PbfReader } from 'pbf'

// OpenFreeMap documents the latest XYZ alias and the backup_planet path used in its own styles.
const SOURCE = 'https://tiles.openfreemap.org/backup_planet/latest'
const MIN_ZOOM = 8
const MAX_ZOOM = 14
const MAX_TILES = 24
const MAX_PARALLEL = 4
const CACHE_TILES = 32
const RETRY_MS = 60_000

function mercatorY(lat, count) {
  return (1 - Math.asinh(Math.tan(Math.max(-85.05112878, Math.min(85.05112878, lat)) * Math.PI / 180)) / Math.PI) * count / 2
}

export function roadTileCover({ bounds, zoom, center }) {
  if (!Number.isFinite(zoom) || zoom < MIN_ZOOM || !bounds?.every(Number.isFinite)) return []
  const [west, south, east, north] = bounds
  if (west >= east || south >= north) return []
  for (let z = Math.min(MAX_ZOOM, Math.floor(zoom)); z >= MIN_ZOOM; z--) {
    const n = 2 ** z
    const x = lon => (lon + 180) / 360 * n
    const index = value => Math.max(0, Math.min(n - 1, value))
    const x1 = index(Math.floor(x(west))), x2 = index(Math.ceil(x(east)) - 1)
    const y1 = index(Math.floor(mercatorY(north, n))), y2 = index(Math.ceil(mercatorY(south, n)) - 1)
    if ((x2 - x1 + 1) * (y2 - y1 + 1) > MAX_TILES) continue
    const cx = x(center?.[0] ?? (west + east) / 2)
    const cy = mercatorY(center?.[1] ?? (south + north) / 2, n)
    const cover = []
    for (let row = y1; row <= y2; row++) {
      for (let col = x1; col <= x2; col++) {
        cover.push({ z, x: col, y: row, key: z + '/' + col + '/' + row,
          distance: (col + 0.5 - cx) ** 2 + (row + 0.5 - cy) ** 2 })
      }
    }
    return cover.sort((a, b) => a.distance - b.distance)
  }
  return []
}

function kindFor(className, zoom) {
  switch (className) {
    case 'motorway': return 'expressway'
    case 'trunk':
    case 'primary': return 'arterial'
    case 'secondary': return 'secondary'
    case 'tertiary': return zoom >= 10 ? 'secondary' : null
    case 'minor': return zoom >= 12 ? 'local' : null
    case 'service': return zoom >= 14 ? 'local' : null
    default: return null
  }
}

// Clip the MVT drawing buffer off each edge, preserving disconnected runs through the tile.
function clippedRuns(line, extent) {
  const runs = []
  let run = []
  for (let i = 1; i < line.length; i++) {
    const { x, y } = line[i - 1]
    const b = line[i], dx = b.x - x, dy = b.y - y
    let t0 = 0, t1 = 1
    if (Math.min(x, b.x) < 0 || Math.max(x, b.x) > extent) {
      if (!dx || (x < 0 && b.x < 0) || (x > extent && b.x > extent)) continue
      const tWest = -x / dx, tEast = (extent - x) / dx
      t0 = Math.max(0, Math.min(tWest, tEast))
      t1 = Math.min(1, Math.max(tWest, tEast))
    }
    if (Math.min(y, b.y) < 0 || Math.max(y, b.y) > extent) {
      if (!dy || (y < 0 && b.y < 0) || (y > extent && b.y > extent)) continue
      const tNorth = -y / dy, tSouth = (extent - y) / dy
      t0 = Math.max(t0, Math.min(tNorth, tSouth))
      t1 = Math.min(t1, Math.max(tNorth, tSouth))
    }
    if (t0 >= t1 || (!dx && !dy)) continue
    const ax = t0 ? x + t0 * dx : x, ay = t0 ? y + t0 * dy : y
    const last = run.at(-1)
    if (!last || Math.abs(last[0] - ax) > 1e-8 || Math.abs(last[1] - ay) > 1e-8) {
      run = [[ax, ay]]
      runs.push(run)
    }
    run.push(t1 === 1 ? [b.x, b.y] : [x + t1 * dx, y + t1 * dy])
  }
  return runs
}

function labelPosition(run) {
  const lengths = []
  let total = 0
  for (let i = 1; i < run.length; i++) {
    const length = Math.hypot(run[i][0] - run[i - 1][0], run[i][1] - run[i - 1][1])
    total += length
    lengths.push(length)
  }
  let rest = total / 2
  for (let i = 0; i < lengths.length; i++) {
    if (rest <= lengths[i]) {
      const ratio = rest / lengths[i]
      return { length: total, point: run[i].map((v, axis) => v + (run[i + 1][axis] - v) * ratio) }
    }
    rest -= lengths[i]
  }
  return null
}

function shortRoadName(properties) {
  if (properties.subclass === 'junction') return null
  for (const field of ['name:zh-Hans', 'name:zh', 'name']) {
    const value = typeof properties[field] === 'string' && properties[field].trim()
    if (value && /^[\p{Script=Han}A-Za-z0-9·・ -]{2,14}$/u.test(value) && /\p{Script=Han}/u.test(value) &&
      !/^(?:(?:未命名|无名|無名)(?:道路|公路|路)?|道路施工|施工道路|出入口)$/u.test(value)) return value
  }
  return null
}

export function decodeRoadTile(buffer, { x, y, z, key = z + '/' + x + '/' + y }) {
  const { layers } = new VectorTile(new PbfReader(buffer))
  const roads = [], numbers = new Map(), names = new Map()
  const n = 2 ** z
  function lngLat([px, py], extent) {
    const lon = (x + px / extent) / n * 360 - 180
    const lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * (y + py / extent) / n))) * 180 / Math.PI
    return [lon, lat]
  }

  // The public PBF bundles all layers. Only materialize road geometry and its labels.
  for (const id of ['transportation', 'transportation_name']) {
    const layer = layers[id]
    if (!layer) continue
    for (let i = 0; i < layer.length; i++) {
      const feature = layer.feature(i)
      const kind = kindFor(feature.properties.class, z)
      if (feature.type !== 2 || !kind) continue
      const label = id === 'transportation_name'
      const ref = label && String(feature.properties.ref ?? '').toUpperCase().match(/(?:^|[\s;,；、/])([GS]\d{1,4}[A-Z]?)(?=$|[\s;,；、/])/u)?.[1]
      const text = ref || (label && z >= 12 && !feature.properties.ref && shortRoadName(feature.properties))
      if (label && !text) continue
      for (const line of feature.loadGeometry()) {
        for (const run of clippedRuns(line, layer.extent)) {
          if (!label) {
            roads.push({ kind, coordinates: run.map(point => lngLat(point, layer.extent)) })
            continue
          }
          const mid = labelPosition(run)
          const candidates = ref ? numbers : names
          if (!mid || mid.length <= (candidates.get(text)?.length ?? 0)) continue
          const [lon, lat] = lngLat(mid.point, layer.extent)
          candidates.set(text, { text, lon, lat, length: mid.length, roadKind: kind })
        }
      }
    }
  }
  const priority = { expressway: 3, arterial: 2, secondary: 1, local: 0 }
  const rank = (a, b) => priority[b.roadKind] - priority[a.roadKind] || b.length - a.length
  const labels = [...numbers.values()].sort(rank).slice(0, 8).map(({ text, lon, lat }) => ({ text, lon, lat }))
  for (const { text, lon, lat } of [...names.values()].sort(rank).slice(0, 8)) {
    labels.push({ text, lon, lat, kind: 'name' })
  }
  return { key, x, y, z, roads, labels }
}

export function createRoadDetailTiles({ onTile, onRemove, onStatus, fetcher = fetch }) {
  const cache = new Map(), shown = new Set(), jobs = new Map(), failed = new Map()
  let wanted = new Map(), timer = 0, disposed = false

  function report() {
    onStatus({ complete: wanted.size > 0 && shown.size === wanted.size, loaded: shown.size,
      expected: wanted.size, failed: failed.size > 0 })
  }

  function schedule(delay) {
    clearTimeout(timer)
    timer = setTimeout(pump, delay)
  }

  function show(tile) {
    cache.delete(tile.key)
    cache.set(tile.key, tile)
    if (cache.size > CACHE_TILES) cache.delete(cache.keys().next().value)
    shown.add(tile.key)
    onTile(tile)
  }

  async function request(coords) {
    const { key } = coords
    const controller = new AbortController()
    jobs.set(key, controller)
    const deadline = setTimeout(() => controller.abort(), 10_000)
    try {
      const response = await fetcher(SOURCE + '/' + key + '.pbf', { signal: controller.signal, credentials: 'omit' })
      if (!response.ok) throw new Error('Road tile HTTP ' + response.status)
      const buffer = await response.arrayBuffer()
      if (jobs.get(key) === controller) show(decodeRoadTile(buffer, coords))
    } catch {
      if (jobs.get(key) === controller) failed.set(key, Date.now() + RETRY_MS)
    } finally {
      clearTimeout(deadline)
      if (jobs.get(key) === controller) {
        jobs.delete(key)
        report()
        pump()
      }
    }
  }

  function pump() {
    if (disposed) return
    clearTimeout(timer)
    let retry = Infinity
    for (const tile of wanted.values()) {
      if (jobs.size >= MAX_PARALLEL) break
      if (shown.has(tile.key) || jobs.has(tile.key)) continue
      const delay = (failed.get(tile.key) ?? 0) - Date.now()
      if (delay > 0) {
        retry = Math.min(retry, delay)
        continue
      }
      failed.delete(tile.key)
      request(tile)
    }
    if (Number.isFinite(retry)) schedule(retry)
  }

  function setWanted(tiles) {
    const next = new Map(tiles.map(tile => [tile.key, tile]))
    if (next.size === wanted.size && [...next.keys()].every(key => wanted.has(key))) return
    wanted = next
    clearTimeout(timer)
    for (const [key, controller] of jobs) if (!wanted.has(key)) {
      jobs.delete(key)
      controller.abort()
    }
    for (const key of failed.keys()) if (!wanted.has(key)) failed.delete(key)
    for (const key of shown) if (!wanted.has(key)) {
      shown.delete(key)
      onRemove(key)
    }
    for (const key of wanted.keys()) if (!shown.has(key) && cache.has(key)) show(cache.get(key))
    report()
    if (wanted.size > shown.size) schedule(160)
  }
  return {
    update(view) { if (!disposed) setWanted(roadTileCover(view)) },
    clear() { if (!disposed) setWanted([]) },
    dispose() {
      setWanted([])
      cache.clear()
      disposed = true
    },
  }
}
