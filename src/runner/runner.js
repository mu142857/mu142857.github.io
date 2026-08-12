// The runner minigame: walk off the right end of the street and you drop into an endless
// dodge-the-cursed-stones run. The character stays pinned at RUNNER_PLAYER_X and the world
// scrolls past under it, so the same parallax layers the city uses drive the whole scene.
import {
  CANVAS_WIDTH, CANVAS_HEIGHT, GROUND_Y, BUILDING_BASE_Y, MODULATE_COLOR, ARROW_COLOR,
  ANIM_FRAME_DURATION, GRAVITY, JUMP_VELOCITY, DOUBLE_JUMP_VELOCITY,
  PLAYER_BODY_H, PLAYER_TUCKED_BOTTOM,
  RUNNER_GRAVITY, RUNNER_JUMP_VELOCITY, RUNNER_DOUBLE_JUMP_VELOCITY, RUNNER_PLAYER_X,
  RUNNER_START_SPEED, RUNNER_MAX_SPEED, RUNNER_ACCELERATION, RUNNER_VENUE_SECONDS,
  RUNNER_FADE_TIME,
} from '../engine/config.js';
import { loadImage } from '../engine/assets.js';
import { ParallaxLayer } from '../world/parallax.js';
import { THEMES } from '../world/themes.js';
import { drawText } from '../ui/pixelText.js';
import { t } from '../i18n.js';
import { STONE_TYPES, stoneSource, measureStoneSpans } from './stones.js';

const BEST_KEY = 'runner-best';

// Spacing. A stone is only ever placed far enough ahead that the player can finish the jump
// it demands AND still have REACTION_TIME of warning before it arrives — so the run is always
// solvable, however fast it has got. HEADROOM covers the speed-up during the approach.
const REACTION_TIME = 0.5;
const GAP_HEADROOM = 1.15;
const MIN_GAP = 84;

const OPENING_GRACE = 1.4; // clear road at the start of a run
const VENUE_GRACE = 1.0; // clear road after the lights come back on
const DEATH_INPUT_LOCK = 0.4; // ignore input right after a crash so mashing doesn't skip it
const LARGE_AFTER = 480; // px of distance before the big stone can show up at all
const LARGE_CHANCE_START = 0.1;
const LARGE_CHANCE_MAX = 0.32;
const LARGE_CHANCE_RAMP = 6000; // px of distance over which the monolith reaches its max share

export class Runner {
  constructor(player, input, particles) {
    this.player = player;
    this.particles = particles;
    this._input = input;
    this.venues = [];
    this.venueIndex = 0;
    this.stones = [];
    this.phase = 'run'; // 'run' | 'dead'
    this.venuePhase = 'none'; // 'none' | 'clearing' | 'out' | 'in'
    this.blackout = 0; // 0..1, drawn by the caller so it covers the HUD text too
    this.scrollX = 0;
    this.distance = 0;
    this.speed = RUNNER_START_SPEED;
    this.best = Number(localStorage.getItem(BEST_KEY)) || 0;
    this.stoneSheet = null;
    this._dustTimer = 0;
    this._stoneAnimTime = 0;
    this.onVenueChange = null; // called with the new venue's theme key at full black

    // The player's state machine is written for the city, where holding "right" walks. Here
    // the character runs on the spot, so it gets a permanently-held "right" (with lockX on)
    // and only the jump is wired through to the real input.
    this._runInput = {
      isDown: (action) => action === 'right',
      wasPressed: (action) => action === 'jump' && input.wasPressed('jump'),
      anyKeyPressed: () => false,
    };
  }

  async load(themeKeys) {
    this.stoneSheet = await loadImage('Assets/cursed_stone-Sheet.png');
    measureStoneSpans(this.stoneSheet); // shaped hitboxes, read straight off the art
    // Both venues are loaded up front: the blackout swap has to be instant, with no chance of
    // a half-loaded backdrop appearing when the lights come back.
    this.venues = await Promise.all(themeKeys.map(async (key) => {
      const theme = THEMES[key];
      const [layerImages, groundImage] = await Promise.all([
        Promise.all(theme.layers.map((l) => loadImage(l.src))),
        loadImage(theme.ground.src),
      ]);
      return {
        key,
        layers: theme.layers.map((l, i) => new ParallaxLayer(layerImages[i], l.factor, { align: l.align })),
        ground: new ParallaxLayer(groundImage, theme.ground.factor, { align: theme.ground.align }),
      };
    }));
  }

  get score() {
    return Math.floor(this.distance / 10);
  }

  // --- Scene entry / exit ---------------------------------------------------

  enter(themeKey) {
    const index = this.venues.findIndex((v) => v.key === themeKey);
    this.venueIndex = index >= 0 ? index : 0; // you run out of the city you were just in
    this.player.lockX = true;
    this.player.animSpeed = 1.35;
    this.player.gravity = RUNNER_GRAVITY;
    this.player.jumpVelocity = RUNNER_JUMP_VELOCITY;
    this.player.doubleJumpVelocity = RUNNER_DOUBLE_JUMP_VELOCITY;
    this.reset();
  }

