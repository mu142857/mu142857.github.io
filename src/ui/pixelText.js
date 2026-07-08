// Pixel-font text for the canvas. IMPORTANT: text is drawn in DEVICE space (identity
// transform, smoothing ON) at a moderate font size — NOT rasterized at a tiny native px and
// upscaled by RENDER_SCALE, which mushed the glyphs. Rendering the font large and letting it
// sit small on the high-res canvas gives solid, crisp, readable letters. Callers reset the
// transform to identity and pass device coordinates + a device font size.

const FAMILY = 'PixelFont';

export async function loadPixelFont() {
  const face = new FontFace(FAMILY, "url('Assets/shared/PixelFont.ttf')");
  await face.load();
  document.fonts.add(face);
}

export function measureText(ctx, text, sizePx) {
  ctx.font = `${sizePx}px "${FAMILY}"`;
  return ctx.measureText(text).width;
}

export function drawText(ctx, text, x, y, { sizePx, color = '#ffffff', align = 'left', baseline = 'top' } = {}) {
  ctx.font = `${sizePx}px "${FAMILY}"`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = baseline;
  ctx.fillText(text, x, y);
}

export function wrapText(ctx, text, maxWidth, sizePx) {
  const words = text.split(' ');
  const lines = [];
  let line = '';
  for (const word of words) {
    const test = line ? `${line} ${word}` : word;
    if (line && measureText(ctx, test, sizePx) > maxWidth) {
      lines.push(line);
      line = word;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}
