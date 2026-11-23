// Atmosphere for the 480x270 scene: everything the art deliberately does NOT bake in.
//
//   water   a layer's rows slide left/right by 0..2 px, more near the viewer, almost none far
//           away; optional glints (short light bars that wink on the surface).
//   lights  window glows: an additive halo in three hard alpha steps around a lit window,
//           breathing a little, fading out as the day arrives.
//   clouds  sprites drifting left, each at its own speed, wrapping around.
//   fog     a band in three hard alpha steps with a wavy outline, drifting slowly.
//   shafts  low sun rays: hard-edged bars of added light, appearing once the sun is up.
//   motes   fireflies before dawn, dust in the light after.
//
// Rules carried over from 好结局's fx.js: offsets are whole pixels and edges are hard (no
// anti-aliasing, alpha comes in steps); changes over time are continuous.

import { W, H, mkCanvas, clamp, lerp, hash, mixColor, parseColor, rgb } from './engine.js';

const TAU = Math.PI * 2;

// ---------------------------------------------------------------- water
const WATER_PAD = 4; // the scratch is this much wider on each side, so shifted rows never show a gap
const [waterCvs, waterG] = mkCanvas(W + WATER_PAD * 2, H);

// `drawLayer(g, dx)` draws the layer (already cross-faded) with its x origin moved by dx.
export function drawWater(g, cfg, time, mix, drawLayer) {
  const y0 = clamp(Math.round(cfg.y0), 0, H);
  const y1 = clamp(Math.round(cfg.y1), y0, H);
  const amp = cfg.amp ?? 2;
  const speed = cfg.speed ?? 1;
  waterG.clearRect(0, 0, waterCvs.width, H);
  drawLayer(waterG, WATER_PAD);
  if (y0 > 0) g.drawImage(waterCvs, WATER_PAD, 0, W, y0, 0, 0, W, y0);
  if (y1 < H) g.drawImage(waterCvs, WATER_PAD, y1, W, H - y1, 0, y1, W, H - y1);
  // Rows with the same offset are copied as one strip.
  let runStart = y0;
  let runOff = null;
  for (let y = y0; y <= y1; y++) {
    let off = null;
    if (y < y1) {
      const depth = Math.pow((y - y0 + 1) / Math.max(1, y1 - y0), 0.8); // 0 far .. 1 near
      const wave = Math.sin(time * 1.3 * speed + y * 1.7 + Math.sin(y * 0.37) * 2.0)
        + 0.5 * Math.sin(time * 0.7 * speed - y * 0.9);
      off = Math.round(clamp(wave * 0.75, -1, 1) * amp * depth);
    }
    if (off !== runOff) {
      if (runOff !== null && y > runStart) {
        g.drawImage(waterCvs, WATER_PAD - runOff, runStart, W, y - runStart, 0, runStart, W, y - runStart);
      }
      runStart = y;
      runOff = off;
    }
  }
  if (cfg.glints) drawGlints(g, cfg, y0, y1, time, mix);
}

// Short bars of light on the water. Each one lives in its own time slot: it appears, holds,
// and goes, then turns up somewhere else. Nearer bars are longer.
function drawGlints(g, cfg, y0, y1, time, mix) {
  const n = cfg.glints;
  const col = mixColor(cfg.glintDawn || '#9fb0d8', cfg.glintSunrise || '#fff0c0', mix);
  const cx = cfg.glintX; // optional: keep them in a column (the sun's reflection)
  const spread = cfg.glintSpread ?? 60;
  g.save();
  g.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const period = 1.6 + hash(i * 7 + 1) * 2.4;
    const slot = Math.floor(time / period + hash(i * 7 + 2));
    const p = (time / period + hash(i * 7 + 2)) % 1;
    const a = Math.sin(p * Math.PI); // in and out, continuously
    if (a < 0.15) continue;
    const d = Math.pow(hash(slot * 131 + i * 17 + 3), 1.4); // more of them far away
    const y = Math.round(lerp(y0 + 2, y1 - 2, d));
    const len = Math.round(2 + d * 7);
    const x = cx != null
      ? Math.round(cx + (hash(slot * 31 + i * 5 + 4) - 0.5) * 2 * spread * (0.35 + d))
      : Math.round(hash(slot * 31 + i * 5 + 4) * (W - len));
    g.fillStyle = rgb(col, 0.42 * a);
    g.fillRect(x, y, len, 1);
  }
  g.restore();
}

