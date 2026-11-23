"""Background layers of the dawn street: sky + lake (pinned), far shore, island + boats,
our shore curving away, the trees and lamps right behind the walk, foreground silhouettes.

Flat side view, no perspective. Horizon at y = 150; the sun sits on it at x = 392 (screen
coordinates: the sky layer never scrolls). Light is low and from the RIGHT in both states.
"""
import numpy as np

from kit import Pix, noise, noise1d, periodic, sh, dilate, erode, drop_single, long_runs
from pal import PAL

W, H, TILE = 480, 270, 960
HOR = 150
SUN = (392, 150)
SUN_R = 13
LIGHTS = []          # (layer, x, y, w, h) of every lamp / lit window, collected for scene.json


# ====================================================================== sky + lake
def draw_sky():
    p = Pix(W, H, PAL)
    xx, yy = p.xx, p.yy
    dx, dy = xx + 0.5 - SUN[0], yy + 0.5 - SUN[1]
    n1 = noise(H, W, 120, 10, 11, 3)
    n2 = noise(H, W, 60, 6, 12, 2)
    sky = yy < HOR
    # colour bands: the further from the sun (left), the lower each band sits
    ye = yy + n1 * 7 - np.clip(SUN[0] - xx, 0, None) * 0.035
    bounds = [141, 127, 108, 88, 69, 52, 36, 21, 9]
    band = np.full((H, W), 9)
    for i in range(8, -1, -1):
        band[ye >= bounds[i]] = i
    p.put(sky, "sky", 9 - band)

    up = HOR - yy
    ringE = sky & (up < 8 * np.exp(-(dx / 230) ** 2) + n1 * 2 + 0.5)
    p.put(ringE, "ring", 0)
    # sunrise: rings around the half-risen sun
    ringD = sky & (up < 21 * np.exp(-(dx / 125) ** 2) + n1 * 3.5 + 1) & (up > 3 + n1 * 2)
    p.put(ringD, "ring", 1, "sunrise")
    p.put(sky & (np.hypot(dx / 2.2, dy) + n2 * 1.8 < 37), "ring", 2, "sunrise")
    p.put(sky & (np.hypot(dx / 1.35, dy) + n2 * 1.3 < 29), "ring", 3, "sunrise")
    p.put(sky & (np.hypot(dx / 1.2, dy) + n2 * 1.0 < 19), "ring", 4, "sunrise")
    sun = sky & (dx ** 2 + dy ** 2 <= SUN_R ** 2)
    p.put(sun, "sun", 1, "sunrise")
    p.put(sun & (up <= 4), "sun", 0, "sunrise")
    # dawn: only a line of pale light lying on the horizon, thickest under where the sun will be
    p.put(sky & (up < 5.0 * np.exp(-(dx / 190) ** 2) + n1 * 1.2), "ring", 1, "dawn")
    p.put(sky & (up < 3.2 * np.exp(-(dx / 120) ** 2) + n1 * 0.8), "ring", 2, "dawn")
    p.put(sky & (up < 2.0 * np.exp(-(dx / 70) ** 2) + 0.2), "ring", 3, "dawn")
    p.put(sky & (up <= 1) & (np.abs(dx) < 34), "ring", 4, "dawn")

    # long strata, edges bitten out by sideways-stretched noise
    n3 = noise(H, W, 64, 5, 21, 3) + 0.55 * noise(H, W, 150, 14, 22, 1)
    strips = [(96, 46, 118, 8.0), (330, 24, 104, 6.5), (228, 76, 132, 7.5), (40, 99, 78, 6.0),
              (440, 60, 80, 6.0), (318, 109, 96, 5.0), (150, 122, 72, 4.0), (452, 122, 52, 3.4)]
    cloud = p.Z()
    zone = np.zeros((H, W), int)
    for cx, cy, hl, ht in strips:
        m = (((xx - cx) / hl) ** 2 + ((yy - cy) / ht) ** 2 + n3 * 0.9 < 0.78) & (yy < HOR - 16)
        d = np.hypot(cx - SUN[0], (cy - SUN[1]) * 1.6)
        zone[m] = 0 if d < 105 else (1 if d < 215 else 2)
        cloud |= m
    belly = cloud & (~sh(cloud, 0, -1) | (~sh(cloud, 0, -2) & (n3 > 0.05)))
    top = cloud & ~belly & (~sh(cloud, 0, 1) | ~sh(cloud, 0, 2) | (~sh(cloud, 0, 3) & (n3 < 0.1)))
    for z, name in enumerate(("cloudA", "cloudB", "cloudC")):
        zm = cloud & (zone == z)
        p.put(zm, name, 1)
        p.put(zm & top, name, 0)
        p.put(zm & belly, name, 2)

    # stars, dawn only: scattered, thinning toward the horizon and the light
    r = np.random.default_rng(5)
    for _ in range(70):
        x, y = int(r.integers(2, W - 2)), int(r.integers(2, 104))
        if cloud[y - 1:y + 2, x - 1:x + 2].any() or r.random() < (y / 104) ** 1.5 * 0.8 + max(0, x - 250) / 600:
            continue
        m = p.Z()
        m[y, x] = True
        p.put(m, "star", int(r.choice([0, 0, 1, 1, 2])), "dawn")

    # ---- the lake
    water = yy >= HOR
    nw = noise(H, W, 46, 2.5, 31, 2)
    yw = yy + nw * 1.6
    bnd = [150, 153, 157, 162, 168, 176, 186, 198, 214]
    wl = np.zeros((H, W), int)
    for i in range(8):
        wl[yw >= bnd[i]] = 7 - i
    p.put(water, "water", wl)
    nr = noise(H, W, 9, 1.2, 33, 1)
    p.add(long_runs(water & (yy > 152) & (nr > 0.60), 3), 1)
    p.add(long_runs(water & (yy > 152) & (nr < -0.60), 3), -1)
    p.add(water & (yy < 152) & (noise(H, W, 30, 1, 35, 1) > -0.15), -1)      # the far shore's dark edge on the water
    hot = water & (((dx) / 62) ** 2 + ((yy - HOR) / 9.5) ** 2 + nw * 0.25 < 1)
    p.put(hot, "hot", 0)
    p.put(water & ((dx / 27) ** 2 + ((yy - HOR) / 5.2) ** 2 + nw * 0.2 < 1), "hot", 1)
    # the light's reflection: a column of short bars, bright and dense at the top, dimmer and
    # sparser toward us; lengths and positions are irregular on purpose (never an even dash)
    for st, keep, ymax in (("sunrise", 1.0, 214), ("dawn", 0.55, 184)):
        r = np.random.default_rng(77)
        for y in range(HOR + 1, ymax):
            t = (y - HOR) / (214 - HOR)
            rolls = r.random(3)
            if rolls[0] > (1.0 - 0.62 * t) * keep:
                continue
            ln = int(r.integers(3, 6 + int(t * 16)))
            off = int(round(r.normal(0, 2 + t * 13)))
            x0 = SUN[0] + off - ln // 2
            m = p.R(x0, y, x0 + ln, y + 1)
            p.put(m, "glint", 2 if (t < 0.22 and abs(off) < 5) else (1 if rolls[1] > t * 0.9 else 0), st)
            if rolls[2] < 0.3 and ln > 5:                    # a second, dimmer bar further out on the same row
                x1 = x0 + int(r.choice([-1, 1])) * int(r.integers(ln + 3, ln + 12))
                p.put(p.R(x1, y, x1 + int(r.integers(2, 5)), y + 1), "glint", 0, st)
    return p


