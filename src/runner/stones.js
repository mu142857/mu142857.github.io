// The cursed stones — the runner's cacti.
//
// `Assets/cursed_stone-Sheet.png` is a 5x10 grid of 63x61 frames. Frame numbers here are
// 1-indexed, exactly the way they're counted in Aseprite (frame 28 = row 6, column 3).
//
// Each frame is mostly empty padding, so every type carries the crop rect of its art: the
// union of its frames' opaque bounds, measured straight off the PNG. Cropping keeps the
// stones bottom-aligned to the ground without guesswork, and lets the same rect double as
// the collision box.
export const STONE_SHEET_COLS = 5;
export const STONE_FRAME_W = 63;
export const STONE_FRAME_H = 61;

export const STONE_TYPES = {
  // Thin spike. Clearable with a single jump (apex ~30px vs. its 20px).
  small: {
    frames: [2, 3, 4],
    cropX: 31,
    cropY: 41,
    w: 6,
    h: 20,
    clearTime: 0.60, // airtime the jump it demands takes — used to space obstacles out
  },
  // Full-grown monolith, over half the screen tall. Needs the double jump, and there is no
  // way through it otherwise — the spacing rules below are what keep the run always solvable.
  large: {
    frames: [28, 29, 30],
    cropX: 20,
    cropY: 13,
    w: 28,
    h: 48,
    clearTime: 1.10, // a full double jump is a ~1.09s commitment
  },
};

export function stoneSource(type, frameNumber) {
  const idx = frameNumber - 1;
  const col = idx % STONE_SHEET_COLS;
  const row = Math.floor(idx / STONE_SHEET_COLS);
  return {
    sx: col * STONE_FRAME_W + type.cropX,
    sy: row * STONE_FRAME_H + type.cropY,
  };
}

const ALPHA_CUTOFF = 24; // anything fainter than this is anti-aliased edge, not stone

// The monolith is an obelisk, not a block: it tapers from 27px wide at its base to 10px at
// its tip, so a plain crop-rect hitbox has ~4px of empty air at each top corner — exactly
// where a jump that just clears it passes through. Measuring the art's per-row extent (the
// union over the type's frames, so the box never flickers with the animation) makes the
// collision follow the silhouette instead.
//
// Fills in `type.spans`: one { min, max } per row, top row first, or null for an empty row.
// Leaves it undefined if the pixels can't be read, and the collision falls back to the rect.
export function measureStoneSpans(sheet) {
  for (const type of Object.values(STONE_TYPES)) {
    const canvas = document.createElement('canvas');
    canvas.width = type.w;
    canvas.height = type.h;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const rows = Array.from({ length: type.h }, () => null);
    for (const frame of type.frames) {
      const { sx, sy } = stoneSource(type, frame);
      ctx.clearRect(0, 0, type.w, type.h);
      ctx.drawImage(sheet, sx, sy, type.w, type.h, 0, 0, type.w, type.h);
      let data;
      try {
        data = ctx.getImageData(0, 0, type.w, type.h).data;
      } catch {
        return; // tainted canvas — leave spans undefined
      }
      for (let y = 0; y < type.h; y++) {
        for (let x = 0; x < type.w; x++) {
          if (data[(y * type.w + x) * 4 + 3] <= ALPHA_CUTOFF) continue;
          const row = rows[y];
          if (!row) rows[y] = { min: x, max: x };
          else if (x < row.min) row.min = x;
          else if (x > row.max) row.max = x;
        }
      }
    }
    type.spans = rows;
  }
}
