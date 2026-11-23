// The character: movement, and — kept separate — how it is drawn.
//
// Drawing sits behind one small interface so the placeholder can be swapped for the real
// sprite sheet without touching anything else:
//
//     figure.draw(g, screenX, feetY, facing, state, t)
//
//   g        the 480x270 buffer's 2D context
//   screenX  the character's centre line, in buffer pixels
//   feetY    the row its soles rest on (the ground line, minus the jump height)
//   facing   1 = right, -1 = left
//   state    { anim: 'idle' | 'walk' | 'run' | 'stop' | 'jump' | 'lie' | 'getup', mix: 0..1,
//              air: px above the ground, ground: the ground row, vy: vertical speed (px/s, up
//              is negative), moveT: seconds since she stood still, stride: run-cycle clock }
//   t        seconds, for picking the animation frame
//
// Whatever the figure is, the light is the scene's: it comes from the RIGHT and low (the
// sunrise). `lightFrame` gives any frame a 1-px rim on its right-hand edge, and
// `drawContactShadow` puts a shadow under the feet that stretches away to the left.

import { mkCanvas, clamp, lerp, mixColor, rgb } from './engine.js';

// All movement numbers in one place. World units are buffer pixels (480 across).
export const TUNE = {
  walk: 150, // px/s: the speed 晨's run cycle was drawn for (The Cloud's RUN_SPEED)
  sprint: 1.5, // multiplier while Shift is held (the cycle plays that much faster)
  accel: 0.3, // seconds from standing to full speed (= her three push-off frames)
  decel: 0.2, // seconds to brake (= her two braking frames)
  gravity: 900, // px/s^2
  jump: -250, // px/s  (about 35 px high)
  jump2: -205, // the mid-air hop (about 23 px more)
  edge: 18, // how close to either end of the world the character may get
};

export class Player {
  constructor(ground, x, figure) {
    this.ground = ground;
    this.x = x;
    this.air = 0; // px above the ground
    this.vy = 0;
    this.facing = 1;
    this.anim = 'idle';
    this.animT = 0;
    this.sprinting = false;
    this.jumpsUsed = 0;
    this.auto = null; // { x, then }: walking somewhere on its own (a clicked door)
    this.farthest = x; // rightmost x reached, for fading the intro
    this.figure = figure || new PlaceholderFigure();
    this.onDoubleJump = null;
    this.vel = 0; // px/s along `facing`
    this.moveT = 0; // seconds since she last stood still (picks the push-off frames)
    this.stride = 0; // run-cycle clock, advancing with her speed
    this.intro = null; // { wait, up }: lying on the ground, then getting up
  }

  // Start the visit the way The Cloud starts: face down on the ground, then getting up.
  // `wait` seconds lying (any key cuts it short), then `up` seconds of the getting-up frames.
  lieDown(wait, up) {
    this.intro = { wait, up };
    this.anim = 'lie';
    this.animT = 0;
  }

  get grounded() { return this.air <= 0 && this.vy === 0; }

  walkTo(x, then) { this.auto = { x, then }; }

  update(dt, input, length) {
    let left = input.isDown('left');
    let right = input.isDown('right');
    let sprint = input.isDown('sprint');
    const jumpPressed = input.wasPressed('jump');

    if (this.intro) {
      const it = this.intro;
      this.animT += dt;
      if (this.anim === 'lie') {
        it.wait -= dt;
        if (it.wait <= 0 || left || right || jumpPressed) { this.anim = 'getup'; this.animT = 0; }
      } else if (this.animT >= it.up) {
        this.intro = null;
        this.anim = 'idle';
        this.animT = 0;
      }
      return;
    }

    if (this.auto) {
      if (left || right || jumpPressed) {
        this.auto = null; // any input of the player's own takes over
      } else {
        const d = this.auto.x - this.x;
        if (Math.abs(d) <= 2) {
          const then = this.auto.then;
          this.auto = null;
          this.x = Math.round(this.x + d);
          this.vel = 0;
          if (then) then();
        } else {
          left = d < 0;
          right = d > 0;
          sprint = Math.abs(d) > 160;
        }
      }
    }

    const moving = left !== right;
    this.sprinting = moving && sprint;
    const top = TUNE.walk * (this.sprinting ? TUNE.sprint : 1);
    if (moving) {
      const facing = left ? -1 : 1;
      if (facing !== this.facing) { this.facing = facing; this.vel *= 0.4; }
      this.vel = this.vel < top
        ? Math.min(top, this.vel + (top / TUNE.accel) * dt)
        : Math.max(top, this.vel - (TUNE.walk / TUNE.decel) * dt);
    } else {
      this.vel = Math.max(0, this.vel - (TUNE.walk / TUNE.decel) * dt);
    }
    if (this.vel > 0) {
      let step = this.facing * this.vel * dt;
      if (this.auto && Math.abs(step) > Math.abs(this.auto.x - this.x)) step = this.auto.x - this.x;
      this.x += step;
      this.moveT += dt;
      this.stride += dt * Math.max(0.6, this.vel / TUNE.walk);
    } else {
      this.moveT = 0;
      this.stride = 0;
    }
    const before = this.x;
    this.x = clamp(this.x, TUNE.edge, length - TUNE.edge);
    if (this.x !== before) this.vel = 0; // walked into the end of the world
    if (this.x > this.farthest) this.farthest = this.x;

    if (jumpPressed) {
      if (this.grounded) {
        this.vy = TUNE.jump;
        this.jumpsUsed = 1;
      } else if (this.jumpsUsed < 2) {
        this.vy = TUNE.jump2;
        this.jumpsUsed = 2;
        if (this.onDoubleJump) this.onDoubleJump(this.x, this.ground - this.air);
      }
    }
    if (!this.grounded || this.vy < 0) {
      this.vy += TUNE.gravity * dt;
      this.air -= this.vy * dt;
      if (this.air <= 0) {
        this.air = 0;
        this.vy = 0;
        this.jumpsUsed = 0;
      }
    }

    const anim = this.air > 0 ? 'jump'
      : moving ? (this.sprinting ? 'run' : 'walk')
        : this.vel > 0 ? 'stop' : 'idle';
    if (anim !== this.anim) { this.anim = anim; this.animT = 0; } else this.animT += dt;
  }

