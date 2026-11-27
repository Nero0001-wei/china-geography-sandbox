import { sameJourneyCity, railVehicleForService } from './vehicle-journey.js'
import { gcj02ToWgs84 } from '../shared/coordinates.js'
import { NANJING_HUANGSHAN_ENDPOINTS } from '../shared/route-endpoints.js'
import { LANDMARKS } from '../shared/landmarks.js'
import sampleData from './routes/nanjing-huangshan.json'

const cities = [
  { city: '南京市', cityCode: '025', adcode: '320102' },
  { city: '黄山市', cityCode: '0559', adcode: '341003' },
]
export const exampleStops = Object.values(NANJING_HUANGSHAN_ENDPOINTS).map((item, i) => ({
  ...cities[i], name: item.name, address: item.address, location: item.gcj02, id: item.poiId,
}))
export const exampleSlug = 'nanjing-huangshan'
export const segmentNames = { drive: '自驾', walk: '步行', bus: '公交', coach: '长途客车', ferry: '客运轮渡', metro: '地铁', rail: '铁路', flight: '飞机', taxi: '打车', transfer: '换乘' }

function railStationName(name) {
  return name?.endsWith('站') ? name : name ? name + '站' : ''
}

export function railArrivalSummary(route) {
  const train = route.segments?.findLast(s => s.type === 'rail' && !s.unconfirmed)
  if (!train?.to?.name) return ''
  const number = train.name?.match(/^[A-Z]+\d+/i)?.[0]
  return [number, railStationName(train.to.name)].filter(Boolean).join(' → ')
}

export function transferMarkers(segments = []) {
  const markers = new Map()
  function add(stop, rail) {
    if (!stop?.name || !stop.location) return
    const name = rail ? railStationName(stop.name) : stop.name
    const key = [name, ...stop.location].join('|')
    markers.set(key, { name, location: stop.location })
  }
  for (const s of segments.filter(part => part.type === 'rail')) {
    add(s.to, true)
    add(s.from, true)
  }
  for (const s of segments.filter(part => ['metro', 'bus'].includes(part.type))) {
    add(s.to, false)
    add(s.from, false)
  }
  return [...markers.values()]
}

export function field(place) {
  return { text: place?.name || '', place: place || null }
}

export function landmarkStop(landmark, mode) {
  const point = mode === 'driving' ? landmark.destination : (landmark.transitDestination || landmark.destination)
  return point ? { ...point, landmarkId: landmark.id, landmarkName: landmark.name } : null
}

export function forMode(input, mode) {
  const landmark = LANDMARKS.find(item => item.id === input.place?.landmarkId)
  return landmark ? field(landmarkStop(landmark, mode)) : input
}

export function samePlace(a, b) {
  if (!a || !b) return false
  return (a.id && a.id === b.id) || Math.hypot(a.location[0] - b.location[0], a.location[1] - b.location[1]) < 0.00008
}

export function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return '用时待确认'
  const minutes = Math.max(1, Math.round(seconds / 60))
  return minutes >= 60 ? Math.floor(minutes / 60) + ' 小时' + (minutes % 60 ? ' ' + minutes % 60 + ' 分' : '') : minutes + ' 分钟'
}

export function amapLink(start, end, mode) {
  const url = new URL('https://uri.amap.com/navigation')
  for (const [key, point] of [['from', start], ['to', end]]) {
    url.searchParams.set(key, [...point.location, point.name].join(','))
  }
  url.searchParams.set('mode', mode === 'driving' ? 'car' : 'bus')
  url.searchParams.set('coordinate', 'gaode')
  return url.href
}

function mapStop(stop) {
  return { ...stop, gcj02: stop.location, location: gcj02ToWgs84(stop.location) }
}

function decorate(route, start, end, mode) {
  const sameCity = start.city === end.city
  const label = (point) => sameCity ? (point.landmarkName || point.name) : (point.city?.replace(/市$/, '') || point.name)
  function endpoint(place, leg, station) {
    const point = { ...mapStop(place), cityLabel: label(place) }
    // A city-to-city itinerary can start or end at the station without local transfer legs.
    if (mode === 'transit' && leg?.type === 'rail' && /^19010[234]$/.test(place.typecode) && station?.name && station.location) {
      point.mapAnchor = station.location
      point.cityLabel = railStationName(station.name)
    }
    return point
  }
  const first = route.segments?.[0]
  const last = route.segments?.at(-1)
  return {
    ...route, mode, title: label(start) + '至' + label(end),
    start: endpoint(start, first, first?.from),
    end: endpoint(end, last, last?.to),
  }
}

export function previewJourney() {
  return decorate(sampleData, exampleStops[0], exampleStops[1], 'driving')
}

async function getJourneys(start, end, mode, signal) {
  const response = await fetch('./api/journeys', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start, end, mode }), signal,
  })
  const data = await response.json()
  if (!response.ok || data.status !== 'ok' || !data.routes?.length) {
    throw new Error(data.message || '暂未找到可用方案，可以更换出行方式或地点。')
  }
  return data.routes
}

