#!/usr/bin/env python3
"""Categorical palette check for the README plates.

Six gates, all of them measured:
  1. lightness band     -- the hues sit in a narrow L* range so none dominates
  2. chroma floor       -- every hue is saturated enough to read as a category
  3. contrast on paper  -- >= 3:1, since these are marks and small labels
  4. separation, normal -- pairwise dE >= 15
  5. separation, CVD    -- pairwise dE >= 8 under deuteranopia and protanopia
  6. separation from ink-- each hue is distinguishable from the body text
"""
import itertools
import math
import sys

import itertools
import math


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


def lab(h):
    r, g, b = (srgb_to_lin(c) for c in hex_rgb(h))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else (7.787 * t + 16 / 116)
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de(a, b):
    la, lb = lab(a), lab(b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(la, lb)))


def simulate(h, kind):
    """Brettel-style CVD approximation in linear RGB."""
    r, g, b = (srgb_to_lin(c) for c in hex_rgb(h))
    if kind == "deuteranopia":
        R = 0.625 * r + 0.70 * g + 0.0 * b
        G = 0.70 * r + 0.30 * g + 0.0 * b
        B = 0.0 * r + 0.30 * g + 1.0 * b
    elif kind == "protanopia":
        R = 0.567 * r + 0.433 * g + 0.0 * b
        G = 0.558 * r + 0.442 * g + 0.0 * b
        B = 0.0 * r + 0.242 * g + 0.758 * b
    else:                                        # tritanopia
        R = 0.95 * r + 0.05 * g + 0.0 * b
        G = 0.0 * r + 0.433 * g + 0.567 * b
        B = 0.0 * r + 0.475 * g + 0.525 * b
    inv = lambda c: 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    to8 = lambda c: max(0, min(255, round(inv(max(0.0, min(1.0, c))) * 255)))
    return "#%02x%02x%02x" % (to8(R), to8(G), to8(B))


def lch(h):
    L, a, b = lab(h)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def report(name, paper, ink, cats):
    print("=== %s  (paper %s) ===" % (name, paper))
    bad = 0
    print("  %-8s %-9s %6s %6s %6s   %s" % ("role", "hex", "L*", "C*", "vs bg", "note"))
    for k, v in cats.items():
        L, C, H = lch(v)
        c = contrast(v, paper)
        why = []
        if not (44 <= L <= 88):
            why.append("L* outside 44-88")
        if C < 18:
            why.append("chroma %.0f below 18" % C)
        if c < 3.0:
            why.append("contrast %.2f below 3:1" % c)
        if de(v, ink) < 15:
            why.append("too close to ink")
        bad += bool(why)
        print("  %-8s %-9s %6.1f %6.1f %6.2f   %s" % (k, v, L, C, c, "; ".join(why)))

    print("  pairwise separation")
    for (ka, va), (kb, vb) in itertools.combinations(cats.items(), 2):
        n = de(va, vb)
        d = de(simulate(va, "deuteranopia"), simulate(vb, "deuteranopia"))
        p = de(simulate(va, "protanopia"), simulate(vb, "protanopia"))
        ok = n >= 15 and d >= 8 and p >= 8
        bad += not ok
        print("    %-8s %-8s  normal %5.1f  deut %5.1f  prot %5.1f   %s"
              % (ka, kb, n, d, p, "" if ok else "<-- TOO CLOSE"))
    print("  %s\n" % ("all gates pass" if not bad else "%d problems" % bad))
    return bad


POSTER = {"red": "#e0452c", "rust": "#b85236", "sage": "#7fae8e", "amber": "#e0a03a"}

bad = report("poster", "#100c0b", "#f2e8dd", POSTER)
# bone is the neutral slot: near the text colour on purpose, so it is checked
# for contrast rather than for being a hue of its own
print("=== bone, the neutral ===")
c = contrast("#e8dcc8", "#100c0b")
print("  bone     #e8dcc8   %5.2f:1 on the plate   %s" % (c, "ok" if c >= 4.5 else "TOO LOW"))
bad += c < 4.5
sys.exit(1 if bad else 0)
