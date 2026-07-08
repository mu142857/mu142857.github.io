const MAX_DT = 0.1; // clamp to avoid a spiral-of-death after the tab is backgrounded and refocused

export class GameLoop {
  constructor(update, render) {
    this.update = update;
    this.render = render;
    this._lastTime = null;
    this._rafId = null;
    this._tick = this._tick.bind(this);
  }

  start() {
    this._rafId = requestAnimationFrame(this._tick);
  }

  stop() {
    if (this._rafId !== null) cancelAnimationFrame(this._rafId);
    this._rafId = null;
    this._lastTime = null;
  }

  _tick(timestamp) {
    if (this._lastTime === null) this._lastTime = timestamp;
    const dt = Math.min((timestamp - this._lastTime) / 1000, MAX_DT);
    this._lastTime = timestamp;

    this.update(dt);
    this.render();

    this._rafId = requestAnimationFrame(this._tick);
  }
}
