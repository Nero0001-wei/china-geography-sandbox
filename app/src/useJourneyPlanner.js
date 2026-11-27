import { useCallback, useEffect, useRef, useState } from 'react'
import { exampleSlug, exampleStops, field, findRailItineraries, forMode, landmarkStop, planJourney, previewJourney, samePlace, suggestHub } from './journey-planning.js'
import { compareRouteGeometry } from './route-differences.js'

const blank = { start: field(), end: field(), departure: field(), arrival: field(), mode: 'driving', connection: 'integrated' }
const demo = (mode, connection) => ({ ...blank, mode, connection, start: field(exampleStops[0]), end: field(exampleStops[1]) })
const idle = { status: 'idle', routes: [], index: 0 }
const previewOnly = import.meta.env.MODE === 'pages'

function readyResult(routes) {
  const hasMissingRail = route => route.segments?.some(s => s.type === 'rail' && !(s.geometry?.length >= 2))
  const hasDrawnRail = route => route.segments?.some(s => s.type === 'rail' && s.geometry?.length >= 2)
  const index = hasMissingRail(routes[0]) ? routes.findIndex(r => hasDrawnRail(r) && !hasMissingRail(r)) : 0
  return { status: 'ready', routes, index: Math.max(0, index) }
}

function setExampleUrl(next) {
  const url = new URL(location.href)
  if (!next && url.searchParams.get('route') !== exampleSlug) return
  url.searchParams.delete('mode')
  url.searchParams.delete('connection')
  if (next) {
    url.searchParams.set('route', exampleSlug)
    if (next.mode === 'transit') {
      url.searchParams.set('mode', 'transit')
      if (next.connection !== 'integrated') url.searchParams.set('connection', next.connection)
    }
  } else {
    url.searchParams.delete('route')
  }
  if (url.href !== location.href) history.replaceState(null, '', url)
}

function issue(draft) {
  const { start, end, mode, connection, departure, arrival } = draft
  if (!start.place || !end.place) return '请先选定起点和目的地。'
  if (samePlace(start.place, end.place)) return '起点与目的地相同，请换一个地点。'
  if (mode === 'transit' && connection !== 'integrated') {
    if ((departure.text && !departure.place) || (arrival.text && !arrival.place)) return '请从候选列表中确认枢纽，或清空后使用建议。'
    if (samePlace(departure.place, arrival.place)) return '出发与到达的枢纽相同，请重新选择。'
  }
  return ''
}

