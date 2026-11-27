import { gcj02ToWgs84 } from './coordinates.js'
import { NANJING_HUANGSHAN_ENDPOINTS } from '../shared/route-endpoints.js'
import { createAmapClient, failure, send } from './amap-client.js'
import { formatLocation, readLocation } from './journey-data.js'

const DRIVING_PATH = '/v5/direction/driving'
const API_PATH = '/api/routes/nanjing-huangshan'
const NO_ROUTE_MESSAGE = '高德暂未找到这两个地点之间的驾车路线。'

function pathGeometry(steps) {
  const points = []
  for (const step of steps) {
    if (typeof step?.polyline !== 'string' || !step.polyline) return null
    for (const value of step.polyline.split(';')) {
      if (!value.trim()) continue
      const point = readLocation(value)
      if (!point) return null
      const previous = points.at(-1)
      if (previous?.[0] !== point[0] || previous?.[1] !== point[1]) points.push(point)
    }
  }
  return points.length > 1 ? points.map(gcj02ToWgs84) : null
}

function positiveInteger(value) {
  if (typeof value !== 'string' && typeof value !== 'number') return null
  const number = Number(value)
  return Number.isSafeInteger(number) && number > 0 ? number : null
}

function readDrivingPath(path) {
  if (!Array.isArray(path?.steps) || !path.steps.length) return null
  const geometry = pathGeometry(path.steps)
  const distanceMeters = positiveInteger(path.distance)
  let durationSeconds = positiveInteger(path.cost?.duration)
  if (durationSeconds === null) {
    const segmentSeconds = path.steps.map((step) => positiveInteger(step?.cost?.duration))
    if (segmentSeconds.every((value) => value !== null)) {
      durationSeconds = segmentSeconds.reduce((total, value) => total + value, 0)
    }
  }
  return geometry && distanceMeters && durationSeconds ? { geometry, distanceMeters, durationSeconds } : null
}

function formatEndpoint({ name, address }) {
  return { name, address }
}

async function requestDriving(requestAmap) {
  const { start, end } = NANJING_HUANGSHAN_ENDPOINTS
  const { data, error } = await requestAmap(DRIVING_PATH, {
    origin: formatLocation(start.gcj02),
    destination: formatLocation(end.gcj02),
    origin_id: start.poiId,
    destination_id: end.poiId,
    strategy: '32',
    show_fields: 'cost,polyline',
  }, NO_ROUTE_MESSAGE)
  if (error) return error

  const routes = data.route?.paths
  if (!Array.isArray(routes) || !routes.length) return failure(NO_ROUTE_MESSAGE, 'no_route')
  const path = readDrivingPath(routes[0])
  if (!path) return failure('高德驾车结果缺少完整的路线、里程或预计用时。', 'unavailable', 502)

  return {
    httpStatus: 200,
    body: { status: 'ok', route: { ...path, start: formatEndpoint(start), end: formatEndpoint(end), source: 'amap' } },
  }
}

export function createAmapRouteMiddleware({ key, fetcher = fetch } = {}) {
  const requestAmap = createAmapClient({ key, fetcher })

  return async (request, response, next) => {
    if (request.url?.split('?')[0] !== API_PATH) return next()
    if (request.method !== 'GET') {
      response.setHeader('Allow', 'GET')
      return send(response, failure('该接口使用 GET。', 'method_not_allowed', 405))
    }
    send(response, await requestDriving(requestAmap))
  }
}

export function amapRoutePlugin(key) {
  const register = (server) => {
    server.middlewares.use(createAmapRouteMiddleware({ key }))
  }
  return { name: 'amap-nanjing-huangshan', configureServer: register, configurePreviewServer: register }
}
