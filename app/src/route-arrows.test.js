import assert from 'node:assert/strict'
import test from 'node:test'
import { OrthographicCamera } from 'three'
import { createRouteArrows } from './route-arrows.js'

function scene(t) {
  const layer = createRouteArrows()
  t.after(() => layer.dispose())
  const camera = new OrthographicCamera(-100, 100, 50, -50, 0.1, 500)
  camera.position.z = 100
  camera.updateMatrixWorld()
  function glyphs() {
    layer.update(camera, 200, 100, 0)
    if (!layer.mesh.visible) return []
    const { attributes, drawRange } = layer.mesh.geometry
    const points = []
    for (let i = 0; i < drawRange.count; i += 6) {
      const x = j => attributes.position.getX(i + j) * 100
      const y = j => attributes.position.getY(i + j) * 50
      points.push({ x: x(0), y: y(0), dx: x(0) - x(2), dy: y(0) - y(2), width: Math.hypot(x(1) - x(4), y(1) - y(4)) })
    }
    return points
  }
  return { layer, camera, glyphs }
}

test('arrows follow travel through bends, rotate with the view and retain their pixel spacing', t => {
  const { layer, camera, glyphs } = scene(t)
  layer.setDrawings([{ positions: [-70, -30, 0, 30, -30, 0, 30, -30, 0, 30, 50, 0] }])
  const initial = glyphs()
  assert.ok(initial.some(p => p.dx > 0 && p.dy === 0))
  assert.ok(initial.some(p => p.dy > 0 && p.dx === 0))
  camera.rotation.z = Math.PI
  camera.updateMatrixWorld()
  assert.ok(glyphs().some(p => p.dx < 0 && Math.abs(p.dy) < 1e-5))
  camera.zoom = 4
  camera.rotation.z = 0
  camera.updateProjectionMatrix()
  camera.updateMatrixWorld()
  layer.setDrawings([{ positions: [5000, 0, 0, -5000, 0, 0] }])
  const zoomed = glyphs()
  assert.ok(zoomed.length >= 3 && zoomed.length <= 6)
  assert.ok(zoomed.every(p => p.dx < 0 && Math.abs(p.width - initial[0].width) < 1e-4))
  assert.ok(Math.abs(zoomed[0].x - zoomed[1].x - (initial[1].x - initial[0].x)) < 1e-4)
})

test('arrows skip gaps, short disconnected tracks and unconfirmed flight previews', t => {
  const { layer, glyphs } = scene(t)
  layer.setDrawings([
    { positions: [-80, 0, 0, -30, 0, 0, 30, 0, 0, 80, 0, 0] },
    { positions: [-80, 5, 0, -68, 5, 0, 20, 5, 0, 32, 5, 0] },
    { positions: [-80, 10, 0, 80, 10, 0], airportPreview: true },
  ])
  const marks = glyphs()
  assert.equal(marks.length, 2)
  assert.ok(marks.every(p => p.y === 0 && Math.abs(p.x) > 30))
  layer.setDrawings([])
  assert.deepEqual(glyphs(), [])
})