// ---------------------------------------------------------------- lights
// A lit window's glow: the window rectangle grown outward with rounded corners, three hard
// steps. Built once per light as a small sprite, then drawn additively.
function lightSprite(l) {
  const r = l.r ?? Math.max(8, Math.round(Math.max(l.w, l.h) * 0.7));
  const steps = l.steps || [0.2, 0.11, 0.05];
  const w = l.w + r * 2;
  const h = l.h + r * 2;
  const [c, x] = mkCanvas(w, h);
  const im = x.createImageData(w, h);
  const [cr, cg, cb] = parseColor(l.color || '#ffc870');
  for (let py = 0; py < h; py++) {
    for (let px = 0; px < w; px++) {
      const dx = Math.max(r - px, px - (r + l.w - 1), 0);
      const dy = Math.max(r - py, py - (r + l.h - 1), 0);
      const d = Math.hypot(dx, dy);
      const a = d <= r / 3 ? steps[0] : d <= (r * 2) / 3 ? steps[1] : d <= r ? steps[2] : 0;
      if (!a) continue;
      const i = (py * w + px) * 4;
      im.data[i] = cr; im.data[i + 1] = cg; im.data[i + 2] = cb; im.data[i + 3] = Math.round(a * 255);
    }
  }
  x.putImageData(im, 0, 0);
  return { c, r };
}

export function prepareLights(lights) {
  return (lights || []).map((l, i) => ({ ...l, sprite: lightSprite(l), seed: i * 97 + 13 }));
}

// `repeat` is the layer's tiling period, if it tiles: its lights then repeat with it.
export function drawLights(g, lights, ox, time, mix, repeat = 0) {
  if (!lights.length) return;
  g.save();
  g.globalCompositeOperation = 'lighter';
  for (const l of lights) {
    let x = l.x - l.sprite.r + ox;
    if (repeat) { // the leftmost copy that can still reach the screen
      x = ((x % repeat) + repeat) % repeat - repeat;
      while (x + l.sprite.c.width < 0) x += repeat;
    }
    if (x > W || x + l.sprite.c.width < 0) continue;
    const day = l.fadeWithMix ? 1 - mix : 1;
    if (day <= 0.01) continue;
    const f = l.flicker || 0;
    const s = l.seed;
    const breathe = 0.5 + 0.25 * Math.sin(time * (1.1 + hash(s) * 0.8) + hash(s + 1) * TAU)
      + 0.25 * Math.sin(time * (3.3 + hash(s + 2) * 2) + hash(s + 3) * TAU);
    g.globalAlpha = clamp((l.alpha ?? 1) * day * (1 - f * breathe * 2), 0, 1);
    do {
      g.drawImage(l.sprite.c, x, l.y - l.sprite.r);
      x += repeat;
    } while (repeat && x < W);
  }
  g.restore();
}

// ---------------------------------------------------------------- clouds
export function drawCloud(g, c, img, imgB, cam, time, mix) {
  if (!img) return;
  const period = c.wrap || W + img.width + 200;
  let x = (c.x - time * (c.speed || 0) - cam * (c.k || 0)) % period;
  if (x < -img.width) x += period;
  x = Math.round(x);
  if (x >= W) return;
  if (mix < 1 || !imgB) g.drawImage(img, x, c.y);
  if (mix > 0 && imgB && imgB !== img) {
    g.globalAlpha = mix;
    g.drawImage(imgB, x, c.y);
    g.globalAlpha = 1;
  }
}

// ---------------------------------------------------------------- fog
// A tile of white with three alpha steps and a wavy, tileable outline; tinted when drawn.
const FOG_TILE = 512;

