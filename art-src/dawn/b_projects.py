"""Building 2: the workshop (Projects).

A low, wide maker's shed: a boarded hall with a tin roof and a glazed roof monitor, its big
sliding door half open onto a lit room (bench, monitor, desk lamp, tools); a plastered lean-to
on the right with the door the character walks to; an aerial, a flue and a dish on the roofs;
a hanging sign with a gear. No lettering anywhere.

Local plan (BW 236 x BH 154, ground line GL = 150):
  hall     x 12-158, boarded wall y 60-150, tin roof y 44-62, monitor y 23-44
  opening  x 58-116, y 86-147 (the room); the door leaf hangs over x 20-58
  lean-to  x 158-206, roof sloping down to the right, door x 169-197 / y 91-150
"""
import numpy as np

from draw_bg import crown
from draw_main import window, G
from kit import Pix, noise, sh, dilate, drop_single, long_runs, STATES, ramp, lch
from pal import PAL, LAMP_D

NAME = "projects"
ID = "projects"
X = 800
BW, BH, GL = 236, 154, 150
DOOR = 183
STOP = (154, 214)
POOLS = [(87, 32), (183, 14)]
LABEL_Y = 34


def _warm(cols, t):
    return [tuple(int(round(c[i] + (LAMP_D[i] - c[i]) * t)) for i in range(3)) for c in cols]


EXTRA = {
    "dawn": {
        "tin": ramp(7, .125, .385, .030, .034, 250, 226),                           # corrugated roof sheets
        "woodwarm": _warm(ramp(7, .15, .40, .034, .038, 260, 240), 0.24),            # boards inside the lamp's reach
        "woodhot": _warm(ramp(7, .20, .47, .034, .038, 258, 238), 0.42),
    },
    "sunrise": {
        "tin": ramp(7, .40, .78, .034, .082, 64, 94),
        "woodwarm": PAL["sunrise"]["wood"],
        "woodhot": PAL["sunrise"]["wood"],
    },
}
P = {s: {**PAL[s], **EXTRA[s]} for s in STATES}


