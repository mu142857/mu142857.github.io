// Boot and main loop of the 480x270 site (next.html). It runs next to the current site and
// shares its content: index.html's section templates, the overlay, the input manager, the
// touch gamepad and the language dictionary are all imported, not copied.
//
// URL parameters (for looking at things and for the screenshot tool):
//   ?scene=<folder>   which scene under Assets/ (default: dawn, else dawn-greybox)
//   ?x=1200           put the player there
//   ?mix=0.7          pin the dawn->sunrise mix instead of following the player's x
//   ?fx=off           no atmosphere (water, glows, clouds drift, fog, rays, motes)
//   ?filter=low|off   grain + vignette only / no filter at all
// window.G = { player, camera, scene, clock, stage, png(), step(seconds), open(id) }

import { W, H, mkCanvas, clamp, Stage, Clock } from './engine.js';
import { loadScene } from './scene.js';
import { Player } from './player.js';
import * as filter from './filter.js';
import {
  adoptTemplates, wireSettings, wireRotateHint, drawIntro, drawStopLabel, stopLabelY, drawDoorChevron,
} from './ui.js';
import { InputManager } from '../engine/input.js';
import { Particles } from '../engine/particles.js';
import { Overlay } from '../ui/overlay.js';
import { TouchControls } from '../ui/touchControls.js';
import { loadPixelFont } from '../ui/pixelText.js';
import { applyTranslations } from '../i18n.js';

const params = new URLSearchParams(location.search);

async function pickScene() {
  const asked = params.get('scene');
  if (asked) return loadScene(asked);
  try {
    return await loadScene('dawn'); // the real art, once it exists
  } catch {
    return loadScene('dawn-greybox');
  }
}

async function main() {
  applyTranslations(); // before anything is seen, so a saved 中文 never flashes English
  const stage = new Stage();
  const [buf, g] = mkCanvas(W, H);

  const [scene] = await Promise.all([pickScene(), loadPixelFont(), adoptTemplates()]);
  scene.fxOn = params.get('fx') !== 'off';
  const tier = params.get('filter');
  if (tier === 'off' || tier === 'low') filter.FILTER.tier = tier;

  const input = new InputManager();
  const overlay = new Overlay();
  const touch = new TouchControls(input);
  const dust = new Particles();
  const openSettings = wireSettings(overlay);
  const syncRotateHint = wireRotateHint(stage);

  const startX = params.has('x') ? Number(params.get('x')) : scene.spawn;
  const player = new Player(scene.ground, clamp(startX || scene.spawn, 0, scene.length));
  const camera = { x: 0 };
  const pinnedMix = params.has('mix') ? clamp(Number(params.get('mix')) || 0, 0, 1) : null;
  let mix = 0;
  let nearStop = null;
  let dustTimer = 0;

  function follow() {
    camera.x = Math.round(clamp(player.x - W / 2, 0, Math.max(0, scene.length - W)));
    mix = pinnedMix ?? scene.mixAt(player.x);
  }
  follow();

  const syncTouch = () => { touch.setVisible(stage.touch); syncRotateHint(); };
  stage.onLayout = () => { syncTouch(); clock.dirty = true; };

  // The mid-air hop pushes off a flat fan of sparks, so it reads as a push and not a glitch.
  player.onDoubleJump = (x, y) => {
    for (let i = 0; i < 14; i++) {
      const angle = Math.PI * (i / 13);
      const speed = 50 + Math.random() * 60;
      const life = 0.26 + Math.random() * 0.16;
      dust.emit({
        x, y: y - 2, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed * 0.5,
        g: 320, life, maxLife: life, size: Math.random() < 0.5 ? 2 : 1, color: '#ffe9a8',
      });
    }
  };

  const openStop = (stop) => { if (!overlay.isOpen) overlay.show(stop.id); };

  // Click / tap a stop: enter it if the character is already there, otherwise walk to its
  // door and enter on arrival.
  stage.canvas.addEventListener('click', (e) => {
    if (overlay.isOpen) return;
    const { nx, ny } = stage.norm(e.clientX, e.clientY);
    const wx = nx * W + camera.x;
    const wy = ny * H;
    const stop = scene.stops.find((s) => wx >= s.x0 && wx <= s.x1);
    if (!stop || wy > scene.ground + 10) return;
    if (scene.stopAt(player.x) === stop) openStop(stop);
    else player.walkTo(stop.door, () => openStop(stop));
  });
  window.addEventListener('keydown', (e) => { if (e.code === 'Escape' && overlay.isOpen) overlay.hide(); });

  function update(dt) {
    if (overlay.isOpen) {
      if (input.wasPressed('interact')) overlay.hide();
      input.endFrame();
      return;
    }
    player.update(dt, input, scene.length);
    follow();
    nearStop = scene.stopAt(player.x);
    touch.setEnter(stage.touch && !!nearStop, 'enter');

    if (player.sprinting && player.anim === 'run') { // dust kicked up behind a sprint
      dustTimer += dt;
      while (dustTimer >= 0.035) {
        dustTimer -= 0.035;
        const back = -player.facing;
        const life = 0.34 + Math.random() * 0.18;
        dust.emit({
          x: player.x + back * 6 + (Math.random() * 4 - 2), y: scene.ground - 2 - Math.random() * 5,
          vx: back * (30 + Math.random() * 40), vy: -(20 + Math.random() * 34),
          g: 160, life, maxLife: life, size: Math.random() < 0.6 ? 2 : 1,
          color: mix < 0.5 ? '#8f9cc4' : '#f1dca6',
        });
      }
    } else {
      dustTimer = 0;
    }
    dust.update(dt);

    if (input.wasPressed('interact') && nearStop) openStop(nearStop);
    input.endFrame();
  }

  let backdropTick = 0;
  function draw() {
    const S = stage.scale;
    const t = clock.time;
    scene.render(g, camera.x, mix, t, (gg) => {
      dust.draw(gg, camera.x);
      player.draw(gg, camera.x, mix);
    });
    const showStop = nearStop && !overlay.isOpen;
    if (showStop) drawDoorChevron(g, nearStop, camera.x, stopLabelY(nearStop, scene.ground) + 26, t, mix);

    filter.capture(buf);
    const ctx = stage.ctx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(buf, 0, 0, W * S, H * S);
    filter.draw(ctx, S, scene.warmthAt(mix));

    ctx.imageSmoothingEnabled = true;
    if (scene.title) {
      const walked = player.farthest - scene.spawn;
      drawIntro(ctx, S, scene.title, mix, 1 - clamp((walked - 60) / 110, 0, 1), stage.touch);
    }
    if (showStop) drawStopLabel(ctx, S, nearStop, camera.x, scene.ground, mix, stage.touch);

    if (backdropTick++ % 4 === 0) stage.paintBackdrop(buf);
  }

  const clock = new Clock(update, draw);
  syncTouch();
  clock.start();

  window.G = {
    player, camera, scene, clock, stage, filter: filter.FILTER,
    get mix() { return mix; },
    // The 480x270 buffer as a PNG data URL, redrawn first (works with rAF asleep).
    png() { draw(); return buf.toDataURL('image/png'); },
    step(seconds = 1 / 60) { for (let s = 0; s < seconds; s += 1 / 60) clock.step(1 / 60); },
    open(id) { overlay.show(id); },
    openSettings,
  };
  window.READY = true;
}

main().catch((e) => {
  console.error(e);
  const el = document.getElementById('boot-error');
  if (el) { el.textContent = String(e && e.message ? e.message : e); el.classList.remove('hidden'); }
});
