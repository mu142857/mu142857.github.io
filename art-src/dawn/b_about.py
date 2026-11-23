"""Building 4: a small home (About Me).

A low cottage: plaster over a rubble base, timber corner posts, a steep slate roof with one
gabled dormer (the lit attic), a ground-floor window with shutters, a painted door under a
little canopy with a porch lamp, a bicycle leaning on the wall, a mailbox on a post, and a
garden strip on the left with a board fence, a hedge, a washing line and a bird house.
Sprite 214 x 154, ground line = local y 150.
"""
import numpy as np

from draw_bg import crown
from draw_main import G, shutter, window
from kit import Pix, dilate, drop_single, long_runs, noise, sh
from pal import PAL

NAME = "about"
ID = "about"
X = 1560
BW, BH, GL = 214, 154, 150
DOOR = 152
STOP = (116, 188)
POOLS = [(68, 17), (152, 15)]


def draw(lights):
    p = Pix(BW, BH, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(401)
    OX, OY = X, G - GL
    L = lambda x, y, w, h: lights.append(("main", OX + x, OY + y, w, h))
    X0, X1, EAVE, BASE = 38, 190, 76, 134

    # ---- garden strip on the left: pole + bird house, washing line, hedge, board fence
    pole = p.R(5, 84, 8, GL)
    p.put(pole, "wood", 3)
    p.put(p.R(7, 84, 8, GL), "wood", 5)
    bh = p.R(1, 72, 13, 84)                                               # bird house
    p.put(bh, "wood", 4)
    p.put(p.R(11, 72, 13, 84), "wood", 6)
    p.put(p.R(1, 72, 2, 84), "wood", 2)
    p.put(p.R(0, 83, 14, 85), "wood", 2)
    p.put(p.P([(-2, 73), (7, 64), (16, 73)]), "roof", 2)
    p.put(p.P([(7, 64), (16, 73), (13, 73), (7, 67)]), "roof", 4)
    p.put(p.E(7, 77.5, 2.2, 2.2), "wood", 0)
    p.put(p.R(6, 81, 10, 82), "wood", 6)                                  # perch
    line = p.L(8, 90, 22, 94) | p.L(22, 94, 38, 92)
    p.put(line, "iron", 3)
    wash = p.Z()
    for (a, b, top, h, mat, lv, lift) in ((10, 20, 91, 21, "cream", 2, 2), (22, 28, 95, 12, "cloth", 3, 0), (29, 37, 94, 17, "cream", 1, -2)):
        m = p.P([(a, top), (b, top + (1 if lift >= 0 else -1)), (b, top + h + min(0, lift)), (a, top + h - max(0, lift))])
        p.put(m, mat, lv)
        p.add(m & (xx >= b - 2), 1)                                        # the edge that faces the sun
        p.add(m & (xx == a), -1)
        p.add(m & (xx == (a + b) // 2) & (yy > top + 3), -1)               # one fold
        p.put(p.R(a + 1, top - 1, a + 3, top + 2), "wood", 5)              # pegs
        p.put(p.R(b - 3, top - 1, b - 1, top + 2), "wood", 5)
        wash |= m
    crown(p, [(14, 128, 7, 6), (24, 125, 8, 7), (33, 128, 7, 6), (5, 130, 6, 5), (19, 131, 6, 4), (29, 131, 6, 4)], "leafB", 410, base=3, drips=0)
    x, fence = 0, p.Z()
    while x < X0 - 1:
        w = int(r.integers(5, 8))
        top = 135 + int(r.integers(-1, 2))
        b = p.P([(x, top + 2), (x + w / 2, top - 1), (x + w, top + 2), (x + w, GL), (x, GL)]) & (xx < X0 - 1)
        lv = 3 + int(r.integers(0, 2))
        p.put(b, "wood", lv)
        p.put(b & (xx == x + w - 1), "wood", lv + 2)
        p.put(b & (xx == x), "wood", lv - 2)
        fence |= b
        x += w
    p.add(fence & (yy >= 139) & (yy < 141), 1)                             # the rail showing between boards
    p.add(fence & (yy >= GL - 2), -1)
    p.mottle(fence, 411, t=0.62)

    # ---- chimney (behind the roof)
    ch = p.R(152, 6, 168, 34)
    p.put(ch, "stone", 3)
    p.put(p.R(164, 6, 168, 34), "stone", 5)
    p.put(p.R(152, 6, 154, 34), "stone", 2)
    p.mottle(ch, 402, t=0.5)
    cap = p.R(150, 3, 170, 6)
    p.put(cap, "stone", 4)
    p.put(cap & (yy == 3), "stone", 6)
    p.put(cap & (yy == 5), "stone", 2)
    for cx in (155, 162):                                                 # two pots
        p.put(p.R(cx, 0, cx + 4, 3), "roof", 3)
        p.put(p.R(cx + 3, 0, cx + 4, 3), "roof", 5)

    # ---- wall: plaster over a rubble base, timber posts at the corners
    wall = p.R(X0, EAVE, X1, GL)
    p.put(wall, "wall", 3)
    n = noise(BH, BW, 30, 20, 403, 2)
    p.add(wall & (n > 0.42), 1)
    p.add(wall & (n < -0.46), -1)
    p.mottle(wall, 404, t=0.66)
    p.add(wall & (yy < EAVE + 9), -1)                                      # in the eave's shade
    p.add(wall & (yy < EAVE + 6), -1)
    base = p.R(X0 - 1, BASE, X1 + 1, GL)
    p.put(base, "stone", 3)
    p.put(base & (yy >= GL - 3), "stone", 2)
    for _ in range(26):                                                   # rubble: a few stones a step off, never a grid
        bx, by = int(r.integers(X0, X1)), int(r.integers(BASE + 2, GL - 1))
        st = p.E(bx, by, r.uniform(3.0, 6.5), r.uniform(1.8, 3.2)) & base & (yy > BASE)
        p.put(st, "stone", int(r.choice([2, 4, 4, 5])))
        p.add(st & ~sh(st, 0, 1), 1)
        p.add(st & ~sh(st, 0, -1), -1)
    p.put(p.R(X1 - 3, BASE, X1 + 1, GL), "stone", 5)
    p.mottle(base, 405, t=0.55)
    beam = p.R(X0 - 1, BASE - 4, X1 + 1, BASE)                             # sill beam between plaster and stone
    p.put(beam, "wood", 3)
    p.put(beam & (yy == BASE - 4), "wood", 5)
    p.put(beam & (yy == BASE - 1), "wood", 1)
    for a, b, lv in ((X0, X0 + 5, 2), (X1 - 5, X1, 4)):
        post = p.R(a, EAVE, b, BASE - 4)
        p.put(post, "wood", lv)
        p.put(post & (xx == b - 1), "wood", lv + 2)
        p.put(post & (xx == a), "wood", lv - 1)
        p.mottle(post, 406 + a, t=0.6)
    for cx, cy, k in ((118, 96, 3), (182, 120, 2)):                       # plaster gone, stone showing
        for _ in range(k):
            bx, by = cx + int(r.integers(-6, 7)), cy + int(r.integers(-5, 6))
            st = p.E(bx, by, r.uniform(2.6, 4.4), r.uniform(1.8, 2.8)) & p.is_mat("wall")
            p.put(st, "stone", int(r.integers(3, 6)))
            p.add(st & ~sh(st, 0, 1), 1)
            p.add(st & ~sh(st, 0, -1), -1)

    # ---- roof: steep, with one gabled dormer
    roof = p.P([(28, EAVE + 2), (47, 24), (181, 24), (200, EAVE + 2)])
    p.put(roof, "roof", 2)
    p.add(roof & (xx > 128 + (yy - 24) * 0.36), 1)
    p.add(roof & (xx > 176 + (yy - 24) * 0.36), 1)
    for cy in range(30, EAVE, 6):
        ln = roof & (yy == cy) & (noise(BH, BW, 12, 1, 407 + cy, 1) > -0.3)
        p.add(long_runs(ln, 5), -1)
    for _ in range(20):
        tx, ty = int(r.integers(30, 196)), 25 + 6 * int(r.integers(0, 8))
        p.add(p.R(tx, ty, tx + int(r.integers(5, 10)), ty + 5) & roof, int(r.choice([-1, 1])))
    p.mottle(roof, 408, t=0.6)
    nm = noise(BH, BW, 10, 5, 409, 2)
    p.put(drop_single(roof & (yy > 58) & (xx < 80) & (nm > 0.30)), "moss", 1)
    p.put(drop_single(roof & (yy > 66) & (xx < 70) & (nm > 0.12)), "moss", 2)
    ridge = p.R(45, 21, 183, 25)
    p.put(ridge, "roof", 4)
    p.put(ridge & (yy == 21), "roof", 6)
    p.put(ridge & (yy == 24), "roof", 1)
    chsh = p.P([(152, 25), (169, 25), (169, 30), (150, 46), (136, 46)]) & roof      # the chimney's shadow, thrown left
    p.add(chsh, -1)
    p.add(p.R(152, 25, 169, 29) & roof, -1)
    fascia = p.R(27, EAVE + 2, 201, EAVE + 5)
    p.put(fascia, "wood", 2)
    p.put(fascia & (yy == EAVE + 2), "wood", 4)
    p.put(p.R(195, EAVE + 2, 201, EAVE + 5), "wood", 5)
    # dormer
    dw = p.P([(81, 52), (97, 34), (113, 52), (113, 73), (81, 73)])
    p.put(dw, "wall", 4)
    p.add(dw & (yy < 50), -1)
    p.put(dw & (xx >= 111), "wall", 6)
    p.put(p.P([(76, 54), (97, 30), (97, 36), (80, 56)]), "roof", 1)        # the slope that faces away from the sun
    lit_s = p.P([(97, 30), (118, 54), (114, 56), (97, 36)])
    p.put(lit_s, "roof", 4)
    p.put(lit_s & ~sh(lit_s, 0, 1), "roof", 6)
    dfr = p.R(88, 50, 106, 72)
    p.put(dfr, "wood", 4)
    p.put(dfr & (xx == 88), "wood", 6)
    p.put(dfr & ((xx == 105) | (yy == 50)), "wood", 2)
    dg = p.R(90, 52, 104, 70)
    p.put(dg, "glow", 4, "dawn")
    p.put(dg & (yy < 59), "glow", 5, "dawn")
    p.put(p.P([(92, 70), (94, 63), (99, 63), (101, 70)]) & dg, "glow", 6, "dawn")           # a desk lamp
    p.put(p.R(101, 62, 104, 70) & dg, "cab", 1, "dawn")                   # books standing on the sill
    p.put(p.R(99, 64, 101, 70) & dg, "cab", 3, "dawn")
    p.put(dg, "glass", 2, "sunrise")
    p.put(dg & (yy > 64), "glass", 1, "sunrise")
    p.put(p.P([(90, 62), (100, 52), (104, 52), (90, 66)]) & dg, "glass", 4, "sunrise")
    p.put(p.R(96, 52, 98, 70), "wood", 3)
    p.put(p.R(90, 60, 104, 61), "wood", 3)
    dsill = p.R(86, 72, 108, 75)
    p.put(dsill, "stone", 5)
    p.put(dsill & (yy == 72), "stone", 7)
    p.put(dsill & (yy == 74), "stone", 3)
    L(90, 52, 14, 18)
    dorm = dw | lit_s | p.P([(76, 54), (97, 30), (97, 36), (80, 56)])

    # ---- ground-floor window with shutters and a flower box
    sills = window(p, 56, 92, 84, 124, True, lights, OX, OY)
    sh_l, sh_r = shutter(p, 45, 90, 54, 126), shutter(p, 86, 90, 95, 126)
    box = p.R(54, 127, 86, 131)
    p.put(box, "wood", 3)
    p.put(box & (yy == 127), "wood", 5)
    p.put(box & (yy == 130), "wood", 1)
    crown(p, [(59, 124, 5, 4), (67, 122, 6, 5), (75, 124, 5, 4), (82, 123, 5, 4)], "leafB", 412, base=3, drips=3)

    # ---- door under a little canopy
    p.put(p.R(136, 90, 168, GL), "wood", 4)
    p.put(p.R(136, 90, 137, GL), "wood", 6)
    p.put(p.R(167, 90, 168, GL), "wood", 2)
    p.put(p.R(136, 90, 168, 91), "wood", 2)
    tr = p.R(139, 93, 165, 98)
    p.put(tr, "glow", 5, "dawn")
    p.put(tr, "glass", 3, "sunrise")
    p.put(p.R(151, 93, 153, 98), "wood", 3)
    leaf = p.R(139, 100, 165, GL)
    p.put(leaf, "cloth", 2)
    p.put(leaf & (xx >= 163), "cloth", 3)
    p.put(leaf & (xx == 139), "cloth", 1)
    p.mottle(leaf, 413, t=0.62)
    p.add(leaf, -1, "sunrise")                                            # so the painted door stands off the plaster
    dgl = p.R(146, 105, 158, 119)
    p.put(dilate(dgl) & leaf & ~dgl, "cloth", 1)
    p.put(dgl, "glow", 4, "dawn")
    p.put(dgl & (yy < 111), "glow", 5, "dawn")
    p.put(dgl, "glass", 2, "sunrise")
    p.put(p.P([(146, 114), (155, 105), (158, 105), (146, 118)]) & dgl, "glass", 4, "sunrise")
    p.put(p.R(152, 105, 153, 119), "cloth", 1)
    pan = p.R(144, 125, 160, 145)
    p.put(pan, "cloth", 1)
    p.put(pan & ((yy == 125) | (xx == 159)), "cloth", 0)
    p.put(pan & ((yy == 144) | (xx == 144)), "cloth", 3)
    p.put(p.R(161, 121, 163, 126), "lamp", 1)                             # brass handle
    step = p.R(132, 147, 172, 153)
    p.put(step, "stone", 5)
    p.put(step & (yy == 147), "stone", 7)
    p.put(step & (yy >= 150), "stone", 3)
    p.put(p.R(169, 147, 172, 153), "stone", 6)
    can = p.P([(131, 83), (173, 83), (178, 89), (126, 89)])
    p.put(can, "roof", 3)
    p.put(can & (yy == 83), "roof", 5)
    p.put(can & (xx > 160), "roof", 4)
    p.put(can & (yy == 88), "roof", 1)
    for a, b in ((130, 135), (174, 169)):                                 # brackets
        br = p.L(a, 89, b, 96, 2)
        p.put(br, "wood", 2)
    p.add(p.R(129, 89, 175, 92) & ~can & p.is_mat("wall", "wood"), -1)     # the canopy's shade
    L(146, 105, 12, 14)

    # ---- porch lamp
    p.put(p.R(172, 98, 180, 100), "iron", 1)
    p.put(p.R(172, 98, 180, 99), "iron", 3)
    p.put(p.P([(173, 103), (177.5, 99), (182, 103)]), "iron", 1)
    lg = p.R(174, 103, 181, 111)
    p.put(lg, "lamp", 2, "dawn")
    p.put(p.R(176, 105, 179, 110), "lamp", 3, "dawn")
    p.put(lg, "lamp", 0, "sunrise")
    p.put(p.R(179, 103, 181, 111), "lamp", 2, "sunrise")
    p.put(p.R(174, 111, 181, 113), "iron", 1)
    p.put(p.R(173, 103, 174, 112), "iron", 1)
    p.put(p.R(181, 103, 182, 112), "iron", 3)
    L(174, 103, 7, 8)

    # ---- bicycle leaning on the wall between the window and the door
    bike = p.Z()
    for cx in (106, 127):
        ring = p.E(cx, GL - 8.5, 8.5, 8.5) & ~p.E(cx, GL - 8.5, 7.2, 7.2)
        bike |= ring
        bike |= p.E(cx, GL - 8.5, 1.4, 1.4)
    fr = p.L(106, GL - 9, 113, GL - 19) | p.L(113, GL - 19, 124, GL - 20) | p.L(124, GL - 20, 127, GL - 9) \
        | p.L(113, GL - 19, 117, GL - 8) | p.L(117, GL - 8, 124, GL - 20) | p.L(106, GL - 9, 117, GL - 8)
    bike |= fr | p.L(112, GL - 23, 113, GL - 19) | p.L(124, GL - 20, 123, GL - 26)
    p.put(bike, "iron", 2)
    p.put(bike & ~sh(bike, -1, 0) & (yy < GL - 2), "iron", 4)
    p.put(fr & ~p.E(106, GL - 8.5, 1.4, 1.4) & ~p.E(127, GL - 8.5, 1.4, 1.4), "cloth", 4)   # a painted frame
    p.put(p.R(108, GL - 25, 116, GL - 23), "wood", 1)                     # saddle
    p.put(p.R(108, GL - 25, 116, GL - 24), "wood", 3)
    p.put(p.R(121, GL - 28, 127, GL - 26), "iron", 2)                     # handlebar
    p.put(p.R(126, GL - 28, 128, GL - 25), "wood", 2)
    bskt = p.P([(127, GL - 25), (136, GL - 25), (134, GL - 17), (128, GL - 17)])          # a basket on the front
    p.put(bskt, "wood", 4)
    p.put(bskt & (yy == GL - 25), "wood", 6)
    p.put(bskt & (xx <= 128), "wood", 2)

    # ---- potted bush by the door, mailbox on a post
    pot = p.P([(172, 138), (186, 138), (184, GL), (174, GL)])
    p.put(pot, "roof", 3)
    p.put(pot & (yy <= 139), "roof", 5)
    p.put(pot & (xx >= 183), "roof", 5)
    p.put(pot & (xx <= 174), "roof", 2)
    crown(p, [(175, 132, 6, 5), (182, 127, 7, 6), (185, 134, 5, 4), (178, 123, 5, 4)], "leafB", 414, base=3, drips=2)
    mpost = p.R(203, 127, 206, GL)
    p.put(mpost, "wood", 3)
    p.put(p.R(205, 127, 206, GL), "wood", 5)
    mb = p.R(197, 117, 212, 127) | (p.E(204.5, 117, 7.5, 5) & (yy < 117))
    p.put(mb, "cloth", 3)
    p.put(mb & (xx >= 210), "cloth", 5)
    p.put(mb & (xx <= 197), "cloth", 1)
    p.put(mb & (yy >= 125), "cloth", 1)
    p.put(mb & ~sh(mb, 0, 1) & (xx > 199), "cloth", 5)
    p.put(p.R(199, 119, 207, 120), "cloth", 0)                            # the slot
    p.put(p.R(209, 109, 210, 118), "iron", 3)                             # the flag, up
    p.put(p.R(205, 109, 209, 113), "lamp", 1)

    # ---- water stains under the sills
    allsill = sills | dsill
    for _ in range(14):
        ys, xs = np.nonzero(sh(sills, 0, 1) & ~sills & p.is_mat("wall"))
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        p.add(p.R(xs[i], ys[i], xs[i] + 2, ys[i] + int(r.integers(4, 11))) & p.is_mat("wall"), -1)

    # ---- dawn: lamp and window light spilling onto the plaster
    nz = noise(BH, BW, 9, 9, 415, 1) * 1.2
    wallm = p.is_mat("wall", st="dawn")
    hard = p.is_mat("stone", "wood", "cloth", "iron", st="dawn")
    for cx, cy, rad in ((70, 110, 30), (97, 62, 16), (152, 108, 24), (177, 108, 32)):
        d = (np.hypot(xx + 0.5 - cx, (yy + 0.5 - cy) * 1.15) + nz) / rad
        p.remat(wallm & (d < 1.0), "wallwarm", 0, "dawn")
        p.remat(wallm & (d < 0.52), "wallhot", 0, "dawn")
        p.add(wallm & (d < 0.26), 1, "dawn")
        p.add(hard & (d < 0.6), 1, "dawn")
    # ---- sunrise: everything that sticks out throws a shadow to the left
    flat = p.is_mat("wall", "wallwarm", "wallhot", st="sunrise")
    p.cast(allsill, flat, 5, slope=0.8)
    p.cast(sh_l | sh_r, flat, 3, slope=0.2)
    p.cast(can, flat | p.is_mat("wood", st="sunrise"), 8, slope=0.9)
    p.cast(lg, flat, 10, slope=0.3)
    p.cast(dorm, roof & ~dorm, 9, slope=0.5)
    p.cast(p.R(X1 - 5, EAVE, X1, BASE), flat, 0, slope=0)
    p.cast(bike | bskt, flat | p.is_mat("stone", st="sunrise"), 6, slope=0.25)
    p.cast(wash, p.is_mat("leafB", "wood", st="sunrise"), 6, slope=0.6)
    return p