  leave() {
    this.player.lockX = false;
    this.player.animSpeed = 1;
    this.player.gravity = GRAVITY;
    this.player.jumpVelocity = JUMP_VELOCITY;
    this.player.doubleJumpVelocity = DOUBLE_JUMP_VELOCITY;
  }

  // Restart the run without leaving the scene (and without changing venue).
  reset() {
    this.stones = [];
    this.phase = 'run';
    this.venuePhase = 'none';
    this.blackout = 0;
    this.scrollX = 0;
    this.distance = 0;
    this.speed = RUNNER_START_SPEED;
    this.venueTimer = 0;
    this.spawnHold = OPENING_GRACE;
    this.deadTimer = 0;
    this.nextSpawnX = CANVAS_WIDTH;
    this._dustTimer = 0;
    this.particles.list.length = 0;
    this.player.reset(RUNNER_PLAYER_X);
  }

  // --- Update ---------------------------------------------------------------

  // Returns 'exit' when the player asked to go back to the city.
  update(dt) {
    if (this._input.wasPressed('interact') && (this.phase === 'run' || this.deadTimer > DEATH_INPUT_LOCK)) {
      return 'exit';
    }

    if (this.phase === 'dead') {
      this.deadTimer += dt;
      if (this.deadTimer > DEATH_INPUT_LOCK && this._input.wasPressed('jump')) this.reset();
      return null;
    }

    this.speed = Math.min(RUNNER_MAX_SPEED, this.speed + RUNNER_ACCELERATION * dt);
    this.scrollX += this.speed * dt;
    this.distance += this.speed * dt;
    this._stoneAnimTime += dt;

    this.player.update(dt, this._runInput);
    this._updateVenue(dt);
    this._updateStones();
    this._emitRunDust(dt);

    if (this._hitStone()) this._die();
    return null;
  }

  _die() {
    this.phase = 'dead';
    this.deadTimer = 0;
    if (this.score > this.best) {
      this.best = this.score;
      localStorage.setItem(BEST_KEY, String(this.best));
    }
    // A puff of grit at the point of impact.
    for (let i = 0; i < 16; i++) {
      const life = 0.4 + Math.random() * 0.3;
      this.particles.emit({
        x: this.player.x + 2, y: this.player.y - 3 - Math.random() * 4,
        vx: 30 + Math.random() * 55, vy: -(20 + Math.random() * 45),
        g: 260, life, maxLife: life,
        size: Math.random() < 0.5 ? 2 : 1, color: '#c8b98a',
      });
    }
  }

  // Blackout venue swap: the harder version of the dino game's night mode — the whole screen
  // goes black and a completely different place fades in. Nothing spawns from the moment the
  // swap is queued until well after the lights are back, and the swap waits for the stones
  // already on screen to scroll away, so the blackout can never hide an obstacle.
  _updateVenue(dt) {
    if (this.spawnHold > 0) this.spawnHold -= dt;

    switch (this.venuePhase) {
      case 'none':
        this.venueTimer += dt;
        if (this.venueTimer >= RUNNER_VENUE_SECONDS) this.venuePhase = 'clearing';
        break;
      case 'clearing':
        if (this.stones.length === 0) this.venuePhase = 'out';
        break;
      case 'out':
        this.blackout = Math.min(1, this.blackout + dt / RUNNER_FADE_TIME);
        if (this.blackout >= 1) {
          this.venueIndex = (this.venueIndex + 1) % this.venues.length;
          this.venuePhase = 'in';
          if (this.onVenueChange) this.onVenueChange(this.venues[this.venueIndex].key);
        }
        break;
      case 'in':
        this.blackout = Math.max(0, this.blackout - dt / RUNNER_FADE_TIME);
        if (this.blackout <= 0) {
          this.venuePhase = 'none';
          this.venueTimer = 0;
          this.spawnHold = VENUE_GRACE;
          this.nextSpawnX = this.scrollX + CANVAS_WIDTH;
        }
        break;
    }
  }

  _updateStones() {
    const leftEdge = this.scrollX - 4;
    this.stones = this.stones.filter((s) => s.x + s.type.w > leftEdge);
    if (this.venuePhase !== 'none' || this.spawnHold > 0) return;
    if (this.scrollX + CANVAS_WIDTH < this.nextSpawnX) return;

    const type = this._pickType();
    const x = Math.max(this.nextSpawnX, this.scrollX + CANVAS_WIDTH + 1);
    this.stones.push({ type, x, phase: Math.floor(Math.random() * type.frames.length) });

    const gap = this.speed * (type.clearTime + REACTION_TIME + Math.random() * 0.5) * GAP_HEADROOM;
    this.nextSpawnX = x + type.w + Math.max(gap, MIN_GAP);
  }

