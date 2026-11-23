"""Palettes for the dawn street, one ramp per material and per state.

dawn    = before sunrise: everything in one blue / indigo family, low chroma; the only warm
          colour is lamp and window light (amber, small areas).
sunrise = the sun half up on the right: faded-photograph gold and mustard, sky going teal at
          the top. Warm means YELLOW, not red (taken from the 丁坝日出 baseline).
Every ramp runs dark -> light so `add(+1)` always means "one step lighter".
"""
from kit import lch, ramp

PAL = {"dawn": {}, "sunrise": {}}
D, S = PAL["dawn"], PAL["sunrise"]

# ---------------------------------------------------------------- sky + water (pinned to the screen)
# sky: index 0 = zenith ... 9 = horizon
D["sky"] = [lch(.225, .058, 262), lch(.25, .058, 257), lch(.275, .057, 252), lch(.305, .055, 247), lch(.335, .053, 242),
            lch(.365, .050, 237), lch(.40, .047, 232), lch(.435, .044, 227), lch(.475, .040, 222), lch(.52, .036, 218)]
S["sky"] = [lch(.615, .060, 192), lch(.675, .060, 185), lch(.735, .055, 175), lch(.785, .052, 160), lch(.825, .060, 136),
            lch(.855, .075, 112), lch(.865, .095, 98), lch(.845, .115, 90), lch(.79, .120, 80), lch(.71, .110, 68)]
# light around the sun: 0 = flat band along the horizon ... 4 = innermost ring
D["ring"] = [lch(.545, .032, 217), lch(.575, .030, 215), lch(.62, .027, 212), lch(.68, .022, 209), lch(.76, .017, 206)]
S["ring"] = [lch(.68, .125, 50), lch(.75, .145, 58), lch(.81, .142, 70), lch(.885, .130, 90), lch(.935, .095, 100)]
D["sun"] = [lch(.76, .017, 206), lch(.80, .014, 204)]
S["sun"] = [lch(.935, .090, 92), lch(.972, .045, 104)]
# clouds by distance from the sun (A near, B mid, C far); each: 0 shaded top, 1 body, 2 lit belly
D["cloudA"] = [lch(.31, .044, 236), lch(.35, .042, 231), lch(.46, .032, 221)]
D["cloudB"] = [lch(.285, .048, 242), lch(.32, .046, 238), lch(.385, .040, 231)]
D["cloudC"] = [lch(.215, .052, 252), lch(.245, .052, 248), lch(.285, .050, 243)]
S["cloudA"] = [lch(.565, .090, 38), lch(.635, .105, 46), lch(.875, .135, 74)]
S["cloudB"] = [lch(.655, .060, 92), lch(.71, .072, 86), lch(.885, .110, 90)]
S["cloudC"] = [lch(.585, .045, 180), lch(.64, .042, 172), lch(.875, .085, 100)]
D["star"] = [lch(.42, .040, 240), lch(.60, .030, 230), lch(.78, .020, 220)]
S["star"] = S["sky"][:3]
# water: 0 = nearest (darkest) ... 7 = at the horizon
D["water"] = [lch(.22, .047, 248), lch(.245, .047, 245), lch(.275, .046, 241), lch(.305, .045, 237),
              lch(.34, .044, 233), lch(.375, .042, 229), lch(.41, .040, 225), lch(.445, .038, 222)]
S["water"] = [lch(.445, .070, 95), lch(.485, .077, 93), lch(.53, .084, 91), lch(.575, .092, 89),
              lch(.62, .100, 86), lch(.665, .108, 83), lch(.705, .115, 78), lch(.745, .120, 72)]
D["hot"] = [lch(.475, .034, 221), lch(.515, .030, 219)]
S["hot"] = [lch(.755, .125, 64), lch(.82, .130, 78)]
D["glint"] = [lch(.49, .030, 219), lch(.565, .026, 215), lch(.67, .020, 210)]
S["glint"] = [lch(.83, .125, 86), lch(.905, .110, 94), lch(.965, .050, 104)]

# ---------------------------------------------------------------- far shore (k .04): fades into the sky
D["hill"] = [lch(.33, .044, 238), lch(.365, .042, 233), lch(.405, .040, 228), lch(.44, .036, 224)]
S["hill"] = [lch(.60, .085, 58), lch(.655, .090, 62), lch(.70, .085, 70), lch(.765, .110, 76)]
D["farwin"] = [lch(.62, .080, 72), lch(.74, .085, 80)]
S["farwin"] = [lch(.765, .110, 76), lch(.84, .115, 84)]

# ---------------------------------------------------------------- island + boats (k .18)
D["isle"] = ramp(6, .20, .40, .046, .038, 244, 226)
S["isle"] = ramp(6, .40, .76, .070, .115, 50, 82)
D["sail"] = ramp(4, .30, .52, .034, .026, 236, 220)
S["sail"] = ramp(4, .62, .93, .075, .060, 70, 98)
D["beam"] = [lch(.70, .090, 78), lch(.84, .075, 88)]
S["beam"] = [lch(.80, .110, 80), lch(.90, .090, 92)]

