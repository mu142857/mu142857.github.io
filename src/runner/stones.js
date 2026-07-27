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
  // Thin spike. Clearable with a single jump (apex ~28px vs. its 20px).
  small: {
    frames: [2, 3, 4],
    cropX: 31,
    cropY: 41,
    w: 6,
    h: 20,
    clearTime: 0.46, // airtime a single jump spends above it — used to space obstacles out
  },
  // Full-grown monolith, over half the screen tall. Needs the double jump, and there is no
  // way through it otherwise — the spacing rules below are what keep the run always solvable.
  large: {
    frames: [28, 29, 30],
    cropX: 20,
    cropY: 13,
    w: 28,
    h: 48,
    clearTime: 0.78,
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
