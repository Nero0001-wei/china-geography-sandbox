import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { disposeModel } from './dispose-model.js'
import { createVehicleJourney, sampleVehicleJourney } from './vehicle-journey.js'

const displayPixels = {
  car: 55.5,
  coach: 47,
  ferry: 51,
  train: 87,
  'intercity-rail': 82.5,
  'high-speed-rail': 87,
  plane: 104,
}

export function vehicleDisplayPixels(vehicle, overview) {
  const fullSize = displayPixels[vehicle]
  if (!Number.isFinite(overview?.span)) return fullSize
  const span = overview.span
  const overviewSize = THREE.MathUtils.clamp(span / 4, 7, fullSize)
  // Restore the usual silhouette gradually as the route fills more of the map.
  return THREE.MathUtils.lerp(overviewSize, fullSize, THREE.MathUtils.smoothstep(span, 80, 140))
}

export function createVehicleLayer(invalidate, onPlayback) {
  const group = new THREE.Group()
  group.name = 'Route vehicle'
  group.visible = false
  const loader = new GLTFLoader()
  const assets = new Map()
  const motionPreference = matchMedia('(prefers-reduced-motion: reduce)')
  let playing = !motionPreference.matches
  let ready = false
  let journey = null
  let elapsed = 0
  let lastFrame = null
  let active = null
  let disposed = false

  function load(id) {
    if (assets.has(id)) return assets.get(id).pending
    const asset = { model: null }
    assets.set(id, asset)
    asset.pending = loader.loadAsync(import.meta.env.BASE_URL + 'models/vehicles/' + id + '.glb')
      .then(({ scene }) => {
        const bounds = new THREE.Box3().setFromObject(scene)
        if (disposed || bounds.isEmpty()) {
          disposeModel(scene)
          return
        }
        const size = bounds.getSize(new THREE.Vector3())
        const center = bounds.getCenter(new THREE.Vector3())
        const span = Math.max(size.x, size.y, size.z)
        scene.position.set(-center.x, -bounds.min.y, -center.z)
        const model = new THREE.Group()
        model.name = id
        model.visible = false
        model.add(scene)
        group.add(model)
        Object.assign(asset, { model, span })
      })
      .catch(error => {
        assets.delete(id)
        if (!disposed) console.warn('交通模型加载失败', id, error)
      })
    return asset.pending
  }

  function notify() {
    onPlayback?.({ available: ready, playing })
    invalidate()
  }

  function setRoute(route, drawings, startWithPlane) {
    const next = createVehicleJourney(route, drawings)
    journey = next
    ready = false
    elapsed = (startWithPlane && next?.runs.find(run => run.vehicle === 'plane')?.startSeconds) || 0
    lastFrame = null
    if (active) active.visible = false
    active = null
    group.visible = false
    notify()
    if (next) Promise.all(next.vehicles.map(load)).then(() => {
      if (disposed || next !== journey) return
      ready = next.vehicles.some(id => assets.get(id)?.model)
      notify()
    })
  }

  function toggle() {
    if (!ready) return
    playing = !playing
    lastFrame = null
    notify()
  }

  function preferenceChanged() {
    playing = !motionPreference.matches
    lastFrame = null
    notify()
  }
  motionPreference.addEventListener('change', preferenceChanged)

  function update(time, camera, viewportHeight, routeYOffset = 0, overview = null) {
    if (!ready) return false
    if (playing && lastFrame !== null) elapsed += Math.max(0, time - lastFrame) / 1000
    lastFrame = playing ? time : null
    const pose = sampleVehicleJourney(journey, elapsed)
    const asset = pose && assets.get(pose.vehicle)
    const model = asset?.model
    if (active !== model && active) active.visible = false
    active = model
    group.visible = Boolean(model)
    if (model) {
      const unit = (camera.top - camera.bottom) / (camera.zoom * viewportHeight)
      group.position.set(pose.x, pose.y + routeYOffset + (pose.vehicle === 'plane' ? 3 * unit : 0), pose.z)
      group.rotation.y = pose.heading
      model.visible = true
      model.scale.setScalar(vehicleDisplayPixels(pose.vehicle, overview) * unit / asset.span)
    }
    return playing
  }

  return {
    group, setRoute, toggle, update,
    resetClock() { lastFrame = null },
    dispose() {
      disposed = true
      motionPreference.removeEventListener('change', preferenceChanged)
      disposeModel(group)
      assets.clear()
    },
  }
}
