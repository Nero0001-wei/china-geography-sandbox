import assert from 'node:assert/strict'
import test from 'node:test'
import { OrthographicCamera, Vector3 } from 'three'
import { buildRouteFocus, buildTerrainRoute, canPreviewFlight, createRouteLayer, frameTerrainRoute, routeZoomLimit } from './route-layer.js'
import { createVehicleJourney } from './vehicle-journey.js'

const terrain = {
  metadata: { width: 21, height: 21, bounds: { minX: -1e6, maxX: 1e6, minY: -1e6, maxY: 1e6 } },
  geoToWorld: (lon, lat) => [lon - 118, lat - 30],
  gridPoint: (x, z) => [x + 10, z + 10],
  sample: () => ({ elevation: 0 }),
}
const start = { location: [118, 30] }
const end = { location: [122, 31] }
const schematic = { type: 'rail', schematic: true, geometry: [start.location, end.location] }

test('preserves small bends of long drives for street-scale viewing', () => {
  const bend = [119, 30.0004]
  const route = buildTerrainRoute(terrain, { mode: 'driving', geometry: [start.location, bend, [120, 30]] })
  assert.ok(route.positions.some((value, index) => index % 3 === 0 && value === 1 &&
    Math.abs(route.positions[index + 2] - 0.0004) < 1e-9))
})

function makeTestLayer(t) {
  const originalDocument = globalThis.document
  const context = { beginPath() {}, arc() {}, roundRect() {}, fill() {}, fillText() {}, measureText: () => ({ width: 45 }) }
  globalThis.document = { createElement: () => ({ getContext: () => context }) }
  t.after(() => {
    if (originalDocument === undefined) delete globalThis.document
    else globalThis.document = originalDocument
  })
  const layer = createRouteLayer(terrain)
  t.after(() => layer.dispose())
  return layer
}

test('road zoom lowers routes, station dots and their screen-space obstacles together', t => {
  const layer = makeTestLayer(t)
  const width = 1000, height = 800
  const camera = new OrthographicCamera(-25, 25, 20, -20, 0.1, 300)
  camera.position.set(0, 60, 60)
  camera.lookAt(0, 0, 0)
  camera.zoom = 500
  camera.updateProjectionMatrix()
  camera.updateMatrixWorld()
  const station = { name: '测试站', location: [118.03, 30] }
  const track = layer.setRoute({ mode: 'driving', start, geometry: [start.location, [120, 30]] }, [station])
  const snapshot = track.positions.slice()
  const boxes = layer.update(camera, width, height, true, true, true)
  const anchor = track.anchors[0].clone().add(layer.group.position)
  assert.ok(Math.abs(anchor.y - 0.0006) < 1e-10)
  function screen(point) {
    point.project(camera)
    return [(point.x + 1) * width / 2, (1 - point.y) * height / 2]
  }
  const [x, y] = screen(anchor.clone())
  assert.ok(layer.lineDistance(camera, width, height, x + 10, y) < 1e-8)
  const badge = boxes.find(box => box.width === 27)
  assert.equal(badge.x, x)
  assert.equal(badge.y, y)
  const dot = boxes.find(box => box.width === 12)
  const [sx, sy] = screen(new Vector3(118.03 - 118, anchor.y, 0))
  assert.ok(Math.hypot(dot.x - sx, dot.y - sy) < 1e-8)
  layer.update(camera, width, height)
  assert.equal(layer.group.position.y, 0)
  assert.deepEqual(track.positions, snapshot)
  assert.ok(layer.lineDistance(camera, width, height, x + 10, y) > 10)
})

test('overview follows drawable loop geometry through zoom and clears for marker-only routes', t => {
  const layer = makeTestLayer(t)
  const width = 1000, height = 800
  const camera = new OrthographicCamera(-25, 25, 20, -20, 0.1, 300)
  camera.position.set(0, 60, 60)
  camera.lookAt(0, 0, 0)
  camera.updateMatrixWorld()
  const loop = { type: 'rail', geometry: [start.location, [126, 30], [126, 32], start.location] }
  const route = { mode: 'transit', start, end: start, segments: [loop] }
  layer.setRoute(route)
  layer.update(camera, width, height)
  assert.equal(layer.overview, null) // The loop is 160 px wide despite its coincident endpoints.

  camera.zoom = 0.5
  camera.updateProjectionMatrix()
  const badges = layer.update(camera, width, height)
  const { x, width: spanX, span } = layer.overview
  assert.equal(Math.round(spanX), 80)
  assert.equal(Math.round(x), 540)
  assert.equal(span, spanX)
  assert.equal(badges.length, 2)
  assert.ok(badges.every(badge => badge.width >= 21 && badge.width < 27))
  assert.ok(badges[1].x - badges[0].x >= badges[0].width + 4.99)
  assert.ok(badges[0].x < width / 2 && badges[1].x > width / 2)

  layer.setRoute({ ...route, end, segments: [schematic] })
  assert.equal(layer.overview, null)
  assert.equal(layer.update(camera, width, height).length, 2)
  assert.equal(layer.overview, null)
  layer.setRoute(null)
  assert.deepEqual(layer.update(camera, width, height), [])
  assert.equal(layer.overview, null)
})

