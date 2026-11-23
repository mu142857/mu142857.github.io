// 晨, the girl from The Cloud, as the site's character.
//
// Assets/dawn/chen.png is Oscar's sheet copied unchanged from the game
// (art/characters/chen/chen_oscar.png): one row of 68x60 frames, facing right.
//   0-6 getting up · 7-10 idle · 11-14 a glance · 15-17 push-off · 18-23 run loop ·
//   24-25 braking · 26-30 picking something up
// Frame numbers, timings (100 ms a frame) and anchors are the game's own (scripts/chen.gd).
// The sheet has no jump: in the air she holds the run's two airborne frames.
//
// The sprite's own colours are daylight colours, so each frame is multiplied by the scene's
// ambient light (cold and dim before dawn, warm once the sun is up) before the shared rim
// light goes on.

import { mkCanvas, clamp, lerp, mixColor } from './engine.js';
import { drawContactShadow, lightFrame } from './player.js';

const FW = 68;
const FH = 60;
const AX = 28; // body centre line inside the frame
const FOOT_STAND = 56; // the row her soles are on
const FOOT_RUN = 57; // run frames plant the foot a pixel lower
const FRAME = 0.1; // seconds

const IDLE = [7, 8, 9, 10];
const GLANCE = [[11, 0.1], [12, 0.1], [13, 0.7], [14, 0.1]];
const IDLE_SPAN = 3.6; // seconds of plain idle before each glance
const START = [15, 16, 17];
const RUN = [18, 19, 20, 21, 22, 23];
const STOP = [24, 25];
const GETUP = [0, 1, 2, 3, 4, 5, 6];
const AIR_UP = 19;
const AIR_DOWN = 22;

const AMBIENT_DAWN = '#6c80c4'; // multiplied in (#ffffff = unchanged)
const AMBIENT_SUN = '#ffeccc';
const RIM_DAWN = '#9fb4e6';
const RIM_SUN = '#ffe2a0';

export const GETUP_TIME = GETUP.length * FRAME;

export async function loadChen(url = 'Assets/dawn/chen.png') {
  const img = new Image();
  img.src = url;
  await img.decode();
  return new ChenFigure(img);
}

export class ChenFigure {
  constructor(sheet) {
    this.sheet = sheet;
    this.tinted = new Map(); // mixQ -> the whole sheet under that light
    this.frames = new Map(); // `${mixQ}:${index}` -> a 68x60 canvas
    this.halfWidth = 9;
  }

  _sheet(mixQ) {
    let c = this.tinted.get(mixQ);
    if (c) return c;
    const amb = mixColor(AMBIENT_DAWN, AMBIENT_SUN, mixQ / 16);
    const [cv, x] = mkCanvas(this.sheet.width, this.sheet.height, { willReadFrequently: true });
    x.drawImage(this.sheet, 0, 0);
    const im = x.getImageData(0, 0, cv.width, cv.height);
    const d = im.data;
    for (let i = 0; i < d.length; i += 4) {
      if (!d[i + 3]) continue;
      d[i] = Math.round((d[i] * amb[0]) / 255);
      d[i + 1] = Math.round((d[i + 1] * amb[1]) / 255);
      d[i + 2] = Math.round((d[i + 2] * amb[2]) / 255);
    }
    x.putImageData(im, 0, 0);
    this.tinted.set(mixQ, cv);
    return cv;
  }

  _frame(index, mixQ) {
    const key = `${mixQ}:${index}`;
    let c = this.frames.get(key);
    if (!c) {
      const [cv, x] = mkCanvas(FW, FH);
      x.drawImage(this._sheet(mixQ), index * FW, 0, FW, FH, 0, 0, FW, FH);
      this.frames.set(key, cv);
      c = cv;
    }
    return [c, key];
  }

  // Which sheet frame, and which row its soles are on.
  _pick(state, t) {
    switch (state.anim) {
      case 'lie': return [0, FOOT_STAND];
      case 'getup': return [GETUP[Math.min(GETUP.length - 1, Math.floor(t / FRAME))], FOOT_STAND];
      case 'jump': return [(state.vy ?? 0) < 0 ? AIR_UP : AIR_DOWN, FOOT_RUN];
      case 'stop': return [STOP[Math.min(STOP.length - 1, Math.floor(t / FRAME))], FOOT_RUN];
      case 'walk':
      case 'run': {
        const moved = state.moveT ?? 1;
        if (moved < START.length * FRAME) return [START[Math.floor(moved / FRAME)], FOOT_STAND];
        return [RUN[Math.floor((state.stride ?? t) / FRAME) % RUN.length], FOOT_RUN];
      }
      default: {
        const u = t % (IDLE_SPAN + 1);
        if (u < IDLE_SPAN) return [IDLE[Math.floor(u / FRAME) % IDLE.length], FOOT_STAND];
        let left = u - IDLE_SPAN;
        for (const [f, dur] of GLANCE) {
          if (left < dur) return [f, FOOT_STAND];
          left -= dur;
        }
        return [IDLE[0], FOOT_STAND];
      }
    }
  }

  draw(g, screenX, feetY, facing, state, t) {
    const mixQ = Math.round(clamp(state.mix, 0, 1) * 16);
    const [index, foot] = this._pick(state, t);
    const [frame, key] = this._frame(index, mixQ);
    const rim = mixColor(RIM_DAWN, RIM_SUN, mixQ / 16);
    const lit = lightFrame(frame, `chen:${key}`, facing, rim, lerp(0.3, 0.5, mixQ / 16));
    const lying = state.anim === 'lie' || (state.anim === 'getup' && t < 0.3);
    drawContactShadow(g, screenX - (lying ? 6 * facing : 0), state.ground, state.air, state.mix, lying ? 18 : this.halfWidth);
    const ax = facing < 0 ? FW - 1 - AX : AX;
    g.drawImage(lit, screenX - ax, feetY - 1 - foot);
  }
}
