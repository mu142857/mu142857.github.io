import {
  CANVAS_WIDTH, CANVAS_HEIGHT, GROUND_Y, BUILDING_BASE_Y, PLAYER_SPAWN_X,
  HIGHLIGHT_COLOR, HIGHLIGHT_BOX_COLOR, ARROW_COLOR, VIGNETTE_SIZE, VIGNETTE_ALPHA,
} from './engine/config.js';
import { loadImage } from './engine/assets.js';
import { GameLoop } from './engine/loop.js';
import { InputManager } from './engine/input.js';
import { Player } from './entities/player.js';
import { World } from './world/world.js';
import { Camera } from './world/camera.js';
import { Overlay } from './ui/overlay.js';
import { loadPixelFont, drawText, wrapText } from './ui/pixelText.js';
import { Particles } from './engine/particles.js';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

// Render at an integer multiple of the 160x90 logical resolution (canvas_item-style): the
// world is drawn with the context scaled by RENDER_SCALE (smoothing off) for crisp, smooth
// pixel art. Text is drawn in a separate device-space pass (see the render function).
let renderScale = 1;
function resizeCanvas() {
  renderScale = Math.max(1, Math.floor(Math.min(
    window.innerWidth / CANVAS_WIDTH,
    window.innerHeight / CANVAS_HEIGHT,
  )));
  canvas.width = CANVAS_WIDTH * renderScale;
  canvas.height = CANVAS_HEIGHT * renderScale;
  canvas.style.width = `${canvas.width}px`;
  canvas.style.height = `${canvas.height}px`;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

const CONTROLS = 'Walk A / D    Shift Sprint    Jump Space    Enter Up / Click';

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
  wrapText(ctx, CONTROLS, 150 * S, BODY_H * S).forEach((line) => {
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

// Section name above the nearby building (device-space pass).
function drawBuildingLabel(ctx, world, cameraX, S) {
  const b = world.nearbyBuilding;
  if (!b) return;
  const img = world.imageFor(b);
  const top = BUILDING_BASE_Y - img.height;
  const bottomWorldY = Math.max(LABEL_H + 2, top - 1); // sit above the box, clamped on-screen
  const cx = (b.worldX + img.width / 2 - cameraX) * S;
  drawText(ctx, b.label, cx, bottomWorldY * S, {
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

// Bouncing chevron just above the player's head when near a building (scaled pass).
function drawPrompt(ctx, world, player, cameraX, time) {
  if (!world.nearbyBuilding) return;
  const screenX = player.x - cameraX;
  const bounce = Math.sin(time * 6) * 2;
  const baseY = GROUND_Y - 24 + bounce;
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
  await world.setTheme('rustCity');

  const input = new InputManager();
  const player = new Player(playerSheet, PLAYER_SPAWN_X);
  const camera = new Camera(world.worldWidth, CANVAS_WIDTH);
  const overlay = new Overlay();
  const dust = new Particles();
  let dustTimer = 0;
  let promptTime = 0;

  // Click a nearby building (inside its box) to enter it, as an alternative to the Enter key.
  canvas.addEventListener('click', (e) => {
    if (overlay.isOpen) return;
    const b = world.nearbyBuilding;
    if (!b) return;
    const rect = canvas.getBoundingClientRect();
    const wx = ((e.clientX - rect.left) / rect.width) * CANVAS_WIDTH + camera.x;
    const wy = ((e.clientY - rect.top) / rect.height) * CANVAS_HEIGHT;
    const img = world.imageFor(b);
    const top = BUILDING_BASE_Y - img.height;
    if (wx >= b.worldX && wx <= b.worldX + img.width && wy >= top && wy <= BUILDING_BASE_Y) {
      overlay.show(b.sectionId);
    }
  });

  function update(dt) {
    if (overlay.isOpen) {
      if (input.wasPressed('interact')) overlay.hide();
      input.endFrame();
      return;
    }

    player.update(dt, input);
    player.x = Math.max(PLAYER_SPAWN_X, Math.min(player.x, world.worldWidth));
    camera.update(player.x);
    world.update(player.x);
    promptTime += dt;

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

    if (world.nearbyBuilding && input.wasPressed('interact')) {
      overlay.show(world.nearbyBuilding.sectionId);
    }

    input.endFrame();
  }

  function render() {
    const S = renderScale;

    // World pass — scaled, crisp pixel art.
    ctx.setTransform(S, 0, 0, S, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    world.draw(ctx, camera.x, CANVAS_WIDTH, CANVAS_HEIGHT);
    if (!overlay.isOpen) drawHighlightBox(ctx, world, camera.x);
    dust.draw(ctx, camera.x); // behind the player
    player.draw(ctx, camera.x);
    if (!overlay.isOpen) drawPrompt(ctx, world, player, camera.x, promptTime);
    if (!overlay.isOpen) drawStartArrow(ctx, player, camera.x, promptTime);
    drawVignette(ctx); // edge band, on top of the scene but under the UI text

    // Text pass — device space, anti-aliased so glyphs stay solid and readable.
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = true;
    drawIntro(ctx, camera.x, S);
    if (!overlay.isOpen) drawBuildingLabel(ctx, world, camera.x, S);
  }

  new GameLoop(update, render).start();
}

main();
