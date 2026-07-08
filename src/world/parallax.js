export class ParallaxLayer {
  constructor(image, factor, { align = 'top' } = {}) {
    this.image = image;
    this.factor = factor;
    this.align = align;
    this.tileWidth = image.width;
  }

  draw(ctx, cameraX, canvasWidth, canvasHeight) {
    const offset = cameraX * this.factor;
    // cameraX is always clamped >= 0, so a plain modulo is safe here (no negative-offset wraparound to worry about).
    const startX = -(offset % this.tileWidth);
    const drawY = this.align === 'bottom' ? canvasHeight - this.image.height : 0;

    for (let x = startX; x < canvasWidth; x += this.tileWidth) {
      ctx.drawImage(this.image, x, drawY);
    }
  }
}