export function useJourneyPlanner() {
  const [initialExample] = useState(() => {
    const params = new URLSearchParams(location.search)
    if (params.get('route') !== exampleSlug) return null
    const mode = !previewOnly && params.get('mode') === 'transit' ? 'transit' : 'driving'
    const connection = params.get('connection')
    return demo(mode, mode === 'transit' && ['rail', 'flight'].includes(connection) ? connection : 'integrated')
  })
  const [draft, setDraft] = useState(() => initialExample || blank)
  const [result, setResult] = useState(idle)
  const request = useRef(null)
  const locationRequest = useRef(null)
  const [locating, setLocating] = useState(false)
  const [locationNotice, setLocationNotice] = useState('')

  const calculate = useCallback(async next => {
    request.current?.abort()
    if (previewOnly) {
      setExampleUrl(next)
      setResult(readyResult([previewJourney()]))
      return
    }
    const warning = issue(next)
    if (warning) { setResult({ ...idle, status: 'error', message: warning }); return }
    const controller = new AbortController()
    request.current = controller
    setResult({ ...idle, status: 'loading' })
    try {
      let departure = next.departure.place
      let arrival = next.arrival.place
      if (next.mode === 'transit' && next.connection !== 'integrated') {
        if (next.connection === 'rail' && !departure && !arrival) {
          const routes = await findRailItineraries(next.start.place, next.end.place, controller.signal)
          if (controller.signal.aborted) return
          if (routes.length) {
            setResult(readyResult(routes))
            return
          }
        }
        departure ??= await suggestHub(next.start.place, next.connection, controller.signal)
        arrival ??= await suggestHub(next.end.place, next.connection, controller.signal)
        if (controller.signal.aborted) return
        setDraft({ ...next, departure: field(departure), arrival: field(arrival) })
        if (samePlace(departure, arrival)) throw new Error('两端匹配到同一枢纽。可手动更换，或选「综合换乘」查询直达目的地的交通。')
      }
      const routes = await planJourney({
        start: next.start.place, end: next.end.place, mode: next.mode, connection: next.connection,
        departure, arrival,
      }, controller.signal)
      if (!controller.signal.aborted) setResult(readyResult(routes))
    } catch (error) {
      if (!controller.signal.aborted) setResult({ ...idle, status: 'error', message: error.message })
    }
  }, [])

  useEffect(() => {
    if (initialExample) calculate(initialExample)
    return () => { request.current?.abort(); locationRequest.current?.abort() }
  }, [initialExample, calculate])

  function cancelLocation() {
    locationRequest.current?.abort()
    locationRequest.current = null
    setLocating(false)
    setLocationNotice('')
  }

  async function useDeviceLocation() {
    if (locationRequest.current) return
    if (!window.isSecureContext || !navigator.geolocation) {
      setLocationNotice('当前页面无法使用定位。请用浏览器打开本机预览地址或 HTTPS 页面，也可以手动输入起点。')
      return
    }
    const controller = new AbortController()
    locationRequest.current = controller
    setLocating(true)
    setLocationNotice('正在获取设备位置…')
    try {
      const position = await new Promise((resolve, reject) => navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true, timeout: 15000, maximumAge: 0,
      }))
      if (controller.signal.aborted) return
      const { latitude, longitude, accuracy } = position.coords
      setLocationNotice('已定位，正在通过高德查询附近地址…')
      const response = await fetch('./api/location/reverse', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store',
        body: JSON.stringify({ location: [longitude, latitude] }), signal: controller.signal,
      })
      const data = await response.json()
      if (controller.signal.aborted) return
      if (!response.ok || data.status !== 'ok' || !data.place) {
        setLocationNotice(data.message || '未能查询附近地址，请手动输入起点。')
        return
      }
      request.current?.abort()
      setResult(idle)
      setExampleUrl(null)
      setDraft(current => ({
        ...current, start: field({ ...data.place, accuracyMeters: Number.isFinite(accuracy) ? Math.ceil(accuracy) : null }),
        departure: field(),
      }))
      setLocationNotice('')
    } catch (error) {
      if (controller.signal.aborted) return
      const message = {
        1: '定位权限未开启。可在浏览器的网站权限和系统定位设置中允许访问，或手动输入起点。',
        2: '设备暂时无法确定位置，请手动输入起点或稍后重试。',
        3: '定位超时，请重试或手动输入起点。',
      }[error.code]
      setLocationNotice(message || '暂时无法取得附近地址，请重试或手动输入起点。')
    } finally {
      if (locationRequest.current === controller) {
        locationRequest.current = null
        setLocating(false)
      }
    }
  }

  function change(next, { plan = false, keepExample = false } = {}) {
    if (next.start !== draft.start || next === blank) cancelLocation()
    setDraft(next)
    setExampleUrl(keepExample ? next : null)
    if (plan && !issue(next)) calculate(next)
    else {
      request.current?.abort()
      setResult(idle)
    }
  }
  function updateField(key, value) {
    const next = { ...draft, [key]: value }
    if (key === 'start') next.departure = field()
    if (key === 'end') next.arrival = field()
    change(next)
  }
  function edit(key, text) { updateField(key, { text, place: null }) }
  function pick(key, place) { updateField(key, field(place)) }
  function changeTransport(next) {
    const keepExample = new URLSearchParams(location.search).get('route') === exampleSlug
    change(next, { plan: true, keepExample })
  }
  function setMode(mode) {
    if (mode === draft.mode) return
    changeTransport({ ...draft, mode, start: forMode(draft.start, mode), end: forMode(draft.end, mode) })
  }
  function setConnection(connection) {
    if (connection !== draft.connection) changeTransport({ ...draft, connection, departure: field(), arrival: field() })
  }
  function pickLandmark(landmark) {
    const stop = landmarkStop(landmark, draft.mode)
    if (!stop) return false
    const next = { ...draft, end: field(stop), arrival: field() }
    change(next)
    if (next.start.place) calculate(next)
    return !next.start.place
  }
  function example() { change(demo(draft.mode, draft.connection), { plan: true, keepExample: true }) }

  function selectRoute(index) {
    setResult(previous => {
      const route = previous.routes[index]
      if (!route || previous.index === index) return previous
      const comparison = route.mode === 'transit' ? compareRouteGeometry(previous.routes[previous.index], route) : null
      return { ...previous, index, comparison }
    })
  }

  return {
    draft, result, route: result.routes[result.index] || null, canPlan: !issue(draft), previewOnly,
    locating, locationNotice, useDeviceLocation, cancelLocation,
    validation: issue(draft), edit, pick, setMode, setConnection, pickLandmark, example,
    calculate: () => calculate(draft), clear: () => change(blank),
    swap: () => change({ ...draft, start: draft.end, end: draft.start, departure: draft.arrival, arrival: draft.departure }),
    selectRoute,
  }
}
