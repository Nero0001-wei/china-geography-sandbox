import * as THREE from 'three'
import { LineMaterial } from 'three/addons/lines/LineMaterial.js'
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js'
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js'
import { SCENE_UNIT_METERS } from './terrain-data.js'
import { createSurfaceSampler, drapePolyline, projectCoordinate, segmentDistanceSquared } from './terrain-polyline.js'
import { sameJourneyCity } from './vehicle-journey.js'
import { createRouteArrows } from './route-arrows.js'

const CLEARANCE = 0.026
const COMPACT_CLEARANCE = 0.0015
const ROAD_DETAIL_CLEARANCE = 0.0006
const EPSILON = 1e-8
const COMPACT_ROUTE_SPAN = 95_000 / SCENE_UNIT_METERS
const BADGE_SIZE = 27
const OVERVIEW_SPAN = 140
const ROUTE_WIDTH = 4
const FLIGHT_PREVIEW_WIDTH = 2.25
const BADGE_COLORS = ['#087565', '#b84638']
const LABEL_HEIGHT = 25

export const ROUTE_COLORS = {
  walk: '#178676',
  bus: '#206d9f',
  coach: '#206d9f',
  ferry: '#077c96',
  metro: '#8840ae',
  rail: '#c14833',
  flight: '#375ba8',
  drive: '#1768da',
  taxi: '#ad6c12',
  transfer: '#626976',
}

export function hasSegmentTrack(segment) {
  return Boolean(segment && !segment.schematic && !segment.unconfirmed &&
    Array.isArray(segment.geometry) && segment.geometry.length >= 2)
}

export function canPreviewFlight(segment, route) {
  if (segment?.type !== 'flight' || segment.unavailable || segment.localTransfer || hasSegmentTrack(segment) ||
    sameJourneyCity(segment.from, segment.to) === true || sameJourneyCity(route?.start, route?.end) === true) return false
  const a = segment.from?.location
  const b = segment.to?.location
  const valid = p => Array.isArray(p) && Number.isFinite(p[0]) && Number.isFinite(p[1]) &&
    Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 90
  return valid(a) && valid(b) && (a[0] !== b[0] || a[1] !== b[1])
}

function airportPreviewPositions(terrain, segment, surfacePoint) {
  const endpoints = [segment.from.location, segment.to.location]
  const [a, b] = endpoints.map(coordinate => {
    const projected = projectCoordinate(coordinate, terrain)
    return projected && surfacePoint(...projected)
  })
  if (!a || !b) return []
  const dx = b.x - a.x
  const dz = b.z - a.z
  const distance = Math.hypot(dx, dz)
  if (distance < EPSILON) return []
  const lift = Math.min(distance * 0.14, 3.2)
  return drapePolyline(terrain, endpoints, (x, z) => {
    const point = surfacePoint(x, z)
    if (!point) return null
    const t = THREE.MathUtils.clamp(((x - a.x) * dx + (z - a.z) * dz) / distance ** 2, 0, 1)
    const arc = THREE.MathUtils.lerp(a.y, b.y, t) + 4 * lift * t * (1 - t)
    point.y = Math.max(point.y, arc)
    return point
  }, true, 32)
}