# ====================================================================== far shore (k .04)
def draw_far():
    p = Pix(TILE, H, PAL)
    xx, yy = p.xx, p.yy
    x = np.arange(TILE)
    hb = 11 + 6 * periodic(TILE, 5, (1, 2, 3, 5)) + 9 * np.exp(-((x - 190) / 110) ** 2) + 6 * np.exp(-((x - 700) / 70) ** 2)
    hf = 4.5 + 3.5 * periodic(TILE, 6, (2, 3, 5, 8))
    hb, hf = np.round(hb).astype(int), np.round(hf).astype(int)
    back = (yy >= HOR - hb[xx]) & (yy < HOR)
    front = (yy >= HOR - hf[xx]) & (yy < HOR)
    p.put(back, "hill", 2)
    p.add(back & ~sh(back, 0, 1) & (np.roll(hb, -1)[xx] < hb[xx]), 1)        # crest catching the light where it falls away to the right
    p.put(front, "hill", 1)
    # two small towns under the hills: blocks in groups, one spire each
    r = np.random.default_rng(9)
    for x0, n in ((286, 16), (742, 9), (70, 6)):
        cx = x0
        spire = int(r.integers(2, n - 2))
        for i in range(n):
            w, h = int(r.integers(3, 8)), int(r.integers(4, 10))
            top = HOR - hf[cx] - h + 2
            b = p.R(cx, top, cx + w, HOR)
            p.put(b, "hill", 0)
            p.put(p.R(cx + w - 1, top, cx + w, HOR), "hill", 3)               # sunward edge
            if i == spire:
                p.put(p.R(cx + 1, top - 7, cx + 3, top), "hill", 0)
                p.put(p.R(cx + 2, top - 10, cx + 3, top - 7), "hill", 0)
            elif w >= 5 and r.random() < 0.55:
                p.put(p.P([(cx - 1, top), (cx + w / 2, top - 3), (cx + w + 1, top)]), "hill", 0)
            if r.random() < 0.5:
                wx, wy = cx + int(r.integers(1, max(2, w - 2))), top + int(r.integers(2, max(3, h - 1)))
                p.put(p.R(wx, wy, wx + 1, wy + 1), "farwin", int(r.integers(0, 2)), "dawn")
            cx += w + int(r.choice([0, 0, 1, 1, 2, 5]))
    return p


