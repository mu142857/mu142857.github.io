export class Overlay {
  constructor() {
    this.el = document.getElementById('overlay');
    this.contentEl = document.getElementById('overlay-content');
    this.closeBtn = document.getElementById('overlay-close');
    this.isOpen = false;
    this.closeBtn.addEventListener('click', () => this.hide());
  }

  show(sectionId) {
    const template = document.getElementById(`section-${sectionId}`);
    if (!template) throw new Error(`Missing template for section: ${sectionId}`);
    this.contentEl.innerHTML = '';
    this.contentEl.appendChild(template.content.cloneNode(true));
    this.el.classList.remove('hidden');
    this.isOpen = true;
  }

  hide() {
    this.el.classList.add('hidden');
    this.isOpen = false;
  }
}
