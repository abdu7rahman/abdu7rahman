#!/usr/bin/env python3
"""The one place the README's plates get their colours.

Two themes, because GitHub renders a README on white or on #0d1117 depending
on the reader, and a plate that only works on one of them looks like a mistake
on the other. Every asset is emitted twice and the README picks with <picture>.

The categorical hues are not chosen by eye. Running tools/check_palette.py
checks six things for both themes: the hues sit in a narrow L* band so none of
them dominates, each clears a chroma floor so it still reads as a category,
each clears 3:1 against its own background, and every pair holds dE >= 15 in
normal vision and >= 8 under simulated deuteranopia and protanopia. Change a
value and run that script before committing it.

    python3 tools/check_palette.py
"""

WARMDAY = {
    "name":  "warmday",
    "bg":    "#efe7d6",   # paper
    "panel": "#f6efe0",   # a plate raised off the paper
    "sunk":  "#e3d9c4",   # a recessed well
    "grid":  "#e1d8c7",   # ink hairline at 8%
    "line":  "#d6cdbc",   # ink hairline at 14%
    "txt":   "#2c2a23",   # ink
    "mut":   "#565f5a",   # ink, faint
    # categorical, in the order plates should reach for them
    "c1":    "#3f6b57",   # pine
    "c2":    "#9a4a26",   # clay
    "c3":    "#35617f",   # lake
    "c4":    "#6d7f45",   # moss
    # A fill, never a fifth category and never a label. Four is the ceiling
    # here: sweeping the gamut for a fifth hue that clears every gate against
    # pine/clay/lake/moss returns nothing but electric blue, which is the
    # exact register this palette exists to avoid.
    "tint":  "#a8813e",
    "warn":  "#9a4a26",
    "ok":    "#3f6b57",
}

NIGHT = {
    "name":  "night",
    "bg":    "#0f1a18",
    "panel": "#172420",
    "sunk":  "#15211e",
    "grid":  "#233330",
    "line":  "#2c3f3a",
    "txt":   "#f3ece0",
    "mut":   "#9ba59f",
    "c1":    "#86bb9c",
    "c2":    "#d98c6c",
    "c3":    "#7fa8c4",
    "c4":    "#8d9c58",
    "tint":  "#d9a673",
    "warn":  "#d98c6c",
    "ok":    "#86bb9c",
}

THEMES = (WARMDAY, NIGHT)

MONO = ("'JetBrains Mono',ui-monospace,'SF Mono',SFMono-Regular,Menlo,"
        "Consolas,'Liberation Mono',monospace")
SANS = ("'Schibsted Grotesk',ui-sans-serif,system-ui,-apple-system,"
        "'Segoe UI',Helvetica,Arial,sans-serif")
SERIF = "'Fraunces',Georgia,'Times New Roman',serif"


def suffix(theme):
    """Filename tail for a theme: warmday is the default, night is suffixed."""
    return "" if theme["name"] == "warmday" else "-" + theme["name"]