# ====================================================================== shared: broadleaf trees
def crown(p, clumps, mat, seed, base=2, drips=6):
    """Leaf clumps (cx, cy, rx, ry) painted back to front, each shaded as a ball lit from the
    right and a little above, each casting a band of shade on the ones behind it."""
    n = noise(p.h, p.w, 3.2, 3.0, seed, 2)
    whole = p.Z()
    for i, (cx, cy, rx, ry) in enumerate(clumps):
        ex, ey = (p.xx + 0.5 - cx) / rx, (p.yy + 0.5 - cy) / ry
        m = ex ** 2 + ey ** 2 + n * 0.34 < 1.0
        m = drop_single(m)
        p.add(whole & ~m & sh(m, -2, 2), -1)                       # shade it throws to the lower left
        t = ex * 0.80 - ey * 0.52 + n * 0.22
        lv = np.full((p.h, p.w), base)
        lv = lv + (t > 0.18) + (t > 0.62) + (t > 0.94) - (t < -0.40) - (t < -0.86)
        p.put(m, mat, lv)
        whole |= m
    # a few strands hanging from the underside, tapering to a point
    r = np.random.default_rng(seed + 1)
    under = whole & ~sh(whole, 0, -1)
    ys, xs = np.nonzero(under)
    for _ in range(drips):
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        x, y, ln = int(xs[i]), int(ys[i]), int(r.integers(3, 7))
        p.put(p.R(x, y, x + 2, y + ln - 1), mat, base - 1)
        p.put(p.R(x + int(r.integers(0, 2)), y + ln - 1, x + 1 + int(r.integers(0, 2)), y + ln + 1), mat, base - 1)
    return whole


def dome(r, cx, top, half_w, depth, n, size):
    """Clump centres for a broadleaf canopy: a dome that is wider than tall with a ragged,
    nearly flat underside; big clumps in the middle, small ones round the rim."""
    cl = []
    for i in range(n):
        u = r.uniform(-1, 1) * r.uniform(0.35, 1.0) ** 0.5
        roof = 1 - (1 - abs(u) ** 2.2) ** 0.75                       # 0 at the middle, 1 at the rim
        v = roof + r.uniform(0, 1) ** 1.5 * (1 - roof) * 0.95
        k = size * (1.0 - 0.45 * abs(u)) * r.uniform(0.75, 1.15)
        cl.append((cx + u * half_w, top + k * 0.55 + v * depth, k * r.uniform(1.15, 1.5), k * r.uniform(0.72, 0.95)))
    cl.sort(key=lambda c: (round(c[1] / (depth * 0.34)), c[0]))          # top tier first; within a tier, left to right
    return cl


