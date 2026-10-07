// Classic page backdrop: a field of points rolling as a wave behind the content, drawn with
// three.js on a fixed full-screen canvas. The wave flows sideways on its own and its crest
// eases toward the cursor; points thin out near the crest's centre and glow toward the edges,
// with two slow light bands sweeping across. Tinted to the site's warm cream.
//
// Adapted from the ThreeWaveBackground in github.com/mobyyyc/qiyuancai.

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js';

const COLOR = '#f4e9c1';

export function startWave(canvas) {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const small = window.matchMedia('(max-width: 760px)').matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch {
    canvas.remove(); // no WebGL — the page reads fine without the backdrop
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 8, 110);

  // Fewer points on phones: the per-frame update runs on the CPU.
  const cols = small ? 120 : 210;
  const rows = small ? 50 : 90;
  const count = cols * rows;
  const width = 220;
  const depth = 95;

  const baseX = new Float32Array(count);
  const baseZ = new Float32Array(count);
  const positions = new Float32Array(count * 3);
  const alphas = new Float32Array(count).fill(1);
  const intensities = new Float32Array(count).fill(1);

  let i = 0;
  for (let r = 0; r < rows; r++) {
    const z = (r / (rows - 1) - 0.5) * depth;
    for (let c = 0; c < cols; c++) {
      const x = (c / (cols - 1) - 0.5) * width;
      baseX[i] = x;
      baseZ[i] = z;
      positions[i * 3] = x;
      positions[i * 3 + 2] = z;
      i++;
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));
  geometry.setAttribute('intensity', new THREE.BufferAttribute(intensities, 1));

  const material = new THREE.PointsMaterial({
    color: COLOR,
    size: small ? 0.42 : 0.32,
    transparent: true,
    opacity: 0.7,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  });

  // Per-point alpha and brightness, patched into the stock points shader.
  material.onBeforeCompile = (shader) => {
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>',
        '#include <common>\nattribute float alpha;\nattribute float intensity;\nvarying float vAlpha;\nvarying float vIntensity;')
      .replace('#include <begin_vertex>',
        '#include <begin_vertex>\nvAlpha = alpha;\nvIntensity = intensity;');
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>',
        '#include <common>\nvarying float vAlpha;\nvarying float vIntensity;')
      .replace('vec4 diffuseColor = vec4( diffuse, opacity );',
        'vec4 diffuseColor = vec4( diffuse * vIntensity, opacity * vAlpha );');
  };

  const points = new THREE.Points(geometry, material);
  points.rotation.x = -0.22;
  scene.add(points);

  const posAttr = geometry.getAttribute('position');
  const alphaAttr = geometry.getAttribute('alpha');
  const intAttr = geometry.getAttribute('intensity');

  // Cursor → a point on the z=0 plane in the wave's local space; the crest lerps toward it.
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  const hit = new THREE.Vector3();
  const target = new THREE.Vector3();
  const center = new THREE.Vector3();
  let yLimit = 22;

  const onMouseMove = (e) => {
    ndc.set((e.clientX / window.innerWidth) * 2 - 1, -(e.clientY / window.innerHeight) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    if (!raycaster.ray.intersectPlane(plane, hit)) return;
    points.worldToLocal(hit);
    target.set(
      THREE.MathUtils.clamp(hit.x, -width * 0.45, width * 0.45),
      THREE.MathUtils.clamp(hit.y, -yLimit, yLimit),
      THREE.MathUtils.clamp(hit.z, -depth * 0.35, depth * 0.35),
    );
  };

  const update = (t) => {
    center.lerp(target, 0.05);
    const half = width * 0.5;
    const offset = t * 15;
    const light1 = center.x + Math.sin(t * 0.35) * width * 0.26;
    const light2 = center.x + Math.cos(t * 0.21 + 1.3) * width * 0.18;
    const pos = posAttr.array, alpha = alphaAttr.array, inten = intAttr.array;

    for (let p = 0; p < count; p++) {
      const x = ((baseX[p] + offset + half) % width) - half;
      const z0 = baseZ[p];

      const dist = Math.min(1, Math.abs(x - center.x) / (half * 0.95));
      const near = 1 - dist;
      const smooth = near * near * (3 - 2 * near);
      const spread = 0.04 + Math.pow(1 - smooth, 1.15) * 0.96;
      const ridgeY = center.y * (0.3 + smooth * 0.7);

      const yWave =
        Math.sin(x * 0.13 - t * 2.1 + z0 * 0.07) * 3.6 +
        Math.cos(x * 0.09 - t * 1.35 + z0 * 0.02) * 2.1 +
        Math.sin((x + z0) * 0.18 - t * 2.6) * 1.45 +
        Math.sin(x * 0.24 + t * 3.0) * Math.cos(z0 * 0.19 - t * 2.4) * 1.3;
      const y = ridgeY + yWave * spread * (0.3 + smooth * 1.05);

      const zBase = z0 + Math.sin(x * 0.06 - t * 1.8 + z0 * 0.05) * 2.8 + Math.cos(x * 0.04 + t * 1.1) * 1.2;
      const z = center.z + (zBase - center.z) * spread;

      pos[p * 3] = x;
      pos[p * 3 + 1] = y;
      pos[p * 3 + 2] = z;

      alpha[p] = Math.pow(dist, 1.65) * (0.9 + 0.1 * Math.sin(t * 1.7 + z0 * 0.08));

      const band1 = Math.exp(-(((x - light1) / (width * 0.12)) ** 2));
      const band2 = Math.exp(-(((x - light2) / (width * 0.17)) ** 2));
      const glow = Math.min(1, Math.abs(y - ridgeY) / 8);
      inten[p] = Math.min(1.9, 0.42 + band1 * 0.9 + band2 * 0.55 + glow * 0.35);
    }
    posAttr.needsUpdate = alphaAttr.needsUpdate = intAttr.needsUpdate = true;
    renderer.render(scene, camera);
  };

  const onResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight, false);
    const planeHeight = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * Math.abs(camera.position.z);
    yLimit = planeHeight * 0.4;
    if (reduceMotion) update(4); // a single still frame
  };

  onResize();
  window.addEventListener('resize', onResize);

  if (reduceMotion) return;

  window.addEventListener('mousemove', onMouseMove, { passive: true });
  const clock = new THREE.Clock();
  const loop = () => {
    update(clock.getElapsedTime());
    requestAnimationFrame(loop);
  };
  loop();
}
