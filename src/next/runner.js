// The run: stand at the tip of the pier, press Enter, and 晨 runs the lakeside walk for as
// long as she can keep clearing what has been left on it (bollards, crates, barrels, and a
// stack of crates that needs the mid-air hop).
//
// It is the old site's runner (src/runner/runner.js) rebuilt for the 480x270 street:
//   - the backdrop is the street's own scene, re-declared as endlessly tiling layers
//     (`runSceneDef`), so the two places are visibly the same world;
//   - instead of the old blackout venue swap, the light itself turns: every LIGHT_HOLD seconds
//     it drifts between sunrise and before-dawn. Both lights share their geometry, so nothing
//     is ever hidden while it changes;
//   - the spacing rule is the old one: an obstacle is only placed far enough ahead that the
//     jump it demands can be finished with REACTION_TIME to spare, at any speed.
//
// She stays at PLAYER_X on screen; the world scrolls under her (`scroll`, in scene pixels).

import { W, clamp, lerp, mixColor, rgb } from './engine.js';
import { Scene } from './scene.js';
import { drawText } from '../ui/pixelText.js';
import { t } from '../i18n.js';

export const RUN = {
  playerX: 110, // her fixed place on screen
  startSpeed: 230, // px/s the walk scrolls at
  maxSpeed: 400,
  accel: 4.5, // px/s gained per second of running
  gravity: 1300,
  jump: -360, // tops out about 50 px up, 0.55 s in the air
  jump2: -340, // the mid-air hop: about 44 px more from wherever it fires
  strideAt: 150, // the speed her run cycle was drawn for (it plays faster as she speeds up)
  lightHold: 24, // seconds in one light before it starts to turn
  lightTurn: 5, // seconds the turn takes
};

const BEST_KEY = 'dawn-run-best';
const REACTION_TIME = 0.5;
const GAP_HEADROOM = 1.15;
const MIN_GAP = 150;
const OPENING_GRACE = 1.3; // clear walk at the start of a run
const DEATH_INPUT_LOCK = 0.45; // ignore input right after a fall, so mashing does not skip it
const TALL_AFTER = 1400; // px run before the stack can appear at all
const TALL_CHANCE = [0.1, 0.3]; // its share of obstacles, rising over TALL_RAMP px
const TALL_RAMP = 16000;
const AIR_TIME = { 1: 0.56, 2: 1.05 }; // seconds the jump an obstacle demands takes

// Her collision box, relative to (PLAYER_X, the row under her soles): the cloak and body,
// not the hair or the trailing hem. Pulled in so a near miss reads as a miss.
const BOX = { left: -4, right: 6, top: -38, bottom: -2 };

// The street's scene.json, re-declared for an endless run: every layer tiles, the walk is a
// bare 960-px tile, the foreground keeps its grass but loses the tree, and nothing is a door.
export function runSceneDef(def) {
  const run = def.run;
  const tile = run.tile || 960;
  const layers = (def.layers || []).map((L) => {
    if (L.name === 'main') return { ...L, repeat: tile, images: [{ file: run.ground, x: 0, y: 0 }] };
    if (L.name === 'front' && run.front) return { ...L, repeat: tile, images: [{ file: run.front, x: 0, y: 0 }] };
    if (L.images && !L.repeat && L.k) return { ...L, repeat: tile, images: [L.images[0]] };
    return L;
  });
  return {
    ...def,
    layers,
    lights: (def.lights || []).filter((l) => (l.layer || 'main') !== 'main' && l.x < tile),
    stops: [],
    title: null,
  };
}

export async function loadRunner(street, figure, input, dust) {
  if (!street.def.run) return null;
  const scene = new Scene(`${street.name}-run`, street.base, runSceneDef(street.def));
  await scene.load();
  const load = (state) => new Promise((resolve) => {
    const im = new Image();
    im.onload = () => resolve(im);
    im.onerror = () => resolve(null);
    im.src = street.base + street.def.run.sheet.replace('{state}', state);
  });
  const sheets = await Promise.all(street.states.map(load));
  if (!sheets[0] && !sheets[1]) return null;
  return new Runner(scene, [sheets[0] || sheets[1], sheets[1] || sheets[0]], street.def.run.obstacles, figure, input, dust);
}

