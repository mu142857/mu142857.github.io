// Scene loader and layer renderer.
//
// A scene is a folder under Assets/ with a scene.json (the contract is documented in
// art-src/greybox.py's output and in the report that accompanies this engine):
//
//   layers   back to front. Screen x of an image = image.x - round(camera * layer.k).
//            `repeat` tiles the layer horizontally with that period. The layer named
//            "player" has no images: it marks where the character is drawn.
//   states   two lightings of the same geometry ("dawn", "sunrise"). `{state}` in a file name
//            is replaced per state. The renderer cross-fades them by `mix` (0..1), which
//            follows the player's x through `mixByX`.
//   extras   lights / clouds / fog / shafts / motes — see fx.js. Each is slotted between the
//            layers by its own parallax factor `k` (drawn just before the first layer that
//            moves faster), or right after the layer named in `after`.
//
// Cross-fade: state A is drawn, then state B on top at alpha = mix. Because both states share
// their geometry, that is an exact blend wherever the art is opaque.

import { W, H, clamp, lerp } from './engine.js';
import {
  drawWater, prepareLights, drawLights, drawCloud, prepareFog, drawFog,
  prepareShafts, drawShaft, prepareMotes, drawMotes,
} from './fx.js';

function loadImage(src) {
  return new Promise((resolve) => {
    const im = new Image();
    im.onload = () => resolve(im);
    im.onerror = () => resolve(null); // a missing file is tolerated: the art arrives in pieces
    im.src = src;
  });
}

export async function loadScene(name) {
  const base = `Assets/${name}/`;
  const res = await fetch(`${base}scene.json`, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`No scene.json for scene "${name}"`);
  const def = await res.json();
  const scene = new Scene(name, base, def);
  await scene.load();
  return scene;
}

export class Scene {
  constructor(name, base, def) {
    this.name = name;
    this.base = base;
    this.def = def;
    this.length = def.length || W;
    this.ground = def.ground ?? 232;
    this.states = def.states && def.states.length ? def.states : ['default'];
    if (this.states.length === 1) this.states = [this.states[0], this.states[0]];
    this.stops = def.stops || [];
    this.title = def.title || null;
    this.spawn = def.spawn ?? 150;
    this.images = new Map(); // resolved path -> HTMLImageElement | null
    this.missing = [];
    this.fxOn = true;
  }

  _path(file, stateIndex) {
    return this.base + file.replace('{state}', this.states[stateIndex]);
  }

  // [imageA, imageB] for a file. A state whose file is missing falls back to the other one,
  // so a half-finished scene still shows something in both lights.
  pair(file) {
    const a = this.images.get(this._path(file, 0)) || null;
    const b = this.images.get(this._path(file, 1)) || null;
    return [a || b, b || a];
  }

  async load() {
    const def = this.def;
    const files = new Set();
    for (const L of def.layers || []) for (const im of L.images || []) files.add(im.file);
    for (const c of def.clouds || []) files.add(c.file);
    const paths = new Set();
    for (const f of files) { paths.add(this._path(f, 0)); paths.add(this._path(f, 1)); }
    await Promise.all([...paths].map(async (p) => {
      const im = await loadImage(p);
      this.images.set(p, im);
      if (!im) this.missing.push(p);
    }));
    if (this.missing.length) console.warn(`[scene ${this.name}] missing images:\n` + this.missing.join('\n'));

    // The draw list: layers in order, with the extras slotted in between.
    const lights = prepareLights(def.lights);
    this.items = (def.layers || []).map((L) => ({
      type: L.name === 'player' ? 'player' : 'layer',
      k: L.name === 'player' ? 1 : (L.k ?? 1),
      layer: L,
      lights: lights.filter((l) => (l.layer || 'main') === L.name),
    }));
    if (!this.items.some((it) => it.type === 'player')) this._insert({ type: 'player', k: 1 }, 1);
    for (const c of def.clouds || []) this._insert({ type: 'cloud', cloud: c }, c.k ?? 0.02, c.after);
    for (const f of prepareFog(def.fog)) this._insert({ type: 'fog', fog: f }, f.k ?? 0.5, f.after);
    for (const s of prepareShafts(def.shafts)) this._insert({ type: 'shaft', shaft: s }, s.z ?? 1, s.after);
    const motes = prepareMotes(def.motes, this.ground);
    if (motes) this._insert({ type: 'motes', motes }, def.motes.z ?? 1, def.motes.after);
  }

