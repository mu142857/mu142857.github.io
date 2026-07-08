# Jiamu Shangguan — Site Guide

Two views of the same portfolio, switchable by a button:

1. **Interactive** (`index.html`) — a pixel side-scroller. Walk right past buildings; each building
   opens a portfolio section. This is the main site.
2. **Classic** (`Home/index.html`) — a normal responsive template ("Twenty" by HTML5 UP).

---

## 1. Run / preview it

You can't just double-click `index.html` (ES modules are blocked on `file://`). Serve it:

```bash
cd "/Users/jiamulin/Desktop/程序programs/Web/Jiamu Website"
python3 -m http.server 5500
```

Open **http://localhost:5500** . Classic view: **http://localhost:5500/Home/** . Stop with `Ctrl+C`.

> ⚠️ **After editing code, the browser often caches the old version.** Hard-refresh with
> **`Cmd + Shift + R`** to see changes. (This plain server doesn't send no-cache headers.)

---

## 2. ✅ WHAT YOU STILL NEED TO ADD

### A. Images

All images are currently dashed **placeholder boxes** (labelled with what goes there).

1. Put image files in a new folder **`Assets/content/`**.
2. Name them **lowercase-with-hyphens**, matching the list below (e.g. `phage.png`).
   - Screenshots: PNG. Photos: JPG. Keep them small (they display small) — ~600px wide is plenty.
3. In `index.html`, find the placeholder and **replace the whole `<div ...>…</div>` with an `<img>`**.
   The image automatically inherits the framed styling.

| Section (`<template>` in `index.html`) | Placeholder label | Suggested filename | Replace with |
|---|---|---|---|
| `section-gameProjects` | Phage screenshot | `phage.png` | `<img class="card-thumb" src="Assets/content/phage.png" alt="Phage">` |
| `section-gameProjects` | Signal Split screenshot | `signal-split.png` | `<img class="card-thumb" src="Assets/content/signal-split.png" alt="Signal Split">` |
| `section-projects` | Physics sim screenshot | `physics-sim.png` | `<img class="card-thumb" src="Assets/content/physics-sim.png" alt="Physics Simulation">` |
| `section-projects` | Sentiment Flow screenshot | `sentiment-flow.png` | `<img class="card-thumb" src="Assets/content/sentiment-flow.png" alt="Sentiment Flow">` |
| `section-projects` | Loo-k screenshot | `look.png` | `<img class="card-thumb" src="Assets/content/look.png" alt="Loo-k">` |
| `section-projects` | Open Prince George screenshot | `open-pg.png` | `<img class="card-thumb" src="Assets/content/open-pg.png" alt="Open Prince George">` |
| `section-projects` | DonaTrust screenshot | `donatrust.png` | `<img class="card-thumb" src="Assets/content/donatrust.png" alt="DonaTrust">` |
| `section-about` | Portrait / avatar | `about-portrait.jpg` | `<img class="portrait" src="Assets/content/about-portrait.jpg" alt="Jiamu Shangguan">` |
| `section-experience` | Drone show photo | `experience-drone.jpg` | `<img src="Assets/content/experience-drone.jpg" alt="AUAV drone show">` |
| `section-music` | Studio / piano photo | `music-studio.jpg` | `<img src="Assets/content/music-studio.jpg" alt="R&S Studio">` |

- Inside a **project card**, keep `class="card-thumb"` on the `<img>`.
- For the **About portrait**, keep `class="portrait"` so it stays small.
- Other section images (drone, studio) need no class — they fill the width.

### B. Project links to fill

Some project cards link to `href="#"` (do nothing). Replace `#` with the real URL in `index.html`:

| Section | Card | Current link | Fill in |
|---|---|---|---|
| `section-projects` | Physics Simulation | `#` | project / devpost / repo URL |
| `section-projects` | Sentiment Flow | `#` | devpost or GitHub URL |
| `section-projects` | Loo-k | `#` | live site or repo URL |
| `section-projects` | Open Prince George | `#` | repo or site URL |
| `section-projects` | DonaTrust Portal | `#` | prototype or repo URL |

Already wired (no action needed): Phage → bilibili, Signal Split → itch.io, Music → R&S Studio,
and the top-right social icons (email, GitHub, LinkedIn, itch.io).

### C. bilibili follower count (manual)

Auto-fetch from the browser is **not possible** (bilibili blocks cross-origin requests + returns 403
to public proxies). Update it by hand in `index.html`, `section-gameProjects`:

```html
<span>5,912 / 10,000</span>              <!-- update the number -->
<div class="progress-fill" style="width: 59%"></div>   <!-- update % = followers / 100 -->
```

> If you deploy to GitHub Pages and want true auto-update, ask me to set up a scheduled GitHub
> Action that fetches the count server-side and writes it to a JSON the page reads. (It *might*
> still be 403'd on the runner's IP — worth a try.)

### D. Optional / later

- **Text content**: all section copy lives in the `<template>` blocks in `index.html`. Edit freely.
- **Forest-town theme**: a second world skin is scaffolded but has no art yet (see `themes.js`
  `forestTown: null`). Drop in art + a theme-toggle button when ready.

---

## 3. Project structure

```
index.html      Interactive site: canvas, HUD (social + Classic Site button), section <template>s.
style.css       All styling (game canvas, HUD, overlay cards, chips, progress bar, vignette).
GUIDE.md        This file.
Assets/
  player/player-Sheet.png          Character sprite sheet (5×12 grid, 128×80/frame).
  rust_city_style/                 Parallax layers, ground, building1–6.png, lamp, PixelFont note.
  shared/PixelFont.ttf             The pixel font (used on canvas + in overlays).
  content/                         ← PUT YOUR IMAGES HERE (create this folder).
src/
  main.js                          Boot + game loop + HUD/text/vignette/dust orchestration.
  engine/     config.js (all tunable numbers), loop, input, assets, spritesheet, particles.
  entities/   player.js (state machine + sprint), playerAnimations.js (frame ranges).
  world/      world.js (layout/draw/proximity), camera, parallax, buildings.js, themes.js.
  ui/         overlay.js (section modal), pixelText.js (canvas text).
Home/         The "classic" HTML5-UP template (self-contained; has its own assets + Font Awesome).
```

### Building order & sections

`src/world/buildings.js` lists the buildings left-to-right from spawn. Current order (most
important first): **Game Projects → Projects → Music → About → Technical Skills → Work Experience**.
Reorder that array to rearrange them. The building *art* (`themes.js` `buildings` list) is
index-aligned, so reordering `buildings.js` alone just changes which section sits behind each
building — no art changes needed.

### Handy tunables (`src/engine/config.js`)

- `WALK_SPEED` (84), `SPRINT_MULTIPLIER` (2.0 — hold Shift), `JUMP_VELOCITY`, `GRAVITY`.
- `GROUND_Y` (79, feet line), `BUILDING_BASE_Y` (80, building bases).
- `PLAYER_SPAWN_X`, `LAYOUT_START_X`, `BUILDING_GAP` (spacing), `PROXIMITY_RADIUS`.
- `MODULATE_COLOR` (background dimming), `VIGNETTE_SIZE`/`VIGNETTE_ALPHA`, `ARROW_COLOR`,
  `HIGHLIGHT_COLOR`/`HIGHLIGHT_BOX_COLOR`.
- Text sizes are in `main.js`: `TITLE_H`, `BODY_H`, `LABEL_H` (world px × render scale).

### Controls

Walk **A/D** or arrows · Sprint **hold Shift** (kicks up pixel dust) · Jump **Space** ·
Enter a building **↑ / Enter / click the box**.

---

## 4. Deploy (GitHub Pages)

Push this whole folder to a repo (e.g. as the source of `mu142857.github.io`, or a project repo
with Pages enabled). `index.html` at the root is the interactive site; `Home/` is the classic one.
No build step — it's plain HTML/CSS/JS.

---

## 5. Contact / links reference (already wired)

- Email: linjiamu49@gmail.com · GitHub: github.com/mu142857 ·
  LinkedIn: linkedin.com/in/jiamu-shangguan-464092399 · itch.io: safari-mu.itch.io
- Music (R&S Studio): https://r-s-studio.github.io/ · bilibili: https://space.bilibili.com/1876827674
