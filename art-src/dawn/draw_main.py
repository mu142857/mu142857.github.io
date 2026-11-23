"""The layer the player walks on: the lakeside walk (road, curb, paving, parapet), the things
standing on it near the start (bench, street lamp), and building 1 -- the arcade (Game Projects).

Plan (flat side view, 1 px = 1 px, character about 46 px tall, feet on y = 232):
  y 250-270  road                      y 239-249  curb face
  y 232-238  paving (top row = the lit edge the feet stand on)
  y 209-231  parapet between the walk and the lake, pillars with ball finials
  arcade     230 x 176 sprite at world (360, 60): two floors + roof, ground line = local y 172
             storey height ~62 px, door 30 x 60, shop window 88 x 46
"""
import numpy as np

from draw_bg import crown, lamp_post, trunk
from kit import Pix, noise, sh, dilate, drop_single, long_runs
from pal import PAL

LEN, H = 2880, 270
G = 232
ARC_X, ARC_Y = 360, 60
PIER_X = 2622          # the stone walk ends here; b_pier.py draws everything to the right of it
SPRITES = []          # (name, world x, world y, Pix)
STOPS = []


# ====================================================================== the walk
def bench(p, x):
    slats = p.Z()
    for fx in (x + 4, x + 41):
        fr = p.R(fx, G - 16, fx + 3, G) | p.P([(fx - 2, G - 31), (fx + 1, G - 31), (fx + 3, G - 15), (fx, G - 15)])
        p.put(fr, "iron", 1)
        p.put(fr & ~sh(fr, -1, 0), "iron", 3)
        p.put(p.R(fx - 2, G - 2, fx + 5, G), "iron", 1)
        p.put(p.R(fx - 3, G - 22, fx + 6, G - 20), "iron", 2)
        p.put(p.R(fx - 3, G - 22, fx + 6, G - 21), "iron", 4)
    for y0, y1, lv in ((G - 30, G - 27, 4), (G - 25, G - 22, 3), (G - 17, G - 14, 4)):
        m = p.R(x, y0, x + 48, y1)
        p.put(m, "wood", lv)
        p.put(m & (p.yy == y0), "wood", lv + 2)
        p.put(m & (p.yy == y1 - 1), "wood", lv - 1)
        p.put(m & (p.xx >= x + 46), "wood", lv + 2)
        slats |= m
    p.put(p.R(x, G - 14, x + 48, G - 12), "wood", 1)                   # front edge of the seat, in its own shade
    p.mottle(slats, 66, t=0.6)
    p.add(p.R(x + 1, G, x + 46, G + 2), -1)                            # shade under it
    p.cast(slats | p.R(x + 4, G - 16, x + 44, G), (p.yy >= G) & (p.yy < G + 7), 26, slope=0.12)


