import assert from 'node:assert/strict'
import test from 'node:test'
import { createVehicleJourney, sameJourneyCity, sampleVehicleJourney, vehicleForSegment } from './vehicle-journey.js'

const road = [0, 0, 0, 3, 4, 0, 3, 4, 0, 3, 4, 15]
const drawing = (segmentIndex, positions = road) => ({ segmentIndex, positions })
const ride = (type, name) => ({ type, name })
const atFraction = (journey, index, fraction) => {
  const { startSeconds, endSeconds } = journey.runs[index]
  return sampleVehicleJourney(journey, startSeconds + fraction * (endSeconds - startSeconds))
}

test('uses the road mode and actual rail service number for the fleet', () => {
  for (const [type, name, expected] of [
    ['drive', '驾车', 'car'], ['taxi', '出租车', null], ['bus', '9路', null],
    ['bus', '98路（长途客运站—汽车东站）', null], ['bus', '城际巴士', 'coach'], ['coach', '宁扬线', 'coach'],
    ['ferry', '城际客轮', 'ferry'], ['ferry', '江心洲轮渡', null],
    ['metro', '地铁1号线', null], ['flight', 'MU5123', 'plane'],
    ['rail', 'Z282', 'train'], ['rail', 'T110（南京—北京）', 'train'], ['rail', 'K738', 'train'],
    ['rail', '列车 G35（北京南—南京南）', 'high-speed-rail'],
    ['rail', 'Ｄ２２８１', 'high-speed-rail'], ['rail', 'c123', 'intercity-rail'],
    ['rail', '高速动车', 'high-speed-rail'], ['high-speed-rail', '', 'high-speed-rail'],
    ['rail', '普快', 'train'], ['walk', '步行', null], ['transfer', '地面接驳', null],
  ]) {
    assert.equal(vehicleForSegment({ type, name }), expected, type + ' ' + name)
  }
  assert.equal(vehicleForSegment({ type: 'rail', trip: 'T110', name: 'G1' }), 'train')
})

test('legacy driving geometry follows each rendered edge by arc length, height and heading', () => {
  const journey = createVehicleJourney({ mode: 'driving' }, [drawing(0)])
  assert.deepEqual(atFraction(journey, 0, 0), { vehicle: 'car', x: 0, y: 0, z: 0, heading: Math.PI / 2 })
  assert.deepEqual(atFraction(journey, 0, 1 / 8), { vehicle: 'car', x: 1.5, y: 2, z: 0, heading: Math.PI / 2 })
  const bend = atFraction(journey, 0, 1 / 4)
  assert.deepEqual([bend.x, bend.y, bend.z], [3, 4, 0])
  assert.ok(Math.abs(bend.heading - Math.atan2(0.6, 1)) < 1e-8)
  assert.deepEqual(atFraction(journey, 0, 1 / 2), { vehicle: 'car', x: 3, y: 4, z: 5, heading: 0 })
  assert.equal(sampleVehicleJourney(journey, journey.durationSeconds - 0.01), null)
  assert.deepEqual(sampleVehicleJourney(journey, journey.durationSeconds), atFraction(journey, 0, 0))
})

test('suppresses walking, unavailable tracks and schematic/unconfirmed legs between visible rides', () => {
  const segments = [ride('walk'), ride('coach'), ride('bus'), ride('walk'),
    { ...ride('rail', 'G35'), unconfirmed: true }, { ...ride('flight'), schematic: true },
    { ...ride('taxi'), unavailable: true }, ride('rail', 'T110'), ride('taxi')]
  const drawings = segments.flatMap((_, i) => i === 2 ? [] : [drawing(i)])
  const journey = createVehicleJourney({ mode: 'transit', segments }, drawings)
  assert.deepEqual(journey.runs.map(part => part.vehicle), ['coach', 'train'])
  assert.equal(sampleVehicleJourney(journey, 0).vehicle, 'coach')
  assert.equal(sampleVehicleJourney(journey, journey.runs[0].endSeconds), null)
  assert.equal(atFraction(journey, 1, 0).vehicle, 'train')
})