def draw(lights):
    p = Pix(BW, BH, P)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(301)
    OY = G - GL
    L = lambda x, y, w, h: lights.append(("main", X + x, OY + y, w, h))
    HX0, HX1 = 12, 158

    # ================================================================== the hall: boarded wall
    hall = p.R(HX0, 60, HX1, GL)
    p.put(hall, "wood", 3)
    n = noise(BH, BW, 30, 26, 302, 2)
    p.add(hall & (n > 0.50), 1)
    p.add(hall & (n < -0.54), -1)
    x = HX0 + int(r.integers(7, 12))
    while x < HX1 - 5:                                                    # board edges: some run the full height, some do not
        w = int(r.integers(8, 15))
        y0 = 60 if r.random() < 0.5 else 60 + int(r.integers(6, 44))
        y1 = 138 if r.random() < 0.5 else 138 - int(r.integers(6, 44))
        if y1 - y0 > 12:
            p.add(p.R(x, y0, x + 1, y1) & hall, -1)
        if r.random() < 0.22:
            p.add(p.R(x + 1, 60, x + w, 138) & hall, int(r.choice([-1, 1])))
        x += w
    p.mottle(hall, 303, t=0.74)
    p.add(hall & (yy < 69), -1)                                           # under the eave
    p.add(hall & (yy < 66), -1)
    p.put(p.R(HX1 - 3, 60, HX1, GL), "wood", 5)                           # the corner post that faces the sun
    p.put(p.R(HX1 - 1, 60, HX1, GL), "wood", 6)
    p.put(p.R(HX0, 60, HX0 + 2, GL), "wood", 2)
    pl = p.R(HX0 - 1, 138, HX1 + 1, GL)                                   # stone footing
    p.put(pl, "stone", 3)
    p.put(pl & (yy == 138), "stone", 5)
    p.put(pl & (yy >= 147), "stone", 2)
    p.put(p.R(HX1 - 3, 138, HX1 + 1, GL), "stone", 5)
    x = HX0 + int(r.integers(4, 16))
    while x < HX1:
        p.add(p.R(x, 140 + int(r.integers(0, 2)), x + 1, 148 - int(r.integers(0, 3))), -1)
        x += int(r.integers(16, 34))
    p.mottle(pl & (yy > 138), 304, t=0.5)

    # ================================================================== the lean-to: plaster
    lean = p.P([(HX1, 70), (206, 77), (206, GL), (HX1, GL)])
    p.put(lean, "wall", 3)
    n2 = noise(BH, BW, 26, 20, 305, 2)
    p.add(lean & (n2 > 0.42), 1)
    p.add(lean & (n2 < -0.46), -1)
    p.mottle(lean, 306, t=0.66)
    p.put(p.R(204, 76, 206, GL) & lean, "wall", 6)                        # sunward corner
    for cx, cy, k in ((163, 132, 3),):                      # the stone showing through
        for _ in range(k):
            bx, by = cx + int(r.integers(-3, 4)), cy + int(r.integers(-6, 7))
            st = p.E(bx, by, r.uniform(2.4, 4.0), r.uniform(1.8, 2.8)) & lean
            p.put(st, "stone", int(r.integers(3, 6)))
            p.add(st & ~sh(st, 0, 1), 1)
            p.add(st & ~sh(st, 0, -1), -1)
    lp = p.R(HX1, 140, 207, GL)
    p.put(lp, "stone", 3)
    p.put(lp & (yy == 140), "stone", 5)
    p.put(lp & (yy >= 147), "stone", 2)
    p.put(p.R(203, 140, 207, GL), "stone", 5)
    p.mottle(lp & (yy > 140), 307, t=0.5)

    # ================================================================== roofs
    # flue (behind the roof)
    fl = p.R(22, 20, 28, 47)
    p.put(fl, "tin", 2)
    p.put(p.R(26, 20, 28, 47), "tin", 4)
    p.put(p.R(22, 20, 23, 47), "tin", 1)
    p.put(p.R(21, 31, 29, 33), "tin", 3)
    p.put(p.R(21, 31, 29, 32), "tin", 5)
    cone = p.P([(18, 20), (25, 13), (32, 20)]) | p.R(18, 19, 32, 21)
    p.put(cone, "tin", 2)
    p.put(cone & (xx >= 25) & (yy < 19), "tin", 4)
    p.put(p.R(18, 20, 32, 21), "tin", 1)
    p.put(p.R(23, 21, 27, 23), "tin", 0)

    roof = p.P([(5, 62), (13, 44), (157, 44), (165, 62)])
    p.put(roof, "tin", 2)
    p.add(roof & (xx > 104 + (yy - 44) * 0.4), 1)
    p.add(roof & (xx > 150 + (yy - 44) * 0.4), 1)
    x = 9 + int(r.integers(8, 16))
    while x < 160:                                                        # sheet laps, unevenly spaced, a sheet or two a step off
        w = int(r.integers(13, 24))
        p.add(p.R(x, 45, x + 1, 62) & roof, -1)
        if r.random() < 0.3:
            p.add(p.R(x + 1, 45, x + w, 62) & roof, int(r.choice([-1, 1])))
        x += w
    p.mottle(roof, 308, t=0.62)
    rn = noise(BH, BW, 9, 5, 309, 2)
    rust = drop_single(roof & (yy > 52) & (xx < 120) & (rn > 0.34))
    p.put(rust, "roof", 3)
    p.put(drop_single(roof & (yy > 56) & (xx < 100) & (rn > 0.2)), "roof", 2)
    p.put(roof & (yy == 44), "tin", 5)
    p.put(p.R(22, 44, 28, 49), "tin", 1)                                  # the flue's foot in its own shade
    gut = p.R(4, 62, 166, 65)
    p.put(gut, "iron", 2)
    p.put(gut & (yy == 62), "iron", 4)
    p.put(gut & (yy == 64), "iron", 1)
    p.put(p.R(162, 62, 166, 65), "iron", 4)

    # the monitor: a raised strip of glazing along the ridge
    mon = p.R(42, 29, 130, 45)
    p.put(mon, "wood", 2)
    p.put(p.R(127, 29, 130, 45), "wood", 5)
    p.put(p.R(42, 29, 44, 45), "wood", 1)
    p.put(p.R(42, 43, 130, 45), "wood", 1)
    for i in range(5):
        a = 46 + i * 16
        pane = p.R(a, 32, a + 13, 42)
        p.put(pane, "glow", 2 + (i in (1, 2)), "dawn")
        p.put(pane & (yy < 35), "glow", 3 + (i in (1, 2)), "dawn")
        p.put(pane, "glass", 2, "sunrise")
        p.put(pane & (yy > 38), "glass", 1, "sunrise")
        p.put(p.P([(a, 39), (a + 7, 32), (a + 12, 32), (a, 44)]) & pane, "glass", 4, "sunrise")
    mr = p.P([(36, 30), (41, 23), (131, 23), (136, 30)])
    p.put(mr, "tin", 3)
    p.add(mr & (xx > 100), 1)
    p.put(mr & (yy == 23), "tin", 6)
    p.put(mr & (yy == 29), "tin", 1)
    p.add(mon & (yy < 32), -1)
    L(46, 32, 38, 10)
    L(86, 32, 38, 10)

    # aerial on the monitor roof: mast, boom, four rods of unequal length
    p.put(p.R(112, 4, 114, 23), "iron", 2)
    p.put(p.R(113, 4, 114, 23), "iron", 4)
    p.put(p.R(100, 8, 127, 9), "iron", 3)
    for ax, ah in ((101, 5), (107, 4), (118, 3), (126, 2)):
        p.put(p.R(ax, 8 - ah, ax + 1, 9 + ah), "iron", 3)
    p.put(p.L(113, 14, 121, 23), "iron", 1)                               # stay

    # lean-to roof, sloping down to the right
    lr = p.P([(154, 63), (211, 71), (211, 78), (154, 70)])
    p.put(lr, "tin", 3)
    p.add(lr & (xx > 190), 1)
    top = lr & ~sh(lr, 0, 1)
    p.put(top, "tin", 6)
    p.put(lr & ~sh(lr, 0, -1), "tin", 1)
    for sx in (171, 186, 200):
        p.add(p.R(sx, 62, sx + 1, 80) & lr & ~top, -1)
    p.put(p.R(209, 70, 211, 78) & lr, "tin", 6)
    p.add(lean & sh(lr, 0, 2) & ~lr, -1)                                  # its shade on the plaster
    p.add(lean & sh(lr, 0, 4) & ~lr, -1)
    # the dish
    p.put(p.R(193, 58, 195, 69), "iron", 2)
    dish = p.E(196, 54, 4.6, 7.0) & (xx - 196 < (yy - 54) * 0.25 + 2.2)
    p.put(dish, "cream", 1)
    p.put(dish & (xx <= 193), "cream", 0)
    p.put(dish & ~sh(dish, -1, 0), "cream", 3)
    p.put(p.L(197, 54, 203, 50), "iron", 3)
    p.put(p.R(203, 49, 205, 51), "iron", 4)

    # ================================================================== the big sliding door and the room behind it
    RX0, RX1, RY0, RY1 = 58, 116, 86, 147
    p.put(p.R(RX0 - 2, RY0 - 3, RX1 + 3, GL), "wood", 2)                  # the opening's frame
    p.put(p.R(RX1, RY0 - 3, RX1 + 3, GL), "wood", 4)
    p.put(p.R(RX1 + 2, RY0 - 3, RX1 + 3, GL), "wood", 5)
    room = p.R(RX0, RY0, RX1, RY1)
    p.put(room, "glow", 3)
    p.put(room & (yy < 132), "glow", 4)
    p.put(room & (yy < 112), "glow", 5)
    C = lambda m, mat, lv, st=None: p.put(m & room, mat, lv, st)
    # shelves on the back wall, things standing on them
    for sy, items in ((107, ((60, 8, 5, 1), (67, 5, 7, 3), (74, 9, 6, 2))), (119, ((61, 6, 6, 2), (69, 4, 4, 1), (75, 7, 7, 3)))):
        C(p.R(59, sy, 85, sy + 2), "cab", 2)
        C(p.R(59, sy, 85, sy + 1), "cab", 3)
        for ix, ih, iw, lv in items:
            C(p.R(ix, sy - ih, ix + iw, sy), "cab", lv)
            C(p.R(ix + iw - 1, sy - ih, ix + iw, sy), "cab", min(4, lv + 1))
    # a board of tools on the right
    C(p.R(99, 100, 115, 122), "glow", 2)
    C(p.R(101, 103, 103, 106) | p.R(102, 106, 103, 117), "cab", 1)        # spanner
    C(p.R(105, 104, 111, 107) | p.R(107, 107, 109, 118), "cab", 1)        # hammer
    C(p.P([(112, 104), (115, 104), (115, 119), (113, 119)]), "cab", 2)    # square
    # pendant lamp
    C(p.R(88, RY0, 89, 93), "cab", 1)
    C(p.E(88.5, 99, 11, 4.5), "glow", 6)
    C(p.P([(83, 97), (86, 93), (91, 93), (94, 97)]), "cab", 1)
    C(p.R(86, 97, 91, 98), "glow", 6)
    # the bench
    C(p.R(61, 127, 115, 130), "cab", 3)
    C(p.R(61, 127, 115, 128), "cab", 4)
    for lx in (63, 110):
        C(p.R(lx, 130, lx + 3, RY1), "cab", 1)
    C(p.R(63, 139, 113, 141), "cab", 1)
    C(p.R(95, 130, 109, 138), "cab", 2)
    C(p.R(95, 130, 109, 131), "cab", 1)
    C(p.R(100, 133, 104, 134), "glow", 5)
    # monitor on the bench: a little chart on the screen
    C(p.R(67, 111, 86, 125), "cab", 0)
    scr = p.R(68, 112, 85, 124) & room
    p.put(scr, "screen", 1)
    p.put(p.R(68, 112, 85, 114) & scr, "screen", 2)
    for bx, bh in ((70, 3), (74, 6), (78, 4), (82, 8)):
        p.put(p.R(bx, 123 - bh, bx + 2, 123) & scr, "screen", 0)
    C(p.R(75, 125, 79, 127), "cab", 1)
    # desk lamp, its head turned down at the bench
    C(p.R(101, 125, 107, 127), "cab", 1)
    C(p.L(104, 125, 107, 117, 1), "cab", 1)
    C(p.L(107, 117, 100, 112, 1), "cab", 1)
    C(p.P([(95, 112), (100, 109), (102, 113), (97, 116)]), "cab", 2)
    C(p.R(95, 115, 99, 117), "glow", 6)
    C(p.R(90, 124, 99, 127), "glow", 6)
    # stool, floor
    C(p.R(70, 134, 80, 136), "cab", 2)
    C(p.R(72, 136, 73, RY1) | p.R(77, 136, 78, RY1), "cab", 1)
    C(room & (yy >= 144), "cab", 2)
    p.add(p.P([(RX1, 144), (RX1, RY1), (84, RY1), (92, 144)]) & room, 2, "sunrise")   # the low sun reaches a little way in
    p.add(room & (xx < RX0 + 3), -1)                                      # shade behind the leaf's edge
    sill = p.R(RX0 - 2, RY1, RX1 + 3, GL)
    p.put(sill, "stone", 4)
    p.put(sill & (yy == RY1), "stone", 6)
    L(RX0, RY0, RX1 - RX0, RY1 - RY0)

    # the leaf, slid aside to the left
    leaf = p.R(20, 85, RX0 + 1, GL - 2)
    p.put(leaf, "wood", 4)
    for bx in range(27, RX0, 8):
        p.add(p.R(bx, 85, bx + 1, GL - 2) & leaf & (noise(BH, BW, 1, 7, 310 + bx, 1) > -0.45), -1)
    p.mottle(leaf, 311, t=0.62)
    for a, b in ((89, 94), (137, 142)):
        rail_ = p.R(20, a, RX0 + 1, b)
        p.put(rail_, "wood", 5)
        p.put(rail_ & (yy == a), "wood", 6)
        p.put(rail_ & (yy == b - 1), "wood", 2)
    br = p.L(23, 136, 55, 95, 3) & leaf
    p.put(br, "wood", 5)
    p.put(br & ~sh(br, 0, 1), "wood", 6)
    p.put(br & ~sh(br, 0, -1), "wood", 2)
    p.put(p.R(20, 85, 21, GL - 2), "wood", 2)
    p.put(p.R(RX0, 85, RX0 + 1, GL - 2), "wood", 6)
    p.add(p.R(RX0 - 2, 85, RX0 + 1, GL - 2), 1, "dawn")                   # its edge catches the room's light
    p.put(p.R(52, 112, 54, 122), "iron", 3)                               # pull handle
    p.put(p.R(20, GL - 2, RX0 + 1, GL), "iron", 0)
    # the rail it hangs from
    rail = p.R(15, 80, 122, 83)
    p.put(rail, "iron", 1)
    p.put(rail & (yy == 80), "iron", 3)
    for hx in (26, 48):
        p.put(p.R(hx, 83, hx + 5, 87), "iron", 2)
        p.put(p.R(hx + 4, 83, hx + 5, 87), "iron", 4)
    for bx in (17, 70, 118):
        p.put(p.R(bx, 77, bx + 3, 80), "iron", 2)

    # ================================================================== window, right of the opening
    sills = window(p, 126, 92, 150, 120, False, lights, X, OY)

    # ================================================================== the lean-to's door
    p.put(p.R(166, 88, 200, GL), "wood", 4)
    p.put(p.R(166, 88, 167, GL), "wood", 6)
    p.put(p.R(199, 88, 200, GL), "wood", 2)
    p.put(p.R(166, 88, 200, 89), "wood", 2)
    dl = p.R(169, 91, 197, GL)
    p.put(dl, "cloth", 2)
    p.put(dl & (xx >= 195), "cloth", 3)
    p.mottle(dl, 312, t=0.62)
    dg = p.R(174, 96, 192, 114)
    p.put(dilate(dg) & dl & ~dg, "cloth", 1)
    p.put(dg, "glow", 4, "dawn")
    p.put(dg & (yy < 103), "glow", 5, "dawn")
    p.put(dg, "glass", 2, "sunrise")
    p.put(p.P([(174, 109), (187, 96), (192, 96), (174, 114)]) & dg, "glass", 4, "sunrise")
    p.put(p.R(182, 96, 184, 114), "cloth", 1)
    p.put(p.R(174, 104, 192, 105), "cloth", 1)
    for a, b in ((119, 131), (134, 146)):
        pan = p.R(174, a, 192, b)
        p.put(pan, "cloth", 1)
        p.put(pan & ((yy == a) | (xx == 191)), "cloth", 0)
        p.put(pan & ((yy == b - 1) | (xx == 174)), "cloth", 3)
    p.put(p.R(193, 116, 195, 122), "lamp", 1)
    step = p.R(163, 147, 203, 153)
    p.put(step, "stone", 5)
    p.put(step & (yy == 147), "stone", 7)
    p.put(step & (yy >= 150), "stone", 3)
    p.put(p.R(200, 147, 203, 153), "stone", 6)
    L(174, 96, 18, 18)
    # lamp over the door: a swan neck and a tin shade
    p.put(p.R(182, 74, 184, 79), "iron", 1)
    p.put(p.R(183, 74, 184, 79), "iron", 3)
    shade = p.P([(176, 84), (183, 78), (190, 84)]) | p.R(176, 83, 190, 85)
    p.put(shade, "iron", 1)
    p.put(shade & (xx >= 184) & (yy < 83), "iron", 3)
    bulb = p.R(180, 85, 186, 87)
    p.put(bulb, "lamp", 3, "dawn")
    p.put(bulb, "lamp", 0, "sunrise")
    L(180, 85, 6, 3)

    # ================================================================== hanging sign: a gear
    SY = 83
    p.put(p.R(206, SY, 233, SY + 2), "iron", 1)
    p.put(p.R(206, SY, 233, SY + 1), "iron", 3)
    p.put(p.L(206, SY + 13, 218, SY + 2), "iron", 1)
    for cx in (212, 226):
        p.put(p.R(cx, SY + 2, cx + 1, SY + 7), "iron", 2)
    board = p.R(207, SY + 7, 232, SY + 32)
    p.put(board, "wood", 3)
    p.put(board & ((yy == SY + 7) | (xx == 231)), "wood", 5)
    p.put(board & ((yy == SY + 31) | (xx == 207)), "wood", 1)
    face = p.R(209, SY + 9, 230, SY + 30)
    p.put(face, "cloth", 1)
    gcx, gcy = 219.5, SY + 19.5
    gear = p.E(gcx, gcy, 6.3, 6.3)
    for k in range(8):
        a = k * np.pi / 4
        tx, ty = gcx + np.cos(a) * 7.4, gcy + np.sin(a) * 7.4
        gear |= p.R(tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5)
    gear &= face & ~p.E(gcx, gcy, 2.6, 2.6)
    p.put(gear, "cream", 2)
    p.put(gear & (xx - yy > gcx - gcy + 4), "cream", 3)
    p.put(gear & (xx - yy < gcx - gcy - 5), "cream", 1)

    # ================================================================== things standing outside
    # an oil drum at the left corner
    dr = p.R(0, 126, 13, GL)
    p.put(dr, "cloth", 2)
    p.put(p.R(10, 126, 13, GL), "cloth", 4)
    p.put(p.R(0, 126, 2, GL), "cloth", 1)
    for by in (126, 134, 142):
        p.put(p.R(0, by, 13, by + 1), "cloth", 4)
        p.put(p.R(0, by + 1, 13, by + 2), "cloth", 1)
    p.put(p.R(0, GL - 1, 13, GL), "cloth", 0)
    # planks leaning on the wall behind it
    for a, b, lv in ((6, 96, 3), (10, 100, 5)):
        pk = p.P([(a - 3, GL), (a + 1, GL), (a + 9, b), (a + 6, b - 1)]) & ~dr
        p.put(pk, "wood", lv)
        p.put(pk & ~sh(pk, -1, 0), "wood", lv + 1)
    # a cable drum under the window
    sp = p.E(139, 138.5, 11.5, 11.5)
    p.put(sp, "wood", 4)
    p.put(sp & ~p.E(138.2, 139.2, 11.2, 11.2), "wood", 6)                 # rim lit on the upper right
    p.put(sp & ~p.E(139.9, 137.7, 11.2, 11.2), "wood", 2)
    hub = p.E(139, 138.5, 4.2, 4.2)
    p.put(hub, "wood", 2)
    p.put(p.E(139, 138.5, 1.8, 1.8), "iron", 1)
    for a in (0.5, 2.6, 4.7):
        bx, by = 139 + np.cos(a) * 7.6, 138.5 + np.sin(a) * 7.6
        p.put(p.R(bx - 1, by - 1, bx + 1, by + 1), "iron", 2)
    p.mottle(sp & ~hub, 313, t=0.6)
    # a crate under the sign, a plant on it
    cx0, cy0, cw, chh = 209, 133, 19, 17
    cr = p.R(cx0, cy0, cx0 + cw, cy0 + chh)
    p.put(cr, "wood", 3)
    p.put(cr & ((yy - cy0) % 5 == 4), "wood", 2)
    fr = cr & ((xx < cx0 + 2) | (xx >= cx0 + cw - 2) | (yy < cy0 + 2) | (yy >= cy0 + chh - 2))
    p.put(fr, "wood", 4)
    p.put(cr & (yy == cy0), "wood", 6)
    p.put(cr & (xx >= cx0 + cw - 1), "wood", 6)
    p.put(cr & (xx == cx0), "wood", 2)
    p.put(p.L(cx0 + 2, cy0 + chh - 3, cx0 + cw - 3, cy0 + 2, 2) & cr, "wood", 4)
    tb = p.R(212, 127, 225, 133)                                          # a tool box on it
    p.put(tb, "cloth", 2)
    p.put(tb & (yy == 127), "cloth", 4)
    p.put(tb & (xx >= 224), "cloth", 4)
    p.put(tb & (yy == 132), "cloth", 0)
    p.put(p.R(216, 124, 221, 125) | p.R(216, 125, 217, 127) | p.R(220, 125, 221, 127), "iron", 3)
    p.put(p.R(218, 129, 220, 131), "lamp", 1)
    # downpipe at the left corner
    p.put(p.R(14, 65, 18, 138), "iron", 1)
    p.put(p.R(17, 65, 18, 138), "iron", 3)
    p.put(p.R(13, 100, 19, 102), "iron", 2)

    # ================================================================== stains
    for _ in range(14):
        ys, xs = np.nonzero(sh(sills, 0, 1) & ~sills & p.is_mat("wood"))
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        p.add(p.R(xs[i], ys[i], xs[i] + 2, ys[i] + int(r.integers(4, 11))) & p.is_mat("wood"), -1)
    for _ in range(6):                                                    # rain streaks down the boards from the gutter
        sx = int(r.integers(HX0 + 3, HX1 - 4))
        p.add(p.R(sx, 65, sx + 2, 65 + int(r.integers(5, 16))) & hall & p.is_mat("wood"), -1)

    # ================================================================== dawn: light spilling out
    nz = noise(BH, BW, 9, 9, 315, 1) * 1.2
    woodm = p.is_mat("wood", st="dawn") & (hall | leaf) & ~room
    wallm = p.is_mat("wall", st="dawn")
    hard = p.is_mat("stone", "iron", "cloth", "tin", st="dawn")
    for cx, cy, rad, below in ((87, 116, 41, 0), (183, 106, 27, 85)):
        d = (np.hypot(xx + 0.5 - cx, (yy + 0.5 - cy) * 1.15) + nz) / rad
        d = np.where(yy < below, 9.0, d)                                  # a shaded lamp only lights what is under it
        p.remat(woodm & (d < 1.0), "woodwarm", 0, "dawn")
        p.remat(woodm & (d < 0.78) & ~leaf, "woodhot", 0, "dawn")
        p.remat(wallm & (d < 1.0), "wallwarm", 0, "dawn")
        p.remat(wallm & (d < 0.55), "wallhot", 0, "dawn")
        p.add(hard & (d < 0.7), 1, "dawn")
    p.add(mon & p.is_mat("wood", st="dawn"), 1, "dawn")                   # the monitor's frame, lit from inside

    # ================================================================== sunrise: shadows thrown to the left
    flatw = p.is_mat("wood", "woodwarm", "woodhot", st="sunrise") & hall
    flatp = p.is_mat("wall", "wallwarm", "wallhot", st="sunrise")
    p.cast(sills, flatw, 5, slope=0.8)
    p.cast(leaf, flatw, 4, slope=0.3)
    p.cast(sp, flatw | p.is_mat("stone", st="sunrise"), 7, slope=0.2)
    p.cast(p.R(14, 65, 18, 138), flatw, 3, slope=0.0)
    p.cast(shade, flatp, 6, slope=0.5)
    p.cast(p.R(166, 88, 200, GL), flatp, 3, slope=0.2)
    p.cast(board, flatp, 5, slope=0.4)
    p.cast(cr, flatp | p.is_mat("stone", st="sunrise"), 6, slope=0.2)
    return p
