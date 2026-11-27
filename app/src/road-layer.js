import * as THREE from 'three'
import { LineMaterial } from 'three/addons/lines/LineMaterial.js'
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js'
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js'
import { ROAD_STYLES } from './road-styles.js'
import { createRoadDetailTiles } from './road-detail-tiles.js'
import { createSurfaceSampler, drapePolyline } from './terrain-polyline.js'
import { METERS_TO_HEIGHT, SCENE_UNIT_METERS } from './terrain-data.js'

const ROAD_LIFT = 0.00035
const WEB_MERCATOR_PIXEL_METERS = 156543.033928

// Intersect the orthographic view with the exaggerated terrain. A ground-plane
// footprint alone misses mountains when the camera is tilted close to horizontal.
export function roadTileView(terrain, camera, width) {
  const metersPerPixel = (camera.right - camera.left) / (camera.zoom * width) * SCENE_UNIT_METERS
  if (metersPerPixel > 1200) return null
  const direction = camera.getWorldDirection(new THREE.Vector3())
  if (direction.y > -0.001) return null
  const sample = new THREE.Vector3()
  const point = new THREE.Vector3()
  const elevations = terrain.metadata.elevationRange ?? [0, 6500]
  const top = elevations[1] * METERS_TO_HEIGHT + 0.002
  const bottom = Math.min(0, elevations[0]) * METERS_TO_HEIGHT - 0.002
  function atHeight(h) {
    point.copy(sample).addScaledVector(direction, (h - sample.y) / direction.y)
    return h - (terrain.sample(point.x, point.z)?.elevation ?? 0) * METERS_TO_HEIGHT
  }
  const bounds = [Infinity, Infinity, -Infinity, -Infinity]
  let center = null
  for (const u of [-1, 0, 1]) {
    for (const v of [-1, 0, 1]) {
      sample.set(u, v, 0).unproject(camera)
      let hi = top, lo = bottom
      for (let i = 1; i <= 8; i++) {
        lo = THREE.MathUtils.lerp(top, bottom, i / 8)
        if (atHeight(lo) <= 0) break
        hi = lo
      }
      for (let i = 0; i < 8; i++) {
        const mid = (lo + hi) / 2
        if (atHeight(mid) > 0) hi = mid
        else lo = mid
      }
      atHeight((lo + hi) / 2)
      const [lon, lat] = terrain.worldToGeo(point.x, point.z)
      if (!Number.isFinite(lon) || !Number.isFinite(lat)) return null
      if (!u && !v) center = [lon, lat]
      bounds[0] = Math.min(bounds[0], lon)
      bounds[1] = Math.min(bounds[1], lat)
      bounds[2] = Math.max(bounds[2], lon)
      bounds[3] = Math.max(bounds[3], lat)
    }
  }
  const zoom = Math.min(14, Math.round(Math.log2(
    WEB_MERCATOR_PIXEL_METERS * Math.cos(THREE.MathUtils.degToRad(center[1])) / metersPerPixel)))
  return zoom >= 8 ? { bounds, center, zoom } : null
}

function* overviewRoads(data) {
  for (const tier of data.tiers) {
    if (!tier || !Object.hasOwn(ROAD_STYLES, tier.id) || !Array.isArray(tier.lines)) continue
    for (const coordinates of tier.lines) yield { kind: tier.id, coordinates }
  }
}

