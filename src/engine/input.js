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
    // On-screen touch buttons feed the same actions, keyed by action name rather than key code.
    this._virtualHeld = new Set();
    this._virtualPressed = new Set();

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
    return this._virtualHeld.has(action) || ACTION_KEYS[action].some((code) => this._held.has(code));
  }

  wasPressed(action) {
    return this._virtualPressed.has(action)
      || ACTION_KEYS[action].some((code) => this._pressedThisFrame.has(code));
  }

  anyKeyPressed() {
    return this._anyKeyThisFrame;
  }

  // --- Touch buttons -------------------------------------------------------
  // A tap can start and end between two update ticks, so the press is latched until the next
  // endFrame() rather than being read straight off the held set.
  pressVirtual(action) {
    if (!ACTION_KEYS[action]) throw new Error(`Unknown action: ${action}`);
    this._virtualHeld.add(action);
    this._virtualPressed.add(action);
    this._anyKeyThisFrame = true;
  }

  releaseVirtual(action) {
    this._virtualHeld.delete(action);
  }

  // Call once per update tick, after all state has been read for the frame.
  endFrame() {
    this._pressedThisFrame.clear();
    this._virtualPressed.clear();
    this._anyKeyThisFrame = false;
  }
}
