import assert from 'node:assert/strict'
import test from 'node:test'
import { PbfWriter } from 'pbf'
import { createRoadDetailTiles, decodeRoadTile, roadTileCover } from './road-detail-tiles.js'

function geometry(points) {
  const commands = []
  let lastX = 0, lastY = 0
  const zigzag = v => (v << 1) ^ (v >> 31)
  for (const [i, [x, y]] of points.entries()) {
    if (i === 0) commands.push(9)
    if (i === 1) commands.push((points.length - 1) * 8 + 2)
    commands.push(zigzag(x - lastX), zigzag(y - lastY))
    lastX = x
    lastY = y
  }
  return commands
}

function tinyTile() {
  const writer = new PbfWriter()
  const crossing = [[-12, 100], [50, 100], [260, 100], [260, 200], [100, 200]]
  for (const layerName of ['transportation', 'transportation_name', 'waterway']) {
    writer.writeMessage(3, (name, layer) => {
      layer.writeStringField(1, name)
      for (const roadClass of [0, 1]) {
        layer.writeMessage(2, (_, feature) => {
          feature.writePackedVarint(2, [0, roadClass, 1, 2])
          feature.writeVarintField(3, 2)
          feature.writePackedVarint(4, geometry(crossing))
        })
      }
      for (const key of ['class', 'ref']) layer.writeStringField(3, key)
      for (const value of ['motorway', 'rail', 'G3;S103']) {
        layer.writeMessage(4, (s, pbf) => pbf.writeStringField(1, s), value)
      }
      layer.writeVarintField(5, 256)
      layer.writeVarintField(15, 2)
    }, layerName)
  }
  return writer.finish()
}

const view = { bounds: [118.79, 32.045, 118.795, 32.049], zoom: 12, center: [118.79, 32.045] }

test('clips MVT buffers without joining disconnected runs or drawing rail and unrelated layers', () => {
  const tile = decodeRoadTile(tinyTile(), { x: 3399, y: 1662, z: 12 })
  const longitude = px => (3399 + px / 256) / 4096 * 360 - 180
  assert.deepEqual(tile.roads.map(r => r.kind), ['expressway', 'expressway'])
  assert.deepEqual(tile.roads[0].coordinates.map(p => p[0]), [longitude(0), longitude(50), longitude(256)])
  assert.deepEqual(tile.roads[1].coordinates.map(p => p[0]), [longitude(256), longitude(100)])
  assert.deepEqual(tile.labels.map(l => l.text), ['G3'])
  assert.equal(tile.labels[0].lon, longitude(128))
})

test('retains real short Chinese street labels at z12 and prioritises simplified Chinese and road references', () => {
  const writer = new PbfWriter()
  const examples = [
    { name: 'Old name', 'name:zh': '中山門大街', 'name:zh-Hans': '中山门大街' },
    { name: 'Central Road', 'name:zh': '中央北路' }, { name: '虎踞路' }, { name: 'Main Street' },
    { name: '收费站/停车区' }, { subclass: 'junction', name: '高速路口' },
    { name: '施工道路' }, { name: '京台高速', ref: 'G3' },
  ]
  const rows = examples.map(row => ({ class: 'primary', ...row }))
  const keys = [...new Set(rows.flatMap(row => Object.keys(row)))]
  const values = [...new Set(rows.flatMap(row => Object.values(row)))]
  writer.writeMessage(3, (_, layer) => {
    layer.writeStringField(1, 'transportation_name')
    for (const row of rows) {
      layer.writeMessage(2, (_, feature) => {
        feature.writePackedVarint(2, Object.entries(row).flatMap(([k, v]) => [keys.indexOf(k), values.indexOf(v)]))
        feature.writeVarintField(3, 2)
        feature.writePackedVarint(4, geometry([[32, 100], [190, 100]]))
      })
    }
    for (const k of keys) layer.writeStringField(3, k)
    for (const v of values) layer.writeMessage(4, (value, pbf) => pbf.writeStringField(1, value), v)
    layer.writeVarintField(5, 256)
    layer.writeVarintField(15, 2)
  })
  const fixture = writer.finish()
  const labels = z => decodeRoadTile(fixture, { x: 1000, y: 1000, z }).labels
  assert.deepEqual(labels(12).map(l => [l.text, l.kind]), [
    ['G3', undefined], ['中山门大街', 'name'], ['中央北路', 'name'], ['虎踞路', 'name'],
  ])
  assert.deepEqual(labels(11).map(l => l.text), ['G3'])
})

test('bounds cover the entire footprint or use the local overview, including overzoomed views', () => {
  const broad = { bounds: [116, 29, 120, 33], center: [118, 31], zoom: 13 }
  const cover = roadTileCover(broad)
  assert.ok(cover.length && cover.length <= 24)
  assert.ok(cover[0].z < broad.zoom)
  assert.ok(cover.every((tile, i) => !i || tile.distance >= cover[i - 1].distance))
  assert.deepEqual(roadTileCover({ ...broad, bounds: [72, 16, 137, 55] }), [])
  assert.deepEqual(roadTileCover({ ...view, zoom: 7 }), [])
  assert.equal(roadTileCover({ ...view, zoom: 18 })[0].z, 14)
})

test('switching modes aborts pending requests and a late tile cannot reappear', async () => {
  let pending, status
  const shown = [], removed = []
  const fetcher = (url, { signal }) => new Promise(resolve => { pending = { resolve, signal, url } })
  const tiles = createRoadDetailTiles({ fetcher, onTile: t => shown.push(t), onRemove: key => removed.push(key), onStatus: s => { status = s } })
  try {
    tiles.update(view)
    await new Promise(resolve => setTimeout(resolve, 200))
    assert.ok(pending.url.endsWith('/12/3399/1662.pbf'))
    tiles.clear()
    assert.ok(pending.signal.aborted)
    pending.resolve(new Response(tinyTile()))
    await new Promise(resolve => setTimeout(resolve, 0))
    assert.deepEqual(shown, [])
    assert.equal(status.expected, 0)
    assert.deepEqual(removed, [])
  } finally { tiles.dispose() }
})

test('switches only a complete viewport, uses its in-memory cache, and reports an unavailable tile', async () => {
  let requests = 0, final
  const shown = [], removed = []
  const tiles = createRoadDetailTiles({
    fetcher: async () => { requests++; return requests === 1 ? new Response(tinyTile()) : new Response(null, { status: 503 }) },
    onTile: t => shown.push(t.key), onRemove: key => removed.push(key), onStatus: s => { final = s },
  })
  try {
    tiles.update(view)
    assert.equal(final.complete, false)
    await new Promise(resolve => setTimeout(resolve, 200))
    assert.deepEqual(final, { complete: true, expected: 1, loaded: 1, failed: false })
    tiles.clear()
    assert.deepEqual(removed, shown)
    tiles.update(view)
    assert.equal(requests, 1)
    assert.equal(final.complete, true)
    const other = { ...view, bounds: [118.17, 30.12, 118.175, 30.125] }
    tiles.update(other)
    await new Promise(resolve => setTimeout(resolve, 200))
    assert.deepEqual(final, { complete: false, loaded: 0, expected: 1, failed: true })
  } finally { tiles.dispose() }
})
