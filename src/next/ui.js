// Everything around the scene: the section templates, the Settings modal, and the text drawn
// over the picture (the intro lines and the name over a door).
//
// Text is never baked into the art. It is drawn in DEVICE space after the buffer has been
// upscaled and filtered — large and anti-aliased, the way src/ui/pixelText.js intends — so
// glyphs stay solid, and grain and vignette do not sit on top of them.

import { W, clamp, mixColor, rgb } from './engine.js';
import { drawText, measureText, wrapText } from '../ui/pixelText.js';
import { getLang, setLang, applyTranslations, t } from '../i18n.js';
import { applyBiliStats } from '../bili-stats.js';

// The section content lives in index.html's <template id="section-*"> blocks. Until the
// cut-over there is exactly one copy of it: this page fetches index.html and adopts those
// templates (the Settings one included), then runs the same language and follower-count
// passes index.html runs.
export async function adoptTemplates() {
  const res = await fetch('index.html', { cache: 'no-cache' });
  if (!res.ok) throw new Error('Could not load index.html for the section templates');
  const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
  let n = 0;
  for (const src of doc.querySelectorAll('template[id^="section-"]')) {
    if (document.getElementById(src.id)) continue;
    const tpl = document.createElement('template');
    tpl.id = src.id;
    tpl.innerHTML = src.innerHTML;
    document.body.appendChild(tpl);
    n++;
  }
  applyTranslations();
  applyBiliStats(); // patches the templates in place when data/bilibili.json arrives
  return n;
}

// Settings opens through the same overlay as the sections; the template is cloned fresh each
// time, so the buttons are re-wired on every open (as in src/main.js).
export function wireSettings(overlay, music) {
  const open = () => {
    overlay.show('settings');
    const musicBtn = document.getElementById('setting-music');
    if (musicBtn && !music) musicBtn.closest('.setting-row').remove();
    if (musicBtn && music) {
      const desc = musicBtn.closest('.setting-row').querySelector('.meta');
      if (desc) desc.textContent = t('settings.musicDescNext'); // index.html still describes the old worlds
      const sync = () => {
        musicBtn.textContent = t(music.enabled ? 'ui.on' : 'ui.off');
        musicBtn.classList.toggle('off', !music.enabled);
      };
      sync();
      musicBtn.addEventListener('click', () => { music.setEnabled(!music.enabled); sync(); });
    }

    const langBtn = document.getElementById('setting-lang');
    langBtn.textContent = getLang() === 'zh' ? '中文' : 'English';
    langBtn.addEventListener('click', () => {
      setLang(getLang() === 'zh' ? 'en' : 'zh');
      open();
    });

    const clearBtn = document.getElementById('setting-clear');
    clearBtn.textContent = t('ui.clear');
    clearBtn.addEventListener('click', () => {
      if (!clearBtn.classList.contains('confirm')) {
        clearBtn.classList.add('confirm');
        clearBtn.textContent = t('ui.confirm');
        return;
      }
      localStorage.clear();
      location.reload();
    });
  };
  document.getElementById('settings-toggle').addEventListener('click', open);
  return open;
}

// ---------------------------------------------------------------- text over the picture
// Sizes are in scene pixels; S (device pixels per scene pixel) turns them into font sizes.
const HI = 9;
const NAME = 18;
const HINT = 7;
const LABEL = 10;
const KEYS = 6;

// Light text before dawn, dark once the sky behind it is bright (it switches at the halfway
// point, like 好结局's narration colour).
function inkFor(mix) {
  return mix < 0.5
    ? { main: '#f0f2ff', dim: '#aeb8dc', shade: 'rgba(6, 8, 20, 0.5)' }
    : { main: '#2c2a48', dim: '#4d4a6a', shade: 'rgba(255, 244, 214, 0.4)' };
}

function shadowed(ctx, text, x, y, S, opts, shade) {
  const o = Math.max(1, Math.round(S / 3));
  drawText(ctx, text, x + o, y + o, { ...opts, color: shade });
  drawText(ctx, text, x, y, opts);
}