async function stationTransfer(a, b, signal) {
  if (samePlace(a, b)) return []
  try {
    const [route] = await getJourneys(a, b, 'transit', signal)
    if (route.segments?.length) return sameJourneyCity(a, b)
      ? route.segments.map(segment => ({ ...segment, localTransfer: true })) : route.segments
  } catch (error) {
    if (signal.aborted) throw error
  }
  return [{ type: 'transfer', name: '地面接驳待查询', from: mapStop(a), to: mapStop(b), geometry: [], unavailable: true }]
}

function highSpeedTrain(segment) {
  if (segment.type !== 'rail' || segment.unconfirmed) return false
  const service = railVehicleForService(segment)
  return service === 'high-speed-rail' || service === 'intercity-rail'
}

export async function findRailItineraries(start, end, signal) {
  try {
    const routes = await getJourneys(start, end, 'transit', signal)
    return routes.filter(route => route.segments.some(highSpeedTrain))
      .map(route => decorate(route, start, end, 'transit'))
  } catch (error) {
    if (signal.aborted) throw error
    return []
  }
}

function matchesStation(stop, hub) {
  const stationName = name => name?.trim().replace(/站$/, '')
  if (!stop?.name || stationName(stop.name) !== stationName(hub.name) || !stop.location) return false
  const [lon, lat] = hub.location
  const dx = (stop.location[0] - lon) * Math.cos(lat * Math.PI / 180)
  return Math.hypot(dx, stop.location[1] - lat) * 111_320 < 3000
}

async function hubConnection(kind, departure, arrival, signal) {
  const from = mapStop(departure)
  const to = mapStop(arrival)
  if (kind === 'rail') {
    const routes = await findRailItineraries(departure, arrival, signal)
    for (const route of routes) {
      const train = route.segments.find(segment => highSpeedTrain(segment) &&
        matchesStation(segment.from, from) && matchesStation(segment.to, to))
      if (train) return train
    }
  }
  return { type: kind, from, to, name: kind === 'flight' ? '航班待确认' : '高铁车次待确认',
    geometry: [], unconfirmed: true }
}

export async function suggestHub(stop, kind, signal) {
  const airport = kind === 'flight'
  function eligible(point) {
    const code = String(point.typecode || '')
    return (airport ? code === '150104' : code.startsWith('1502')) &&
      !/停车|进站口|出站口|售票|货运|货场|通用机场|已停|建设中|候车|出发层|到达层/.test(point.name)
  }
  if (eligible(stop)) return stop
  const params = new URLSearchParams({ q: stop.city + (airport ? '机场' : '高铁站'), kind })
  const response = await fetch('./api/places?' + params, { signal })
  const data = await response.json()
  if (!response.ok || data.status !== 'ok') throw new Error(data.message || '枢纽搜索暂不可用。')
  let candidates = (data.places || []).filter(p => p.adcode?.slice(0, 4) === stop.adcode?.slice(0, 4) && eligible(p))
  if (airport) {
    const airports = candidates.filter(p => !/航站楼|候机楼|T\d/i.test(p.name))
    if (airports.length) candidates = airports
  }
  const [lon, lat] = stop.location
  const latScale = Math.cos(lat * Math.PI / 180)
  const distance = point => Math.hypot((point.location[0] - lon) * latScale, point.location[1] - lat)
  candidates.sort((a, b) => distance(a) - distance(b))
  if (!candidates.length) throw new Error('没有找到' + stop.city + '的合适' + (airport ? '机场' : '车站') + '，请手动指定。')
  return candidates[0]
}

export async function planJourney({ start, end, mode, connection, departure, arrival }, signal) {
  if (mode === 'transit' && connection !== 'integrated') {
    const outbound = await stationTransfer(start, departure, signal)
    const link = await hubConnection(connection, departure, arrival, signal)
    const inbound = await stationTransfer(arrival, end, signal)
    const segments = [...outbound, link, ...inbound]
    return [decorate({ source: 'connections', segments, geometry: segments.flatMap(s => s.geometry || []),
      distanceMeters: null, durationSeconds: null }, start, end, mode)]
  }
  const example = mode === 'driving' && start.id === exampleStops[0].id && end.id === exampleStops[1].id
  if (example) {
    let note = '高德查询暂不可用，显示路网参考。'
    try {
      const response = await fetch('./api/routes/nanjing-huangshan', { signal, cache: 'no-store' })
      const data = await response.json()
      if (data.status === 'ok' && data.route) return [decorate(data.route, start, end, mode)]
      if (data.message) note = data.message
    } catch (error) {
      if (signal.aborted) throw error
    }
    return [decorate({ ...sampleData, note }, start, end, mode)]
  }
  const routes = await getJourneys(start, end, mode, signal)
  return routes.map(route => decorate(route, start, end, mode))
}
