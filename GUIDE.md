# Jiamu Shangguan — Site Guide

Two views of the same portfolio, switchable by a button:

1. **Interactive** (`index.html`) — a pixel side-scroller. Walk right past buildings; each building
   opens a portfolio section. Keep walking past the last one and an **ENTER GAME** arrow drops you
   into an endless runner. This is the main site.
2. **Classic** (`classic.html` + `classic.css`) — a normal scrolling one-pager: sticky nav,
   text-only hero, then About / Skills / Experience / Games / Projects / Music / Contact.
   Same palette as the interactive site; typography follows the old HTML5 UP "Twenty" template
   (Lato, light weights, uppercase headings with wide letter-spacing). **No rounded corners
   anywhere** — `classic.css` enforces `border-radius: 0 !important` on every element.

---

## 1. Run / preview it

You can't just double-click `index.html` (ES modules are blocked on `file://`). Serve it:

```bash
cd "/Users/jiamulin/Desktop/程序programs/Web/Personal Website/mu142857.github.io"
python3 -m http.server 5500
```

Open **http://localhost:5500** . Classic view: **http://localhost:5500/classic.html** .
Stop with `Ctrl+C`.

> ⚠️ **After editing code, the browser often caches the old version.** Hard-refresh with
> **`Cmd + Shift + R`** to see changes. (This plain server doesn't send no-cache headers.)

---

## 2. Keeping the content up to date

**Content lives in two places and must be edited in both:**

| | Interactive site | Classic site |
|---|---|---|
| File | `index.html`, inside the `<template id="section-…">` blocks | `classic.html`, inside `<section id="…">` |
| Game cards | `section-gameProjects` | `#games` |
| Other projects | `section-projects` | `#projects` |

Card markup is nearly identical between them — the interactive one puts `class="card-thumb"` on
the `<img>`; the classic one doesn't need a class. When you add a project, add it to both.

### A. Images — done

All images live in **`Assets/content/`**, lowercase-with-hyphens (`phage.png`,
`until-someone-passes.png`, `eight-for-long.png`, `signal-split.png`, `look.png`,
`physics-sim.png`, `sentiment-flow.png`, `open-pg.png`, `donatrust.png`,
`about-portrait.jpg`, `experience-drone.jpg`, `music-studio.jpg`, `favicon.png`).

- **Screenshots are portrait by design** (the games are all vertical-composition). Cards crop
  them to a wide thumbnail with `object-fit: cover` — that is intentional, leave it.
- New image → drop it in `Assets/content/` and point the card's `src` at it. No other wiring.
- The About portrait is used by the interactive site only; the classic hero is text-only
  (name → role → rule → blurb → social icons) and deliberately shows no photo.

### B. Project links to fill

Some project cards link to `href="#"` (do nothing). Replace `#` in **both** `index.html` and
`classic.html`:

| Section | Card | Current link | Fill in |
|---|---|---|---|
| `section-projects` | Physics Simulation | `#` | project / devpost / repo URL |
| `section-projects` | Sentiment Flow | `#` | devpost or GitHub URL |
| `section-projects` | Loo-k | `#` | live site or repo URL |
| `section-projects` | Open Prince George | `#` | repo or site URL |
| `section-projects` | DonaTrust Portal | `#` | prototype or repo URL |

Already wired (no action needed): Phage → bilibili, Until Someone Passes / Signal Split →
their itch.io pages, Eight For Long → `maggieeeeem.itch.io/eight-for-long`, Music → R&S Studio,
and the social icons (email, GitHub, LinkedIn, itch.io, bilibili).

### C. Game card order

Games are listed **most-important-first** and the order is currently:

1. **Until Someone Passes** — GMTK 2026, narrative/art game, team lead (design + all code).
   Jam results (~10,500 entries, 37,000+ jammers): Audio **#53**, Narrative **#126**, Artwork **#140**
2. **Phage** — the long-running main project
3. **Eight For Long** — GMTK 2026, puzzle/strategy, team lead (design + all code).
   Jam results: Narrative **#476**, Artwork **#1,849**, Audio **#3,354**
4. **Signal Split** — UW Game Jam

Both 2026 GMTK entries were made in the same jam with a three-person team each; on both you were
team lead — you assembled and coordinated the team, did the design, and wrote all the code.
Keep the two lists (`index.html` and `classic.html`) in the same order.

### D. bilibili follower count (manual)

Auto-fetch from the browser is **not possible** (bilibili blocks cross-origin requests + returns 403
to public proxies). Update it by hand in **both** files (`section-gameProjects` / `#games`):

```html
<span>6,600 / 10,000</span>              <!-- update the number -->
<div class="progress-fill" style="width: 66%"></div>   <!-- update % = followers / 100 -->
```

> If you deploy to GitHub Pages and want true auto-update, ask me to set up a scheduled GitHub
> Action that fetches the count server-side and writes it to a JSON the page reads. (It *might*
> still be 403'd on the runner's IP — worth a try.)

### E. Optional / later

- **Text content**: section copy lives in the `<template>` blocks in `index.html` and the
  `<section>`s in `classic.html`. Edit freely.
- **`Home/`** is the leftover HTML5 UP "Twenty" template plus a "coming soon" placeholder page.
  Nothing links to it any more except Font Awesome (`Home/assets/css/fontawesome-all.min.css`,
  loaded by both sites) — if you delete the folder, move the Font Awesome CSS + `webfonts/`
  out first.
- **Forest-town theme**: a second world skin is scaffolded but has no art yet (see `themes.js`
  `forestTown: null`). Drop in art + a theme-toggle button when ready.

---

## 3. Project structure

```
index.html      Interactive site: canvas, HUD (social + Classic/skin/Settings buttons), section
                <template>s, the first-visit world picker, and the Settings modal template.
style.css       Interactive-site styling (canvas, HUD, overlay cards, chips, progress bar, vignette).
classic.html    Classic site: one scrolling page, same content as the templates in index.html.
classic.css     Classic-site styling (Lato typography, cards, chips; border-radius: 0 everywhere).
GUIDE.md        This file.
Assets/
  player/player-Sheet.png          Character sprite sheet (5×12 grid, 128×80/frame).
  cursed_stone-Sheet.png           Runner obstacles (5×10 grid, 63×61/frame).
  rust_city_style/                 Parallax layers, ground, building1–6.png, lamp, PixelFont note.
  silvaron_style/                  The second skin (same layout).
  shared/PixelFont.ttf             The pixel font (used on canvas + in overlays).
  content/                         All site photos + screenshots (see §2A).
src/
  main.js                          Boot + game loop + scene switching + HUD/text/vignette/dust.
  i18n.js                          The bilingual dictionary (see "Language" below) — every 中文
                                   string on both sites lives here.
  engine/     config.js (all tunable numbers), loop, input, assets, spritesheet, particles,
              music.js (per-skin looping tracks, crossfaded on theme changes).
  entities/   player.js (state machine + sprint + double jump), playerAnimations.js.
  world/      world.js (layout/draw/proximity/gate), camera, parallax, buildings.js, themes.js.
  runner/     runner.js (the minigame scene), stones.js (obstacle sheet spec).
  ui/         overlay.js (section modal), pixelText.js (canvas text),
              touchControls.js (on-screen gamepad for phones).
Home/         Leftover HTML5-UP "Twenty" template. Only still needed for the Font Awesome CSS
              + webfonts that both sites link to (see §2E).
```

### The classic site (`classic.html` / `classic.css`)

Plain HTML, no build step; the only JS is a small inline module at the bottom that drives the
Settings modal and the language pass (it imports `src/i18n.js`). Anchor nav (`#about`, `#skills`, …) with `scroll-behavior: smooth`; the top bar
is `position: sticky`. Two rules matter when editing:

- **`border-radius: 0 !important`** is set on `*` — the whole design is square on purpose.
- **No pixel font.** PixelFont belongs to the game; the classic site is Lato throughout so it
  reads as a normal professional page. Headings are uppercase with wide letter-spacing, and
  buttons (`.cta`, `.game-link`) are outlined rather than filled, inverting on hover.

Breakpoints: 880px (two-column grids collapse to one) and 640px (nav wraps to its own row).

### Building order & sections

`src/world/buildings.js` lists the buildings left-to-right from spawn. Current order (most
important first): **Game Projects → Projects → Music → About → Technical Skills → Work Experience**.
Reorder that array to rearrange them. The building *art* (`themes.js` `buildings` list) is
index-aligned, so reordering `buildings.js` alone just changes which section sits behind each
building — no art changes needed.

### Handy tunables (`src/engine/config.js`)

- `WALK_SPEED` (84), `SPRINT_MULTIPLIER` (2.0 — hold Shift), `JUMP_VELOCITY`, `GRAVITY`,
  `DOUBLE_JUMP_VELOCITY`.
- Runner: `RUNNER_START_SPEED`/`RUNNER_MAX_SPEED`/`RUNNER_ACCELERATION` (how fast it ramps),
  `RUNNER_JUMP_VELOCITY`/`RUNNER_DOUBLE_JUMP_VELOCITY`/`RUNNER_GRAVITY` (jump feel — if you
  change these, check they still clear a 48px stone), `RUNNER_VENUE_SECONDS` (blackout interval).
- `GROUND_Y` (79, feet line), `BUILDING_BASE_Y` (80, building bases).
- `PLAYER_SPAWN_X`, `LAYOUT_START_X`, `BUILDING_GAP` (spacing), `PROXIMITY_RADIUS`.
- `MODULATE_COLOR` (background dimming), `VIGNETTE_SIZE`/`VIGNETTE_ALPHA`, `ARROW_COLOR`,
  `HIGHLIGHT_COLOR`/`HIGHLIGHT_BOX_COLOR`.
- Text sizes are in `main.js`: `TITLE_H`, `BODY_H`, `LABEL_H` (world px × render scale).

### Controls

**Desktop** — Walk **A/D** or arrows · Sprint **hold Shift** (kicks up pixel dust) ·
Jump **Space**, press it again in mid-air for a **double jump** · Enter a building or the game
gate **↑ / Enter / click**.

**Phone / tablet** — an on-screen gamepad appears: **◀ ▶** bottom-left to walk, **≫** (sprint)
and **^** (jump) bottom-right, plus an **ENTER** button that pops up only when the character is
standing next to a building (or at the game gate). Tapping the building itself works too.
Multi-touch is supported, so you can hold *right* + *sprint* and still tap *jump*.

### The runner minigame (`src/runner/`)

Walk past the last building and a bobbing **ENTER GAME** arrow appears; Enter (or a tap) fades
to black and drops you into an endless runner. Enter again returns you to the exact spot in the
city you left from.

- **The character runs on the spot** at `RUNNER_PLAYER_X` and the world scrolls past, reusing
  the city's parallax layers — so the run gets a proper parallax backdrop for free.
- **Obstacles** are the two cursed stones in `Assets/cursed_stone-Sheet.png`: a 6×20 spike
  (frames 2–4) and a 28×48 monolith (frames 28–30), both at native size, both looping at 10fps.
  `stones.js` carries each type's measured crop rect.
- **Hitboxes follow the art, not the crop rect.** The monolith is an obelisk — 27px wide at
  the base, 10px at the tip — so a rectangular box would have ~4px of solid air at each top
  corner, right where a jump that just clears it passes. `measureStoneSpans` reads the sprite's
  opaque extent row by row at load time and the collision tests those rows. The character's box
  shrinks too: its JUMP pose tucks its legs up into the top 4px of its 8px frame, so while it is
  airborne only that tucked body counts (`PLAYER_TUCKED_BOTTOM` in `config.js`).
- **The monolith needs the double jump** — it is taller than half the screen. The runner swaps
  in its own physics (`RUNNER_*` in `config.js`): a ~30px first hop and a ~40px second one, under
  *lighter* gravity than the city's. That last part is the difficulty dial — under heavy gravity
  a tall jump means a brutally fast drop and almost no time to place the mid-air hop.
- **It is always solvable.** Every stone is placed at least `clearTime + reaction` seconds of
  travel behind the previous one, at the *current* scroll speed plus headroom, so there is always
  room to land, see the next one, and jump it. No monolith appears in the first 320px.
- **Blackout venue swaps** — every `RUNNER_VENUE_SECONDS` the whole screen fades to black and a
  completely different place fades in (Rust City ↔ Silvaron). Spawning stops the moment a swap is
  queued and the swap waits for the stones already on screen to scroll away, so the blackout can
  never hide an obstacle; a further grace period keeps the road clear after the lights come back.
- **Crashing** ends the run with your score and best (kept in `localStorage` under `runner-best`).
  Space retries, Enter goes back to the city.
- On a phone the gamepad switches to runner mode: the walk pad and sprint step aside and **^**
  becomes one big jump button, next to a **BACK** button.
- The **skin** ("Forest Style" / "City Style") and **Classic Site** buttons hide during a run
  (`body.in-runner` in `style.css`) — mid-run they are one stray click away from reskinning the
  world under you or leaving the page. The social icons and the **Settings** button stay (it
  holds the music toggle, and opening it pauses the run). The class is added and removed at
  full black, so they never blink in or out on screen.
- **Theme music** (`src/engine/music.js`, tracks in `Assets/music/`): one looping track per skin
  — `glitch.mp3` for Rust City ("City"), `Silvaron.m4a` for Silvaron ("Forest"). The music
  follows the active theme with a crossfade: the skin toggle, the runner's venue swap
  (`runner.onVenueChange`), and stepping back out into the city all retarget it. Playback can
  only start after the first click/keypress (browser autoplay policy); the on/off state is kept
  in `localStorage` under `music-on`, default on.

**Tuning the difficulty.** Making the run easier or harder is mostly two numbers:
`RUNNER_GRAVITY` (lower = more hang time = more room to place the double jump) and
`RUNNER_MAX_SPEED` (a stone is only visible for `CANVAS_WIDTH - RUNNER_PLAYER_X` = 130px
before it arrives, so top speed is really a cap on reaction time). If you change the jump
velocities, keep `v² / (2 × RUNNER_GRAVITY)` at ≥22px for the first hop and ≥52px for the two
combined, or the monolith stops being clearable. Obstacle spacing follows automatically from
each type's `clearTime` in `stones.js`, which should equal the airtime of the jump it demands.

### Settings & saved data

Both sites have a **Settings** button (HUD top-right on the interactive site, top bar on the
classic one) opening a modal in that site's own style — pixel overlay vs. Lato/outlined. Three
controls, in both: **Music** on/off, **Language** (English/中文, switches the whole site
live), and **Clear saved data** (two clicks: `Clear` → `Confirm?`), which wipes
`localStorage` and reloads.

**Language (`src/i18n.js`).** English is the source of truth and lives in the HTML/JS;
`i18n.js` holds only the Chinese, in two dictionaries: `ZH` (per `data-i18n` element key —
both HTML files tag every translatable element) and `UI` (strings built in JS: canvas text,
building labels, runner HUD, button labels — read via `t(key)`). Translation rules: proper
nouns are not force-translated — companies, products (Godot, AUAV…), and English-born project
names stay English; games use their official Chinese titles (直到经过, 8分钟, 信号分裂;
Phage stays Phage); the name is 上官嘉木. To edit copy: change the English in the HTML *and*
the matching key in `ZH`. New content needs a `data-i18n="key"` attribute + a `ZH` entry —
missing keys just stay English rather than breaking. Canvas CJK glyphs render through a
sans-serif fallback (PixelFont is Latin-only; see `FONT_STACK` in `pixelText.js`).

Everything the site remembers lives in `localStorage` under four keys, shared by both views:

| Key | Meaning | Written by |
|---|---|---|
| `skin-theme` | chosen world (`rustCity` / `silvaron`) | world picker, skin toggle |
| `music-on` | music on/off (`1` / `0`, default on) | Settings |
| `site-lang` | UI language (`en` / `zh`, default `en`) | Settings |
| `runner-best` | runner best score | the runner |

**First-visit world picker** (`#theme-picker` in `index.html`, logic in `main.js`
`pickTheme()`): when the interactive site loads with no `skin-theme` saved — a true first
visit, or right after Clear saved data — a full-screen chooser shows three square covers from
`Assets/theme/`: **Forest** (Silvaron), **City** (Rust City), and **???** (Crimson Sanctum).
The third is sealed — clicking it flashes a red pixel-font **ACCESS DENIED** — until that
world actually exists. Picking one records it and boots straight into that skin; the classic
site never asks (it has no skins), so someone who lands on classic first only meets the picker
when they switch over.

### Mobile / responsive layout

The side-scroller only makes sense wide, so the site always plays in landscape:

- **Phone held upright** → CSS rotates the whole app a quarter turn (`body.rotated` in
  `style.css`), so it fills the screen sideways *even if the phone's rotation lock is on*.
  Turn the phone counter-clockwise and it reads normally. A "turn your phone" hint fades out
  after 5s.
- Everything visible lives inside `#app`, which `layout()` in `src/main.js` sizes in pixels;
  the rotation makes `#app` the containing block for the HUD, gamepad, and section overlay, so
  they all turn together.
- Body classes replace media queries — a rotated app's CSS viewport reports the *wrong* axis,
  so `layout()` sets `.touch`, `.rotated`, `.compact` (shrinks the HUD and the overlay text)
  and `.narrow` from the app's own dimensions instead.
- The canvas backing store stays an integer multiple of 160×90 (crisp pixels); on touch
  devices its *displayed* size takes the fractional fit so it fills the small screen.

Test it by resizing a desktop browser window to phone size — anything with a short side of
520px or less switches into touch mode.

---

## 4. Deploy (GitHub Pages)

Push this whole folder to a repo (e.g. as the source of `mu142857.github.io`, or a project repo
with Pages enabled). `index.html` at the root is the interactive site; `classic.html` is the
classic one. No build step — it's plain HTML/CSS/JS.

---

## 5. Contact / links reference (already wired)

- Email: linjiamu49@gmail.com · GitHub: github.com/mu142857 ·
  LinkedIn: linkedin.com/in/jiamu-shangguan-464092399 · itch.io: safari-mu.itch.io
- Music (R&S Studio): https://r-s-studio.github.io/ · bilibili: https://space.bilibili.com/1876827674
