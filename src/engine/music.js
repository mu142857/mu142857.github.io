// Theme music. One looping track per skin; whenever the active theme changes — the skin
// toggle, the runner's blackout venue swap, or stepping back out into the city — the old
// track fades down while the new one fades up. Browsers refuse to start audio before the
// user has touched the page, so playback arms itself on the first gesture; until then the
// manager just remembers what should be playing.

const CROSSFADE_TIME = 1.4; // s — theme changes; a touch longer than the venue blackout
const TOGGLE_FADE_TIME = 0.5; // s — the on/off button, and the first-gesture fade-in
const BASE_VOLUME = 0.55; // keep the tracks under the game, not on top of it
const TICK_MS = 50; // setInterval, not rAF: rAF pauses in background tabs and fades would stall

const MUSIC_STORAGE_KEY = 'music-on';

export class Music {
  constructor(tracks, initialKey) {
    this.tracks = new Map(Object.entries(tracks).map(([key, src]) => {
      const audio = new Audio(src);
      audio.loop = true;
      audio.preload = 'auto';
      audio.volume = 0;
      return [key, { audio, level: 0 }]; // level 0..1, volume = level * BASE_VOLUME
    }));
    this.key = initialKey;
    this.enabled = localStorage.getItem(MUSIC_STORAGE_KEY) !== '0';
    this.unlocked = false;
    this._fadeTime = TOGGLE_FADE_TIME;
    this._timer = null;

    // Any first gesture arms playback (autoplay policy). Capture phase, so a press the game
    // canvas or a button swallows still counts.
    const unlock = () => {
      this.unlocked = true;
      window.removeEventListener('pointerdown', unlock, true);
      window.removeEventListener('keydown', unlock, true);
      this._retarget(TOGGLE_FADE_TIME);
    };
    window.addEventListener('pointerdown', unlock, true);
    window.addEventListener('keydown', unlock, true);
  }

  setTheme(key) {
    if (key === this.key || !this.tracks.has(key)) return;
    this.key = key;
    this._retarget(CROSSFADE_TIME);
  }

  setEnabled(on) {
    this.enabled = on;
    localStorage.setItem(MUSIC_STORAGE_KEY, on ? '1' : '0');
    this._retarget(TOGGLE_FADE_TIME);
  }

  _target(key) {
    return this.unlocked && this.enabled && key === this.key ? 1 : 0;
  }

  _retarget(fadeTime) {
    this._fadeTime = fadeTime;
    for (const [key, t] of this.tracks) {
      if (this._target(key) > 0 && t.audio.paused) {
        t.audio.play().catch(() => {}); // a rejected play just means "still locked"
      }
    }
    if (!this._timer) this._timer = setInterval(() => this._tick(), TICK_MS);
  }

  _tick() {
    const step = (TICK_MS / 1000) / this._fadeTime;
    let settled = true;
    for (const [key, t] of this.tracks) {
      const target = this._target(key);
      if (t.level !== target) {
        t.level = target > t.level ? Math.min(target, t.level + step) : Math.max(target, t.level - step);
        t.audio.volume = t.level * BASE_VOLUME;
        if (t.level === 0) t.audio.pause(); // keeps its position for the fade back in
      }
      if (t.level !== target) settled = false;
    }
    if (settled) {
      clearInterval(this._timer);
      this._timer = null;
    }
  }
}
