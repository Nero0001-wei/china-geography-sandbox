import assert from 'node:assert/strict'
import test from 'node:test'
import { OrthographicCamera, Texture, TextureLoader, Vector3 } from 'three'
import { makeAtlasSurface } from './atlas-surface.js'

const terrain = {
  metadata: { width: 5, height: 3, bounds: { minX: 0, maxX: 400_000, minY: 0, maxY: 200_000 } },
  gridElevation: () => 0,
}
const tile = (file, cells) => ({ file, cells, crop: [0, 0, 64, 64] })
const atlas = {
  width: 128, height: 64, paper: [235, 232, 223],
  tiles: [tile('west', [0, 0, 2, 2]), tile('east', [2, 0, 4, 2])],
  detail: {
    width: 512, height: 256,
    tiles: [tile('north', [1, 0, 2, 1]), tile('south', [2, 1, 3, 2])],
  },
}
const renderer = { capabilities: { getMaxAnisotropy: () => 8 }, getPixelRatio: () => 1 }
const camera = new OrthographicCamera(-3, 3, 3, -3, 0.1, 100)
camera.position.set(0, 10, 0.01)
camera.lookAt(new Vector3())

function drawnCells(mesh) {
  const cells = []
  for (const { start, count, materialIndex } of mesh.geometry.groups) {
    const texture = mesh.material[materialIndex].map.name || 'overview'
    for (let i = start; i < start + count; i += 6) {
      const vertex = mesh.geometry.index.array[i]
      const cell = Math.floor(vertex / 5) * 4 + vertex % 5
      assert.equal(cells[cell], undefined, 'Each terrain cell must be drawn only once')
      cells[cell] = texture
    }
  }
  return cells
}

test('partial fine coverage retains parent textures while loading and releases late arrivals on zoom-out', async t => {
  const disposed = new Set()
  let finishSouth
  t.mock.method(TextureLoader.prototype, 'loadAsync', async url => {
    const texture = new Texture()
    texture.name = url.split('/').pop()
    texture.addEventListener('dispose', () => disposed.add(texture.name))
    if (texture.name === 'south') await new Promise(resolve => { finishSouth = resolve })
    return texture
  })
  const surface = makeAtlasSurface(terrain, atlas, { width: 32 }, renderer, () => {})
  t.after(() => surface.dispose())
  const update = width => surface.update(camera, width, new Vector3())
  const tick = () => new Promise(resolve => setImmediate(resolve))

  update(15)
  assert.equal(surface.mesh.geometry.groups.length, 1)
  assert.deepEqual(drawnCells(surface.mesh), Array(8).fill('overview'))

  update(90)
  await tick()
  update(90)
  const regional = ['west', 'west', 'east', 'east', 'west', 'west', 'east', 'east']
  assert.deepEqual(drawnCells(surface.mesh), regional)
  update(300)
  assert.deepEqual(drawnCells(surface.mesh), regional)
  await tick()
  update(300)
  assert.deepEqual(drawnCells(surface.mesh), ['west', 'north', 'east', 'east', 'west', 'west', 'east', 'east'])

  update(15)
  finishSouth()
  await tick()
  assert.deepEqual(drawnCells(surface.mesh), Array(8).fill('overview'))
  assert.deepEqual(disposed, new Set(['north', 'south', 'west', 'east']))
})

test('overview still covers all terrain cells with a two-level atlas', () => {
  const { detail, ...olderAtlas } = atlas
  const surface = makeAtlasSurface(terrain, olderAtlas, { width: 32 }, renderer, () => {})
  surface.update(camera, 15)
  assert.equal(surface.mesh.geometry.groups.length, 1)
  assert.deepEqual(drawnCells(surface.mesh), Array(8).fill('overview'))
  surface.dispose()
})
