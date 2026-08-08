#!/usr/bin/env python3
"""The one place the README's plates get their colours.

Warm black, and red carrying most of the page. Deliberately not the portfolio's
palette -- that site is warm paper and this is a poster, and they should not
look like the same thing.

The old plates were slate (#05080c) with neon cyan and violet, which is the
house style of every generated landing page. The blue is gone entirely and
so is the purple. What is left is red as the dominant accent, a deeper rust
under it, amber and one sage green for the series that have to stay apart, and
bone for the highest-contrast marks.

The hues are not chosen by eye. tools/check_palette.py checks a narrow L* band
so none of them dominates by accident, a chroma floor so each still reads as a
category, 3:1 against the plate, and pairwise dE of at least 15 in normal
vision and 8 under simulated deuteranopia and protanopia. red-to-amber is the
tight pair -- 17.2 and 12.8 -- and everything else has room. Change a value and
run that script before committing it.

    python3 tools/check_palette.py
"""

POSTER = {
    "name":  "poster",
    "bg":    "#100c0b",   # warm black, not a blue-black
    "panel": "#1a1412",   # a plate raised off it
    "sunk":  "#16100f",   # a recessed well
    "grid":  "#241a17",
    "line":  "#33241f",
    "txt":   "#f2e8dd",   # warm bone
    "mut":   "#a8988a",
    # categorical, in the order plates should reach for them
    "c1":    "#e0452c",   # red, and the one that carries the page
    "c2":    "#b85236",   # rust, a darker red for the second warm slot
    "c3":    "#7fae8e",   # sage, the only cool hue, so two series can differ
    "c4":    "#e0a03a",   # amber
    "tint":  "#e8dcc8",   # bone, for marks that have to sit on top of the rest
    "warn":  "#e0452c",
    "ok":    "#7fae8e",
}

THEMES = (POSTER,)

MONO = ("'JetBrains Mono',ui-monospace,'SF Mono',SFMono-Regular,Menlo,"
        "Consolas,'Liberation Mono',monospace")
SANS = ("'Schibsted Grotesk',ui-sans-serif,system-ui,-apple-system,"
        "'Segoe UI',Helvetica,Arial,sans-serif")
SERIF = "'Fraunces',Georgia,'Times New Roman',serif"

# kept so the generators keep their two-argument shape; there is one theme now
WARMDAY = POSTER
NIGHT = POSTER


def suffix(theme):
    """Filename tail. One theme, so the plates keep their plain names."""
    return ""
