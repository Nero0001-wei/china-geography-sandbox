const AMAP_ORIGIN = 'https://restapi.amap.com'
const REQUEST_TIMEOUT_MS = 8000

// https://lbs.amap.com/api/webservice/guide/tools/info
const RATE_LIMIT_CODES = new Set(['10003', '10004', '10010', '10014', '10015', '10019', '10020', '10021', '10044', '40000'])
const KEY_ERROR_CODES = new Set(['10001', '10002', '10005', '10006', '10007', '10008', '10009', '10012', '10013', '10041', '40002'])
const NO_ROUTE_CODES = new Set(['20800', '20801', '20802', '20803'])

export function failure(message, status = 'unavailable', httpStatus = 200) {
  return { httpStatus, body: { status, message } }
}

export function send(response, { httpStatus = 200, body }) {
  if (response.destroyed) return
  response.statusCode = httpStatus
  response.setHeader('Content-Type', 'application/json; charset=utf-8')
  response.setHeader('Cache-Control', 'private, no-store')
  response.end(JSON.stringify(body))
}

export function createAmapClient({ key, fetcher = fetch, coalesce = true }) {
  const serviceKey = key?.trim()
  const pending = new Map()

  async function fetchResult(path, query, noRouteMessage) {
    const url = new URL(path, AMAP_ORIGIN)
    url.search = new URLSearchParams({ ...query, key: serviceKey }).toString()
    let data
    try {
      const response = await fetcher(url, {
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
        redirect: 'error',
        cache: 'no-store',
        headers: { 'Cache-Control': 'no-store' },
      })
      if (response.status === 429) return { error: failure('高德服务请求频繁，请稍后再试。', 'unavailable', 503) }
      if (!response.ok) return { error: failure('暂时无法连接高德服务。', 'unavailable', 502) }
      data = await response.json()
    } catch (error) {
      const timeout = error?.name === 'TimeoutError'
      return { error: failure(timeout ? '高德服务请求超时，请稍后再试。' : '暂时无法获取高德服务结果。', 'unavailable', timeout ? 504 : 502) }
    }

    if (String(data?.status) === '1') return { data }
    const code = String(data?.infocode)
    if (RATE_LIMIT_CODES.has(code)) return { error: failure('高德服务配额暂不可用。', 'unavailable', 503) }
    if (KEY_ERROR_CODES.has(code)) return { error: failure('当前高德 Web 服务 Key 无法调用该接口。', 'unavailable', 503) }
    if (noRouteMessage && NO_ROUTE_CODES.has(code)) return { error: failure(noRouteMessage, 'no_route') }
    return { error: failure('高德服务暂未返回可用结果。', 'unavailable', 502) }
  }

  return function request(path, query, noRouteMessage) {
    if (!serviceKey) return { error: failure('暂未配置高德 Web 服务 Key。', 'not_configured') }
    if (!coalesce) return fetchResult(path, query, noRouteMessage)
    const cacheKey = `${path}?${new URLSearchParams(query)}`
    if (!pending.has(cacheKey)) {
      pending.set(cacheKey, fetchResult(path, query, noRouteMessage).finally(() => pending.delete(cacheKey)))
    }
    return pending.get(cacheKey)
  }
}
