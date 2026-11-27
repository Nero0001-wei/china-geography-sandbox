import * as THREE from 'three'
import { disposeModel } from './dispose-model.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { LANDMARK_DISPLAY_SIZE } from '../shared/landmarks.js'
import { allLandmarksSelected, matchesLandmark } from '../shared/landmark-filters.js'
import { applyLandmarkOcclusion, loadLandmarkOcclusion } from './landmark-occlusion.js'
import { createLandmarkOutline } from './landmark-outline.js'
import { createLandmarkShadow } from './landmark-shadow.js'
import { CLUSTER_RELEASE_GAP, createLandmarkClusters, screenGap } from './landmark-clusters.js'
import { SCENE_UNIT_METERS } from './terrain-data.js'

const BASE_GAP = 0.002
const MAX_MODEL_LOADS = 5
const REGIONAL_MODEL_ZOOM = 1.38
const POINT_SIZE = 12

function southFacingRotation(terrain, [lon, lat], x, z) {
  // The GLB front is local +Z. Project the local meridian to account for map convergence.
  const [southX, southZ] = terrain.geoToWorld(lon, lat - 0.001)
  return Math.atan2(southX - x, southZ - z)
}

function modelSupport(terrain, entry) {
  // Sample the site's ground footprint. The enlarged national-view icon can span another mountain.
  const { x, z } = entry.anchor
  const { min, max } = entry.bounds
  const scale = (entry.landmark.groundSpanMeters ?? 0) / SCENE_UNIT_METERS / Math.max(entry.size.x, entry.size.z)
  const cos = Math.cos(entry.heading)
  const sin = Math.sin(entry.heading)
  let support = entry.anchor.y
  for (const dx of [min.x, (min.x + max.x) / 2, max.x]) {
    for (const dz of [min.z, (min.z + max.z) / 2, max.z]) {
      const worldX = x + scale * (dx * cos + dz * sin)
      const worldZ = z + scale * (dz * cos - dx * sin)
      const sample = terrain.sample(worldX, worldZ)
      if (sample?.land && sample.valid) support = Math.max(support, terrain.surfaceHeight(worldX, worldZ))
    }
  }
  return support + BASE_GAP
}

