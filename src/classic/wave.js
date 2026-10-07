// Classic page backdrop: "harmonic ridgelines" — a stack of thin lines across the middle of the
// screen, each one a slowly drifting sum of sine harmonics shaped like a spectrum, drawn back to
// front so nearer ridges hide the ones behind (the pulsar-plot look). The cursor swells the
// lines under it, and moving it "plucks" them: damped ripples spread out from the pluck point.
// Plain 2D canvas on a fixed full-screen layer; it dims once the hero has scrolled away so it
// never fights the body text.

const CREAM = '244, 233, 193';
const GOLD = '255, 224, 102';
const FILL = 'rgba(18, 17, 28, 0.94)'; // ≈ the page background, so ridges occlude what's behind

export function startWave(canvas) {
  const ctx = canvas.getContext('2d');
  if (!ctx) { canvas.remove(); return; }

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const small = window.matchMedia('(max-width: 760px)').matches;

  const LINES = small ? 20 : 32;
  const STEP = small ? 5 : 6; // px between samples along a line

  // Per-line randomness: harmonic phases and where the line's main "peaks" sit. On wide screens
  // the ridges rise on the right, clear of the hero text in the left column.
  const centre = small ? 0.5 : 0.68;
  const rand = mulberry32(142857);
  const lines = Array.from({ length: LINES }, () => ({
    phase: [0, 1, 2, 3].map(() => rand() * Math.PI * 2),
    peakA: centre + (rand() - 0.5) * 0.14,
    peakB: centre + (rand() - 0.5) * 0.4,
    weightB: 0.25 + rand() * 0.45,
  }));
  // Harmonics shared by all lines: spatial frequency (per px) and drift speed.
  const HARMONICS = [
    { f: 0.011, s: 0.55, a: 0.5 },
    { f: 0.023, s: -0.8, a: 0.28 },
    { f: 0.047, s: 1.3, a: 0.15 },
    { f: 0.093, s: -2.1, a: 0.07 },
  ];

  let w = 0, h = 0, dpr = 1;
  let top = 0, gap = 0, amp = 0;

  const mouse = { x: -9999, y: -9999, sx: -9999, sy: -9999, inside: false };
  const plucks = []; // { x, y, t0, a }
  let lastPluck = { x: 0, y: 0, t: 0 };

  const resize = () => {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const band = h * (small ? 0.26 : 0.4);
    top = h * (small ? 0.66 : 0.4);
    gap = band / (LINES - 1);
    amp = gap * (small ? 4 : 6.5);
    if (reduceMotion) draw(6);
  };

  const now = () => performance.now() / 1000;

  const onMove = (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.inside = true;
    // A pluck whenever the cursor has travelled far enough since the last one.
    const t = now();
    const d = Math.hypot(e.clientX - lastPluck.x, e.clientY - lastPluck.y);
    if (d > 70 && t - lastPluck.t > 0.12) {
      plucks.push({ x: e.clientX, y: e.clientY, t0: t, a: Math.min(1, d / 160) });
      if (plucks.length > 8) plucks.shift();
      lastPluck = { x: e.clientX, y: e.clientY, t };
    }
  };
  const onLeave = () => { mouse.inside = false; };

  function height(line, i, x, y0, t) {
    const u = x / w;
    // spectrum-shaped envelope: a tall central bump plus a secondary one
    const env =
      Math.exp(-(((u - line.peakA) / 0.13) ** 2)) +
      line.weightB * Math.exp(-(((u - line.peakB) / 0.07) ** 2));
    let n = 0;
    for (let k = 0; k < HARMONICS.length; k++) {
      const hk = HARMONICS[k];
      n += hk.a * Math.sin(hk.f * x + line.phase[k] + hk.s * t + i * 0.35);
    }
    let y = env * (0.55 + n) * amp + Math.abs(n) * amp * 0.06;

    // cursor swell
    if (mouse.sx > -999) {
      const dx = (x - mouse.sx) / 110;
      const dy = (y0 - mouse.sy) / 140;
      y += Math.exp(-dx * dx - dy * dy) * amp * 0.55;
    }
    // pluck ripples
    for (const p of plucks) {
      const age = t - p.t0;
      const d = Math.hypot(x - p.x, y0 - p.y);
      const front = d - age * 420; // ripple front travels outward
      y += p.a * amp * 0.35 * Math.exp(-age * 1.4) * Math.exp(-((front / 120) ** 2)) * Math.cos(front * 0.05);
    }
    return Math.max(y, -gap * 0.6);
  }

  function draw(t) {
    // ease the drawn cursor position toward the real one
    if (mouse.inside) {
      if (mouse.sx < -999) { mouse.sx = mouse.x; mouse.sy = mouse.y; }
      mouse.sx += (mouse.x - mouse.sx) * 0.12;
      mouse.sy += (mouse.y - mouse.sy) * 0.12;
    }
    while (plucks.length && t - plucks[0].t0 > 3) plucks.shift();

    ctx.clearRect(0, 0, w, h);
    // dim after the first screen so the lines sit quietly behind the content
    // (and on phones throughout, where the text spans the full width)
    ctx.globalAlpha = (small ? 0.55 : 1) * (1 - 0.6 * Math.min(1, window.scrollY / (h * 0.8)));

    // Lines fade out toward both edges — far more on the left, where the hero text sits —
    // and turn gold under the cursor (or at the ridge centre when there's no cursor).
    const cx = mouse.inside ? mouse.sx / w : centre;
    const stroke = ctx.createLinearGradient(0, 0, w, 0);
    if (small) {
      stroke.addColorStop(0, `rgba(${CREAM}, 0)`);
      stroke.addColorStop(0.2, `rgba(${CREAM}, 0.5)`);
      stroke.addColorStop(0.8, `rgba(${CREAM}, 0.5)`);
    } else {
      stroke.addColorStop(0, `rgba(${CREAM}, 0)`);
      stroke.addColorStop(0.3, `rgba(${CREAM}, 0.06)`);
      stroke.addColorStop(0.5, `rgba(${CREAM}, 0.5)`);
      stroke.addColorStop(0.9, `rgba(${CREAM}, 0.45)`);
    }
    stroke.addColorStop(Math.min(0.88, Math.max(0.32, cx)), `rgba(${GOLD}, 0.95)`);
    stroke.addColorStop(1, `rgba(${CREAM}, 0)`);
    ctx.strokeStyle = stroke;
    ctx.fillStyle = FILL;
    ctx.lineJoin = 'round';

    const baseAlpha = ctx.globalAlpha;
    for (let i = 0; i < LINES; i++) {
      const line = lines[i];
      const y0 = top + i * gap;
      ctx.beginPath();
      ctx.moveTo(0, y0);
      for (let x = 0; x <= w + STEP; x += STEP) {
        ctx.lineTo(x, y0 - height(line, i, x, y0, t));
      }
      // occlude the ridges behind, then stroke this one
      ctx.lineTo(w + STEP, y0 + 2);
      ctx.lineTo(0, y0 + 2);
      ctx.closePath();
      ctx.globalAlpha = baseAlpha;
      ctx.fill();
      ctx.globalAlpha = baseAlpha * (0.35 + 0.65 * (i / (LINES - 1))); // nearer = brighter
      ctx.lineWidth = 1;
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  resize();
  window.addEventListener('resize', resize);
  if (reduceMotion) return;

  window.addEventListener('mousemove', onMove, { passive: true });
  document.addEventListener('mouseleave', onLeave);
  const loop = () => {
    draw(now());
    requestAnimationFrame(loop);
  };
  loop();
}

// Small seeded PRNG so the ridges look the same on every visit.
function mulberry32(a) {
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
