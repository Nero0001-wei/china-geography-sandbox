import { BufferAttribute } from 'three'

// Fraction of ambient light reaching a surface, from exposed faces to deep openings.
const shades = Uint8Array.from({ length: 16 }, (_, i) => Math.round(255 * (1 - 0.6 * i / 15)))
const crcTable = Uint32Array.from({ length: 256 }, (_, byte) => {
  let value = byte
  for (let i = 0; i < 8; i++) value = (value >>> 1) ^ ((value & 1) ? 0xedb88320 : 0)
  return value
})

export async function loadLandmarkOcclusion() {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}models/vertex-occlusion.bin`)
    if (!response.ok) return null
    const bytes = new Uint8Array(await response.arrayBuffer())
    if (bytes.length < 8 || String.fromCharCode(...bytes.subarray(0, 4)) !== 'LAO1') return null
    const start = 8 + new DataView(bytes.buffer).getUint32(4, true)
    if (start > bytes.length) return null
    const index = JSON.parse(new TextDecoder().decode(bytes.subarray(8, start)))
    return { index, weights: bytes.subarray(start) }
  } catch {
    return null
  }
}

// Hash the exact position, normal and index bytes, excluding interleaved neighbours and padding.
function checksum(geometry) {
  let crc = 0xffffffff
  for (const attr of [geometry.attributes.position, geometry.attributes.normal, geometry.index]) {
    if (!attr) continue
    const array = attr.isInterleavedBufferAttribute ? attr.data.array : attr.array
    const unit = array.BYTES_PER_ELEMENT
    const bytes = new Uint8Array(array.buffer, array.byteOffset, array.byteLength)
    const width = unit * attr.itemSize
    const stride = attr.isInterleavedBufferAttribute ? unit * attr.data.stride : width
    const offset = attr.isInterleavedBufferAttribute ? unit * attr.offset : 0
    for (let row = 0, start = offset; row < attr.count; row++, start += stride) {
      for (let j = start; j < start + width; j++) crc = (crc >>> 8) ^ crcTable[(crc ^ bytes[j]) & 255]
    }
  }
  return (crc ^ 0xffffffff) >>> 0
}

export function applyLandmarkOcclusion(gltf, id, cache) {
  const record = cache?.index?.[id]
  if (!Array.isArray(record)) return false
  const definitions = gltf.parser.json.meshes
  if (record.length !== definitions.length || record.some((parts, i) =>
    !Array.isArray(parts) || parts.length !== definitions[i].primitives.length)) return false
  const meshes = []
  gltf.scene.traverse(mesh => { if (mesh.isMesh) meshes.push(mesh) })
  const sections = new Map()
  for (const mesh of meshes) {
    const ref = gltf.parser.associations.get(mesh)
    const section = record[ref?.meshes]?.[ref?.primitives]
    const geometry = mesh.geometry
    if (!Array.isArray(section) || section.length !== 3 || !geometry.attributes.normal ||
        geometry.attributes.color || !geometry.attributes.position) return false
    const [start, count, expected] = section
    if (!Number.isInteger(start) || start < 0 || count !== geometry.attributes.position.count ||
        start + Math.ceil(count / 2) > cache.weights.length || checksum(geometry) !== expected) return false
    sections.set(geometry, section)
  }
  // Validate the entire model before modifying any mesh, so a newer GLB falls back as a unit.
  for (const [geometry, [start, count]] of sections) {
    const visibility = new Uint8Array(count)
    for (let i = 0; i < count; i++) {
      const pair = cache.weights[start + (i >> 1)]
      visibility[i] = shades[(i & 1) ? pair >> 4 : pair & 15]
    }
    geometry.setAttribute('landmarkAmbient', new BufferAttribute(visibility, 1, true))
  }
  for (const mesh of meshes) {
    for (const material of [mesh.material].flat()) {
      if (!material.isMeshStandardMaterial || material.defines.LANDMARK_AMBIENT) continue
      material.defines.LANDMARK_AMBIENT = 1
      material.needsUpdate = true
    }
  }
  return meshes.length > 0
}
