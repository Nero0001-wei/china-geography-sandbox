import assert from 'node:assert/strict'
import { Readable } from 'node:stream'
import test from 'node:test'
import { gcj02ToWgs84, wgs84ToGcj02 } from '../shared/coordinates.js'
import { createAmapLocationMiddleware } from './amap-location.js'

const PATH = '/api/location/reverse'
const PUBLIC_POINT = [116.391276, 39.907462]

async function request(middleware, location, { method = 'POST', url = PATH } = {}) {
  const body = Buffer.from(JSON.stringify({ location }))
  const incoming = Object.assign(Readable.from([body]), {
    method, url, headers: { 'content-type': 'application/json' },
  })
  const headers = new Map()
  const outgoing = {
    setHeader(name, value) { headers.set(name, value) },
    end(data) { this.body = JSON.parse(data) },
  }
  await middleware(incoming, outgoing, () => assert.fail('Reverse endpoint was not handled'))
  return { status: outgoing.statusCode, body: outgoing.body, headers }
}

test('forward and inverse coordinate transforms round-trip a public point', () => {
  const gcj = wgs84ToGcj02(PUBLIC_POINT)
  assert.notDeepEqual(gcj, PUBLIC_POINT)
  const roundTrip = gcj02ToWgs84(gcj)
  PUBLIC_POINT.forEach((coordinate, index) => assert.ok(Math.abs(coordinate - roundTrip[index]) < 1e-7))
})

test('reverse lookup sends only converted GCJ-02 and keeps the query point despite returned POIs', async () => {
  const mockKey = 'test-only-location-key'
  const upstream = []
  const middleware = createAmapLocationMiddleware({ key: mockKey, fetcher: async (url, options) => {
    upstream.push({ pathname: url.pathname, params: url.searchParams, cache: options.cache, headers: options.headers })
    return Response.json({
      status: '1',
      regeocode: {
        formatted_address: '北京市东城区长安街',
        addressComponent: {
          country: '中国', province: '北京市', city: [], citycode: '010', district: '东城区', adcode: '110101',
          streetNumber: { street: '长安街', location: '116.4,39.9' },
        },
        pois: [{ id: 'B0TESTPOI', name: '附近兴趣点', location: '116.4,39.9' }],
      },
    })
  } })

  const converted = wgs84ToGcj02(PUBLIC_POINT).map((coordinate) => coordinate.toFixed(6))
  const results = await Promise.all([request(middleware, PUBLIC_POINT), request(middleware, PUBLIC_POINT)])
  assert.equal(upstream.length, 2)
  for (const { pathname, params, cache, headers } of upstream) {
    assert.equal(pathname, '/v3/geocode/regeo')
    assert.equal(params.get('location'), converted.join(','))
    assert.notEqual(params.get('location'), PUBLIC_POINT.join(','))
    assert.equal(params.get('extensions'), 'base')
    assert.equal(cache, 'no-store')
    assert.equal(headers['Cache-Control'], 'no-store')
  }
  for (const result of results) {
    assert.equal(result.status, 200)
    assert.equal(result.headers.get('Cache-Control'), 'private, no-store')
    const { place } = result.body
    assert.equal(place.city, '北京市')
    assert.equal(place.cityCode, '010')
    assert.equal(place.adcode, '110101')
    assert.equal(place.name, '北京市东城区长安街')
    assert.equal(place.source, 'device_location')
    assert.deepEqual(place.location, converted.map(Number))
    assert.ok(!Object.hasOwn(place, 'id'))
    assert.ok(!JSON.stringify(result.body).includes(mockKey))
  }
})

test('reverse coverage accepts Hong Kong and Macau, then checks service geography within broad bounds', async () => {
  const scenarios = [
    { province: '香港特别行政区', city: [], citycode: '1852', adcode: '810001' },
    { country: '中国澳门', province: '澳门特别行政区', city: [], citycode: '1853', adcode: '820001' },
    { country: '蒙古国', province: '乌兰巴托', city: '乌兰巴托', adcode: '' },
    {},
  ]
  const middleware = createAmapLocationMiddleware({ key: 'mock', fetcher: async () => {
    return Response.json({ status: '1', regeocode: { addressComponent: scenarios.shift() } })
  } })
  assert.equal((await request(middleware, [114.17, 22.28])).body.place.city, '香港特别行政区')
  assert.equal((await request(middleware, [113.54, 22.19])).body.place.city, '澳门特别行政区')
  assert.equal((await request(middleware, [106.92, 47.919])).body.status, 'outside_coverage')
  assert.equal((await request(middleware, [108.8, 20.9])).body.status, 'no_address')
})

test('invalid format, obviously foreign points and absent key never reach the provider', async () => {
  const middleware = createAmapLocationMiddleware({ fetcher: () => assert.fail('Unexpected upstream lookup') })
  assert.equal((await request(middleware, [200, 90])).status, 400)
  assert.equal((await request(middleware, ['116.4', 39.9])).status, 400)
  assert.equal((await request(middleware, [2.2945, 48.8584])).body.status, 'outside_coverage')
  assert.equal((await request(middleware, PUBLIC_POINT, { method: 'GET' })).status, 405)
  assert.equal((await request(middleware, PUBLIC_POINT, { url: `${PATH}?q=x` })).status, 400)
  const noKey = await request(middleware, PUBLIC_POINT)
  assert.equal(noKey.status, 200)
  assert.equal(noKey.body.status, 'not_configured')
  assert.ok(noKey.body.message)
})

test('network errors return a useful message without sharing provider URLs or intermediate location', async () => {
  const mockKey = 'test-only-location-key'
  const middleware = createAmapLocationMiddleware({ key: mockKey, fetcher: async (url) => {
    throw new DOMException(String(url), 'TimeoutError')
  } })
  const result = await request(middleware, PUBLIC_POINT)
  assert.equal(result.status, 504)
  assert.equal(result.body.status, 'unavailable')
  assert.match(result.body.message, /超时/)
  assert.ok(!result.body.message.includes(mockKey))
  assert.ok(!result.body.message.includes('restapi'))
  assert.equal(result.headers.get('Cache-Control'), 'private, no-store')
})
