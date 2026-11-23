#!/usr/bin/env python
"""Grey-box placeholder scene for the 480x270 engine (next.html).

Flat colour blocks only: it exists so the engine can be built and tested before the real art
lands in Assets/dawn/. It follows the same scene.json contract the real scene uses, so the two
are interchangeable (`?scene=dawn-greybox` forces this one).

Run:
  "/Users/jiamulin/Desktop/程序programs/AI Oscar/.venv/bin/python" art-src/greybox.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 480, 270
LENGTH = 2880
GROUND = 232          # feet line: the first ground row
HORIZON = 150
OUT = Path(__file__).resolve().parent.parent / "Assets" / "dawn-greybox"

# state -> palette. Everything is a flat block; the two states share all geometry.
PAL = {
    "dawn": dict(
        sky=[(14, 18, 44), (22, 30, 66), (34, 48, 92), (58, 76, 122), (104, 118, 150)],
        glow=(150, 150, 170), sun=None,
        far=(40, 52, 92), far2=(50, 64, 106),
        water=(30, 42, 78), water_hi=(52, 68, 108),
        mid=(26, 32, 62), mid_win=(214, 164, 88),
        ground=(20, 24, 46), ground_top=(52, 62, 98), ground_dark=(14, 16, 34),
        wall=[(52, 60, 98), (60, 62, 104), (46, 62, 96), (58, 56, 96), (50, 66, 102), (56, 60, 90)],
        roof=(30, 34, 64), door=(22, 24, 48), window=(232, 180, 96), lit=(74, 80, 118),
        front=(8, 10, 22), cloud=(60, 72, 112), cloud_hi=(86, 98, 136),
    ),
    "sunrise": dict(
        sky=[(84, 142, 146), (132, 172, 156), (190, 196, 150), (232, 204, 128), (246, 186, 96)],
        glow=(255, 226, 150), sun=(255, 240, 190),
        far=(170, 140, 96), far2=(186, 154, 104),
        water=(196, 164, 92), water_hi=(248, 222, 150),
        mid=(120, 96, 70), mid_win=(150, 120, 84),
        ground=(84, 66, 46), ground_top=(222, 188, 120), ground_dark=(60, 46, 34),
        wall=[(176, 146, 100), (186, 150, 104), (168, 148, 108), (180, 140, 98), (172, 152, 112), (184, 148, 96)],
        roof=(112, 86, 62), door=(74, 56, 42), window=(120, 104, 86), lit=(232, 200, 134),
        front=(34, 24, 18), cloud=(206, 176, 120), cloud_hi=(250, 226, 160),
    ),
}

# Six stops, in the site's order. (x, width, height) of each placeholder building.
STOPS = ["gameProjects", "projects", "music", "about", "skills", "experience"]
BUILDINGS = [(520, 170, 128), (900, 200, 104), (1290, 150, 150), (1650, 180, 116), (2030, 160, 138), (2400, 210, 110)]


def blank(w=W, h=H):
    return np.zeros((h, w, 4), dtype=np.uint8)


def rect(a, x0, y0, x1, y1, c):
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(a.shape[1], x1), min(a.shape[0], y1)
    if x1 > x0 and y1 > y0:
        a[y0:y1, x0:x1, :3] = c
        a[y0:y1, x0:x1, 3] = 255


def save(a, state, name):
    d = OUT / state
    d.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a, "RGBA").save(d / name)


def sky(p):
    a = blank()
    n = len(p["sky"])
    for i, c in enumerate(p["sky"]):          # flat bands down to the horizon, then the last one
        rect(a, 0, i * HORIZON // n, W, (i + 1) * HORIZON // n, c)
    rect(a, 0, HORIZON, W, H, p["sky"][-1])
    rect(a, 300, HORIZON - 3, W, HORIZON, p["glow"])            # the light is on the right, low
    if p["sun"]:
        yy, xx = np.mgrid[0:H, 0:W]
        disc = (xx - 392) ** 2 + (yy - HORIZON) ** 2 <= 14 ** 2
        a[disc & (yy < HORIZON), :3] = p["sun"]
    return a


def far(p):
    a = blank(960)
    rng = np.random.default_rng(3)
    x = 0
    while x < 960:                             # stepped ridge, tileable (ends where it starts)
        w = int(rng.integers(40, 110))
        h = int(rng.integers(14, 46))
        rect(a, x, HORIZON - h, min(960, x + w), HORIZON + 2, p["far"])
        rect(a, x + w // 3, HORIZON - h - 8, min(960, x + w // 3 + w // 3), HORIZON - h, p["far2"])
        x += w
    return a


def water(p):
    a = blank()
    rect(a, 0, HORIZON, W, GROUND + 6, p["water"])
    rng = np.random.default_rng(5)
    for _ in range(26):                        # a few solid light bars so the row shimmer shows
        y = int(rng.integers(HORIZON + 4, GROUND))
        x = int(rng.integers(0, W - 40))
        rect(a, x, y, x + int(rng.integers(10, 44)), y + 1, p["water_hi"])
    return a


def mid(p):
    a = blank(960)
    rng = np.random.default_rng(11)
    x = 10
    while x < 940:
        w = int(rng.integers(34, 70))
        h = int(rng.integers(40, 96))
        rect(a, x, GROUND - h, min(960, x + w), GROUND + 4, p["mid"])
        for wy in range(GROUND - h + 8, GROUND - 14, 16):
            if rng.random() < 0.45:
                rect(a, x + 8, wy, x + 14, wy + 7, p["mid_win"])
        x += w + int(rng.integers(12, 60))
    return a


def ground(p):
    a = blank(LENGTH)
    rect(a, 0, GROUND, LENGTH, H, p["ground"])
    rect(a, 0, GROUND, LENGTH, GROUND + 2, p["ground_top"])      # the lit walking surface
    for x in range(0, LENGTH, 96):
        rect(a, x, GROUND + 14, x + 60, GROUND + 16, p["ground_dark"])
    return a


def building(p, i, w, h):
    a = blank(w, h)
    rect(a, 0, 14, w, h, p["wall"][i])
    rect(a, 0, 0, w, 14, p["roof"])
    rect(a, w - 5, 14, w, h, p["lit"])                           # the right side faces the light
    dx = w // 2 - 10
    rect(a, dx, h - 54, dx + 20, h, p["door"])
    for k, wx in enumerate((14, w - 44)):
        rect(a, wx, 30 + 6 * (i % 3), wx + 30, 52 + 6 * (i % 3), p["window"])
    for k in range(i + 1):                                       # i+1 pips: which stop this is
        rect(a, 8 + k * 8, 4, 13 + k * 8, 9, p["window"])
    return a


def front(p):
    a = blank(960)
    for x, w, h in ((0, 90, 38), (230, 46, 20), (520, 130, 46), (800, 60, 26)):
        rect(a, x, H - h, x + w, H, p["front"])
        rect(a, x + w // 3, H - h - 22, x + w // 3 + 6, H - h, p["front"])
    return a


def cloud(p, w, h):
    a = blank(w, h)
    rect(a, 6, h // 3, w - 6, h, p["cloud"])
    rect(a, w // 4, 0, w * 3 // 4, h // 3 + 1, p["cloud"])
    rect(a, 6, h - 2, w - 6, h, p["cloud_hi"])                   # lit from below at dawn
    return a


def main():
    for state, p in PAL.items():
        save(sky(p), state, "sky.png")
        save(far(p), state, "far.png")
        save(water(p), state, "water.png")
        save(mid(p), state, "mid.png")
        save(ground(p), state, "ground.png")
        save(front(p), state, "front.png")
        save(cloud(p, 96, 18), state, "cloud1.png")
        save(cloud(p, 60, 12), state, "cloud2.png")
        for i, (x, w, h) in enumerate(BUILDINGS):
            save(building(p, i, w, h), state, f"building{i + 1}.png")

    main_images = [{"file": "{state}/ground.png", "x": 0, "y": 0}]
    stops, lights = [], []
    for i, (x, w, h) in enumerate(BUILDINGS):
        y = GROUND - h
        main_images.append({"file": f"{{state}}/building{i + 1}.png", "x": x, "y": y})
        stops.append({"id": STOPS[i], "x0": x, "x1": x + w, "door": x + w // 2})
        for wx in (14, w - 44):
            lights.append({"layer": "main", "x": x + wx, "y": y + 30 + 6 * (i % 3), "w": 30, "h": 22,
                           "color": "#ffc870", "flicker": 0.08, "fadeWithMix": True})

    scene = {
        "screen": [W, H],
        "length": LENGTH,
        "ground": GROUND,
        "states": ["dawn", "sunrise"],
        "mixByX": [[0, 0], [2400, 1]],
        "warmth": {"dawn": 0.0, "sunrise": 1.0},
        "layers": [
            {"name": "sky", "k": 0, "images": [{"file": "{state}/sky.png", "x": 0, "y": 0}]},
            {"name": "far", "k": 0.06, "repeat": 960, "images": [{"file": "{state}/far.png", "x": 0, "y": 0}]},
            {"name": "water", "k": 0, "images": [{"file": "{state}/water.png", "x": 0, "y": 0}],
             "fx": {"water": {"y0": HORIZON, "y1": GROUND}}},
            {"name": "mid", "k": 0.38, "repeat": 960, "images": [{"file": "{state}/mid.png", "x": 0, "y": 0}]},
            {"name": "main", "k": 1, "images": main_images},
            {"name": "player"},
            {"name": "front", "k": 1.4, "repeat": 960, "images": [{"file": "{state}/front.png", "x": 0, "y": 0}]},
        ],
        "stops": stops,
        "lights": lights,
        "clouds": [
            {"file": "{state}/cloud1.png", "x": 120, "y": 40, "speed": 1.5, "k": 0.02},
            {"file": "{state}/cloud2.png", "x": 340, "y": 78, "speed": 0.9, "k": 0.02},
        ],
        "fog": [{"y": 196, "h": 34, "alpha": [0.10, 0.06, 0.03],
                 "color": {"dawn": "#8fa3c8", "sunrise": "#f0d9a0"}, "speed": 3, "k": 0.5}],
        "shafts": [{"x": 470, "y": 96, "angle": 200, "w": 34, "len": 300, "alpha": 0.10, "showFromMix": 0.5},
                   {"x": 480, "y": 40, "angle": 196, "w": 18, "len": 320, "alpha": 0.07, "showFromMix": 0.5}],
        "motes": {"count": 40, "dawn": "firefly", "sunrise": "dust"},
        "title": {"x": 24, "y": 40, "w": 220, "h": 90},
    }
    (OUT / "scene.json").write_text(json.dumps(scene, indent=1), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
