import { wgs84ToGcj02 } from '../shared/coordinates.js'
import { createAmapClient, failure, send } from './amap-client.js'
import { jsonBody } from './http-json.js'
import { cleanText, formatLocation } from './journey-data.js'

const API_PATH = '/api/location/reverse'
const DOMESTIC_ADCODE = /^(11|12|13|14|15|21|22|23|31|32|33|34|35|36|37|41|42|43|44|45|46|50|51|52|53|54|61|62|63|64|65|71|81|82)\d{4}$/
const DOMESTIC_COUNTRY = /^(?:中国(?:大陆|香港(?:特别行政区)?|澳门(?:特别行政区)?|台湾(?:省)?)?|中华人民共和国|hong kong|macau|macao|taiwan|china|cn)$/iu
const OUTSIDE = '当前位置超出沙盘的国内路线查询范围，可手动选择起点。'
const NO_ADDRESS = '高德没有找到当前位置附近的详细地址，可手动选择起点。'

function validCoordinates(point) {
  return Array.isArray(point) && point.length === 2 && point.every(Number.isFinite) &&
    Math.abs(point[0]) <= 180 && Math.abs(point[1]) <= 90
}

function withinDomesticBounds([lon, lat]) {
  // This only removes clearly distant points. Amap's administrative lookup handles borders and islands.
  return lon >= 72 && lon <= 136 && lat >= 3 && lat <= 55
}

function placeFromAddress(result, location) {
  const parts = result?.addressComponent
  const country = cleanText(parts?.country)
  const adcode = cleanText(parts?.adcode)
  if (country && !DOMESTIC_COUNTRY.test(country)) return failure(OUTSIDE, 'outside_coverage')

  const province = cleanText(parts?.province)
  const city = cleanText(parts?.city) || province
  const district = cleanText(parts?.district)
  const cityCode = cleanText(parts?.citycode)
  const street = cleanText(parts?.streetNumber?.street)
  const number = cleanText(parts?.streetNumber?.number)
  const formatted = cleanText(result?.formatted_address)
  const address = formatted || [...new Set([province, city, district, cleanText(parts?.township), street + number].filter(Boolean))].join('')
  if (!address || (!DOMESTIC_ADCODE.test(adcode) && !country)) return failure(NO_ADDRESS, 'no_address')

  return { body: {
    status: 'ok',
    place: {
      name: cleanText(parts?.building?.name) || address,
      address, city, district, province,
      cityCode: /^\d{3,4}$/.test(cityCode) ? cityCode : '',
      adcode: DOMESTIC_ADCODE.test(adcode) ? adcode : '',
      location,
      source: 'device_location',
    },
  } }
}

async function reverseLocation(input, requestAmap) {
  const point = input?.location
  if (!validCoordinates(point)) return failure('定位坐标格式有误，可重试定位或手动选择起点。', 'invalid_request', 400)
  if (!withinDomesticBounds(point)) return failure(OUTSIDE, 'outside_coverage')

  // Only the service's converted coordinates are sent in the upstream GET request.
  const location = formatLocation(wgs84ToGcj02(point))
  const { data, error } = await requestAmap('/v3/geocode/regeo', { location, extensions: 'base' })
  if (error) return error
  return placeFromAddress(data.regeocode, location.split(',').map(Number))
}

export function createAmapLocationMiddleware({ key, fetcher = fetch } = {}) {
  const requestAmap = createAmapClient({ key, fetcher, coalesce: false })
  return async (request, response, next) => {
    if (request.url?.split('?', 1)[0] !== API_PATH) return next()
    if (request.method !== 'POST') {
      response.setHeader('Allow', 'POST')
      return send(response, failure('该接口使用 POST。', 'method_not_allowed', 405))
    }
    if (request.url !== API_PATH) {
      request.resume()
      return send(response, failure('请将定位坐标放入 JSON 请求体。', 'invalid_request', 400))
    }

    const { input, error } = await jsonBody(request, '定位请求')
    if (response.destroyed) return
    return send(response, error ?? await reverseLocation(input, requestAmap))
  }
}

export function amapLocationPlugin(key) {
  const register = (server) => {
    server.middlewares.use(createAmapLocationMiddleware({ key }))
  }
  return { name: 'amap-reverse-location', configureServer: register, configurePreviewServer: register }
}
