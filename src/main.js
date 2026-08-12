import {
  CANVAS_WIDTH, CANVAS_HEIGHT, GROUND_Y, BUILDING_BASE_Y, PLAYER_SPAWN_X,
  HIGHLIGHT_COLOR, HIGHLIGHT_BOX_COLOR, ARROW_COLOR, VIGNETTE_SIZE, VIGNETTE_ALPHA,
  SCENE_FADE_TIME,
} from './engine/config.js';
import { loadImage } from './engine/assets.js';
import { GameLoop } from './engine/loop.js';
import { InputManager } from './engine/input.js';
import { Player } from './entities/player.js';
import { World } from './world/world.js';
import { Camera } from './world/camera.js';
import { Overlay } from './ui/overlay.js';
import { loadPixelFont, drawText, wrapText, measureText } from './ui/pixelText.js';
import { Particles } from './engine/particles.js';
import { TouchControls } from './ui/touchControls.js';
import { Runner } from './runner/runner.js';
import { Music } from './engine/music.js';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const app = document.getElementById('app');
const rotateHint = document.getElementById('rotate-hint');

const KEY_CONTROLS = 'Walk A / D    Sprint Shift    Jump Space x2    Enter Up / Click';
const TOUCH_CONTROLS = 'Buttons to walk and jump    Tap jump twice in the air    Tap a building to enter';

// --- Responsive layout ------------------------------------------------------
// The stage is the drawable area. On a phone held upright it is the viewport turned on its
// side (CSS rotates #app a quarter turn — see body.rotated in style.css), so the site is
// always played in landscape, rotation lock or not.
let renderScale = 1;
let touchMode = false;
let rotated = false;
let controlsText = KEY_CONTROLS;

function layout() {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  // Coarse pointer = finger. The size check also covers a desktop window shrunk to phone size.
  touchMode = window.matchMedia('(pointer: coarse)').matches || Math.min(vw, vh) <= 520;
  rotated = touchMode && vh > vw;

  const stageW = rotated ? vh : vw;
  const stageH = rotated ? vw : vh;
  document.body.classList.toggle('rotated', rotated);
  document.body.classList.toggle('touch', touchMode);
  // A phone in landscape is wide but short: either axis being small means "shrink the UI".
  document.body.classList.toggle('compact', stageW < 760 || stageH < 500);
  document.body.classList.toggle('narrow', stageW < 560);
  app.style.width = `${stageW}px`;
  app.style.height = `${stageH}px`;
  controlsText = touchMode ? TOUCH_CONTROLS : KEY_CONTROLS;

  // Backing store stays an integer multiple of 160x90 so the world pass draws crisp pixels.
  const fit = Math.min(stageW / CANVAS_WIDTH, stageH / CANVAS_HEIGHT);
  renderScale = Math.max(1, touchMode ? Math.ceil(fit) : Math.floor(fit));
  canvas.width = CANVAS_WIDTH * renderScale;
  canvas.height = CANVAS_HEIGHT * renderScale;
  // Desktop keeps the exact integer-scaled size; on a phone the screen is small enough that
  // filling it beats a pixel-perfect multiple, so the CSS size takes the fractional fit
  // (drawn from a larger backing store, so nothing is upscaled).
  const cssScale = touchMode ? fit : renderScale;
  canvas.style.width = `${Math.round(CANVAS_WIDTH * cssScale)}px`;
  canvas.style.height = `${Math.round(CANVAS_HEIGHT * cssScale)}px`;
}
window.addEventListener('resize', layout);
window.addEventListener('orientationchange', layout);
layout();

// Client coords -> 0..1 across the canvas. getBoundingClientRect gives the on-screen box, so
// when #app is rotated a quarter turn the canvas's local axes are swapped: its local +x runs
// down the screen and its local +y runs right-to-left.
function canvasNorm(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  if (rotated) {
    return {
      nx: (clientY - rect.top) / rect.height,
      ny: (rect.right - clientX) / rect.width,
    };
  }
  return {
    nx: (clientX - rect.left) / rect.width,
    ny: (clientY - rect.top) / rect.height,
  };
}