  _pickType() {
    // No monolith until the run has settled and the player has met a small one first.
    if (this.distance < LARGE_AFTER) return STONE_TYPES.small;
    const ramp = (this.distance - LARGE_AFTER) / LARGE_CHANCE_RAMP;
    const chance = Math.min(LARGE_CHANCE_MAX, LARGE_CHANCE_START + ramp * LARGE_CHANCE_MAX);
    return Math.random() < chance ? STONE_TYPES.large : STONE_TYPES.small;
  }

  // Boxes are pulled in by 1px all round — the classic runner fudge, so a near miss reads as
  // a miss — and both sides are shaped rather than rectangular: the stone is tested row by
  // row against its real silhouette (see measureStoneSpans), and the character's box stops at
  // its tucked-up feet while it is airborne instead of at the anchor its legs have left.
  _hitStone() {
    const left = this.player.x - 2;
    const right = this.player.x + 2;
    const tuck = this.player.state === 'JUMP' ? PLAYER_TUCKED_BOTTOM : 0;
    const bottom = this.player.y - tuck;
    const top = this.player.y - PLAYER_BODY_H;

    for (const s of this.stones) {
      const { type } = s;
      const sx = s.x - this.scrollX;
      if (right <= sx + 1 || left >= sx + type.w - 1) continue; // nowhere near it

      const stoneTop = BUILDING_BASE_Y - type.h;
      if (!type.spans) { // pixels unreadable — fall back to the crop rect
        if (bottom > stoneTop + 1) return true;
        continue;
      }
      const first = Math.max(0, Math.floor(top - stoneTop));
      const last = Math.min(type.h - 1, Math.floor(bottom - stoneTop));
      for (let r = first; r <= last; r++) {
        const span = type.spans[r];
        if (span && right > sx + span.min + 1 && left < sx + span.max) return true;
      }
    }
    return false;
  }

  _emitRunDust(dt) {
    if (this.player.state !== 'WALK') {
      this._dustTimer = 0;
      return;
    }
    this._dustTimer += dt;
    while (this._dustTimer >= 0.055) {
      this._dustTimer -= 0.055;
      const life = 0.3 + Math.random() * 0.18;
      this.particles.emit({
        x: this.player.x - 3 + (Math.random() * 2 - 1),
        y: GROUND_Y - 1 - Math.random() * 2,
        vx: -(20 + Math.random() * 24), vy: -(8 + Math.random() * 14),
        g: 90, life, maxLife: life,
        size: Math.random() < 0.6 ? 2 : 1, color: '#e8dcb0',
      });
    }
  }

  // --- Draw -----------------------------------------------------------------

  draw(ctx) {
    const venue = this.venues[this.venueIndex];
    for (const layer of venue.layers) layer.draw(ctx, this.scrollX, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Same CanvasModulate dimming the city uses, so the two scenes read as one world.
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = MODULATE_COLOR;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    ctx.globalCompositeOperation = 'source-over';

    venue.ground.draw(ctx, this.scrollX, CANVAS_WIDTH, CANVAS_HEIGHT);
    this._drawStones(ctx);
    this.particles.draw(ctx, 0);
    this.player.draw(ctx, 0); // the player's x is already a screen x here
  }

  _drawStones(ctx) {
    // One shared 10fps clock; each stone starts on its own frame so they don't pulse in unison.
    const tick = Math.floor(this._stoneAnimTime / ANIM_FRAME_DURATION);
    for (const s of this.stones) {
      const { type } = s;
      const frame = type.frames[(tick + s.phase) % type.frames.length];
      const { sx, sy } = stoneSource(type, frame);
      ctx.drawImage(
        this.stoneSheet, sx, sy, type.w, type.h,
        Math.round(s.x - this.scrollX), BUILDING_BASE_Y - type.h, type.w, type.h,
      );
    }
  }

  // Device-space pass (crisp text), drawn by the caller after the world.
  drawHud(ctx, S, touchMode) {
    const pad = (n) => String(n).padStart(5, '0');
    drawText(ctx, `${t('run.hi')} ${pad(this.best)}   ${pad(this.score)}`, 5 * S, 5 * S, {
      sizePx: 10 * S, color: '#c8ccda',
    });

    if (this.phase !== 'dead') return;
    const cx = (CANVAS_WIDTH / 2) * S;
    drawText(ctx, t('run.gameOver'), cx, 24 * S, { sizePx: 16 * S, color: ARROW_COLOR, align: 'center' });
    drawText(ctx, `${t('run.score')} ${pad(this.score)}    ${t('run.best')} ${pad(this.best)}`, cx, 44 * S, {
      sizePx: 10 * S, color: '#f4e9c1', align: 'center',
    });
    const hint = t(touchMode ? 'run.retryTouch' : 'run.retryKey');
    drawText(ctx, hint, cx, 58 * S, { sizePx: 9 * S, color: '#9aa0b8', align: 'center' });
  }
}
