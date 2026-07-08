export class Camera {
  constructor(worldWidth, canvasWidth) {
    this.worldWidth = worldWidth;
    this.canvasWidth = canvasWidth;
    this.x = 0;
  }

  // Hard-clamped centering, no dead-zone/smoothing (MVP feel — easy to upgrade later
  // without touching any other module).
  update(playerCenterX) {
    const target = playerCenterX - this.canvasWidth / 2;
    this.x = Math.max(0, Math.min(target, this.worldWidth - this.canvasWidth));
  }
}
