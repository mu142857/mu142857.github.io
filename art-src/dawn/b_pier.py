"""The end of the street: the stone quay stops and a wooden pier walks out toward the sunrise.

Scenery only (no section behind it). draw_main clears the walk from PIER_X on, the last copy of
the trees layer turns into open water there (draw_bg.draw_trees(end=True)), so between the
piles you look straight at the lake and the sun.

Local frame: x = world x - X, y = world y - TOP. Deck top = the walk's level (world y 232).
"""
import numpy as np

from kit import Pix, noise, sh, drop_single, long_runs
from pal import PAL

NAME = "pier"
X = 2590
TOP = 148                    # world y of the sprite's first row
BW, BH = 2880 - X, 270 - TOP
GL = 232 - TOP               # 84: the row the feet stand on
QUAY = 2622 - X              # local x where the stone ends
TIP = 2868 - X               # local x of the pier's last plank


def _pile(p, x, top, w=7, seed=0):
    """A round timber pile from `top` down into the water (bottom of the picture)."""
    m = p.R(x, top, x + w, BH)
    p.put(m, "wood", 2)
    p.put(p.R(x + w - 2, top, x + w, BH), "wood", 5)                      # the side the sun is on
    p.put(p.R(x + w - 3, top, x + w - 2, BH), "wood", 3)
    p.put(p.R(x, top, x + 1, BH), "wood", 1)
    p.add(m & (p.yy >= BH - 14), -1)                                      # wet and dark near the water
    p.put(m & (p.yy >= BH - 5), "moss", 1)
    p.put(p.R(x + w - 2, BH - 5, x + w, BH), "moss", 2)
    n = noise(BH, BW, 1.4, 9, 900 + seed, 1)
    p.add(drop_single(m & (p.xx > x) & (p.xx < x + w - 3) & (n > 0.5)), -1)   # grain running down it
    return m


