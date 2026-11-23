"""Building 3: the music shop (Music).

A narrow, tall house with its gable to the street: a painted wooden shopfront (an upright piano
and a guitar in the lit window), a plastered first floor with an oriel window and a few dark
timbers, a round lit window in the gable; a hanging sign with a pair of notes, and a gramophone
standing on a crate outside. No lettering anywhere.

Local plan (BW 172 x BH 206, ground line GL = 202):
  walls      x 14-138; gable apex (76, 14), eaves y 62
  first floor y 62-128 (tie beam 62-67, oriel 74-123), bressummer y 128-134
  shopfront  y 134-202: window x 24-86 / y 147-187, door x 101-129 / y 152-202
"""
import numpy as np

from draw_bg import crown
from draw_main import G
from kit import Pix, noise, sh, dilate, drop_single, long_runs, STATES, ramp, lch
from pal import PAL

NAME = "music"
ID = "music"
X = 1180
BW, BH, GL = 172, 206, 202
DOOR = 115
STOP = (88, 144)
POOLS = [(55, 32), (115, 14)]
LABEL_Y = 116

EXTRA = {
    "dawn": {
        "paint": ramp(6, .150, .385, .040, .044, 238, 208),                  # the shopfront's old paint
        "brass": ramp(5, .19, .45, .030, .044, 236, 214),
    },
    "sunrise": {
        "paint": ramp(6, .37, .72, .040, .064, 152, 118),                    # a faded sage green, the one cool note
        "brass": ramp(5, .46, .86, .085, .125, 68, 96),
    },
}
P = {s: {**PAL[s], **EXTRA[s]} for s in STATES}