export function buildTerrainRoute(terrain, route, localView = false, previewFlights = false) {
  if (!route) return null
  // A transit route's aggregate geometry can include off-track stops from different legs.
  const segmented = Array.isArray(route.segments) || route.mode === 'transit'
  const geometry = Array.isArray(route.geometry) ? route.geometry : []
  const segments = segmented ? (route.segments || []) : [{ type: 'drive', geometry }]
  const surfacePoint = createSurfaceSampler(terrain)
  const drawings = segments.flatMap((segment, segmentIndex) => {
    const airportPreview = previewFlights && canPreviewFlight(segment, route)
    if (!airportPreview && !hasSegmentTrack(segment)) return []
    const positions = airportPreview ? airportPreviewPositions(terrain, segment, surfacePoint)
      : drapePolyline(terrain, segment.geometry, surfacePoint, segment.type !== 'drive')
    return positions.length ? [{ positions, type: segment.type, segmentIndex, airportPreview }] : []
  })
  const start = route.start?.mapAnchor ?? route.start?.location ?? segments[0]?.from?.location ?? geometry[0] ?? segments[0]?.geometry?.[0]
  const end = route.end?.mapAnchor ?? route.end?.location ?? segments.at(-1)?.to?.location ?? geometry.at(-1) ?? segments.at(-1)?.geometry?.at?.(-1)
  const anchors = [start, end].map((coordinate) => {
    const location = projectCoordinate(coordinate, terrain)
    return location && surfacePoint(...location)
  })
  if (!drawings.length && (!segmented || !anchors.every(Boolean))) return null
  const extent = new THREE.Box2()
  const point = new THREE.Vector2()
  for (const { positions } of drawings) {
    for (let index = 0; index < positions.length; index += 3) extent.expandByPoint(point.set(positions[index], positions[index + 2]))
  }
  for (const anchor of anchors) if (anchor) extent.expandByPoint(point.set(anchor.x, anchor.z))
  const compact = extent.getSize(point).length() <= COMPACT_ROUTE_SPAN
  const clearance = compact || localView ? COMPACT_CLEARANCE : CLEARANCE
  for (const { positions } of drawings) {
    for (let index = 1; index < positions.length; index += 3) positions[index] += clearance
  }
  for (const anchor of anchors) if (anchor) anchor.y += clearance
  const positions = drawings.flatMap((segment) => segment.positions)
  return { positions, drawings, anchors, compact, clearance }
}

// Coordinates from both alternatives bound the same comparison view on either selection.
export function buildRouteFocus(terrain, coordinates) {
  if (!coordinates?.length) return null
  const surfacePoint = createSurfaceSampler(terrain)
  const points = []
  const extent = new THREE.Box2()
  const horizontal = new THREE.Vector2()
  for (const coordinate of coordinates) {
    const projected = projectCoordinate(coordinate, terrain)
    const point = projected && surfacePoint(...projected)
    if (!point) continue
    points.push(point.x, point.y + COMPACT_CLEARANCE, point.z)
    extent.expandByPoint(horizontal.set(point.x, point.z))
  }
  if (!points.length) return null
  return { positions: points, anchors: [], compact: extent.getSize(horizontal).length() <= COMPACT_ROUTE_SPAN }
}

export function routeZoomLimit(track, camera, width, allowDetail = false) {
  const narrow = THREE.MathUtils.clamp((800 - width) / 380, 0, 1)
  const overview = THREE.MathUtils.lerp(14, 20, narrow)
  if (!track.compact && !allowDetail) return overview
  // On city trips the line is detailed, while the backdrop remains the national DEM.
  const minimumSpan = 12_000 / SCENE_UNIT_METERS
  const cameraSpan = Math.min(camera.right - camera.left, camera.top - camera.bottom)
  return Math.max(overview, cameraSpan / minimumSpan)
}

