import assert from 'node:assert/strict'
import test from 'node:test'
import { OrthographicCamera, Vector3 } from 'three'
import { roadTileView } from './road-layer.js'
import { METERS_TO_HEIGHT } from './terrain-data.js'

test('detail requests follow the tilted camera on an elevated plateau and stay off at national scale', () => {
  const elevation = 3600
  const terrain = {
    metadata: { elevationRange: [-100, 6113] },
    sample: () => ({ elevation }),
    worldToGeo: (x, z) => [91 + x, 30 - z],
  }
  const camera = new OrthographicCamera(-33, 33, 22, -22, 0.1, 300)
  const center = new Vector3(0, elevation * METERS_TO_HEIGHT, 0)
  camera.position.copy(center).add(new Vector3(3, 75, 30))
  camera.lookAt(center)
  camera.updateMatrixWorld()
  assert.equal(roadTileView(terrain, camera, 1050), null)
  camera.zoom = 180
  camera.updateProjectionMatrix()
  const view = roadTileView(terrain, camera, 1050)
  assert.equal(view.zoom, 12)
  assert.ok(Math.abs(view.center[0] - 91) < 0.001 && Math.abs(view.center[1] - 30) < 0.001)
  const [west, south, east, north] = view.bounds
  assert.ok(west < view.center[0] && east > view.center[0] && south < view.center[1] && north > view.center[1])
})
