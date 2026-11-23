# One building = one module `b_<id>.py`

`draw_main.build()` imports every module named in `draw_main.BUILDINGS` (missing ones are skipped),
so buildings can be drawn independently. The arcade (`draw_main.draw_arcade`) is the model to
follow for structure, level of detail and the two-state lighting.

```python
from draw_bg import crown, lamp_post, trunk          # foliage / posts, if wanted
from draw_main import window, shutter, G            # shared pieces (pass ox=X, oy=G-GL to window)
from kit import Pix, noise, sh, dilate, drop_single, long_runs, STATES, ramp, lch
from pal import PAL

NAME = "music"          # file name: Assets/dawn/{state}/music.png
ID = "music"            # section id (index.html template `section-<ID>`); leave out for scenery
X = 1180                # world x of the sprite's left edge
BW, BH, GL = 220, 196, 192    # sprite size; GL = local row of the ground line (sprite top = 232 - GL)
DOOR = 120              # local x the character walks to
STOP = (90, 150)        # local x range in which the door prompt shows
POOLS = [(120, 15)]     # dawn light lying on the pavement: (local centre x, half width)
LABEL_Y = 40            # optional: local y of the name label (default is 98 px above the ground)

def draw(lights):       # -> Pix(BW, BH, pal)
    ...
    lights.append(("main", X + x, G - GL + y, w, h))   # every lit window / lamp, in world px
```

Rules: do not edit `kit.py`, `pal.py`, `draw_bg.py`, `draw_main.py` or `build.py` from a building
module. New materials go in the module: `P = {s: {**PAL[s], **EXTRA[s]} for s in STATES}` and
`Pix(BW, BH, P)`; every ramp dark -> light, sunrise ramps about .045-.055 L per step.

Check with `preview_b.py b_<id>` (writes `preview/<NAME>_street.png` and `_zoom.png`, never
touches `Assets/`).

Street plan (world x): arcade 360-590 · projects 800 · music 1180 · about 1560 · skills 1940 ·
experience 2300 · pier 2600-2880. Sprites stay within about 240 px wide so the lake shows between
them. The character (晨) is 50 px tall; doors about 30 x 60.
