// Tiny pixel-particle system (kept blocky and integer-positioned to match the pixel art).
// Used for the dust the character kicks up while sprinting.
export class Particles {
  constructor() {
    this.list = [];
  }

  emit(p) {
    this.list.push(p);
  }

  update(dt) {
    for (let i = this.list.length - 1; i >= 0; i--) {
      const p = this.list[i];
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.vy += p.g * dt;
      p.life -= dt;
      if (p.life <= 0) this.list.splice(i, 1);
    }
  }

  draw(ctx, cameraX) {
    for (const p of this.list) {
      // Stepped alpha (not a smooth fade) so the puff reads as chunky pixels, not a gradient.
      ctx.globalAlpha = Math.ceil((p.life / p.maxLife) * 3) / 3;
      ctx.fillStyle = p.color;
      ctx.fillRect(Math.round(p.x - cameraX), Math.round(p.y), p.size, p.size);
    }
    ctx.globalAlpha = 1;
  }
}
