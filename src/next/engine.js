// Canvas, scaling and the clock for the 480x270 site (next.html).
//
// Carried over from 好结局's engine.js:
//   - The scene is always drawn on a 480x270 offscreen buffer and then upscaled once, by a
//     whole number, with nearest-neighbour. Positions are whole pixels (space is hard-edged);
//     changes over time (fades, drifts) are continuous.
//   - LOGIC RUNS ON setInterval, requestAnimationFrame ONLY DRAWS. rAF does not fire while the
//     page is hidden (a background tab, the desktop app's hidden preview pane), so nothing may
//     depend on it to advance.
// Different from 好结局: the window is filled. The scene takes the largest whole-number scale
// that fits (counted in device pixels, so a Retina screen gets finer steps), and the rest of
// the window shows a blurred, dimmed copy of the scene itself instead of black bars.

export const W = 480;
export const H = 270;
const NEAR_MISS = 0.92; // see Stage.layout

export function mkCanvas(w, h, opts) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  const x = c.getContext('2d', opts);
  x.imageSmoothingEnabled = false;
  return [c, x];
}

export const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
export const lerp = (a, b, t) => a + (b - a) * t;

// Integer -> 0..1, fixed. Used wherever something must look random but never change.
export function hash(n) {
  n = Math.imul((n | 0) ^ 0x9e3779b9, 0x85ebca6b);
  n ^= n >>> 13;
  n = Math.imul(n, 0xc2b2ae35);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}

export function rng(seed) {
  let s = (seed >>> 0) || 1;
  return () => {
    s ^= s << 13; s >>>= 0;
    s ^= s >>> 17;
    s ^= s << 5; s >>>= 0;
    return s / 4294967296;
  };
}

export function parseColor(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function mixColor(a, b, t) {
  const A = parseColor(a);
  const B = parseColor(b);
  return [0, 1, 2].map((i) => Math.round(lerp(A[i], B[i], t)));
}

export const rgb = (c, a = 1) => (a >= 1 ? `rgb(${c[0]},${c[1]},${c[2]})` : `rgba(${c[0]},${c[1]},${c[2]},${a})`);

// The stage: the display canvas, its size, and the body mode classes the CSS keys off.
// (Body classes instead of media queries, same reason as the current site: on a phone held
// upright #app is rotated a quarter turn, so the CSS viewport reports the wrong axis.)
export class Stage {
  constructor() {
    this.app = document.getElementById('app');
    this.canvas = document.getElementById('game');
    this.ctx = this.canvas.getContext('2d');
    this.backdrop = document.getElementById('backdrop');
    this.backCtx = this.backdrop.getContext('2d');
    this.scale = 1; // device pixels per scene pixel (whole number)
    this.touch = false;
    this.rotated = false;
    this.onLayout = null;
    const relayout = () => { this.layout(); if (this.onLayout) this.onLayout(); };
    window.addEventListener('resize', relayout);
    window.addEventListener('orientationchange', () => { setTimeout(relayout, 300); setTimeout(relayout, 900); });
    this.layout();
  }

  layout() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    this.touch = window.matchMedia('(pointer: coarse)').matches || Math.min(vw, vh) <= 520;
    this.rotated = this.touch && vh > vw;
    const stageW = this.rotated ? vh : vw;
    const stageH = this.rotated ? vw : vh;
    document.body.classList.toggle('rotated', this.rotated);
    document.body.classList.toggle('touch', this.touch);
    document.body.classList.toggle('compact', stageW < 760 || stageH < 500);
    document.body.classList.toggle('narrow', stageW < 560);
    this.app.style.width = `${stageW}px`;
    this.app.style.height = `${stageH}px`;

    const d = Math.min(window.devicePixelRatio || 1, 4);
    const fit = Math.min((stageW * d) / W, (stageH * d) / H); // device px per scene px, fractional
    // Desktop: the largest whole multiple that fits, shown 1:1 in device pixels. Phone: the
    // screen is small enough that filling it beats a pixel-perfect multiple, so the backing
    // store rounds UP and CSS shrinks it to the exact fit.
    // A window that misses the next multiple by a hair takes it anyway: the picture then
    // overhangs the stage by at most a few scene pixels per side (clipped by #app), which is
    // far less noticeable than a wide frame around it.
    const whole = fit - Math.floor(fit) > NEAR_MISS ? Math.ceil(fit) : Math.floor(fit);
    this.scale = Math.max(1, this.touch ? Math.ceil(fit) : whole);
    const cssScale = (this.touch ? fit : this.scale) / d;
    this.canvas.width = W * this.scale;
    this.canvas.height = H * this.scale;
    this.canvas.style.width = `${W * cssScale}px`;
    this.canvas.style.height = `${H * cssScale}px`;
  }

  // Client coords -> 0..1 across the scene canvas (handles the quarter-turn on phones).
  norm(clientX, clientY) {
    const r = this.canvas.getBoundingClientRect();
    if (this.rotated) return { nx: (clientY - r.top) / r.height, ny: (r.right - clientX) / r.width };
    return { nx: (clientX - r.left) / r.width, ny: (clientY - r.top) / r.height };
  }

  // The area around the scene: a tiny copy of the buffer, stretched over the whole stage by
  // CSS (smooth scaling + blur + dim, see next.css). It follows the scene's own colours, so
  // the frame is never a black bar.
  paintBackdrop(buf) {
    this.backCtx.imageSmoothingEnabled = true;
    this.backCtx.drawImage(buf, 0, 0, this.backdrop.width, this.backdrop.height);
  }
}

// Logic at a steady 60 Hz on a timer; drawing on rAF, only when something changed.
// A throttled timer (hidden page: about one tick a second) is caught up in sub-steps so the
// simulation keeps real time instead of running in slow motion.
const STEP = 1 / 60;
const MAX_CATCH_UP = 1.2;

export class Clock {
  constructor(update, draw) {
    this.update = update;
    this.draw = draw;
    this.time = 0;
    this.dirty = true;
    this._last = 0;
    this._acc = 0;
  }

  start() {
    this._last = performance.now();
    setInterval(() => this._tick(), 1000 / 60);
    const frame = () => {
      requestAnimationFrame(frame);
      if (!this.dirty) return;
      this.dirty = false;
      this.draw();
    };
    requestAnimationFrame(frame);
  }

  _tick() {
    const now = performance.now();
    this._acc += Math.min((now - this._last) / 1000, MAX_CATCH_UP);
    this._last = now;
    while (this._acc >= STEP) {
      this._acc -= STEP;
      this.step(STEP);
    }
  }

  // One logic step. Exposed so tests can advance the world deterministically.
  step(dt) {
    this.time += dt;
    try { this.update(dt); } catch (e) { console.error(e); }
    this.dirty = true;
  }
}
