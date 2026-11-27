import assert from 'node:assert/strict'
import { test } from 'node:test'
import { LANDMARKS } from '../shared/landmarks.js'
import { createMapSearchIndex, searchMap } from './map-search.js'

const nanjing = { id: 'city-nanjing', name: '南京市', kind: 'city', lon: 118.8, lat: 32, subtitle: '江苏省' }
const innerMongolia = { id: 'province-inner-mongolia', name: '内蒙古自治区', kind: 'province', lon: 111.7, lat: 40.8 }
const boundaries = { islandLabels: [{ name: '钓鱼岛', lon: 123.475, lat: 25.745 }] }
const index = createMapSearchIndex(boundaries, [nanjing, innerMongolia])

function first(query) {
  return searchMap(index, query)[0]
}

test('results preserve the model anchor and existing map-label coordinates', () => {
  const landmark = LANDMARKS.find(place => place.id === 'zhongshan')
  const result = first('中山陵')
  assert.equal(result.landmark, landmark)
  assert.deepEqual([result.lon, result.lat], landmark.anchor)
  assert.equal(result.kind, 'landmark')
  assert.equal(first('秦岭').kind, 'landform')
  assert.equal(first('渤海').water, true)
  assert.equal(first('钓鱼岛').island, true)
  assert.deepEqual([first('钓鱼岛').lon, first('钓鱼岛').lat], [123.475, 25.745])
})

test('matches administrative names and landmark aliases before partial matches', () => {
  assert.equal(first('南京'), nanjing)
  assert.equal(first('内蒙古'), innerMongolia)
  assert.equal(first('故宫').id, 'gugong')
  assert.equal(first('小蛮腰').id, 'canton-tower')
  assert.equal(first('台北１０１').id, 'taipei-101')
  assert.equal(first('三潭').id, 'west-lake')
})

test('accepts a locality before or after the attraction name', () => {
  assert.equal(first('北京 故宫').id, 'gugong')
  assert.ok(searchMap(index, '北京 故宫').every(({ subtitle }) => subtitle.includes('北京')))
  assert.equal(first('太和殿 北京市').id, 'gugong')
  assert.equal(first('江苏南京中山陵').id, 'zhongshan')
  assert.equal(first('阿坝九寨沟').id, 'jiuzhaigou')
})

test('tolerates omitted name characters, transpositions and a single typo', () => {
  assert.equal(first('故殿').id, 'gugong')
  assert.equal(first('中山凌').id, 'zhongshan')
  assert.equal(first('中陵山').id, 'zhongshan')
  assert.equal(first('杭州西乎').id, 'west-lake')
})

test('returns a bounded list and ignores empty or unmatched queries', () => {
  assert.equal(searchMap(index, '山', 3).length, 3)
  assert.deepEqual(searchMap(index, '山', 0), [])
  assert.deepEqual(searchMap(index, ' · '), [])
  assert.deepEqual(searchMap(index, '甲'), [])
  assert.deepEqual(searchMap(index, '无关搜索内容'), [])
})
