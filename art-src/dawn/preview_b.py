"""Preview ONE building module in the street without redrawing the whole world.

    "/Users/jiamulin/Desktop/程序programs/AI Oscar/.venv/bin/python" preview_b.py b_music [zoom x0 y0 x1 y1]

Loads the already-rendered layers from Assets/dawn/{state}/*.png, draws only this module, pastes
it on the walk and writes to art-src/dawn/preview/:
    <name>_street.png   what the camera sees, dawn above sunrise, 3x
    <name>_zoom.png     the sprite itself on the street, dawn left / sunrise right, 5x
                        (pass "zoom x0 y0 x1 y1" in sprite-local pixels to zoom on a part instead)
It never writes to Assets/, so several buildings can be worked on at the same time.
"""
import importlib
import sys

import numpy as np
from PIL import Image

from kit import OUT, PREVIEW, STATES, over, save_png

K = {"sky": 0.0, "far": 0.04, "isle": 0.18, "bank": 0.38, "trees": 0.62, "ground": 1.0, "front": 1.3}
W, H, G = 480, 270, 232


def street(state, cam, sprite, sx, sy, front=True):
    a = np.zeros((H, W, 4), np.uint8)
    for name in ("sky", "far", "isle", "bank", "trees", "ground", "front"):
        if name == "front" and not front:
            continue
        img = np.array(Image.open(OUT / state / f"{name}.png").convert("RGBA"))
        off = -int(round(cam * K[name]))
        if name == "sky":
            over(a, img, 0, 0)
        elif name == "ground":
            over(a, img, off, 0)
            over(a, sprite, sx - cam, sy)
        else:
            x = off % 960 - 960
            while x < W:
                over(a, img, x, 0)
                x += 960
    return a


def main():
    name = sys.argv[1]
    mod = importlib.import_module(name)
    pix = mod.draw([])
    sy = G - mod.GL
    cam = int(np.clip(mod.X + pix.w // 2 - W // 2, 0, 2880 - W))
    shots = {s: street(s, cam, pix.render(s), mod.X, sy) for s in STATES}
    save_png(np.concatenate([shots[s] for s in STATES], axis=0), PREVIEW / f"{mod.NAME}_street.png", 3)
    clean = {s: street(s, cam, pix.render(s), mod.X, sy, front=False) for s in STATES}
    if len(sys.argv) >= 7 and sys.argv[2] == "zoom":
        x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])
    else:
        x0, y0, x1, y1 = 0, 0, pix.w, pix.h
    ax0, ax1 = max(0, mod.X - cam + x0 - 6), min(W, mod.X - cam + x1 + 6)
    ay0, ay1 = max(0, sy + y0 - 6), min(H, sy + y1 + 10)
    save_png(np.concatenate([clean[s][ay0:ay1, ax0:ax1] for s in STATES], axis=1), PREVIEW / f"{mod.NAME}_zoom.png", 5)
    print("wrote", PREVIEW / f"{mod.NAME}_street.png", "and _zoom.png; cam", cam)


if __name__ == "__main__":
    main()