  // Put an extra just before the first LAYER that moves faster than k (so k = 1 lands in front
  // of the main layer and the player, behind the foreground), or right after layer `after`.
  _insert(item, k, after) {
    let at = this.items.length;
    if (after) {
      const i = this.items.findIndex((it) => it.layer && it.layer.name === after);
      if (i >= 0) at = i + 1;
    } else {
      const i = this.items.findIndex((it) => (it.type === 'layer' || it.type === 'player') && it.k > k);
      if (i >= 0) at = i;
    }
    this.items.splice(at, 0, item);
  }

  // 0..1: how far the light has moved from the first state to the second, for a player at x.
  mixAt(x) {
    const pts = this.def.mixByX;
    if (!pts || !pts.length) return 0;
    if (x <= pts[0][0]) return pts[0][1];
    for (let i = 1; i < pts.length; i++) {
      if (x <= pts[i][0]) {
        const [x0, m0] = pts[i - 1];
        const [x1, m1] = pts[i];
        return lerp(m0, m1, (x - x0) / Math.max(1, x1 - x0));
      }
    }
    return pts[pts.length - 1][1];
  }

  // How warm the scene is right now (0 cold .. 1 warm): the filter scales its glow by it.
  warmthAt(mix) {
    const w = this.def.warmth;
    if (!w) return mix;
    return lerp(w[this.states[0]] ?? 0, w[this.states[1]] ?? 1, mix);
  }

  stopAt(x) {
    return this.stops.find((s) => x >= s.x0 && x <= s.x1) || null;
  }

  _drawImages(g, L, cam, mix, dx) {
    const ox = -Math.round(cam * (L.k ?? 1)) + dx;
    for (const im of L.images || []) {
      const [a, b] = this.pair(im.file);
      if (!a) continue;
      const draw = (x) => {
        if (x >= W + 8 || x + a.width <= -8) return;
        if (mix < 1 || b === a) g.drawImage(a, x, im.y || 0);
        if (mix > 0 && b !== a) {
          g.globalAlpha = mix;
          g.drawImage(b, x, im.y || 0);
          g.globalAlpha = 1;
        }
      };
      if (L.repeat) {
        let x = ((im.x || 0) + ox) % L.repeat;
        if (x > 0) x -= L.repeat;
        // Step back far enough that an image wider than the period still covers the left edge.
        while (x + a.width > 0) x -= L.repeat;
        for (x += L.repeat; x < W + 8; x += L.repeat) draw(x);
      } else {
        draw((im.x || 0) + ox);
      }
    }
  }

  // Draw the whole scene into g (the 480x270 buffer). `drawPlayer(g)` is called at the
  // player's place in the stack.
  render(g, cam, mix, time, drawPlayer) {
    mix = clamp(mix, 0, 1);
    g.globalAlpha = 1;
    g.globalCompositeOperation = 'source-over';
    g.clearRect(0, 0, W, H);
    const fx = this.fxOn;
    for (const it of this.items) {
      switch (it.type) {
        case 'layer': {
          const L = it.layer;
          const water = fx && L.fx && L.fx.water;
          if (water) drawWater(g, water, time, mix, (wg, dx) => this._drawImages(wg, L, cam, mix, dx));
          else this._drawImages(g, L, cam, mix, 0);
          if (fx && it.lights.length) drawLights(g, it.lights, -Math.round(cam * (L.k ?? 1)), time, mix, L.repeat || 0);
          break;
        }
        case 'player':
          if (drawPlayer) drawPlayer(g);
          break;
        case 'cloud': {
          const [a, b] = this.pair(it.cloud.file);
          drawCloud(g, it.cloud, a, b, cam, fx ? time : 0, mix);
          break;
        }
        case 'fog':
          if (fx) drawFog(g, it.fog, cam, time, mix, this.states);
          break;
        case 'shaft':
          if (fx) drawShaft(g, it.shaft, cam, time, mix, this.states);
          break;
        case 'motes':
          if (fx) drawMotes(g, it.motes, cam, time, mix);
          break;
      }
    }
  }
}