export function prepareFog(list) {
  return (list || []).map((f, i) => {
    const h = Math.max(6, Math.round(f.h));
    const [mask, mx] = mkCanvas(FOG_TILE, h);
    const im = mx.createImageData(FOG_TILE, h);
    const al = f.alpha || [0.1, 0.06, 0.03];
    const ph = [hash(i * 11 + 1) * TAU, hash(i * 11 + 2) * TAU, hash(i * 11 + 3) * TAU];
    const mid = (h - 1) / 2;
    for (let x = 0; x < FOG_TILE; x++) {
      const u = (x / FOG_TILE) * TAU;
      // Whole numbers of waves across the tile, so it repeats without a seam.
      const wob = 0.5 + 0.22 * Math.sin(u * 2 + ph[0]) + 0.16 * Math.sin(u * 5 + ph[1]) + 0.12 * Math.sin(u * 9 + ph[2]);
      const half = [0.34, 0.68, 1.0].map((k) => Math.round(mid * k * wob * 1.6));
      const lift = Math.round(Math.sin(u * 3 + ph[1]) * mid * 0.18);
      for (let y = 0; y < h; y++) {
        const d = Math.abs(y - mid - lift);
        const a = d <= half[0] ? al[0] : d <= half[1] ? al[1] : d <= half[2] ? al[2] : 0;
        if (!a) continue;
        const k = (y * FOG_TILE + x) * 4;
        im.data[k] = im.data[k + 1] = im.data[k + 2] = 255;
        im.data[k + 3] = Math.round(a * 255);
      }
    }
    mx.putImageData(im, 0, 0);
    const [tile, tg] = mkCanvas(FOG_TILE, h);
    return { ...f, h, mask, tile, tg, key: '' };
  });
}

export function drawFog(g, f, cam, time, mix, states) {
  const ca = typeof f.color === 'string' ? f.color : (f.color && f.color[states[0]]) || '#8fa3c8';
  const cb = typeof f.color === 'string' ? f.color : (f.color && f.color[states[1]]) || ca;
  const col = mixColor(ca, cb, Math.round(mix * 24) / 24);
  const key = col.join(',');
  if (key !== f.key) { // re-tint only when the colour actually moved
    f.key = key;
    f.tg.globalCompositeOperation = 'source-over';
    f.tg.clearRect(0, 0, FOG_TILE, f.h);
    f.tg.drawImage(f.mask, 0, 0);
    f.tg.globalCompositeOperation = 'source-in';
    f.tg.fillStyle = rgb(col);
    f.tg.fillRect(0, 0, FOG_TILE, f.h);
  }
  let x = Math.round(-(cam * (f.k ?? 0.5)) - time * (f.speed || 0)) % FOG_TILE;
  if (x > 0) x -= FOG_TILE;
  for (; x < W; x += FOG_TILE) g.drawImage(f.tile, x, Math.round(f.y));
}

// ---------------------------------------------------------------- shafts
// A ray is a bar starting at (x, y), running `len` along `angle`, `w` wide.
// ANGLE: degrees counter-clockwise from +x with y pointing UP (the maths convention), so the
// direction on screen is (cos a, -sin a). 200 = heading left and 20 degrees downward, which is
// what a low sun on the right gives.
// Rasterised row by row into spans, so the edges are hard.
function spansFor(s, widthScale) {
  const a = ((s.angle ?? 200) * Math.PI) / 180;
  const dx = Math.cos(a);
  const dy = -Math.sin(a);
  const nx = -dy;
  const ny = dx;
  const hw = ((s.w || 30) * widthScale) / 2;
  const len = s.len || 260;
  const pts = [
    [s.x + nx * hw, s.y + ny * hw], [s.x - nx * hw, s.y - ny * hw],
    [s.x - nx * hw + dx * len, s.y - ny * hw + dy * len], [s.x + nx * hw + dx * len, s.y + ny * hw + dy * len],
  ];
  const spans = [];
  for (let y = 0; y < H; y++) {
    const yc = y + 0.5;
    let lo = Infinity;
    let hi = -Infinity;
    for (let i = 0; i < 4; i++) {
      const [x0, y0] = pts[i];
      const [x1, y1] = pts[(i + 1) % 4];
      if ((y0 <= yc && y1 > yc) || (y1 <= yc && y0 > yc)) {
        const x = x0 + ((yc - y0) / (y1 - y0)) * (x1 - x0);
        if (x < lo) lo = x;
        if (x > hi) hi = x;
      }
    }
    if (hi > lo) spans.push([y, Math.round(lo), Math.round(hi)]);
  }
  return spans;
}

export function prepareShafts(list) {
  return (list || []).map((s, i) => ({ ...s, outer: spansFor(s, 1), core: spansFor(s, 0.45), seed: i * 53 + 7 }));
}

