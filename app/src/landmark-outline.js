import * as THREE from 'three'

const PADDING = 4
const MASK_SCALE = 2

// Draw only the active model into a small mask at screen resolution. The outline follows
// the assembled silhouette, so adjacent meshes do not acquire seams between them.
export function createLandmarkOutline(renderer) {
  const maskScene = new THREE.Scene()
  const maskCamera = new THREE.OrthographicCamera()
  const target = new THREE.WebGLRenderTarget(1, 1, { depthBuffer: false })
  const maskMaterial = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, depthTest: false, depthWrite: false })
  const cutouts = new Map()
  const clearColor = new THREE.Color()
  let activeModel = null
  let caster = null

  const uniforms = {
    mask: { value: target.texture },
    pixel: { value: new THREE.Vector2() },
    rect: { value: new THREE.Vector4() },
    lineColor: { value: new THREE.Color('#ffe3a0') },
    edgeColor: { value: new THREE.Color('#2c382a') },
  }
  const material = new THREE.ShaderMaterial({
    uniforms, transparent: true, depthTest: false, depthWrite: false,
    vertexShader: `
      uniform vec4 rect;
      varying vec2 maskUv;
      void main() {
        maskUv = uv;
        gl_Position = vec4(rect.xy + position.xy * rect.zw, 0.0, 1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D mask;
      uniform vec2 pixel;
      uniform vec3 lineColor;
      uniform vec3 edgeColor;
      varying vec2 maskUv;

      float expandedMask(float radius) {
        vec2 axis = pixel * radius;
        vec2 diagonal = axis * 0.70710678;
        return max(max(
          max(texture2D(mask, maskUv + vec2(axis.x, 0.0)).a, texture2D(mask, maskUv - vec2(axis.x, 0.0)).a),
          max(texture2D(mask, maskUv + vec2(0.0, axis.y)).a, texture2D(mask, maskUv - vec2(0.0, axis.y)).a)
        ), max(
          max(texture2D(mask, maskUv + diagonal).a, texture2D(mask, maskUv - diagonal).a),
          max(texture2D(mask, maskUv + vec2(diagonal.x, -diagonal.y)).a, texture2D(mask, maskUv + vec2(-diagonal.x, diagonal.y)).a)
        ));
      }

      void main() {
        float outside = 1.0 - texture2D(mask, maskUv).a;
        float line = expandedMask(1.45);
        float edge = max(line, expandedMask(2.15));
        gl_FragColor = vec4(mix(edgeColor, lineColor, line / max(edge, 0.001)), outside * edge);
        #include <colorspace_fragment>
      }
    `,
  })
  const geometry = new THREE.PlaneGeometry(2, 2)
  const quad = new THREE.Mesh(geometry, material)
  quad.frustumCulled = false
  const overlay = new THREE.Scene()
  const overlayCamera = new THREE.Camera()
  overlay.add(quad)

  function materialFor(source) {
    if (!source.alphaTest) return maskMaterial
    if (!cutouts.has(source)) {
      const cutout = maskMaterial.clone()
      cutout.map = source.map
      cutout.alphaMap = source.alphaMap
      cutout.alphaTest = source.alphaTest
      cutouts.set(source, cutout)
    }
    return cutouts.get(source)
  }

  function setModel(model) {
    maskScene.clear()
    for (const cutout of cutouts.values()) cutout.dispose()
    cutouts.clear()
    activeModel = model
    caster = null
    if (!model) return
    caster = model.clone(true)
    caster.matrixAutoUpdate = false
    caster.traverse(object => {
      if (!object.isMesh) return
      object.material = Array.isArray(object.material) ? object.material.map(materialFor) : materialFor(object.material)
    })
    maskScene.add(caster)
  }

  return {
    render(model, camera, frame, width, height) {
      if (model !== activeModel) setModel(model)
      if (!caster) return
      const left = Math.max(0, Math.floor(frame.left - PADDING))
      const top = Math.max(0, Math.floor(frame.top - PADDING))
      const w = Math.min(width, Math.ceil(frame.right + PADDING)) - left
      const h = Math.min(height, Math.ceil(frame.bottom + PADDING)) - top
      if (w <= 0 || h <= 0) return

      caster.matrix.copy(model.matrixWorld)
      caster.matrixWorldNeedsUpdate = true
      maskCamera.copy(camera, false)
      maskCamera.setViewOffset(width, height, left, top, w, h)
      target.setSize(w * MASK_SCALE, h * MASK_SCALE)
      uniforms.pixel.value.set(1 / w, 1 / h)
      uniforms.rect.value.set((2 * left + w) / width - 1, 1 - (2 * top + h) / height, w / width, h / height)

      const previousTarget = renderer.getRenderTarget()
      const previousAlpha = renderer.getClearAlpha()
      renderer.getClearColor(clearColor)
      try {
        renderer.setRenderTarget(target)
        renderer.setClearColor(0, 0)
        renderer.clear(true, false, false)
        renderer.render(maskScene, maskCamera)
      } finally {
        renderer.setRenderTarget(previousTarget)
        renderer.setClearColor(clearColor, previousAlpha)
      }
      renderer.render(overlay, overlayCamera)
    },
    dispose() {
      setModel(null)
      target.dispose()
      maskMaterial.dispose()
      material.dispose()
      geometry.dispose()
    },
  }
}
