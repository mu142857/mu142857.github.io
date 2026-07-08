import { FRAME_W, FRAME_H, SHEET_COLS } from './config.js';

// Frame numbers throughout the codebase are 1-indexed (matching the art spec).
// This is the ONLY place the -1 conversion to a 0-indexed grid happens.
export function getFrameRect(frameNumber) {
  const idx = frameNumber - 1;
  const col = idx % SHEET_COLS;
  const row = Math.floor(idx / SHEET_COLS);
  return { sx: col * FRAME_W, sy: row * FRAME_H, sw: FRAME_W, sh: FRAME_H };
}

export function drawFrame(ctx, image, frameNumber, dx, dy, { flip = false } = {}) {
  const { sx, sy, sw, sh } = getFrameRect(frameNumber);
  if (!flip) {
    ctx.drawImage(image, sx, sy, sw, sh, dx, dy, sw, sh);
    return;
  }
  ctx.save();
  ctx.translate(dx + sw, dy);
  ctx.scale(-1, 1);
  ctx.drawImage(image, sx, sy, sw, sh, 0, 0, sw, sh);
  ctx.restore();
}