export class Runner {
  constructor(scene, sheets, types, figure, input, dust) {
    this.scene = scene;
    this.sheets = sheets;
    this.low = types.filter((o) => o.jumps < 2);
    this.tall = types.filter((o) => o.jumps >= 2);
    this.sheetH = sheets[0].height;
    this.figure = figure;
    this.input = input;
    this.dust = dust;
    this.ground = scene.ground;
    this.best = Number(localStorage.getItem(BEST_KEY)) || 0;
    this.mix = 1;
    this.reset();
  }

  get score() { return Math.floor(this.distance / 10); }

  // Start (or restart) a run. `mix` is the light it opens in; the pier is at sunrise.
  reset(mix = this.mix) {
    this.phase = 'run'; // 'run' | 'dead'
    this.items = []; // { type, x }  (x = world px of its left edge)
    this.scroll = 0;
    this.distance = 0;
    this.speed = RUN.startSpeed;
    this.air = 0;
    this.vy = 0;
    this.jumps = 0;
    this.stride = 0;
    this.animT = 0;
    this.deadT = 0;
    this.spawnHold = OPENING_GRACE;
    this.nextSpawn = W;
    this.mix = mix;
    this.lightFrom = mix;
    this.lightTo = mix;
    this.lightT = 0; // seconds into the current hold (then the turn)
    this.dustT = 0;
    this.hitItem = null;
    this.fallX = RUN.playerX;
    this.dust.list.length = 0;
  }

  // Returns 'exit' when the player asks to go back to the pier.
  update(dt) {
    const input = this.input;
    if (input.wasPressed('interact') && (this.phase === 'run' || this.deadT > DEATH_INPUT_LOCK)) return 'exit';
    this.dust.update(dt);

    if (this.phase === 'dead') {
      this.deadT += dt;
      this.animT += dt;
      if (this.deadT > DEATH_INPUT_LOCK && input.wasPressed('jump')) this.reset();
      return null;
    }

    this.speed = Math.min(RUN.maxSpeed, this.speed + RUN.accel * dt);
    this.scroll += this.speed * dt;
    this.distance += this.speed * dt;
    this.stride += dt * (this.speed / RUN.strideAt);
    this._light(dt);

    if (input.wasPressed('jump')) {
      if (this.air <= 0 && this.vy === 0) {
        this.vy = RUN.jump;
        this.jumps = 1;
      } else if (this.jumps < 2) {
        this.vy = RUN.jump2;
        this.jumps = 2;
        this._hopSparks();
      }
    }
    if (this.air > 0 || this.vy < 0) {
      this.vy += RUN.gravity * dt;
      this.air -= this.vy * dt;
      if (this.air <= 0) { this.air = 0; this.vy = 0; this.jumps = 0; this._land(); }
    }

    this._spawn(dt);
    this._runDust(dt);
    if (this._hit()) this._fall();
    return null;
  }

  // The light turns between the two states: hold, then a slow eased drift to the other one.
  _light(dt) {
    this.lightT += dt;
    if (this.lightT < RUN.lightHold) return;
    if (this.lightTo === this.lightFrom) this.lightTo = this.lightFrom > 0.5 ? 0 : 1;
    const u = clamp((this.lightT - RUN.lightHold) / RUN.lightTurn, 0, 1);
    this.mix = lerp(this.lightFrom, this.lightTo, u * u * (3 - 2 * u));
    if (u >= 1) { this.lightFrom = this.lightTo; this.lightT = 0; }
  }