test('transit draws each available track through its bends and leaves a gap between legs', () => {
  const metro = { type: 'metro', geometry: [start.location, [119, 31], [120, 30]] }
  const walk = { type: 'walk', geometry: [[121, 31], end.location] }
  const result = buildTerrainRoute(terrain, {
    mode: 'transit', start, end, segments: [metro, schematic, walk], geometry: [start.location, end.location],
  })
  assert.deepEqual(result.drawings.map(part => part.type), ['metro', 'walk'])
  assert.deepEqual(result.drawings.map(part => part.segmentIndex), [0, 2])
  const metroPositions = result.drawings[0].positions
  assert.ok(metroPositions.some((x, i) => i % 3 === 0 && x === 1 && metroPositions[i + 2] === 1))
  assert.equal(metroPositions.at(-3), 2)
  assert.equal(result.drawings[1].positions[0], 3)
})

test('flight preview is opt-in and uses only validated airport locations', () => {
  const flight = { type: 'flight', name: '航班待确认', unconfirmed: true, geometry: [], from: start, to: end }
  const route = { mode: 'transit', start, end, segments: [schematic, flight] }
  assert.deepEqual(buildTerrainRoute(terrain, route).drawings, [])
  const track = buildTerrainRoute(terrain, route, false, true)
  assert.equal(track.drawings.length, 1)
  const [line] = track.drawings
  assert.equal(line.segmentIndex, 1)
  assert.equal(line.airportPreview, true)
  assert.deepEqual(line.positions.slice(0, 3), [0, track.clearance, 0])
  assert.deepEqual(line.positions.slice(-3), [4, track.clearance, 1])
  assert.ok(line.positions.some((value, i) => i % 3 === 1 && value > track.clearance + 0.4))
  assert.deepEqual(createVehicleJourney(route, track.drawings).vehicles, ['plane'])
  assert.equal(buildTerrainRoute(terrain, { ...route, segments: [{ ...flight, to: { location: [139, 55] } }] }, false, true).drawings.length, 0)
  assert.equal(canPreviewFlight({ ...flight, to: start }), false)
  assert.equal(canPreviewFlight({ ...flight, from: { location: [NaN, 30] } }), false)
  assert.equal(canPreviewFlight({ ...flight, type: 'rail' }), false)
  assert.equal(canPreviewFlight(flight, { start: { city: '上海市' }, end: { city: '上海市' } }), false)
  const confirmed = { ...flight, unconfirmed: false, geometry: [start.location, end.location] }
  assert.equal(canPreviewFlight(confirmed), false)
  assert.equal(buildTerrainRoute(terrain, { ...route, segments: [confirmed] }, false, true).drawings[0].airportPreview, false)
})

test('a transit itinerary with only stop coordinates still shows both endpoint markers', () => {
  for (const segments of [[schematic], [], undefined]) {
    const result = buildTerrainRoute(terrain, { mode: 'transit', start, end, segments, geometry: [start.location, end.location] })
    assert.equal(result.anchors.filter(Boolean).length, 2)
    assert.equal(result.positions.length, 0)
  }
})

test('local framing uses the difference area and keeps the complete itinerary available for overview', () => {
  const camera = new OrthographicCamera(-30, 30, 20, -20)
  const direction = new Vector3(0, 1, 0.2).normalize()
  const route = buildTerrainRoute(terrain, { mode: 'transit', start, end, segments: [
    { type: 'rail', geometry: [start.location, end.location] },
  ] })
  const local = buildRouteFocus(terrain, [[122, 31], [121.9, 31.09], null])
  const overview = frameTerrainRoute(route, camera, direction, 960, 640, 1, routeZoomLimit(route, camera, 960))
  const detail = frameTerrainRoute(local, camera, direction, 960, 640, 1, routeZoomLimit(local, camera, 960, true))
  assert.ok(detail.zoom > overview.zoom * 5)
  assert.ok(Math.abs(detail.target.x - 3.95) < 0.01)
  assert.ok(Math.abs(overview.target.x - 2) < 0.01)
  assert.equal(buildRouteFocus(terrain, [[Infinity, 0]]), null)
})
