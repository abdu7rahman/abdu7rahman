#!/usr/bin/env python3
"""The one place the README's plates get their colours.

There are no hues here any more. GitHub is a near-white page or a near-black
one, both of them neutral, and a plate that arrives with a red accent and a
warm paper background does not sit in that page -- it sits on top of it and
announces itself. The plates now use GitHub's own surface, border, text and
muted values, so the edge of a plate is the same hairline as the edge of a
table and the whole thing reads as part of the page.

Two themes, because GitHub has two, and <picture> picks between them.

Categories are separated by lightness rather than hue. A stacked bar with six
slices still needs six distinguishable steps; a monochrome ramp gives that
without introducing a colour the page does not have. It also removes the
colourblindness problem at the source rather than testing around it -- steps
that differ only in lightness are the one thing every form of colour vision
agrees on.

    python3 tools/check_palette.py
"""

LIGHT = {
    "name":   "light",
    "bg":     "#ffffff",   # GitHub's canvas.default
    "panel":  "#ffffff",
    "sunk":   "#f6f8fa",   # canvas.subtle -- a recessed well
    "grid":   "#eaeef2",
    "line":   "#d1d9e0",   # border.default, the same hairline a table uses
    "edge":   "#ffffff",
    "shadow": "#1f2328",
    "txt":    "#1f2328",   # fg.default
    "mut":    "#59636e",   # fg.muted
    # A neutral ramp, dark to light. Categories are steps on this, not hues.
    "ramp":   ["#1f2328", "#39414a", "#59636e", "#7b848e", "#9aa4ae", "#bcc5ce"],
    "ink":    "#1f2328",
}

DARK = {
    "name":   "dark",
    "bg":     "#0d1117",
    "panel":  "#0d1117",
    "sunk":   "#151b23",
    "grid":   "#21262d",
    "line":   "#3d444d",
    "edge":   "#3d444d",
    "shadow": "#010409",
    "txt":    "#f0f6fc",
    "mut":    "#9198a1",
    "ramp":   ["#f0f6fc", "#c8d1d9", "#a3abb5", "#7d858f", "#585f68", "#383e45"],
    "ink":    "#f0f6fc",
}

THEMES = (LIGHT, DARK)

# System stacks first. The platform font already ships optical sizing, tracking
# tables and legibility tuning, and it is also the font the rest of the page is
# set in, which is most of what makes a plate stop looking like a plate.
SANS = ("ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',"
        "'Noto Sans',Helvetica,Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")


def suffix(theme):
    """Filename tail. Light is the plain name; dark carries the marker."""
    return "" if theme["name"] == "light" else "-dark"


def theme_from_argv(argv):
    """Both the generators and the CI take the theme as argv[1]."""
    want = argv[1] if len(argv) > 1 else "light"
    for t in THEMES:
        if t["name"] == want:
            return t
    raise SystemExit("unknown theme %r; expected one of %s"
                     % (want, ", ".join(t["name"] for t in THEMES)))


# ── motion ────────────────────────────────────────────────────────────────
# A critically damped spring, as a bezier. Nothing here overshoots: overshoot
# belongs to motion a gesture threw, and a README cannot be thrown.
EASE_CSS = "cubic-bezier(0.22, 1, 0.36, 1)"
