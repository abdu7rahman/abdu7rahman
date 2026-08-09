#!/usr/bin/env python3
"""Contrast and separation checks for the README plates.

The plates are monochrome now, so the old categorical gates -- chroma floors,
pairwise dE in normal vision and under two simulated colour vision
deficiencies -- have nothing left to check. What replaces them is stricter in
the way that matters: a ramp separated only by lightness has to actually be
separated, and every step of it has to stay visible on its own background.

Four gates, all measured:
  1. text contrast      -- body 7:1, muted 4.5:1 against the plate
  2. ramp visibility    -- every step >= 1.6:1 against the plate, so no slice
                           of a chart disappears into the surface behind it
  3. ramp separation    -- adjacent steps >= 8 dL*, which is what makes six
                           greys read as six categories rather than a gradient
  4. hairline           -- the border is present but quiet: 1.15:1 to 2.2:1

Separating by lightness rather than hue is also why there is no deuteranopia
check any more. Lightness is the one channel every form of colour vision
agrees on, so the problem is removed at the source instead of tested around.

    python3 tools/check_palette.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import THEMES


def srgb_to_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    r, g, b = (srgb_to_lin(c) for c in hex_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def lstar(h):
    y = lum(h)
    return 116 * (y ** (1 / 3)) - 16 if y > 0.008856 else 903.3 * y


def main():
    bad = 0
    for t in THEMES:
        print("=== %s  (plate %s) ===" % (t["name"], t["bg"]))

        for role, floor in (("txt", 7.0), ("mut", 4.5)):
            c = contrast(t[role], t["bg"])
            ok = c >= floor
            bad += not ok
            print("  %-6s %-9s %6.2f:1  (floor %.1f)   %s"
                  % (role, t[role], c, floor, "ok" if ok else "TOO LOW"))

        c = contrast(t["line"], t["bg"])
        ok = 1.15 <= c <= 2.2
        bad += not ok
        print("  %-6s %-9s %6.2f:1  (1.15-2.2)   %s"
              % ("line", t["line"], c, "ok" if ok else
                 ("TOO LOUD" if c > 2.2 else "INVISIBLE")))

        print("  ramp")
        prev = None
        for i, step in enumerate(t["ramp"]):
            L = lstar(step)
            c = contrast(step, t["bg"])
            why = []
            if c < 1.6:
                why.append("only %.2f:1 on the plate" % c)
            if prev is not None and abs(L - prev) < 8:
                why.append("only %.1f dL* from the step before" % abs(L - prev))
            bad += bool(why)
            print("    %d  %-9s  L* %5.1f   %5.2f:1   %s"
                  % (i, step, L, c, "; ".join(why)))
            prev = L

        print("  %s\n" % ("all gates pass" if not bad else "%d problems" % bad))

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
