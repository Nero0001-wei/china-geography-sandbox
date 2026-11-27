import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js'
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js'
import { LineMaterial } from 'three/addons/lines/LineMaterial.js'
import { LANDMARKS } from '../shared/landmarks.js'
import { ALL_LANDMARKS } from '../shared/landmark-filters.js'
import { makeAtlasSurface } from './atlas-surface.js'
import { createRoadLayer } from './road-layer.js'
import { createLandmarkLayer } from './landmark-layer.js'
import { createLandmarkTooltip } from './landmark-tooltip.js'
import { createVehicleLayer } from './vehicle-layer.js'
import { buildRouteFocus, createRouteLayer, frameTerrainRoute, routeZoomLimit } from './route-layer.js'
import { getMapLabels, METERS_TO_HEIGHT, SCENE_UNIT_METERS } from './terrain-data.js'

const HOME = new THREE.Vector3(1.5, 65, 30).normalize()
const TOP = new THREE.Vector3(0, 1, 0.0005).normalize()
const MAP_MAX_ZOOM = 180
const MODEL_TURN_PER_PIXEL = Math.PI / 110
const DRAG_THRESHOLD = 6

function labelLeader(label, cx, cy) {
  const vx = label.x - cx
  const vy = label.y - cy
  const distance = Math.hypot(vx, vy)
  // The visible segment stops short of the model and begins at the edge of the pill.
  const edge = Math.min(label.width / (2 * Math.abs(vx)), label.height / (2 * Math.abs(vy)))
  const length = distance * (1 - edge) - Math.max(3, label.size * 0.34)
  if (length <= 10 || !distance) return null
  return { x: cx + vx * edge, y: cy + vy * edge, dx: vx / distance * length, dy: vy / distance * length }
}

function intersectLeaders(a, b) {
  const den = a.dx * b.dy - a.dy * b.dx
  if (!den) return false
  const x = b.x - a.x, y = b.y - a.y
  const t = (x * b.dy - y * b.dx) / den, s = (x * a.dy - y * a.dx) / den
  return t > 0 && t < 1 && s > 0 && s < 1
}

function linework(terrain, lines, color, opacity, width, offset = 0.016) {
  const vertices = []
  const { width: cols, height: rows, bounds } = terrain.metadata
  const inBounds = ([x, z]) => Math.abs(x) <= (bounds.maxX - bounds.minX) / SCENE_UNIT_METERS / 2 &&
    Math.abs(z) <= (bounds.maxY - bounds.minY) / SCENE_UNIT_METERS / 2
  const cellWidth = (bounds.maxX - bounds.minX) / (cols - 1)
  const cellHeight = (bounds.maxY - bounds.minY) / (rows - 1)
  const maxStep = Math.min(cellWidth, cellHeight) / SCENE_UNIT_METERS / 2

  for (const line of lines) {
    const projected = line.map(([lon, lat]) => terrain.geoToWorld(lon, lat))
    for (let i = 1; i < projected.length; i++) {
      const start = projected[i - 1]
      const end = projected[i]
      if (!inBounds(start) && !inBounds(end)) continue

      const [x1, z1] = start
      const [x2, z2] = end
      const steps = Math.min(140, Math.max(1, Math.ceil(Math.hypot(x2 - x1, z2 - z1) / maxStep)))
      let x = x1
      let z = z1
      let y = (terrain.sample(x, z)?.elevation ?? 0) * METERS_TO_HEIGHT + offset
      for (let j = 1; j <= steps; j++) {
        const nextX = THREE.MathUtils.lerp(x1, x2, j / steps)
        const nextZ = THREE.MathUtils.lerp(z1, z2, j / steps)
        const nextY = (terrain.sample(nextX, nextZ)?.elevation ?? 0) * METERS_TO_HEIGHT + offset
        vertices.push(x, y, z, nextX, nextY, nextZ)
        x = nextX
        z = nextZ
        y = nextY
      }
    }
  }

  const geometry = new LineSegmentsGeometry()
  geometry.setPositions(vertices)
  const material = new LineMaterial({
    color, opacity, linewidth: width, transparent: true, depthWrite: false,
  })

  return new LineSegments2(geometry, material)
}