  _spawn(dt) {
    const left = this.scroll - 60;
    if (this.items.length && this.items[0].x + this.items[0].type.w < left) this.items.shift();
    if (this.spawnHold > 0) { this.spawnHold -= dt; return; }
    if (this.scroll + W < this.nextSpawn) return;

    const type = this._pick();
    const x = Math.max(this.nextSpawn, this.scroll + W + 2);
    this.items.push({ type, x });
    const gap = this.speed * (AIR_TIME[type.jumps >= 2 ? 2 : 1] + REACTION_TIME + Math.random() * 0.55) * GAP_HEADROOM;
    this.nextSpawn = x + type.w + Math.max(gap, MIN_GAP);
  }

  _pick() {
    const any = (list) => list[Math.floor(Math.random() * list.length)];
    if (!this.tall.length || this.distance < TALL_AFTER) return any(this.low);
    const chance = lerp(TALL_CHANCE[0], TALL_CHANCE[1], clamp((this.distance - TALL_AFTER) / TALL_RAMP, 0, 1));
    return Math.random() < chance ? any(this.tall) : any(this.low);
  }

  _hit() {
    const feet = this.ground - this.air;
    const l = RUN.playerX + BOX.left;
    const r = RUN.playerX + BOX.right;
    const top = feet + BOX.top;
    const bottom = feet + BOX.bottom;
    for (const it of this.items) {
      const x = it.x - this.scroll;
      if (r <= x + 2 || l >= x + it.type.w - 2) continue;
      if (bottom > this.ground - it.type.h + 2 && top < this.ground) { this.hitItem = it; return true; }
    }
    return false;
  }

  _fall() {
    this.phase = 'dead';
    this.deadT = 0;
    this.animT = 0;
    this.air = 0;
    this.vy = 0;
    // She ends up face down in front of what she ran into, her head against it.
    this.fallX = Math.min(RUN.playerX, Math.round(this.hitItem.x - this.scroll) - 35); // frame 0 reaches 34 px right of her centre line
    if (this.score > this.best) {
      this.best = this.score;
      localStorage.setItem(BEST_KEY, String(this.best));
    }
    for (let i = 0; i < 18; i++) { // grit knocked loose where she went over
      const life = 0.4 + Math.random() * 0.3;
      this.dust.emit({
        x: RUN.playerX + 6, y: this.ground - 4 - Math.random() * 12,
        vx: 40 + Math.random() * 110, vy: -(40 + Math.random() * 110),
        g: 520, life, maxLife: life, size: Math.random() < 0.5 ? 2 : 1, color: this._dustColor(),
      });
    }
  }

  _dustColor() { return this.mix < 0.5 ? '#8f9cc4' : '#f1dca6'; }

  _runDust(dt) {
    if (this.air > 0) { this.dustT = 0; return; }
    this.dustT += dt;
    while (this.dustT >= 0.045) {
      this.dustT -= 0.045;
      const life = 0.3 + Math.random() * 0.18;
      this.dust.emit({
        x: RUN.playerX - 7 + (Math.random() * 4 - 2), y: this.ground - 2 - Math.random() * 4,
        vx: -(this.speed * 0.25 + Math.random() * 50), vy: -(18 + Math.random() * 34),
        g: 170, life, maxLife: life, size: Math.random() < 0.6 ? 2 : 1, color: this._dustColor(),
      });
    }
  }

  _land() {
    for (let i = 0; i < 6; i++) {
      const life = 0.22 + Math.random() * 0.14;
      const side = i % 2 ? 1 : -1;
      this.dust.emit({
        x: RUN.playerX + side * 4, y: this.ground - 2,
        vx: side * (20 + Math.random() * 50) - this.speed * 0.2, vy: -(10 + Math.random() * 30),
        g: 220, life, maxLife: life, size: 1, color: this._dustColor(),
      });
    }
  }

  _hopSparks() {
    const y = this.ground - this.air;
    for (let i = 0; i < 14; i++) {
      const angle = Math.PI * (i / 13);
      const speed = 50 + Math.random() * 60;
      const life = 0.26 + Math.random() * 0.16;
      this.dust.emit({
        x: RUN.playerX, y: y - 2, vx: Math.cos(angle) * speed - this.speed * 0.3, vy: Math.sin(angle) * speed * 0.5,
        g: 320, life, maxLife: life, size: Math.random() < 0.5 ? 2 : 1, color: '#ffe9a8',
      });
    }
  }

