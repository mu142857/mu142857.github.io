export class Overlay {
  constructor() {
    this.el = document.getElementById('overlay');
    this.contentEl = document.getElementById('overlay-content');
    this.closeBtn = document.getElementById('overlay-close');
    this.isOpen = false;
    this._openedAt = 0;
    this.closeBtn.addEventListener('click', () => this.hide());
    // Tapping the dimmed area outside the panel closes it too (the only obvious gesture on a
    // phone, where the × is a small target). The grace period stops the click that a tap on
    // the touch ENTER button synthesizes from landing on the backdrop and closing it again.
    this.el.addEventListener('click', (e) => {
      if (e.target === this.el && performance.now() - this._openedAt > 300) this.hide();
    });
  }

  show(sectionId) {
    const template = document.getElementById(`section-${sectionId}`);
    if (!template) throw new Error(`Missing template for section: ${sectionId}`);
    this.contentEl.innerHTML = '';
    this.contentEl.appendChild(template.content.cloneNode(true));
    this.el.classList.remove('hidden');
    this.contentEl.parentElement.scrollTop = 0;
    this.isOpen = true;
    this._openedAt = performance.now();
    document.body.classList.add('overlay-open'); // hides the touch gamepad
  }

  hide() {
    this.el.classList.add('hidden');
    this.isOpen = false;
    document.body.classList.remove('overlay-open');
  }
}