  draw(g, cam, mix) {
    const sx = Math.round(this.x - cam);
    const state = {
      anim: this.anim, mix, air: this.air, ground: this.ground,
      vy: this.vy, moveT: this.moveT, stride: this.stride,
    };
    this.figure.draw(g, sx, this.ground - Math.round(this.air), this.facing, state, this.animT);
  }
}

// ---------------------------------------------------------------- light shared by any figure

// Shadow on the ground under the feet. The light is low on the right, so beyond the dark
// patch under the soles a fainter strip runs off to the left, longer once the sun is up.
// Two hard alpha steps; it shrinks while the character is in the air.
export function drawContactShadow(g, screenX, ground, air, mix, halfWidth = 8) {
  const k = clamp(1 - air / 60, 0.25, 1);
  const col = mixColor('#05060f', '#33210f', mix);
  const hw = Math.max(2, Math.round(halfWidth * k));
  const cx = screenX - 1;
  g.fillStyle = rgb(col, lerp(0.34, 0.4, mix) * k);
  g.fillRect(cx - hw, ground, hw * 2, 1);
  g.fillRect(cx - hw + 2, ground + 1, hw * 2 - 4, 1);
  const len = Math.round(lerp(8, 30, mix) * k);
  g.fillStyle = rgb(col, lerp(0.14, 0.2, mix) * k);
  g.fillRect(cx - hw - len, ground, len, 1);
  g.fillRect(cx - hw - Math.round(len * 0.6), ground + 1, Math.round(len * 0.6) + 2, 1);
}

// Returns a canvas holding `frame` facing the right way, with a 1-px rim of light on the
// pixels that face right (the outermost opaque pixel of every row, and the top of the head).
// `frame` is any canvas / image whose character faces right.
const lightCache = new Map();
export function lightFrame(frame, key, facing, rimColor, rimAlpha) {
  const id = `${key}|${facing}|${rimColor.join(',')}|${rimAlpha.toFixed(2)}`;
  let out = lightCache.get(id);
  if (out) return out;
  if (lightCache.size > 1200) lightCache.clear();
  const w = frame.width;
  const h = frame.height;
  const [c, x] = mkCanvas(w, h, { willReadFrequently: true });
  if (facing < 0) { x.translate(w, 0); x.scale(-1, 1); }
  x.drawImage(frame, 0, 0);
  x.setTransform(1, 0, 0, 1, 0, 0);
  const im = x.getImageData(0, 0, w, h);
  const d = im.data;
  const a = clamp(rimAlpha, 0, 1);
  for (let y = 0; y < h; y++) {
    for (let px = w - 1; px >= 0; px--) {
      const i = (y * w + px) * 4;
      if (d[i + 3] < 128) continue;
      for (let k = 0; k < 3; k++) d[i + k] = Math.round(lerp(d[i + k], rimColor[k], a));
      break; // only the outermost pixel of the row
    }
  }
  x.putImageData(im, 0, 0);
  lightCache.set(id, c);
  return c;
}

// ---------------------------------------------------------------- the placeholder
// A code-drawn silhouette about 46 px tall with a scarf, so there is something to walk around
// with until the real character is drawn. Idle: breathes (upper body sinks a pixel). Walk: two
// stride poses with a passing pose between them. Jump: legs tucked.
const FW = 36;
const FH = 50; // feet on the last row; head top on row 4 -> 46 px tall
const AX = 18; // the centre line inside the frame