const THEME_LABELS = { rustCity: 'City', silvaron: 'Forest' };
const THEME_ORDER = ['rustCity', 'silvaron'];
const SKIN_STORAGE_KEY = 'skin-theme';
const LANG_STORAGE_KEY = 'site-lang'; // 'en' | 'zh' — stored now, consumed once translations land
const MUSIC_TRACKS = {
  rustCity: 'Assets/music/glitch.mp3',
  silvaron: 'Assets/music/Silvaron.m4a',
};

// First visit (no saved skin): a full-screen picker with the three world covers. Resolves
// with the chosen theme key and records it, so the question is only ever asked once — until
// the save is cleared, which deliberately counts as a first visit again. The third cover is
// sealed: clicking it just flashes the red ACCESS DENIED line.
function pickTheme() {
  return new Promise((resolve) => {
    const picker = document.getElementById('theme-picker');
    const denied = document.getElementById('theme-denied');
    picker.classList.remove('hidden');
    picker.addEventListener('click', (e) => {
      const btn = e.target.closest('.theme-option');
      if (!btn) return;
      if (!btn.dataset.theme) {
        denied.classList.remove('flash');
        void denied.offsetWidth; // restart the animation on every click
        denied.classList.add('flash');
        return;
      }
      localStorage.setItem(SKIN_STORAGE_KEY, btn.dataset.theme);
      picker.classList.add('hidden');
      resolve(btn.dataset.theme);
    });
  });
}

// Text sizes, in world px (multiplied by renderScale to get the device font size).
const TITLE_H = 16;
const BODY_H = 10;
const LABEL_H = 12;

// World-anchored intro (device-space pass). Sized large and rendered with AA so glyphs
// are solid and readable rather than blown-up single pixels.
function drawIntro(ctx, cameraX, S) {
  const dx = (8 - cameraX) * S;
  let y = 3;
  drawText(ctx, 'Hi, I am', dx, y * S, { sizePx: TITLE_H * S, color: '#f4e9c1' });
  y += TITLE_H + 2;
  drawText(ctx, 'Jiamu Shangguan', dx, y * S, { sizePx: TITLE_H * S, color: '#f4e9c1' });
  y += TITLE_H + 3;
  wrapText(ctx, controlsText, 150 * S, BODY_H * S).forEach((line) => {
    drawText(ctx, line, dx, y * S, { sizePx: BODY_H * S, color: '#c8ccda' });
    y += BODY_H + 1.5;
  });
}

// Thin dark band at each screen edge (world-space pass), near-black at the very edge fading
// quickly to clear a few pixels in — an edge vignette, not a full-screen darkening.
function drawVignette(ctx) {
  const s = VIGNETTE_SIZE;
  const W = CANVAS_WIDTH;
  const H = CANVAS_HEIGHT;
  const edge = `rgba(0, 0, 0, ${VIGNETTE_ALPHA})`;
  const clear = 'rgba(0, 0, 0, 0)';
  const bands = [
    { g: [0, 0, 0, s], rect: [0, 0, W, s] }, // top
    { g: [0, H, 0, H - s], rect: [0, H - s, W, s] }, // bottom
    { g: [0, 0, s, 0], rect: [0, 0, s, H] }, // left
    { g: [W, 0, W - s, 0], rect: [W - s, 0, s, H] }, // right
  ];
  for (const { g, rect } of bands) {
    const grad = ctx.createLinearGradient(g[0], g[1], g[2], g[3]);
    grad.addColorStop(0, edge);
    grad.addColorStop(1, clear);
    ctx.fillStyle = grad;
    ctx.fillRect(rect[0], rect[1], rect[2], rect[3]);
  }
}

// World-y of the baseline the nearby building's name sits on: just above the highlight box,
// clamped so a building taller than the screen still gets a readable label. The prompt
// chevron hangs off the same number so the two always read as one stacked hint.
function labelBottomY(world) {
  const img = world.imageFor(world.nearbyBuilding);
  return Math.max(LABEL_H + 2, BUILDING_BASE_Y - img.height - 1);
}

