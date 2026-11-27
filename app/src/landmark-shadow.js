import * as THREE from 'three'
import { createShadowGround } from './landmark-shadow-ground.js'

const MAP_SIZE = 192
const FILTER_TAPS = 24
const disk = new Float32Array(FILTER_TAPS * 2)
for (let i = 0; i < FILTER_TAPS; i++) {
  const angle = i * Math.PI * (3 - Math.sqrt(5))
  const radius = Math.sqrt((i + 0.5) / FILTER_TAPS)
  disk.set([Math.cos(angle) * radius, Math.sin(angle) * radius], i * 2)
}

// RG holds the packed light-space depth. Filtered alpha retains the silhouette at cutout edges.
const shadowDepth = `
  float landmarkDepth(vec4 sampleValue) {
    return unpackRGToDepth(sampleValue.rg) / max(sampleValue.a, 0.001);
  }
`

const fragmentShader = `
  #include <packing>
  ${shadowDepth}
  uniform sampler2D shadowMapLocal;
  uniform vec2 disk[${FILTER_TAPS}];
  varying vec3 lightPoint;
  varying vec2 groundOffset;

  float occlusion(vec4 sampleValue, float receiver) {
    return sampleValue.a * smoothstep(0.001, 0.005, receiver - landmarkDepth(sampleValue));
  }

  void main() {
    vec2 uv = lightPoint.xy;
    float edge = 1.0 - smoothstep(0.80, 1.0, length(groundOffset));
    if (edge <= 0.0 || any(lessThan(uv, vec2(-0.08))) || any(greaterThan(uv, vec2(1.08)))) discard;

    // Estimate the caster-to-ground gap. Higher features cast a wider penumbra.
    float gapSum = 0.0;
    float blockers = 0.0;
    for (int i = 0; i < 8; i++) {
      vec4 sampleValue = texture2D(shadowMapLocal, uv + 0.055 * disk[3 * i]);
      float weight = occlusion(sampleValue, lightPoint.z);
      gapSum += weight * (lightPoint.z - landmarkDepth(sampleValue));
      blockers += weight;
    }
    float gap = (gapSum + 0.06) / (blockers + 0.5);
    float radius = clamp(0.032 + 0.22 * gap, 0.032, 0.08);
    float coverage = 0.0;
    for (int i = 0; i < ${FILTER_TAPS}; i++) {
      coverage += occlusion(texture2D(shadowMapLocal, uv + radius * disk[i]), lightPoint.z);
    }
    float alpha = 0.38 * edge * coverage / float(${FILTER_TAPS});
    if (alpha < 0.002) discard;
    gl_FragColor = vec4(0.010, 0.013, 0.018, alpha);
    #include <colorspace_fragment>
  }
`

// The terrain and the model sample the same light-space map. On the model only direct
// daylight is blocked by another surface; ambient fill can still reach a shaded wall.
function shadeLandmark(model, uniforms) {
  const materials = new Set()
  model.traverse(object => {
    if (object.isMesh) for (const item of [object.material].flat()) materials.add(item)
  })
  for (const material of materials) {
    if (!material.isMeshStandardMaterial) continue
    material.onBeforeCompile = shader => {
      shader.uniforms.shadowMapLocal = uniforms.shadowMapLocal
      shader.uniforms.worldToLight = uniforms.worldToLight
      shader.vertexShader = shader.vertexShader.replace('#include <common>', `
        #include <common>
        uniform mat4 worldToLight;
        varying vec3 vLandmarkLight;
        #ifdef LANDMARK_AMBIENT
          attribute float landmarkAmbient;
          varying float vLandmarkAmbient;
        #endif
      `).replace('#include <project_vertex>', `
        #include <project_vertex>
        vLandmarkLight = (worldToLight * (modelMatrix * vec4(transformed, 1.0))).xyz * 0.5 + 0.5;
        #ifdef LANDMARK_AMBIENT
          vLandmarkAmbient = landmarkAmbient;
        #endif
      `)
      shader.fragmentShader = shader.fragmentShader.replace('#include <packing>', `
        #include <packing>
        ${shadowDepth}
        uniform sampler2D shadowMapLocal;
        varying vec3 vLandmarkLight;
        #ifdef LANDMARK_AMBIENT
          varying float vLandmarkAmbient;
        #endif
        float blocked(vec2 offset, float bias) {
          vec4 tap = texture2D(shadowMapLocal, vLandmarkLight.xy + offset / ${MAP_SIZE.toFixed(1)});
          return tap.a * smoothstep(bias, bias + 0.0015, vLandmarkLight.z - landmarkDepth(tap));
        }
      `).replace('#include <aomap_fragment>', `
        #include <aomap_fragment>
        #ifdef LANDMARK_AMBIENT
          reflectedLight.indirectDiffuse *= vLandmarkAmbient;
        #endif
        #if NUM_DIR_LIGHTS > 0
          float incidence = clamp(dot(normal, directionalLights[0].direction), 0.05, 1.0);
          float slope = sqrt(1.0 - incidence * incidence) / incidence;
          float bias = 0.0006 + min(0.012, 0.0032 * slope);
          float shade = (2.0 * blocked(vec2(0.0), bias)
            + blocked(vec2(-0.9, -0.9), bias) + blocked(vec2(0.9, -0.9), bias)
            + blocked(vec2(-0.9, 0.9), bias) + blocked(vec2(0.9, 0.9), bias)) / 6.0;
          float sunlight = 1.0 - 0.88 * shade;
          reflectedLight.directDiffuse *= sunlight;
          reflectedLight.directSpecular *= sunlight;
          #ifdef USE_CLEARCOAT
            clearcoatSpecularDirect *= sunlight;
          #endif
        #endif
      `)
    }
    material.customProgramCacheKey = () => 'landmark-daylight'
    material.needsUpdate = true
  }
}