export function createRoadLayer(terrain, invalidate, onStatus) {
  const group = new THREE.Group()
  group.name = 'Road network'
  group.visible = false
  const overview = new THREE.Group()
  const detail = new THREE.Group()
  group.add(overview, detail)
  const materials = Object.fromEntries(Object.entries(ROAD_STYLES).map(([kind, style]) =>
    [kind, new LineMaterial({ color: style.color, linewidth: style.width, transparent: true,
      opacity: 0.96, depthWrite: false })]))
  const sample = createSurfaceSampler(terrain)
  const jobs = []
  const liveTiles = new Map()
  const recentTiles = new Map()
  let retainedSegments = 0
  const viewProjection = new THREE.Matrix4()
  const previousView = new THREE.Matrix4()
  let previousWidth = 0
  let frame = 0
  let disposed = false
  let overviewState = 'idle'
  let overviewRequest
  let tileStatus = { complete: false, expected: 0 }
  let labels = []
  let reported = ''
  let usingTiles = false

  function refresh() {
    let count = 0
    let hasRoads = false
    for (const tile of liveTiles.values()) {
      if (tile.mesh) {
        count++
        if (tile.mesh.children.length) hasRoads = true
      }
    }
    detail.visible = tileStatus.complete && count === tileStatus.expected && hasRoads
    overview.visible = !detail.visible
    const phase = detail.visible ? 'detail' : overviewState === 'ready' ? 'overview'
      : overviewState === 'error' ? 'unavailable' : 'loading'
    const detailUnavailable = Boolean(!detail.visible && tileStatus.failed)
    const present = new Set()
    const active = detail.visible ? detail : overview
    active.traverse(object => {
      if (object.isLineSegments2 && object.material.visible) present.add(object.name)
    })
    const kinds = Object.keys(ROAD_STYLES).filter(kind => present.has(kind))
    const signature = phase + ':' + detailUnavailable + ':' + kinds.join(',')
    if (group.visible && signature !== reported) {
      reported = signature
      onStatus?.({ phase, detailUnavailable, kinds })
    }
    labels = detail.visible ? Array.from(liveTiles.values()).flatMap(tile => tile.labels) : []
    invalidate()
  }

  function enqueue(roads, done) {
    const job = { roads, done, buckets: {}, cancelled: false }
    jobs.push(job)
    schedule()
    return job
  }

  function schedule() {
    if (!frame && !disposed && group.visible && jobs.length) frame = requestAnimationFrame(build)
  }

  // Project in small batches. City tiles with several thousand streets should
  // not block orbit controls or route playback while the overview is visible.
  function build() {
    frame = 0
    const deadline = performance.now() + 5
    while (jobs.length && performance.now() < deadline) {
      const job = jobs[0]
      if (job.cancelled) {
        jobs.shift()
        continue
      }
      const next = job.roads.next()
      if (next.done) {
        jobs.shift()
        const result = new THREE.Group()
        for (const [kind, positions] of Object.entries(job.buckets)) {
          const geometry = new LineSegmentsGeometry()
          geometry.setPositions(positions)
          const line = new LineSegments2(geometry, materials[kind])
          line.name = kind
          line.renderOrder = ROAD_STYLES[kind].order
          result.add(line)
        }
        job.done(result)
        continue
      }
      const { kind, coordinates } = next.value
      if (!Object.hasOwn(ROAD_STYLES, kind)) continue
      const positions = drapePolyline(terrain, coordinates, sample, true)
      if (!positions.length) continue
      const bucket = job.buckets[kind] ??= []
      for (let i = 0; i < positions.length; i += 3) {
        bucket.push(positions[i], positions[i + 1] + ROAD_LIFT, positions[i + 2])
      }
    }
    schedule()
  }

  function removeTile(key) {
    const tile = liveTiles.get(key)
    if (!tile) return
    liveTiles.delete(key)
    if (tile.job) tile.job.cancelled = true
    if (tile.mesh) {
      tile.mesh.removeFromParent()
      if (!disposed && group.visible) {
        recentTiles.set(key, tile)
        retainedSegments += tile.segments
        while (recentTiles.size > 12 || retainedSegments > 90_000) {
          const [oldKey, old] = recentTiles.entries().next().value
          recentTiles.delete(oldKey)
          retainedSegments -= old.segments
          old.mesh.traverse(object => object.geometry?.dispose())
        }
      } else {
        tile.mesh.traverse(object => object.geometry?.dispose())
      }
    }
    refresh()
  }

  const tiles = createRoadDetailTiles({
    onTile(data) {
      if (disposed || !group.visible) return
      removeTile(data.key)
      const cached = recentTiles.get(data.key)
      if (cached) {
        recentTiles.delete(data.key)
        retainedSegments -= cached.segments
        liveTiles.set(data.key, cached)
        detail.add(cached.mesh)
        refresh()
        return
      }
      const tile = { labels: data.labels ?? [], mesh: null }
      liveTiles.set(data.key, tile)
      tile.job = enqueue(data.roads.values(), mesh => {
        tile.job = null
        tile.mesh = mesh
        tile.segments = mesh.children.reduce((n, line) => n + line.geometry.instanceCount, 0)
        detail.add(mesh)
        refresh()
      })
    },
    onRemove: removeTile,
    onStatus(status) {
      tileStatus = status
      refresh()
    },
  })

  async function loadOverview() {
    overviewRequest = new AbortController()
    overviewState = 'loading'
    try {
      const response = await fetch(import.meta.env.BASE_URL + 'data/roads/overview.json', { signal: overviewRequest.signal })
      if (!response.ok) throw new Error('Road overview unavailable')
      const data = await response.json()
      if (data.version !== 1 || !Array.isArray(data.tiers)) throw new Error('Invalid road overview')
      if (disposed) return
      enqueue(overviewRoads(data), mesh => {
        overview.add(mesh)
        overviewState = mesh.children.length ? 'ready' : 'error'
        refresh()
      })
    } catch {
      if (disposed) return
      overviewState = 'error'
      refresh()
    }
  }

  function setEnabled(enabled) {
    if (group.visible === enabled || disposed) return
    group.visible = enabled
    previousWidth = 0
    if (enabled) {
      if (overviewState === 'idle' || overviewState === 'error') loadOverview()
      schedule()
      refresh()
    } else {
      cancelAnimationFrame(frame)
      frame = 0
      tiles.clear()
      usingTiles = false
      reported = ''
      labels = []
      invalidate()
    }
  }

  function update(camera, width) {
    if (!group.visible || !width) return
    camera.updateMatrixWorld()
    viewProjection.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse)
    if (previousWidth === width && viewProjection.equals(previousView)) return
    previousView.copy(viewProjection)
    previousWidth = width
    const metersPerPixel = (camera.right - camera.left) / (camera.zoom * width) * SCENE_UNIT_METERS
    const t = THREE.MathUtils.smoothstep(Math.log2(metersPerPixel), 6, 12.4)
    for (const [kind, material] of Object.entries(materials)) {
      material.linewidth = ROAD_STYLES[kind].width * (1 - 0.48 * t)
    }
    const showSecondary = metersPerPixel < 2600
    if (materials.secondary.visible !== showSecondary) {
      materials.secondary.visible = showSecondary
      refresh()
    }
    const view = roadTileView(terrain, camera, width)
    if (view) {
      usingTiles = true
      tiles.update(view)
    } else if (usingTiles) {
      usingTiles = false
      tiles.clear()
    }
  }

  return {
    group, setEnabled, update,
    get labels() { return labels },
    dispose() {
      disposed = true
      group.visible = false
      overviewRequest?.abort()
      cancelAnimationFrame(frame)
      tiles.dispose()
      for (const key of liveTiles.keys()) removeTile(key)
      jobs.length = 0
      overview.traverse(obj => obj.geometry?.dispose())
      for (const tile of recentTiles.values()) tile.mesh.traverse(object => object.geometry?.dispose())
      recentTiles.clear()
      for (const material of Object.values(materials)) material.dispose()
    },
  }
}