test('does not bridge disjoint pairs inside a single clipped polyline', () => {
  const positions = new Float32Array([0, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 10, 3, 7, 11, 3, 7])
  const journey = createVehicleJourney({ segments: [ride('coach')] }, [drawing(0, positions)])
  assert.equal(journey.runs.length, 2)
  assert.equal(atFraction(journey, 0, 0.5).x, 0.5)
  assert.equal(atFraction(journey, 1, 0.5).x, 10.5)
  assert.equal(sampleVehicleJourney(journey, (journey.runs[0].endSeconds + journey.runs[1].startSeconds) / 2), null)
})

test('changes vehicles at a shared stop without pausing for a nonexistent gap', () => {
  const journey = createVehicleJourney({ segments: [ride('coach'), ride('flight')] }, [
    drawing(0, [0, 0, 0, 2, 1, 0]), drawing(1, [2, 1, 0, 0, 2, 0]),
  ])
  assert.equal(journey.runs[0].endSeconds, journey.runs[1].startSeconds)
  assert.deepEqual(atFraction(journey, 1, 0), { vehicle: 'plane', x: 2, y: 1, z: 0, heading: -Math.PI / 2 })
})

test('keeps city-wide driving and individual local transfers off the vehicle timeline', () => {
  const start = { city: '北京市', adcode: '110101' }
  const end = { city: '北京市', adcode: '110229' }
  assert.equal(createVehicleJourney({ mode: 'driving', start, end }, [drawing(0)]), null)
  assert.equal(vehicleForSegment({ type: 'rail', name: 'G35', from: start, to: end }), null)
  assert.equal(vehicleForSegment({ type: 'coach', localTransfer: true }), null)
  assert.equal(sameJourneyCity({ adcode: '320106' }, { adcode: '320115' }), true)
  assert.equal(sameJourneyCity({ adcode: '469001' }, { adcode: '469002' }), false)
  assert.equal(sameJourneyCity({}, { city: '南京' }), null)
  assert.equal(sameJourneyCity({ city: '南京市' }, { city: '南京' }), true)
})

test('only plays ferries with evidence that the sailing crosses cities', () => {
  const start = { city: '烟台市', location: [121.44, 37.46] }
  const end = { city: '大连市', location: [121.62, 38.91] }
  const route = { start, end }
  const sailing = { type: 'ferry', name: '客运轮渡' }
  assert.equal(vehicleForSegment({ ...sailing, from: start, to: end }), 'ferry')
  assert.equal(vehicleForSegment({ ...sailing, name: '烟台大连客轮' }, route), 'ferry')
  const from = { location: [121.4, 37.5] }
  assert.equal(vehicleForSegment({ ...sailing, from, to: { location: [121.61, 38.94] } }, route), 'ferry')
  assert.equal(vehicleForSegment({ ...sailing, from, to: { location: [121.46, 37.53] } }, route), null)
})

test('requires a valid drawing and never interprets a transit overview as a drive', () => {
  const fakeOverview = { geometry: [[118, 33], [120, 40]] }
  assert.equal(createVehicleJourney({ mode: 'transit', ...fakeOverview }, [drawing(0)]), null)
  assert.equal(createVehicleJourney({ segments: [ride('walk')] }, [drawing(0)]), null)
  assert.equal(createVehicleJourney({ segments: [ride('rail', 'Z282')] }, []), null)
  assert.equal(createVehicleJourney({ mode: 'driving' }, [drawing(0, [1, 1, 1, 1, 1, 1])]), null)
  assert.equal(sampleVehicleJourney(null, 0), null)
})

test('only the explicit airport preview permits a schematic or unconfirmed flight', () => {
  const flight = { ...ride('flight'), unconfirmed: true, geometry: [] }
  const rail = { ...ride('rail', 'G35'), unconfirmed: true, geometry: [] }
  const route = { segments: [flight, rail, flight] }
  assert.equal(createVehicleJourney(route, [drawing(0)]), null)
  const journey = createVehicleJourney(route, route.segments.map((_, index) => ({
    ...drawing(index), airportPreview: true,
  })))
  assert.deepEqual(journey.vehicles, ['plane'])
  assert.deepEqual(journey.runs.map(run => run.segmentIndex), [0, 2])
})
