#!/usr/bin/env python3
"""The one place the README's plates get their colours.

Two themes now, not one. GitHub renders this README on a white page or a
near-black one depending on the reader's setting, and a single dark plate meant
half of them got a black slab dropped into a white column. Every plate is
emitted twice and the README picks between them with <picture>, so the page
adapts instead of the reader adapting to it.

The neutrals are warm in both directions -- paper rather than white, and a warm
black rather than the blue-black every generated landing page uses. That keeps
one identity across the two themes while letting each behave correctly against
its own background.

The accents are per-theme, which is the point rather than a compromise. A hue
that clears 3:1 against warm black is far too light to clear it against paper;
holding one hex for both would mean one of them is illegible. Same four hue
angles, different lightness and chroma, so the plates read as the same family.

The hues are not chosen by eye. tools/check_palette.py checks, for each theme,
a lightness band so none of them dominates by accident, a chroma floor so each
still reads as a category, 3:1 against that theme's plate, and pairwise dE of at
least 15 in normal vision and 8 under simulated deuteranopia and protanopia.

The old set paired red with a rust that sat 12.8 from it under deuteranopia,
against a floor of 8 -- two of the four categories were nearly one category for
a red-green colourblind reader. The second warm is now a cool slot, which is
what bought the separation.

    python3 tools/check_palette.py
"""

LIGHT = {
    "name":   "light",
    "bg":     "#faf6f0",   # warm paper, not white -- the plate is a surface
    "panel":  "#ffffff",   # raised off it
    "sunk":   "#f1ebe1",   # a recessed well
    "grid":   "#ebe3d7",
    "line":   "#dcd2c4",
    "edge":   "#ffffff",   # the lit top edge of a raised surface
    "shadow": "#2a201a",   # shadows are warm too, never neutral grey
    "txt":    "#191411",
    "mut":    "#6f6357",
    # categorical, in the order plates should reach for them
    "c1":     "#c2411f",   # red, and the one that carries the page
    "c2":     "#8a6a15",   # amber, darkened until it reads on paper
    "c3":     "#2f7a5c",   # sage
    "c4":     "#4c5fa8",   # indigo, the cool slot
    "tint":   "#3d332c",   # ink, for marks that sit on top of the rest
    "warn":   "#c2411f",
    "ok":     "#2f7a5c",
}

DARK = {
    "name":   "dark",
    "bg":     "#14100e",   # warm black, not a blue-black
    "panel":  "#1e1815",
    "sunk":   "#191311",
    "grid":   "#291f1a",
    "line":   "#392b24",
    "edge":   "#4a3931",   # a raised edge catches light rather than glowing
    "shadow": "#000000",
    "txt":    "#f4ece2",   # warm bone
    "mut":    "#a3968a",
    "c1":     "#ef6547",
    "c2":     "#eab95e",
    "c3":     "#63b391",
    "c4":     "#8b9be8",
    "tint":   "#eee2d2",
    "warn":   "#e8593a",
    "ok":     "#63b391",
}

THEMES = (LIGHT, DARK)

# System stacks first. The platform font already ships optical sizing, tracking
# tables and legibility tuning; the webfonts are a preference, not a dependency,
# and GitHub will not load them inside an <img> anyway.
SANS = ("ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,"
        "'Helvetica Neue',Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")


def suffix(theme):
    """Filename tail. Light is the plain name; dark carries the marker."""
    return "" if theme["name"] == "light" else "-dark"


def theme_from_argv(argv):
    """Both generators and the CI take the theme as argv[1]."""
    want = argv[1] if len(argv) > 1 else "light"
    for t in THEMES:
        if t["name"] == want:
            return t
    raise SystemExit("unknown theme %r; expected one of %s"
                     % (want, ", ".join(t["name"] for t in THEMES)))


# ── type scale ────────────────────────────────────────────────────────────
# Tracking is size-specific, never one value for everything. Large text reads
# too loose as it grows and wants negative tracking; small text wants a little
# positive to stay legible. Leading moves the other way -- tight on display,
# looser on body. These are the only values the plates are allowed to use.
TYPE = {
    "display": {"size": 54, "track": -1.2, "weight": 700},
    "title":   {"size": 26, "track": -0.5, "weight": 650},
    "head":    {"size": 15, "track": -0.1, "weight": 600},
    "body":    {"size": 13, "track": 0.0,  "weight": 400},
    "label":   {"size": 11, "track": 0.35, "weight": 500},
    "micro":   {"size": 9.5, "track": 0.5, "weight": 500},
}


def type_attrs(role, family=None):
    """SVG attributes for a role in the scale, so no plate invents its own."""
    t = TYPE[role]
    return ('font-family="%s" font-size="%s" font-weight="%d" letter-spacing="%s"'
            % (family or SANS, t["size"], t["weight"], t["track"]))


# ── motion ────────────────────────────────────────────────────────────────
# A critically damped spring, as a bezier. Nothing on these plates overshoots:
# overshoot belongs to motion a gesture threw, and a README cannot be thrown.
EASE = "0.22 1 0.36 1"          # keySplines form, for SMIL
EASE_CSS = "cubic-bezier(0.22, 1, 0.36, 1)"


def reduced_motion_css(selectors):
    """Animation only runs when the reader has not asked for less of it.

    Every plate is authored so its static form is the settled, finished state,
    and animation moves away from that and back. That ordering is what makes
    this rule safe: switching the animation off leaves the plate correct rather
    than leaving it stuck at frame zero.
    """
    sel = ",".join(selectors)
    return ("@media (prefers-reduced-motion: reduce){%s{animation:none!important}}"
            % sel)
