import * as THREE from 'three'
import { METERS_TO_HEIGHT, SCENE_UNIT_METERS } from './terrain-data.js'

// Snap the patch edges to blocks so small zoom changes can reuse the geometry.
const CELL_BLOCK = 4

export function createShadowGround(terrain, anchor, material) {
  const { width, height, bounds } = terrain.metadata
  const spanX = (bounds.maxX - bounds.minX) / SCENE_UNIT_METERS
  const spanZ = (bounds.maxY - bounds.minY) / SCENE_UNIT_METERS
  const [column, row] = terrain.gridPoint(anchor.x, anchor.z)
  const mesh = new THREE.Mesh(new THREE.BufferGeometry(), material)
  let extent

  function update(radius) {
    const reachX = radius * (width - 1) / spanX
    const reachZ = radius * (height - 1) / spanZ
    const left = Math.max(0, Math.floor((column - reachX) / CELL_BLOCK) * CELL_BLOCK)
    const top = Math.max(0, Math.floor((row - reachZ) / CELL_BLOCK) * CELL_BLOCK)
    const right = Math.min(width - 1, Math.ceil((column + reachX) / CELL_BLOCK) * CELL_BLOCK)
    const bottom = Math.min(height - 1, Math.ceil((row + reachZ) / CELL_BLOCK) * CELL_BLOCK)
    if (extent && extent.left === left && extent.top === top && extent.right === right && extent.bottom === bottom) return
    extent = { left, top, right, bottom }

    const columns = right - left + 1
    const rows = bottom - top + 1
    const positions = new Float32Array(columns * rows * 3)
    const IndexArray = columns * rows > 65535 ? Uint32Array : Uint16Array
    const indices = new IndexArray((columns - 1) * (rows - 1) * 6)
    let offset = 0
    // Match atlas-surface's vertex positions and cell diagonals exactly, including on steep slopes.
    for (let y = top; y <= bottom; y++) {
      for (let x = left; x <= right; x++) {
        const i = (y - top) * columns + x - left
        positions[i * 3] = (x / (width - 1) - 0.5) * spanX
        positions[i * 3 + 1] = terrain.gridElevation(y * width + x) * METERS_TO_HEIGHT
        positions[i * 3 + 2] = (y / (height - 1) - 0.5) * spanZ
        if (x < right && y < bottom) {
          indices[offset++] = i
          indices[offset++] = i + columns
          indices[offset++] = i + 1
          indices[offset++] = i + 1
          indices[offset++] = i + columns
          indices[offset++] = i + columns + 1
        }
      }
    }
    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geometry.setIndex(new THREE.BufferAttribute(indices, 1))
    geometry.computeBoundingSphere()
    mesh.geometry.dispose()
    mesh.geometry = geometry
  }

  return { mesh, update, dispose: () => mesh.geometry.dispose() }
}
