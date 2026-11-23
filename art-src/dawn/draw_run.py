"""Art for the run (the minigame at the end of the pier): the things left on the walk that 晨
has to jump, drawn in the street's own style and in both lights.

One sheet, Assets/dawn/{state}/obstacles.png: every obstacle stands on the sheet's bottom row,
side by side. OBSTACLES lists each one's rectangle and how many jumps it takes; build.py copies
that list into scene.json ("run"), so the game never guesses at the art's size.

晨 is 50 px tall. One jump tops out about 50 px up, the second adds about 44, so "low" things
stay under 26 px and the one "tall" thing is 46 (it cannot be cleared with a single jump).
"""
import numpy as np

from kit import Pix, noise, sh, drop_single, long_runs
from pal import PAL

SHEET_H = 48
# name, width, height, jumps needed
SPECS = [("bollard", 14, 18, 1), ("crate", 20, 18, 1), ("barrel", 18, 25, 1), ("stack", 26, 46, 2)]
GAP = 4
OBSTACLES = []


def _crate(p, x0, y0, w, h, seed):
    xx, yy = p.xx, p.yy
    cr = p.R(x0, y0, x0 + w, y0 + h)
    p.put(cr, "wood", 3)
    p.put(cr & ((yy - y0) % 5 == 4), "wood", 2)                           # board edges
    fr = cr & ((xx < x0 + 2) | (xx >= x0 + w - 2) | (yy < y0 + 2) | (yy >= y0 + h - 2))
    p.put(fr, "wood", 4)
    p.put(p.L(x0 + 2, y0 + h - 3, x0 + w - 3, y0 + 2, 2) & cr, "wood", 4)   # the brace across it
    p.put(cr & (yy == y0), "wood", 6)
    p.put(cr & (xx >= x0 + w - 1), "wood", 6)                             # the edge toward the sun
    p.put(cr & (xx == x0), "wood", 2)
    p.put(cr & (yy == y0 + h - 1), "wood", 1)
    p.mottle(cr & ~fr, seed, t=0.6)
    return cr


def draw_obstacles():
    w_total = sum(s[1] for s in SPECS) + GAP * (len(SPECS) + 1)
    p = Pix(w_total, SHEET_H, PAL)
    xx, yy = p.xx, p.yy
    B = SHEET_H                                                           # the ground line (exclusive)
    x = GAP
    del OBSTACLES[:]
    for name, w, h, jumps in SPECS:
        t = B - h
        if name == "bollard":                                             # an iron mooring bollard
            stem = p.R(x + 3, t + 6, x + w - 3, B)
            p.put(stem, "iron", 2)
            p.put(p.R(x + w - 5, t + 6, x + w - 3, B), "iron", 4)
            p.put(p.R(x + 3, t + 6, x + 4, B), "iron", 1)
            head = p.E(x + w / 2, t + 4.5, w / 2, 4.5)
            p.put(head, "iron", 2)
            p.put(head & (yy <= t + 2), "iron", 3)
            p.put(head & (xx >= x + w - 4) & (yy <= t + 5), "iron", 4)
            p.put(head & (yy >= t + 7), "iron", 1)
            foot = p.R(x + 1, B - 3, x + w - 1, B)
            p.put(foot, "iron", 1)
            p.put(foot & (yy == B - 3), "iron", 3)
            p.put(p.R(x + w - 3, B - 3, x + w - 1, B), "iron", 3)
            rope = p.R(x + 2, t + 9, x + w - 2, t + 12)                    # a turn of rope round its neck
            p.put(rope, "cream", 1)
            p.put(rope & (yy == t + 9), "cream", 2)
            p.put(rope & (yy == t + 11), "cream", 0)
        elif name == "crate":
            _crate(p, x, t, w, h, 301)
        elif name == "barrel":
            bulge = np.round(2.2 * np.sin(np.clip((yy - t) / (h - 1), 0, 1) * np.pi)).astype(int)
            body = (yy >= t) & (yy < B) & (xx >= x + 2 - bulge) & (xx < x + w - 2 + bulge)
            p.put(body, "wood", 3)
            for sx in (x + 5, x + 9, x + 13):                             # stave joints, full height
                p.add(body & (xx == sx), -1)
            p.put(body & (xx >= x + w - 4 + bulge), "wood", 5)
            p.put(body & (xx >= x + w - 3 + bulge), "wood", 6)
            p.put(body & (xx < x + 3 - bulge), "wood", 2)
            p.mottle(body, 302, t=0.62)
            for hy in (t + 4, t + h - 7):                                 # two hoops, unbroken
                hoop = body & (yy >= hy) & (yy < hy + 3)
                p.put(hoop, "iron", 2)
                p.put(hoop & (yy == hy), "iron", 4)
                p.put(hoop & (xx >= x + w - 4 + bulge), "iron", 4)
            lid = body & (yy <= t + 1)
            p.put(lid, "wood", 5)
            p.put(lid & (yy == t), "wood", 6)
            p.put(body & (yy == B - 1), "wood", 1)
        elif name == "stack":                                             # two crates, the top one set back
            _crate(p, x, B - 24, w, 24, 303)
            top = _crate(p, x + 5, t, 19, 22, 304)
            p.add(p.R(x, B - 24, x + w, B - 22) & ~top & (xx < x + 5), 0)
            p.add(p.R(x + 5, B - 24, x + 24, B - 23), -1)                 # the top crate's shade on the lower one
        OBSTACLES.append({"name": name, "x": x, "w": w, "h": h, "jumps": jumps})
        x += w + GAP
    return p
