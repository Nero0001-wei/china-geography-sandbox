import assert from 'node:assert/strict'
import test from 'node:test'
import { vehicleDisplayPixels } from './vehicle-layer.js'

test('vehicle sizes leave short route lines visible and return smoothly to the usual model scale', () => {
  const expectedSizes = { car: 55.5, coach: 47, ferry: 51, train: 87, 'intercity-rail': 82.5, 'high-speed-rail': 87, plane: 104 }
  for (const [vehicle, usual] of Object.entries(expectedSizes)) {
    assert.equal(vehicleDisplayPixels(vehicle, null), usual)
    const size = span => vehicleDisplayPixels(vehicle, { span })
    assert.equal(size(12), 7)
    assert.equal(size(40), 10)
    assert.equal(size(80), 20)
    assert.ok(size(110) > size(80) && size(110) < usual)
    assert.ok(Math.abs(usual - size(139.9)) < 0.01)
    assert.equal(size(140), usual)
    assert.equal(size(400), usual)
  }
})