// Section name above the nearby building (device-space pass).
function drawBuildingLabel(ctx, world, cameraX, S) {
  const b = world.nearbyBuilding;
  if (!b) return;
  const img = world.imageFor(b);
  const cx = (b.worldX + img.width / 2 - cameraX) * S;
  drawText(ctx, b.label, cx, labelBottomY(world) * S, {
    sizePx: LABEL_H * S, color: HIGHLIGHT_COLOR, align: 'center', baseline: 'bottom',
  });
}

// Subtle semi-transparent outline around the nearby building (scaled pass).
function drawHighlightBox(ctx, world, cameraX) {
  const b = world.nearbyBuilding;
  if (!b) return;
  const img = world.imageFor(b);
  const x = b.worldX - cameraX;
  const top = BUILDING_BASE_Y - img.height;
  const w = img.width;
  const h = img.height;
  ctx.fillStyle = HIGHLIGHT_BOX_COLOR;
  ctx.fillRect(x, top, w, 1);
  ctx.fillRect(x, BUILDING_BASE_Y - 1, w, 1);
  ctx.fillRect(x, top, 1, h);
  ctx.fillRect(x + w - 1, top, 1, h);
}

// Right-pointing chevron next to the player at the start, hinting to walk right toward the
// buildings. Only shows while the player is still near the spawn (scaled pass).
function drawStartArrow(ctx, player, cameraX, time) {
  if (player.x > PLAYER_SPAWN_X + 40) return;
  const bob = Math.sin(time * 6) * 2;
  const bx = player.x - cameraX + 10 + bob;
  const by = GROUND_Y - 11;
  ctx.fillStyle = ARROW_COLOR;
  ctx.fillRect(bx, by - 3, 2, 6);
  ctx.fillRect(bx + 2, by - 2, 2, 4);
  ctx.fillRect(bx + 4, by - 1, 2, 2);
}

// The gate into the runner minigame: a big bobbing chevron standing past the last building,
// pointing on down the road (scaled pass). Its label is drawn in the text pass.
function drawGateArrow(ctx, world, cameraX, time) {
  const bx = world.gateX - cameraX + Math.sin(time * 5) * 2;
  if (bx < -12 || bx > CANVAS_WIDTH) return;
  const by = GROUND_Y - 16;
  ctx.fillStyle = ARROW_COLOR;
  ctx.fillRect(bx, by - 6, 3, 12);
  ctx.fillRect(bx + 3, by - 4, 3, 8);
  ctx.fillRect(bx + 6, by - 2, 3, 4);
}

function drawGateLabel(ctx, world, cameraX, S) {
  const cx = world.gateX + 4 - cameraX;
  if (cx < -40 || cx > CANVAS_WIDTH + 40) return;
  // Kept fully on screen: the camera stops at the end of the world, so a label centred on the
  // gate would otherwise hang off the right edge.
  const half = measureText(ctx, 'ENTER GAME', LABEL_H * S) / 2;
  const margin = half + 3 * S;
  const x = Math.max(margin, Math.min(cx * S, CANVAS_WIDTH * S - margin));
  drawText(ctx, 'ENTER GAME', x, (GROUND_Y - 22) * S, {
    sizePx: LABEL_H * S, color: ARROW_COLOR, align: 'center', baseline: 'bottom',
  });
}

// Bouncing chevron over the player when near a building (scaled pass). It sits directly
// under the building's name rather than over the character's head, so the name and the
// "press to enter" hint read as one thing.
function drawPrompt(ctx, world, player, cameraX, time) {
  if (!world.nearbyBuilding) return;
  const screenX = player.x - cameraX;
  const bounce = Math.sin(time * 6) * 2;
  const baseY = labelBottomY(world) + 3 + bounce;
  ctx.fillStyle = ARROW_COLOR;
  ctx.fillRect(screenX - 3, baseY, 6, 2);
  ctx.fillRect(screenX - 2, baseY + 2, 4, 2);
  ctx.fillRect(screenX - 1, baseY + 4, 2, 2);
}