def trunk(p, pts, w0, w1, mat, seed):
    """A tapering trunk along a polyline, shaded as a cylinder (lit on the right)."""
    whole = p.Z()
    (xa, ya), (xb, yb) = pts[0], pts[-1]
    total = sum(abs(q[1] - a[1]) for a, q in zip(pts, pts[1:])) or 1
    done = 0
    cen = np.zeros(p.h)
    wid = np.zeros(p.h)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for y in range(int(min(y0, y1)), int(max(y0, y1)) + 1):
            if not 0 <= y < p.h:
                continue
            f = (y - y0) / ((y1 - y0) or 1)
            g = (done + abs(y - y0)) / total
            cen[y], wid[y] = x0 + (x1 - x0) * f, w0 + (w1 - w0) * g
        done += abs(y1 - y0)
    rows = np.nonzero(wid)[0]
    for y in rows:
        a, b = int(round(cen[y] - wid[y] / 2)), int(round(cen[y] + wid[y] / 2))
        whole[y, max(0, a):max(0, b)] = True
    rel = np.zeros((p.h, p.w))
    for y in rows:
        rel[y] = (np.arange(p.w) + 0.5 - cen[y]) / max(1.0, wid[y] / 2)
    lv = np.full((p.h, p.w), 2)
    lv = lv + (rel > 0.15) + (rel > 0.62) - (rel < -0.45) - (rel < -0.82)
    lv[rel > 0.9] -= 1                                               # the far edge turns away again
    p.put(whole, mat, lv)
    bark = noise(p.h, p.w, 1.6, 10, seed, 1)
    p.add(whole & (bark > 0.5), 1)
    p.add(whole & (bark < -0.5), -1)
    return whole


# ====================================================================== island + boats (k .18)
def boat(p, cx, wl, lit):
    hull = p.P([(cx - 12, wl - 5), (cx + 13, wl - 5), (cx + 9, wl), (cx - 8, wl)])
    p.put(hull, "isle", 1)
    p.put(hull & (p.yy == wl - 5), "isle", 4)
    p.put(hull & (p.yy == wl - 1) & (p.xx > cx - 6), "isle", 0)
    cabin = p.R(cx - 4, wl - 10, cx + 4, wl - 5)
    p.put(cabin, "isle", 2)
    p.put(p.R(cx + 3, wl - 10, cx + 4, wl - 5), "isle", 4)
    p.put(p.R(cx - 5, wl - 11, cx + 5, wl - 10), "isle", 3)
    if lit:
        p.put(p.R(cx - 2, wl - 8, cx + 1, wl - 6), "lamp", 2, "dawn")
        LIGHTS.append(("isle", cx - 2, wl - 8, 3, 2))
    p.put(p.R(cx - 2, wl - 8, cx + 1, wl - 6), "isle", 5, "sunrise")
    p.put(p.R(cx + 6, wl - 31, cx + 7, wl - 5), "isle", 2)                       # mast
    p.put(p.L(cx + 7, wl - 30, cx + 13, wl - 6), "isle", 1)                      # forestay
    p.put(p.L(cx + 5, wl - 30, cx - 11, wl - 6), "isle", 1)                      # backstay
    boom = p.P([(cx + 6, wl - 15), (cx - 9, wl - 13), (cx - 9, wl - 10), (cx + 6, wl - 12)])
    p.put(boom, "sail", 1)                                                       # furled sail on the boom
    p.put(boom & ~sh(boom, 0, 1), "sail", 3)
    refl = p.P([(cx - 9, wl), (cx + 10, wl), (cx + 6, wl + 4), (cx - 5, wl + 4)])
    p.put(long_runs(refl & (noise(p.h, p.w, 6, 1, cx, 1) > -0.45), 3), "isle", 0)


