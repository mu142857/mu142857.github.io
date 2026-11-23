// The layer of "light and air" over the whole picture: bloom, a faint haze, film grain and a
// vignette. Ported from 好结局's filter.js.
//
// Principle: not one pixel of the art underneath is touched. The 480x270 buffer is still
// upscaled by a whole number with nearest-neighbour; the filter is drawn AFTER that, on the
// display canvas. It is the one deliberate exception to "hard steps, no smooth gradients".
//
//   bloom     bright areas spill a very faint glow. The scene is halved three times (each an
//             average), only what is brighter than the threshold is kept, and it is scaled
//             back up smoothly and screened on. No ctx.filter = 'blur()': mobile Safari may
//             not have it.
//   haze      one very faint colour screened over everything: the darkest areas lift a touch.
//   grain     fine film grain: 6 pre-made noise tiles, swapped a few times a second at a
//             random offset. Blended with 'overlay', so grain in the dark stays dark.
//   vignette  the corners a little darker.
//
// Warmth: bloom and haze are scaled by how warm the scene is right now (0 cold .. 1 warm), so
// before dawn a lit window does not flood the cold street with glow; `coldKeep` is how much
// of them survives at 0.
//
// Tiers: 'full' everything, 'low' grain + vignette only (two full-screen draws), 'off' nothing.
// URL: ?filter=low / ?filter=off.

import { W, H, clamp, hash, rng, mixColor, rgb } from './engine.js';

export const FILTER = {
  on: true,
  tier: 'full',
  coldKeep: 0.35,
  bloom: { on: true, strength: 0.2, threshold: 0.6, range: 8 },
  haze: { on: true, strength: 0.04, cold: '#a8a2c4', warm: '#f0dcae' },
  grain: { on: true, strength: 0.09, size: 2, speed: 8 },
  vignette: { on: true, strength: 0.28, range: 0.5 },
};

const S = { chain: [], mid: null, has: false, grain: null, grainKey: '', pat: null, patCtx: null, vig: null, vigKey: '' };

const active = () => FILTER.on && FILTER.tier !== 'off';

function chainCanvas(slot, w, h, read) {
  let c = S.chain[slot];
  if (!c || c.cvs.width !== w || c.cvs.height !== h) {
    const cvs = document.createElement('canvas');
    cvs.width = w;
    cvs.height = h;
    const ctx = cvs.getContext('2d', { willReadFrequently: !!read });
    ctx.imageSmoothingEnabled = true;
    c = S.chain[slot] = { cvs, ctx };
  }
  return c;
}

// Call right after the scene is drawn into the buffer (before any text): keeps the bright
// parts, shrunk and smeared, for draw() to screen back on.
export function capture(src) {
  S.has = false;
  const B = FILTER.bloom;
  if (!active() || FILTER.tier !== 'full' || !B.on || !(B.strength > 0)) return;
  const steps = B.range >= 16 ? 4 : B.range >= 8 ? 3 : 2;
  let from = src;
  let w = W;
  let h = H;
  for (let i = 0; i < steps; i++) { // halve each time: every step is a 2x2 average
    w = Math.ceil(w / 2);
    h = Math.ceil(h / 2);
    const c = chainCanvas(i, w, h, i === steps - 1);
    c.ctx.clearRect(0, 0, w, h);
    c.ctx.drawImage(from, 0, 0, w, h);
    from = c.cvs;
  }
  const last = S.chain[steps - 1];
  const im = last.ctx.getImageData(0, 0, w, h);
  const px = im.data;
  const n = w * h;
  const th = clamp(B.threshold, 0, 0.98);
  const f = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { // keep only what is brighter than the threshold, colour as is
    const r = px[i * 4];
    const g = px[i * 4 + 1];
    const b = px[i * 4 + 2];
    const v = clamp(((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 - th) / (1 - th), 0, 1);
    f[i * 3] = r * v; f[i * 3 + 1] = g * v; f[i * 3 + 2] = b * v;
  }
  const t = new Float32Array(n * 3);
  for (let pass = 0; pass < 2; pass++) { // two 1-2-1 passes each way: a soft glow, not blocks
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 3;
        const l = (y * w + Math.max(0, x - 1)) * 3;
        const r = (y * w + Math.min(w - 1, x + 1)) * 3;
        for (let k = 0; k < 3; k++) t[i + k] = (f[l + k] + 2 * f[i + k] + f[r + k]) / 4;
      }
    }
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 3;
        const u = (Math.max(0, y - 1) * w + x) * 3;
        const d = (Math.min(h - 1, y + 1) * w + x) * 3;
        for (let k = 0; k < 3; k++) f[i + k] = (t[u + k] + 2 * t[i + k] + t[d + k]) / 4;
      }
    }
  }
  for (let i = 0; i < n; i++) {
    px[i * 4] = f[i * 3]; px[i * 4 + 1] = f[i * 3 + 1]; px[i * 4 + 2] = f[i * 3 + 2]; px[i * 4 + 3] = 255;
  }
  last.ctx.putImageData(im, 0, 0);
  // Scale up smoothly in two goes (x4 here, the rest on the display canvas): no diamond grid.
  const mid = chainCanvas(8, w * 4, h * 4, false);
  mid.ctx.drawImage(last.cvs, 0, 0, w * 4, h * 4);
  S.mid = mid.cvs;
  S.has = true;
}

