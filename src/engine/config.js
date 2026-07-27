// All tunable numbers live here so game feel can be tuned without hunting through logic files.

export const CANVAS_WIDTH = 160;
export const CANVAS_HEIGHT = 90;

export const FRAME_W = 128;
export const FRAME_H = 80;
export const SHEET_COLS = 5;

// The character's logical anchor/pivot inside each 128x80 frame is at (34, 17) in the
// artist's coordinates: 34 from the LEFT edge (= 94 from the right), and 17 up from the
// BOTTOM edge — which is frame-y 63 from the top, sitting right at the character's feet
// (measured: every grounded frame bottoms out at row 63). player.x/y track this anchor's
// world position; drawing offsets by it (and mirrors X on flip) so the character stays put.
export const PLAYER_ANCHOR_X = 34;
export const PLAYER_ANCHOR_Y = FRAME_H - 17; // = 63, frame-y of the feet pivot

export const ANIM_FRAME_DURATION = 0.1; // 10fps, independent of render rate

export const WALK_SPEED = 84; // px/s (world units) — normal stroll
export const SPRINT_MULTIPLIER = 2.0; // hold Shift to sprint (~168 px/s), kicking up pixel dust
export const IDLE_TO_LONG_DELAY = 3.0; // seconds of no input before idle-long kicks in

export const GRAVITY = 560; // px/s^2 — heavy so the hop lands quickly
export const JUMP_VELOCITY = -140; // px/s, negative = up (keeps ~17px apex despite the heavy gravity)
// One extra mid-air hop, available in both scenes. Deliberately weaker than the first so the
// city's little jump stays a little jump; the runner swaps in its own, far stronger pair.
export const DOUBLE_JUMP_VELOCITY = -118; // adds ~12px on top of the first hop's ~17px

// Canvas-y of the ground surface / the player's feet-anchor rest line (79 so the character
// sits ON the floor, not 1px into it).
export const GROUND_Y = 79;
// Buildings and lamps sit 1px lower than the player's foot line so their bases don't float.
export const BUILDING_BASE_Y = GROUND_Y + 1;

// Player spawns to the LEFT of every building and cannot walk left past this point (a soft
// wall). At spawn the camera is clamped at 0, so the character sits mid-screen with the
// intro title in the empty space to its left.
export const PLAYER_SPAWN_X = 80;

// Building layout: first building's left edge, and the gap on each side of a lamp placed
// between adjacent buildings (building | 2px | lamp | 2px | building).
export const LAYOUT_START_X = 200;
export const BUILDING_GAP = 2;

export const PROXIMITY_RADIUS = 10; // px slack around a building where its prompt/interact is active

// CanvasModulate-style tint: everything behind the player and ground (parallax + buildings)
// is multiplied by this color to dim it, mirroring the Godot CanvasModulate in the source game.
export const MODULATE_COLOR = '#898989';

// On-canvas edge vignette: a thin dark band only at the screen edges (not a full-screen
// gradient), ~VIGNETTE_SIZE world px thick, near-black at the very edge fading quickly to clear.
export const VIGNETTE_SIZE = 10; // world px
export const VIGNETTE_ALPHA = 0.92;

// Near-building highlight: a subtle semi-transparent white box and solid white label.
export const HIGHLIGHT_COLOR = '#ffffff';
export const HIGHLIGHT_BOX_COLOR = 'rgba(255, 255, 255, 0.32)';
// The "enter" chevron above the player stays yellow.
export const ARROW_COLOR = '#ffe066';

// ---- Runner minigame (the endless run past the end of the street) ----------------------
// The cursed stones are drawn at their native art size (6x20 and 28x48). That matches this
// world's tiny-character/huge-props scale (buildings are 100px, lamps 33px, the character is
// 8px) but it means a 48px wall to clear, so the run needs its own physics: a much stronger
// jump, and heavier gravity so the big leap still feels snappy instead of floaty.
export const RUNNER_GRAVITY = 1150;
export const RUNNER_JUMP_VELOCITY = -256; // apex ~28px — clears the 20px stone on its own
export const RUNNER_DOUBLE_JUMP_VELOCITY = -296; // +38px, so a timed double clears the 48px one
export const RUNNER_PLAYER_X = 30; // fixed screen x — the character runs on the spot
export const RUNNER_START_SPEED = 100; // px/s the ground scrolls at
export const RUNNER_MAX_SPEED = 205;
export const RUNNER_ACCELERATION = 2.4; // px/s of scroll speed gained per second of running
export const RUNNER_VENUE_SECONDS = 22; // running time between blackout venue swaps
export const RUNNER_FADE_TIME = 0.4; // seconds for each half of a venue blackout
export const SCENE_FADE_TIME = 0.35; // seconds for each half of the city <-> runner fade
