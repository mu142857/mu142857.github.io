import {
  ANIM_FRAME_DURATION,
  WALK_SPEED,
  IDLE_TO_LONG_DELAY,
  GRAVITY,
  JUMP_VELOCITY,
  DOUBLE_JUMP_VELOCITY,
  GROUND_Y,
  FRAME_W,
  PLAYER_ANCHOR_X,
  PLAYER_ANCHOR_Y,
  SPRINT_MULTIPLIER,
} from '../engine/config.js';
import { drawFrame } from '../engine/spritesheet.js';
import { ANIM } from './playerAnimations.js';

export class Player {
  constructor(sheet, x = 0) {
    this.sheet = sheet;
    this.x = x;
    this.y = GROUND_Y;
    this.vy = 0;
    this.facing = 1; // 1 = right, -1 = left
    this.state = 'IDLE_STAND';
    this.animIndex = 0;
    this.animTimer = 0;
    this.animDone = false; // true once a non-looping clip has played its last frame
    this.idleTimer = 0; // seconds spent in IDLE_STAND with no input
    this.sprinting = false; // moving with Shift held
    this.jumpsUsed = 0; // 1 after the ground jump, 2 after the mid-air one

    // Per-scene knobs. The city uses the defaults; the runner minigame swaps in a much
    // stronger jump, runs the walk cycle faster, and pins x (the ground scrolls instead).
    this.gravity = GRAVITY;
    this.jumpVelocity = JUMP_VELOCITY;
    this.doubleJumpVelocity = DOUBLE_JUMP_VELOCITY;
    this.animSpeed = 1;
    this.lockX = false;
    this.onDoubleJump = null; // called with (x, y) so the caller can puff out particles
  }

  // Drop the character back on the ground in a known state (used when a scene starts).
  reset(x) {
    this.x = x;
    this.y = GROUND_Y;
    this.vy = 0;
    this.facing = 1;
    this.jumpsUsed = 0;
    this.idleTimer = 0;
    this.sprinting = false;
    this.state = 'IDLE_STAND';
    this.animIndex = 0;
    this.animTimer = 0;
    this.animDone = false;
  }

  update(dt, input) {
    const left = input.isDown('left');
    const right = input.isDown('right');
    const moving = left !== right; // both held or neither held = standing still
    const dir = left ? -1 : 1;
    const jumpPressed = input.wasPressed('jump');
    this.sprinting = moving && input.isDown('sprint');

    switch (this.state) {
      case 'IDLE_STAND':
        this._updateIdleStand(dt, moving, dir, jumpPressed);
        break;
      case 'IDLE_LONG':
        this._updateIdleLong(dt, moving, dir, jumpPressed);
        break;
      case 'CURLED':
        this._updateCurled(input);
        break;
      case 'WAKING':
        // input is ignored mid-wake — the character finishes waking up before acting on anything else
        break;
      case 'WALK':
        this._updateWalk(dt, moving, dir, jumpPressed);
        break;
      case 'JUMP':
        this._updateJump(dt, moving, dir, jumpPressed);
        break;
    }

    this._advanceAnim(dt);

    // Non-looping clips need an explicit transition once they've finished playing.
    if (this.state === 'IDLE_LONG' && this.animDone) {
      this._setState('CURLED');
    } else if (this.state === 'WAKING' && this.animDone) {
      this._setState(moving ? 'WALK' : 'IDLE_STAND');
    }
  }

  _updateIdleStand(dt, moving, dir, jumpPressed) {
    if (moving) {
      this._moveHorizontal(dir, dt);
      this._setState('WALK');
      return;
    }
    if (jumpPressed) {
      this._setState('JUMP');
      return;
    }
    this.idleTimer += dt;
    if (this.idleTimer >= IDLE_TO_LONG_DELAY) {
      this._setState('IDLE_LONG');
    }
  }

  _updateIdleLong(dt, moving, dir, jumpPressed) {
    if (moving) {
      this._moveHorizontal(dir, dt);
      this._setState('WALK');
      return;
    }
    if (jumpPressed) {
      this._setState('JUMP');
    }
    // otherwise let the long-idle animation keep playing toward CURLED
  }

  _updateCurled(input) {
    if (input.anyKeyPressed()) {
      this._setState('WAKING');
    }
  }

  _updateWalk(dt, moving, dir, jumpPressed) {
    if (jumpPressed) {
      this._setState('JUMP');
      return;
    }
    if (!moving) {
      this._setState('IDLE_STAND');
      return;
    }
    this._moveHorizontal(dir, dt);
  }

  _updateJump(dt, moving, dir, jumpPressed) {
    if (moving) this._moveHorizontal(dir, dt); // air control

    // Double jump: one extra hop per airborne stretch. It *replaces* the current velocity
    // rather than adding to it, so the height gained is the same no matter how fast you were
    // already falling — press it near the top of the first hop for the full reach.
    if (jumpPressed && this.jumpsUsed < 2) {
      this.jumpsUsed = 2;
      this.vy = this.doubleJumpVelocity;
      if (this.onDoubleJump) this.onDoubleJump(this.x, this.y);
    }

    this.vy += this.gravity * dt;
    this.y += this.vy * dt;

    if (this.y >= GROUND_Y) {
      this.y = GROUND_Y;
      this.vy = 0;
      this.jumpsUsed = 0;
      this._setState(moving ? 'WALK' : 'IDLE_STAND');
    }
  }

  _moveHorizontal(dir, dt) {
    this.facing = dir;
    if (this.lockX) return; // runner minigame: the world moves, the character doesn't
    const speed = WALK_SPEED * (this.sprinting ? SPRINT_MULTIPLIER : 1);
    this.x += dir * speed * dt;
  }

  _setState(state) {
    if (this.state === state) return;
    this.state = state;
    this.animIndex = 0;
    this.animTimer = 0;
    this.animDone = false;
    if (state === 'IDLE_STAND') this.idleTimer = 0;
    if (state === 'JUMP') {
      this.vy = this.jumpVelocity;
      this.jumpsUsed = 1;
    }
  }

  _advanceAnim(dt) {
    const clip = ANIM[this.state];
    const frameTime = ANIM_FRAME_DURATION / this.animSpeed;
    this.animTimer += dt;
    while (this.animTimer >= frameTime) {
      this.animTimer -= frameTime;
      if (this.animIndex < clip.frames.length - 1) {
        this.animIndex++;
      } else if (clip.loop) {
        this.animIndex = 0;
      } else {
        this.animDone = true;
      }
    }
  }

  get currentFrame() {
    return ANIM[this.state].frames[this.animIndex];
  }

  draw(ctx, cameraX = 0) {
    const flip = this.facing < 0;
    // When flipped, the anchor mirrors to the other side of the frame (94 from the new
    // left edge), so the character's center stays anchored and doesn't jump on turn.
    const anchorX = flip ? FRAME_W - PLAYER_ANCHOR_X : PLAYER_ANCHOR_X;
    // No rounding: the high-res canvas (ctx scaled by RENDER_SCALE) lets the sprite sit at
    // sub-pixel positions for smooth movement, while nearest-neighbor keeps the art crisp.
    const dx = this.x - cameraX - anchorX;
    const dy = this.y - PLAYER_ANCHOR_Y;
    drawFrame(ctx, this.sheet, this.currentFrame, dx, dy, { flip });
  }
}