  // ---------------------------------------------------------------- drawing

  draw(g, time) {
    this.scene.render(g, this.scroll, this.mix, time, (gg) => {
      const dead = this.phase === 'dead';
      if (!dead) this._drawItems(gg);
      this.dust.draw(gg, 0);
      const state = {
        anim: dead ? 'fall' : this.air > 0 ? 'jump' : 'run',
        mix: this.mix, air: this.air, ground: this.ground, vy: this.vy, moveT: 1, stride: this.stride,
      };
      const x = dead ? Math.round(lerp(RUN.playerX, this.fallX, clamp(this.animT / 0.2, 0, 1))) : RUN.playerX;
      this.figure.draw(gg, x, this.ground - Math.round(this.air), 1, state, this.animT);
      if (dead) this._drawItems(gg); // what she tripped on stays in view, in front of her
    });
  }

  _drawItems(g) {
    const [a, b] = this.sheets;
    const shade = rgb(mixColor('#05060f', '#33210f', this.mix), lerp(0.3, 0.34, this.mix));
    const reach = Math.round(lerp(5, 16, this.mix)); // the sun is low: shadows stretch to the left
    for (const it of this.items) {
      const { type } = it;
      const x = Math.round(it.x - this.scroll);
      if (x > W || x + type.w < -20) continue;
      g.fillStyle = shade;
      g.fillRect(x - reach, this.ground, type.w + reach - 1, 1);
      g.fillRect(x - Math.round(reach * 0.6), this.ground + 1, type.w + Math.round(reach * 0.6) - 3, 1);
      const sy = this.sheetH - type.h;
      const dy = this.ground - type.h;
      if (this.mix < 1 || a === b) g.drawImage(a, type.x, sy, type.w, type.h, x, dy, type.w, type.h);
      if (this.mix > 0 && a !== b) {
        g.globalAlpha = this.mix;
        g.drawImage(b, type.x, sy, type.w, type.h, x, dy, type.w, type.h);
        g.globalAlpha = 1;
      }
    }
  }

  // Device-space pass (crisp text), drawn by the caller after the picture is on screen.
  drawHud(ctx, S, touch) {
    const light = this.mix < 0.5;
    const main = light ? '#f0f2ff' : '#2c2a48';
    const dim = light ? '#aeb8dc' : '#4d4a6a';
    const shade = light ? 'rgba(6, 8, 20, 0.5)' : 'rgba(255, 244, 214, 0.4)';
    const o = Math.max(1, Math.round(S / 3));
    const text = (s, x, y, opts) => {
      drawText(ctx, s, x + o, y + o, { ...opts, color: shade });
      drawText(ctx, s, x, y, opts);
    };
    const pad = (n) => String(n).padStart(5, '0');
    text(`${t('run.hi')} ${pad(this.best)}`, 14 * S, 12 * S, { sizePx: 8 * S, color: dim });
    text(pad(this.score), 14 * S, 23 * S, { sizePx: 14 * S, color: main });

    const cx = (W / 2) * S;
    if (this.phase === 'dead') {
      text(t('run.gameOver'), cx, 70 * S, { sizePx: 20 * S, color: main, align: 'center' });
      text(`${t('run.score')} ${pad(this.score)}    ${t('run.best')} ${pad(this.best)}`, cx, 98 * S, {
        sizePx: 9 * S, color: main, align: 'center',
      });
      if (this.deadT > DEATH_INPUT_LOCK) {
        text(t(touch ? 'run.retryTouchPier' : 'run.retryKeyPier'), cx, 114 * S, { sizePx: 7 * S, color: dim, align: 'center' });
      }
    } else if (this.distance < 500) {
      ctx.save();
      ctx.globalAlpha = clamp((500 - this.distance) / 150, 0, 1);
      text(t(touch ? 'run.howTouch' : 'run.howKey'), cx, 70 * S, { sizePx: 8 * S, color: dim, align: 'center' });
      ctx.restore();
    }
  }
}
