const ACTION_KEYS = {
  left: ['ArrowLeft', 'KeyA'],
  right: ['ArrowRight', 'KeyD'],
  jump: ['Space'],
  interact: ['ArrowUp', 'Enter'],
  sprint: ['ShiftLeft', 'ShiftRight'],
};

const PREVENT_DEFAULT_CODES = new Set(Object.values(ACTION_KEYS).flat());

export class InputManager {
  constructor() {
    this._held = new Set();
    this._pressedThisFrame = new Set();
    this._anyKeyThisFrame = false;

    window.addEventListener('keydown', (e) => {
      if (PREVENT_DEFAULT_CODES.has(e.code)) e.preventDefault();
      this._held.add(e.code);
      this._anyKeyThisFrame = true;
      if (!e.repeat) this._pressedThisFrame.add(e.code);
    });

    window.addEventListener('keyup', (e) => {
      this._held.delete(e.code);
    });
  }

  isDown(action) {
    return ACTION_KEYS[action].some((code) => this._held.has(code));
  }

  wasPressed(action) {
    return ACTION_KEYS[action].some((code) => this._pressedThisFrame.has(code));
  }

  anyKeyPressed() {
    return this._anyKeyThisFrame;
  }

  // Call once per update tick, after all state has been read for the frame.
  endFrame() {
    this._pressedThisFrame.clear();
    this._anyKeyThisFrame = false;
  }
}