function buildMask(legs, sink, scarfLift) {
  const m = new Uint8Array(FW * FH);
  const box = (x0, y0, x1, y1, v = 1) => {
    for (let y = Math.max(0, y0); y <= Math.min(FH - 1, y1); y++) {
      for (let x = Math.max(0, x0); x <= Math.min(FW - 1, x1); x++) m[y * FW + x] = v;
    }
  };
  const s = sink; // the upper body's vertical offset
  // head (chamfered), with hair at the back
  box(14, 4 + s, 21, 4 + s); box(13, 5 + s, 22, 12 + s); box(14, 13 + s, 21, 13 + s);
  box(12, 6 + s, 12, 11 + s);
  // neck, coat (a little wider at the hem), arms hanging at the sides
  box(16, 14 + s, 19, 14 + s);
  box(13, 15 + s, 22, 15 + s); box(12, 16 + s, 23, 29 + s); box(12, 30 + s, 24, 32);
  box(11, 17 + s, 11, 28 + s); box(24, 17 + s, 24, 27 + s);
  // scarf: a band at the neck and a tail trailing behind (value 2 = the accent colour)
  box(14, 14 + s, 21, 16 + s, 2);
  box(10 - scarfLift, 16 + s - scarfLift, 13, 18 + s, 2);
  box(8 - scarfLift * 2, 18 + s - scarfLift * 2, 10, 20 + s - scarfLift, 2);

  const leg = (x, y0, y1, slope) => {
    for (let y = y0; y <= y1; y++) {
      const dx = Math.round(((y - y0) / Math.max(1, y1 - y0)) * slope);
      box(x + dx, y, x + dx + 2, y);
    }
    const fx = x + slope;
    box(fx, y1 - 1, fx + 4, y1); // a foot, toe forward
  };
  if (legs === 'stand') { leg(14, 33, 49, 0); leg(19, 33, 49, 0); }
  else if (legs === 'strideA') { leg(17, 33, 49, 5); leg(15, 33, 49, -5); }
  else if (legs === 'strideB') { leg(17, 33, 49, 3); leg(15, 33, 49, -3); }
  else if (legs === 'pass') { leg(16, 33, 49, 0); leg(17, 33, 45, 2); }
  else if (legs === 'tuck') { leg(13, 33, 43, 2); leg(19, 33, 41, 3); }
  return m;
}

const FRAMES = {
  idle: [buildMask('stand', 0, 0), buildMask('stand', 1, 0)],
  walk: [buildMask('strideA', 1, 1), buildMask('pass', 0, 1), buildMask('strideB', 1, 1), buildMask('pass', 0, 1)],
  jump: [buildMask('tuck', 0, 2)],
};
FRAMES.run = FRAMES.walk;
const FRAME_TIME = { idle: 0.7, walk: 0.12, run: 0.075, jump: 1 };

export class PlaceholderFigure {
  constructor() {
    this.cache = new Map();
    this.halfWidth = 8;
  }

  // The frame's colours follow the light: cold and dark before dawn, warmer after.
  _frame(anim, index, mixQ) {
    const key = `${anim}${index}@${mixQ}`;
    let c = this.cache.get(key);
    if (c) return [c, key];
    const mix = mixQ / 16;
    const body = mixColor('#151a33', '#2b2434', mix);
    const scarf = mixColor('#8a5a3c', '#d9a24e', mix);
    const mask = FRAMES[anim][index];
    const [cv, x] = mkCanvas(FW, FH);
    const im = x.createImageData(FW, FH);
    for (let i = 0; i < mask.length; i++) {
      if (!mask[i]) continue;
      const col = mask[i] === 2 ? scarf : body;
      im.data[i * 4] = col[0]; im.data[i * 4 + 1] = col[1]; im.data[i * 4 + 2] = col[2]; im.data[i * 4 + 3] = 255;
    }
    x.putImageData(im, 0, 0);
    this.cache.set(key, cv);
    return [cv, key];
  }

  draw(g, screenX, feetY, facing, state, t) {
    const list = FRAMES[state.anim] || FRAMES.idle;
    if (!(state.anim in FRAMES)) state = { ...state, anim: 'idle' };
    const index = Math.floor(t / (FRAME_TIME[state.anim] || 0.2)) % list.length;
    const mixQ = Math.round(clamp(state.mix, 0, 1) * 16);
    const [frame, key] = this._frame(state.anim in FRAMES ? state.anim : 'idle', index, mixQ);
    const rim = mixColor('#7f97cf', '#ffd98a', mixQ / 16);
    const lit = lightFrame(frame, `ph:${key}`, facing, rim, lerp(0.55, 0.9, mixQ / 16));
    drawContactShadow(g, screenX, state.ground, state.air, state.mix, this.halfWidth);
    const ax = facing < 0 ? FW - 1 - AX : AX;
    g.drawImage(lit, screenX - ax, feetY - FH);
  }
}
