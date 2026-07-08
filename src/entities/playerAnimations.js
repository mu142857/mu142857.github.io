function range(start, end) {
  // inclusive of both ends, matching how the frame spec is written (e.g. "12-34")
  const frames = [];
  for (let n = start; n <= end; n++) frames.push(n);
  return frames;
}

export const ANIM = {
  IDLE_STAND: { frames: [9, 10, 11], loop: true },
  IDLE_LONG: { frames: range(12, 34), loop: false },
  CURLED: { frames: [35], loop: true },
  WAKING: { frames: range(36, 41), loop: false },
  WALK: { frames: range(43, 47), loop: true },
  JUMP: { frames: [57], loop: true },
  // Reserved for later — not wired into the state machine yet.
  DASH: { frames: range(2, 8), loop: false },
  ATTACK: { frames: range(48, 55), loop: false },
};
