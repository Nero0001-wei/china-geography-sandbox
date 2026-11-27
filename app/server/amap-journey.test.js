import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import test from 'node:test'
import { gcj02ToWgs84, wgs84ToGcj02 } from '../shared/coordinates.js'
import { NANJING_HUANGSHAN_ENDPOINTS as endpoints } from '../shared/route-endpoints.js'
import { createAmapJourneyMiddleware } from './amap-journey.js'
import { matchedRoadGeometry, transitRoutes } from './journey-data.js'

const key = 'fake-route-service-key-for-tests'
const { start, end } = endpoints
const post = (body) => ({
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
})

async function withApi(options, tests) {
  const middleware = createAmapJourneyMiddleware(options)
  const server = createServer((request, response) => {
    middleware(request, response, () => { response.writeHead(404).end() })
      .catch(() => { response.writeHead(500).end() })
  })
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
  try {
    const origin = `http://127.0.0.1:${server.address().port}`
    await tests((path, options) => fetch(origin + path, options))
  } finally {
    await new Promise((resolve) => server.close(resolve))
  }
}

function poi(name, typecode = '150200', id = 'B000000001') {
  return { id, name, location: '118.8,31.9', entr_location: '118.801,31.901', cityname: '南京市', citycode: '025', adcode: '320114', type: '交通设施服务', typecode }
}

test('retains service and station metadata for intercity models without turning local feeder buses into coaches', () => {
  const point = { name: '起点', location: '118.8,32.0', adcode: '320102', citycode: '025', cityname: '南京市' }
  const lines = [
    ['跨市客运', '南京至扬州'],
    ['轮渡', '海上快线'],
    ['普通公交', '12路(长途汽车站—轮渡码头)'],
    ['普通公交', '长途客运中心接驳线'],
  ]
  const segments = lines.map(([type, name]) => ({ bus: { buslines: [{ type, name, departure_stop: point }] } }))
  segments.push({ railway: { name: '沪宁线', trip: 'C3123', departure_stop: point } })
  const [result] = transitRoutes([{ segments }], { location: start.gcj02 }, { location: end.gcj02 })
  assert.deepEqual(result.segments.map(({ type }) => type), ['coach', 'ferry', 'bus', 'bus', 'rail'])
  assert.equal(result.segments.at(-1).trip, 'C3123')
  assert.equal(result.segments[0].from.cityCode, '025')
  assert.equal(result.segments[0].from.adcode, '320102')
})

test('place search routes distinct queries independently, coalesces repeats and filters hubs', async () => {
  const called = []
  let releaseFirst
  const firstRequest = new Promise((resolve) => { releaseFirst = resolve })
  let markFirstReceived
  const firstReceived = new Promise((resolve) => { markFirstReceived = resolve })

  await withApi({ key, fetcher: async (url) => {
    assert.equal(url.pathname, '/v3/place/text')
    assert.equal(url.searchParams.get('extensions'), 'all')
    const text = url.searchParams.get('keywords')
    called.push(text)
    if (text === '南京南站') {
      assert.equal(url.searchParams.get('types'), '150200')
      markFirstReceived()
      await firstRequest
      return Response.json({ status: '1', pois: [poi(text, '150202'), poi('机场无关结果', '150104', 'B000000002'), poi(text, '150202')] })
    }
    assert.equal(url.searchParams.get('types'), '150100')
    return Response.json({ status: '1', pois: [poi(text, '150104')] })
  } }, async (api) => {
    const railQuery = `/api/places?q=${encodeURIComponent('南京南站')}&kind=rail`
    const first = api(railQuery)
    await firstReceived
    const repeat = api(railQuery)
    const airportResponse = await api(`/api/places?q=${encodeURIComponent('南京禄口机场T2航站楼')}&kind=flight`)
    const airport = await airportResponse.json()
    releaseFirst()
    const responses = await Promise.all([first, repeat].map(async (promise) => (await promise).json()))

    assert.equal(airport.places[0].name, '南京禄口机场T2航站楼')
    assert.equal(airport.places[0].cityCode, '025')
    assert.deepEqual(responses[0], responses[1])
    assert.deepEqual(called, ['南京南站', '南京禄口机场T2航站楼'])
    assert.deepEqual(responses[0].places.map(({ name, location }) => [name, location]), [['南京南站', [118.801, 31.901]]])
    assert.ok(!JSON.stringify(responses).includes(key))
  })
})