export function drawShaft(g, s, cam, time, mix, states) {
  const from = s.showFromMix ?? 0.5;
  const vis = clamp((mix - from) / (s.fadeIn ?? 0.25), 0, 1);
  if (vis <= 0) return;
  const breathe = 0.85 + 0.15 * Math.sin(time * 0.5 + hash(s.seed) * TAU);
  const ca = typeof s.color === 'string' ? s.color : (s.color && s.color[states[0]]) || '#cfd8f0';
  const cb = typeof s.color === 'string' ? s.color : (s.color && s.color[states[1]]) || '#ffe2a0';
  const col = mixColor(ca, cb, mix);
  const ox = Math.round(-(cam * (s.k || 0)));
  const a = (s.alpha ?? 0.1) * vis * breathe;
  g.save();
  g.globalCompositeOperation = 'lighter';
  g.fillStyle = rgb(col, a * 0.6);
  for (const [y, x0, x1] of s.outer) g.fillRect(x0 + ox, y, x1 - x0, 1);
  g.fillStyle = rgb(col, a * 0.4);
  for (const [y, x0, x1] of s.core) g.fillRect(x0 + ox, y, x1 - x0, 1);
  g.restore();
}

// ---------------------------------------------------------------- motes
export function prepareMotes(cfg, ground) {
  if (!cfg || !cfg.count) return null;
  const list = [];
  for (let i = 0; i < cfg.count; i++) {
    list.push({
      x: hash(i * 5 + 1) * (W + 40),
      u: hash(i * 5 + 2), // height within the band
      k: 0.7 + hash(i * 5 + 3) * 0.6,
      ph: hash(i * 5 + 4) * TAU,
      sp: 0.4 + hash(i * 5 + 5) * 0.9,
    });
  }
  return {
    list,
    kinds: [cfg.dawn || cfg.kind || 'firefly', cfg.sunrise || cfg.kind || 'dust'],
    ground,
    fly: cfg.fireflyColor || '#e6f2a8',
    dust: cfg.dustColor || '#fff0c8',
    yTop: cfg.yTop ?? 40,
  };
}

function drawFirefly(g, m, p, cam, time, a, col) {
  const period = W + 40;
  let x = (p.x - cam * p.k + Math.sin(time * 0.31 * p.sp + p.ph) * 14) % period;
  if (x < 0) x += period;
  x = Math.round(x - 20);
  const y = Math.round(m.ground - 8 - p.u * 62 + Math.sin(time * 0.53 * p.sp + p.ph * 2) * 5);
  const blink = clamp(Math.sin(time * (0.9 + p.sp * 0.6) + p.ph * 3) * 1.6 + 0.4, 0, 1); // dark part of the time
  const v = a * blink;
  if (v <= 0.03) return;
  g.fillStyle = rgb(col, 0.16 * v); // a small plus-shaped halo, then the spark itself
  g.fillRect(x - 1, y, 3, 1);
  g.fillRect(x, y - 1, 1, 3);
  g.fillStyle = rgb(col, 0.9 * v);
  g.fillRect(x, y, 1, 1);
}

function drawDust(g, m, p, cam, time, a, col) {
  const period = W + 40;
  let x = (p.x - cam * p.k - time * (2 + p.sp * 3)) % period;
  if (x < 0) x += period;
  x = Math.round(x - 20);
  const span = m.ground - m.yTop;
  const y = Math.round(m.yTop + ((p.u * span + time * (1 + p.sp * 1.5)) % span) + Math.sin(time * 0.4 + p.ph) * 3);
  const tw = 0.55 + 0.45 * Math.sin(time * (0.6 + p.sp) + p.ph * 5);
  g.fillStyle = rgb(col, 0.4 * a * tw);
  g.fillRect(x, y, 1, 1);
}

export function drawMotes(g, m, cam, time, mix) {
  if (!m) return;
  const cols = { firefly: m.fly, dust: m.dust };
  g.save();
  g.globalCompositeOperation = 'lighter';
  for (let side = 0; side < 2; side++) {
    const kind = m.kinds[side];
    const a = side === 0 ? 1 - mix : mix;
    if (a <= 0.02 || kind === 'none') continue;
    if (side === 1 && m.kinds[0] === kind) continue; // same kind on both sides: drawn once at full strength
    const strength = m.kinds[0] === m.kinds[1] ? 1 : a;
    const col = parseColor(cols[kind] || m.dust);
    for (const p of m.list) (kind === 'firefly' ? drawFirefly : drawDust)(g, m, p, cam, time, strength, col);
  }
  g.restore();
}
