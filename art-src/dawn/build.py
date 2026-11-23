"""Draw every layer of the dawn street, write Assets/dawn/{dawn,sunrise}/*.png and scene.json,
and paste up previews (art-src/dawn/preview/) of what the camera sees.

    "/Users/jiamulin/Desktop/程序programs/AI Oscar/.venv/bin/python" build.py [cam ...]
"""
import json
import sys
import time

import numpy as np

import draw_bg
from kit import OUT, PREVIEW, STATES, over, save_png

K = {"sky": 0.0, "far": 0.04, "isle": 0.18, "bank": 0.38, "trees": 0.62, "main": 1.0, "front": 1.3}
ORDER = ["sky", "far", "isle", "bank", "trees", "main", "front"]
W, H = 480, 270
# layers whose second copy is drawn separately because the street ends in open water:
# name -> x inside that copy past which nothing stands (lights there are dropped)
ENDS = {"trees": 700, "bank": draw_bg.BANK_END}


def compose(layers, st, cam):
    a = np.zeros((H, W, 4), np.uint8)
    for name in ORDER:
        if name not in layers:
            continue
        img = layers[name][st]
        off = -int(round(cam * K[name]))
        if name in ("sky",):
            over(a, img, 0, 0)
            continue
        tile = img.shape[1]
        if name == "main":
            over(a, img, off, 0)
        elif name in ENDS:                          # two different copies, not a repeating tile
            over(a, img, off, 0)
            over(a, layers[name + "_end"][st], off + 960, 0)
        else:
            x = off % tile - tile
            while x < W:
                over(a, img, x, 0)
                x += tile
    return a


def main():
    cams = [int(v) for v in sys.argv[1:]] or [0]
    layers = {}
    t0 = time.time()
    for name, fn in draw_bg.LAYERS:
        p = fn()
        p.save(name)
        layers[name] = {s: p.render(s) for s in STATES}
        print(f"{name:6s} {time.time() - t0:5.1f}s")
    n_lights = len(draw_bg.LIGHTS)
    for name, fn in (("trees", draw_bg.draw_trees), ("bank", draw_bg.draw_bank)):
        p = fn(end=True)
        p.save(name + "_end")
        layers[name + "_end"] = {s: p.render(s) for s in STATES}
    del draw_bg.LIGHTS[n_lights:]                    # their lamps are listed below, per copy
    # lights on tiled layers: one entry per copy the camera can reach
    tiled = []
    for l in draw_bg.LIGHTS:
        k = K[l[0]]
        for i in range(1, int((W + k * (2880 - W)) // 960) + 1):
            if l[0] in ENDS and (i > 1 or l[1] > ENDS[l[0]]):
                continue
            tiled.append((l[0], l[1] + 960 * i) + tuple(l[2:]))
    draw_bg.LIGHTS.extend(tiled)
    try:
        import draw_main
        for name, p in draw_main.build(draw_bg.LIGHTS).items():
            p.save(name)
            if name == "ground":
                layers["main"] = {s: p.render(s) for s in STATES}
        extra = draw_main.SPRITES
        for s in STATES:
            for nm, x, y, pix in extra:
                over(layers["main"][s], pix.render(s), x, y)
    except ModuleNotFoundError:
        extra = []
    for s_ in STATES:
        a = compose(layers, s_, 300)
        save_png(a[55:240, 50:300], PREVIEW / f"zoom_arcade_{s_}.png", 5)
        save_png(compose(layers, s_, 0)[150:262, 150:400], PREVIEW / f"zoom_walk_{s_}.png", 5)
        save_png(compose(layers, s_, 2400)[140:270, 180:480], PREVIEW / f"zoom_pier_{s_}.png", 4)
    for cam in cams:
        both = np.concatenate([compose(layers, s, cam) for s in STATES], axis=0)
        save_png(both, PREVIEW / f"cam{cam:04d}.png", 3)
    ended = lambda name: {"name": name, "k": K[name], "images": [{"file": "{state}/%s.png" % name, "x": 0, "y": 0},
                                                                {"file": "{state}/%s_end.png" % name, "x": 960, "y": 0}]}
    rep = lambda name: {"name": name, "k": K[name], "repeat": 960, "images": [{"file": "{state}/%s.png" % name, "x": 0, "y": 0}]}
    main_imgs = [{"file": "{state}/ground.png", "x": 0, "y": 0}] + [{"file": "{state}/%s.png" % nm, "x": int(x), "y": int(y)} for nm, x, y, _ in extra]
    scene = {
        "screen": [W, H], "length": 2880, "ground": 232, "spawn": 120,
        "states": list(STATES), "mixByX": [[700, 0], [2400, 1]], "warmth": {"dawn": 0.0, "sunrise": 1.0},
        "layers": [
            {"name": "sky", "k": 0, "images": [{"file": "{state}/sky.png", "x": 0, "y": 0}],
             "fx": {"water": {"y0": 152, "y1": 214, "glintX": 392}}},
            rep("far"), rep("isle"), ended("bank"), ended("trees"),
            {"name": "main", "k": 1, "images": main_imgs},
            {"name": "player"},
            rep("front"),
        ],
        "stops": draw_main.STOPS,
        # lamps get a small tight halo; big windows only a faint one (their spill is painted into the art)
        "lights": [dict({"layer": l[0], "x": int(l[1]), "y": int(l[2]), "w": int(l[3]), "h": int(l[4]),
                         "color": "#ffc46a", "fadeWithMix": True},
                        **({"r": int(max(l[3], l[4]) * 0.55), "alpha": 0.45, "flicker": 0.02} if max(l[3], l[4]) >= 16
                           else {"r": 15, "steps": [0.17, 0.09, 0.04], "flicker": 0.07}))
                   for l in draw_bg.LIGHTS],
        "fog": [{"y": 196, "h": 30, "alpha": [0.10, 0.06, 0.03], "color": {"dawn": "#8296c0", "sunrise": "#f3dca0"}, "speed": 3, "k": 0.5}],
        "shafts": [{"x": 470, "y": 96, "angle": 196, "w": 46, "len": 620, "alpha": 0.07, "showFromMix": 0.55},
                   {"x": 470, "y": 150, "angle": 190, "w": 30, "len": 620, "alpha": 0.06, "showFromMix": 0.55}],
        "motes": {"count": 36, "dawn": "firefly", "sunrise": "dust"},
        "title": {"x": 24, "y": 20, "w": 300, "h": 56},
    }
    (OUT / "scene.json").write_text(json.dumps(scene, ensure_ascii=False, indent=1))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