# ---------------------------------------------------------------- our own shore curving away (k .38)
D["bank"] = ramp(6, .15, .31, .044, .040, 248, 228)
S["bank"] = ramp(6, .30, .66, .060, .105, 55, 90)
D["leafA"] = ramp(6, .175, .345, .042, .046, 236, 206)
S["leafA"] = ramp(6, .36, .72, .070, .118, 68, 102)
D["hut"] = ramp(6, .16, .37, .040, .034, 252, 232)
S["hut"] = ramp(6, .30, .74, .055, .110, 44, 84)

# ---------------------------------------------------------------- trees and lamps right behind the walk (k .62)
D["leafB"] = ramp(7, .105, .315, .040, .052, 240, 200)
S["leafB"] = ramp(7, .22, .76, .058, .130, 60, 104)
D["trunk"] = ramp(6, .085, .235, .030, .034, 260, 238)
S["trunk"] = ramp(6, .16, .56, .040, .095, 38, 74)
D["iron"] = ramp(5, .08, .26, .028, .032, 258, 236)
S["iron"] = ramp(5, .19, .50, .036, .080, 40, 78)
# lamp glass: unlit ... lit core. At sunrise the lamps are off and only catch the sun.
D["lamp"] = [lch(.42, .075, 62), lch(.58, .090, 70), lch(.72, .090, 80), lch(.84, .070, 90)]
S["lamp"] = [lch(.50, .070, 60), lch(.66, .095, 74), lch(.80, .105, 84), lch(.90, .085, 94)]

# ---------------------------------------------------------------- the walk itself (k 1)
D["stone"] = ramp(8, .115, .365, .034, .040, 254, 230)
S["stone"] = ramp(8, .33, .71, .050, .108, 48, 84)
D["pave"] = ramp(6, .215, .47, .036, .033, 242, 222)
S["pave"] = ramp(6, .64, .905, .090, .100, 72, 96)
D["moss"] = ramp(4, .14, .27, .040, .046, 226, 196)
S["moss"] = ramp(4, .30, .58, .062, .105, 84, 108)
D["wood"] = ramp(7, .11, .34, .034, .038, 262, 240)
S["wood"] = ramp(7, .30, .66, .055, .110, 44, 80)
D["shadow"] = ramp(3, .10, .17, .034, .038, 256, 246)        # cast shadows on the ground
S["shadow"] = ramp(3, .27, .40, .050, .066, 44, 60)

# ---------------------------------------------------------------- foreground silhouettes (k 1.4)
D["front"] = [lch(.065, .022, 258), lch(.095, .030, 254), lch(.13, .034, 250)]
S["front"] = [lch(.15, .028, 42), lch(.20, .036, 50), lch(.26, .046, 58)]

# ---------------------------------------------------------------- buildings (k 1)
LAMP_D = lch(.74, .100, 76)                       # the colour lamp light pulls things toward


def _warm(cols, t):
    return [tuple(int(round(c[i] + (LAMP_D[i] - c[i]) * t)) for i in range(3)) for c in cols]


D["wall"] = ramp(8, .150, .405, .036, .040, 252, 228)
S["wall"] = ramp(8, .53, .87, .062, .098, 62, 92)
D["wallwarm"] = _warm(ramp(8, .205, .50, .036, .040, 250, 228), 0.34)     # plaster inside a lamp's reach
S["wallwarm"] = S["wall"]
D["wallhot"] = _warm(ramp(8, .29, .62, .036, .040, 248, 226), 0.60)      # right beside the light
S["wallhot"] = S["wall"]
D["roof"] = ramp(7, .095, .30, .038, .042, 264, 238)
S["roof"] = ramp(7, .29, .61, .060, .105, 42, 68)
D["glass"] = ramp(5, .085, .26, .042, .040, 256, 232)                    # unlit panes: deep blue, a cool reflection
S["glass"] = ramp(5, .44, .90, .070, .095, 62, 98)                       # at sunrise they mirror the sky
D["glow"] = ramp(7, .30, .82, .075, .085, 46, 90)                        # a lit room seen through a window
S["glow"] = ramp(7, .26, .60, .050, .075, 46, 82)                        # the same room with the sun outside: dim
D["cab"] = ramp(5, .13, .33, .040, .055, 18, 52)                        # things standing inside the lit room
S["cab"] = ramp(5, .17, .40, .040, .060, 30, 60)
D["screen"] = [lch(.62, .075, 196), lch(.78, .070, 188), lch(.90, .045, 180)]
S["screen"] = [lch(.52, .050, 150), lch(.64, .055, 130), lch(.76, .060, 112)]
D["cloth"] = ramp(6, .17, .42, .050, .048, 276, 252)
S["cloth"] = ramp(6, .50, .85, .085, .120, 58, 90)
D["cream"] = ramp(4, .40, .66, .030, .030, 240, 216)                     # painted signs, capsule toys
S["cream"] = ramp(4, .66, .95, .070, .055, 74, 100)
D["pavewarm"] = _warm(ramp(6, .26, .52, .036, .033, 242, 222), 0.34)     # pavement in a pool of window light
S["pavewarm"] = S["pave"]
D["fur"] = ramp(4, .13, .30, .030, .030, 262, 240)                       # the cat
S["fur"] = ramp(4, .24, .58, .045, .090, 40, 72)