test('transit preserves the published tracks and itinerary when a railway shape and a taxi road match are unavailable', async () => {
  const initialWalking = { polyline: '118.85,32.048;118.85,32.047' }
  const stationEntrance = { name: '地铁站', location: '118.85,32.047' }
  const southStation = { name: '南京南', location: '118.798034 31.968763' }
  const arrivalStation = { name: '测试车站', location: '118.089444 30.277519' }
  const transit = {
    distance: '345678', cost: { duration: '15480' },
    segments: [
      {
        walking: { origin: '118.85,32.048', destination: '118.85,32.047', distance: '100', cost: { duration: '80' }, steps: [{ polyline: initialWalking }] },
        bus: { buslines: [
          { name: '地铁1号线', type: '地铁线路', departure_stop: stationEntrance, arrival_stop: southStation, polyline: { polyline: '118.85,32.047;118.8,32;118.798034,31.968763' } },
          { name: '同一段的替代线路', type: '地铁线路' },
        ] },
      },
      { railway: { name: 'G1234', departure_stop: southStation, arrival_stop: arrivalStation, time: '7740' } },
      { taxi: { startpoint: arrivalStation.location, startname: arrivalStation.name, endpoint: end.gcj02.join(','), endname: end.name, drivetime: '2460', polyline: { polyline: '' } } },
    ],
  }
  await withApi({ key, fetcher: async (url) => {
    if (url.pathname === '/v5/direction/driving') return new Response(null, { status: 503 })
    assert.equal(url.pathname, '/v5/direction/transit/integrated')
    assert.equal(url.searchParams.get('city1'), '025')
    assert.equal(url.searchParams.get('city2'), '0559')
    assert.equal(url.searchParams.get('originpoi'), start.poiId)
    assert.equal(url.searchParams.get('destinationpoi'), end.poiId)
    assert.equal(url.searchParams.get('show_fields'), 'cost,polyline')
    return Response.json({ status: '1', route: { transits: [transit] } })
  } }, async (api) => {
    const response = await api('/api/journeys', post({ start: { poiId: start.poiId }, end: { poiId: end.poiId }, mode: 'transit' }))
    assert.equal(response.status, 200)
    const data = await response.json()
    const [route] = data.routes
    assert.equal(route.durationSeconds, 15480)
    assert.equal(route.distanceMeters, 345678)
    assert.equal(route.source, 'amap')
    assert.deepEqual(route.start.location, gcj02ToWgs84(start.gcj02))
    assert.deepEqual(route.start.gcj02, start.gcj02)
    assert.deepEqual(route.segments.map((segment) => [segment.type, segment.geometry.length]), [['walk', 2], ['metro', 3], ['rail', 0], ['taxi', 0]])
    assert.equal(route.segments[2].durationSeconds, 7740)
    assert.deepEqual(route.segments[2].to.location, gcj02ToWgs84([118.089444, 30.277519]))
    assert.equal(route.segments[3].to.name, end.name)
  })
})

test('reuses a matched road reference across itineraries and preserves original railway and taxi tracks', async () => {
  const origin = '118.089444,30.277519'
  const destination = end.gcj02.join(',')
  const coordinates = [origin, '118.12,30.18', destination].join(';')
  const taxi = { startpoint: origin, endpoint: destination, distance: '42000', drivetime: '2400' }
  let roadCalls = 0
  await withApi({ key, fetcher: async (url) => {
    if (url.pathname === '/v5/direction/driving') {
      roadCalls++
      assert.equal(url.searchParams.get('origin'), origin)
      assert.equal(url.searchParams.get('destination'), '118.176450,30.066134')
      return Response.json({ status: '1', route: { paths: [{ steps: [{ polyline: coordinates }] }] } })
    }
    const railway = { name: '测试班次', polyline: { polyline: coordinates } }
    const transits = [{ segments: [{ railway }, { taxi }] }, { segments: [{ taxi }] },
      { segments: [{ taxi: { ...taxi, polyline: { polyline: coordinates } } }] }]
    return Response.json({ status: '1', route: { transits } })
  } }, async (api) => {
    const { routes } = await (await api('/api/journeys', post({ start, end, mode: 'transit' }))).json()
    const [rail, inferredTaxi] = routes[0].segments
    assert.equal(roadCalls, 1)
    assert.equal(rail.geometry.length, 3)
    assert.equal(rail.geometrySource, undefined)
    assert.equal(inferredTaxi.geometrySource, 'amap-driving')
    assert.equal(inferredTaxi.distanceMeters, 42000)
    assert.equal(inferredTaxi.durationSeconds, 2400)
    assert.deepEqual(inferredTaxi.geometry, rail.geometry)
    assert.deepEqual(routes[1].segments[0], inferredTaxi)
    assert.equal(routes[2].segments[0].geometrySource, undefined)
    assert.equal(routes[2].segments[0].geometry.length, 3)
  })
})