def draw_ground(lights, pools=(), length=LEN, street=True):
    """The walk. `street=False` draws a bare 960-px tile of it for the run (no bench, lamp,
    light pools or pier cut; pillars at fixed places so the tile repeats)."""
    LEN = length
    p = Pix(LEN, H, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(61)
    # ---- road
    road = yy >= 250
    p.put(road, "stone", 1)
    p.put(road & (yy < 252), "stone", 2)
    p.mottle(road, 62, t=0.5)
    # ---- curb: long stones, a joint here and there
    curb = (yy >= 239) & (yy < 250)
    p.put(curb, "stone", 4)
    p.put(curb & (yy >= 245), "stone", 3)
    p.put(curb & ((yy == 239) | (yy >= 248)), "stone", 2)
    p.mottle(curb & (yy > 239) & (yy < 248), 63, t=0.5)
    x = 0
    while x < LEN:
        x += int(r.integers(34, 72))
        p.add(p.R(x, 240 + int(r.integers(0, 2)), x + 1, 248 - int(r.integers(0, 3))), -1)
    # ---- paving
    pave = (yy >= G) & (yy < 239)
    p.put(pave, "pave", 3)
    p.put(pave & (yy < 236), "pave", 4)
    p.put(pave & (yy == G), "pave", 5)
    p.add(long_runs(pave & (yy == G) & (noise(H, LEN, 14, 1, 67, 1) < -0.35), 3), -1)      # the lit edge is worn away in places
    p.mottle(pave & (yy > G), 64, t=0.48)
    x = 0
    while x < LEN:
        x += int(r.integers(18, 46))
        p.add(p.L(x, G + 1, x - 2, 238) & pave, -1)
    # ---- parapet between the walk and the lake
    wall = (yy >= 213) & (yy < G)
    p.put(wall, "stone", 3)
    p.put(wall & (yy >= 229), "stone", 2)
    cope = (yy >= 209) & (yy < 213)
    p.put(cope, "stone", 5)
    p.put(cope & (yy == 209), "stone", 6)
    p.put(cope & (yy == 212), "stone", 3)
    p.put(wall & (yy == 213), "stone", 1)
    for y0, y1 in ((214, 222), (222, 229)):
        x = int(r.integers(0, 20))
        while x < LEN:
            w = int(r.integers(14, 38))
            if r.random() < 0.24:
                p.add(p.R(x + 1, y0, x + w, y1), int(r.choice([-1, 1])))
            p.add(p.R(x, y0 + int(r.random() < 0.3), x + 1, y1 - int(r.random() < 0.4)), -1)
            x += w
    p.add(long_runs(wall & (yy == 222) & (noise(H, LEN, 22, 1, 68, 1) > -0.25), 6), -1)
    p.mottle(wall & (yy > 213), 65, t=0.52)
    nm = noise(H, LEN, 16, 3, 69, 2)
    p.put(cope & (yy < 211) & (nm > 0.42), "moss", 3)
    p.put(drop_single(wall & (yy >= 225) & (nm > 0.36)), "moss", 1)
    p.put(drop_single(wall & (yy >= 228) & (nm > 0.22)), "moss", 2)
    for _ in range(90 * LEN // 2880):                                     # water stains under the coping
        x, ln = int(r.integers(0, LEN - 2)), int(r.integers(3, 11))
        p.add(p.R(x, 213, x + 2, 213 + ln), -1)
    fixed = iter((70, 300, 512, 770, 10 ** 6))
    x = 96 if street else next(fixed)
    while x < (PIER_X - 90 if street else LEN):
        pil = p.R(x, 201, x + 12, G)
        p.put(pil, "stone", 4)
        p.put(p.R(x, 201, x + 2, G), "stone", 3)
        p.put(p.R(x + 9, 201, x + 12, G), "stone", 6)
        p.put(p.R(x - 1, 227, x + 13, G), "stone", 3)
        p.put(p.R(x + 10, 227, x + 13, G), "stone", 5)
        cap = p.R(x - 2, 197, x + 14, 201)
        p.put(cap, "stone", 5)
        p.put(cap & (yy == 197), "stone", 7)
        p.put(cap & (yy == 200), "stone", 3)
        ball = p.E(x + 6, 193, 4.2, 4.2)
        p.put(ball, "stone", 4)
        p.put(ball & (xx >= x + 7) & (yy <= 194), "stone", 6)
        p.put(ball & (xx <= x + 3), "stone", 3)
        p.put(ball & (yy >= 196), "stone", 3)
        p.mottle(pil, 70 + x, t=0.55)
        p.cast(pil | cap, wall | cope, 7, slope=0.3)
        x = x + int(r.integers(170, 262)) if street else next(fixed)
    if not street:
        return p
    # ---- things on the walk near the start
    bench(p, 196)
    lamp_post(p, 318, G, 136, "main")
    # ---- window light lying on the paving in front of the arcade (dawn only)
    for cx, hw in ((ARC_X + 68, 44), (ARC_X + 145, 15), (ARC_X + 183, 11)) + tuple(pools):
        half = hw + (yy - G) * 2.2
        pool = (yy >= G) & (yy < 250) & (np.abs(xx - cx) < half)
        p.remat(pool & pave, "pavewarm", 0, "dawn")
        p.remat(pool & pave & (np.abs(xx - cx) < half * 0.6), "pavewarm", 1, "dawn")
        p.add(pool & curb & (np.abs(xx - cx) < half * 0.7), 1, "dawn")
    p.clear(xx >= PIER_X)
    return p


# ====================================================================== building 1: the arcade
def window(p, x0, y0, x1, y1, lit, lights, ox=ARC_X, oy=ARC_Y):
    """A sash window with lintel, frame and sill. (ox, oy) = the sprite's world origin, for the light entry."""
    xx, yy = p.xx, p.yy
    p.put(p.R(x0 - 3, y0 - 6, x1 + 3, y0 - 2), "stone", 4)               # lintel
    p.put(p.R(x0 - 3, y0 - 6, x1 + 3, y0 - 5), "stone", 6)
    p.put(p.R(x0 - 2, y0 - 2, x1 + 2, y1 + 2), "wood", 4)                # frame
    p.put(p.R(x0 - 2, y0 - 2, x0 - 1, y1 + 2), "wood", 6)                # the reveal that faces the sun
    p.put(p.R(x1 + 1, y0 - 2, x1 + 2, y1 + 2), "wood", 2)
    p.put(p.R(x0 - 2, y0 - 2, x1 + 2, y0 - 1), "wood", 2)
    glass = p.R(x0, y0, x1, y1)
    mx = (x0 + x1) // 2
    if lit:
        p.put(glass, "glow", 3, "dawn")
        p.put(glass & (yy < y0 + 12), "glow", 4, "dawn")
        for a, b in ((x0, x0 + 9), (x1 - 8, x1)):                         # drawn curtains, the room between them
            cur = p.R(a, y0, b, y1)
            p.put(cur, "glow", 5, "dawn")
            p.add(cur & ((xx - a) % 4 == 3), -1, "dawn")
        p.put(p.P([(mx - 8, y1 - 9), (mx - 5, y1 - 15), (mx - 1, y1 - 15), (mx + 2, y1 - 9)]) & glass, "glow", 6, "dawn")   # a table lamp
        p.put(p.R(mx - 4, y1 - 9, mx - 2, y1) & glass, "cab", 1, "dawn")
        lights.append(("main", ox + x0, oy + y0, x1 - x0, y1 - y0))
    else:
        p.put(glass, "glass", 1, "dawn")
        p.put(glass & (yy > y1 - 9), "glass", 0, "dawn")
        p.put(p.P([(x0, y0 + 14), (x0 + 14, y0), (x0 + 22, y0), (x0, y0 + 22)]) & glass, "glass", 2, "dawn")
        p.put(p.P([(x1 - 8, y1), (x1, y1 - 8), (x1, y1 - 3), (x1 - 3, y1)]) & glass, "glass", 2, "dawn")
    p.put(glass, "glass", 2, "sunrise")
    p.put(glass & (yy > y1 - 10), "glass", 1, "sunrise")
    p.put(p.P([(x0, y0 + 16), (x0 + 16, y0), (x0 + 26, y0), (x0, y0 + 26)]) & glass, "glass", 4, "sunrise")
    p.put(p.P([(x1 - 12, y1), (x1, y1 - 12), (x1, y1 - 6), (x1 - 6, y1)]) & glass, "glass", 3, "sunrise")
    p.put(p.R(mx, y0, mx + 1, y1), "wood", 3)                            # glazing bars
    p.put(p.R(x0, y0 + 12, x1, y0 + 13), "wood", 3)
    sill = p.R(x0 - 4, y1 + 2, x1 + 4, y1 + 5)
    p.put(sill, "stone", 5)
    p.put(sill & (yy == y1 + 2), "stone", 7)
    p.put(sill & (yy == y1 + 4), "stone", 3)
    return sill


def shutter(p, x0, y0, x1, y1):
    m = p.R(x0, y0, x1, y1)
    p.put(m, "cloth", 3)
    p.add(m & ((p.yy - y0) % 4 == 3), -1)                                 # the shade under each louvre
    p.add(m & ((p.yy - y0) % 4 == 0), 1)
    p.put(p.R(x0, y0, x0 + 1, y1), "cloth", 5)
    p.put(p.R(x1 - 1, y0, x1, y1), "cloth", 1)
    p.put(p.R(x0, y0, x1, y0 + 1), "cloth", 4)
    p.put(p.R(x0, y1 - 1, x1, y1), "cloth", 1)
    return m


def cabinet(p, x, w, h, base, clip, seed):
    r = np.random.default_rng(seed)
    t = base - h
    def put(m, mat, lv, st=None):
        p.put(m & clip, mat, lv, st)
    put(p.R(x, t, x + w, base), "cab", 1)
    put(p.R(x + w - 3, t, x + w, base), "cab", 3)
    put(p.R(x, t, x + 1, base), "cab", 0)
    put(p.R(x + 1, t + 1, x + w - 1, t + 5), "glow", 6)                   # lit marquee
    put(p.R(x + 3, t + 2, x + w - 4, t + 4), "cab", 2)
    put(p.R(x + 2, t + 7, x + w - 2, t + 18), "cab", 0)                   # bezel
    scr = p.R(x + 3, t + 8, x + w - 3, t + 17)
    put(scr, "screen", 1)
    put(p.E(x + w / 2, t + 12.5, w / 2 - 5, 3) & scr, "screen", 2)
    for _ in range(3):                                                    # whatever is on screen
        sx, sy = x + 4 + int(r.integers(0, w - 9)), t + 9 + int(r.integers(0, 6))
        put(p.R(sx, sy, sx + int(r.integers(1, 3)), sy + 2) & scr, "screen", 0)
    put(p.R(x - 1, t + 19, x + w + 1, t + 23), "cab", 3)                  # control panel
    put(p.R(x - 1, t + 19, x + w + 1, t + 20), "cab", 4)
    put(p.R(x + 4, t + 16, x + 5, t + 19), "cab", 0)                      # stick
    put(p.R(x + 3, t + 15, x + 6, t + 17), "screen", 2)
    put(p.R(x + w - 7, t + 20, x + w - 5, t + 21), "glow", 6)
    put(p.R(x + w - 4, t + 20, x + w - 2, t + 21), "screen", 1)
    put(p.R(x + w // 2 - 2, base - 10, x + w // 2 + 2, base - 4), "cab", 2)


def draw_arcade(lights):
    BW, BH, GL = 230, 176, 172
    p = Pix(BW, BH, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(71)
    X0, X1 = 14, 198
    L = lambda x, y, w, h: lights.append(("main", ARC_X + x, ARC_Y + y, w, h))

    # ---- chimney (behind the roof)
    ch = p.R(40, 3, 56, 24)
    p.put(ch, "stone", 3)
    p.put(p.R(52, 3, 56, 24), "stone", 5)
    p.put(p.R(40, 3, 42, 24), "stone", 2)
    p.mottle(ch, 75, t=0.5)
    cap = p.R(38, 0, 58, 3)
    p.put(cap, "stone", 4)
    p.put(cap & (yy == 0), "stone", 6)
    p.put(cap & (yy == 2), "stone", 2)

    # ---- wall
    wall = p.R(X0, 44, X1, GL)
    p.put(wall, "wall", 3)
    n = noise(BH, BW, 34, 22, 72, 2)
    p.add(wall & (n > 0.42), 1)                                           # broad calm patches of plaster
    p.add(wall & (n < -0.46), -1)
    p.mottle(wall, 73, t=0.66)
    p.add(wall & (yy < 53), -1)                                           # in the eave's shade
    p.add(wall & (yy < 50), -1)
    # patches where the plaster has come away and the stone shows
    for cx, cy, k in ((122, 150, 5), (76, 52, 3), (186, 118, 3)):
        for _ in range(k):
            bx, by = cx + int(r.integers(-7, 8)), cy + int(r.integers(-6, 7))
            st = p.E(bx, by, r.uniform(2.6, 4.6), r.uniform(1.8, 3.0)) & wall
            p.put(st, "stone", int(r.integers(3, 6)))
            p.add(st & ~sh(st, 0, 1), 1)
            p.add(st & ~sh(st, 0, -1), -1)
    # corner stones: long and short alternately, the sunward corner bright
    for i, y in enumerate(range(52, 160, 9)):
        w = 10 if i % 2 == 0 else 6
        for a, b, lv in ((X1 - w, X1, 5), (X0, X0 + w, 3)):
            q = p.R(a, y, b, y + 8)
            p.put(q, "stone", lv)
            p.put(q & (yy == y), "stone", lv + 1)
            p.put(q & (yy == y + 7), "stone", lv - 2)
        p.put(p.R(X1 - 1, y, X1, y + 8), "stone", 7)
    # plinth and string course
    pl = p.R(X0 - 1, 160, X1 + 1, GL)
    p.put(pl, "stone", 3)
    p.put(pl & (yy == 160), "stone", 5)
    p.put(pl & (yy >= 169), "stone", 2)
    p.put(p.R(X1 - 3, 160, X1 + 1, GL), "stone", 5)
    x = X0 + int(r.integers(4, 18))
    while x < X1:
        p.add(p.R(x, 162 + int(r.integers(0, 2)), x + 1, 170 - int(r.integers(0, 3))), -1)
        x += int(r.integers(16, 34))
    p.mottle(pl & (yy > 160), 76, t=0.5)
    sc = p.R(X0 - 1, 104, X1 + 1, 108)
    p.put(sc, "stone", 4)
    p.put(sc & (yy == 104), "stone", 6)
    p.put(sc & (yy == 107), "stone", 2)
    p.add(wall & (yy >= 108) & (yy < 110), -1)

    # ---- roof
    roof = p.P([(7, 47), (16, 20), (196, 20), (205, 47)])
    p.put(roof, "roof", 2)
    p.add(roof & (xx > 132 + (yy - 20) * 0.4), 1)
    p.add(roof & (xx > 182 + (yy - 20) * 0.3), 1)
    for cy in range(25, 47, 5):
        line = roof & (yy == cy) & (noise(BH, BW, 12, 1, 74 + cy, 1) > -0.3)
        p.add(long_runs(line, 5), -1)
    for _ in range(16):                                                   # a few slates a step off, no more
        tx, ty = int(r.integers(12, 198)), 21 + 5 * int(r.integers(0, 5))
        p.add(p.R(tx, ty, tx + int(r.integers(5, 10)), ty + 4) & roof, int(r.choice([-1, 1])))
    p.mottle(roof, 80, t=0.6)
    nm = noise(BH, BW, 10, 5, 77, 2)
    p.put(drop_single(roof & (yy > 34) & (xx < 110) & (nm > 0.30)), "moss", 1)
    p.put(drop_single(roof & (yy > 40) & (xx < 90) & (nm > 0.12)), "moss", 2)
    ridge = p.R(14, 17, 198, 21)
    p.put(ridge, "roof", 4)
    p.put(ridge & (yy == 17), "roof", 6)
    p.put(ridge & (yy == 20), "roof", 1)
    p.put(p.R(40, 20, 57, 26), "roof", 1)                                 # the chimney's foot in its own shadow
    fascia = p.R(6, 47, 206, 50)
    p.put(fascia, "wood", 2)
    p.put(fascia & (yy == 47), "wood", 4)
    p.put(p.R(200, 47, 206, 50), "wood", 5)

    # ---- upper floor
    sills = p.Z()
    for wx, lit in ((32, True), (94, False)):
        sills |= window(p, wx, 60, wx + 28, 94, lit, lights)
        shutter(p, wx - 11, 58, wx - 2, 96)
        shutter(p, wx + 30, 58, wx + 39, 96)
        box = p.R(wx - 2, 97, wx + 30, 102)                               # flower box
        p.put(box, "wood", 3)
        p.put(box & (yy == 97), "wood", 5)
        p.put(box & (yy == 101), "wood", 1)
        crown(p, [(wx + 3, 94, 5, 4), (wx + 11, 92, 6, 5), (wx + 19, 94, 5, 4), (wx + 26, 93, 5, 4)], "leafB", 200 + wx, base=3, drips=4)
    # balcony: door, pots, slab, railing, and the cat
    p.put(p.R(150, 52, 182, 104), "wood", 4)
    p.put(p.R(150, 52, 151, 104), "wood", 6)
    p.put(p.R(181, 52, 182, 104), "wood", 2)
    bd = p.R(153, 55, 179, 104)
    p.put(bd, "glass", 1, "dawn")
    p.put(bd & (yy > 86), "glass", 0, "dawn")
    p.put(p.P([(153, 72), (170, 55), (179, 55), (153, 81)]) & bd, "glass", 2, "dawn")
    p.put(bd, "glass", 2, "sunrise")
    p.put(bd & (yy > 84), "glass", 1, "sunrise")
    p.put(p.P([(153, 76), (174, 55), (179, 55), (179, 60), (153, 86)]) & bd, "glass", 4, "sunrise")
    p.put(p.R(165, 55, 167, 104), "wood", 3)
    p.put(p.R(153, 70, 179, 71), "wood", 3)
    for px in (141, 184):
        pot = p.P([(px, 90), (px + 9, 90), (px + 8, 100), (px + 1, 100)])
        p.put(pot, "roof", 3)
        p.put(pot & (yy == 90), "roof", 5)
        p.put(pot & (xx >= px + 7), "roof", 5)
        crown(p, [(px + 2, 84, 5, 5), (px + 6, 79, 6, 6), (px + 8, 86, 4, 4)], "leafB", 210 + px, base=3, drips=2)
    slab = p.R(136, 100, 196, 104)
    p.put(slab, "stone", 5)
    p.put(slab & (yy == 100), "stone", 7)
    p.put(slab & (yy == 103), "stone", 2)
    rail = p.R(136, 78, 196, 81)
    bal = p.Z()
    for bx in range(138, 195, 7):
        bal |= p.R(bx, 81, bx + 2, 100)
    p.put(bal, "iron", 1)
    p.put(bal & ~sh(bal, -1, 0), "iron", 3)
    p.put(rail, "iron", 2)
    p.put(rail & (yy == 78), "iron", 4)
    for px in (136, 193):
        p.put(p.R(px, 76, px + 3, 100), "iron", 1)
        p.put(p.R(px + 2, 76, px + 3, 100), "iron", 3)
    cat = p.E(52.5, 88, 4.6, 6) | p.E(53, 79.5, 3.3, 3.0) | p.P([(50, 78), (51, 74), (53, 78)]) | p.P([(53, 78), (55, 74), (56, 78)]) \
        | p.R(46, 91, 50, 94) | p.R(45, 88, 47, 92)
    p.put(cat, "fur", 0, "dawn")
    p.put(cat, "fur", 1, "sunrise")
    p.put(cat & ~sh(cat, -1, 0), "fur", 3, "sunrise")

    # ---- shop window: a lit room full of machines
    p.put(p.R(21, 109, 115, 161), "wood", 3)
    p.put(p.R(21, 109, 22, 161), "wood", 5)
    p.put(p.R(114, 109, 115, 161), "wood", 1)
    room = p.R(24, 112, 112, 158)
    p.put(room, "glow", 3)
    p.put(room & (yy < 146), "glow", 4)
    p.put(room & (yy < 134), "glow", 5)
    for px, py in ((34, 137), (58, 134), (104, 138), (77, 136)):          # posters on the back wall
        p.put(p.R(px, py, px + 6, py + 8) & room, "glow", 2)
        p.put(p.R(px + 1, py + 1, px + 5, py + 4) & room, "cab", 3)
    for lx in (39, 68, 97):                                               # pendant lamps
        p.put(p.E(lx, 132, 10, 5) & room, "glow", 6)
        p.put(p.P([(lx - 4, 130), (lx - 2, 126), (lx + 2, 126), (lx + 4, 130)]) & room, "cab", 1)
        p.put(p.R(lx - 2, 130, lx + 2, 131) & room, "glow", 6)
    p.put(room & (yy >= 154), "cab", 2)                                   # floor
    cabinet(p, 27, 18, 31, 157, room, 1)
    cabinet(p, 46, 17, 28, 156, room, 2)
    cabinet(p, 64, 19, 32, 157, room, 3)
    st = p.R(85, 148, 91, 150) | p.R(87, 150, 89, 157)                    # a stool
    p.put(st & room, "cab", 1)
    cabinet(p, 93, 17, 30, 157, room, 4)
    for mx in (53, 82):                                                   # mullions, dark against the light
        p.put(p.R(mx, 112, mx + 3, 158), "wood", 2)
        p.put(p.R(mx, 112, mx + 1, 158), "wood", 4)
    for a, b, c, d in ((24, 150, 60, 112), (70, 158, 112, 118)):          # sunrise: the sky slides across the glass
        band = p.P([(a, b), (c, d), (c + 12, d), (a + 12, b)]) & room
        p.add(band, 2, "sunrise")
    sill = p.R(19, 158, 117, 162)
    p.put(sill, "stone", 5)
    p.put(sill & (yy == 158), "stone", 7)
    p.put(sill & (yy == 161), "stone", 3)
    sills |= sill
    L(24, 112, 88, 46)

    # ---- awning
    aw = p.P([(22, 108), (114, 108), (119, 121), (17, 121)])
    stripe = ((xx - 17) // 8) % 2 == 0
    p.put(aw, "cloth", 2)
    p.put(aw & stripe, "cloth", 4)
    p.add(aw & (yy == 108), 1)
    p.add(aw & (xx > 96), 1)
    p.add(aw & (yy >= 119), -1)
    val = p.R(17, 121, 119, 126)                                          # a straight valance (scallops read as dashes)
    p.put(val, "cloth", 1)
    p.put(val & stripe, "cloth", 3)
    p.add(val & (xx > 96), 1)
    p.add(val & (yy == 125), -1)
    below = (p.R(19, 126, 117, 132) | p.R(19, 132, 112, 135)) & ~val
    p.add(below, -1)                                                      # its shade on the glass and frame
    p.cast(aw | val, p.R(14, 108, 118, 150), 9, slope=0.9)

    # ---- door
    p.put(p.R(127, 109, 163, GL), "wood", 4)
    p.put(p.R(127, 109, 128, GL), "wood", 6)
    p.put(p.R(162, 109, 163, GL), "wood", 2)
    p.put(p.R(127, 109, 163, 110), "wood", 2)
    tr = p.R(130, 112, 160, 118)
    p.put(tr, "glow", 5, "dawn")
    p.put(tr, "glass", 3, "sunrise")
    p.put(p.R(144, 112, 146, 118), "wood", 3)
    leaf = p.R(130, 120, 160, GL)
    p.put(leaf, "wood", 3)
    p.put(leaf & (xx >= 158), "wood", 4)
    p.mottle(leaf, 78, t=0.6)
    dg = p.R(135, 125, 155, 145)
    p.put(dilate(dg) & leaf & ~dg, "wood", 2)
    p.put(dg, "glow", 4, "dawn")
    p.put(dg & (yy < 133), "glow", 5, "dawn")
    p.put(dg, "glass", 2, "sunrise")
    p.put(p.P([(135, 139), (149, 125), (155, 125), (135, 145)]) & dg, "glass", 4, "sunrise")
    p.put(p.R(144, 125, 146, 145), "wood", 2)
    p.put(p.R(135, 134, 155, 135), "wood", 2)
    plq = p.R(138, 137, 144, 141)                                         # the little plaque hung inside the glass
    p.put(plq, "cream", 2)
    p.put(p.R(139, 138, 143, 139), "cab", 1)
    pan = p.R(135, 150, 155, 167)
    p.put(pan, "wood", 2)
    p.put(pan & ((yy == 150) | (xx == 154)), "wood", 1)
    p.put(pan & ((yy == 166) | (xx == 135)), "wood", 4)
    p.put(p.R(155, 146, 157, 151), "lamp", 1)                             # brass handle
    step = p.R(124, 169, 166, 175)
    p.put(step, "stone", 5)
    p.put(step & (yy == 169), "stone", 7)
    p.put(step & (yy >= 172), "stone", 3)
    p.put(p.R(163, 169, 166, 175), "stone", 6)
    L(135, 125, 20, 20)

    # ---- wall lamp by the door
    p.put(p.R(165, 116, 172, 118), "iron", 1)
    p.put(p.R(165, 116, 172, 117), "iron", 3)
    p.put(p.P([(167, 121), (171.5, 117), (176, 121)]), "iron", 1)
    lg = p.R(168, 121, 175, 129)
    p.put(lg, "lamp", 2, "dawn")
    p.put(p.R(170, 123, 173, 128), "lamp", 3, "dawn")
    p.put(lg, "lamp", 0, "sunrise")
    p.put(p.R(173, 121, 175, 129), "lamp", 2, "sunrise")
    p.put(p.R(168, 129, 175, 131), "iron", 1)
    p.put(p.R(167, 121, 168, 130), "iron", 1)
    p.put(p.R(175, 121, 176, 130), "iron", 3)
    L(168, 121, 7, 8)

    # ---- capsule-toy machine
    vm = p.R(172, 136, 195, GL)
    p.put(vm, "cloth", 2)
    p.put(p.R(192, 136, 195, GL), "cloth", 4)
    p.put(p.R(172, 136, 173, GL), "cloth", 1)
    p.put(p.R(171, 134, 196, 137), "cloth", 3)
    p.put(p.R(171, 134, 196, 135), "cloth", 5)
    pnl = p.R(175, 139, 191, 156)
    p.put(pnl, "glow", 5, "dawn")
    p.put(pnl, "glow", 4, "sunrise")
    for _ in range(15):                                                   # capsules heaped behind the glass
        bx, by = 175 + int(r.integers(0, 13)), 146 + int(r.integers(0, 8))
        mat, lv = [("cream", 2), ("cream", 1), ("screen", 1), ("cloth", 4), ("lamp", 1), ("cab", 3)][int(r.integers(0, 6))]
        b = p.E(bx + 1.5, by + 1.5, 1.8, 1.8) & pnl
        p.put(b, mat, lv)
    p.put(p.R(175, 139, 191, 140), "cab", 1)
    p.put(p.R(178, 159, 189, 168), "cab", 0)
    p.put(p.E(183.5, 163.5, 2.6, 2.6), "cream", 2)
    p.put(p.R(183, 162, 184, 165), "cab", 1)
    p.put(p.R(172, GL - 2, 195, GL), "cloth", 0)
    L(175, 139, 16, 17)

    # ---- hanging sign (no lettering: a joystick)
    p.put(p.R(198, 62, 226, 64), "iron", 1)
    p.put(p.R(198, 62, 226, 63), "iron", 3)
    p.put(p.L(198, 76, 211, 64), "iron", 1)
    for cx in (206, 220):
        p.put(p.R(cx, 64, cx + 1, 69), "iron", 2)
    board = p.R(202, 69, 225, 93)
    p.put(board, "wood", 3)
    p.put(board & ((yy == 69) | (xx == 224)), "wood", 5)
    p.put(board & ((yy == 92) | (xx == 202)), "wood", 1)
    p.put(p.R(204, 71, 223, 91), "cloth", 2)
    p.put(p.R(207, 85, 220, 88), "cream", 2)
    p.put(p.R(207, 85, 220, 86), "cream", 3)
    p.put(p.R(212, 77, 214, 85), "cream", 1)
    p.put(p.E(213, 75.5, 3.2, 3.2), "lamp", 2)
    p.put(p.R(217, 82, 219, 84), "lamp", 1)

    # ---- drain pipe, crates, a potted bush, ivy
    p.put(p.R(15, 50, 19, 168), "iron", 1)
    p.put(p.R(18, 50, 19, 168), "iron", 3)
    for by in (84, 134):
        p.put(p.R(13, by, 21, by + 2), "iron", 2)
    p.put(p.R(15, 166, 25, 170), "iron", 1)
    p.put(p.R(15, 166, 25, 167), "iron", 3)
    for cx0, cy0, cw, chh in ((27, 152, 21, 20), (30, 139, 15, 13)):
        cr = p.R(cx0, cy0, cx0 + cw, cy0 + chh)
        p.put(cr, "wood", 3)
        p.put(cr & ((yy - cy0) % 5 == 4), "wood", 2)
        fr = cr & ((xx < cx0 + 2) | (xx >= cx0 + cw - 2) | (yy < cy0 + 2) | (yy >= cy0 + chh - 2))
        p.put(fr, "wood", 4)
        p.put(cr & (yy == cy0), "wood", 6)
        p.put(cr & (xx >= cx0 + cw - 1), "wood", 6)
        p.put(cr & (xx == cx0), "wood", 2)
        p.put(p.L(cx0 + 2, cy0 + chh - 3, cx0 + cw - 3, cy0 + 2, 2) & cr, "wood", 4)
    pot = p.P([(101, 160), (117, 160), (115, GL), (103, GL)])
    p.put(pot, "roof", 3)
    p.put(pot & (yy <= 161), "roof", 5)
    p.put(pot & (xx >= 114), "roof", 5)
    p.put(pot & (xx <= 103), "roof", 2)
    crown(p, [(104, 153, 7, 6), (112, 147, 8, 7), (116, 155, 6, 5), (108, 142, 6, 5)], "leafB", 230, base=3, drips=3)
    stem = [(17, 171), (20, 152), (15, 134), (21, 117), (17, 100), (24, 86), (19, 72), (27, 62), (38, 56), (52, 53)]
    ivy = []
    for (xa, ya), (xb, yb) in zip(stem, stem[1:]):
        for t in np.linspace(0, 1, 5, endpoint=False):
            ivy.append((xa + (xb - xa) * t + r.uniform(-3.5, 3.5), ya + (yb - ya) * t + r.uniform(-2, 2),
                        r.uniform(3.0, 5.6), r.uniform(2.6, 4.4)))
    keep = {st: (p.mat[st][GL - 1:].copy(), p.lvl[st][GL - 1:].copy()) for st in p.mat}
    crown(p, ivy, "leafB", 231, base=3, drips=9)
    for st, (m_, l_) in keep.items():                                     # the creeper stops at the ground
        p.mat[st][GL - 1:], p.lvl[st][GL - 1:] = m_, l_

    # ---- water stains under the sills
    for _ in range(26):
        ys, xs = np.nonzero(sh(sills, 0, 1) & ~sills & p.is_mat("wall"))
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        ln = int(r.integers(4, 13))
        p.add(p.R(xs[i], ys[i], xs[i] + 2, ys[i] + ln) & p.is_mat("wall"), -1)

    # ---- dawn: lamp and window light spilling onto the plaster (hard steps, slightly ragged)
    nz = noise(BH, BW, 9, 9, 79, 1) * 1.2
    wallm = p.is_mat("wall", st="dawn")
    hard = p.is_mat("stone", "wood", "cloth", "iron", st="dawn")
    for cx, cy, rad in ((46, 78, 30), (68, 150, 50), (145, 134, 26), (171, 126, 34), (183, 148, 20)):
        d = (np.hypot(xx + 0.5 - cx, (yy + 0.5 - cy) * 1.15) + nz) / rad
        p.remat(wallm & (d < 1.0), "wallwarm", 0, "dawn")
        p.remat(wallm & (d < 0.52), "wallhot", 0, "dawn")
        p.add(wallm & (d < 0.26), 1, "dawn")
        p.add(hard & (d < 0.6), 1, "dawn")
    # ---- sunrise: low sun from the right, so everything that sticks out throws a shadow to the left
    flat = p.is_mat("wall", "wallwarm", "wallhot", st="sunrise")
    p.cast(sills, flat, 5, slope=0.8)
    p.cast(slab | rail, flat | p.is_mat("stone", st="sunrise"), 8, slope=0.9)
    p.cast(vm, flat, 7, slope=0.2)
    p.cast(lg, flat, 10, slope=0.3)
    p.cast(p.R(15, 50, 19, 168), flat, 3, slope=0.0)
    return p


# ====================================================================== buildings 2-6
# Each lives in its own module b_<id>.py (see b_template.md for the contract). Missing ones are skipped.
BUILDINGS = ["b_projects", "b_music", "b_about", "b_skills", "b_experience", "b_pier"]


def build(lights):
    import importlib
    import os
    only = os.environ.get("ONLY")                      # e.g. ONLY=b_pier,b_experience while others are in progress
    names = [n for n in BUILDINGS if only is None or n in only.split(",")]
    out, pools = {}, []
    arcade = draw_arcade(lights)
    SPRITES.append(("arcade", ARC_X, ARC_Y, arcade))
    STOPS.append({"id": "gameProjects", "x0": ARC_X + 110, "x1": ARC_X + 180, "door": ARC_X + 145})
    out["arcade"] = arcade
    for name in names:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        pix = mod.draw(lights)
        SPRITES.append((mod.NAME, mod.X, G - mod.GL, pix))
        out[mod.NAME] = pix
        if getattr(mod, "ID", None):
            stop = {"id": mod.ID, "x0": mod.X + mod.STOP[0], "x1": mod.X + mod.STOP[1], "door": mod.X + mod.DOOR}
            if hasattr(mod, "LABEL_Y"):
                stop["labelY"] = G - mod.GL + mod.LABEL_Y
            STOPS.append(stop)
        pools += [(mod.X + cx, hw) for cx, hw in getattr(mod, "POOLS", ())]
    out["ground"] = draw_ground(lights, pools)
    return out
