export function disposeModel(scene) {
  const geometries = new Set()
  const materials = new Set()
  const textures = new Set()
  scene.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry)
    for (const material of [object.material].flat()) {
      if (!material || materials.has(material)) continue
      materials.add(material)
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value)
    }
  })
  const images = new Set([...textures].map((texture) => texture.source.data))
  for (const image of images) image?.close?.()
  for (const texture of textures) texture.dispose()
  for (const material of materials) material.dispose()
  for (const geometry of geometries) geometry.dispose()
}
