import * as THREE from 'three'

// All layout distances are CSS pixels, including when the WebGL canvas uses a higher DPR.
const SPACING = 46
const LENGTH = 4.5
const HALF_WIDTH = 1.45
const END_GAP = 12

function continuousRuns(drawings) {
  const runs = []
  const a = new THREE.Vector3()
  for (const { positions, airportPreview } of drawings) {
    if (airportPreview) continue
    let run
    for (let i = 0; i < positions.length; i += 6) {
      a.fromArray(positions, i)
      if (!run || run.world.at(-1).distanceToSquared(a) > 1e-16) {
        run = { world: [a.clone()], screen: [new THREE.Vector3()], distances: [0] }
        runs.push(run)
      }
      run.world.push(new THREE.Vector3().fromArray(positions, i + 3))
      run.screen.push(new THREE.Vector3())
      run.distances.push(0)
    }
  }
  return runs
}

export function createRouteArrows() {
  const geometry = new THREE.BufferGeometry()
  const material = new THREE.ShaderMaterial({
    uniforms: { ink: { value: new THREE.Color('#e7f4ff') } },
    // Positions have already been projected with the route's camera and height offset.
    vertexShader: 'void main() { gl_Position = vec4(position, 1.0); }',
    fragmentShader: `uniform vec3 ink;
      void main() {
        gl_FragColor = vec4(ink, 1.0);
        #include <colorspace_fragment>
      }`,
    depthWrite: false, transparent: true, side: THREE.DoubleSide,
  })
  material.forceSinglePass = true
  const mesh = new THREE.Mesh(geometry, material)
  mesh.name = 'Route direction arrows'
  mesh.renderOrder = 6
  mesh.frustumCulled = false
  mesh.visible = false

  const transform = new THREE.Matrix4()
  const tip = new THREE.Vector3()
  const tail = new THREE.Vector3()
  const vertices = []
  let runs = []

  function update(camera, width, height, yOffset) {
    transform.makeTranslation(0, yOffset, 0).premultiply(camera.matrixWorldInverse).premultiply(camera.projectionMatrix)
    vertices.length = 0
    function vertex(x, y, depth) {
      vertices.push(2 * x / width - 1, 2 * y / height - 1, depth)
    }
    for (const { world, screen, distances } of runs) {
      for (let i = 0; i < world.length; i++) {
        const p = screen[i].copy(world[i]).applyMatrix4(transform)
        p.x = (p.x + 1) * width / 2
        p.y = (p.y + 1) * height / 2
        if (i) distances[i] = distances[i - 1] + Math.hypot(p.x - screen[i - 1].x, p.y - screen[i - 1].y)
      }
      const total = distances.at(-1)
      for (let i = 1; i < screen.length; i++) {
        const a = screen[i - 1], b = screen[i]
        if (Math.max(a.x, b.x) < -LENGTH || Math.min(a.x, b.x) > width + LENGTH ||
            Math.max(a.y, b.y) < -LENGTH || Math.min(a.y, b.y) > height + LENGTH) continue
        const start = distances[i - 1], length = distances[i] - start
        if (length < 1e-8) continue
        // Clip the iteration range along the dominant axis. Even an edge stretching far
        // beyond the viewport then costs at most one screenful of marks at street zoom.
        const horizontal = Math.abs(b.x - a.x) >= Math.abs(b.y - a.y)
        const origin = horizontal ? a.x : a.y
        const delta = horizontal ? b.x - a.x : b.y - a.y
        const t0 = (-LENGTH - origin) / delta
        const t1 = ((horizontal ? width : height) + LENGTH - origin) / delta
        const visibleStart = start + length * Math.max(0, Math.min(t0, t1))
        const visibleEnd = Math.min(start + length * Math.min(1, Math.max(t0, t1)), total - END_GAP)
        const first = SPACING / 2 + SPACING * Math.max(0, Math.ceil((visibleStart - SPACING / 2) / SPACING))
        for (let d = first; d < visibleEnd; d += SPACING) {
          tip.lerpVectors(a, b, (d - start) / length)
          if (tip.x < -LENGTH || tip.x > width + LENGTH || tip.y < -LENGTH || tip.y > height + LENGTH) continue
          // Sample both ends on the same continuous path. Skip a chevron at a hairpin
          // where its straight chord would visibly cut across the bend.
          let j = i
          while (j > 1 && distances[j - 1] >= d - LENGTH) j--
          tail.lerpVectors(screen[j - 1], screen[j], (d - LENGTH - distances[j - 1]) / (distances[j] - distances[j - 1]))
          const dx = tip.x - tail.x, dy = tip.y - tail.y
          const chord = Math.hypot(dx, dy)
          if (chord < LENGTH * 0.90) continue
          const nx = -dy / chord * HALF_WIDTH, ny = dx / chord * HALF_WIDTH
          const notchZ = THREE.MathUtils.lerp(tail.z, tip.z, 0.43)
          for (const side of [-1, 1]) {
            vertex(tip.x, tip.y, tip.z)
            vertex(tail.x + nx * side, tail.y + ny * side, tail.z)
            vertex(tail.x + dx * 0.43, tail.y + dy * 0.43, notchZ)
          }
        }
      }
    }
    mesh.visible = vertices.length > 0
    if (!mesh.visible) return
    let buffer = geometry.getAttribute('position')
    if (!buffer || buffer.array.length < vertices.length) {
      geometry.dispose()
      const capacity = 18 * THREE.MathUtils.ceilPowerOfTwo(vertices.length / 18)
      buffer = new THREE.BufferAttribute(new Float32Array(capacity), 3).setUsage(THREE.DynamicDrawUsage)
      geometry.setAttribute('position', buffer)
    }
    buffer.array.set(vertices)
    buffer.clearUpdateRanges()
    buffer.addUpdateRange(0, vertices.length)
    buffer.needsUpdate = true
    geometry.setDrawRange(0, vertices.length / 3)
  }

  return {
    mesh, update,
    setDrawings(drawings) {
      runs = continuousRuns(drawings)
      mesh.visible = false
      geometry.setDrawRange(0, 0)
    },
    dispose() { geometry.dispose(); material.dispose() },
  }
}