export function createLandmarkShadow(renderer, terrain, entry) {
  const { model, bounds, size, anchor, mount, pivot } = entry
  const diagonal = size.length()
  const half = diagonal * 0.62
  const camera = new THREE.OrthographicCamera(-half, half, half, -half, diagonal * 0.8, diagonal * 4)
  const center = bounds.getCenter(new THREE.Vector3())
  center.y -= bounds.min.y
  const castScene = new THREE.Scene()
  const caster = model.clone(true)
  const depthMaterial = new THREE.MeshDepthMaterial({ side: THREE.DoubleSide, depthPacking: THREE.RGDepthPacking })
  const materials = new Set([depthMaterial])
  function casterMaterial(original) {
    if (!original.alphaTest) return depthMaterial
    const cutout = depthMaterial.clone()
    cutout.map = original.map
    cutout.alphaMap = original.alphaMap
    cutout.alphaTest = original.alphaTest
    materials.add(cutout)
    return cutout
  }
  caster.traverse(object => {
    if (object.isMesh) object.material = Array.isArray(object.material)
      ? object.material.map(casterMaterial) : casterMaterial(object.material)
  })
  castScene.add(caster)

  const target = new THREE.WebGLRenderTarget(MAP_SIZE, MAP_SIZE, {
    minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false,
  })
  const lightMatrix = new THREE.Matrix4()
  const worldToLocal = new THREE.Matrix4()
  const uniforms = {
    shadowMapLocal: { value: target.texture }, disk: { value: disk },
    worldToLight: { value: new THREE.Matrix4() },
    anchor: { value: new THREE.Vector2(anchor.x, anchor.z) }, reach: { value: 1 },
  }
  shadeLandmark(model, uniforms)
  const material = new THREE.ShaderMaterial({
    uniforms, fragmentShader, transparent: true, depthWrite: false,
    polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
    vertexShader: `
      uniform mat4 worldToLight;
      uniform vec2 anchor;
      uniform float reach;
      varying vec3 lightPoint;
      varying vec2 groundOffset;
      void main() {
        lightPoint = (worldToLight * vec4(position, 1.0)).xyz * 0.5 + 0.5;
        groundOffset = (position.xz - anchor) / reach;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
  })
  const ground = createShadowGround(terrain, anchor, material)
  const footprint = Math.hypot(Math.max(-bounds.min.x, bounds.max.x), Math.max(-bounds.min.z, bounds.max.z))
  const localLight = new THREE.Vector3()
  const lastLight = new THREE.Vector3()
  const previousColor = new THREE.Color()

  function update(lightDirection) {
    ground.mesh.visible = pivot.visible
    if (!pivot.visible) return
    mount.updateWorldMatrix(true, false)
    worldToLocal.copy(mount.matrixWorld).invert()
    localLight.copy(lightDirection).transformDirection(worldToLocal)
    // Pan and zoom reuse the same model-space depth map.
    if (lastLight.distanceToSquared(localLight) > 0.00004) {
      camera.position.copy(center).addScaledVector(localLight, 2 * diagonal)
      camera.lookAt(center)
      camera.updateMatrixWorld()
      lightMatrix.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse)
      const previousTarget = renderer.getRenderTarget()
      const previousAlpha = renderer.getClearAlpha()
      renderer.getClearColor(previousColor)
      renderer.setRenderTarget(target)
      renderer.setClearColor(0, 0)
      renderer.render(castScene, camera)
      renderer.setRenderTarget(previousTarget)
      renderer.setClearColor(previousColor, previousAlpha)
      lastLight.copy(localLight)
    }
    uniforms.worldToLight.value.multiplyMatrices(lightMatrix, worldToLocal)
    const slope = Math.hypot(lightDirection.x, lightDirection.z) / lightDirection.y
    uniforms.reach.value = (footprint + size.y * slope + 0.55 * diagonal) * pivot.scale.x
    ground.update(uniforms.reach.value)
  }

  return {
    mesh: ground.mesh, update,
    invalidate: () => lastLight.set(0, 0, 0),
    dispose() {
      ground.dispose()
      material.dispose()
      for (const item of materials) item.dispose()
      target.dispose()
    },
  }
}
