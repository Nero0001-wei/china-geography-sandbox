import { NANJING_HUANGSHAN_ENDPOINTS } from '../shared/route-endpoints.js'
import { createAmapClient, failure, send } from './amap-client.js'
import { jsonBody } from './http-json.js'
import { enrichNetworkRailRoutes } from './network-rail.js'
import { cleanText, drivingRoutes, formatLocation, matchedRoadGeometry, missingTaxiEndpoints, readLocation, transitRoutes } from './journey-data.js'

const API_PATHS = { places: '/api/places', journeys: '/api/journeys' }
const KIND_TYPE = { rail: '150200', flight: '150100' }
const NO_ROUTE_MESSAGE = '高德暂未返回这两个地点之间的可用路线。'
const FIXED_PLACES = new Map([
  [NANJING_HUANGSHAN_ENDPOINTS.start.poiId, {
    ...NANJING_HUANGSHAN_ENDPOINTS.start, city: '南京市', cityCode: '025', adcode: '320102',
  }],
  [NANJING_HUANGSHAN_ENDPOINTS.end.poiId, {
    ...NANJING_HUANGSHAN_ENDPOINTS.end, city: '黄山市', cityCode: '0559', adcode: '341003',
  }],
])

function textMatching(value, rule) {
  return typeof value === 'string' && rule.test(value.trim()) ? value.trim() : ''
}

function providerId(value) {
  return textMatching(value, /^[A-Za-z0-9]{4,40}$/)
}

function cityCode(value) {
  return textMatching(value, /^\d{3,4}$/)
}

function adcode(value) {
  return textMatching(value, /^\d{6}$/)
}

function fromProvider(poi) {
  const id = providerId(poi?.id)
  const name = cleanText(poi?.name)
  const location = readLocation(poi?.entr_location) ?? readLocation(poi?.location)
  if (!id || !name || !location) return null
  return {
    id, name, location,
    address: cleanText(poi.address) || [poi.pname, poi.cityname, poi.adname].map((part) => cleanText(part)).filter(Boolean).join(' '),
    city: cleanText(poi.cityname) || cleanText(poi.pname),
    cityCode: cityCode(poi.citycode),
    adcode: adcode(poi.adcode),
    type: cleanText(poi.type),
    typecode: adcode(poi.typecode),
  }
}

function parsePlace(input) {
  const id = providerId(input?.poiId) || providerId(input?.id)
  const fixed = FIXED_PLACES.get(id)
  const place = fixed ?? input
  const location = readLocation(place?.gcj02) ?? readLocation(place?.location)
  const name = cleanText(place?.name)
  if (!name || !location) return null
  return {
    id, name, location,
    address: cleanText(place.address),
    city: cleanText(place.city),
    cityCode: cityCode(place.cityCode),
    adcode: adcode(place.adcode),
    type: cleanText(place.type),
    typecode: adcode(place.typecode),
  }
}

async function places(url, requestAmap) {
  const query = url.searchParams.get('q')?.trim() ?? ''
  const kind = url.searchParams.get('kind')
  if (query.length < 1 || query.length > 80 || /\p{Cc}/u.test(query)) {
    return failure('请输入 1–80 个字符的地点关键词。', 'invalid_request', 400)
  }
  if (kind !== null && !Object.hasOwn(KIND_TYPE, kind)) {
    return failure('地点类别应为铁路站点或机场。', 'invalid_request', 400)
  }

  const kindType = KIND_TYPE[kind]
  const { data, error } = await requestAmap('/v3/place/text', {
    keywords: query, extensions: 'all', offset: '15', page: '1',
    ...(kindType ? { types: kindType } : {}),
  })
  if (error) return error
  const results = Array.isArray(data.pois) ? data.pois.map(fromProvider).filter(Boolean) : []
  const matching = kindType ? results.filter((poi) => poi.typecode.startsWith(kindType.slice(0, 4))) : results
  const unique = new Map(matching.map((place) => [place.id, place]))
  return { body: { status: 'ok', places: [...unique.values()] } }
}

