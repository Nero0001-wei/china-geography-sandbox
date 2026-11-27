import assert from 'node:assert/strict'
import test from 'node:test'
import { enrichNetworkRailRoutes } from './network-rail.js'

const points = [[118, 32], [118, 32.2], [118.12, 32.2], [118.12, 32.33]]
const length = 47781
const leg = () => ({
  type: 'rail', name: 'G35', from: { name: '甲', location: points[0] },
  to: { name: '乙', location: points.at(-1) }, distanceMeters: length, geometry: [],
})
function response(coords = points, tags = 'railway=rail', distance = length) {
  return Response.json({ features: [{ geometry: { type: 'LineString', coordinates: coords },
    properties: { messages: [['WayTags'], [tags]], 'track-length': distance } }] })
}
const route = segment => ({ segments: [segment] })

test('rail fallback sends only public station coordinates, shares results and checks each service distance', async () => {
  let count = 0
  const server = async url => {
    count++
    assert.equal(url.hostname, 'brouter.de')
    assert.deepEqual([...url.searchParams.keys()].sort(), ['alternativeidx','format','lonlats','profile'])
    assert.equal(url.searchParams.get('profile'), 'rail')
    assert.equal(url.searchParams.get('lonlats'), '118.000000,32.000000|118.120000,32.330000')
    return response()
  }
  const a = route(leg()), b = route({ ...leg(), distanceMeters: length * 1.4 }), c = route(leg())
  await Promise.all([enrichNetworkRailRoutes([a, b], { fetcher: server }), enrichNetworkRailRoutes([c], { fetcher: server })])
  assert.equal(count, 1)
  assert.equal(a.segments[0].geometrySource, 'rail-network')
  assert.deepEqual(c.segments[0].geometry, points)
  assert.deepEqual(a.geometry, points)
  assert.deepEqual(b.segments[0].geometry, [])
})

test('rejects non-rail geometry, incorrect snap, distance outliers, service errors or missed via stops', async () => {
  for (const [fetcher, overrides] of [
    [() => response(points, 'railway=subway'), {}],
    [() => response(points, 'highway=trunk'), {}],
    [() => response(points.slice().reverse()), {}],
    [() => response(points, 'railway=rail', 15000), {}],
    [() => response(), { viaStops: [{ name: '丙', location: [118.03, 32.1] }] }],
    [() => { throw new Error('upstream unavailable') }, {}],
  ]) {
    const item = route({ ...leg(), ...overrides })
    await enrichNetworkRailRoutes([item], { fetcher })
    assert.deepEqual(item.segments[0].geometry, [])
  }
})

test('skips existing track, unconfirmed train and modes other than rail', async () => {
  let calls = 0
  for (const overrides of [{ geometry: points }, { unconfirmed: true }, { type: 'flight' }]) {
    await enrichNetworkRailRoutes([route({ ...leg(), ...overrides })], { fetcher: () => { calls++; return response() } })
  }
  assert.equal(calls, 0)
})