export function frameTerrainRoute(track, camera, direction, width, height, minZoom, maxZoom) {
  const right = new THREE.Vector3().crossVectors(camera.up, direction).normalize()
  const up = new THREE.Vector3().crossVectors(direction, right)
  const extent = new THREE.Box3()
  const world = new THREE.Vector3()
  const local = new THREE.Vector3()
  function add(point) {
    extent.expandByPoint(local.set(point.dot(right), point.dot(up), point.dot(direction)))
  }
  for (let index = 0; index < track.positions.length; index += 3) add(world.fromArray(track.positions, index))
  for (const anchor of track.anchors) if (anchor) add(anchor)

  const center = extent.getCenter(new THREE.Vector3())
  const size = extent.getSize(new THREE.Vector3())
  const target = right.clone().multiplyScalar(center.x).addScaledVector(up, center.y).addScaledVector(direction, center.z)
  const viewWidth = camera.right - camera.left
  const viewHeight = camera.top - camera.bottom
  const narrow = width <= 560
  const short = narrow && height < 450
  const shortLocal = short && track.compact
  const topInset = shortLocal ? 139 : narrow ? 132 : 65
  const bottomInset = shortLocal ? 46 : short ? 67 : narrow ? 76 : 65
  const useWidth = viewWidth * Math.max(0.56, 1 - 126 / width)
  const useHeight = viewHeight * Math.min(0.54, Math.max(shortLocal ? 0.27 : 0.4, 1 - (topInset + bottomInset) / height))
  const zoom = THREE.MathUtils.clamp(Math.min(useWidth / size.x, useHeight / size.y), minZoom, maxZoom)
  target.addScaledVector(up, (topInset - bottomInset) / (2 * height) * viewHeight / zoom)

  if (short) {
    const unitsPerPixel = viewWidth / (width * zoom)
    const legendRight = 200
    const legendTop = height - 76
    let bias = 0
    const centerHeight = target.dot(up)
    for (const anchor of track.anchors) {
      if (!anchor) continue
      const x = width / 2 + (anchor.dot(right) - center.x) / unitsPerPixel
      const y = height / 2 - (anchor.dot(up) - centerHeight) / unitsPerPixel
      if (y + BADGE_SIZE / 2 >= legendTop) bias = Math.max(bias, legendRight + BADGE_SIZE / 2 + 4 - x)
    }
    if (shortLocal) {
      for (let index = 0; index < track.positions.length; index += 3) {
        world.fromArray(track.positions, index)
        const y = height / 2 - (world.dot(up) - centerHeight) / unitsPerPixel
        if (y + 4 < legendTop) continue
        const x = width / 2 + (world.dot(right) - center.x) / unitsPerPixel
        bias = Math.max(bias, legendRight + 6 - x)
      }
    }
    // Allow marker text to flip left near the right edge while the dots stay in view.
    const room = Math.max(0, width / 2 - size.x / (2 * unitsPerPixel) - 22)
    target.addScaledVector(right, -Math.min(bias, room) * unitsPerPixel)
  }
  return { target, zoom }
}

function overlaySprite(canvas) {
  const map = new THREE.CanvasTexture(canvas)
  map.colorSpace = THREE.SRGBColorSpace
  const material = new THREE.SpriteMaterial({ map, depthTest: false, depthWrite: false })
  const sprite = new THREE.Sprite(material)
  sprite.renderOrder = 9
  return sprite
}

function makeBadge(text, color) {
  const canvas = document.createElement('canvas')
  canvas.width = 96
  canvas.height = 96
  const ctx = canvas.getContext('2d')
  ctx.beginPath()
  ctx.arc(48, 48, 39, 0, Math.PI * 2)
  ctx.shadowColor = 'rgba(36, 40, 30, 0.40)'
  ctx.shadowBlur = 8
  ctx.shadowOffsetY = 3
  ctx.fillStyle = '#fffaf0'
  ctx.fill()
  ctx.shadowColor = 'transparent'
  ctx.beginPath()
  ctx.arc(48, 48, 32, 0, Math.PI * 2)
  ctx.fillStyle = color
  ctx.fill()
  ctx.fillStyle = '#ffffff'
  ctx.font = 'bold 38px system-ui, sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, 48, 51)
  return overlaySprite(canvas)
}

function makeCityLabel(cityLabel, color) {
  if (typeof cityLabel !== 'string' || !cityLabel.trim()) return null
  const text = Array.from(cityLabel.trim()).slice(0, 12).join('')
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const supersampling = 3
  const font = `bold ${13 * supersampling}px system-ui, sans-serif`
  ctx.font = font
  canvas.width = Math.ceil(ctx.measureText(text).width) + 20 * supersampling
  canvas.height = LABEL_HEIGHT * supersampling

  ctx.beginPath()
  ctx.roundRect(4, 5, canvas.width - 8, canvas.height - 11, 18)
  ctx.shadowColor = 'rgba(36, 40, 30, 0.34)'
  ctx.shadowBlur = 5
  ctx.shadowOffsetY = 2
  ctx.fillStyle = '#fffaf0'
  ctx.fill()
  ctx.shadowColor = 'transparent'
  ctx.font = font
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = color
  ctx.fillText(text, canvas.width / 2, canvas.height / 2 + supersampling)

  return { sprite: overlaySprite(canvas), width: canvas.width / supersampling, text }
}