function journeyQuery(start, end, mode) {
  const positions = { origin: formatLocation(start.location), destination: formatLocation(end.location) }
  if (mode === 'driving') {
    return {
      ...positions, strategy: '32', show_fields: 'cost,polyline',
      ...(start.id ? { origin_id: start.id } : {}),
      ...(end.id ? { destination_id: end.id } : {}),
    }
  }
  return {
    ...positions, city1: start.cityCode, city2: end.cityCode,
    strategy: '0', AlternativeRoute: '4', show_fields: 'cost,polyline',
    ...(start.adcode ? { ad1: start.adcode } : {}),
    ...(end.adcode ? { ad2: end.adcode } : {}),
    ...(start.id && end.id ? { originpoi: start.id, destinationpoi: end.id } : {}),
  }
}

async function findTaxiRoads(transits, requestAmap) {
  const roads = new Map()
  const jobs = new Map()
  for (const transit of transits) {
    if (!Array.isArray(transit?.segments)) continue
    for (const item of transit.segments) {
      const endpoints = missingTaxiEndpoints(item?.taxi)
      if (!endpoints) continue
      const key = endpoints.origin + ';' + endpoints.destination
      if (!jobs.has(key)) {
        if (jobs.size >= 4) continue
        jobs.set(key, { endpoints, taxis: [] })
      }
      jobs.get(key).taxis.push(item.taxi)
    }
  }
  const pending = [...jobs.values()]
  for (let i = 0; i < pending.length; i += 2) {
    await Promise.all(pending.slice(i, i + 2).map(async ({ endpoints, taxis }) => {
      const { data } = await requestAmap('/v5/direction/driving', {
        ...endpoints, strategy: '32', show_fields: 'polyline',
      })
      const geometry = matchedRoadGeometry(data?.route?.paths?.[0], endpoints)
      if (!geometry.length) return
      for (const taxi of taxis) roads.set(taxi, geometry)
    }))
  }
  return roads
}

async function journeys(input, requestAmap, fetcher) {
  const mode = input?.mode
  const start = parsePlace(input?.start)
  const end = parsePlace(input?.end)
  if (!start || !end || (mode !== 'driving' && mode !== 'transit')) {
    return failure('请选择有效的起终点和出行方式。', 'invalid_request', 400)
  }
  if ((start.id && start.id === end.id) || formatLocation(start.location) === formatLocation(end.location)) {
    return failure('起点和终点需要是不同地点。', 'invalid_request', 400)
  }
  if (mode === 'transit' && (!start.cityCode || !end.cityCode)) {
    return failure('公交查询需要两端城市，请从地点搜索结果中重新选择。', 'invalid_request', 400)
  }

  const driving = mode === 'driving'
  const path = driving ? '/v5/direction/driving' : '/v5/direction/transit/integrated'
  const { data, error } = await requestAmap(path, journeyQuery(start, end, mode), NO_ROUTE_MESSAGE)
  if (error) return error
  const options = driving ? data.route?.paths : data.route?.transits
  if (!Array.isArray(options) || !options.length) return failure(NO_ROUTE_MESSAGE, 'no_route')
  const choices = options.slice(0, 5)
  const routes = driving ? drivingRoutes(choices, start, end)
    : transitRoutes(choices, start, end, await findTaxiRoads(choices, requestAmap))
  if (!routes.length) return failure('高德未返回可识别的路线分段。', 'unavailable', 502)
  if (!driving) await enrichNetworkRailRoutes(routes, { fetcher })
  return { body: { status: 'ok', routes } }
}

export function createAmapJourneyMiddleware({ key, fetcher = fetch } = {}) {
  const requestAmap = createAmapClient({ key, fetcher })
  return async (request, response, next) => {
    const pathname = request.url?.split('?', 1)[0]
    if (pathname !== API_PATHS.places && pathname !== API_PATHS.journeys) return next()

    const search = pathname === API_PATHS.places
    const method = search ? 'GET' : 'POST'
    if (request.method !== method) {
      response.setHeader('Allow', method)
      return send(response, failure(`该接口使用 ${method}。`, 'method_not_allowed', 405))
    }
    if (search) return send(response, await places(new URL(request.url, 'http://localhost'), requestAmap))

    const { input, error } = await jsonBody(request, '路线请求')
    if (response.destroyed) return
    return send(response, error ?? await journeys(input, requestAmap, fetcher))
  }
}

export function amapJourneyPlugin(key) {
  const register = (server) => {
    server.middlewares.use(createAmapJourneyMiddleware({ key }))
  }
  return { name: 'amap-place-and-journey', configureServer: register, configurePreviewServer: register }
}