def draw_isle():
    p = Pix(TILE, H, PAL)
    xx, yy = p.xx, p.yy
    x = np.arange(TILE)
    wl = 160
    hi = 13 * np.clip(1 - ((x - 690) / 112) ** 2, 0, None) ** 0.6 + 1.5 * periodic(TILE, 14, (9, 14, 23))
    hi = np.where(np.abs(x - 690) < 112, np.round(hi), 0).astype(int)
    land = (yy >= wl - hi[xx]) & (yy <= wl) & (hi[xx] > 0)
    p.put(land, "isle", 2)
    p.put(land & ~sh(land, 0, 1), "isle", 4)
    p.put(land & (yy >= wl - 1), "isle", 1)
    p.add(land & ~sh(land, -1, 0) & (xx > 690), 1)
    p.mottle(land, 15, t=0.5)
    refl = (yy > wl) & (yy <= wl + 4) & (hi[xx] > 3) & (noise(H, TILE, 7, 1, 16, 1) > -0.4 - (yy - wl) * -0.12)
    p.put(long_runs(refl, 3), "isle", 0)
    # lighthouse on the left shoulder
    lx, base = 618, wl - hi[618]
    tower = p.P([(lx - 4, base + 1), (lx - 3, base - 33), (lx + 3, base - 33), (lx + 4, base + 1)])
    p.put(tower, "sail", 1)
    p.put(tower & (xx >= lx + 1), "sail", 2)
    p.put(tower & (xx >= lx + 2), "sail", 3)
    p.put(tower & (xx <= lx - 3), "sail", 0)
    p.put(tower & (yy >= base - 22) & (yy < base - 16), "isle", 2)               # the dark band
    p.put(tower & (yy >= base - 22) & (yy < base - 16) & (xx >= lx + 1), "isle", 3)
    p.put(p.R(lx - 5, base - 35, lx + 5, base - 33), "isle", 1)                  # gallery
    p.put(p.R(lx - 3, base - 41, lx + 3, base - 35), "isle", 1)                  # lantern room frame
    p.put(p.R(lx - 2, base - 40, lx + 2, base - 36), "lamp", 3, "dawn")
    p.put(p.R(lx - 2, base - 40, lx + 2, base - 36), "lamp", 1, "sunrise")
    p.put(p.R(lx + 1, base - 40, lx + 2, base - 36), "lamp", 3, "sunrise")
    p.put(p.P([(lx - 4, base - 41), (lx, base - 46), (lx + 4, base - 41)]), "isle", 1)
    LIGHTS.append(("isle", lx - 2, base - 40, 4, 4))
    # the keeper's trees
    crown(p, [(648, wl - 17, 12, 9), (664, wl - 24, 12, 11), (683, wl - 20, 13, 10), (704, wl - 23, 15, 12),
              (726, wl - 17, 13, 9), (746, wl - 12, 10, 7), (772, wl - 7, 9, 5)], "isle", 31, base=2, drips=3)
    for cx, y, lit in ((118, 172, True), (332, 183, False), (890, 176, False), (432, 168, False)):
        boat(p, cx, y, lit)
    return p


# ====================================================================== our shore curving away (k .38)
BANK_END = 96           # in the last copy of the bank the land stops here; past it, open lake


