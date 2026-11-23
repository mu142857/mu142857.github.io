// Boot and main loop of the 480x270 site (index.html). The overlay, the input manager, the
// touch gamepad and the language dictionary are the same modules the first site (v1.html,
// src/main.js) uses: imported, not copied.
//
// URL parameters (for looking at things and for the screenshot tool):
//   ?scene=<folder>   which scene under Assets/ (default: dawn, else dawn-greybox)
//   ?x=1200           put the player there
//   ?mix=0.7          pin the dawn->sunrise mix instead of following the player's x
//   ?fx=off           no atmosphere (water, glows, clouds drift, fog, rays, motes)
//   ?filter=low|off   grain + vignette only / no filter at all
// window.G = { player, camera, scene, clock, stage, runner, music, mode, png(), step(seconds),
//              open(id), enterRun(), exitRun() }

import { W, H, mkCanvas, clamp, Stage, Clock } from './engine.js';
import { loadScene } from './scene.js';
import { Player } from './player.js';
import { loadChen, GETUP_TIME } from './chen.js';
import { loadRunner } from './runner.js';
import { Music } from '../engine/music.js';
import * as filter from './filter.js';
import {
  wireSettings, wireRotateHint, drawIntro, drawStopLabel, stopLabelY, drawDoorChevron,
} from './ui.js';
import { InputManager } from '../engine/input.js';
import { Particles } from '../engine/particles.js';
import { Overlay } from '../ui/overlay.js';
import { TouchControls } from '../ui/touchControls.js';
import { loadPixelFont } from '../ui/pixelText.js';
import { applyTranslations } from '../i18n.js';
import { applyBiliStats } from '../bili-stats.js';

const params = new URLSearchParams(location.search);

// One track for the street, another for the run; they cross-fade when the scene changes.
const MUSIC_TRACKS = { street: 'Assets/music/Silvaron.m4a', run: 'Assets/music/glitch.mp3' };
const FADE_TIME = 0.35; // seconds for each half of the black between the street and the run

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
  applyBiliStats(); // live follower count: patches the section templates when data/bilibili.json arrives
  const stage = new Stage();
  const [buf, g] = mkCanvas(W, H);

  const [scene, chen] = await Promise.all([
    pickScene(), loadChen().catch(() => null), loadPixelFont(),
  ]);
  scene.fxOn = params.get('fx') !== 'off';
  const tier = params.get('filter');
  if (tier === 'off' || tier === 'low') filter.FILTER.tier = tier;

  const input = new InputManager();
  const overlay = new Overlay();
  const touch = new TouchControls(input);
  const dust = new Particles();
  const music = new Music(MUSIC_TRACKS, 'street');
  const openSettings = wireSettings(overlay, music);
  const syncRotateHint = wireRotateHint(stage);

  const startX = params.has('x') ? Number(params.get('x')) : scene.spawn;
  const player = new Player(scene.ground, clamp(startX || scene.spawn, 0, scene.length), chen);
  // A plain visit opens like The Cloud does: she is lying on the walk, and gets up.
  if (chen && !params.has('x')) player.lieDown(1.1, GETUP_TIME);
  // The run (the minigame at the tip of the pier). Without it the pier is just scenery.
  const runner = chen ? await loadRunner(scene, chen, input, dust).catch((e) => { console.error(e); return null; }) : null;
  if (!runner) scene.stops = scene.stops.filter((s) => s.id !== 'run');
  let mode = 'street'; // 'street' | 'run'
  const fade = { a: 0, dir: 0, then: null }; // the screen goes black while the scene is swapped
  const transition = (then) => { if (!fade.dir) { fade.dir = 1; fade.then = then; } };
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

  function enterRun() {
    mode = 'run';
    document.body.classList.add('in-runner');
    touch.setMode('runner');
    runner.reset(1); // the pier is at sunrise, so the run starts there
    music.setTheme('run');
  }
  function exitRun() {
    mode = 'street';
    document.body.classList.remove('in-runner');
    touch.setMode('city');
    dust.list.length = 0;
    player.vel = 0;
    player.facing = -1; // back on the pier, looking down the street she came along
    music.setTheme('street');
  }

  const openStop = (stop) => {
    if (overlay.isOpen || fade.dir) return;
    if (stop.id === 'run') transition(enterRun);
    else overlay.show(stop.id);
  };

  // Click / tap a stop: enter it if the character is already there, otherwise walk to its
  // door and enter on arrival.
  stage.canvas.addEventListener('click', (e) => {
    if (overlay.isOpen || fade.dir) return;
    if (mode === 'run') { input.pressVirtual('jump'); input.releaseVirtual('jump'); return; } // a click jumps
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
    if (fade.dir) {
      fade.a += (fade.dir * dt) / FADE_TIME;
      if (fade.dir > 0 && fade.a >= 1) { fade.a = 1; fade.dir = -1; fade.then(); }
      else if (fade.dir < 0 && fade.a <= 0) { fade.a = 0; fade.dir = 0; }
      if (fade.dir > 0) { input.endFrame(); return; } // nothing moves while the lights go down
    }
    if (mode === 'run') {
      touch.setEnter(stage.touch, 'back');
      if (runner.update(dt) === 'exit') transition(exitRun);
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
    const running = mode === 'run';
    const light = running ? runner.mix : mix;
    if (running) {
      runner.draw(g, t);
    } else {
      scene.render(g, camera.x, mix, t, (gg) => {
        dust.draw(gg, camera.x);
        player.draw(gg, camera.x, mix);
      });
    }
    const showStop = !running && nearStop && !overlay.isOpen;
    if (showStop) drawDoorChevron(g, nearStop, camera.x, stopLabelY(nearStop, scene.ground) + 26, t, mix);

    filter.capture(buf);
    const ctx = stage.ctx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(buf, 0, 0, W * S, H * S);
    filter.draw(ctx, S, scene.warmthAt(light));

    ctx.imageSmoothingEnabled = true;
    if (running) runner.drawHud(ctx, S, stage.touch);
    if (!running && scene.title) {
      const walked = player.farthest - scene.spawn;
      drawIntro(ctx, S, scene.title, mix, 1 - clamp((walked - 60) / 110, 0, 1), stage.touch);
    }
    if (showStop) drawStopLabel(ctx, S, nearStop, camera.x, scene.ground, mix, stage.touch);

    if (fade.a > 0) {
      ctx.fillStyle = `rgba(4, 5, 12, ${Math.min(1, fade.a)})`;
      ctx.fillRect(0, 0, W * S, H * S);
    }

    if (backdropTick++ % 4 === 0) stage.paintBackdrop(buf);
  }

  const clock = new Clock(update, draw);
  syncTouch();
  clock.start();

  window.G = {
    player, camera, scene, clock, stage, filter: filter.FILTER, runner, music, input,
    get mix() { return mode === 'run' ? runner.mix : mix; },
    get mode() { return mode; },
    enterRun, exitRun, // skip the fade (for tests and screenshots)
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