async function main() {
  const [playerSheet] = await Promise.all([
    loadImage('Assets/player/player-Sheet.png'),
    loadPixelFont(),
  ]);
  const world = new World();
  const savedTheme = localStorage.getItem(SKIN_STORAGE_KEY);
  const initialTheme = THEME_ORDER.includes(savedTheme) ? savedTheme : await pickTheme();
  await world.setTheme(initialTheme);
  const music = new Music(MUSIC_TRACKS, initialTheme);

  const input = new InputManager();
  const player = new Player(playerSheet, PLAYER_SPAWN_X);
  const camera = new Camera(world.worldWidth, CANVAS_WIDTH);
  const overlay = new Overlay();
  const dust = new Particles();
  const touch = new TouchControls(input);
  const runner = new Runner(player, input, dust);
  await runner.load(THEME_ORDER);
  runner.onVenueChange = (key) => music.setTheme(key); // crossfade with the blackout venue swap
  let dustTimer = 0;
  let promptTime = 0;
  let lastBlack = 0; // last --ui-fade written to the DOM (see render)

  // A flat fan of sparks kicked out from under the feet on the mid-air hop, so the second
  // jump reads as a push off something rather than a glitch. The character is 8px tall and
  // tucks its legs up in the jump pose — only the top 4px are drawn — so the sparks come off
  // 4px above the feet anchor, where the tucked-up feet actually are.
  const DOUBLE_JUMP_PUFF_Y = 5; // 4px for the tuck, +1 so the fan sits just under the sprite
  player.onDoubleJump = (x, y) => {
    for (let i = 0; i < 12; i++) {
      const angle = Math.PI * (i / 11); // 0..PI sweeps right to left, always downward
      const speed = 24 + Math.random() * 26;
      const life = 0.26 + Math.random() * 0.16;
      dust.emit({
        x, y: y - DOUBLE_JUMP_PUFF_Y,
        vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed * 0.5,
        g: 150, life, maxLife: life,
        size: Math.random() < 0.5 ? 2 : 1, color: ARROW_COLOR,
      });
    }
  };

  // --- Scenes ---------------------------------------------------------------
  // Two scenes share one player and one particle system: the city, and the runner minigame
  // reached by walking off the right end of the street. Swapping between them happens behind
  // a full-screen fade, at the moment the screen is fully black.
  const GATE_RADIUS = 26; // how close to the gate you must stand for it to accept "enter"
  let scene = 'city';
  let cityX = PLAYER_SPAWN_X; // where to set the character back down on return
  let transition = null; // { t, phase: 'out' | 'in', swap }

  const atGate = () => player.x >= world.gateX - GATE_RADIUS;

  function startTransition(swap) {
    if (transition) return;
    transition = { t: 0, phase: 'out', swap };
  }

  // Returns true while the world should stay frozen (the fade-to-black half).
  function advanceTransition(dt) {
    if (!transition) return false;
    transition.t += dt;
    if (transition.t < SCENE_FADE_TIME) return transition.phase === 'out';
    if (transition.phase === 'out') {
      transition.swap();
      transition = { t: 0, phase: 'in', swap: null }; // the new scene runs as it fades in
      return false;
    }
    transition = null;
    return false;
  }

  function fadeAlpha() {
    if (!transition) return 0;
    const t = Math.min(1, transition.t / SCENE_FADE_TIME);
    return transition.phase === 'out' ? t : 1 - t;
  }

  // The two skin/site switches are city furniture: mid-run they are a stray click away from
  // reskinning the world under you or leaving the page entirely, and they crowd the score.
  // Both scene swaps happen at full black, so they appear and disappear unseen.
  function enterRunner() {
    scene = 'runner';
    cityX = player.x;
    document.body.classList.add('in-runner');
    touch.setMode('runner');
    runner.enter(world.theme);
  }

  function exitRunner() {
    scene = 'city';
    runner.leave();
    music.setTheme(world.theme); // the runner's venue may have cycled away from the city's skin
    document.body.classList.remove('in-runner');
    touch.setMode('city');
    dust.list.length = 0;
    player.reset(cityX);
    camera.update(player.x);
    world.update(player.x);
  }

  // Show the gamepad only on touch devices, and re-check whenever the stage changes (a phone
  // being turned, or a desktop window resized down). These run after the module-level layout()
  // listener, so touchMode / rotated are already up to date.
  let hintDismissed = false;
  function dismissHint() {
    if (hintDismissed) return;
    hintDismissed = true;
    rotateHint.classList.add('fading');
    setTimeout(() => rotateHint.classList.add('hidden'), 700);
  }
  function syncTouchUI() {
    touch.setVisible(touchMode);
    const showHint = rotated && !hintDismissed;
    rotateHint.classList.toggle('hidden', !showHint);
    if (showHint) setTimeout(dismissHint, 5000); // it has made its point by then
  }
  window.addEventListener('resize', syncTouchUI);
  window.addEventListener('orientationchange', syncTouchUI);
  syncTouchUI();

  // Settings opens through the same overlay as the sections. The template is cloned fresh
  // on every open, so the buttons are re-queried and re-wired each time — no stale handlers.
  const settingsToggle = document.getElementById('settings-toggle');
  settingsToggle.addEventListener('click', () => {
    overlay.show('settings');

    const musicBtn = document.getElementById('setting-music');
    const syncMusic = () => {
      musicBtn.textContent = music.enabled ? 'On' : 'Off';
      musicBtn.classList.toggle('off', !music.enabled);
    };
    syncMusic();
    musicBtn.addEventListener('click', () => {
      music.setEnabled(!music.enabled);
      syncMusic();
    });

    // The language switch only stores the preference for now; translations come later.
    const langBtn = document.getElementById('setting-lang');
    const syncLang = () => {
      langBtn.textContent = localStorage.getItem(LANG_STORAGE_KEY) === 'zh' ? '中文' : 'English';
    };
    syncLang();
    langBtn.addEventListener('click', () => {
      const next = localStorage.getItem(LANG_STORAGE_KEY) === 'zh' ? 'en' : 'zh';
      localStorage.setItem(LANG_STORAGE_KEY, next);
      syncLang();
    });

    // Two clicks to clear: the first arms the button, the second wipes and reloads. With no
    // saved skin left, the reload lands on the first-visit world picker.
    const clearBtn = document.getElementById('setting-clear');
    clearBtn.addEventListener('click', () => {
      if (!clearBtn.classList.contains('confirm')) {
        clearBtn.classList.add('confirm');
        clearBtn.textContent = 'Confirm?';
        return;
      }
      localStorage.clear();
      location.reload();
    });
  });

  const skinToggle = document.getElementById('skin-toggle');
  function updateSkinToggleLabel() {
    const nextTheme = THEME_ORDER[(THEME_ORDER.indexOf(world.theme) + 1) % THEME_ORDER.length];
    skinToggle.textContent = `${THEME_LABELS[nextTheme]} Style ›`;
  }
  updateSkinToggleLabel();
  skinToggle.addEventListener('click', async () => {
    const nextTheme = THEME_ORDER[(THEME_ORDER.indexOf(world.theme) + 1) % THEME_ORDER.length];
    music.setTheme(nextTheme);
    await world.setTheme(nextTheme);
    localStorage.setItem(SKIN_STORAGE_KEY, nextTheme);
    camera.worldWidth = world.worldWidth;
    // The new skin's buildings are different widths, so the street ends somewhere else. In
    // the runner the character's x is a fixed screen position, not a place in the city —
    // clamp the spot we'll put it back down on instead of the live one.
    if (scene === 'city') {
      player.x = Math.max(PLAYER_SPAWN_X, Math.min(player.x, world.worldWidth));
      camera.update(player.x);
      world.update(player.x);
    } else {
      cityX = Math.max(PLAYER_SPAWN_X, Math.min(cityX, world.worldWidth));
    }
    updateSkinToggleLabel();
  });

  // Click/tap a nearby building (inside its box) to enter it, as an alternative to Enter.
  // The gate arrow at the end of the street is clickable the same way.
  canvas.addEventListener('click', (e) => {
    if (overlay.isOpen || scene !== 'city' || transition) return;
    const { nx, ny } = canvasNorm(e.clientX, e.clientY);
    const wx = nx * CANVAS_WIDTH + camera.x;
    const wy = ny * CANVAS_HEIGHT;

    if (atGate() && wx >= world.gateX - 8 && wx <= world.gateX + 17 && wy >= GROUND_Y - 30 && wy <= GROUND_Y) {
      startTransition(enterRunner);
      return;
    }

    const b = world.nearbyBuilding;
    if (!b) return;
    const img = world.imageFor(b);
    const top = BUILDING_BASE_Y - img.height;
    if (wx >= b.worldX && wx <= b.worldX + img.width && wy >= top && wy <= BUILDING_BASE_Y) {
      overlay.show(b.sectionId);
    }
  });

  function update(dt) {
    if (advanceTransition(dt)) {
      input.endFrame(); // the world is frozen behind the black, but presses must not pile up
      return;
    }

    if (overlay.isOpen) {
      if (input.wasPressed('interact')) overlay.hide();
      input.endFrame();
      return;
    }

    if (scene === 'runner') {
      if (runner.update(dt) === 'exit') startTransition(exitRunner);
      touch.setEnter(touchMode, 'BACK');
      dust.update(dt);
      input.endFrame();
      return;
    }

    player.update(dt, input);
    player.x = Math.max(PLAYER_SPAWN_X, Math.min(player.x, world.worldWidth));
    camera.update(player.x);
    world.update(player.x);
    promptTime += dt;
    // The ENTER button only exists while there's something to enter.
    touch.setEnter(touchMode && (!!world.nearbyBuilding || atGate()), 'ENTER');

    // Kick up pixel dust behind the character while sprinting on the ground.
    if (player.sprinting && player.state === 'WALK') {
      dustTimer += dt;
      while (dustTimer >= 0.03) {
        dustTimer -= 0.03;
        const back = -player.facing;
        const life = 0.34 + Math.random() * 0.18;
        dust.emit({
          x: player.x + back * 3 + (Math.random() * 2 - 1),
          y: GROUND_Y - 1 - Math.random() * 3,
          vx: back * (16 + Math.random() * 20),
          vy: -(10 + Math.random() * 16),
          g: 70,
          life,
          maxLife: life,
          size: Math.random() < 0.6 ? 2 : 1,
          color: '#e8dcb0',
        });
      }
    } else {
      dustTimer = 0;
    }
    dust.update(dt);

    if (input.wasPressed('interact')) {
      if (world.nearbyBuilding) overlay.show(world.nearbyBuilding.sectionId);
      else if (atGate()) startTransition(enterRunner);
    }

    input.endFrame();
  }

  function render() {
    const S = renderScale;

    // World pass — scaled, crisp pixel art.
    ctx.setTransform(S, 0, 0, S, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    if (scene === 'runner') {
      runner.draw(ctx); // draws its own backdrop, stones, dust and player
    } else {
      world.draw(ctx, camera.x, CANVAS_WIDTH, CANVAS_HEIGHT);
      if (!overlay.isOpen) drawHighlightBox(ctx, world, camera.x);
      dust.draw(ctx, camera.x); // behind the player
      player.draw(ctx, camera.x);
      if (!overlay.isOpen) {
        drawPrompt(ctx, world, player, camera.x, promptTime);
        drawStartArrow(ctx, player, camera.x, promptTime);
        drawGateArrow(ctx, world, camera.x, promptTime);
      }
    }
    drawVignette(ctx); // edge band, on top of the scene but under the UI text

    // Text pass — device space, anti-aliased so glyphs stay solid and readable.
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = true;
    if (scene === 'runner') {
      runner.drawHud(ctx, S, touchMode);
    } else {
      drawIntro(ctx, camera.x, S);
      if (!overlay.isOpen) {
        drawBuildingLabel(ctx, world, camera.x, S);
        drawGateLabel(ctx, world, camera.x, S);
      }
    }

    // Both blackouts land here, last of all, so they cover the HUD text too: the scene fade
    // and the runner's venue swap.
    const black = Math.max(fadeAlpha(), scene === 'runner' ? runner.blackout : 0);
    if (black > 0) {
      ctx.fillStyle = `rgba(0, 0, 0, ${black})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    // The DOM UI floats above the canvas, so it has to be faded separately or it stays lit
    // over a black screen. Only written when it actually moves, to avoid a style recalc a frame.
    if (Math.abs(black - lastBlack) > 0.005 || (black === 0 && lastBlack !== 0)) {
      app.style.setProperty('--ui-fade', String(1 - black));
      lastBlack = black;
    }
  }

  new GameLoop(update, render).start();
}

main();