def draw(lights):
    p = Pix(BW, BH, PAL)
    xx, yy = p.xx, p.yy
    r = np.random.default_rng(91)
    Y = lambda wy: wy - TOP

    # ---- the quay's end: wall face dropping into the water, its right side toward the sun
    face = p.R(QUAY - 8, GL, QUAY + 6, BH)
    p.put(face, "stone", 3)
    p.put(p.R(QUAY + 3, GL, QUAY + 6, BH), "stone", 6)
    p.put(p.R(QUAY + 2, GL, QUAY + 3, BH), "stone", 4)
    for jy in (Y(244), Y(255)):
        p.add(p.R(QUAY - 8, jy, QUAY + 6, jy + 1), -1)
    p.mottle(face, 92, t=0.5)
    p.put(face & (yy >= BH - 9), "moss", 1)
    p.put(face & (yy >= BH - 9) & (xx >= QUAY + 3), "moss", 2)
    p.put(drop_single(face & (yy >= BH - 16) & (noise(BH, BW, 3, 3, 93, 1) > 0.25)), "moss", 1)
    cope = p.R(QUAY - 12, GL - 2, QUAY + 8, GL + 5)                        # the big stone that finishes the walk
    p.put(cope, "stone", 5)
    p.put(cope & (yy == GL - 2), "stone", 7)
    p.put(cope & (yy >= GL + 3), "stone", 3)
    p.put(cope & (xx >= QUAY + 6), "stone", 7)

    # ---- the parapet's last pillar, taller than the others
    px0 = 2600 - X
    pil = p.R(px0, Y(188), px0 + 14, GL)
    p.put(pil, "stone", 4)
    p.put(p.R(px0, Y(188), px0 + 2, GL), "stone", 3)
    p.put(p.R(px0 + 11, Y(188), px0 + 14, GL), "stone", 6)
    base = p.R(px0 - 1, Y(226), px0 + 15, GL)
    p.put(base, "stone", 3)
    p.put(p.R(px0 + 12, Y(226), px0 + 15, GL), "stone", 5)
    cap = p.R(px0 - 2, Y(184), px0 + 16, Y(188))
    p.put(cap, "stone", 5)
    p.put(cap & (yy == Y(184)), "stone", 7)
    p.put(cap & (yy == Y(187)), "stone", 3)
    ball = p.E(px0 + 7, Y(179), 5.2, 5.2)
    p.put(ball, "stone", 4)
    p.put(ball & (xx >= px0 + 8) & (yy <= Y(180)), "stone", 6)
    p.put(ball & (xx <= px0 + 3), "stone", 3)
    p.put(ball & (yy >= Y(182)), "stone", 3)
    p.mottle(pil, 94, t=0.55)
    p.put(drop_single(pil & (yy >= Y(218)) & (noise(BH, BW, 4, 3, 95, 1) > 0.3)), "moss", 1)

    # ---- piles (drawn first: the deck and its beam sit on them)
    piles = []
    for i, (wx, top) in enumerate(((2652, 236), (2712, 212), (2772, 236), (2830, 212), (2862, 236))):
        piles.append((wx - X, Y(top), _pile(p, wx - X, Y(top), 7, i)))
    # diagonal braces under the deck, between piles
    for (xa, _, _), (xb, _, _) in ((piles[0], piles[1]), (piles[2], piles[3])):
        br = p.L(xa + 7, Y(262), xb, Y(244), 3)
        p.put(br, "wood", 2)
        p.put(br & ~sh(br, 0, 1), "wood", 4)
        p.put(br & ~sh(br, 0, -1), "wood", 1)

    # ---- deck: a lit walking surface and the long edge beam under it
    deck = p.R(QUAY + 6, GL, TIP, GL + 4)
    p.put(deck, "wood", 4)
    p.put(deck & (yy == GL), "wood", 6)
    p.put(deck & (yy == GL + 3), "wood", 2)
    p.add(long_runs(deck & (yy == GL) & (noise(BH, BW, 12, 1, 96, 1) < -0.3), 3), -1)     # worn places
    x = QUAY + 6
    while x < TIP - 6:                                                    # board ends, uneven widths
        x += int(r.integers(7, 17))
        p.add(p.R(x, GL + 1, x + 1, GL + 3), -1)
    beam = p.R(QUAY + 6, GL + 4, TIP + 2, GL + 10)
    p.put(beam, "wood", 3)
    p.put(beam & (yy == GL + 4), "wood", 1)                               # the deck's own shade on it
    p.put(beam & (yy == GL + 5), "wood", 4)
    p.put(beam & (yy >= GL + 8), "wood", 2)
    p.put(p.R(TIP, GL + 4, TIP + 2, GL + 10), "wood", 6)
    p.mottle(beam & (yy > GL + 5), 97, t=0.55)
    for jx in (2700 - X, 2792 - X):                                       # two scarf joints in the beam
        p.add(p.L(jx, GL + 5, jx + 4, GL + 9), -1)
    for bx, _, _ in piles:                                                # bolt heads where the beam meets each pile
        p.put(p.R(bx + 2, GL + 6, bx + 5, GL + 8), "iron", 3)
        p.put(p.R(bx + 2, GL + 7, bx + 5, GL + 8), "iron", 1)

    # ---- the two tall piles are posts: caps, and a rope slung between quay, posts and the tip
    tall = [(bx, top) for bx, top, _ in piles if top < GL - 10]
    for bx, top in tall:
        m = p.R(bx - 1, top - 3, bx + 8, top)
        p.put(m, "iron", 2)
        p.put(m & (yy == top - 3), "iron", 4)
        p.put(p.R(bx + 6, top - 3, bx + 8, top), "iron", 4)
        post = p.R(bx, top, bx + 7, GL)
        p.cast(post, deck & (yy <= GL + 1), 16, slope=0.0)
    anchors = [(px0 + 14, Y(200))] + [(bx + 3, top + 4) for bx, top in tall] + [(TIP - 4, Y(222))]
    rope = p.Z()
    for (xa, ya), (xb, yb) in zip(anchors, anchors[1:]):
        prev = (xa, ya)
        n = max(6, int((xb - xa) // 5))
        for i in range(1, n + 1):
            t = i / n
            cur = (xa + (xb - xa) * t, ya + (yb - ya) * t + 9 * np.sin(np.pi * t))      # it hangs slack
            rope |= p.L(prev[0], prev[1], cur[0], cur[1])
            prev = cur
    rope &= ~p.on                                                          # passes behind the posts
    p.put(rope, "cream", 0)
    p.put(rope & ~sh(rope, 0, 1), "cream", 1)

    # ---- at the tip: a mooring post with a lantern, and a pennant on a tall pole
    tp = TIP - 7
    pole = p.R(tp, Y(160), tp + 2, GL)
    p.put(pole, "iron", 1)
    p.put(p.R(tp + 1, Y(160), tp + 2, GL), "iron", 3)
    p.put(p.R(tp - 1, Y(158), tp + 3, Y(160)), "iron", 4)
    pen = p.P([(tp, Y(163)), (tp - 30, Y(168)), (tp - 22, Y(172)), (tp - 31, Y(178)), (tp, Y(176))])
    wave = np.round(1.6 * np.sin((xx - tp) / 6.0)).astype(int)            # the cloth ripples in the wind off the lake
    pen = pen | (sh(pen, 0, 1) & (wave > 0))
    p.put(pen, "cloth", 3)
    p.put(pen & (((xx - tp) // 7) % 2 == 0), "cloth", 4)
    p.put(pen & ~sh(pen, 0, -1), "cloth", 5)
    p.put(pen & ~sh(pen, 0, 1), "cloth", 1)
    lp = TIP - 34                                                          # lantern post
    p.put(p.R(lp, Y(204), lp + 3, GL), "wood", 2)
    p.put(p.R(lp + 2, Y(204), lp + 3, GL), "wood", 5)
    arm = p.R(lp - 9, Y(204), lp + 4, Y(206))
    p.put(arm, "wood", 2)
    p.put(arm & (yy == Y(204)), "wood", 4)
    p.put(p.L(lp - 6, Y(206), lp, Y(212)), "wood", 2)
    p.put(p.R(lp - 7, Y(206), lp - 6, Y(209)), "iron", 2)
    lg = p.R(lp - 10, Y(209), lp - 3, Y(218))
    p.put(p.P([(lp - 11, Y(209)), (lp - 6.5, Y(206)), (lp - 2, Y(209))]), "iron", 1)
    p.put(lg, "lamp", 2, "dawn")
    p.put(p.R(lp - 8, Y(211), lp - 5, Y(217)), "lamp", 3, "dawn")
    p.put(lg, "lamp", 0, "sunrise")
    p.put(p.R(lp - 5, Y(209), lp - 3, Y(218)), "lamp", 2, "sunrise")
    p.put(p.R(lp - 10, Y(218), lp - 3, Y(220)), "iron", 1)
    lights.append(("main", X + lp - 10, TOP + Y(209), 7, 9))
    # lantern light on the boards (dawn)
    near = deck & (np.abs(xx - (lp - 6)) < 26)
    p.add(near & (yy <= GL + 1), 1, "dawn")
    p.add(deck & (np.abs(xx - (lp - 6)) < 12) & (yy <= GL + 1), 1, "dawn")

    # ---- things left on the deck: a crate, a coil of rope, a fishing rod leaning on the crate
    cx0, cy0, cw, chh = 2742 - X, GL - 15, 18, 15
    cr = p.R(cx0, cy0, cx0 + cw, GL)
    p.put(cr, "wood", 3)
    p.put(cr & ((yy - cy0) % 5 == 4), "wood", 2)
    fr = cr & ((xx < cx0 + 2) | (xx >= cx0 + cw - 2) | (yy < cy0 + 2) | (yy >= GL - 2))
    p.put(fr, "wood", 4)
    p.put(cr & (yy == cy0), "wood", 6)
    p.put(cr & (xx >= cx0 + cw - 1), "wood", 6)
    p.put(cr & (xx == cx0), "wood", 2)
    p.cast(cr, deck & (yy <= GL + 1), 14, slope=0.0)
    rod = p.L(cx0 + cw + 9, GL - 1, cx0 + cw - 18, Y(176))
    p.put(rod, "wood", 5)
    p.put(rod & (yy > GL - 16), "wood", 3)
    coil = p.E(2690 - X, GL - 2.5, 8, 3)
    p.put(coil, "cream", 1)
    p.put(coil & (yy <= GL - 4), "cream", 2)
    p.put(p.E(2690 - X, GL - 3, 4, 1.2), "cream", 0)
    p.put(coil & (yy == GL - 1), "cream", 0)

    # ---- a rowboat tied up on the near side, low in the water
    bx0, by0 = 2664 - X, Y(251)
    hull = p.P([(bx0, by0), (bx0 + 62, by0), (bx0 + 56, by0 + 12), (bx0 + 8, by0 + 12)]) \
        | p.P([(bx0 + 62, by0), (bx0 + 70, by0 - 4), (bx0 + 56, by0 + 12)])
    p.put(hull, "wood", 3)
    p.put(hull & (yy >= by0 + 7), "wood", 2)
    p.put(hull & (yy <= by0 + 1), "wood", 6)                               # gunwale
    p.put(hull & (yy == by0 + 2), "wood", 1)
    p.put(hull & (xx >= bx0 + 58), "wood", 5)
    p.add(long_runs(hull & (yy == by0 + 6), 12), 1)                        # one strake
    p.mottle(hull & (yy > by0 + 2), 98, t=0.55)
    for sx in (bx0 + 18, bx0 + 40):                                        # thwarts seen end-on
        p.put(p.R(sx, by0 - 2, sx + 7, by0), "wood", 4)
        p.put(p.R(sx, by0 - 2, sx + 7, by0 - 1), "wood", 6)
    oar = p.L(bx0 + 10, by0 - 3, bx0 + 50, by0 - 7, 2)
    p.put(oar, "wood", 5)
    p.put(p.R(bx0 + 4, by0 - 5, bx0 + 12, by0 - 1), "wood", 4)
    wl = p.R(bx0 + 2, by0 + 12, bx0 + 66, by0 + 13)                       # the line where it sits in the water
    p.put(wl, "water", 2)
    refl = p.R(bx0 + 8, by0 + 13, bx0 + 58, by0 + 19) & (noise(BH, BW, 9, 1.0, 99, 1) > -0.2)
    p.put(long_runs(refl, 6), "shadow", 0)                                # its broken reflection
    moor = p.L(bx0 + 68, by0 - 3, piles[1][0] + 1, GL + 9)
    p.put(moor & ~p.on, "cream", 0)

    # ---- sunrise: the sun is straight ahead, so posts throw long shadows back along the boards
    p.cast(p.R(lp, Y(204), lp + 3, GL), deck & (yy <= GL + 1), 20, slope=0.0)
    return p
