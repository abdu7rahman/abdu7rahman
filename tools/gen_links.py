#!/usr/bin/env python3
"""The row of buttons under the banner.

These were mono all-caps labels on a plate with a coloured spine and a corner
tick in the opposite corner -- four separate decorations on a thing whose whole
job is to be pressed. A button should look pressable and say where it goes;
everything else on it is noise.

So: one shape, a sunk surface with a hairline, an icon at the size the label
reads at, and a sans label with the tracking its size actually wants. The one
that matters most -- the interactive demos -- is the only filled one, because
if everything is emphasised nothing is.

    python3 tools/gen_links.py light
    python3 tools/gen_links.py dark
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import MONO, SANS, theme_from_argv, suffix

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

T = theme_from_argv(sys.argv)
SFX = suffix(T)

# 24x24 glyphs, drawn to sit on the text baseline rather than float above it
GLYPH = {
    "linkedin": '<path fill="{c}" d="M6.94 8.5H3.9V20h3.04V8.5ZM5.42 3.7a1.77 1.77 0 1 0 0 3.53 1.77 1.77 0 0 0 0-3.53ZM20.1 20h-3.03v-5.6c0-1.34-.03-3.06-1.87-3.06-1.87 0-2.16 1.46-2.16 2.96V20H9.99V8.5h2.91v1.57h.04c.4-.77 1.4-1.58 2.87-1.58 3.07 0 3.64 2.02 3.64 4.65V20Z"/>',
    "mail": '<path fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" d="M3.6 6.4h16.8v11.2H3.6z"/><path fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" d="m3.9 7 8.1 5.4L20.1 7"/>',
    "globe": '<circle cx="12" cy="12" r="8.3" fill="none" stroke="{c}" stroke-width="1.7"/><path fill="none" stroke="{c}" stroke-width="1.7" d="M3.7 12h16.6M12 3.7c2.2 2.4 3.3 5.3 3.3 8.3s-1.1 5.9-3.3 8.3c-2.2-2.4-3.3-5.3-3.3-8.3S9.8 6.1 12 3.7Z"/>',
    "play": '<path fill="{c}" d="M9 5.6 18.6 12 9 18.4Z"/>',
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# These render in an <img>, so the font is whatever ui-sans-serif resolves to on
# the reader's machine -- SF on a Mac, Segoe on Windows, whatever fontconfig
# picks on Linux. Their advance widths differ, so no width model is right for
# everyone, and a button sized to a best guess clips its own label on the
# platforms the guess was not made on.
#
# So size to an upper bound and centre the label inside it. Being wrong now
# means a little more padding on a narrow font, which nobody notices, instead of
# a clipped word, which everybody does.
EM_UPPER = 0.64


def button(name, glyph, label, alt, solid=False, pad=26):
    """One button. Width follows the label rather than a fixed column."""
    h = 48
    lw = len(label) * EM_UPPER * 13.5
    w = int(pad + 24 + 10 + lw + pad)

    # The one emphasised button is solid ink rather than a colour: on a page
    # with no accent, weight is what makes something primary.
    ink = T["bg"] if solid else T["txt"]
    accent = T["bg"] if solid else T["mut"]
    fill = T["txt"] if solid else T["sunk"]
    stroke = T["txt"] if solid else T["line"]

    # A pill, not a rounded box. Fully rounded ends read as pressable at a
    # glance, which is the whole job of the shape.
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}'
         f'" height="{h}" fill="none" role="img" aria-label="{esc(alt)}">',
         f'<title>{esc(alt)}</title>',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{(h-1)/2:.1f}" '
         f'fill="{fill}" stroke="{stroke}"/>',
         f'<g transform="translate({pad} {(h-24)//2})">{GLYPH[glyph].format(c=accent)}</g>',
         f'<text x="{pad + 24 + 10 + lw / 2:.0f}" y="{h//2 + 5}" font-family="{SANS}" '
         f'font-size="13.5" font-weight="550" letter-spacing="-0.05" '
         f'text-anchor="middle" fill="{ink}">{esc(label)}</text>',
         '</svg>']
    path = f"{OUT}/link-{name}{SFX}.svg"
    open(path, "w").write("\n".join(s))
    return path


button("linkedin", "linkedin", "LinkedIn", "LinkedIn — in/abdu7rahman")
button("site", "globe", "Portfolio", "Portfolio — abdu7rahman.github.io")
button("email", "mail", "Email", "Email — mohammedabdulr.1@northeastern.edu")
button("demo", "play", "Run my robots in the browser",
       "Run my robots — draw a map and search it, chase a cursor, race five "
       "controllers, reach into a UR12e cell", solid=True)
print("wrote 4 link buttons (%s)" % T["name"])