export function createMapScene(host, overlays, data, callbacks) {
  const { terrain, boundaries, profile } = data
  const { bounds } = terrain.metadata
  const terrainWidth = (bounds.maxX - bounds.minX) / SCENE_UNIT_METERS
  const terrainDepth = (bounds.maxY - bounds.minY) / SCENE_UNIT_METERS
  const scene = new THREE.Scene()
  const landmarkScene = new THREE.Scene()
  scene.background = new THREE.Color(...data.atlas.paper.map((v) => v / 255)).convertSRGBToLinear()
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 300)
  const homeRight = new THREE.Vector3().crossVectors(camera.up, HOME).normalize()
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
  const canvas = renderer.domElement
  canvas.tabIndex = 0
  canvas.setAttribute('aria-label', '三维地形地图。按住鼠标中键拖动可平移地图，左键横拖景点可转动模型。方向键平移，加减键缩放，0 键重置视角和模型朝向。')
  host.append(canvas)

  const controls = new OrbitControls(camera, host)
  controls.mouseButtons.MIDDLE = THREE.MOUSE.PAN
  controls.enableDamping = true
  controls.dampingFactor = 0.12
  controls.maxPolarAngle = Math.PI * 0.47
  controls.maxZoom = MAP_MAX_ZOOM
  controls.cursor.set(0, 0, 0)
  controls.maxTargetRadius = Math.hypot(terrainWidth, terrainDepth) / 2
  controls.rotateSpeed = 0.55
  controls.panSpeed = 0.78
  controls.zoomSpeed = 0.80
  controls.listenToKeyEvents(canvas)

  const surface = makeAtlasSurface(terrain, data.atlas, data.overview, renderer, invalidate)
  scene.add(surface.mesh)
  const roads = createRoadLayer(terrain, invalidate, callbacks.onRoadStatus)
  scene.add(roads.group)

  const national = linework(terrain, [...boundaries.country, ...boundaries.islands], '#6a604a', 0.62, 0.92)
  national.renderOrder = 2
  const provinces = linework(terrain, boundaries.provinces, '#756c59', 0.46, 0.78)
  provinces.renderOrder = 1
  const profileCoordinates = profile.samples
    .filter(({ longitude }) => longitude >= 79.2 && longitude <= 121.65)
    .map(({ longitude }) => [longitude, profile.latitude])
  const section = linework(terrain, [profileCoordinates], '#006869', 0.96, 1.85, 0.045)
  section.renderOrder = 3
  section.visible = false
  scene.add(national, provinces, section)
  const routeLayer = createRouteLayer(terrain)
  const vehicles = createVehicleLayer(invalidate, callbacks.onPlayback)
  const landmarks = createLandmarkLayer(host, terrain, LANDMARKS,
    landmark => callbacks.onLandmark?.(landmark), invalidate, renderer, expandCity)
  scene.add(landmarks.shadows)
  scene.add(routeLayer.group)
  landmarkScene.add(landmarks.group, vehicles.group)

  const raycaster = new THREE.Raycaster()
  const pointer = new THREE.Vector2()
  let landmarkFilter = ALL_LANDMARKS
  const tooltip = createLandmarkTooltip(host, canvas, id => landmarkFilter.showNames ? landmarks.getCluster(id) : null, event => {
    const screenPoint = aimAt(event)
    return landmarks.pick(raycaster, screenPoint)?.id
  }, id => {
    if (landmarks.setHighlight(id)) requestFrame()
  })
  const projected = new THREE.Vector3()
  const origin = new THREE.Vector3()
  const north = new THREE.Vector3()
  const northDirection = new THREE.Vector3()
  const homeCenter = new THREE.Vector3(-0.12, 0.35, -0.2)
  const range = new THREE.Vector3()
  let state = { provinces: true, labels: true, profile: false }
  let selection = null
  let focusedLandmark = null
  let searchedLandmarkId = null
  let destinationLandmarkId = null
  let expandedMembers = new Set()
  let profilePoint = null
  let transition
  let routeFramed = false
  let differenceFrame = null
  let showDifference = false
  let frame = 0
  let sceneChanged = true
  let contextAvailable = true
  let inViewport = true
  let disposed = false
  let width = 1
  let height = 1
  const landmarkCaptions = []
  const shieldNodes = []
  const shieldPositions = new WeakMap()

  function updateRoadShields(occupied) {
    const names = new Set()
    const cells = new Set()
    let used = 0
    for (const label of roads.labels) {
      if (names.has(label.text)) continue
      let world = shieldPositions.get(label)
      if (!world) {
        const [x, z] = terrain.geoToWorld(label.lon, label.lat)
        world = new THREE.Vector3(x, terrain.surfaceHeight(x, z), z)
        shieldPositions.set(label, world)
      }
      projected.copy(world).project(camera)
      const x = (projected.x + 1) * width / 2, y = (1 - projected.y) * height / 2
      const street = label.kind === 'name'
      const halfWidth = label.text.length * (street ? 5.8 : 3.6) + 5
      if (x < halfWidth + 7 || x > width - halfWidth - 7 || y < 14 || y > height - 25 ||
        occupied.some(box => Math.abs(box.x - x) < box.width / 2 + halfWidth + 7 &&
          Math.abs(box.y - y) < (box.height ?? 18) / 2 + 12)) continue
      const cell = Math.floor(x / 155) + ',' + Math.floor(y / 105)
      if (cells.has(cell)) continue
      let node = shieldNodes[used]
      if (!node) {
        node = document.createElement('span')
        node.className = 'road-shield'
        overlays.roadLabels.append(node)
        shieldNodes.push(node)
      }
      node.hidden = false
      node.classList.toggle('road-street-name', street)
      node.textContent = label.text
      node.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -50%)`
      names.add(label.text)
      cells.add(cell)
      occupied.push({ x, y, width: halfWidth * 2 + 30, height: 29 })
      if (++used >= (width < 560 ? 4 : 9)) break
    }
    for (let i = used; i < shieldNodes.length; i++) shieldNodes[i].hidden = true
  }

  const terrainLabels = getMapLabels(boundaries).map((label, i) => {
    const [x, z] = terrain.geoToWorld(label.lon, label.lat)
    return {
      ...label,
      point: new THREE.Vector3(x, label.water ? 0 : terrain.surfaceHeight(x, z) + 0.08, z),
      element: overlays.labels[i],
    }
  })

  function position(point, element, offsetY = 0) {
    projected.copy(point).project(camera)
    if (Math.abs(projected.x) > 0.99 || Math.abs(projected.y) > 0.99) return null
    const x = (projected.x + 1) / 2 * width
    const y = (1 - projected.y) / 2 * height + offsetY
    element.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`
    return [x, y]
  }

  function placeMarker(point, element) {
    const visible = point && position(point, element)
    element.hidden = !visible
    if (visible) {
      element.classList.toggle('marker-is-low', visible[1] > height - 105)
      element.classList.toggle('marker-is-right', visible[0] > width - 145)
    }
    return visible
  }

  function updateOverlays(visibleLandmarks, routeObstacles) {
    landmarkCaptions.length = 0
    const occupied = routeObstacles
    if (routeLayer.overview) {
      const { x, y, width, height } = routeLayer.overview
      occupied.push({ x, y, width: width + 10, height: height + 10 })
    }
    const marker = placeMarker(selection, overlays.marker)
    if (marker) occupied.push({ x: marker[0], y: marker[1], width: 110 })
    placeMarker(profilePoint, overlays.profilePoint)
    for (const element of host.parentElement.querySelectorAll(':scope > .map-heading, :scope > .basemap-switch, :scope > .map-tools, :scope > .map-legend, :scope > .map-scale, :scope > .map-landmark-detail')) {
      const w = element.offsetWidth, h = element.offsetHeight
      if (w && h) occupied.push({ x: element.offsetLeft + w / 2, y: element.offsetTop + h / 2, width: w, height: h })
    }
    // Reserve visible model footprints so displaced captions leave the models clickable.
    for (const { x, y, size, bounds } of visibleLandmarks) {
      if (!size) continue
      if (bounds) {
        occupied.push({ x: (bounds.left + bounds.right) / 2, y: (bounds.top + bounds.bottom) / 2,
          width: bounds.right - bounds.left, height: bounds.bottom - bounds.top })
      } else occupied.push({ x, y, width: size, height: size })
    }
    const labelPriority = ({ button, clustered, national }) => {
      const id = button.dataset.landmarkId
      return Number(id === destinationLandmarkId) * 16 + Number(expandedMembers.has(id)) * 8 +
        Number(clustered) * 4 + Number(id === focusedLandmark) * 2 + Number(national)
    }
    const leaders = []
    visibleLandmarks.sort((a, b) => labelPriority(b) - labelPriority(a))
    for (const label of visibleLandmarks) {
      const { x, y, size, button } = label
      if (label.dot || label.modelControl) {
        button.hidden = label.offscreen
        button.classList.remove('has-leader', 'has-hover-placement')
        const box = label.modelControl ? label.bounds : null
        button.style.left = `${(box ? (box.left + box.right) / 2 : x).toFixed(1)}px`
        button.style.top = `${(box ? (box.top + box.bottom) / 2 : y).toFixed(1)}px`
        if (box) {
          button.style.setProperty('--landmark-focus-width', `${Math.max(20, box.right - box.left)}px`)
          button.style.setProperty('--landmark-focus-height', `${Math.max(20, box.bottom - box.top)}px`)
        }
        continue
      }
      const canOffset = label.clustered || expandedMembers.has(button.dataset.landmarkId)
      const dy = (size + label.height) / 2 + 5
      const dx = (size + label.width) / 2 + 6
      const candidates = [[x, y - dy], [x, y + dy], [x - dx, y], [x + dx, y]]
      if (canOffset || button.dataset.landmarkId === focusedLandmark) {
        for (const offset of [-label.width / 2 + 12, label.width / 2 - 12]) {
          candidates.push([x + offset, y - dy], [x + offset, y + dy])
        }
      }
      if (canOffset) {
        candidates.push([x - dx, y - dy], [x + dx, y - dy], [x - dx, y + dy], [x + dx, y + dy])
      }
      // Use the actual button height for the very narrow gaps beside a mobile toolbar.
      const halfWidth = label.width / 2, halfHeight = 14
      const padX = 2, padY = 2
      const minX = halfWidth + 3, maxX = width - minX
      const minY = halfHeight + 3, maxY = height - minY
      let fallback, fallbackDistance = Infinity
      const fits = (cx, cy) => {
        if (cx < minX || cx > maxX || cy < minY || cy > maxY ||
          occupied.some(other => Math.abs(other.x - cx) < other.width / 2 + halfWidth + padX &&
            Math.abs(other.y - cy) < (other.height ?? 18) / 2 + halfHeight + padY)) return false
        const segment = canOffset && labelLeader(label, cx, cy)
        if (segment && leaders.some(other => intersectLeaders(segment, other))) {
          const distance = Math.hypot(cx - x, cy - y)
          if (distance < fallbackDistance) {
            fallback = [cx, cy]
            fallbackDistance = distance
          }
          return false
        }
        return true
      }
      let placement = label.offscreen ? null : candidates.find(([cx, cy]) => fits(cx, cy))
      if (!placement && canOffset && !label.offscreen) {
        // The nearest free position lies on an obstacle edge, a viewport edge, or an
        // axis through the anchor. Testing those coordinates also finds narrow gaps.
        const xs = [x, minX, maxX], ys = [y, minY, maxY]
        for (const other of occupied) {
          const dx = other.width / 2 + halfWidth + padX + 0.1
          const dy = (other.height ?? 18) / 2 + halfHeight + padY + 0.1
          xs.push(other.x - dx, other.x + dx)
          ys.push(other.y - dy, other.y + dy)
        }
        let best = 205 ** 2
        for (const cx of xs) {
          if (cx < minX || cx > maxX) continue
          for (const cy of ys) {
            const distance = (cx - x) ** 2 + (cy - y) ** 2
            if (distance < best && fits(cx, cy)) {
              best = distance
              placement = [cx, cy]
            }
          }
        }
      }
      placement ??= fallback
      button.hidden = !placement
      button.classList.toggle('has-hover-placement', !placement)
      if (!placement) {
        const above = (label.bounds?.top ?? y) - halfHeight - 5
        const below = (label.bounds?.bottom ?? y) + halfHeight + 5
        button.style.left = `${THREE.MathUtils.clamp(x, minX, maxX).toFixed(1)}px`
        button.style.top = `${THREE.MathUtils.clamp(above >= minY ? above : below, minY, maxY).toFixed(1)}px`
        button.classList.remove('has-leader')
      }
      if (placement) {
        const [cx, cy] = placement
        button.style.left = `${cx.toFixed(1)}px`
        button.style.top = `${cy.toFixed(1)}px`
        const leader = canOffset && labelLeader(label, cx, cy)
        button.classList.toggle('has-leader', Boolean(leader))
        if (leader) {
          leaders.push(leader)
          button.style.setProperty('--leader-x', `${leader.x - cx}px`)
          button.style.setProperty('--leader-y', `${leader.y - cy}px`)
          button.style.setProperty('--leader-width', `${Math.hypot(leader.dx, leader.dy)}px`)
          button.style.setProperty('--leader-angle', `${Math.atan2(leader.dy, leader.dx)}rad`)
        }
        occupied.push({ x: cx, y: cy, width: label.width, height: label.height })
        landmarkCaptions.push({ button, cx, cy, halfWidth, halfHeight })
      }
    }

    for (const label of terrainLabels) {
      const offsetY = width < 560 && label.id === 'plains' && camera.zoom < 1.7 ? 17 : 0
      const visible = state.labels && (!label.detail || camera.zoom > 1.5) &&
        position(label.point, label.element, offsetY)
      if (!visible) {
        label.element.hidden = true
        continue
      }
      const [x, y] = visible
      const labelWidth = label.name.length * (width < 560 ? 12 : 14) + 9
      const labelSpacing = width < 560 ? 17 : 23
      const nearHeading = y < 83 && x - labelWidth / 2 < (width < 560 ? 185 : 248)
      const nearScale = y > height - 60 && x + labelWidth / 2 > width - 124
      const collides = x - labelWidth / 2 < 6 || x + labelWidth / 2 > width - 6 ||
        y < 54 || y > height - 30 || nearHeading || nearScale ||
        occupied.some((other) => Math.abs(other.x - x) < (other.width + labelWidth) / 2 + 7 &&
          Math.abs(other.y - y) < Math.max(labelSpacing, (other.height ?? 18) / 2 + 11))
      label.element.hidden = collides && !label.island
      label.element.classList.toggle('hide-island-name', Boolean(label.island && (collides || camera.zoom < 1.6)))
      if (!collides && (!label.island || camera.zoom >= 1.6)) occupied.push({ x, y, width: labelWidth })
    }

    updateRoadShields(occupied)
    origin.copy(controls.target).project(camera)
    const [lon, lat] = terrain.worldToGeo(controls.target.x, controls.target.z)
    const [northX, northZ] = terrain.geoToWorld(lon, Math.min(lat + 0.15, 89.9))
    northDirection.set(northX, controls.target.y, northZ)
    north.copy(northDirection).project(camera)
    const angle = Math.atan2((north.x - origin.x) * width, (north.y - origin.y) * height)
    overlays.compass.style.transform = `rotate(${Number.isFinite(angle) ? angle : 0}rad)`

    const viewWidth = (camera.right - camera.left) / camera.zoom
    const viewKilometers = viewWidth * SCENE_UNIT_METERS / 1000
    const ideal = 82 / width * viewKilometers
    const unit = 10 ** Math.floor(Math.log10(ideal))
    const distance = [1, 2, 5, 10].map((amount) => amount * unit)
      .reduce((closest, amount) => Math.abs(amount - ideal) < Math.abs(closest - ideal) ? amount : closest)
    overlays.scaleLine.style.width = `${distance / viewKilometers * width}px`
    overlays.scaleText.textContent = `${distance} km`
  }

  function invalidate() {
    sceneChanged = true
    requestFrame()
  }

  function requestFrame() {
    if (!frame && !disposed && contextAvailable && inViewport && !document.hidden) frame = requestAnimationFrame(render)
  }

  function render(time) {
    frame = 0
    if (transition) {
      const factor = Math.min(1, (time - transition.started) / 460)
      const eased = 1 - (1 - factor) ** 3
      controls.target.lerpVectors(transition.fromTarget, transition.target, eased)
      camera.position.lerpVectors(transition.fromCamera, transition.position, eased)
      camera.zoom = THREE.MathUtils.lerp(transition.fromZoom, transition.zoom, eased)
      camera.updateProjectionMatrix()
      if (factor === 1) transition = null
      else invalidate()
    }
    controls.update()
    if (sceneChanged) {
      sceneChanged = false
      surface.update(camera, width, controls.target)
      roads.update(camera, width, height)
      const routeObstacles = routeLayer.update(camera, width, height, routeFramed, showDifference, roads.group.visible)
      const routeDistance = routeLayer.track?.compact ? (x, y) => routeLayer.lineDistance(camera, width, height, x, y) : null
      const visibleLandmarks = landmarks.update(camera, width, height, {
        routeDistance, destinationId: destinationLandmarkId, focusedId: focusedLandmark, searchedId: searchedLandmarkId,
        overview: routeLayer.overview, filter: landmarkFilter,
      })
      updateOverlays(visibleLandmarks, routeObstacles)
      landmarks.group.updateMatrixWorld()
      tooltip.refresh()
    }
    if (vehicles.update(time, camera, height, routeLayer.group.position.y, routeLayer.overview)) requestFrame()
    // When a vehicle passes below a DOM caption, let its silhouette show through.
    const vehicle = vehicles.group
    if (vehicle.visible) projected.copy(vehicle.position).project(camera)
    const vx = (1 + projected.x) * width / 2
    const vy = (1 - projected.y) * height / 2
    for (const { button, cx, cy, halfWidth, halfHeight } of landmarkCaptions) {
      button.classList.toggle('over-route-vehicle', vehicle.visible &&
        Math.abs(vx - cx) < halfWidth + 12 && Math.abs(vy - cy) < halfHeight + 13)
    }
    renderer.render(scene, camera)
    // A screen-sized landmark spans many kilometres in this view. Keep its real anchor
    // and let its own geometry resolve depth without clipping its base against distant terrain.
    renderer.autoClear = false
    landmarks.renderHighlight(camera, width, height)
    renderer.clearDepth()
    renderer.render(landmarkScene, camera)
    renderer.autoClear = true
  }

  function size() {
    width = Math.max(1, host.clientWidth)
    height = Math.max(1, host.clientHeight)
    const aspect = width / height
    const viewHeight = Math.max(40, 62 / aspect)
    camera.left = -viewHeight * aspect / 2
    camera.right = -camera.left
    camera.top = viewHeight / 2
    camera.bottom = -camera.top
    controls.minZoom = Math.min(0.72, 0.95 * viewHeight * aspect / terrainWidth, 0.95 * viewHeight / terrainDepth)
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
    updateZoomLimit(!routeFramed)
    if (routeFramed) fitRoute(Boolean(transition))
    invalidate()
  }

  function setView(target, direction, zoom, animate = true) {
    routeFramed = false
    const destination = target.clone().addScaledVector(direction, 82)
    if (animate && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      transition = {
        started: performance.now(), fromTarget: controls.target.clone(), fromCamera: camera.position.clone(),
        fromZoom: camera.zoom, target, position: destination, zoom,
      }
    } else {
      transition = null
      controls.target.copy(target)
      camera.position.copy(destination)
      camera.zoom = zoom
      camera.updateProjectionMatrix()
      controls.update()
    }
    invalidate()
  }

  function currentDirection() {
    return range.copy(camera.position).sub(controls.target).normalize()
  }

  function updateZoomLimit(preserveZoom = false) {
    const track = showDifference ? differenceFrame : routeLayer.track
    // A smaller viewport needs more zoom to put the same real separation on screen in CSS pixels.
    let limit = track ? routeZoomLimit(track, camera, width, showDifference) : MAP_MAX_ZOOM * Math.max(1, 540 / width)
    if (roads.group.visible) {
      // Street-level data is available down to z14. Express the manual zoom limit in metres per CSS pixel.
      limit = Math.max(limit, (camera.right - camera.left) * SCENE_UNIT_METERS / (width * 8))
    }
    controls.maxZoom = preserveZoom ? Math.max(limit, camera.zoom, transition?.zoom ?? 0) : limit
    if (transition) transition.zoom = Math.min(transition.zoom, controls.maxZoom)
  }

  function fitRoute(animate = true) {
    const track = showDifference ? differenceFrame : routeLayer.track
    if (!track) return
    const { target, zoom } = frameTerrainRoute(track, camera, HOME,
      width, height, controls.minZoom, Math.min(controls.maxZoom, routeZoomLimit(track, camera, width, showDifference)))
    setView(target, HOME, zoom, animate)
    routeFramed = true
  }

  function stopOrbitDamping() {
    // Consume residual motion while preserving the displayed pose.
    const position = camera.position.clone()
    const target = controls.target.clone()
    controls.enableDamping = false
    controls.update()
    controls.enableDamping = true
    camera.position.copy(position)
    controls.target.copy(target)
    controls.update()
  }

  function setRoute(route, { fit = true, focusCoordinates, stationMarkers, previewFlights = false } = {}) {
    differenceFrame = route && buildRouteFocus(terrain, focusCoordinates)
    showDifference = Boolean(!fit && differenceFrame && showDifference)
    callbacks.onDifferenceView?.(showDifference)
    const track = routeLayer.setRoute(route, stationMarkers, Boolean(differenceFrame), previewFlights)
    vehicles.setRoute(route, track?.drawings, previewFlights)
    if (routeFramed || !fit) clearTransition()
    updateZoomLimit(!fit)
    if (!fit) stopOrbitDamping()
    if (track && fit) fitRoute()
    else invalidate()
    return Boolean(track)
  }

  function clearSelection() {
    selection = null
    callbacks.onSelect(null)
    invalidate()
  }

  function setSelection(lon, lat, name, allowWater = false) {
    const [x, z] = terrain.geoToWorld(lon, lat)
    const point = terrain.sample(x, z)
    const hasElevation = point?.land && point.valid
    if (!point || (!allowWater && !hasElevation)) {
      clearSelection()
      return null
    }
    selection = new THREE.Vector3(x, (hasElevation ? point.elevation * METERS_TO_HEIGHT : 0) + 0.055, z)
    callbacks.onSelect({ lon, lat, elevation: hasElevation ? Math.round(point.elevation) : null, name })
    invalidate()
    return selection
  }

  function expandCity(memberIds) {
    const view = landmarks.expansionView(memberIds, camera, width, height, Math.max(MAP_MAX_ZOOM, controls.maxZoom))
    if (!view) return
    expandedMembers = new Set(memberIds)
    stopOrbitDamping()
    controls.maxZoom = Math.max(controls.maxZoom, view.zoom)
    setView(view.point, view.direction, view.zoom)
  }

  function setDestinationLandmark(id) {
    destinationLandmarkId = id ?? null
    invalidate()
  }

  function setLandmarkFilter(filter, searchedId) {
    if (landmarkFilter.types !== filter.types || landmarkFilter.tiers !== filter.tiers) expandedMembers.clear()
    landmarkFilter = filter
    searchedLandmarkId = searchedId
    invalidate()
  }

  function command(action, payload) {
    if (['fit-route', 'fit-difference', 'reset', 'top', 'focus', 'focus-place', 'focus-landmark'].includes(action)) {
      expandedMembers.clear()
      showDifference = Boolean(action === 'fit-difference' && differenceFrame)
      callbacks.onDifferenceView?.(showDifference)
      updateZoomLimit()
    }
    if (action === 'reset') {
      focusedLandmark = null
      landmarks.resetTurns()
      setView(homeCenter, HOME, 1)
    } else if (action === 'fit-route' || action === 'fit-difference') {
      fitRoute()
    } else if (action === 'top') {
      setView(homeCenter, TOP, 0.96)
    } else if (action === 'zoom-in' || action === 'zoom-out') {
      const direction = currentDirection().clone()
      const zoom = THREE.MathUtils.clamp(
        (transition?.zoom ?? camera.zoom) * (action === 'zoom-in' ? 1.35 : 1 / 1.35),
        controls.minZoom, controls.maxZoom,
      )
      setView(controls.target.clone(), direction, zoom)
    } else if (action === 'focus') {
      const point = setSelection(payload.lon, payload.lat, payload.name)
      if (point) setView(point, HOME, width < 520 ? 3.25 : 2.75)
    } else if (action === 'focus-place') {
      focusedLandmark = null
      const point = setSelection(payload.lon, payload.lat, payload.name, true)
      const zoom = payload.kind === 'city' ? (width < 520 ? 18 : 14) : (width < 520 ? 3.25 : 2.75)
      if (point) {
        stopOrbitDamping()
        setView(point, HOME, Math.min(zoom, controls.maxZoom))
      }
    } else if (action === 'focus-landmark') {
      focusedLandmark = payload?.id
      const fromSearch = focusedLandmark && focusedLandmark === searchedLandmarkId
      if (fromSearch) {
        clearSelection()
        stopOrbitDamping()
        controls.maxZoom = Math.max(controls.maxZoom, MAP_MAX_ZOOM)
      }
      const target = landmarks.focus(focusedLandmark, width < 520 ? 4 : 3.6,
        (camera.top - camera.bottom) / height, controls.maxZoom)
      if (target) {
        const point = target.point.clone()
        const detail = host.parentElement.querySelector('.map-landmark-detail')
        if (detail && !matchMedia('(max-width: 560px)').matches) {
          const unitsPerPixel = (camera.top - camera.bottom) / (height * target.zoom)
          const aimX = Math.max(width / 2, detail.offsetLeft + detail.offsetWidth + 68)
          point.addScaledVector(homeRight, (width / 2 - aimX) * unitsPerPixel)
        }
        setView(point, HOME, target.zoom)
      }
    } else if (action === 'clear') {
      clearSelection()
    }
  }

  function setLayers(next) {
    const changed = state.basemap !== next.basemap
    state = next
    if (changed) {
      const roadMode = state.basemap === 'roads'
      scene.background.copy(surface.setRoadMode(roadMode))
      roads.setEnabled(roadMode)
      updateZoomLimit(true)
    }
    provinces.visible = state.provinces
    section.visible = state.profile
    if (!state.profile) profilePoint = null
    invalidate()
  }

  function markProfile(longitude) {
    if (longitude == null || !state.profile) {
      profilePoint = null
    } else {
      const [x, z] = terrain.geoToWorld(longitude, profile.latitude)
      const point = terrain.sample(x, z)
      profilePoint = point ? new THREE.Vector3(x, point.elevation * METERS_TO_HEIGHT + 0.065, z) : null
    }
    invalidate()
  }

  function handleKey(event) {
    const landmarkId = event.target.dataset.landmarkId
    if (landmarkId && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
      event.preventDefault()
      landmarks.turn(landmarkId, (event.key === 'ArrowLeft' ? -1 : 1) * Math.PI / 12)
      return
    }
    if (event.target !== canvas) return
    const action = { '+': 'zoom-in', '=': 'zoom-in', '-': 'zoom-out', '0': 'reset' }[event.key]
    if (action) {
      event.preventDefault()
      command(action)
    }
  }

  let down = null
  const pointers = new Set()

  function aimAt(event) {
    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left, y = event.clientY - rect.top
    pointer.set(x / rect.width * 2 - 1, 1 - y / rect.height * 2)
    raycaster.setFromCamera(pointer, camera)
    return { x, y }
  }

  function releaseGesture() {
    down = null
    controls.enableRotate = true
  }

  function pointerDown(event) {
    if (event.button === 1) event.preventDefault() // Suppress the browser's native autoscroll.
    if (event.target !== canvas) return
    pointers.add(event.pointerId)
    if (event.pointerType === 'touch') canvas.classList.add('has-touch')
    if (pointers.size > 1) {
      // OrbitControls has tracked both touch positions and can start its normal pinch/pan.
      releaseGesture()
      return
    }
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey) return
    aimAt(event)
    const landmark = landmarks.pick(raycaster)
    down = { id: event.pointerId, x: event.clientX, y: event.clientY, lastX: event.clientX, dragged: false, landmark }
    if (landmark) {
      transition = null
      stopOrbitDamping()
      controls.enableRotate = false
    }
  }

  function pointerMove(event) {
    if (down?.id !== event.pointerId) return
    const { clientX, clientY } = event
    if (!down.dragged && Math.hypot(clientX - down.x, clientY - down.y) <= DRAG_THRESHOLD) return
    down.dragged = true
    if (down.landmark) landmarks.turn(down.landmark.id, (clientX - down.lastX) * MODEL_TURN_PER_PIXEL)
    down.lastX = clientX
  }

  function pointerUp(event) {
    pointers.delete(event.pointerId)
    if (!pointers.size) canvas.classList.remove('has-touch')
    if (down?.id !== event.pointerId) return
    const start = down
    releaseGesture()
    if (start.dragged || Math.hypot(event.clientX - start.x, event.clientY - start.y) > DRAG_THRESHOLD) return
    if (start.landmark) {
      landmarks.activate(start.landmark.id)
      return
    }
    aimAt(event)
    for (const { point } of raycaster.intersectObject(surface.mesh)) {
      const sample = terrain.sample(point.x, point.z)
      if (sample?.land && sample.valid) {
        setSelection(...terrain.worldToGeo(point.x, point.z))
        return
      }
    }
    command('clear')
  }

  function pointerCancel(event) {
    pointers.delete(event.pointerId)
    if (!pointers.size) canvas.classList.remove('has-touch')
    if (down?.id === event.pointerId) releaseGesture()
  }

  function clearTransition() {
    transition = null
    routeFramed = false
  }

  function contextLost(event) {
    event.preventDefault()
    contextAvailable = false
    refreshVisibility()
    callbacks.onContextLost()
  }

  function contextRestored() {
    contextAvailable = true
    landmarks.invalidateShadows()
    callbacks.onContextRestored()
    invalidate()
  }

  controls.addEventListener('change', invalidate)
  controls.addEventListener('start', clearTransition)
  host.addEventListener('keydown', handleKey)
  host.addEventListener('pointerdown', pointerDown, true)
  host.addEventListener('pointermove', pointerMove)
  host.addEventListener('pointerup', pointerUp)
  host.addEventListener('pointercancel', pointerCancel)
  host.addEventListener('lostpointercapture', pointerCancel)
  canvas.addEventListener('webglcontextlost', contextLost)
  canvas.addEventListener('webglcontextrestored', contextRestored)

  function refreshVisibility() {
    cancelAnimationFrame(frame)
    frame = 0
    vehicles.resetClock()
    invalidate()
  }
  const visibility = new IntersectionObserver(([entry]) => {
    inViewport = entry.isIntersecting
    refreshVisibility()
  })
  visibility.observe(host)
  document.addEventListener('visibilitychange', refreshVisibility)

  const sizing = new ResizeObserver(size)
  sizing.observe(host)
  size()
  setView(homeCenter, HOME, 1, false)

  return {
    command, setLayers, markProfile, setRoute, setDestinationLandmark, setLandmarkFilter, refreshOverlays: invalidate,
    togglePlayback: vehicles.toggle,
    dispose() {
      disposed = true
      cancelAnimationFrame(frame)
      sizing.disconnect()
      visibility.disconnect()
      document.removeEventListener('visibilitychange', refreshVisibility)
      canvas.removeEventListener('webglcontextlost', contextLost)
      canvas.removeEventListener('webglcontextrestored', contextRestored)
      host.removeEventListener('keydown', handleKey)
      host.removeEventListener('pointerdown', pointerDown, true)
      host.removeEventListener('pointermove', pointerMove)
      host.removeEventListener('pointerup', pointerUp)
      host.removeEventListener('pointercancel', pointerCancel)
      host.removeEventListener('lostpointercapture', pointerCancel)
      controls.dispose()
      tooltip.dispose()
      scene.remove(surface.mesh)
      surface.dispose()
      roads.group.removeFromParent()
      roads.dispose()
      for (const node of shieldNodes) node.remove()
      scene.remove(routeLayer.group)
      routeLayer.dispose()
      vehicles.group.removeFromParent()
      vehicles.dispose()
      landmarkScene.remove(landmarks.group)
      scene.remove(landmarks.shadows)
      landmarks.dispose()
      scene.traverse((item) => {
        item.geometry?.dispose()
        item.material?.dispose()
      })
      renderer.dispose()
      canvas.remove()
    },
  }
}