test('discards disconnected taxi-road steps and road matches far from either stop', () => {
  const endpoints = { origin: '118.1,30.2', destination: '118.2,30.3' }
  for (const lines of [
    ['118.1,30.2;118.12,30.22', '118.13,30.23;118.2,30.3'],
    ['118.1,30.2;118.12,30.22', '', '118.12,30.22;118.2,30.3'],
    ['118.11,30.2;118.2,30.3'],
    ['118.1,30.2;118.2,30.29'],
  ]) assert.deepEqual(matchedRoadGeometry({ steps: lines.map(polyline => ({ polyline })) }, endpoints), [])
})

test('a rail-only itinerary can acquire a track using just the public stations', async () => {
  const points = [[118.8, 32], [118.83, 32.01], [118.86, 32]]
  const stops = points.map((point, i) => ({ name: ['甲', '乙', '丙'][i], location: wgs84ToGcj02(point).join(',') }))
  const railway = { trip: 'G9999', distance: '6080', departure_stop: stops[0], via_stops: [stops[1]], arrival_stop: stops[2] }
  let requests = 0
  await withApi({ key, fetcher: async url => {
    if (url.hostname === 'restapi.amap.com') return Response.json({ status: '1', route: { transits: [{ segments: [{ railway }] }] } })
    requests++
    assert.equal(url.hostname, 'brouter.de')
    assert.equal(url.searchParams.get('profile'), 'rail')
    assert.equal(url.searchParams.get('lonlats'), points.map(p => p.map(x => x.toFixed(6)).join(',')).join('|'))
    assert.equal(url.searchParams.has('key'), false)
    return Response.json({ features: [{ geometry: { type: 'LineString', coordinates: points },
      properties: { 'track-length': '6080', messages: [['WayTags'], ['railway=rail']] } }] })
  } }, async api => {
    const { routes } = await (await api('/api/journeys', post({ start, end, mode: 'transit' }))).json()
    assert.equal(requests, 1)
    assert.deepEqual(routes[0].segments[0].geometry, points)
    assert.equal(routes[0].segments[0].geometrySource, 'rail-network')
  })
})

test('validates requests, respects the key state and preserves geometry breaks in a driving route', async () => {
  const origin = { id: 'B000000001', name: '自定义起点', location: [118.851, 32.048] }
  const destination = { id: 'B000000002', name: '自定义终点', location: [118.17, 30.07] }
  await withApi({ fetcher: () => assert.fail('Unexpected upstream request') }, async (api) => {
    const noKey = await api('/api/places?q=test')
    assert.equal(noKey.status, 200)
    assert.equal((await noKey.json()).status, 'not_configured')
    assert.equal((await api('/api/places?q=&kind=rail')).status, 400)
    assert.equal((await api('/api/places?q=test&kind=invalid')).status, 400)
    assert.equal((await api('/api/journeys', { method: 'POST', body: 'a' })).status, 415)
    assert.equal((await api('/api/journeys', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{' })).status, 400)
    assert.equal((await api('/api/journeys', post({ name: 'a'.repeat(9000) }))).status, 413)
    assert.equal((await api('/api/journeys', post({ start: origin, end: destination, mode: 'transit' }))).status, 400)
    assert.equal((await api('/api/journeys', post({ start: origin, end: origin, mode: 'driving' }))).status, 400)
    const result = await api('/api/journeys', post({ start: origin, end: destination, mode: 'driving' }))
    assert.equal((await result.json()).status, 'not_configured')
  })
  await withApi({ key, fetcher: async (url) => {
    assert.equal(url.pathname, '/v5/direction/driving')
    assert.equal(url.searchParams.get('origin_id'), origin.id)
    return Response.json({ status: '1', route: { paths: [{
      distance: '278456', cost: { duration: '11341' },
      steps: [
        { polyline: '118.851,32.048;118.85,32.04' },
        { polyline: '118.85,32.04;118.82,32.03' },
        { step_distance: '100' },
        { polyline: '118.81,32.02;118.17,30.07' },
      ],
    }] } })
  } }, async (api) => {
    const response = await api('/api/journeys', post({ start: origin, end: destination, mode: 'driving' }))
    const { routes } = await response.json()
    assert.deepEqual(routes[0].segments.map((segment) => segment.geometry.length), [3, 0, 2])
    assert.deepEqual(routes[0].segments[0].geometry.at(-1), gcj02ToWgs84([118.82, 32.03]))
    assert.deepEqual(routes[0].segments[2].geometry[0], gcj02ToWgs84([118.81, 32.02]))
  })
})
