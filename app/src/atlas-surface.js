import * as THREE from 'three'
import { METERS_TO_HEIGHT, SCENE_UNIT_METERS } from './terrain-data.js'

const atlasURL = `${import.meta.env?.BASE_URL ?? './'}data/atlas/`

function registerTexture(texture, width, height, crop, anisotropy) {
  const [left, top, cropWidth, cropHeight] = crop
  texture.flipY = false
  texture.colorSpace = THREE.SRGBColorSpace
  texture.anisotropy = anisotropy
  texture.offset.set((0.5 - left) / cropWidth, (0.5 - top) / cropHeight)
  texture.repeat.set((width - 1) / cropWidth, (height - 1) / cropHeight)
  texture.needsUpdate = true
  return texture
}

export function makeAtlasSurface(terrain, atlas, image, renderer, invalidate) {
  const { width, height, bounds } = terrain.metadata
  const spanX = (bounds.maxX - bounds.minX) / SCENE_UNIT_METERS
  const spanZ = (bounds.maxY - bounds.minY) / SCENE_UNIT_METERS
  const anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy())
  const overview = registerTexture(new THREE.Texture(image), atlas.width, atlas.height,
    [0, 0, atlas.width, atlas.height], anisotropy)
  const roadsEnabled = { value: false }
  const roadPaper = new THREE.Color('#e5e9df')
  const paper = new THREE.Color(...atlas.paper.map(value => value / 255)).convertSRGBToLinear()
  const roadBackground = paper.clone().lerp(roadPaper, 0.76)
  function atlasMaterial() {
    const material = new THREE.MeshBasicMaterial({ map: overview })
    material.onBeforeCompile = shader => {
      shader.uniforms.roadMode = roadsEnabled
      shader.uniforms.roadPaper = { value: roadPaper }
      shader.fragmentShader = 'uniform bool roadMode;\nuniform vec3 roadPaper;\n' + shader.fragmentShader
      shader.fragmentShader = shader.fragmentShader.replace('#include <map_fragment>', `
        #include <map_fragment>
        if (roadMode) {
          vec3 original = diffuseColor.rgb;
          float water = smoothstep(0.025, 0.12, original.b - original.r)
                      * smoothstep(-0.02, 0.045, original.b - original.g);
          vec3 land = mix(original, roadPaper, 0.76);
          vec3 hydro = mix(original, vec3(0.48, 0.73, 0.83), 0.59);
          diffuseColor.rgb = mix(land, hydro, water);
        }`)
    }
    return material
  }
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(width * height * 3)
  const uvs = new Float32Array(width * height * 2)
  const indices = new Uint32Array((width - 1) * (height - 1) * 6)
  for (let row = 0; row < height; row++) {
    for (let column = 0; column < width; column++) {
      const index = row * width + column
      const u = column / (width - 1)
      const v = row / (height - 1)
      positions[index * 3] = (u - 0.5) * spanX
      positions[index * 3 + 1] = terrain.gridElevation(index) * METERS_TO_HEIGHT
      positions[index * 3 + 2] = (v - 0.5) * spanZ
      uvs[index * 2] = u
      uvs[index * 2 + 1] = v
    }
  }

  const materials = [atlasMaterial()]
  function createTile(entry, level) {
    const [left, top, right, bottom] = entry.cells
    const extent = new THREE.Box3(
      new THREE.Vector3((left / (width - 1) - 0.5) * spanX, -0.1, (top / (height - 1) - 0.5) * spanZ),
      new THREE.Vector3((right / (width - 1) - 0.5) * spanX, 2.2, (bottom / (height - 1) - 0.5) * spanZ),
    )
    const materialIndex = materials.push(atlasMaterial()) - 1
    return {
      entry, level, extent, materialIndex, children: [], start: 0, count: 0,
      texture: null, loading: false, wanted: false, visible: false, retryAfter: 0, distance: 0,
    }
  }

  const tiles = atlas.tiles.map(entry => createTile(entry, atlas))
  const fineTiles = (atlas.detail?.tiles ?? []).map(entry => createTile(entry, atlas.detail))
  const cols = width - 1
  const fineCoverage = new Uint8Array(cols * (height - 1))
  for (const child of fineTiles) {
    const [left, top, right, bottom] = child.entry.cells
    const parent = tiles.find(({ entry: { cells } }) =>
      left >= cells[0] && top >= cells[1] && right <= cells[2] && bottom <= cells[3])
    parent.children.push(child)
    for (let row = top; row < bottom; row++) {
      fineCoverage.fill(1, row * cols + left, row * cols + right)
    }
  }

  // Each parent is contiguous in the index buffer. Its uncovered cells come first,
  // then each fine tile. Switching images never overlaps or changes the terrain.
  let indexOffset = 0
  function writeCells(tile, skipChildren) {
    tile.start = indexOffset
    const [left, top, right, bottom] = tile.entry.cells
    for (let row = top; row < bottom; row++) {
      for (let column = left; column < right; column++) {
        if (skipChildren && fineCoverage[row * cols + column]) continue
        const i = row * width + column
        indices.set([i, i + width, i + 1, i + 1, i + width, i + width + 1], indexOffset)
        indexOffset += 6
      }
    }
    tile.count = indexOffset - tile.start
  }
  for (const tile of tiles) {
    writeCells(tile, tile.children.length > 0)
    for (const child of tile.children) writeCells(child, false)
    tile.total = indexOffset - tile.start
  }
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2))
  geometry.setIndex(new THREE.BufferAttribute(indices, 1))
  geometry.computeBoundingSphere()

  const mesh = new THREE.Mesh(geometry, materials)
  const loader = new THREE.TextureLoader()
  const frustum = new THREE.Frustum()
  const viewProjection = new THREE.Matrix4()
  let disposed = false
  let inFlight = 0
  let useRegional = false
  let useFine = false

  async function loadTile(tile) {
    tile.loading = true
    inFlight++
    try {
      const texture = await loader.loadAsync(atlasURL + tile.entry.file)
      if (!disposed && tile.wanted) {
        tile.texture = registerTexture(texture, tile.level.width, tile.level.height, tile.entry.crop, anisotropy)
        materials[tile.materialIndex].map = tile.texture
      } else {
        texture.dispose()
      }
    } catch {
      tile.retryAfter = performance.now() + 10_000
    } finally {
      tile.loading = false
      inFlight--
      if (!disposed) invalidate()
    }
  }

  function release(tile) {
    if (!tile.texture) return
    materials[tile.materialIndex].map = overview
    tile.texture.dispose()
    tile.texture = null
  }

  function draw(start, count, materialIndex) {
    if (!count) return
    const previous = geometry.groups.at(-1)
    if (previous?.materialIndex === materialIndex && previous.start + previous.count === start) {
      previous.count += count
    } else {
      geometry.addGroup(start, count, materialIndex)
    }
  }

  function update(camera, cssWidth, focus = new THREE.Vector3()) {
    camera.updateMatrixWorld()
    frustum.setFromProjectionMatrix(viewProjection.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse))
    const displayPixels = spanX / (camera.right - camera.left) * camera.zoom * cssWidth * renderer.getPixelRatio()
    // Smaller exit thresholds keep wheel and pinch gestures from toggling levels at the boundary.
    useRegional = displayPixels > image.width * (useRegional ? 0.7 : 0.85)
    useFine = displayPixels > atlas.width * (useFine ? 1.0 : 1.25)
    const pending = []
    const regional = []
    const fine = []
    const now = performance.now()
    function consider(tile, needed, candidates) {
      tile.wanted = false
      if (needed) {
        tile.distance = tile.extent.distanceToPoint(focus)
        candidates.push(tile)
      } else {
        release(tile)
      }
    }
    for (const tile of tiles) {
      tile.visible = frustum.intersectsBox(tile.extent)
      consider(tile, tile.visible && useRegional, regional)
      for (const child of tile.children) {
        child.visible = tile.visible && useFine && frustum.intersectsBox(child.extent)
        consider(child, child.visible, fine)
      }
    }
    // A wide, high-DPI screen can see dozens of tiles near a level change.
    // Budget each level's RGBA8 mip chains, loading the view center first.
    for (const candidates of [regional, fine]) {
      let remainingBytes = 112 * 1024 * 1024
      candidates.sort((a, b) => a.distance - b.distance)
      for (const tile of candidates) {
        const [, , w, h] = tile.entry.crop
        const bytes = w * h * 4 * 4 / 3
        if (bytes > remainingBytes) {
          release(tile)
          continue
        }
        remainingBytes -= bytes
        tile.wanted = true
        if (!tile.texture && !tile.loading && now >= tile.retryAfter) pending.push(tile)
      }
    }
    pending.sort((a, b) => a.distance - b.distance || a.materialIndex - b.materialIndex)
    for (const tile of pending) {
      if (inFlight >= 3) break
      loadTile(tile)
    }

    geometry.clearGroups()
    for (const tile of tiles) {
      if (!tile.visible) continue
      const baseMaterial = tile.texture ? tile.materialIndex : 0
      if (!tile.children.some(child => child.texture)) {
        draw(tile.start, tile.total, baseMaterial)
        continue
      }
      draw(tile.start, tile.count, baseMaterial)
      for (const child of tile.children) {
        if (child.visible) draw(child.start, child.count, child.texture ? child.materialIndex : baseMaterial)
      }
    }
  }

  return {
    mesh, update,
    setRoadMode(enabled) {
      roadsEnabled.value = enabled
      return enabled ? roadBackground : paper
    },
    dispose() {
      disposed = true
      overview.dispose()
      geometry.dispose()
      for (const tile of [...tiles, ...fineTiles]) release(tile)
      for (const material of materials) material.dispose()
    },
  }
}
