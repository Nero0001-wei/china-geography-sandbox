import * as THREE from 'three'
import { METERS_TO_HEIGHT, SCENE_UNIT_METERS } from './terrain-data.js'

const EPSILON = 1e-8

export function projectCoordinate(coordinate, terrain) {
  if (!Array.isArray(coordinate) || coordinate.length < 2) return null
  const [lon, lat] = coordinate
  if (!Number.isFinite(lon) || !Number.isFinite(lat) || Math.abs(lon) > 180 || Math.abs(lat) > 90) return null
  const point = terrain.geoToWorld(lon, lat)
  return point.every(Number.isFinite) ? point : null
}

function evenlySpacedCuts(cuts, value, delta, from, to) {
  if (Math.abs(delta) < EPSILON) return
  const first = Math.min(value + from * delta, value + to * delta)
  const last = Math.max(value + from * delta, value + to * delta)
  for (let integer = Math.ceil(first); integer < last; integer++) {
    const t = (integer - value) / delta
    if (t > from + EPSILON && t < to - EPSILON) cuts.push(t)
  }
}

function clipToGrid(column, row, columnStep, rowStep, width, height) {
  let from = 0
  let to = 1
  for (const [origin, delta, limit] of [[column, columnStep, width - 1], [row, rowStep, height - 1]]) {
    if (Math.abs(delta) < EPSILON) {
      if (origin < 0 || origin > limit) return null
      continue
    }
    const zero = -origin / delta
    const edge = (limit - origin) / delta
    from = Math.max(from, Math.min(zero, edge))
    to = Math.min(to, Math.max(zero, edge))
  }
  return from < to - EPSILON ? [from, to] : null
}

export function segmentDistanceSquared(point, start, end) {
  const dx = end[0] - start[0]
  const dz = end[1] - start[1]
  const length = dx * dx + dz * dz
  const offsetX = point[0] - start[0]
  const offsetZ = point[1] - start[1]
  const t = length ? THREE.MathUtils.clamp((offsetX * dx + offsetZ * dz) / length, 0, 1) : 0
  return (offsetX - dx * t) ** 2 + (offsetZ - dz * t) ** 2
}

function simplifyPath(points, transit) {
  // The same geometry is reused from the national view down to individual roads.
  const tolerance = (transit ? 5 : 8) / SCENE_UNIT_METERS
  const limit = tolerance ** 2
  const spans = [[0, points.length - 1]]
  const kept = new Set([0, points.length - 1])
  while (spans.length) {
    const [start, end] = spans.pop()
    let highest = limit
    let split = -1
    for (let index = start + 1; index < end; index++) {
      const distance = segmentDistanceSquared(points[index], points[start], points[end])
      if (distance > highest) {
        highest = distance
        split = index
      }
    }
    if (split >= 0) {
      kept.add(split)
      spans.push([start, split], [split, end])
    }
  }
  return points.filter((_, index) => kept.has(index))
}

export function createSurfaceSampler(terrain) {
  const { width, height, bounds } = terrain.metadata
  const edgeX = (bounds.maxX - bounds.minX) / (2 * SCENE_UNIT_METERS)
  const edgeZ = (bounds.maxY - bounds.minY) / (2 * SCENE_UNIT_METERS)
  return (x, z) => {
    const [column, row] = terrain.gridPoint(x, z)
    if (column < -EPSILON || row < -EPSILON || column > width - 1 + EPSILON || row > height - 1 + EPSILON) return null
    // Clamp only the floating-point overshoot at the edge to match the mesh exactly.
    x = THREE.MathUtils.clamp(x, -edgeX, edgeX)
    z = THREE.MathUtils.clamp(z, -edgeZ, edgeZ)
    const elevation = terrain.sample(x, z)?.elevation ?? 0
    return new THREE.Vector3(x, elevation * METERS_TO_HEIGHT, z)
  }
}

export function drapePolyline(terrain, geometry, surfacePoint, transit, subdivisions = 1) {
  if (!Array.isArray(geometry) || geometry.length < 2) return []

  const projected = []
  for (const coordinate of geometry) {
    const point = projectCoordinate(coordinate, terrain)
    if (!point) return []
    const previous = projected.at(-1)
    if (!previous || Math.hypot(point[0] - previous[0], point[1] - previous[1]) > EPSILON) projected.push(point)
  }
  if (projected.length < 2) return []

  const { width, height } = terrain.metadata
  const path = simplifyPath(projected, transit)
  const positions = []

  for (let index = 1; index < path.length; index++) {
    const [x, z] = path[index - 1]
    const [nextX, nextZ] = path[index]
    const [column, row] = terrain.gridPoint(x, z)
    const [nextColumn, nextRow] = terrain.gridPoint(nextX, nextZ)
    const columnStep = nextColumn - column
    const rowStep = nextRow - row
    const visible = clipToGrid(column, row, columnStep, rowStep, width, height)
    if (!visible) continue

    const [from, to] = visible
    const cuts = [from, to]
    for (let i = 1; i < subdivisions; i++) cuts.push(from + (to - from) * i / subdivisions)
    // Split at column, row, and diagonal edges of the actual elevation triangles.
    // Between two crossings the surface height is linear, including on steep ridges.
    evenlySpacedCuts(cuts, column, columnStep, from, to)
    evenlySpacedCuts(cuts, row, rowStep, from, to)
    evenlySpacedCuts(cuts, column + row, columnStep + rowStep, from, to)
    cuts.sort((a, b) => a - b)

    let previous = null
    let previousCut = -1
    for (const t of cuts) {
      if (t - previousCut <= EPSILON) continue
      const point = surfacePoint(THREE.MathUtils.lerp(x, nextX, t), THREE.MathUtils.lerp(z, nextZ, t))
      if (previous && point) positions.push(previous.x, previous.y, previous.z, point.x, point.y, point.z)
      previous = point
      previousCut = t
    }
  }
  return positions
}
