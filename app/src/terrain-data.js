import proj4 from 'proj4'

export const SCENE_UNIT_METERS = 100_000
export const VERTICAL_EXAGGERATION = 25
export const METERS_TO_HEIGHT = VERTICAL_EXAGGERATION / SCENE_UNIT_METERS

export const LANDFORMS = [
  { id: 'tibet', name: '青藏高原', lon: 88.8, lat: 32.6, description: '中国地势第一级阶梯' },
  { id: 'sichuan', name: '四川盆地', lon: 105.0, lat: 30.4, description: '中国地势第二级阶梯' },
  { id: 'plains', name: '长江中下游平原', lon: 113.1, lat: 30.25, description: '中国地势第三级阶梯' },
]

export const MAP_LABELS = [
  ...LANDFORMS,
  { name: '天山', lon: 82.9, lat: 43.8 },
  { name: '塔里木盆地', lon: 84.3, lat: 39.8 },
  { name: '内蒙古高原', lon: 110.2, lat: 43.3 },
  { name: '东北平原', lon: 125.1, lat: 45.2 },
  { name: '华北平原', lon: 116.1, lat: 37.0 },
  { name: '云贵高原', lon: 103.6, lat: 25.5 },
  { name: '渤海', lon: 119.8, lat: 39.1, water: true },
  { name: '东海', lon: 124.7, lat: 27.9, water: true },
  { name: '南海', lon: 114.2, lat: 17.3, water: true },
  { name: '台湾岛', lon: 121.1, lat: 23.7, secondary: true },
  { name: '海南岛', lon: 109.8, lat: 19.1, secondary: true },
  { name: '柴达木盆地', lon: 94.7, lat: 37.3, detail: true },
  { name: '祁连山', lon: 99.6, lat: 38.4, detail: true },
  { name: '秦岭', lon: 107.9, lat: 33.9, detail: true },
  { name: '武夷山', lon: 117.1, lat: 27.8, detail: true },
  { name: '大兴安岭', lon: 122.3, lat: 49.5, detail: true },
  { name: '黄土高原', lon: 109.3, lat: 36.4, detail: true },
]

export function getMapLabels(boundaries) {
  return [
    ...MAP_LABELS,
    ...(boundaries?.islandLabels ?? []).map((label) => ({ ...label, island: true, secondary: true })),
  ]
}

async function getAsset(filename, signal) {
  const response = await fetch(`${import.meta.env.BASE_URL}data/${filename}`, { signal })
  if (!response.ok) throw new Error(`无法读取 ${filename}（HTTP ${response.status}）`)
  return filename.endsWith('.json') ? response.json() : response.arrayBuffer()
}

async function getOverview(signal) {
  const blob = new Blob([await getAsset('atlas/overview.webp', signal)], { type: 'image/webp' })
  const image = new Image()
  const url = URL.createObjectURL(blob)
  try {
    image.src = url
    await image.decode()
    return image
  } finally {
    URL.revokeObjectURL(url)
  }
}

function coastlineSampler(buffer, [width, height], additionalLand = []) {
  const offsets = new Uint32Array(buffer, 0, height + 1)
  const edges = new Uint16Array(buffer, offsets.byteLength)
  const patches = additionalLand.map(ring => {
    const xs = ring.map(([x]) => x), ys = ring.map(([, y]) => y)
    return { ring, left: Math.min(...xs), right: Math.max(...xs), top: Math.min(...ys), bottom: Math.max(...ys) }
  })
  return (u, v) => {
    const row = Math.round(v * (height - 1))
    const column = Math.round(u * (width - 1))
    const start = offsets[row]
    let lo = start
    let hi = offsets[row + 1]
    while (lo < hi) {
      const mid = (lo + hi) >>> 1
      if (edges[mid] <= column) lo = mid + 1
      else hi = mid
    }
    if ((lo - start) % 2 === 1) return true
    return patches.some(({ ring, left, right, top, bottom }) => {
      if (u < left || u > right || v < top || v > bottom) return false
      let inside = false
      for (let i = 1; i < ring.length; i++) {
        const [ax, ay] = ring[i - 1], [bx, by] = ring[i]
        if ((ay > v) !== (by > v) && u < ax + (v - ay) * (bx - ax) / (by - ay)) inside = !inside
      }
      return inside
    })
  }
}