def draw_bank(end=False):
    """Our own shore curving away. `end=True` is the copy behind the pier: the shore runs out
    after BANK_END and the rest is left clear, so the lake and the sun show."""
    p = Pix(TILE, H, PAL)
    xx, yy = p.xx, p.yy
    yb = np.round(205 + 2.5 * periodic(TILE, 21, (1, 2, 4, 7))).astype(int)
    if end:
        fall = np.clip((np.arange(TILE) - BANK_END) / 84.0, 0, 1) ** 1.5
        yb = np.round(yb + fall * 70).astype(int)
    r = np.random.default_rng(23)
    # trees first (the bank's turf then covers the foot of each trunk)
    # in groups, never evenly spaced: (x, height, half-width); "p" = a poplar (tall, narrow)
    for cx, hgt, hw, kind in ((30, 50, 24, "b"), (58, 62, 9, "p"), (112, 44, 30, "b"), (140, 34, 18, "b"),
                              (300, 58, 10, "p"), (316, 50, 8, "p"), (356, 54, 34, "b"),
                              (566, 40, 24, "b"), (700, 56, 32, "b"), (742, 42, 20, "b"), (772, 66, 10, "p"),
                              (900, 48, 28, "b")):
        base = yb[cx] + 2
        lean = int(r.integers(-4, 5))
        top = base - hgt
        if end and cx > BANK_END:
            continue
        if kind == "p":
            trunk(p, [(cx, base), (cx + lean * 0.3, top + hgt * 0.3)], 4, 2, "hut", cx)
            cl = [(cx + lean * 0.3 * (1 - i / 8) + r.uniform(-2, 2), top + 4 + i * (hgt - 16) / 8,
                   (hw - 1) * (0.45 + 0.55 * np.sin((i + 1) / 9.5 * np.pi)) + 1, r.uniform(6, 8)) for i in range(9)]
            crown(p, cl, "leafA", 100 + cx, base=2, drips=2)
            continue
        fork = base - hgt * 0.42
        trunk(p, [(cx, base), (cx + lean * 0.5, fork)], 6, 4, "hut", cx)
        trunk(p, [(cx + lean * 0.5 - 1, fork + 2), (cx + lean - hw * 0.5, top + hgt * 0.34)], 3, 2, "hut", cx + 1)
        trunk(p, [(cx + lean * 0.5 + 1, fork + 2), (cx + lean + hw * 0.45, top + hgt * 0.30)], 3, 2, "hut", cx + 2)
        crown(p, dome(r, cx + lean, top, hw, hgt * 0.40, int(hw * 0.55) + 4, 9.5), "leafA", 100 + cx, base=2, drips=5)
    # boathouse with a lit window
    bx, by = 452, yb[470]
    if end:
        bx = -400                                                         # off the picture
    body = p.R(bx, by - 21, bx + 42, by + 2)
    p.put(body, "hut", 2)
    p.put(p.R(bx + 39, by - 21, bx + 42, by + 2), "hut", 4)
    p.put(p.R(bx, by - 21, bx + 2, by + 2), "hut", 1)
    p.mottle(body, 24, t=0.5)
    p.put(p.R(bx, by - 21, bx + 42, by - 19), "hut", 1)                   # eave shadow
    roof = p.P([(bx - 5, by - 21), (bx + 19, by - 36), (bx + 23, by - 36), (bx + 47, by - 21)])
    p.put(roof, "hut", 1)
    p.put(roof & (xx > bx + 21), "hut", 3)
    p.put(roof & (xx > bx + 21) & ~sh(roof, 0, 1), "hut", 5)
    p.put(roof & (yy >= by - 23), "hut", 0)
    p.put(p.R(bx + 8, by - 13, bx + 17, by + 2), "hut", 0)                # door
    win = p.R(bx + 25, by - 14, bx + 33, by - 6)
    p.put(dilate(win) & ~win, "hut", 1)
    p.put(win, "lamp", 1, "dawn")
    p.put(p.R(bx + 26, by - 12, bx + 32, by - 7), "lamp", 2, "dawn")
    p.put(win, "hut", 3, "sunrise")
    p.put(p.R(bx + 30, by - 14, bx + 33, by - 6), "hut", 5, "sunrise")
    p.put(p.R(bx + 28, by - 14, bx + 29, by - 6), "hut", 1)               # glazing bar
    if not end:
        LIGHTS.append(("bank", bx + 25, by - 14, 8, 8))
    # the turf
    land = yy >= yb[xx]
    d = yy - yb[xx]
    lv = np.where(d < 1, 4, np.where(d < 3, 3, np.where(d < 9, 2, 1)))
    p.put(land, "bank", lv)
    p.mottle(land & (d > 1), 22, t=0.42)
    # grass: blades 2 px wide tapering to a point, in clumps, back row darker
    for row, lvl, n in ((0, 2, 150), (1, 4, 110)):
        for _ in range(n):
            x = int((r.normal(0, 1) * 34 + r.choice([60, 210, 250, 410, 520, 640, 830, 930])) % TILE)
            h = int(r.integers(3, 9))
            y0 = yb[x] + 1
            if end and x > BANK_END + 30:
                continue
            ln = int(r.integers(-2, 3))
            p.put(p.P([(x, y0), (x + 2, y0), (x + 1 + ln, y0 - h)]) | p.R(x, y0 - 2, x + 2, y0), "bank", lvl - row)
    # a rowboat pulled up beside the boathouse
    if not end:
        rb = p.P([(506, by - 6), (530, by - 6), (526, by), (510, by)])
        p.put(rb, "hut", 2)
        p.put(rb & ~sh(rb, 0, 1), "hut", 4)
        p.put(rb & ~sh(rb, 0, -1), "hut", 0)
    return p