function grainTiles(cell) {
  const key = String(cell);
  if (S.grainKey === key) return S.grain;
  const T = 256;
  const m = Math.max(8, Math.round(T / cell));
  const r = rng(90210);
  const tiles = [];
  for (let k = 0; k < 6; k++) {
    const small = document.createElement('canvas');
    small.width = small.height = m;
    const sx = small.getContext('2d');
    const im = sx.createImageData(m, m);
    const p = im.data;
    for (let i = 0; i < m * m; i++) { // around mid-grey: with 'overlay', mid-grey = no change
      const c = Math.round(128 + (r() - 0.5) * 2 * 120);
      p[i * 4] = p[i * 4 + 1] = p[i * 4 + 2] = c;
      p[i * 4 + 3] = 255;
    }
    sx.putImageData(im, 0, 0);
    const tile = document.createElement('canvas');
    tile.width = tile.height = m * cell;
    const tx = tile.getContext('2d');
    tx.imageSmoothingEnabled = false;
    tx.drawImage(small, 0, 0, m * cell, m * cell);
    tiles.push(tile);
  }
  S.grainKey = key;
  S.grain = tiles;
  S.pat = null;
  return tiles;
}

function vignetteImage(range) {
  const key = String(range);
  if (S.vigKey === key) return S.vig;
  const w = 256;
  const h = 144;
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  const x = c.getContext('2d');
  const R = Math.hypot(w / 2, h / 2);
  const g = x.createRadialGradient(w / 2, h / 2, R * clamp(range, 0, 0.95), w / 2, h / 2, R);
  g.addColorStop(0, 'rgba(6,10,18,0)');
  g.addColorStop(0.55, 'rgba(6,10,18,0.3)');
  g.addColorStop(1, 'rgba(6,10,18,1)');
  x.fillStyle = g;
  x.fillRect(0, 0, w, h);
  S.vigKey = key;
  S.vig = c;
  return c;
}

// Call after the buffer has been upscaled onto the display canvas. c = its context, s = the
// scale, warmth = 0..1 (how warm the scene is right now).
export function draw(c, s, warmth) {
  if (!active()) return;
  const sw = W * s;
  const sh = H * s;
  const full = FILTER.tier === 'full';
  const F = FILTER;
  const k = F.coldKeep + (1 - F.coldKeep) * clamp(warmth, 0, 1);
  c.save();
  c.imageSmoothingEnabled = true;
  if (full && S.has) {
    c.globalCompositeOperation = 'screen';
    c.globalAlpha = clamp(F.bloom.strength * k, 0, 1);
    c.drawImage(S.mid, 0, 0, sw, sh);
  }
  if (full && F.haze.on && F.haze.strength > 0) {
    c.globalCompositeOperation = 'screen';
    c.globalAlpha = clamp(F.haze.strength * k, 0, 1);
    c.fillStyle = rgb(mixColor(F.haze.cold, F.haze.warm, clamp(warmth, 0, 1)));
    c.fillRect(0, 0, sw, sh);
  }
  c.globalCompositeOperation = 'source-over';
  if (F.vignette.on && F.vignette.strength > 0) {
    c.globalAlpha = clamp(F.vignette.strength, 0, 1);
    c.drawImage(vignetteImage(F.vignette.range), 0, 0, sw, sh);
  }
  if (F.grain.on && F.grain.strength > 0) {
    // Size is in half CSS pixels, so it looks equally fine on a normal and a Retina screen.
    const cell = Math.max(1, Math.round((F.grain.size * (window.devicePixelRatio || 1)) / 2));
    const tiles = grainTiles(cell);
    const tick = Math.floor((performance.now() / 1000) * F.grain.speed);
    const tile = tiles[tick % tiles.length];
    const ox = Math.floor(hash(tick * 3 + 1) * tile.width);
    const oy = Math.floor(hash(tick * 3 + 2) * tile.height);
    c.imageSmoothingEnabled = false;
    c.globalCompositeOperation = 'overlay';
    c.globalAlpha = clamp(F.grain.strength, 0, 1);
    if (c.globalCompositeOperation !== 'overlay') c.globalAlpha *= 0.3; // very old browsers
    if (!S.pat || S.patCtx !== c) { S.pat = tiles.map((t) => c.createPattern(t, 'repeat')); S.patCtx = c; }
    c.translate(-ox, -oy); // one pattern fill instead of dozens of tile draws
    c.fillStyle = S.pat[tick % tiles.length];
    c.fillRect(ox, oy, sw, sh);
  }
  c.restore();
  c.imageSmoothingEnabled = false;
}
