"""Building 6: the office with the clock tower (Work Experience).

The last building before the pier, so it stands almost entirely in sunrise light: a stone
tower with a clock (it reads ten past six), a plastered two-floor wing with one window already
lit, a small drone parked on the wing's flat roof (the internship was at a drone company) and
a hanging sign with a briefcase. No lettering.

Local frame: 232 x 222, ground line at y = 218 (sprite top = world y 14).
"""
import numpy as np

from draw_bg import crown
from draw_main import window, G
from kit import Pix, noise, sh, dilate, drop_single, long_runs
from pal import PAL

NAME = "experience"
ID = "experience"
X = 2290
BW, BH, GL = 232, 222, 218
DOOR = 158
STOP = (122, 196)
POOLS = [(158, 15), (40, 20)]

OY = G - GL


def draw(lights):
    p = Pix(BW, BH, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(81)
    L = lambda x, y, w, h: lights.append(("main", X + x, OY + y, w, h))
    WX0, WX1 = 12, 130            # wing
    TX0, TX1 = 128, 188           # tower

    # ================================================================== the wing
    wall = p.R(WX0, 108, WX1, GL)
    p.put(wall, "wall", 3)
    n = noise(BH, BW, 34, 22, 82, 2)
    p.add(wall & (n > 0.42), 1)
    p.add(wall & (n < -0.46), -1)
    p.mottle(wall, 83, t=0.66)
    p.add(wall & (yy < 114), -1)                                          # under the cornice
    p.add(wall & (yy < 111), -1)
    for cx, cy, k in ((30, 196, 4), (112, 132, 3)):                       # plaster gone, stone showing
        for _ in range(k):
            bx, by = cx + int(r.integers(-7, 8)), cy + int(r.integers(-5, 6))
            st = p.E(bx, by, r.uniform(2.6, 4.4), r.uniform(1.8, 2.8)) & wall
            p.put(st, "stone", int(r.integers(3, 6)))
            p.add(st & ~sh(st, 0, 1), 1)
            p.add(st & ~sh(st, 0, -1), -1)
    for i, y in enumerate(range(112, 204, 9)):                            # quoins on the wing's free corner
        w = 10 if i % 2 == 0 else 6
        q = p.R(WX0, y, WX0 + w, y + 8)
        p.put(q, "stone", 3)
        p.put(q & (yy == y), "stone", 4)
        p.put(q & (yy == y + 7), "stone", 1)
    pl = p.R(WX0 - 1, 206, WX1, GL)                                       # plinth
    p.put(pl, "stone", 3)
    p.put(pl & (yy == 206), "stone", 5)
    p.put(pl & (yy >= 215), "stone", 2)
    x = WX0 + int(r.integers(4, 16))
    while x < WX1:
        p.add(p.R(x, 208 + int(r.integers(0, 2)), x + 1, 216 - int(r.integers(0, 3))), -1)
        x += int(r.integers(16, 34))
    p.mottle(pl & (yy > 206), 84, t=0.5)
    sc = p.R(WX0 - 1, 158, WX1, 162)                                      # string course between the floors
    p.put(sc, "stone", 4)
    p.put(sc & (yy == 158), "stone", 6)
    p.put(sc & (yy == 161), "stone", 2)
    p.add(wall & (yy >= 162) & (yy < 164), -1)
    # cornice and the low parapet of the flat roof
    par = p.R(WX0 - 2, 96, WX1, 102)
    p.put(par, "stone", 4)
    p.put(par & (yy == 96), "stone", 6)
    p.put(par & (yy >= 100), "stone", 3)
    p.mottle(par & (yy > 96) & (yy < 100), 85, t=0.55)
    cor = p.R(WX0 - 5, 102, WX1, 108)
    p.put(cor, "stone", 5)
    p.put(cor & (yy == 102), "stone", 7)
    p.put(cor & (yy >= 105), "stone", 3)
    p.put(cor & (yy == 107), "stone", 2)

    # ---- on the roof: a landing pad with a small drone, and an aerial
    pad = p.R(40, 92, 78, 96)
    p.put(pad, "wood", 3)
    p.put(pad & (yy == 92), "wood", 5)
    p.put(p.R(75, 92, 78, 96), "wood", 5)
    body = p.R(51, 81, 67, 88) | p.R(54, 79, 64, 81)                      # pale shell, so it reads against the trees
    p.put(body, "cream", 1)
    p.put(body & (yy <= 80), "cream", 2)
    p.put(body & (xx >= 64), "cream", 3)
    p.put(body & (yy == 87), "cream", 0)
    p.put(p.R(61, 83, 65, 86), "cab", 0)                                  # its camera eye
    p.put(p.R(62, 84, 64, 85), "screen", 1)
    for ax, d in ((51, -1), (67, 1)):                                     # arms out to the rotors
        mx = ax + d * 10
        arm = p.L(ax, 83, mx, 79, 2)
        p.put(arm, "cream", 0)
        p.put(arm & ~sh(arm, 0, -1), "cream", 2)
        p.put(p.R(mx - 1, 75, mx + 1, 80), "iron", 3)
        blade = p.R(mx - 8, 74, mx + 9, 75)
        p.put(blade, "cream", 1)
        p.put(blade & (xx > mx), "cream", 3)
    for lx in (55, 62):                                                   # legs
        p.put(p.R(lx, 87, lx + 1, 92), "iron", 1)
    p.put(p.R(52, 91, 66, 92), "iron", 2)
    mast = p.R(104, 58, 106, 96)
    p.put(mast, "iron", 1)
    p.put(p.R(105, 58, 106, 96), "iron", 3)
    for cy, hw in ((62, 7), (69, 5), (76, 3)):
        bar = p.R(105 - hw, cy, 105 + hw + 1, cy + 1)
        p.put(bar, "iron", 2)
        p.put(bar & (xx > 105), "iron", 4)
    p.put(p.R(102, 94, 108, 96), "iron", 2)

    # ---- windows: three upstairs (the middle one lit), two wide ones below (the left lit: a desk)
    sills = p.Z()
    for wx, lit in ((24, False), (60, True), (96, False)):
        sills |= window(p, wx, 120, wx + 22, 148, lit, lights, X, OY)
    for wx, lit in ((22, True), (72, False)):
        x0, x1, y0, y1 = wx, wx + 38, 170, 200
        p.put(p.R(x0 - 3, y0 - 6, x1 + 3, y0 - 2), "stone", 4)
        p.put(p.R(x0 - 3, y0 - 6, x1 + 3, y0 - 5), "stone", 6)
        p.put(p.R(x0 - 2, y0 - 2, x1 + 2, y1 + 2), "wood", 4)
        p.put(p.R(x0 - 2, y0 - 2, x0 - 1, y1 + 2), "wood", 6)
        p.put(p.R(x1 + 1, y0 - 2, x1 + 2, y1 + 2), "wood", 2)
        p.put(p.R(x0 - 2, y0 - 2, x1 + 2, y0 - 1), "wood", 2)
        glass = p.R(x0, y0, x1, y1)
        if lit:
            p.put(glass, "glow", 3, "dawn")
            p.put(glass & (yy < y0 + 14), "glow", 4, "dawn")
            p.put(p.E(x0 + 19, y0 + 5, 8, 3.5) & glass, "glow", 6, "dawn")            # a pendant lamp over the desk
            p.put(p.P([(x0 + 15, y0 + 3), (x0 + 17, y0), (x0 + 21, y0), (x0 + 23, y0 + 3)]) & glass, "cab", 1, "dawn")
            desk = p.R(x0 + 4, y1 - 9, x1 - 4, y1 - 7) | p.R(x0 + 6, y1 - 7, x0 + 8, y1) | p.R(x1 - 8, y1 - 7, x1 - 6, y1)
            p.put(desk & glass, "cab", 1, "dawn")
            mon = p.R(x0 + 17, y1 - 21, x0 + 31, y1 - 11)
            p.put(dilate(mon) & glass, "cab", 0, "dawn")
            p.put(mon, "screen", 1, "dawn")
            p.put(p.R(x0 + 19, y1 - 19, x0 + 27, y1 - 17), "screen", 2, "dawn")       # lines of something on screen
            p.put(p.R(x0 + 19, y1 - 15, x0 + 24, y1 - 14), "screen", 2, "dawn")
            p.put(p.R(x0 + 23, y1 - 11, x0 + 25, y1 - 9), "cab", 0, "dawn")
            chair = p.R(x0 + 7, y1 - 18, x0 + 9, y1 - 3) | p.R(x0 + 7, y1 - 8, x0 + 14, y1 - 6)
            p.put(chair & glass, "cab", 2, "dawn")
            L(x0, y0, x1 - x0, y1 - y0)
        else:
            p.put(glass, "glass", 1, "dawn")
            p.put(glass & (yy > y1 - 9), "glass", 0, "dawn")
            p.put(p.P([(x0, y0 + 16), (x0 + 16, y0), (x0 + 26, y0), (x0, y0 + 26)]) & glass, "glass", 2, "dawn")
        p.put(glass, "glass", 2, "sunrise")
        p.put(glass & (yy > y1 - 10), "glass", 1, "sunrise")
        p.put(p.P([(x0, y0 + 20), (x0 + 20, y0), (x0 + 32, y0), (x0, y0 + 32)]) & glass, "glass", 4, "sunrise")
        p.put(p.P([(x1 - 12, y1), (x1, y1 - 12), (x1, y1 - 6), (x1 - 6, y1)]) & glass, "glass", 3, "sunrise")
        for mx in (x0 + 12, x0 + 25):
            p.put(p.R(mx, y0, mx + 1, y1), "wood", 3)
        sill = p.R(x0 - 4, y1 + 2, x1 + 4, y1 + 5)
        p.put(sill, "stone", 5)
        p.put(sill & (yy == y1 + 2), "stone", 7)
        p.put(sill & (yy == y1 + 4), "stone", 3)
        sills |= sill
    # a long planter of clipped box under the lower windows
    box = p.R(18, 209, 114, GL)
    p.put(box, "wood", 3)
    p.put(box & (yy == 209), "wood", 5)
    p.put(box & (yy >= GL - 2), "wood", 1)
    p.put(p.R(112, 209, 114, GL), "wood", 5)
    for jx in (49, 82):
        p.add(p.R(jx, 210, jx + 1, GL - 1), -1)
    hedge = [(20 + i * 4.6 + r.uniform(-2, 2), 205.5 + r.uniform(-2.4, 1.6), r.uniform(3.4, 6.4), r.uniform(2.8, 4.4)) for i in range(21)]
    crown(p, hedge, "leafB", 240, base=3, drips=6)
    # drain pipe down the free corner
    p.put(p.R(WX0 + 1, 108, WX0 + 5, 214), "iron", 1)
    p.put(p.R(WX0 + 4, 108, WX0 + 5, 214), "iron", 3)
    for by in (140, 186):
        p.put(p.R(WX0 - 1, by, WX0 + 7, by + 2), "iron", 2)

    # ================================================================== the tower
    tw = p.R(TX0, 44, TX1, GL)
    p.put(tw, "stone", 4)
    n2 = noise(BH, BW, 26, 18, 86, 2)
    p.add(tw & (n2 > 0.4), 1)
    p.add(tw & (n2 < -0.45), -1)
    p.add(tw & (xx >= TX1 - 14), 1)                                       # the face turns a little toward the sun
    p.add(tw & (xx < TX0 + 6), -1)
    p.mottle(tw, 87, t=0.58)
    # a few dressed blocks picked out, never a grid
    for _ in range(11):
        bx, by = int(r.integers(TX0 + 8, TX1 - 22)), int(r.integers(96, 204))
        bw_, bh_ = int(r.integers(9, 17)), int(r.integers(5, 8))
        blk = p.R(bx, by, bx + bw_, by + bh_) & tw
        p.add(blk, int(r.choice([-1, 1])))
        p.add(blk & (yy == by + bh_ - 1), -1)
    for i, y in enumerate(range(50, 204, 10)):                            # quoins, the sunward corner bright
        w = 9 if i % 2 == 0 else 5
        q = p.R(TX1 - w, y, TX1, y + 9)
        p.put(q, "stone", 6)
        p.put(q & (yy == y), "stone", 7)
        p.put(q & (yy == y + 8), "stone", 4)
    p.put(p.R(TX1 - 1, 44, TX1, GL), "stone", 7)
    tp = p.R(TX0 - 1, 206, TX1 + 1, GL)                                   # tower plinth
    p.put(tp, "stone", 3)
    p.put(tp & (yy == 206), "stone", 5)
    p.put(tp & (yy >= 215), "stone", 2)
    p.put(p.R(TX1 - 3, 206, TX1 + 1, GL), "stone", 6)
    for y0 in (92, 140):                                                  # two string courses
        s_ = p.R(TX0 - 2, y0, TX1 + 2, y0 + 4)
        p.put(s_, "stone", 5)
        p.put(s_ & (yy == y0), "stone", 7)
        p.put(s_ & (yy == y0 + 3), "stone", 2)
        p.put(p.R(TX1, y0, TX1 + 2, y0 + 4), "stone", 7)
        p.add(tw & (yy >= y0 + 4) & (yy < y0 + 6), -1)
    # ---- roof: a slate pyramid, a ball and a short spike
    eave = p.R(TX0 - 5, 40, TX1 + 5, 45)
    p.put(eave, "wood", 3)
    p.put(eave & (yy == 40), "wood", 5)
    p.put(eave & (yy == 44), "wood", 1)
    p.put(p.R(TX1 + 2, 40, TX1 + 5, 45), "wood", 6)
    roof = p.P([(TX0 - 6, 40), (157, 9), (159, 9), (TX1 + 6, 40)])
    p.put(roof, "roof", 2)
    p.add(roof & (xx > 158 + (yy - 9) * 0.25), 1)
    p.add(roof & (xx > 158 + (yy - 9) * 0.78), 1)
    p.add(roof & (xx < 158 - (yy - 9) * 0.80), -1)
    for cy in range(16, 40, 5):
        p.add(long_runs(roof & (yy == cy) & (noise(BH, BW, 10, 1, 88 + cy, 1) > -0.25), 5), -1)
    p.mottle(roof, 89, t=0.62)
    p.put(roof & ~sh(roof, -1, 0) & (yy > 10), "roof", 5)                 # the sunward hip catches the light
    p.put(p.R(157, 1, 159, 9), "iron", 2)
    p.put(p.R(158, 1, 159, 9), "iron", 4)
    ball = p.E(158, 7.5, 2.6, 2.6)
    p.put(ball, "lamp", 1)
    p.put(ball & (xx >= 158), "lamp", 2)
    p.add(tw & (yy < 50), -1)                                             # eave shade
    p.add(tw & (yy < 47), -1)

    # ---- the clock: ten past six
    ccx, ccy = 158, 70
    ring = p.E(ccx, ccy, 16.5, 16.5)
    p.put(ring, "stone", 5)
    p.put(ring & (yy < ccy - 8), "stone", 7)
    p.put(ring & (xx > ccx + 9), "stone", 7)
    p.put(ring & (yy > ccy + 9), "stone", 3)
    face = p.E(ccx, ccy, 13.5, 13.5)
    p.put(dilate(face) & ring & ~face, "stone", 2)                        # the recess the dial sits in
    p.put(face, "glow", 5, "dawn")                                        # lit from inside before sunrise
    p.put(face & (np.hypot(xx + 0.5 - ccx, yy + 0.5 - ccy) > 10.5), "glow", 4, "dawn")
    p.put(face, "cream", 2, "sunrise")
    p.put(face & (xx + yy > ccx + ccy + 9), "cream", 3, "sunrise")
    p.put(face & (xx + yy < ccx + ccy - 12), "cream", 1, "sunrise")
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):                     # four marks only: twelve, three, six, nine
        m = p.R(ccx + dx * 10 - (1 if dx == 0 else 2), ccy + dy * 10 - (1 if dy == 0 else 2),
                ccx + dx * 10 + (1 if dx == 0 else 2), ccy + dy * 10 + (1 if dy == 0 else 2)) & face
        p.put(m, "cab", 1)
    hands = p.R(ccx, ccy, ccx + 2, ccy + 8) | p.L(ccx, ccy, ccx + 9, ccy - 6)
    p.put(hands & face, "cab", 0)
    p.put(p.E(ccx, ccy, 1.6, 1.6), "lamp", 1)
    L(ccx - 13, ccy - 13, 26, 26)

    # ---- a tall narrow window under the clock
    x0, x1, y0, y1 = 150, 166, 102, 132
    p.put(p.R(x0 - 2, y0 - 2, x1 + 2, y1 + 2), "wood", 3)
    p.put(p.R(x0 - 2, y0 - 2, x0 - 1, y1 + 2), "wood", 5)
    p.put(p.R(x1 + 1, y0 - 2, x1 + 2, y1 + 2), "wood", 1)
    gl = p.R(x0, y0, x1, y1)
    p.put(gl, "glass", 1, "dawn")
    p.put(gl & (yy > y1 - 9), "glass", 0, "dawn")
    p.put(p.P([(x0, y0 + 12), (x0 + 12, y0), (x1, y0), (x1, y0 + 4), (x0, y0 + 20)]) & gl, "glass", 2, "dawn")
    p.put(gl, "glass", 2, "sunrise")
    p.put(gl & (yy > y1 - 10), "glass", 1, "sunrise")
    p.put(p.P([(x0, y0 + 14), (x0 + 14, y0), (x1, y0), (x1, y0 + 6), (x0, y0 + 22)]) & gl, "glass", 4, "sunrise")
    p.put(p.R(157, y0, 159, y1), "wood", 3)
    p.put(p.R(x0, 116, x1, 117), "wood", 3)
    sl = p.R(x0 - 4, y1 + 2, x1 + 4, y1 + 5)
    p.put(sl, "stone", 6)
    p.put(sl & (yy == y1 + 2), "stone", 7)
    p.put(sl & (yy == y1 + 4), "stone", 3)
    sills |= sl

    # ---- the door: double leaves under a round fanlight
    dx0, dx1 = 141, 175
    arch = p.E(158, 166, 19, 19) & (yy < 166)
    sur = (p.R(dx0 - 4, 166, dx1 + 4, GL) | (p.E(158, 166, 21, 21) & (yy < 166)))
    p.put(sur, "stone", 6)
    p.put(sur & ~sh(sur, 0, 1), "stone", 7)
    p.put(sur & (xx < dx0), "stone", 4)
    p.put(sur & (xx >= dx1 + 2), "stone", 7)
    hole = p.R(dx0, 166, dx1, GL) | (p.E(158, 166, 17, 17) & (yy < 166))
    p.put(hole, "wood", 2)
    fan = p.E(158, 165, 14.5, 14.5) & (yy < 164)
    p.put(fan, "glow", 5, "dawn")
    p.put(fan & (yy > 157), "glow", 4, "dawn")
    p.put(fan, "glass", 2, "sunrise")
    p.put(fan & (xx + yy < 158 + 158), "glass", 4, "sunrise")
    for a in (-52, 0, 52):                                                # three glazing bars fanning out
        p.put(p.L(158, 164, 158 + 15 * np.sin(np.radians(a)), 164 - 15 * np.cos(np.radians(a))) & (fan | dilate(fan)), "wood", 2)
    p.put(p.R(dx0, 164, dx1, 167), "wood", 4)
    p.put(p.R(dx0, 164, dx1, 165), "wood", 6)
    leaf = p.R(dx0 + 2, 167, dx1 - 2, GL)
    p.put(leaf, "wood", 3)
    p.put(leaf & (xx >= dx1 - 5), "wood", 4)
    p.mottle(leaf, 90, t=0.6)
    p.put(p.R(157, 167, 159, GL), "wood", 1)                              # where the leaves meet
    for a, b in ((dx0 + 5, 155), (161, dx1 - 5)):
        for y0_, y1_ in ((171, 191), (195, 213)):
            pan = p.R(a, y0_, b, y1_)
            p.put(pan, "wood", 2)
            p.put(pan & ((yy == y0_) | (xx == b - 1)), "wood", 1)
            p.put(pan & ((yy == y1_ - 1) | (xx == a)), "wood", 4)
    p.put(p.R(160, 190, 162, 196), "lamp", 1)                             # brass handles
    p.put(p.R(154, 190, 156, 196), "lamp", 1)
    step = p.R(dx0 - 7, GL - 3, dx1 + 7, BH)
    p.put(step, "stone", 5)
    p.put(step & (yy == GL - 3), "stone", 7)
    p.put(step & (yy >= GL), "stone", 3)
    p.put(p.R(dx1 + 4, GL - 3, dx1 + 7, BH), "stone", 6)
    L(144, 150, 28, 14)

    # ---- wall lamp right of the door
    p.put(p.R(178, 168, 186, 170), "iron", 1)
    p.put(p.R(178, 168, 186, 169), "iron", 3)
    p.put(p.P([(179, 173), (183.5, 169), (188, 173)]), "iron", 1)
    lg = p.R(180, 173, 187, 181)
    p.put(lg, "lamp", 2, "dawn")
    p.put(p.R(182, 175, 185, 180), "lamp", 3, "dawn")
    p.put(lg, "lamp", 0, "sunrise")
    p.put(p.R(185, 173, 187, 181), "lamp", 2, "sunrise")
    p.put(p.R(180, 181, 187, 183), "iron", 1)
    p.put(p.R(179, 173, 180, 182), "iron", 1)
    p.put(p.R(187, 173, 188, 182), "iron", 3)
    L(180, 173, 7, 8)

    # ---- hanging sign: a briefcase
    p.put(p.R(188, 104, 222, 106), "iron", 1)
    p.put(p.R(188, 104, 222, 105), "iron", 3)
    p.put(p.L(188, 120, 202, 106), "iron", 1)
    for cx in (198, 216):
        p.put(p.R(cx, 106, cx + 1, 111), "iron", 2)
    board = p.R(194, 111, 221, 137)
    p.put(board, "wood", 3)
    p.put(board & ((yy == 111) | (xx == 220)), "wood", 5)
    p.put(board & ((yy == 136) | (xx == 194)), "wood", 1)
    p.put(p.R(196, 113, 219, 135), "cloth", 2)
    case = p.R(200, 121, 216, 132)
    p.put(case, "cream", 2)
    p.put(case & (yy == 121), "cream", 3)
    p.put(case & (yy >= 130), "cream", 1)
    p.put(p.R(200, 125, 216, 126), "cloth", 1)                            # the lid's seam
    p.put(p.R(207, 124, 209, 127), "lamp", 2)                             # clasp
    hd = p.R(204, 117, 212, 121) & ~p.R(206, 119, 210, 121)
    p.put(hd, "cream", 2)

    # ---- by the door: a pillar box, and a young tree in a tub
    pb = p.R(196, 184, 210, GL)
    p.put(pb, "cloth", 3)
    p.put(p.R(207, 184, 210, GL), "cloth", 5)
    p.put(p.R(196, 184, 198, GL), "cloth", 2)
    capb = p.E(203, 184, 8.5, 4.5) & (yy < 185)
    p.put(capb, "cloth", 4)
    p.put(capb & (xx >= 206), "cloth", 5)
    p.put(p.R(194, 184, 212, 186), "cloth", 2)
    p.put(p.R(199, 191, 207, 193), "cab", 0)                              # the slot
    p.put(p.R(199, 197, 207, 204), "cream", 1)                            # the plate that says when it is emptied
    p.put(p.R(195, GL - 3, 211, GL), "cloth", 1)
    tub = p.P([(113, 204), (129, 204), (127, GL), (115, GL)])
    p.put(tub, "roof", 3)
    p.put(tub & (yy <= 205), "roof", 5)
    p.put(tub & (xx >= 126), "roof", 5)
    p.put(tub & (xx <= 115), "roof", 2)
    p.put(p.R(120, 176, 122, 204), "trunk", 2)
    p.put(p.R(121, 176, 122, 204), "trunk", 4)
    sap = [(121 + 9.5 * np.cos(a) * rr + r.uniform(-1, 1), 170 + 10.5 * np.sin(a) * rr + r.uniform(-1, 1), r.uniform(3.6, 5.6), r.uniform(3.0, 4.6))
           for a, rr in [(i * 2.399, 0.25 + 0.75 * ((i * 0.618) % 1)) for i in range(15)]]
    crown(p, sap, "leafB", 241, base=3, drips=5)

    # ---- water stains under the sills (on plaster only)
    for _ in range(22):
        ys, xs = np.nonzero(sh(sills, 0, 1) & ~sills & p.is_mat("wall"))
        if not len(ys):
            break
        i = int(r.integers(len(ys)))
        p.add(p.R(xs[i], ys[i], xs[i] + 2, ys[i] + int(r.integers(4, 13))) & p.is_mat("wall"), -1)

    # ---- dawn: light spilling from the lit windows, the fanlight, the lamp and the clock
    nz = noise(BH, BW, 7, 7, 91, 2) * 3.0
    wallm = p.is_mat("wall", st="dawn")
    hard = p.is_mat("stone", "wood", "cloth", "iron", st="dawn")
    for cx, cy, rad in ((71, 138, 22), (41, 188, 34), (158, 160, 24), (183, 178, 28), (158, 70, 26)):
        d = (np.hypot(xx + 0.5 - cx, (yy + 0.5 - cy) * 1.15) + nz) / rad
        p.remat(wallm & (d < 1.0), "wallwarm", 0, "dawn")
        p.remat(wallm & (d < 0.52), "wallhot", 0, "dawn")
        p.add(wallm & (d < 0.26), 1, "dawn")
        p.add(hard & (d < 0.62), 1, "dawn")
    # ---- sunrise: the tower stands a little proud of the wing and shades a strip of it
    flat = p.is_mat("wall", "wallwarm", "wallhot", st="sunrise")
    p.cast(tw | eave, flat | (p.is_mat("stone", st="sunrise") & (xx < TX0)), 9, slope=0.5)
    p.cast(sills, flat, 5, slope=0.8)
    p.cast(cor, flat, 4, slope=1.0)
    p.cast(board, p.is_mat("stone", st="sunrise") & (xx < TX1), 8, slope=0.4)
    p.cast(lg, p.is_mat("stone", st="sunrise"), 8, slope=0.3)
    p.cast(ring, p.is_mat("stone", st="sunrise") & ~ring, 5, slope=0.5)
    p.cast(pb, p.is_mat("stone", st="sunrise") & (yy > 150), 6, slope=0.2)
    return p