# ====================================================================== trees, hedge and lamps behind the walk (k .62)
def lamp_post(p, x, foot, top, layer):
    p.put(p.R(x - 3, foot - 9, x + 4, foot), "iron", 1)
    p.put(p.R(x + 2, foot - 9, x + 4, foot), "iron", 3)
    p.put(p.R(x - 2, foot - 12, x + 3, foot - 9), "iron", 2)
    p.put(p.R(x - 1, top, x + 2, foot - 12), "iron", 1)
    p.put(p.R(x + 1, top, x + 2, foot - 12), "iron", 3)
    arm = p.P([(x - 1, top), (x + 2, top - 3), (x + 12, top - 4), (x + 12, top - 2), (x + 3, top - 1), (x + 2, top + 2)])
    p.put(arm, "iron", 1)
    p.put(arm & ~sh(arm, 0, 1), "iron", 3)
    p.put(p.R(x + 10, top - 2, x + 11, top + 1), "iron", 1)                # the hanger
    cap = p.P([(x + 5, top + 3), (x + 10.5, top - 1), (x + 16, top + 3)])
    p.put(cap, "iron", 1)
    p.put(cap & (p.xx >= x + 11), "iron", 3)
    glass = p.R(x + 7, top + 3, x + 14, top + 11)
    p.put(glass, "lamp", 2, "dawn")
    p.put(p.R(x + 9, top + 5, x + 12, top + 10), "lamp", 3, "dawn")
    p.put(glass, "lamp", 0, "sunrise")
    p.put(p.R(x + 12, top + 3, x + 14, top + 11), "lamp", 2, "sunrise")
    p.put(p.R(x + 6, top + 3, x + 7, top + 12), "iron", 1)
    p.put(p.R(x + 14, top + 3, x + 15, top + 12), "iron", 3)
    p.put(p.R(x + 7, top + 11, x + 14, top + 13), "iron", 1)
    LIGHTS.append((layer, x + 7, top + 3, 7, 8))


TREES_END_W = 1010      # the last copy of the trees layer is wider: it ends in open water


