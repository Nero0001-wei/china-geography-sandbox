import assert from 'node:assert/strict'
import test from 'node:test'
import { createLandmarkClusters } from './landmark-clusters.js'

const model = (id, left, top = 0, city = '南京市') => ({
  id, city, left, top, right: left + 20, bottom: top + 20,
})

test('groups intersecting models in one city while keeping other cities and distant sites independent', () => {
  const update = createLandmarkClusters()
  assert.deepEqual(update([
    model('zhongshan', 0), model('qinhuai', 8, 6),
    model('huangshan', 0, 0, '黄山市'), model('distant', 80),
  ]), [['qinhuai', 'zhongshan']])
})

test('an existing pair needs more clearance to split than to stay split', () => {
  const update = createLandmarkClusters()
  const frame = gap => [model('zhongshan', 0), model('qinhuai', 20 + gap)]
  assert.deepEqual(update(frame(6)), [])
  assert.equal(update(frame(2)).length, 1)
  assert.equal(update(frame(6).reverse()).length, 1)
  assert.deepEqual(update(frame(14)), [])
  assert.deepEqual(update(frame(6)), [])
  assert.equal(update(frame(2)).length, 1)
})

test('transitive collisions form one stable group and disjoint pairs in a city stay separate', () => {
  const update = createLandmarkClusters()
  const items = [model('c', 40), model('b', 20), model('a', 0), model('e', 140), model('d', 120)]
  const groups = [['a', 'b', 'c'], ['d', 'e']]
  assert.deepEqual(update(items), groups)
  assert.deepEqual(update(items.reverse()), groups)
  assert.deepEqual(update([model('a', 0), model('b', 20), model('c', 80)]), [['a', 'b']])
})

test('viewport exits clear old links, and a different or missing city never joins a group', () => {
  const update = createLandmarkClusters()
  assert.equal(update([model('a', 0), model('b', 15)]).length, 1)
  assert.deepEqual(update([model('a', 0)]), [])
  assert.deepEqual(update([model('a', 0), model('b', 26)]), [])
  assert.deepEqual(update([model('a', 0, 0, ''), model('b', 0, 0, '')]), [])
  assert.deepEqual(update([model('a', 0), model('b', 0, 0, '北京市')]), [])
})