// "Hi, I am / Jiamu Shangguan" and one line of controls, inside the scene's clean patch of
// sky (`title` in scene.json, screen coordinates). `alpha` fades it as the player walks off.
export function drawIntro(ctx, S, rect, mix, alpha, touch) {
  if (alpha <= 0.01) return;
  const ink = inkFor(mix);
  const x = rect.x * S;
  let y = rect.y;
  ctx.save();
  ctx.globalAlpha = alpha;
  shadowed(ctx, t('game.hi'), x, y * S, S, { sizePx: HI * S, color: ink.dim }, ink.shade);
  y += HI + 3;
  shadowed(ctx, t('game.name'), x, y * S, S, { sizePx: NAME * S, color: ink.main }, ink.shade);
  y += NAME + 6;
  for (const line of wrapText(ctx, t(touch ? 'game.touchControls' : 'game.keyControls'), rect.w * S, HINT * S)) {
    shadowed(ctx, line, x, y * S, S, { sizePx: HINT * S, color: ink.dim }, ink.shade);
    y += HINT + 3;
  }
  ctx.restore();
}

// The section's name on a small plate above its door, with the key to press under it.
// Returns the plate's bottom edge (scene px) so the bouncing chevron can hang below it.
export function stopLabelY(stop, ground) {
  return stop.labelY ?? Math.max(12, ground - 98);
}

export function drawStopLabel(ctx, S, stop, cam, ground, mix, touch) {
  const name = t(`building.${stop.id}`);
  const keys = touch ? '' : `↑ / ${t('game.enter')}`;
  const nameW = measureText(ctx, name, LABEL * S);
  const keysW = keys ? measureText(ctx, keys, KEYS * S) : 0;
  const padX = 6 * S;
  const padY = 4 * S;
  const w = Math.max(nameW, keysW) + padX * 2;
  const h = (LABEL + (keys ? KEYS + 3 : 0)) * S + padY * 2;
  const cx = clamp((stop.door - cam) * S, w / 2 + 4 * S, W * S - w / 2 - 4 * S);
  const top = stopLabelY(stop, ground) * S;
  const line = Math.max(1, Math.round(S / 4));
  const edge = mixColor('#c9d2f2', '#ffe9b0', mix);
  ctx.save();
  ctx.fillStyle = 'rgba(10, 12, 26, 0.58)';
  ctx.fillRect(cx - w / 2, top, w, h);
  ctx.fillStyle = rgb(edge, 0.7);
  ctx.fillRect(cx - w / 2, top, w, line);
  ctx.fillRect(cx - w / 2, top + h - line, w, line);
  ctx.fillRect(cx - w / 2, top, line, h);
  ctx.fillRect(cx + w / 2 - line, top, line, h);
  drawText(ctx, name, cx, top + padY, { sizePx: LABEL * S, color: '#fff4d0', align: 'center' });
  if (keys) drawText(ctx, keys, cx, top + padY + (LABEL + 3) * S, { sizePx: KEYS * S, color: rgb(edge, 0.85), align: 'center' });
  ctx.restore();
  return h / S;
}

// A small chevron bobbing over the door, drawn in the buffer (hard pixels).
export function drawDoorChevron(g, stop, cam, y, time, mix) {
  const x = Math.round(stop.door - cam);
  const by = Math.round(y + Math.sin(time * 5) * 1.5);
  g.fillStyle = rgb(mixColor('#ffe9a8', '#fff6d8', mix));
  g.fillRect(x - 4, by, 9, 1);
  g.fillRect(x - 3, by + 1, 7, 1);
  g.fillRect(x - 2, by + 2, 5, 1);
  g.fillRect(x - 1, by + 3, 3, 1);
  g.fillRect(x, by + 4, 1, 1);
}

// The "turn your phone" hint: shown on a phone held upright, gone after a few seconds.
export function wireRotateHint(stage) {
  const hint = document.getElementById('rotate-hint');
  if (!hint) return () => {};
  let dismissed = false;
  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    hint.classList.add('fading');
    setTimeout(() => hint.classList.add('hidden'), 700);
  };
  return () => {
    const show = stage.rotated && !dismissed;
    hint.classList.toggle('hidden', !show);
    if (show) setTimeout(dismiss, 5000);
  };
}
