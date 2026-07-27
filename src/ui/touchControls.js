// On-screen gamepad for phones/tablets: walk buttons on the left, sprint + jump on the right,
// and a contextual ENTER button that appears when the player is standing by a building.
//
// Pointer events (not touch events) so one finger per button works with multi-touch — holding
// "right" while tapping "jump" is the common case. Releases are tracked on `window` keyed by
// pointerId, so a finger that slides off a button (or a button that hides mid-press) still
// releases exactly its own action and never leaves one stuck down.
export class TouchControls {
  constructor(input) {
    this.root = document.getElementById('touch-controls');
    this.enterBtn = this.root.querySelector('.tbtn-enter');
    this._input = input;
    this._active = new Map(); // pointerId -> { btn, action }

    for (const btn of this.root.querySelectorAll('.tbtn')) {
      const action = btn.dataset.action;
      btn.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        if (this._active.has(e.pointerId)) return;
        this._active.set(e.pointerId, { btn, action });
        btn.classList.add('active');
        input.pressVirtual(action);
      });
      // Long-press on a button must not pop the text-selection / callout menu.
      btn.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    const release = (e) => {
      const entry = this._active.get(e.pointerId);
      if (!entry) return;
      this._active.delete(e.pointerId);
      entry.btn.classList.remove('active');
      input.releaseVirtual(entry.action);
    };
    window.addEventListener('pointerup', release);
    window.addEventListener('pointercancel', release);
  }

  setVisible(visible) {
    this.root.classList.toggle('hidden', !visible);
    if (!visible) this.releaseAll();
  }

  setEnterVisible(visible) {
    this.enterBtn.classList.toggle('hidden', !visible);
  }

  releaseAll() {
    for (const { btn, action } of this._active.values()) {
      btn.classList.remove('active');
      this._input.releaseVirtual(action);
    }
    this._active.clear();
  }
}
