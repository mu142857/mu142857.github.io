import { loadImage } from '../engine/assets.js';
import {
  BUILDING_BASE_Y, PROXIMITY_RADIUS, MODULATE_COLOR,
  LAYOUT_START_X, BUILDING_GAP,
} from '../engine/config.js';
import { ParallaxLayer } from './parallax.js';
import { THEMES } from './themes.js';
import { BUILDINGS } from './buildings.js';

const WORLD_END_MARGIN = 80; // walkable space past the last building

export class World {
  constructor() {
    this.layers = [];
    this.ground = null;
    this.theme = null;
    this.buildings = BUILDINGS;
    this.buildingImages = new Map(); // building id -> HTMLImageElement
    this.lampImage = null;
    this.lamps = []; // { worldX } for lamps placed between buildings
    this.worldWidth = 0;
    this.nearbyBuilding = null;
  }

  async setTheme(themeKey) {
    const theme = THEMES[themeKey];
    if (!theme) throw new Error(`Unknown theme: ${themeKey}`);

    const layerImages = await Promise.all(theme.layers.map((l) => loadImage(l.src)));
    this.layers = theme.layers.map((l, i) => new ParallaxLayer(layerImages[i], l.factor, { align: l.align }));

    const groundImage = await loadImage(theme.ground.src);
    this.ground = new ParallaxLayer(groundImage, theme.ground.factor, { align: theme.ground.align });

    const [buildingImages, lampImage] = await Promise.all([
      Promise.all(theme.buildings.map(loadImage)),
      loadImage(theme.lamp),
    ]);
    this.buildingImages = new Map(this.buildings.map((b, i) => [b.id, buildingImages[i]]));
    this.lampImage = lampImage;

    this._layout();
    this.theme = themeKey;
  }

  // Pack buildings left-to-right: building | gap | lamp | gap | building | ...
  _layout() {
    this.lamps = [];
    let x = LAYOUT_START_X;
    this.buildings.forEach((b, i) => {
      b.worldX = x;
      b.width = this.imageFor(b).width;
      x += b.width;
      if (i < this.buildings.length - 1) {
        x += BUILDING_GAP;
        this.lamps.push({ worldX: x });
        x += this.lampImage.width + BUILDING_GAP;
      }
    });
    this.worldWidth = x + WORLD_END_MARGIN;
  }

  imageFor(building) {
    return this.buildingImages.get(building.id);
  }

  update(playerCenterX) {
    // Buildings are packed close, so proximity zones can overlap — pick the nearest by center.
    let best = null;
    let bestDist = Infinity;
    for (const b of this.buildings) {
      const inRange = playerCenterX >= b.worldX - PROXIMITY_RADIUS
        && playerCenterX <= b.worldX + b.width + PROXIMITY_RADIUS;
      const dist = Math.abs(playerCenterX - (b.worldX + b.width / 2));
      if (inRange && dist < bestDist) {
        best = b;
        bestDist = dist;
      }
    }
    this.nearbyBuilding = best;
  }

  draw(ctx, cameraX, canvasWidth, canvasHeight) {
    for (const layer of this.layers) layer.draw(ctx, cameraX, canvasWidth, canvasHeight);
    this._drawStructures(ctx, cameraX, canvasWidth);

    // CanvasModulate: dim everything drawn so far (parallax + buildings + lamps) by multiplying
    // with MODULATE_COLOR. Ground and the player are drawn afterward, staying bright.
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = MODULATE_COLOR;
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    ctx.globalCompositeOperation = 'source-over';

    this.ground.draw(ctx, cameraX, canvasWidth, canvasHeight);
  }

  _drawStructures(ctx, cameraX, canvasWidth) {
    for (const b of this.buildings) {
      const img = this.imageFor(b);
      const drawX = b.worldX - cameraX;
      if (drawX + img.width < 0 || drawX > canvasWidth) continue;
      ctx.drawImage(img, drawX, BUILDING_BASE_Y - img.height);
    }
    for (const lamp of this.lamps) {
      const drawX = lamp.worldX - cameraX;
      if (drawX + this.lampImage.width < 0 || drawX > canvasWidth) continue;
      ctx.drawImage(this.lampImage, drawX, BUILDING_BASE_Y - this.lampImage.height);
    }
  }
}
