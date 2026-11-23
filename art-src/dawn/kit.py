"""Shared tools for the "dawn street" art scripts (the interactive site's 480x270 world).

Every layer is drawn ONCE as geometry and coloured TWICE (dawn / sunrise): a `Pix` holds, per
state, a material id and a level (step on that material's ramp) for every pixel. Most paint calls
write both states; only the things that really differ between the two lights (lit windows, stars,
the sun, cast shadows, lamp spill) pass `st="dawn"` or `st="sunrise"`. Identical geometry is what
lets the engine cross-fade the two states while the player walks.

Rules carried over from xiao-oscar / cloud.md: hard edges, no outlines, no pure black or white,
no dashed or dotted lines, texture = 2-3 px colour clumps one step up or down (never a checker
dither), one light direction for the whole scene (low, from the RIGHT: the sunrise).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, "/Users/jiamulin/Desktop/程序programs/AI Oscar")
from oscarkit.canvas import Canvas            # noqa: E402
from oscarkit.light import smooth_noise       # noqa: E402
from oscarkit.palette import from_lch         # noqa: E402

STATES = ("dawn", "sunrise")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets" / "dawn"
PREVIEW = ROOT / "art-src" / "dawn" / "preview"


def lch(L, C, h):
    return tuple(int(v) for v in from_lch(L, C, h))


def ramp(n, L0, L1, C0, C1, h0, h1):
    """n colours, dark -> light, linear in OKLCh."""
    return [lch(L0 + (L1 - L0) * i / (n - 1), C0 + (C1 - C0) * i / (n - 1), h0 + (h1 - h0) * i / (n - 1)) for i in range(n)]


def mixc(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def noise(h, w, sx, sy, seed, octaves=2):
    return smooth_noise(h, w, sx=sx, sy=sy, seed=seed, octaves=octaves)


def noise1d(n, scale, seed, octaves=2):
    return smooth_noise(1, n, sx=scale, sy=1, seed=seed, octaves=octaves)[0]


def periodic(n, seed, ks=(1, 2, 3, 5, 8), amps=None):
    """A smooth 1-D profile in about [-1, 1] that tiles seamlessly over n cells."""
    r = np.random.default_rng(seed)
    x = np.arange(n) / n * 2 * np.pi
    amps = amps or [1 / (i + 1) for i in range(len(ks))]
    out = sum(a * np.sin(k * x + r.uniform(0, 6.283)) for k, a in zip(ks, amps))
    return out / sum(amps)


def sh(m, dx, dy, fill=False):
    """Shift a mask (or array) by (dx, dy); vacated cells get `fill`."""
    out = np.full_like(m, fill)
    H, W = m.shape[:2]
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H + min(0, -dy), max(0, -dx):W + min(0, -dx)]
    return out


def dilate(m, n=1):
    for _ in range(n):
        m = m | sh(m, 1, 0) | sh(m, -1, 0) | sh(m, 0, 1) | sh(m, 0, -1)
    return m


def erode(m, n=1):
    for _ in range(n):
        m = m & sh(m, 1, 0) & sh(m, -1, 0) & sh(m, 0, 1) & sh(m, 0, -1)
    return m


def drop_single(m):
    n4 = sh(m, 1, 0).astype(int) + sh(m, -1, 0) + sh(m, 0, 1) + sh(m, 0, -1)
    return m & (n4 >= 1)


def long_runs(m, minrun=4):
    """Keep only horizontal runs of at least `minrun` cells (so edges never break into dots)."""
    out = np.zeros_like(m)
    H, W = m.shape
    pad = np.zeros((H, 1), bool)
    d = np.diff(np.concatenate([pad, m, pad], axis=1).astype(np.int8), axis=1)
    for y in range(H):
        starts, ends = np.nonzero(d[y] == 1)[0], np.nonzero(d[y] == -1)[0]
        for a, b in zip(starts, ends):
            if b - a >= minrun:
                out[y, a:b] = True
    return out


class Pix:
    """An indexed layer: per state, a material id + ramp level for every pixel."""

    def __init__(self, w, h, pal):
        self.w, self.h, self.pal = w, h, pal
        self.names = sorted(set(pal["dawn"]) & set(pal["sunrise"]))
        self.ids = {n: i + 1 for i, n in enumerate(self.names)}
        self.mat = {s: np.zeros((h, w), np.uint8) for s in STATES}
        self.lvl = {s: np.zeros((h, w), np.int16) for s in STATES}
        self._c = Canvas(w, h)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    # ---- shapes (all return bool masks; x1/y1 exclusive)
    def Z(self):
        return np.zeros((self.h, self.w), bool)

    def R(self, x0, y0, x1, y1):
        m = self.Z()
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
        return m

    def P(self, pts):
        """Filled polygon (pixel centres inside, even-odd)."""
        X, Y = self.xx + 0.5, self.yy + 0.5
        inside = self.Z()
        n = len(pts)
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            if y1 == y2:
                continue
            cond = ((y1 <= Y) & (Y < y2)) | ((y2 <= Y) & (Y < y1))
            inside ^= cond & (X < x1 + (Y - y1) * (x2 - x1) / (y2 - y1))
        return inside

    def E(self, cx, cy, rx, ry):
        return ((self.xx + 0.5 - cx) / rx) ** 2 + ((self.yy + 0.5 - cy) / ry) ** 2 <= 1.0

    def L(self, x0, y0, x1, y1, w=1):
        m = self._c.line(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))).copy()
        for _ in range(w - 1):
            m = m | sh(m, 1, 0) if abs(x1 - x0) < abs(y1 - y0) else m | sh(m, 0, 1)
        return m

    # ---- paint
    def _sts(self, st):
        return STATES if st is None else (st,)

    def put(self, m, mat, lvl=0, st=None):
        i = self.ids[mat]
        for s in self._sts(st):
            self.mat[s][m] = i
            self.lvl[s][m] = lvl[m] if isinstance(lvl, np.ndarray) else lvl

    def add(self, m, d, st=None):
        for s in self._sts(st):
            self.lvl[s][m] += d[m] if isinstance(d, np.ndarray) else d

    def remat(self, m, mat, d=0, st=None):
        """Change the material but keep each cell's level (plus d): lamp spill, light pools."""
        for s in self._sts(st):
            self.mat[s][m] = self.ids[mat]
            self.lvl[s][m] += d

    def cast(self, obj, onto, length, slope=0.35, d=-1, st="sunrise"):
        """Shadow `obj` throws to the LEFT (the sun is low on the right) onto `onto`."""
        m = self.Z()
        for k in range(1, length + 1):
            m |= sh(obj, -k, int(round(k * slope)))
        m &= onto & ~obj
        self.add(m, d, st)
        return m

    def clear(self, m):
        for s in STATES:
            self.mat[s][m] = 0

    @property
    def on(self):
        return self.mat["dawn"] > 0

    def is_mat(self, *mats, st="dawn"):
        ids = [self.ids[m] for m in mats]
        return np.isin(self.mat[st], ids)

    # ---- texture (index level, so both states get the same clumps)
    def mottle(self, m, seed, t=0.45, big=(18, 11), st=None, amount=1):
        """2-3 px clumps one step up / down, denser in some patches than others."""
        n1 = noise(self.h, self.w, 2.4, 2.0, seed, 1)
        n2 = noise(self.h, self.w, big[0], big[1], seed + 1, 1)
        up = drop_single(m & (n1 > t) & (n2 > -0.25))
        dn = drop_single(m & (n1 < -t) & (n2 < 0.25))
        self.add(up, amount, st)
        self.add(dn, -amount, st)

    def lit_edge(self, m, dx, dy, d=1, st=None, minrun=1, against=None):
        """Cells of m whose neighbour toward (dx, dy) is outside m (or outside `against`)."""
        other = m if against is None else against
        e = m & ~sh(other, -dx, -dy)
        if minrun > 1:
            e = long_runs(e, minrun) | (e & sh(e, 0, 1) & sh(e, 0, -1))
        self.add(e, d, st)
        return e

    def band(self, m, dx, dy, n):
        """Cells of m within n cells of its boundary on the (dx, dy) side."""
        out = self.Z()
        cur = m
        for _ in range(n):
            nxt = cur & sh(cur, -dx, -dy)
            out |= cur & ~nxt
            cur = nxt
        return out & m

    # ---- output
    def render(self, st):
        a = np.zeros((self.h, self.w, 4), np.uint8)
        mat, lvl = self.mat[st], self.lvl[st]
        for name, i in self.ids.items():
            m = mat == i
            if not m.any():
                continue
            cols = np.array(self.pal[st][name], np.uint8)
            idx = np.clip(lvl[m], 0, len(cols) - 1)
            a[m, :3] = cols[idx]
            a[m, 3] = 255
        return a

    def save(self, name, also_preview=False):
        for s in STATES:
            p = OUT / s / f"{name}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(self.render(s)).save(p)


def over(dst, src, x=0, y=0):
    """Alpha-composite (hard alpha) src onto dst at (x, y), clipping."""
    H, W = dst.shape[:2]
    h, w = src.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    m = s[..., 3] > 0
    dst[y0:y1, x0:x1][m] = s[m]


def save_png(a, path, scale=1):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(a)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
