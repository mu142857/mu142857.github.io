"""Building 5: a bookshop (Technical Skills).

Two floors. Upstairs: plaster with three arched windows (the middle one lit: a reading room).
Downstairs: a painted timber shopfront -- a wide window full of lit bookshelves with a rolling
ladder and a banker's lamp on a table, a glazed door, a wall lamp, and a box of books on a
trestle outside. A sign with an open book hangs from a bracket on the left (no lettering).
Sprite 226 x 186, ground line = local y 182.
"""
import numpy as np

from draw_bg import crown
from draw_main import G
from kit import Pix, dilate, drop_single, long_runs, noise, sh
from pal import PAL

NAME = "skills"
ID = "skills"
X = 1940
BW, BH, GL = 226, 186, 182
DOOR = 156
STOP = (120, 192)
POOLS = [(83, 42), (156, 15), (184, 10)]
LABEL_Y = 98            # on the blank name board, clear of the upper windows

BOOKS = [("cab", 1), ("cab", 2), ("cab", 3), ("cab", 4), ("glow", 1), ("glow", 2), ("glow", 6), ("cream", 1), ("cream", 2),
         ("cloth", 2), ("cloth", 4), ("roof", 4), ("moss", 2), ("screen", 0), ("lamp", 0), ("wood", 5)]


def books(p, x0, x1, base, clip, r, hmax=10, flat=True):
    """A row of spines standing on `base`: irregular widths and heights, neighbours of one colour
    merge into bigger blocks, a gap or a flat stack now and then. No separators, so no grid."""
    x = x0
    while x < x1:
        roll = r.random()
        if roll < 0.09:
            x += int(r.integers(2, 5))
            continue
        if flat and roll < 0.20 and x + 8 < x1:                                    # a few lying flat
            for k in range(int(r.integers(2, 4))):
                mat, lv = BOOKS[int(r.integers(len(BOOKS)))]
                w = int(r.integers(6, 9))
                p.put(p.R(x, base - 2 * (k + 1), x + w, base - 2 * k) & clip, mat, lv)
            x += 9
            continue
        w, h = int(r.integers(2, 5)), int(r.integers(hmax - 4, hmax + 1))
        mat, lv = BOOKS[int(r.integers(len(BOOKS)))]
        m = p.R(x, base - h, x + w, base) & clip
        p.put(m, mat, lv)
        if w >= 3:
            p.add(m & (p.xx == x + w - 1), 1)
        x += w


