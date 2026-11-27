import assert from 'node:assert/strict'
import test from 'node:test'
import { compareRouteGeometry } from './route-differences.js'

const rail = geometry => ({ type: 'rail', geometry })
const metro = geometry => ({ type: 'metro', geometry })
const trip = (...segments) => ({ mode: 'transit', segments })

test('bounds both Beijing approaches symmetrically and excludes the long shared railway', () => {
  const main = [[118.79, 32.09], [117.19, 34.29], [117.00, 36.68], [116.30, 39.85]]
  const beijing = [116.43, 39.90]
  const end = [116.40, 39.90]
  const first = trip(rail(main), metro([main.at(-1), [116.30, 39.91], end]))
  const second = trip(rail([...main, beijing]), metro([beijing, end]))
  const result = compareRouteGeometry(first, second)
  assert.equal(result.kind, 'local')
  assert.deepEqual(compareRouteGeometry(second, first), result)
  assert.equal(result.coordinates.length, 4)
  assert.ok(result.coordinates.every(([lon, lat]) => lon > 116.29 && lon < 116.44 && lat > 39.84 && lat < 39.92))
  assert.ok(result.coordinates.some(([lon]) => lon >= 116.4299))
})

test('a local street deviation remains detectable within a city', () => {
  const a = trip(metro([[116.30, 39.90], [116.40, 39.90]]))
  const b = trip(metro([[116.30, 39.90], [116.37, 39.90], [116.38, 39.903], [116.39, 39.90], [116.40, 39.90]]))
  const result = compareRouteGeometry(a, b)
  assert.equal(result.kind, 'local')
  assert.ok(result.coordinates.every(([lon]) => lon > 116.36 && lon < 116.40))
})

test('collinear samples and split segments of the same mode still trace the same line', () => {
  const a = trip(rail([[116, 39], [116.06, 39.03]]))
  const b = trip(rail([[116, 39], [116.02, 39.01]]), rail([[116.02, 39.01], [116.04, 39.02], [116.06, 39.03]]))
  assert.equal(compareRouteGeometry(a, b).kind, 'same')
  assert.equal(compareRouteGeometry(a, { ...b, segments: [...b.segments, metro([])] }).kind, 'overview')
  assert.equal(compareRouteGeometry(a, { mode: 'transit', geometry: a.segments[0].geometry }).kind, 'overview')
})

test('two different corridors and dispersed differences both keep the whole itinerary in view', () => {
  const a = trip(rail([[116, 39], [116.1, 39], [116.9, 39], [117, 39]]))
  const b = trip(rail([[116, 39.1], [116.1, 39.1], [116.9, 39.1], [117, 39.1]]))
  const c = trip(rail([[116, 39.01], [116.1, 39], [116.9, 39], [117, 39.01]]))
  assert.equal(compareRouteGeometry(a, b).kind, 'overview')
  assert.equal(compareRouteGeometry(a, c).kind, 'overview')
})
