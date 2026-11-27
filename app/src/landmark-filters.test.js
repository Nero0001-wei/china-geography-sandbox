import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ALL_LANDMARKS, allLandmarksSelected, matchesLandmark } from '../shared/landmark-filters.js'

const scenic = { type: 'nature', tier: 'national' }
const museum = { type: 'museum', tier: 'national' }
const localScenic = { type: 'nature', tier: 'regional' }
const historic = { type: 'heritage', tier: 'national' }

test('selects any checked type within the checked tiers', () => {
  const filter = { types: ['nature', 'museum'], tiers: ['national'], showNames: true }
  assert.deepEqual([scenic, museum, localScenic, historic].filter(place => matchesLandmark(place, filter)),
    [scenic, museum])
  filter.tiers = ['national', 'regional']
  assert.equal(matchesLandmark(localScenic, filter), true)
})

test('a cleared checklist excludes every landmark until an option is checked', () => {
  assert.equal(matchesLandmark(scenic, { ...ALL_LANDMARKS, types: [] }), false)
  assert.equal(matchesLandmark(scenic, { ...ALL_LANDMARKS, tiers: [] }), false)
})

test('the name setting is independent of landmark selection', () => {
  const filter = { ...ALL_LANDMARKS, showNames: false }
  assert.equal(allLandmarksSelected(filter), true)
  assert.equal(matchesLandmark(scenic, filter), true)
  assert.equal(allLandmarksSelected({ ...filter, tiers: ['national'] }), false)
})
