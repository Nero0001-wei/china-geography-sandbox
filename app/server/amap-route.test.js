import assert from 'node:assert/strict'
import test from 'node:test'
import { createAmapRouteMiddleware } from './amap-route.js'
import { gcj02ToWgs84 } from './coordinates.js'
import { NANJING_HUANGSHAN_ENDPOINTS } from '../shared/route-endpoints.js'

const routePath = '/api/routes/nanjing-huangshan'
const testKey = 'fake-route-service-key-for-tests'
const { start, end } = NANJING_HUANGSHAN_ENDPOINTS
const responseFixture = () => Response.json({
  status: '1',
  route: { paths: [{
    distance: '312000',
    cost: { duration: '12800' },
    steps: [
      { polyline: '118.851346,32.048217;118.7,32' },
      { polyline: '118.7,32;118.176450,30.066134' },
    ],
  }] },
})

async function request(middleware, method = 'GET', url = routePath) {
  const headers = new Map()
  const response = {
    setHeader(name, value) { headers.set(name, value) },
    end(body) { this.body = JSON.parse(body) },
  }
  let forwarded = false
  await middleware({ method, url }, response, () => { forwarded = true })
  return { status: response.statusCode, body: response.body, headers, forwarded }
}

test('absent key is a normal status and unrelated requests are forwarded', async () => {
  const middleware = createAmapRouteMiddleware({ fetcher: () => assert.fail('Unexpected network request') })
  const route = await request(middleware)
  assert.equal(route.status, 200)
  assert.equal(route.body.status, 'not_configured')
  assert.equal(route.headers.get('Cache-Control'), 'private, no-store')
  assert.equal((await request(middleware, 'POST')).status, 405)
  assert.equal((await request(middleware, 'GET', '/app.js')).forwarded, true)
})

test('fixed POIs drive the request and the route keeps converted endpoints without duplicate points', async () => {
  const middleware = createAmapRouteMiddleware({
    key: testKey,
    fetcher: async (url, options) => {
      assert.equal(url.origin, 'https://restapi.amap.com')
      assert.equal(url.pathname, '/v5/direction/driving')
      assert.equal(url.searchParams.get('origin_id'), start.poiId)
      assert.equal(url.searchParams.get('destination_id'), end.poiId)
      assert.equal(url.searchParams.get('origin'), '118.851346,32.048217')
      assert.equal(url.searchParams.get('destination'), '118.176450,30.066134')
      assert.equal(url.searchParams.get('show_fields'), 'cost,polyline')
      assert.equal(options.redirect, 'error')
      assert.ok(options.signal instanceof AbortSignal)
      return responseFixture()
    },
  })
  const { status, body } = await request(middleware)
  assert.equal(status, 200)
  assert.equal(body.status, 'ok')
  assert.equal(body.route.source, 'amap')
  assert.equal(body.route.distanceMeters, 312000)
  assert.equal(body.route.durationSeconds, 12800)
  assert.equal(body.route.geometry.length, 3)
  assert.deepEqual(body.route.geometry[0], gcj02ToWgs84(start.gcj02))
  assert.deepEqual(body.route.geometry.at(-1), gcj02ToWgs84(end.gcj02))
  assert.notDeepEqual(body.route.geometry[0], start.gcj02)
  assert.deepEqual(body.route.start, { name: start.name, address: start.address })
  assert.deepEqual(body.route.end, { name: end.name, address: end.address })
  assert.ok(!JSON.stringify(body).includes(testKey))
})

test('coalesces concurrent requests and fetches subsequent results anew', async () => {
  let calls = 0
  const middleware = createAmapRouteMiddleware({
    key: testKey,
    fetcher: async () => {
      calls++
      return responseFixture()
    },
  })
  const responses = await Promise.all([request(middleware), request(middleware)])
  assert.deepEqual(responses[0], responses[1])
  assert.equal(calls, 1)
  await request(middleware)
  assert.equal(calls, 2)
})

test('distinguishes an empty result, an invalid result, rate limits and timeouts', async () => {
  const responses = [
    () => Response.json({ status: '1', route: { paths: [] } }),
    () => Response.json({ status: '0', infocode: '20801' }),
    () => Response.json({ status: '1', route: { paths: [{ steps: [{}] }] } }),
    () => Response.json({ status: '0', infocode: '10003' }),
    () => { throw new DOMException(testKey, 'TimeoutError') },
  ]
  const middleware = createAmapRouteMiddleware({ key: testKey, fetcher: async () => responses.shift()() })
  assert.equal((await request(middleware)).body.status, 'no_route')
  assert.equal((await request(middleware)).body.status, 'no_route')
  assert.equal((await request(middleware)).status, 502)
  assert.equal((await request(middleware)).status, 503)
  const timeout = await request(middleware)
  assert.equal(timeout.status, 504)
  assert.ok(!JSON.stringify(timeout.body).includes(testKey))
})