def arch_window(p, cx, y0, y1, hw, lit, L, r, ro=0):
    """Round-headed window: y0 = where the arch springs, glass runs down to y1, half width hw."""
    xx, yy = p.xx, p.yy
    glass = p.R(cx - hw, y0, cx + hw, y1) | (p.E(cx, y0, hw, hw) & (yy < y0))
    frame = dilate(glass, 2) & (yy < y1 + 2)
    sur = (p.R(cx - hw - 5, y0, cx + hw + 5, y1 + 2) | (p.E(cx, y0, hw + 5, hw + 5) & (yy < y0)))
    p.put(sur, "stone", 4)
    p.put(sur & ~sh(sur, 0, 1), "stone", 6)
    p.put(sur & ~sh(sur, -1, 0) & (yy >= y0 - 4), "stone", 6)             # the edge that faces the sun
    p.put(sur & ~sh(sur, 1, 0) & (yy >= y0 - 4), "stone", 3)
    p.put(frame, "wood", 4)
    p.put(frame & ~glass & (xx < cx - hw), "wood", 6)                     # the reveal that faces the sun
    p.put(frame & ~glass & (xx >= cx + hw), "wood", 2)
    p.put(frame & ~glass & (yy < y0) & ~sh(frame, 0, 1), "wood", 2)
    key = p.R(cx - 3, y0 - hw - 7, cx + 3, y0 - hw - 1)
    p.put(key, "stone", 5)
    p.put(key & (yy == y0 - hw - 7), "stone", 7)
    p.put(key & (xx == cx + 2), "stone", 7)
    if lit:
        p.put(glass, "glow", 3, "dawn")
        p.put(glass & (yy < y0 + 14), "glow", 4, "dawn")
        p.put(glass & (yy < y0 + 2), "glow", 5, "dawn")
        shelf = p.R(cx - hw, y0 + 7, cx + hw, y0 + 9)                     # one shelf across the back wall
        p.put(shelf & glass, "cab", 1, "dawn")
        st = p.mat["dawn"].copy(), p.lvl["dawn"].copy(), p.mat["sunrise"].copy(), p.lvl["sunrise"].copy()
        books(p, cx - hw + 1, cx + hw - 1, y0 + 7, glass, r, 8)
        p.mat["sunrise"], p.lvl["sunrise"] = st[2], st[3]                 # (books only show while the lamp is on)
        p.put(p.P([(cx - 7, y1 - 9), (cx - 4, y1 - 15), (cx + 1, y1 - 15), (cx + 4, y1 - 9)]) & glass, "glow", 6, "dawn")
        p.put(p.R(cx - 2, y1 - 9, cx, y1) & glass, "cab", 1, "dawn")
        p.put(p.R(cx + 5, y1 - 5, cx + hw - 1, y1) & glass, "cab", 2, "dawn")    # a stack on the sill
        p.put(p.R(cx + 6, y1 - 8, cx + hw - 3, y1 - 5) & glass, "cab", 3, "dawn")
        L(cx - hw, y0 - hw, 2 * hw, y1 - y0 + hw)
    else:
        p.put(glass, "glass", 1, "dawn")
        p.put(glass & (yy > y1 - 9), "glass", 0, "dawn")
        p.put(p.P([(cx - hw, y0 + 12), (cx + 2, y0 - 4), (cx + 9, y0 - 4), (cx - hw, y0 + 20)]) & glass, "glass", 2, "dawn")
    p.put(glass, "glass", 2, "sunrise")
    p.put(glass & (yy > y1 - 10), "glass", 1, "sunrise")
    p.put(p.P([(cx - hw, y0 + 14 + ro), (cx + 4, y0 - 6 + ro), (cx + hw, y0 - 6 + ro), (cx + hw, y0 - 2 + ro), (cx - hw, y0 + 24 + ro)]) & glass, "glass", 4, "sunrise")
    p.put(p.P([(cx + hw - 10 + ro, y1), (cx + hw, y1 - 10 + ro), (cx + hw, y1 - 5 + ro), (cx + hw - 5 + ro, y1)]) & glass, "glass", 3, "sunrise")
    p.put(p.R(cx, y0 - hw, cx + 1, y1) & glass, "wood", 3)                # glazing bars
    p.put(p.R(cx - hw, y0, cx + hw, y0 + 1), "wood", 3)
    p.put(p.R(cx - hw, y0 + 16, cx + hw, y0 + 17), "wood", 3)
    sill = p.R(cx - hw - 6, y1 + 2, cx + hw + 6, y1 + 5)
    p.put(sill, "stone", 5)
    p.put(sill & (yy == y1 + 2), "stone", 7)
    p.put(sill & (yy == y1 + 4), "stone", 3)
    return sill, sur


