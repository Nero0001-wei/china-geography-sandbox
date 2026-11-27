import { LANDMARKS } from '../shared/landmarks.js'
import { getMapLabels } from './terrain-data.js'

const TYPO_SCORE = 38

const LANDMARK_ALIASES = {
  gugong: ['故宫', '紫禁城', '故宫博物院'],
  badaling: ['长城'],
  qinhuai: ['夫子庙', '秦淮河'],
  'canton-tower': ['小蛮腰'],
  'panda-base': ['熊猫基地', '大熊猫基地'],
  'st-pauls': ['大三巴'],
  'qingming-park': ['清明上河园'],
  'victoria-harbour': ['维港'],
  everest: ['珠穆朗玛峰'],
  'orange-isle': ['橘子洲头'],
}

function normalize(text) {
  return text.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '')
}

function shortAdministrativeName(name) {
  return name.replace(/(?:(?:蒙古|朝鲜|藏族|羌族|白族|土家族|苗族|布依族)*自治州|特别行政区|维吾尔自治区|壮族自治区|回族自治区|自治区|地区|林区|省|市|县)$/u, '')
}

function uniqueNames(names) {
  return [...new Set(names.filter(Boolean).map(normalize))].filter(Boolean)
}

export function createMapSearchIndex(boundaries, places = []) {
  const landmarks = LANDMARKS.map(landmark => {
    const { id, name, province, city, anchor: [lon, lat] } = landmark
    const regions = [...new Set([province, city].filter(Boolean))]
    const localities = regions.flatMap(region => [region, shortAdministrativeName(region)])
    if (regions.length > 1) {
      const [fullProvince, shortProvince, fullCity, shortCity] = localities
      localities.push(fullProvince + fullCity, fullProvince + shortCity, shortProvince + fullCity, shortProvince + shortCity)
    }
    return {
      place: { id, name, kind: 'landmark', lon, lat, subtitle: regions.join(' · '), landmark },
      aliases: LANDMARK_ALIASES[id] ?? [],
      localities,
    }
  })
  const labels = getMapLabels(boundaries).map(label => ({
    place: {
      ...label,
      id: `landform-${label.id ?? label.name}`,
      kind: 'landform',
      subtitle: label.description || (label.water ? '海域' : label.island || label.name.endsWith('岛') ? '岛屿' : '地貌'),
    },
  }))
  const administrativePlaces = places.map(place => ({
    place,
    aliases: [...(place.aliases ?? []), shortAdministrativeName(place.name)],
  }))
  return [...landmarks, ...labels, ...administrativePlaces].map(({ place, aliases = [], localities = [] }) => ({
    place,
    names: uniqueNames([place.name, ...aliases]),
    localities: uniqueNames(localities),
  }))
}

function subsequenceGap(name, query) {
  let best = Infinity
  for (let start = name.indexOf(query[0]); start >= 0; start = name.indexOf(query[0], start + 1)) {
    let end = start
    for (let i = 1; i < query.length && end >= 0; i++) end = name.indexOf(query[i], end + 1)
    if (end >= 0) best = Math.min(best, end - start + 1 - query.length)
  }
  return best
}

function oneEditApart(a, b) {
  if (a.length < b.length) return oneEditApart(b, a)
  let i = 0
  while (i < b.length && a[i] === b[i]) i++
  if (a.length > b.length) return a.slice(i + 1) === b.slice(i)
  if (i === a.length) return false
  return a.slice(i + 1) === b.slice(i + 1) ||
    (a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2))
}

function hasNearSubstring(name, query) {
  if (query.length < 3) return false
  for (let size = query.length - 1; size <= Math.min(query.length + 1, name.length); size++) {
    if (size === 2 && name.length > 2) continue
    for (let start = 0; start <= name.length - size; start++) {
      if (oneEditApart(name.slice(start, start + size), query)) return true
    }
  }
  return false
}

function nameScore(name, query, alias) {
  if (name === query) return alias ? 96 : 100
  const extra = Math.min(8, name.length - query.length) / 2
  const position = name.indexOf(query)
  if (position === 0) return 85 - extra - alias
  if (position > 0) return 76 - extra - Math.min(6, position) / 2 - alias
  if (query.length >= 2) {
    const gap = subsequenceGap(name, query)
    if (gap <= Math.min(5, query.length + 1)) return 58 - gap - alias
  }
  return hasNearSubstring(name, query) ? TYPO_SCORE - Math.abs(extra) - alias : 0
}

function bestNameScore(names, query) {
  return Math.max(...names.map((name, i) => nameScore(name, query, Number(i > 0))))
}

function searchScore({ names, localities }, query) {
  let score = bestNameScore(names, query)
  for (const locality of localities) {
    if (locality.length >= query.length) continue
    let remainder = ''
    if (query.startsWith(locality)) remainder = query.slice(locality.length)
    else if (query.endsWith(locality)) remainder = query.slice(0, -locality.length)
    if (remainder) {
      const localScore = bestNameScore(names, remainder)
      if (localScore) score = Math.max(score, localScore - 7)
    }
  }
  return score
}

export function searchMap(index, query, limit = 8) {
  const term = normalize(query)
  if (!term || limit <= 0) return []
  const matches = index.map(entry => ({ place: entry.place, score: searchScore(entry, term) }))
    .filter(({ score }) => score > 0)
  const strongMatches = matches.filter(({ score }) => score > TYPO_SCORE)
  return (strongMatches.length ? strongMatches : matches).sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ place }) => place)
}