def draw_trees(end=False):
    """The trees right behind the walk. `end=True` draws the copy that closes the street: the
    same tile up to x = 700, where the bank slopes down into the lake and nothing more stands
    between the walk and the sunrise (the pier is in front of that stretch)."""
    Wd = TREES_END_W if end else TILE
    p = Pix(Wd, H, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(41)
    for cx, hgt, hw, w in ((150, 158, 78, 12), (236, 104, 46, 8), (606, 170, 86, 13), (848, 128, 60, 9)):
        base = 240
        lean = int(r.integers(-9, 10))
        top = base - hgt
        fork = base - hgt * 0.40
        if end and cx > 700:
            dome(r, cx + lean, top, hw, hgt * 0.36, int(hw * 0.42) + 6, 16)       # keep the random stream in step
            continue
        trunk(p, [(cx - lean * 0.4, base), (cx - lean * 0.1, base - hgt * 0.2), (cx + lean * 0.3, fork)], w, w - 3, "trunk", cx)
        trunk(p, [(cx + lean * 0.3 - 2, fork + 4), (cx + lean - hw * 0.34, fork - hgt * 0.14), (cx + lean - hw * 0.60, top + hgt * 0.26)], w - 4, 3, "trunk", cx + 1)
        trunk(p, [(cx + lean * 0.3 + 2, fork + 4), (cx + lean + hw * 0.22, fork - hgt * 0.18), (cx + lean + hw * 0.50, top + hgt * 0.22)], w - 5, 3, "trunk", cx + 2)
        trunk(p, [(cx + lean * 0.3, fork + 2), (cx + lean * 0.8, top + hgt * 0.2)], w - 5, 2, "trunk", cx + 3)
        crown(p, dome(r, cx + lean, top, hw, hgt * 0.36, int(hw * 0.42) + 6, 16), "leafB", 300 + cx, base=3, drips=10)
    # the hedge that hides the foot of everything
    yh = np.round(214 + 2.2 * periodic(TILE, 43, (3, 5, 8, 13)) - 3 * np.clip(periodic(TILE, 44, (7, 11)), 0, None)).astype(int)
    yh = np.concatenate([yh, yh])[:Wd]
    n = noise(H, Wd, 3.0, 2.6, 45, 2)
    if end:
        # past x = 700 the bank falls away: a slope of rough grass, a strip of wet stones, then water
        xs = np.arange(Wd)
        fall = np.clip((xs - 704) / 74.0, 0, 1) ** 1.6
        yh = np.round(yh + fall * 64 + 1.5 * noise1d(Wd, 9, 46) * (fall > 0)).astype(int)
        water = (yy >= 214) & (xx >= 700)
        p.put(water, "water", 0)
        nw = noise(H, Wd, 22, 1.2, 47, 2)
        p.add(long_runs(water & (nw > 0.34) & (yy % 2 == 0), 7), 1)                # long calm ripples, never dashes
        p.add(long_runs(water & (nw > 0.62) & (yy % 2 == 0), 9), 1)
    hedge = yy >= yh[xx]
    d = yy - yh[xx]
    p.put(hedge, "leafB", np.where(d < 2, 4, np.where(d < 6, 3, np.where(d < 14, 2, 1))))
    p.add(drop_single(hedge & (n > 0.55) & (d < 12)), 1)
    p.add(drop_single(hedge & (n < -0.55)), -1)
    if end:
        shore = hedge & (xx >= 742) & (d < 3)                                     # wet stones where it meets the lake
        p.put(shore, "stone", 3)
        p.put(shore & (d < 1), "stone", 5)
        p.add(drop_single(shore & (n > 0.2)), -1)
        p.put(sh(hedge, 0, -1) & ~hedge & (xx >= 742) & (yy >= 214), "water", 2)    # the bright line of water along it
    for x in (520, 902):
        if end and x > 700:
            continue
        lamp_post(p, x, 240, 146, "trees")
    return p


# ====================================================================== foreground silhouettes (k 1.3)
def draw_front():
    p = Pix(TILE, H, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(51)
    gh = np.round(7 + 4 * periodic(TILE, 52, (2, 3, 5, 9))).astype(int)
    for lvl, n in ((1, 170), (0, 230)):
        for _ in range(n):
            x = int((r.normal(0, 1) * 46 + r.choice([40, 170, 330, 470, 610, 800, 900])) % TILE)
            h = int(r.integers(7, 20)) + (6 if lvl == 0 else 0)
            y0 = H - gh[x] + 2
            ln = int(r.integers(-5, 6))
            wd = int(r.integers(2, 4))
            p.put(p.P([(x, y0), (x + wd, y0), (x + wd / 2 + ln, y0 - h)]) | p.R(x, y0 - 3, x + wd, y0), "front", lvl)
    p.put(yy >= H - gh[xx], "front", 0)
    # a tree close to the lens: trunk, one bough, leaves across the top of the frame
    t = trunk(p, [(708, H), (712, 150), (706, 40), (700, -4)], 16, 11, "front", 53)
    p.put(t, "front", 0)
    p.put(t & ~sh(t, -1, 0) & (noise(H, TILE, 2, 14, 54, 1) > -0.3), "front", 1)       # rim of light down the sunward side
    roots = p.P([(690, H), (700, H - 22), (724, H - 22), (738, H)])
    p.put(roots, "front", 0)
    b = trunk(p, [(704, 66), (668, 44), (628, 30), (590, 26)], 9, 3, "front", 55)
    p.put(b, "front", 0)
    n = noise(H, TILE, 4, 3.4, 56, 2)
    leaves = p.Z()
    for cx, cy, rx, ry in ((560, 14, 34, 16), (606, 8, 40, 18), (656, 16, 36, 20), (706, 6, 44, 20), (760, 12, 40, 22),
                           (806, 4, 30, 14), (590, 34, 20, 10), (742, 34, 22, 12), (680, 40, 16, 8)):
        leaves |= ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 + n * 0.42 < 1
    leaves = drop_single(leaves)
    p.put(leaves, "front", 0)
    edge = leaves & ~sh(leaves, -1, 0) & ~sh(leaves, 0, -1)
    p.put(drop_single(dilate(edge) & leaves & (n > 0.1)), "front", 1)
    # Slide the tile so the trunk (now at x = 838) never stands on a door. At k = 1.3 it crosses
    # the character when she is at world x = 700, 1438 and 2177 -- the gaps between buildings --
    # and the first and last screens (tile x 0-480 and 240-720) are clear of it.
    for st in p.mat:
        p.mat[st] = np.roll(p.mat[st], 130, axis=1)
        p.lvl[st] = np.roll(p.lvl[st], 130, axis=1)
    return p


LAYERS = [("sky", draw_sky), ("far", draw_far), ("isle", draw_isle), ("bank", draw_bank), ("trees", draw_trees), ("front", draw_front)]