def draw(lights):
    p = Pix(BW, BH, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(501)
    OX, OY = X, G - GL
    L = lambda x, y, w, h: lights.append(("main", OX + x, OY + y, w, h))
    X0, X1 = 30, 206

    # ---- chimney (behind the roof)
    ch = p.R(52, 5, 68, 28)
    p.put(ch, "stone", 3)
    p.put(p.R(64, 5, 68, 28), "stone", 5)
    p.put(p.R(52, 5, 54, 28), "stone", 2)
    p.mottle(ch, 502, t=0.5)
    cap = p.R(50, 2, 70, 5)
    p.put(cap, "stone", 4)
    p.put(cap & (yy == 2), "stone", 6)
    p.put(cap & (yy == 4), "stone", 2)

    # ---- upper wall
    wall = p.R(X0, 46, X1, 112)
    p.put(wall, "wall", 3)
    n = noise(BH, BW, 34, 22, 503, 2)
    p.add(wall & (n > 0.42), 1)
    p.add(wall & (n < -0.46), -1)
    p.mottle(wall, 504, t=0.66)
    p.add(wall & (yy < 56), -1)                                           # in the eave's shade
    p.add(wall & (yy < 53), -1)
    for cx, cy, k in ((90, 96, 3), (198, 62, 2)):                         # plaster gone, stone showing
        for _ in range(k):
            bx, by = cx + int(r.integers(-6, 7)), cy + int(r.integers(-5, 6))
            st = p.E(bx, by, r.uniform(2.6, 4.4), r.uniform(1.8, 2.8)) & wall
            p.put(st, "stone", int(r.integers(3, 6)))
            p.add(st & ~sh(st, 0, 1), 1)
            p.add(st & ~sh(st, 0, -1), -1)
    for a, b, lv in ((X0, X0 + 6, 3), (X1 - 6, X1, 5)):                   # plain stone strips at the corners
        q = p.R(a, 50, b, 108)
        p.put(q, "stone", lv)
        p.put(q & (xx == b - 1), "stone", lv + 2)
        p.mottle(q, 505 + a, t=0.55)

    # ---- roof: shallow, with a skylight
    roof = p.P([(22, 49), (34, 23), (202, 23), (214, 49)])
    p.put(roof, "roof", 2)
    p.add(roof & (xx > 136 + (yy - 23) * 0.4), 1)
    p.add(roof & (xx > 188 + (yy - 23) * 0.3), 1)
    for cy in range(28, 49, 5):
        ln = roof & (yy == cy) & (noise(BH, BW, 12, 1, 506 + cy, 1) > -0.3)
        p.add(long_runs(ln, 5), -1)
    for _ in range(16):
        tx, ty = int(r.integers(26, 206)), 24 + 5 * int(r.integers(0, 5))
        p.add(p.R(tx, ty, tx + int(r.integers(5, 10)), ty + 4) & roof, int(r.choice([-1, 1])))
    p.mottle(roof, 507, t=0.6)
    nm = noise(BH, BW, 10, 5, 508, 2)
    p.put(drop_single(roof & (yy > 37) & (xx < 100) & (nm > 0.30)), "moss", 1)
    p.put(drop_single(roof & (yy > 43) & (xx < 84) & (nm > 0.12)), "moss", 2)
    ridge = p.R(32, 20, 204, 24)
    p.put(ridge, "roof", 4)
    p.put(ridge & (yy == 20), "roof", 6)
    p.put(ridge & (yy == 23), "roof", 1)
    chsh = p.P([(52, 24), (69, 24), (69, 28), (56, 40), (40, 40)]) & roof   # the chimney's shadow, thrown left
    p.add(chsh, -1)
    sky = p.R(138, 29, 162, 43)                                           # skylight
    p.put(sky, "wood", 3)
    p.put(sky & (yy == 29), "wood", 5)
    p.put(sky & (xx == 138), "wood", 5)
    p.put(sky & ((yy == 42) | (xx == 161)), "wood", 1)
    sg = p.R(140, 31, 160, 41)
    p.put(sg, "glass", 1, "dawn")
    p.put(p.P([(140, 39), (150, 31), (155, 31), (144, 41), (140, 41)]) & sg, "glass", 2, "dawn")
    p.put(sg, "glass", 2, "sunrise")
    p.put(p.P([(140, 39), (150, 31), (158, 31), (147, 41), (140, 41)]) & sg, "glass", 4, "sunrise")
    p.put(p.R(150, 31, 151, 41), "wood", 2)
    fascia = p.R(21, 49, 215, 52)
    p.put(fascia, "wood", 2)
    p.put(fascia & (yy == 49), "wood", 4)
    p.put(p.R(209, 49, 215, 52), "wood", 5)

    # ---- upper floor: three arched windows, the middle one a lit reading room
    sills, surs = p.Z(), p.Z()
    for cx, lit, ro in ((64, False, 5), (118, True, -3), (172, False, 0)):
        s_, u_ = arch_window(p, cx, 72, 98, 11, lit, L, r, ro)
        sills |= s_
        surs |= u_

    # ---- painted timber shopfront
    front = p.R(X0 - 1, 112, X1 + 1, GL)
    p.put(front, "cloth", 2)
    p.mottle(front, 509, t=0.66)
    corn = p.R(X0 - 3, 108, X1 + 3, 112)                                  # cornice
    p.put(corn, "cloth", 4)
    p.put(corn & (yy == 108), "cloth", 5)
    p.put(corn & (yy == 111), "cloth", 1)
    band = p.R(X0 - 1, 112, X1 + 1, 123)                                  # the name board (left blank)
    p.put(band, "cloth", 3)
    p.put(band & (yy == 112), "cloth", 1)
    p.put(band & (yy >= 121), "cloth", 1)
    inset = p.R(X0 + 9, 114, X1 - 9, 120)
    p.put(inset, "cloth", 2)
    p.put(inset & (yy == 114), "cloth", 1)
    p.put(inset & (yy == 119), "cloth", 4)
    p.put(band & (xx >= X1 - 2), "cloth", 5)
    for a in (X0, 128, X1 - 8):                                           # pilasters
        pl = p.R(a, 123, a + 8, GL)
        p.put(pl, "cloth", 3)
        p.put(pl & (xx == a + 7), "cloth", 5)
        p.put(pl & (xx == a), "cloth", 1)
        capm = p.R(a - 1, 123, a + 9, 126)
        p.put(capm, "cloth", 4)
        p.put(capm & (yy == 125), "cloth", 1)
        ft = p.R(a - 1, GL - 6, a + 9, GL)
        p.put(ft, "cloth", 2)
        p.put(ft & (yy == GL - 6), "cloth", 4)
    # the window: a lit room lined with books
    p.put(p.R(40, 126, 126, 167), "wood", 3)
    p.put(p.R(40, 126, 41, 167), "wood", 5)
    p.put(p.R(125, 126, 126, 167), "wood", 1)
    room = p.R(43, 129, 123, 164)
    p.put(room, "glow", 3)
    p.put(room & (yy < 152), "glow", 4)
    p.put(room & (yy < 139), "glow", 5)
    case = p.R(45, 131, 104, 162) & room                                  # the bookcase against the back wall
    p.put(case, "glow", 2)
    p.put(case & (xx < 47), "cab", 1)
    p.put(case & (xx >= 102), "cab", 2)
    for sy in (141, 152, 162):
        p.put(p.R(45, sy - 1, 104, sy + 1) & room, "cab", 1)
        books(p, 48, 101, sy - 1, room, r, 9)
    p.put(p.R(45, 130, 104, 132) & room, "cab", 2)
    for a, b in ((104, 110), (110, 116)):                                 # rolling ladder
        p.put(p.L(a, 163, b - 2, 131, 1) & room, "cab", 0)
    for k, ry in enumerate((138, 144, 150, 156)):
        xa = 104 + (163 - ry) * 4 / 32
        p.put(p.R(xa, ry, xa + 7, ry + 1) & room, "cab", 1)
    p.put(room & (yy >= 161) & (xx >= 104), "cab", 2)                     # floor
    tb = p.R(106, 152, 123, 154) | p.R(108, 154, 110, 162) | p.R(119, 154, 121, 162)       # table
    p.put(tb & room, "cab", 1)
    p.put(p.R(106, 152, 123, 153) & room, "cab", 3)
    p.put(p.E(115, 149.5, 8, 3) & room & (yy < 152), "glow", 6)           # the pool under the lamp
    p.put(p.R(115, 144, 116, 152) & room, "cab", 0)
    shade = p.P([(109, 144), (111, 140), (120, 140), (122, 144)]) & room
    p.put(shade, "screen", 0)
    p.put(shade & (yy == 140), "screen", 1)
    p.put(p.R(107, 149, 112, 152) & room, "cab", 3)                       # a book left open on the table
    p.put(p.R(107, 149, 112, 150) & room, "cream", 2)
    for mx in (70, 98):                                                   # mullions, dark against the light
        p.put(p.R(mx, 129, mx + 3, 164), "wood", 2)
        p.put(p.R(mx, 129, mx + 1, 164), "wood", 4)
    for a, b, c, d in ((43, 158, 76, 129), (88, 164, 123, 133)):          # sunrise: the sky slides across the glass
        bandm = p.P([(a, b), (c, d), (c + 12, d), (a + 12, b)]) & room
        p.add(bandm, 2, "sunrise")
    sill = p.R(38, 164, 128, 168)
    p.put(sill, "cloth", 4)
    p.put(sill & (yy == 164), "cloth", 5)
    p.put(sill & (yy == 167), "cloth", 1)
    for a, b in ((44, 68), (72, 96), (100, 122)):                         # stall riser: three sunk panels
        pn = p.R(a, 171, b, GL - 3)
        p.put(pn, "cloth", 1)
        p.put(pn & ((yy == 171) | (xx == b - 1)), "cloth", 0)
        p.put(pn & ((yy == GL - 4) | (xx == a)), "cloth", 3)
    L(43, 129, 80, 35)

    # ---- door
    p.put(p.R(138, 123, 174, GL), "wood", 4)
    p.put(p.R(138, 123, 139, GL), "wood", 6)
    p.put(p.R(173, 123, 174, GL), "wood", 2)
    p.put(p.R(138, 123, 174, 124), "wood", 2)
    tr = p.R(141, 126, 171, 132)
    p.put(tr, "glow", 5, "dawn")
    p.put(tr, "glass", 3, "sunrise")
    p.put(p.R(155, 126, 157, 132), "wood", 3)
    leaf = p.R(141, 134, 171, GL)
    p.put(leaf, "wood", 3)
    p.put(leaf & (xx >= 169), "wood", 4)
    p.mottle(leaf, 510, t=0.6)
    dg = p.R(146, 139, 166, 161)
    p.put(dilate(dg) & leaf & ~dg, "wood", 2)
    p.put(dg, "glow", 4, "dawn")
    p.put(dg & (yy < 148), "glow", 5, "dawn")
    p.put(dg, "glass", 2, "sunrise")
    p.put(p.P([(146, 155), (162, 139), (166, 139), (166, 142), (146, 161)]) & dg, "glass", 4, "sunrise")
    p.put(p.R(155, 139, 157, 161), "wood", 2)
    plq = p.R(148, 150, 154, 154)                                         # the little plaque hung inside the glass
    p.put(plq, "cream", 2)
    p.put(p.R(149, 151, 153, 152), "cab", 1)
    pan = p.R(146, 165, 166, 178)
    p.put(pan, "wood", 2)
    p.put(pan & ((yy == 165) | (xx == 165)), "wood", 1)
    p.put(pan & ((yy == 177) | (xx == 146)), "wood", 4)
    p.put(p.R(166, 160, 168, 165), "lamp", 1)                             # brass handle
    step = p.R(135, 179, 177, 185)
    p.put(step, "stone", 5)
    p.put(step & (yy == 179), "stone", 7)
    p.put(step & (yy >= 182), "stone", 3)
    p.put(p.R(174, 179, 177, 185), "stone", 6)
    L(146, 139, 20, 22)

    # ---- wall lamp right of the door
    p.put(p.R(178, 127, 186, 129), "iron", 1)
    p.put(p.R(178, 127, 186, 128), "iron", 3)
    p.put(p.P([(179, 132), (183.5, 128), (188, 132)]), "iron", 1)
    lg = p.R(180, 132, 187, 140)
    p.put(lg, "lamp", 2, "dawn")
    p.put(p.R(182, 134, 185, 139), "lamp", 3, "dawn")
    p.put(lg, "lamp", 0, "sunrise")
    p.put(p.R(185, 132, 187, 140), "lamp", 2, "sunrise")
    p.put(p.R(180, 140, 187, 142), "iron", 1)
    p.put(p.R(179, 132, 180, 141), "iron", 1)
    p.put(p.R(187, 132, 188, 141), "iron", 3)
    L(180, 132, 7, 8)

    # ---- a box of books on a trestle
    for a in (179, 194):
        leg = p.R(a, 168, a + 2, GL)
        p.put(leg, "wood", 2)
        p.put(p.R(a + 1, 168, a + 2, GL), "wood", 4)
    p.put(p.L(180, GL - 2, 195, 170), "wood", 2)
    cr = p.R(176, 157, 198, 169)
    bx = 178
    for w, h, mat, lv in ((3, 9, "cream", 2), (2, 7, "cloth", 4), (3, 10, "roof", 4), (2, 8, "moss", 2), (3, 9, "cream", 1),
                          (3, 6, "cab", 3), (2, 10, "screen", 0)):         # spines standing in the box
        m = p.R(bx, 158 - h, bx + w, 158)
        p.put(m, mat, lv)
        p.add(m & (xx == bx + w - 1), 1)
        bx += w
    bk = p.R(177, 146, 197, 158) & ~p.is_mat("cloth", "wall", "wallwarm", "wallhot")
    p.add(bk & ~sh(bk, 0, 1), 1)                                          # their top edges catch the light
    p.put(cr, "wood", 3)
    p.put(cr & (yy >= 166), "wood", 2)
    p.put(cr & ((xx < 178) | (xx >= 196)), "wood", 4)
    p.put(cr & (yy == 157), "wood", 6)
    p.put(cr & (xx == 197), "wood", 6)
    p.put(cr & (xx == 176), "wood", 2)
    p.put(p.R(183, 161, 191, 165), "cream", 1)                            # a blank price card
    p.put(p.R(183, 161, 191, 162), "cream", 2)
    box = cr | p.R(177, 148, 197, 158)

    # ---- hanging sign on the left (no lettering: an open book)
    p.put(p.R(2, 64, 30, 66), "iron", 1)
    p.put(p.R(2, 64, 30, 65), "iron", 3)
    p.put(p.L(30, 78, 18, 66), "iron", 1)
    for cx in (8, 22):
        p.put(p.R(cx, 66, cx + 1, 71), "iron", 2)
    board = p.R(3, 71, 28, 97)
    p.put(board, "wood", 3)
    p.put(board & ((yy == 71) | (xx == 27)), "wood", 5)
    p.put(board & ((yy == 96) | (xx == 3)), "wood", 1)
    p.put(p.R(5, 73, 26, 95), "cloth", 2)
    lp = p.P([(7, 79), (15, 82), (15, 91), (7, 88)])
    rp = p.P([(16, 82), (24, 79), (24, 88), (16, 91)])
    p.put(lp, "cream", 1)
    p.put(rp, "cream", 2)
    p.put(rp & ~sh(rp, 0, 1), "cream", 3)
    p.put(lp & ~sh(lp, 0, 1), "cream", 2)
    cover = (dilate(lp | rp) & ~(lp | rp)) & (yy > 84)
    p.put(cover & p.R(5, 73, 26, 95), "cab", 2)
    p.put(p.R(15, 81, 16, 92), "cab", 1)                                  # the gutter between the pages
    p.put(p.R(18, 90, 20, 94), "lamp", 1)                                 # a ribbon marker

    # ---- potted shrub at the left pilaster
    pot = p.P([(27, 168), (41, 168), (39, GL), (29, GL)])
    p.put(pot, "roof", 3)
    p.put(pot & (yy <= 169), "roof", 5)
    p.put(pot & (xx >= 38), "roof", 5)
    p.put(pot & (xx <= 29), "roof", 2)
    p.put(p.R(34, 156, 36, 168), "trunk", 2)
    p.put(p.R(35, 156, 36, 168), "trunk", 4)
    crown(p, [(29, 150, 5, 4), (32, 154, 6, 5), (39, 152, 7, 6), (35, 146, 7, 5), (41, 157, 4, 4)], "leafB", 511, base=3, drips=2)

    # ---- water stains under the sills
    for _ in range(18):
        ys, xs = np.nonzero(sh(sills, 0, 1) & ~sills & p.is_mat("wall"))
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        p.add(p.R(xs[i], ys[i], xs[i] + 2, ys[i] + int(r.integers(3, 8))) & p.is_mat("wall"), -1)

    # ---- dawn: lamp and window light spilling onto the wall and the paintwork
    nz = noise(BH, BW, 9, 9, 512, 1) * 1.2
    wallm = p.is_mat("wall", st="dawn")
    hard = p.is_mat("stone", "wood", "cloth", "iron", st="dawn")
    wallm = wallm & (yy < 104)                                            # the shop window's light stays below the cornice
    for cx, cy, rad in ((118, 82, 21), (83, 146, 52), (156, 150, 26), (183, 136, 34)):
        d = (np.hypot((xx + 0.5 - cx) * 0.9, (yy + 0.5 - cy) * 1.25) + nz) / rad
        if cy > 100:                                                      # (a small window upstairs lights its stone surround, not the wall)
            p.remat(wallm & (d < 1.0), "wallwarm", 0, "dawn")
            p.remat(wallm & (d < 0.52), "wallhot", 0, "dawn")
            p.add(wallm & (d < 0.26), 1, "dawn")
        p.add(hard & (d < 0.6), 1, "dawn")
    # ---- sunrise: low sun from the right
    flat = p.is_mat("wall", "wallwarm", "wallhot", st="sunrise")
    paint = p.is_mat("cloth", st="sunrise")
    p.cast(sills, flat, 5, slope=0.8)
    p.cast(surs, flat, 3, slope=0.3)
    p.cast(corn, paint, 4, slope=1.0)
    p.cast(lg, paint, 10, slope=0.3)
    p.cast(box, paint, 7, slope=0.2)
    p.cast(p.R(X1 - 8, 123, X1, GL), paint, 4, slope=0.0)
    return p