export function createLandmarkLayer(host, terrain, landmarks, onSelect, invalidate, renderer, onExpand) {
  const group = new THREE.Group()
  group.name = 'Landmarks'
  const shadows = new THREE.Group()
  shadows.name = 'Landmark ground shadows'
  const labels = document.createElement('div')
  labels.className = 'map-landmark-labels'
  labels.setAttribute('role', 'group')
  labels.setAttribute('aria-label', '地图景点')
  labels.addEventListener('pointerdown', event => {
    if (event.button !== 1) event.stopPropagation()
  })
  Object.assign(labels.style, { position: 'absolute', inset: '0', pointerEvents: 'none', zIndex: '2' })
  host.append(labels)

  const labelMeasure = document.createElement('canvas').getContext('2d')
  labelMeasure.font = '600 12px ' + getComputedStyle(host).fontFamily
  const loader = new GLTFLoader()
  const occlusion = loadLandmarkOcclusion()
  const outline = createLandmarkOutline(renderer)
  const entries = new Map()
  const clusterModels = createLandmarkClusters()
  const projected = new THREE.Vector3()
  const viewProjection = new THREE.Matrix4()
  const boxTransform = new THREE.Matrix4()
  const projectedBox = new THREE.Box3()
  const scaleVector = new THREE.Vector3()
  const cameraRight = new THREE.Vector3()
  const lightDirection = new THREE.Vector3()
  let disposed = false
  let pendingLoads = 0
  let highlighted = null

  const lighting = new THREE.Group()
  const daylight = new THREE.DirectionalLight('#fffaef', 4.35)
  daylight.position.set(-0.85, 0.72, 0.54)
  lighting.add(new THREE.HemisphereLight('#e2edff', '#958678', 0.52), daylight)
  group.add(lighting)

  async function loadModel(entry) {
    entry.requested = true
    pendingLoads++
    try {
      const gltf = await loader.loadAsync(entry.landmark.modelUrl)
      const { scene } = gltf
      const bounds = new THREE.Box3().setFromObject(scene)
      if (disposed || bounds.isEmpty()) {
        disposeModel(scene)
        return
      }

      entry.bounds = bounds
      entry.size = bounds.getSize(new THREE.Vector3())
      // Keep the surveyed X/Z origin (e.g. the pine trunk beneath an asymmetric crown).
      scene.position.y -= bounds.min.y
      entry.localBounds = bounds.clone().translate(new THREE.Vector3(0, -bounds.min.y, 0))
      entry.mount.add(scene)
      entry.model = scene
      entry.pivot.position.y = modelSupport(terrain, entry)
      entry.shadow = createLandmarkShadow(renderer, terrain, entry)
      shadows.add(entry.shadow.mesh)
      invalidate()
      const cache = await occlusion
      if (!disposed && applyLandmarkOcclusion(gltf, entry.landmark.id, cache)) invalidate()
    } catch (error) {
      if (!disposed) console.warn(`景点模型加载失败：${entry.landmark.name}`, error)
    } finally {
      pendingLoads--
      if (!disposed) invalidate()
    }
  }

  for (const landmark of landmarks) {
    const [x, z] = terrain.geoToWorld(...landmark.anchor)
    const sample = terrain.sample(x, z)
    if (!sample?.land || !sample.valid) continue
    const anchor = new THREE.Vector3(x, terrain.surfaceHeight(x, z), z)
    const pivot = new THREE.Group()
    pivot.position.copy(anchor)
    const heading = southFacingRotation(terrain, landmark.anchor, x, z)
    const mount = new THREE.Group()
    mount.rotation.y = heading
    pivot.add(mount)
    group.add(pivot)

    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'map-landmark-label'
    button.dataset.landmarkId = landmark.id
    button.setAttribute('aria-keyshortcuts', 'ArrowLeft ArrowRight')
    button.title = `${landmark.name} · 按左右方向键转动模型`
    button.hidden = true
    button.textContent = landmark.name
    button.style.position = 'absolute'
    button.addEventListener('click', () => activate(landmark.id))
    labels.append(button)

    const entry = { landmark, anchor, pivot, mount, heading, button, order: entries.size,
      bounds: null, size: null, model: null, cluster: null,
      labelWidth: Math.ceil(labelMeasure.measureText(landmark.name).width) + 22 }
    entries.set(landmark.id, entry)
  }

  function projectModelBounds(entry, frame, width, height) {
    boxTransform.compose(entry.pivot.position, entry.mount.quaternion, scaleVector.setScalar(frame.scale))
      .premultiply(viewProjection)
    projectedBox.copy(entry.localBounds).applyMatrix4(boxTransform)
    frame.left = (projectedBox.min.x + 1) * width / 2
    frame.right = (projectedBox.max.x + 1) * width / 2
    frame.top = (1 - projectedBox.max.y) * height / 2
    frame.bottom = (1 - projectedBox.min.y) * height / 2
  }

  function screenFrame(entry, camera, width, height, routeDistance, compact = false) {
    projected.copy(entry.anchor).applyMatrix4(viewProjection)
    const x = (projected.x + 1) * width / 2
    const y = (1 - projected.y) * height / 2
    const size = entry.landmark.displaySize ?? LANDMARK_DISPLAY_SIZE
    const viewportSpan = Math.min(width, height * 2)
    const viewportScale = THREE.MathUtils.lerp(1.1, 1.26, THREE.MathUtils.smoothstep(viewportSpan, 600, 1600))
    const normalSize = size * viewportScale * THREE.MathUtils.clamp(Math.sqrt(camera.zoom), 27 / 38, 94 / 38)
    const onScreen = x > -normalSize && x < width + normalSize && y > -normalSize && y < height + normalSize
    const local = routeDistance && camera.zoom > 20 && onScreen
    const cappedSize = local ? size / 38 * Math.min(43, Math.max(0, (routeDistance(x, y) - 8) * 1.45)) : normalSize
    const screenSize = compact ? POINT_SIZE
      : THREE.MathUtils.lerp(normalSize, cappedSize, local ? THREE.MathUtils.smoothstep(camera.zoom, 20, 65) : 0)
    const frame = {
      id: entry.landmark.id, city: entry.landmark.city && entry.landmark.province + '/' + entry.landmark.city,
      x, y, size: screenSize, draw: onScreen && (compact || screenSize >= size * 15 / 38),
      inside: x >= 0 && x <= width && y >= 0 && y <= height,
      left: x - screenSize / 2, right: x + screenSize / 2, top: y - screenSize / 2, bottom: y + screenSize / 2,
    }
    if (entry.model && !compact) {
      const worldPerPixel = (camera.top - camera.bottom) / (camera.zoom * height)
      frame.scale = screenSize * worldPerPixel / Math.max(entry.size.x, entry.size.y, entry.size.z)
      // Use the *would-be* footprint even for a currently hidden member.
      // The mount contains the user's rotation and the bounds retain any off-centre origin.
      projectModelBounds(entry, frame, width, height)
    }
    return frame
  }

  function activate(id) {
    const entry = entries.get(id)
    if (!entry?.frame) return
    if (entry?.cluster) onExpand(entry.cluster)
    else onSelect(entry.landmark)
  }

  function update(camera, width, height, { routeDistance, destinationId, focusedId, searchedId, overview, filter }) {
    // Keep the key light on the same side of the screen as the map turns.
    cameraRight.setFromMatrixColumn(camera.matrixWorld, 0)
    lighting.rotation.y = Math.atan2(-cameraRight.z, cameraRight.x)
    lightDirection.copy(daylight.position).applyQuaternion(lighting.quaternion).normalize()
    viewProjection.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse)
    const compactOverview = camera.zoom < REGIONAL_MODEL_ZOOM && allLandmarksSelected(filter)
    const candidates = []
    for (const entry of entries.values()) {
      const landmark = entry.landmark
      const searched = landmark.id === searchedId
      const compact = compactOverview && landmark.tier === 'regional'
        && landmark.id !== destinationId && landmark.id !== focusedId && !searched
      const frame = searched || matchesLandmark(landmark, filter)
        ? screenFrame(entry, camera, width, height, searched ? null : routeDistance, compact) : null
      entry.frame = frame
      entry.compact = compact
      entry.cluster = null
      entry.pivot.visible = Boolean(frame?.draw && !compact)
      if (frame?.draw) candidates.push(frame)
    }
    for (const ids of clusterModels(candidates)) {
      const members = ids.map(id => entries.get(id))
      // Keep a representative of the filtered group visible while its model loads.
      members.sort((a, b) => Number(b.frame.inside) - Number(a.frame.inside)
        || Number(b.landmark.id === searchedId) - Number(a.landmark.id === searchedId)
        || Number(b.landmark.id === destinationId) - Number(a.landmark.id === destinationId)
        || Number(a.compact) - Number(b.compact)
        || Number(b.landmark.tier === 'national') - Number(a.landmark.tier === 'national')
        || a.order - b.order)
      members[0].cluster = ids
      for (const member of members.slice(1)) {
        member.pivot.visible = false
        member.clusteredAway = true
      }
    }
    const visible = []
    const loads = []
    for (const entry of entries.values()) {
      const { frame, cluster, button, landmark } = entry
      const clusteredAway = entry.clusteredAway
      entry.clusteredAway = false
      if (entry.pivot.visible && landmark.modelUrl && !entry.requested) loads.push(entry)
      if (entry.model && entry.pivot.visible) {
        // Cluster at the usual scale, then make room for a short projected route under the model.
        if (overview) {
          const gap = Math.max(0, frame.left - overview.x - overview.width / 2,
            overview.x - overview.width / 2 - frame.right, frame.top - overview.y - overview.height / 2,
            overview.y - overview.height / 2 - frame.bottom)
          const weight = (1 - THREE.MathUtils.smoothstep(gap, 0, 10)) * (1 - THREE.MathUtils.smoothstep(overview.span, 65, 140))
          if (weight > 0) {
            const limit = THREE.MathUtils.clamp(overview.span * 0.17, 5, 18)
            const factor = THREE.MathUtils.lerp(1, Math.min(1, limit / frame.size), weight)
            frame.scale *= factor
            frame.size *= factor
            projectModelBounds(entry, frame, width, height)
          }
        }
        entry.pivot.scale.setScalar(frame.scale)
      }
      entry.shadow?.update(lightDirection)
      if (!frame || clusteredAway || (!frame.inside && !entry.pivot.visible)) {
        button.hidden = true
        button.classList.remove('has-hover-placement')
        continue
      }
      const countOnly = !filter.showNames && Boolean(cluster)
      const modelControl = !filter.showNames && !cluster && Boolean(entry.model && entry.pivot.visible)
      const dot = !cluster && (entry.compact || (!filter.showNames && !modelControl))
      const name = cluster ? landmark.city.replace(/市$/, '') + ' · ' + cluster.length + '个景点' : landmark.name
      const text = filter.showNames ? name : countOnly ? String(cluster.length) : ''
      button.classList.toggle('is-cluster', Boolean(cluster))
      button.classList.toggle('is-cluster-count', countOnly)
      button.classList.toggle('is-landmark-point', dot)
      button.classList.toggle('is-model-control', modelControl)
      if (button.getAttribute('aria-label') !== name) button.setAttribute('aria-label', name)
      if (button.textContent !== text) {
        button.textContent = text
        entry.labelWidth = Math.ceil(labelMeasure.measureText(text).width) + 22
      }
      if (cluster || !filter.showNames) button.removeAttribute('title')
      else button.title = dot ? landmark.name : landmark.name + ' · 按左右方向键转动模型'
      const size = entry.pivot.visible || (dot && entry.compact) ? frame.size : 0
      visible.push({ x: frame.x, y: frame.y, size, button, bounds: size ? frame : null, dot, modelControl,
        offscreen: !frame.inside,
        national: landmark.tier === 'national', clustered: Boolean(cluster),
        width: dot ? POINT_SIZE : countOnly ? Math.max(28, entry.labelWidth) : entry.labelWidth,
        height: dot ? POINT_SIZE : 30 })
    }
    const priorityId = searchedId ?? destinationId ?? focusedId
    loads.sort((a, b) => Number(b.landmark.id === priorityId) - Number(a.landmark.id === priorityId)
      || Number(b.landmark.tier === 'national') - Number(a.landmark.tier === 'national'))
    for (const entry of loads.slice(0, Math.max(0, MAX_MODEL_LOADS - pendingLoads))) loadModel(entry)
    return visible
  }

  function expansionView(ids, camera, width, height, maxZoom) {
    const members = ids.map(id => entries.get(id))
    const point = new THREE.Box3().setFromPoints(members.map(entry => entry.anchor)).getCenter(new THREE.Vector3())
    const probe = camera.clone()
    const direction = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 2).normalize()
    function separated(zoom) {
      probe.zoom = zoom
      probe.updateProjectionMatrix()
      viewProjection.multiplyMatrices(probe.projectionMatrix, probe.matrixWorldInverse)
      const frames = members.map(entry => screenFrame(entry, probe, width, height))
      return frames.every((a, i) => frames.slice(i + 1).every(b => screenGap(a, b) > CLUSTER_RELEASE_GAP + 6))
    }
    function aim() {
      probe.position.copy(point).addScaledVector(direction, 82)
      probe.lookAt(point)
      probe.updateMatrixWorld()
    }
    aim()
    let high = Math.max(camera.zoom, maxZoom)
    // A narrow viewport can require more zoom than the usual terrain limit.
    if (!separated(high)) high *= 2
    // A low orbit can align two anchors in the same line of sight, even at high zoom.
    if (!separated(high)) {
      direction.set(0, 1, 0.0005).normalize()
      aim()
      while (!separated(high) && high < maxZoom * 8) high *= 2
    }
    let low = camera.zoom
    for (let i = 0; i < 12; i++) {
      const mid = (low + high) / 2
      if (separated(mid)) high = mid
      else low = mid
    }
    return { point, direction, zoom: high }
  }

  function pick(raycaster, screenPoint) {
    let picked = null
    let distance = Infinity
    for (const entry of entries.values()) {
      if (!entry.model || !entry.pivot.visible) continue
      if (screenPoint && entry.frame && (screenPoint.x < entry.frame.left || screenPoint.x > entry.frame.right ||
          screenPoint.y < entry.frame.top || screenPoint.y > entry.frame.bottom)) continue
      const hit = raycaster.intersectObject(entry.model, true)[0]
      if (hit && hit.distance < distance) {
        picked = entry.landmark
        distance = hit.distance
      }
    }
    return picked
  }

  return {
    group, shadows, update, pick, activate, expansionView,
    setHighlight(id) {
      const entry = entries.get(id)
      const next = entry?.frame && (entry.pivot.visible || (entry.compact && !entry.button.hidden)) ? entry : null
      if (next === highlighted) return false
      highlighted?.button.classList.remove('is-highlighted')
      highlighted = next
      highlighted?.button.classList.add('is-highlighted')
      return true
    },
    renderHighlight(camera, width, height) {
      const model = highlighted?.pivot.visible ? highlighted.model : null
      outline.render(model, camera, highlighted?.frame, width, height)
    },
    getCluster(id) {
      const entry = entries.get(id)
      if (!entry?.cluster || !entry.frame?.inside) return null
      return {
        button: entry.button, bounds: entry.frame,
        names: [entry.landmark.name, ...entry.cluster.filter(member => member !== id).map(member => entries.get(member).landmark.name)],
      }
    },
    invalidateShadows() {
      for (const entry of entries.values()) entry.shadow?.invalidate()
    },
    turn(id, radians) {
      const entry = entries.get(id)
      if (!entry?.model) return
      entry.mount.rotation.y += radians
      invalidate()
    },
    resetTurns() {
      for (const entry of entries.values()) entry.mount.rotation.y = entry.heading
      invalidate()
    },
    focus(id, baseZoom, worldPerPixel, maxZoom) {
      const point = entries.get(id)?.anchor
      if (!point) return null
      let nearest = Infinity
      for (const { anchor } of entries.values()) {
        if (anchor !== point) nearest = Math.min(nearest, Math.hypot(point.x - anchor.x, point.z - anchor.z))
      }
      const zoom = THREE.MathUtils.clamp(80 * worldPerPixel / nearest, baseZoom, maxZoom)
      return { point, zoom }
    },
    dispose() {
      disposed = true
      labels.remove()
      outline.dispose()
      for (const entry of entries.values()) {
        entry.shadow?.dispose()
        if (entry.model) disposeModel(entry.model)
      }
      shadows.clear()
      group.clear()
      entries.clear()
    },
  }
}
