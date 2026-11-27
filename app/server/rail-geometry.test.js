import assert from 'node:assert/strict'
import test from 'node:test'
import { lookupRailGeometry } from './rail-geometry.js'

const nanjing = { name: '南京南', location: '118.798034 31.968763' }
const west = { name: '黄山西', location: '118.089444 30.277519' }
const north = { name: '黄山北站', location: '118.273139 29.815110' }
const westTrain = { trip: 'G7207', distance: '286637', departure_stop: nanjing, arrival_stop: west }
const northTrain = { name: 'G8965(南京南-黄山北)', trip: [], distance: '307940', departure_stop: nanjing, arrival_stop: north }

test('two Nanjing services follow distinct mapped tracks through their verified station sequences', () => {
  for (const [train, via] of [[westTrain, [117.517, 30.622]], [northTrain, [118.769, 30.95]]]) {
    const line = lookupRailGeometry(train)
    assert.ok(line.length > 800)
    assert.ok(line.some(([lon, lat]) => Math.hypot(lon - via[0], lat - via[1]) < 0.007))
    assert.ok(line.every(([lon, lat]) => Number.isFinite(lon) && Number.isFinite(lat)))
  }
})

test('mismatched services, via stops, distance, direction and malformed provider fields leave a gap', () => {
  assert.ok(lookupRailGeometry({ ...westTrain, via_stops: [{ name: '芜湖' }, { name: '池州' }] }).length)
  for (const override of [
    { trip: 'G999' }, { trip: [], name: [] }, { distance: '200000' }, { distance: 'x' },
    { departure_stop: west, arrival_stop: nanjing }, { arrival_stop: north },
    { arrival_stop: { name: [], location: [] } }, { arrival_stop: { name: '黄山西', location: '120,30' } },
    { via_stops: [{ name: '宣城' }] }, { via_stops: [{ name: '池州' }, { name: '芜湖' }] },
  ]) assert.deepEqual(lookupRailGeometry({ ...westTrain, ...override }), [])
})

test('two Nanjing to Beijing plans follow the conventional railway to their distinct terminals', () => {
  const nanjing = { name: '南京站', location: [118.797487, 32.087006] }
  const fengtai = { name: '北京丰台站', location: [116.30150, 39.85107] }
  const beijing = { name: '北京站', location: [116.42734, 39.90277] }
  const z282 = { trip: 'Z282', departure_stop: nanjing, arrival_stop: fengtai, distance: 1116128 }
  const t110 = { trip: 'T110', departure_stop: nanjing, arrival_stop: beijing, distance: 1107627 }
  const line = lookupRailGeometry(z282)
  assert.ok(line.length > 1000)
  assert.ok(line.some(([lon, lat]) => Math.hypot(lon - 117.15712, lat - 39.15736) < 0.003)) // Tianjin West
  assert.ok(lookupRailGeometry(t110).length > line.length)
  assert.deepEqual(lookupRailGeometry({ ...t110, trip: 'N4' }), lookupRailGeometry(t110))
  assert.deepEqual(lookupRailGeometry({ ...z282, arrival_stop: beijing }), [])
  assert.deepEqual(lookupRailGeometry({ ...t110, via_stops: [{ name: '北京丰台' }] }), [])
})

test('verified southbound codes reuse only the interval between their booked stations', () => {
  const xuzhou = { name: '徐州', location: [117.2071, 34.2653] }
  const tianjin = { name: '天津西', location: [117.1632, 39.1579] }
  const section = { trip: 'T110', departure_stop: xuzhou, arrival_stop: tianjin, distance: 647336 }
  const northbound = lookupRailGeometry(section)
  const southbound = lookupRailGeometry({ ...section, trip: 'N3', departure_stop: tianjin, arrival_stop: xuzhou })
  assert.ok(northbound.length > 500)
  assert.deepEqual(southbound, [...northbound].reverse())
  assert.deepEqual(lookupRailGeometry({ ...section, trip: 'N3' }), [])
})

test('the shared Z240 leg to Sayram Lake follows its booked railway corridor in order', () => {
  const departure = { name: '南京站', location: '118.797510,32.087125' }
  const arrival = { name: '乌鲁木齐站', location: '87.528997,43.840272' }
  const railway = { trip: 'Z240', name: 'Z240(上海-乌鲁木齐)', departure_stop: departure, arrival_stop: arrival, distance: '3617478' }
  const track = lookupRailGeometry(railway)
  let cursor = -1
  for (const [x, y] of [[118.7923, 32.0892], [117.201, 34.27], [108.96, 34.28], [101.81, 36.62], [93.52, 42.85], [87.5260, 43.8390]]) {
    cursor = track.findIndex(([lon, lat], index) => index > cursor && Math.hypot(lon - x, lat - y) < 0.04)
    assert.ok(cursor >= 0, `missing rail corridor near ${x}, ${y}`)
  }
  assert.deepEqual(lookupRailGeometry({ ...railway, via_stops: [{ name: '西宁' }, { name: '哈密' }] }), track)
  assert.deepEqual(lookupRailGeometry({ ...railway, via_stops: [{ name: '武威' }] }), [])
  assert.deepEqual(lookupRailGeometry({ ...railway, distance: 2800000 }), [])
  assert.deepEqual(lookupRailGeometry({ ...railway, departure_stop: arrival, arrival_stop: departure }), [])
})
