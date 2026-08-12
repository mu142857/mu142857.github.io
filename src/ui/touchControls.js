// On-screen gamepad for phones/tablets: walk buttons on the left, sprint + jump on the right,
// and a contextual ENTER button that appears when the player is standing by a building.
//
// Pointer events (not touch events) so one finger per button works with multi-touch — holding
// "right" while tapping "jump" is the common case. Releases are tracked on `window` keyed by
// pointerId, so a finger that slides off a button (or a button that hides mid-press) still
// releases exactly its own action and never leaves one stuck down.
import { t } from '../i18n.js';

export class TouchControls {
  constructor(input) {
    this.root = document.getElementById('touch-controls');
    this.enterBtn = this.root.querySelector('.tbtn-enter');
    this.enterIcon = this.enterBtn.querySelector('i');
    this.enterLabel = this.enterBtn.querySelector('.tbtn-label');
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

  // In the runner the only thing that matters is jumping, so the walk pad and the sprint
  // button step aside (see #touch-controls.runner in style.css) and jump gets the big target.
  setMode(mode) {
    const runner = mode === 'runner';
    this.root.classList.toggle('runner', runner);
    if (runner) this.releaseAll(); // nothing should stay held across a scene change
  }

  // kind is 'enter' | 'back'; the visible label comes from the i18n dictionary, so it is
  // re-resolved every call and follows a language switch on its own.
  setEnter(visible, kind = 'enter') {
    this.enterBtn.classList.toggle('hidden', !visible);
    const label = t(kind === 'back' ? 'game.back' : 'game.enter');
    if (this.enterLabel.textContent === label) return;
    this.enterLabel.textContent = label;
    const back = kind === 'back';
    this.enterIcon.className = back ? 'fas fa-sign-out-alt' : 'fas fa-sign-in-alt';
    this.enterBtn.setAttribute('aria-label', back ? 'Back to the city' : 'Enter');
  }

  releaseAll() {
    for (const { btn, action } of this._active.values()) {
      btn.classList.remove('active');
      this._input.releaseVirtual(action);
    }
    this._active.clear();
  }
}