def draw(lights):
    p = Pix(BW, BH, P)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(401)
    OY = G - GL
    L = lambda x, y, w, h: lights.append(("main", X + x, OY + y, w, h))
    X0, X1, EV, AX, AY = 14, 138, 62, 76, 14

    # ================================================================== chimney (behind the roof)
    ch = p.R(28, 22, 42, 56)
    p.put(ch, "stone", 3)
    p.put(p.R(38, 22, 42, 56), "stone", 5)
    p.put(p.R(28, 22, 30, 56), "stone", 2)
    p.mottle(ch, 402, t=0.5)
    cap = p.R(26, 19, 44, 22)
    p.put(cap, "stone", 4)
    p.put(cap & (yy == 19), "stone", 6)
    p.put(cap & (yy == 21), "stone", 2)
    for px in (31, 37):                                                   # two pots
        p.put(p.R(px, 14, px + 4, 19), "roof", 3)
        p.put(p.R(px + 3, 14, px + 4, 19), "roof", 5)

    # ================================================================== plaster
    wall = p.P([(X0, EV), (AX, AY), (X1, EV), (X1, 134), (X0, 134)])
    p.put(wall, "wall", 3)
    n = noise(BH, BW, 30, 22, 403, 2)
    p.add(wall & (n > 0.42), 1)
    p.add(wall & (n < -0.46), -1)
    p.mottle(wall, 404, t=0.66)
    for cx, cy, k in ((30, 112, 3), (122, 78, 2)):                        # the stone showing through
        for _ in range(k):
            bx, by = cx + int(r.integers(-4, 5)), cy + int(r.integers(-5, 6))
            st = p.E(bx, by, r.uniform(2.4, 4.0), r.uniform(1.8, 2.8)) & wall
            p.put(st, "stone", int(r.integers(3, 6)))
            p.add(st & ~sh(st, 0, 1), 1)
            p.add(st & ~sh(st, 0, -1), -1)

    # ================================================================== timbers
    def beam(m, lv=3):
        m = m & (wall | p.R(X0 - 2, 128, X1 + 2, 134))
        p.put(m, "wood", lv)
        p.put(m & ~sh(m, 0, 1), "wood", lv + 1)                           # top face
        p.put(m & ~sh(m, 0, -1), "wood", lv - 1)
        p.put(m & ~sh(m, -1, 0) & sh(m, 1, 0), "wood", lv + 2)            # the face that looks at the sun
        return m

    timbers = beam(p.R(X0, EV, X1, EV + 5))                               # tie beam
    timbers |= beam(p.R(45, 0, 48, EV))                                   # gable posts
    timbers |= beam(p.R(104, 0, 107, EV))
    timbers |= beam(p.R(74, 0, 78, EV))                                   # king post (the round window sits on it)
    timbers |= beam(p.R(X0, EV + 5, X0 + 4, 128), 2)                      # corner posts
    timbers |= beam(p.R(X1 - 4, EV + 5, X1, 128), 4)
    timbers |= beam(p.P([(18, 126), (22, 126), (40, 90), (36, 90)]))      # braces
    timbers |= beam(p.P([(130, 126), (134, 126), (116, 90), (112, 90)]))
    timbers |= beam(p.R(X0, 88, 44, 91))                                  # rails the braces run up to
    timbers |= beam(p.R(108, 88, X1, 91))
    bres = p.R(X0 - 2, 128, X1 + 2, 134)                                  # bressummer over the shopfront
    p.put(bres, "wood", 2)
    p.put(bres & (yy == 128), "wood", 4)
    p.put(bres & (yy == 133), "wood", 1)
    p.put(p.R(X1 - 2, 128, X1 + 2, 134), "wood", 5)
    for bx in (30, 61, 92, 122):                                          # the joist ends that carry it
        p.put(p.R(bx, 130, bx + 4, 133), "wood", 3)
        p.put(p.R(bx + 3, 130, bx + 4, 133), "wood", 5)

    # ================================================================== the gable's edges and the finial
    lb = p.P([(3, 63), (AX, 2), (AX, 12), (8, 69)])
    rb = p.P([(AX, 2), (149, 63), (144, 69), (AX, 12)])
    p.put(lb, "roof", 2)
    p.put(lb & ~sh(lb, 0, 1), "roof", 4)
    p.put(lb & ~sh(lb, 0, -1), "roof", 1)
    p.put(rb, "roof", 4)
    p.put(rb & ~sh(rb, 0, 1), "roof", 6)
    p.put(rb & ~sh(rb, 0, -1), "roof", 2)
    p.mottle((lb | rb) & sh(lb | rb, 0, 1) & sh(lb | rb, 0, -1), 405, t=0.6)
    for m_ in (lb, rb):                                                   # their shade on the plaster
        p.add(wall & ~timbers & sh(m_, 0, 2) & ~m_, -1)
        p.add(wall & ~timbers & sh(m_, 0, 4) & ~m_, -1)
    p.put(p.R(75, 0, 77, 5), "iron", 2)
    p.put(p.R(76, 0, 77, 5), "iron", 4)
    p.put(p.E(76, 3, 2.3, 2.3), "iron", 2)
    p.put(p.R(76, 1, 78, 3), "iron", 4)

    # ================================================================== round window in the gable (lit)
    ocx, ocy = 76, 42
    ring = p.E(ocx, ocy, 11.5, 11.5)
    p.put(ring, "stone", 4)
    p.put(ring & (xx - yy > ocx - ocy + 5), "stone", 6)
    p.put(ring & (xx - yy < ocx - ocy - 6), "stone", 3)
    p.put(p.E(ocx, ocy, 9.2, 9.2), "wood", 2)
    og = p.E(ocx, ocy, 8.2, 8.2)
    p.put(og, "glow", 4, "dawn")
    p.put(og & (yy < ocy - 2), "glow", 5, "dawn")
    p.put(og, "glass", 2, "sunrise")
    p.put(og & (yy > ocy + 3), "glass", 1, "sunrise")
    p.put(og & (xx + yy > ocx + ocy - 7) & (xx + yy < ocx + ocy - 1), "glass", 4, "sunrise")
    p.put(p.R(ocx - 1, ocy - 9, ocx + 1, ocy + 9) & og, "wood", 2)
    p.put(p.R(ocx - 9, ocy - 1, ocx + 9, ocy + 1) & og, "wood", 2)
    L(ocx - 8, ocy - 8, 16, 16)

    # ================================================================== oriel window on the first floor
    orf = p.P([(45, 82), (52, 74), (100, 74), (107, 82)])
    p.put(orf, "roof", 3)
    p.add(orf & (xx > 86), 1)
    p.put(orf & (yy == 74), "roof", 5)
    p.put(orf & (yy == 81), "roof", 1)
    body = p.R(48, 82, 104, 118)
    p.put(body, "wood", 4)
    p.put(p.R(102, 82, 104, 118), "wood", 6)
    p.put(p.R(48, 82, 50, 118), "wood", 2)
    p.put(p.R(48, 82, 104, 84), "wood", 2)
    for a, b in ((52, 66), (69, 83), (86, 100)):
        pane = p.R(a, 86, b, 113)
        p.put(pane, "glass", 1, "dawn")
        p.put(pane & (yy > 104), "glass", 0, "dawn")
        p.put(p.P([(a, 99), (a + 13, 86), (b, 86), (b, 90), (a, 104)]) & pane, "glass", 2, "dawn")
        p.put(pane, "glass", 2, "sunrise")
        p.put(pane & (yy > 104), "glass", 1, "sunrise")
        p.put(p.P([(a, 100), (a + 14, 86), (b, 86), (b, 92), (a, 108)]) & pane, "glass", 4, "sunrise")
        p.put(p.R(a, 94, b, 95), "wood", 3)
    osill = p.R(46, 113, 106, 118)
    p.put(osill, "wood", 5)
    p.put(osill & (yy == 113), "wood", 6)
    p.put(osill & (yy >= 116), "wood", 2)
    corb = p.P([(50, 118), (102, 118), (95, 125), (57, 125)])
    p.put(corb, "wood", 3)
    p.put(corb & (yy == 124), "wood", 1)
    p.put(corb & (xx > 92), "wood", 4)
    oriel = orf | body | osill | corb

    # ================================================================== shopfront: painted wood
    front = p.R(X0, 134, X1, GL)
    p.put(front, "paint", 2)
    p.mottle(front, 406, t=0.68)
    corn = p.R(X0 - 2, 134, X1 + 2, 138)
    p.put(corn, "paint", 4)
    p.put(corn & (yy == 134), "paint", 5)
    p.put(corn & (yy == 137), "paint", 1)
    fas = p.R(X0, 138, X1, 144)
    p.put(fas, "paint", 3)
    p.put(p.R(20, 139, 132, 143), "paint", 2)                             # a long sunk panel where a name would go; left blank
    p.put(p.R(20, 142, 132, 143), "paint", 4)
    p.put(p.R(20, 139, 132, 140), "paint", 1)
    for a, b in ((X0, X0 + 6), (90, 96), (X1 - 6, X1)):                   # pilasters
        pil = p.R(a, 144, b, GL)
        p.put(pil, "paint", 3)
        p.put(p.R(b - 1, 144, b, GL), "paint", 5)
        p.put(p.R(a, 144, a + 1, GL), "paint", 1)
        p.put(p.R(a - 1, 144, b + 1, 147), "paint", 4)
        p.put(p.R(a - 1, 146, b + 1, 147), "paint", 1)
    for a, b in ((24, 53), (57, 86)):                                     # panels under the window
        pan = p.R(a, 193, b, 199)
        p.put(pan, "paint", 1)
        p.put(pan & ((yy == 193) | (xx == b - 1)), "paint", 0)
        p.put(pan & ((yy == 198) | (xx == a)), "paint", 3)
    base = p.R(X0 - 1, 199, X1 + 1, GL)
    p.put(base, "stone", 3)
    p.put(base & (yy == 199), "stone", 5)

    # ---- the shop window: a lit room, a piano, a guitar on the wall
    p.put(p.R(21, 144, 89, 191), "wood", 3)
    p.put(p.R(21, 144, 22, 191), "wood", 5)
    p.put(p.R(88, 144, 89, 191), "wood", 1)
    room = p.R(24, 147, 86, 187)
    p.put(room, "glow", 3)
    p.put(room & (yy < 177), "glow", 4)
    p.put(room & (yy < 163), "glow", 5)
    C = lambda m, mat, lv, st=None: p.put(m & room, mat, lv, st)
    C(p.R(30, 150, 40, 158), "glow", 3)                                   # a framed picture
    C(p.R(31, 151, 39, 157), "cab", 3)
    C(p.R(31, 154, 39, 157), "cab", 2)
    # pendant lamp
    C(p.R(63, 147, 64, 151), "cab", 1)
    C(p.E(63.5, 157, 10, 4.5), "glow", 6)
    C(p.P([(58, 155), (61, 151), (66, 151), (69, 155)]), "cab", 1)
    C(p.R(61, 155, 66, 156), "glow", 6)
    # upright piano
    C(p.R(27, 163, 59, 186), "cab", 1)
    C(p.R(56, 163, 59, 186), "cab", 3)
    C(p.R(27, 163, 28, 186), "cab", 0)
    C(p.R(26, 161, 60, 164), "cab", 2)                                    # lid
    C(p.R(26, 161, 60, 162), "cab", 4)
    C(p.R(37, 155, 49, 161), "cream", 1)                                  # the open score
    C(p.R(43, 155, 44, 161), "cab", 3)
    C(p.R(38, 157, 42, 158) | p.R(45, 158, 48, 159), "cab", 3)
    C(p.R(25, 173, 61, 177), "cab", 2)                                    # key shelf
    C(p.R(27, 173, 59, 175), "cream", 2)                                  # the keys
    for kx, kw in ((29, 2), (33, 3), (39, 2), (43, 3), (49, 2), (53, 3)):
        C(p.R(kx, 173, kx + kw, 174), "cab", 0)
    C(p.R(27, 175, 59, 176), "cab", 4)
    C(p.R(29, 178, 57, 184), "cab", 0)                                    # lower panel
    C(p.R(40, 182, 42, 186) | p.R(45, 182, 47, 186), "brass", 3)          # pedals
    # stool
    C(p.R(63, 177, 72, 179), "cab", 2)
    C(p.R(65, 179, 66, 186) | p.R(69, 179, 70, 186), "cab", 1)
    # guitar hung on the wall
    C(p.R(76, 150, 80, 154), "cab", 1)
    C(p.R(77, 154, 79, 165), "cab", 1)
    gb = p.E(78, 167, 3.6, 3.4) | p.E(78, 173, 5.0, 4.6)
    C(gb, "cab", 3)
    C(gb & (xx >= 81), "cab", 4)
    C(gb & (xx <= 74), "cab", 2)
    C(p.E(78, 170.5, 1.6, 1.6), "cab", 0)
    C(p.R(76, 175, 80, 176), "cab", 1)
    C(room & (yy >= 185), "cab", 2)                                       # floor
    mull = p.R(72, 147, 74, 187)                                          # one slim mullion
    p.put(mull, "wood", 2)
    p.put(p.R(72, 147, 73, 187), "wood", 4)
    for a, b, c, d in ((24, 180, 52, 147), (60, 187, 86, 156)):           # sunrise: the sky slides across the glass
        p.add(p.P([(a, b), (c, d), (c + 11, d), (a + 11, b)]) & room, 2, "sunrise")
    wsill = p.R(19, 187, 91, 191)
    p.put(wsill, "stone", 5)
    p.put(wsill & (yy == 187), "stone", 7)
    p.put(wsill & (yy == 190), "stone", 3)
    L(24, 147, 62, 40)

    # ---- the door
    p.put(p.R(98, 141, 132, GL), "wood", 4)
    p.put(p.R(98, 141, 99, GL), "wood", 6)
    p.put(p.R(131, 141, 132, GL), "wood", 2)
    p.put(p.R(98, 141, 132, 142), "wood", 2)
    tr = p.R(101, 144, 129, 150)
    p.put(tr, "glow", 5, "dawn")
    p.put(tr, "glass", 3, "sunrise")
    p.put(p.R(114, 144, 116, 150), "wood", 3)
    leaf = p.R(101, 152, 129, GL)
    p.put(leaf, "paint", 1)
    p.put(leaf & (xx >= 127), "paint", 2)
    dg = p.R(107, 157, 123, 180)
    p.put(dilate(dg) & leaf & ~dg, "paint", 0)
    p.put(dg, "glow", 4, "dawn")
    p.put(dg & (yy < 166), "glow", 5, "dawn")
    p.put(dg, "glass", 2, "sunrise")
    p.put(p.P([(107, 174), (121, 157), (123, 157), (123, 162), (107, 180)]) & dg, "glass", 4, "sunrise")
    p.put(p.R(114, 157, 116, 180), "paint", 0)
    pan = p.R(107, 185, 123, 198)
    p.put(pan, "paint", 0)
    p.put(pan & ((yy == 197) | (xx == 107)), "paint", 2)
    p.put(p.R(125, 178, 127, 184), "brass", 3)
    step = p.R(95, 199, 135, 205)
    p.put(step, "stone", 5)
    p.put(step & (yy == 199), "stone", 7)
    p.put(step & (yy >= 202), "stone", 3)
    p.put(p.R(132, 199, 135, 205), "stone", 6)
    L(107, 157, 16, 23)

    # ---- lantern on the pilaster between window and door
    p.put(p.R(92, 148, 94, 151), "iron", 1)
    p.put(p.R(89, 150, 97, 152), "iron", 1)
    p.put(p.R(89, 150, 97, 151), "iron", 3)
    lg = p.R(90, 152, 96, 160)
    p.put(lg, "lamp", 2, "dawn")
    p.put(p.R(92, 154, 94, 159), "lamp", 3, "dawn")
    p.put(lg, "lamp", 0, "sunrise")
    p.put(p.R(94, 152, 96, 160), "lamp", 2, "sunrise")
    p.put(p.R(90, 160, 96, 161), "iron", 1)
    p.put(p.R(92, 161, 94, 162), "iron", 1)
    L(90, 152, 6, 8)

    # ================================================================== hanging sign: a pair of notes
    p.put(p.R(X1, 94, 169, 96), "iron", 1)
    p.put(p.R(X1, 94, 169, 95), "iron", 3)
    p.put(p.L(X1, 108, 151, 96), "iron", 1)
    for cx in (146, 163):
        p.put(p.R(cx, 96, cx + 1, 101), "iron", 2)
    board = p.R(142, 101, 169, 131)
    p.put(board, "wood", 3)
    p.put(board & ((yy == 101) | (xx == 168)), "wood", 5)
    p.put(board & ((yy == 130) | (xx == 142)), "wood", 1)
    face = p.R(144, 103, 167, 129)
    p.put(face, "cloth", 1)
    note = p.E(150.5, 122.5, 3.4, 2.7) | p.E(160.5, 120.5, 3.4, 2.7) | p.R(152, 109, 154, 123) | p.R(162, 107, 164, 121) \
        | p.P([(152, 109), (164, 107), (164, 111), (152, 113)])
    note &= face
    p.put(note, "cream", 2)
    p.put(note & ~sh(note, -1, 0), "cream", 3)

    # ================================================================== outside: a gramophone on a crate, a barrel of plants
    cx0, cy0, cw, chh = 143, 184, 20, 18
    cr = p.R(cx0, cy0, cx0 + cw, cy0 + chh)
    p.put(cr, "wood", 3)
    p.put(cr & ((yy - cy0) % 5 == 4), "wood", 2)
    fr = cr & ((xx < cx0 + 2) | (xx >= cx0 + cw - 2) | (yy < cy0 + 2) | (yy >= cy0 + chh - 2))
    p.put(fr, "wood", 4)
    p.put(cr & (yy == cy0), "wood", 6)
    p.put(cr & (xx >= cx0 + cw - 1), "wood", 6)
    p.put(cr & (xx == cx0), "wood", 2)
    p.put(p.L(cx0 + 2, cy0 + chh - 3, cx0 + cw - 3, cy0 + 2, 2) & cr, "wood", 4)
    gbx = p.R(145, 176, 159, 184)                                         # the gramophone's box
    p.put(gbx, "wood", 4)
    p.put(gbx & (yy == 176), "wood", 6)
    p.put(gbx & (xx >= 158), "wood", 6)
    p.put(gbx & (xx == 145), "wood", 2)
    p.put(gbx & (yy == 183), "wood", 2)
    p.put(p.R(159, 179, 163, 180) | p.R(162, 177, 163, 180), "iron", 3)   # crank
    p.put(p.R(147, 174, 157, 176), "iron", 1)                             # turntable
    # the horn: a thin neck, a cone, and the bell's mouth turned up toward the sunrise
    th = np.radians(32)
    mcx, mcy = 163.0, 160.0

    def bell(ru, rv, ox=0.0, oy=0.0):
        dx, dy = xx + 0.5 - mcx - ox, yy + 0.5 - mcy - oy
        u = dx * np.cos(th) - dy * np.sin(th)                             # along the horn's axis (foreshortened)
        v = dx * np.sin(th) + dy * np.cos(th)
        return (u / ru) ** 2 + (v / rv) ** 2 <= 1.0

    neck = p.L(150, 174, 150, 169, 2) | p.L(150, 169, 153, 166, 2)
    ex, ey = np.sin(th) * 9.0, np.cos(th) * 9.0
    cone = p.P([(151, 165), (154, 168), (mcx + ex, mcy + ey), (mcx - ex, mcy - ey)])
    mouth = bell(4.2, 9.6)
    p.put(neck, "brass", 2)
    p.put(neck & ~sh(neck, -1, 0), "brass", 3)
    p.put(cone, "brass", 2)
    p.put(cone & ~sh(cone, 0, -1), "brass", 1)                            # the underside
    p.put(mouth, "brass", 4)                                              # the rim
    p.put(bell(3.0, 8.2, 0.4, -0.3), "brass", 3)
    p.put(bell(1.7, 5.4, -0.4, 0.3), "brass", 1)                          # the throat
    hb = neck | cone | mouth

    brl = p.P([(1, 186), (13, 186), (14, 194), (13, GL), (1, GL), (0, 194)])
    p.put(brl, "wood", 3)
    p.put(brl & (xx >= 11), "wood", 5)
    p.put(brl & (xx <= 2), "wood", 2)
    for hy in (188, 197):
        p.put(brl & (yy >= hy) & (yy < hy + 2), "iron", 2)
        p.put(brl & (yy == hy) & (xx >= 10), "iron", 4)
    crown(p, [(3, 182, 5, 4), (8, 177, 6, 6), (12, 183, 5, 4), (6, 172, 4, 4)], "leafB", 407, base=3, drips=3)

    # ================================================================== stains under the sills
    sills = osill | wsill | p.R(X0, EV, X1, EV + 5)
    for _ in range(18):
        ys, xs = np.nonzero(sh(sills | corb, 0, 1) & ~(sills | corb) & p.is_mat("wall"))
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        p.add(p.R(xs[i], ys[i], xs[i] + 2, ys[i] + int(r.integers(4, 12))) & p.is_mat("wall"), -1)

    # ================================================================== dawn: light spilling out
    nz = noise(BH, BW, 9, 9, 408, 1) * 1.2
    wallm = p.is_mat("wall", st="dawn")
    hard = p.is_mat("stone", "wood", "paint", "iron", "roof", st="dawn") & ~room
    for cx, cy, rad in ((ocx, ocy, 24), (55, 166, 46), (93, 156, 24)):
        d = (np.hypot(xx + 0.5 - cx, (yy + 0.5 - cy) * 1.15) + nz) / rad
        if cy < 100:
            p.remat(wallm & (d < 1.0), "wallwarm", 0, "dawn")
            p.remat(wallm & (d < 0.6), "wallhot", 0, "dawn")
        p.add(hard & (d < 0.62), 1, "dawn")

    # ================================================================== sunrise: shadows thrown to the left
    flat = p.is_mat("wall", "wallwarm", "wallhot", st="sunrise")
    p.cast(oriel, flat, 9, slope=0.5)
    p.cast(ring, flat, 4, slope=0.5)
    p.cast(timbers, flat, 2, slope=0.5)
    p.cast(board, flat | p.is_mat("wood", st="sunrise"), 8, slope=0.4)
    paintm = p.is_mat("paint", st="sunrise")
    p.cast(lg, paintm, 6, slope=0.3)
    p.cast(p.R(98, 141, 132, GL), paintm, 3, slope=0.2)
    p.cast(bres | corn, paintm, 3, slope=1.0)
    return p