export async function loadMapData(signal) {
  const [metadata, elevation, land, boundaries, profile, inset, atlas, overview, coast] = await Promise.all([
    getAsset('terrain.json', signal),
    getAsset('elevation.i16', signal),
    getAsset('land.u8', signal),
    getAsset('china-boundaries.json', signal),
    getAsset('profile-32n.json', signal),
    getAsset('south-china-sea.json', signal),
    getAsset('atlas/atlas.json', signal),
    getOverview(signal),
    getAsset('atlas/coast.runs', signal),
  ])

  const size = metadata.width * metadata.height
  if (elevation.byteLength !== size * 2 || land.byteLength !== size) {
    throw new Error('高程或海陆数据与网格尺寸不匹配')
  }

  const elevations = new Int16Array(size)
  const bytes = new DataView(elevation)
  for (let i = 0; i < size; i++) elevations[i] = bytes.getInt16(i * 2, true)

  return {
    terrain: createTerrain(metadata, elevations, new Uint8Array(land), coastlineSampler(coast, atlas.coastSize, atlas.additionalLand)),
    atlas, overview,
    boundaries,
    profile,
    inset,
  }
}

export function createTerrain(metadata, elevations, land, detailedLand) {
  const { width, height, bounds, projection, noData, scale } = metadata
  const { minX, maxX, minY, maxY } = bounds
  const projectionTransform = proj4('EPSG:4326', projection)
  const centerX = (minX + maxX) / 2
  const centerY = (minY + maxY) / 2
  const stepX = (maxX - minX) / (width - 1)
  const stepY = (maxY - minY) / (height - 1)

  function geoToWorld(lon, lat) {
    const [x, y] = projectionTransform.forward([lon, lat])
    return [(x - centerX) / SCENE_UNIT_METERS, (centerY - y) / SCENE_UNIT_METERS]
  }

  function worldToGeo(x, z) {
    return projectionTransform.inverse([
      centerX + x * SCENE_UNIT_METERS,
      centerY - z * SCENE_UNIT_METERS,
    ])
  }

  function gridPoint(x, z) {
    return [
      (centerX + x * SCENE_UNIT_METERS - minX) / stepX,
      (maxY - centerY + z * SCENE_UNIT_METERS) / stepY,
    ]
  }

  function gridElevation(index) {
    return elevations[index] === noData ? 0 : elevations[index] * scale
  }

  function sample(x, z) {
    const [column, row] = gridPoint(x, z)
    if (column < 0 || row < 0 || column > width - 1 || row > height - 1) return null

    const nearest = Math.round(row) * width + Math.round(column)
    const left = Math.min(Math.floor(column), width - 2)
    const top = Math.min(Math.floor(row), height - 2)
    const u = column - left
    const v = row - top
    const corner = top * width + left
    const a = gridElevation(corner)
    const b = gridElevation(corner + 1)
    const c = gridElevation(corner + width)
    const d = gridElevation(corner + width + 1)
    // Interpolate the same two triangles that form each rendered grid cell.
    const elevation = u + v <= 1
      ? a + (b - a) * u + (c - a) * v
      : d + (c - d) * (1 - u) + (b - d) * (1 - v)

    return {
      elevation,
      land: detailedLand ? detailedLand(column / (width - 1), row / (height - 1)) : Boolean(land[nearest]),
      valid: elevations[nearest] !== noData,
    }
  }

  function surfaceHeight(x, z) {
    const point = sample(x, z)
    return point?.land && point.valid ? point.elevation * METERS_TO_HEIGHT : 0
  }

  return {
    metadata, elevations, land, geoToWorld, worldToGeo, gridPoint, gridElevation, sample, surfaceHeight,
  }
}
