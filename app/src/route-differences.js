// Compare the paths that are actually drawn. The aggregate itinerary can contain
// joins across gaps, so keep each walk, bus or rail polyline independent.
function readTracks(route) {
  const segments = route?.segments ?? (route?.mode === 'driving' ? [{ type: 'drive', geometry: route.geometry }] : [])
  const tracks = segments.filter(s => !s.schematic && !s.unconfirmed && s.geometry?.length >= 2 &&
    s.geometry.every(p => Array.isArray(p) && Number.isFinite(p[0]) && Number.isFinite(p[1])))
  return { tracks, complete: tracks.length === segments.length }
}

function bounds() {
  return { west: Infinity, east: -Infinity, south: Infinity, north: -Infinity }
}

function extend(box, x, y) {
  box.west = Math.min(box.west, x)
  box.east = Math.max(box.east, x)
  box.south = Math.min(box.south, y)
  box.north = Math.max(box.north, y)
}

function diameter(box) {
  return Math.hypot(box.east - box.west, box.north - box.south)
}

function indexTracks(tracks, lonScale, latScale, cellSize) {
  const grid = new Map()
  const edges = []
  let length = 0
  for (const { type, geometry } of tracks) {
    for (let i = 1; i < geometry.length; i++) {
      const [a, b] = [geometry[i - 1], geometry[i]]
      const x = a[0] * lonScale
      const y = a[1] * latScale
      const dx = (b[0] - a[0]) * lonScale
      const dy = (b[1] - a[1]) * latScale
      const distance = Math.hypot(dx, dy)
      if (!distance) continue
      length += distance
      // Subdivide long edges along the line so a long diagonal never fills a
      // rectangular grid of empty cells. The original corners remain exact.
      const n = Math.ceil(distance / cellSize)
      for (let j = 0; j < n; j++) {
        const x1 = x + dx * j / n
        const y1 = y + dy * j / n
        const x2 = x + dx * (j + 1) / n
        const y2 = y + dy * (j + 1) / n
        const edge = { type, x1, y1, x2, y2, length: distance / n }
        edges.push(edge)
        for (let col = Math.floor(Math.min(x1, x2) / cellSize); col <= Math.floor(Math.max(x1, x2) / cellSize); col++) {
          for (let row = Math.floor(Math.min(y1, y2) / cellSize); row <= Math.floor(Math.max(y1, y2) / cellSize); row++) {
            const key = col + ',' + row
            if (!grid.has(key)) grid.set(key, [])
            grid.get(key).push(edge)
          }
        }
      }
    }
  }
  return { grid, edges, length }
}

function nearTrack(x, y, type, grid, cellSize, tolerance) {
  for (let col = Math.floor((x - tolerance) / cellSize); col <= Math.floor((x + tolerance) / cellSize); col++) {
    for (let row = Math.floor((y - tolerance) / cellSize); row <= Math.floor((y + tolerance) / cellSize); row++) {
      for (const edge of grid.get(col + ',' + row) || []) {
        if (edge.type !== type) continue
        const dx = edge.x2 - edge.x1
        const dy = edge.y2 - edge.y1
        const t = Math.max(0, Math.min(1, ((x - edge.x1) * dx + (y - edge.y1) * dy) / edge.length ** 2))
        if ((x - edge.x1 - t * dx) ** 2 + (y - edge.y1 - t * dy) ** 2 <= tolerance ** 2) return true
      }
    }
  }
  return false
}

function measureDifference(path, other, box, cellSize, tolerance) {
  let different = 0
  for (const { type, x1, y1, x2, y2, length } of path.edges) {
    if (nearTrack(x1, y1, type, other.grid, cellSize, tolerance) &&
        nearTrack(x2, y2, type, other.grid, cellSize, tolerance) &&
        nearTrack((x1 + x2) / 2, (y1 + y2) / 2, type, other.grid, cellSize, tolerance)) continue
    different += length
    extend(box, x1, y1)
    extend(box, x2, y2)
  }
  return different
}

export function compareRouteGeometry(previous, selected) {
  const overview = { kind: 'overview', coordinates: [] }
  const a = readTracks(previous)
  const b = readTracks(selected)
  if (!a.tracks.length || !b.tracks.length) return overview

  const extent = bounds()
  for (const { geometry } of [...a.tracks, ...b.tracks]) {
    for (const [lon, lat] of geometry) extend(extent, lon, lat)
  }
  const lonScale = 111320 * Math.cos((extent.north + extent.south) * Math.PI / 360)
  const latScale = 110574
  const span = Math.hypot((extent.east - extent.west) * lonScale, (extent.north - extent.south) * latScale)
  if (!span) return overview
  // Match sub-street-scale rounding in town and nearby parallel rails on an intercity trip.
  const tolerance = Math.max(5, Math.min(30, span / 30000))
  const cellSize = Math.max(tolerance * 3, span / 6000)
  const left = indexTracks(a.tracks, lonScale, latScale, cellSize)
  const right = indexTracks(b.tracks, lonScale, latScale, cellSize)
  if (!left.length || !right.length) return overview
  const changed = bounds()
  const leftDiff = measureDifference(left, right, changed, cellSize, tolerance)
  const rightDiff = measureDifference(right, left, changed, cellSize, tolerance)
  if (!leftDiff && !rightDiff) {
    return a.complete && b.complete ? { kind: 'same', coordinates: [] } : overview
  }
  // Zoom into one compact divergence when most of both journeys shares the same path.
  // Widely separated changes or substantially different corridors belong in the full view.
  if (leftDiff > left.length * 0.45 || rightDiff > right.length * 0.45 || diameter(changed) > span * 0.56) return overview
  const coordinates = []
  for (const x of [changed.west, changed.east]) {
    for (const y of [changed.south, changed.north]) coordinates.push([x / lonScale, y / latScale])
  }
  return { kind: 'local', coordinates }
}