function disposeSprite(sprite) {
  sprite.material.map.dispose()
  sprite.material.dispose()
  sprite.removeFromParent()
}

function spriteBox(point, sprite, width, height, spriteWidth, spriteHeight) {
  return {
    x: (point.x + 1) * width / 2 + (0.5 - sprite.center.x) * spriteWidth,
    y: (1 - point.y) * height / 2 - (0.5 - sprite.center.y) * spriteHeight,
    width: spriteWidth,
    height: spriteHeight,
  }
}

export function createRouteLayer(terrain) {
  const group = new THREE.Group()
  group.name = 'Journey route'
  group.visible = false
  const routeLines = []
  const arrows = createRouteArrows()
  group.add(arrows.mesh)
  let badges = []
  let labels = []
  const stations = []
  let track = null
  const projection = [new THREE.Vector3(), new THREE.Vector3()]
  const lineStart = new THREE.Vector3()
  const lineEnd = new THREE.Vector3()
  const geometryBounds = new THREE.Box3()
  const projectedBounds = new THREE.Box3()
  const projectionMatrix = new THREE.Matrix4()
  let overview = null

  function setRoute(route, stationMarkers = [], localView = false, previewFlights = false) {
    overview = null
    geometryBounds.makeEmpty()
    for (const line of routeLines.splice(0)) {
      line.removeFromParent()
      line.geometry.dispose()
      line.material.dispose()
    }
    for (const label of labels) if (label) disposeSprite(label.sprite)
    labels = []
    for (const { dot, label } of stations.splice(0)) {
      disposeSprite(dot)
      disposeSprite(label.sprite)
    }
    track = buildTerrainRoute(terrain, route, localView, previewFlights)
    arrows.setDrawings(track?.drawings ?? [])
    group.visible = Boolean(track)
    group.position.y = 0
    if (!track) return null

    if (!badges.length) {
      badges = ['起', '终'].map((text, index) => makeBadge(text, BADGE_COLORS[index]))
      group.add(...badges)
    }

    for (const segment of track.drawings) {
      const geometry = new LineSegmentsGeometry().setPositions(segment.positions)
      geometryBounds.union(geometry.boundingBox)
      const material = new LineMaterial({ color: ROUTE_COLORS[segment.type] ?? ROUTE_COLORS.drive,
        linewidth: segment.airportPreview ? FLIGHT_PREVIEW_WIDTH : ROUTE_WIDTH,
        transparent: true, depthWrite: false, dashed: segment.airportPreview, dashSize: 10, gapSize: 6 })
      const line = new LineSegments2(geometry, material)
      if (segment.airportPreview) line.computeLineDistances()
      line.renderOrder = 5
      routeLines.push(line)
      group.add(line)
    }
    for (const [index, badge] of badges.entries()) {
      const point = track.anchors[index]
      badge.visible = Boolean(point)
      if (point) badge.position.copy(point)
    }
    labels = [route.start, route.end].map((stop, index) => {
      const labelText = localView && !stop?.mapAnchor ? stop?.name : stop?.cityLabel
      const label = track.anchors[index] && makeCityLabel(labelText || stop?.name, BADGE_COLORS[index])
      if (label) {
        label.sprite.position.copy(track.anchors[index])
        group.add(label.sprite)
      }
      return label
    })
    const surfacePoint = createSurfaceSampler(terrain)
    for (const station of stationMarkers) {
      const projected = projectCoordinate(station.location, terrain)
      const point = projected && surfacePoint(...projected)
      if (!point) continue
      const name = station.name?.trim().replace(/站$/, '')
      if (!name || labels.some((label, i) => label?.text.replace(/站$/, '') === name &&
          Math.hypot(point.x - track.anchors[i].x, point.z - track.anchors[i].z) < 1000 / SCENE_UNIT_METERS)) continue
      const label = makeCityLabel(station.name, '#28453f')
      if (!label) continue
      const dot = makeBadge('', '#28453f')
      point.y += track.clearance
      dot.position.copy(point)
      label.sprite.position.copy(point)
      dot.visible = label.sprite.visible = false
      group.add(dot, label.sprite)
      stations.push({ label, dot })
    }
    return track
  }

  function projectedOverview(camera, width, height) {
    if (geometryBounds.isEmpty()) return null
    // The box contains only drawable segments. A loop can have coincident endpoints.
    projectionMatrix.makeTranslation(0, group.position.y, 0)
      .premultiply(camera.matrixWorldInverse).premultiply(camera.projectionMatrix)
    const { min, max } = projectedBounds.copy(geometryBounds).applyMatrix4(projectionMatrix)
    const w = (max.x - min.x) * width / 2
    const h = (max.y - min.y) * height / 2
    const span = Math.max(w, h)
    if (span >= OVERVIEW_SPAN) return null
    return { x: (2 + max.x + min.x) * width / 4, y: (2 - max.y - min.y) * height / 4,
      width: w, height: h, span }
  }

  function update(camera, width, height, focused = false, showStations = false, roadMode = false) {
    if (!track) return []
    const unit = (camera.top - camera.bottom) / (camera.zoom * height)
    // The vertices already contain the atlas clearance. Lower the entire route
    // at street zoom, keeping badges and the animated vehicle on the same line.
    group.position.y = roadMode ? Math.min(track.clearance, Math.max(ROAD_DETAIL_CLEARANCE, unit * 1.5)) - track.clearance : 0
    overview = projectedOverview(camera, width, height)
    const compactness = overview ? 1 - overview.span / OVERVIEW_SPAN : 0
    const badgeSize = BADGE_SIZE - 6 * compactness
    for (const line of routeLines) {
      line.material.linewidth = line.material.dashed ? FLIGHT_PREVIEW_WIDTH : ROUTE_WIDTH + 0.5 * compactness
      if (line.material.dashed) line.material.dashScale = 1 / unit
    }
    arrows.update(camera, width, height, group.position.y)
    for (const badge of badges) {
      badge.scale.setScalar(badgeSize * unit)
      badge.center.set(0.5, 0.5)
    }
    for (const [index, point] of projection.entries()) {
      if (track.anchors[index]) point.copy(track.anchors[index]).add(group.position).project(camera)
    }
    const [from, to] = projection
    const both = badges.every((badge) => badge.visible)
    const dx = both ? (to.x - from.x) * width / 2 : Infinity
    const dy = both ? (to.y - from.y) * height / 2 : Infinity
    const distance = Math.hypot(dx, dy)
    if (both) {
      // As the route shrinks, move both badges outward to uncover the track between them.
      const shift = Math.max((badgeSize + 5 - distance) / (2 * badgeSize), compactness * 0.46)
      const shiftX = shift * (distance > EPSILON ? dx / distance : 1)
      const shiftY = shift * (distance > EPSILON ? dy / distance : 0)
      badges[0].center.set(0.5 + shiftX, 0.5 + shiftY)
      badges[1].center.set(0.5 - shiftX, 0.5 - shiftY)
    }

    const obstacles = []
    for (const [index, badge] of badges.entries()) {
      const point = projection[index]
      if (badge.visible && Math.abs(point.x) < 1.1 && Math.abs(point.y) < 1.1) {
        obstacles.push(spriteBox(point, badge, width, height, badgeSize, badgeSize))
      }
    }

    const labelThreshold = Math.min(72, Math.max(52, ...labels.map((label) => (label?.width ?? 0) + 28)))
    for (const [index, label] of labels.entries()) {
      if (!label) continue
      const point = projection[index]
      const { sprite } = label
      sprite.visible = !showStations && (focused || camera.zoom > 4.5) && distance >= labelThreshold &&
        Math.abs(point.x) < 0.98 && Math.abs(point.y) < 0.98
      if (!sprite.visible) continue
      const x = (point.x + 1) * width / 2
      const badgeGap = 15
      const right = x + badgeGap + label.width < width - 9
      sprite.scale.set(label.width * unit, LABEL_HEIGHT * unit, 1)
      sprite.center.set(right ? -badgeGap / label.width : 1 + badgeGap / label.width, 0.5)
      obstacles.push(spriteBox(point, sprite, width, height, label.width, LABEL_HEIGHT))
    }
    const overlaps = box => obstacles.some(other =>
      Math.abs(other.x - box.x) < (other.width + box.width) / 2 + 2 &&
      Math.abs(other.y - box.y) < (other.height + box.height) / 2 + 2)
    function placeDetailLabel(label, point, gap) {
      const { sprite } = label
      sprite.scale.set(label.width * unit, LABEL_HEIGHT * unit, 1)
      const side = gap / label.width
      const vertical = gap / LABEL_HEIGHT
      for (const [cx, cy] of [[0.5, -vertical], [0.5, 1 + vertical], [-side, 0.5], [1 + side, 0.5],
        [0, -vertical], [1, -vertical], [0, 1 + vertical], [1, 1 + vertical]]) {
        sprite.center.set(cx, cy)
        const box = spriteBox(point, sprite, width, height, label.width, LABEL_HEIGHT)
        if (Math.abs(box.x - width / 2) > (width - box.width) / 2 - 4 ||
            Math.abs(box.y - height / 2) > (height - box.height) / 2 - 4 || overlaps(box)) continue
        sprite.visible = true
        obstacles.push(box)
        break
      }
    }
    // Reserve the stop dots first so that the destination name cannot cover a nearby rail station.
    for (const { dot, label } of stations) {
      dot.visible = label.sprite.visible = false
      if (!showStations) continue
      const point = lineStart.copy(dot.position).add(group.position).project(camera)
      if (Math.abs(point.x) >= 0.98 || Math.abs(point.y) >= 0.98) continue
      const dotBox = { x: (point.x + 1) * width / 2, y: (1 - point.y) * height / 2, width: 12, height: 12 }
      dot.visible = !overlaps(dotBox)
      dot.scale.setScalar(12 * unit)
      if (dot.visible) obstacles.push(dotBox)
    }
    if (showStations) {
      for (const { dot, label } of stations) {
        const point = lineStart.copy(dot.position).add(group.position).project(camera)
        if (Math.abs(point.x) < 0.98 && Math.abs(point.y) < 0.98) placeDetailLabel(label, point, 12)
      }
      for (const [i, label] of labels.entries()) {
        const point = projection[i]
        if (label && Math.abs(point.x) < 0.98 && Math.abs(point.y) < 0.98) placeDetailLabel(label, point, 18)
      }
    }
    return obstacles
  }

  function lineDistance(camera, width, height, x, y) {
    const point = [x, y]
    const positions = track.positions
    let closest = Infinity
    for (let index = 0; index < positions.length; index += 6) {
      lineStart.fromArray(positions, index).add(group.position).project(camera)
      lineEnd.fromArray(positions, index + 3).add(group.position).project(camera)
      closest = Math.min(closest, segmentDistanceSquared(point,
        [(lineStart.x + 1) * width / 2, (1 - lineStart.y) * height / 2],
        [(lineEnd.x + 1) * width / 2, (1 - lineEnd.y) * height / 2]))
    }
    return Math.sqrt(closest)
  }

  return {
    group, setRoute, update, lineDistance,
    get track() { return track },
    get overview() { return overview },
    dispose() {
      setRoute(null)
      arrows.dispose()
      for (const badge of badges) disposeSprite(badge)
      group.clear()
    },
  }
}
