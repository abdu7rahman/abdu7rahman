#!/usr/bin/env python3
"""The banner at the top of the README.

Three things, in a lot of space, with one of them very large.

The version before this was a hairline rectangle holding a 44px name and
three columns of small print. That is minimal and it is not simple -- it is
a default card, and it read like one. Stripping the colour out of a design
does not leave a design.

So the box is gone. Nothing here is grouped by a border; it is grouped by
space, which is what makes a layout feel deliberate rather than defaulted.
The name carries the plate at 76px with the negative tracking display type
wants, and it is the only large thing, so it is unambiguously the first
thing read. The eyebrow and the one line under it are deliberately small --
the contrast between 12px and 76px is the hierarchy, and a middle size
would blur it.

The facts that used to sit in this plate are gone too. They were already in
the table immediately below, and saying a thing twice in the first screen
is the opposite of simple.

    python3 tools/gen_hero.py light
    python3 tools/gen_hero.py dark
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import EASE_CSS, MONO, SANS, theme_from_argv, suffix

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

T = theme_from_argv(sys.argv)
SFX = suffix(T)
W, H = 1000, 390

EYEBROW = "Robotics engineer"
# Two lines, so it can be 88px instead of the 64 a single line would have to
# shrink to. The system font resolves differently on every reader's machine, so
# a single line sized to just fit here would clip on a wider one; two lines buy
# both the size and the slack.
NAME = ("Mohammed", "Abdul Rahman")
LEDE = "Motion planning, manipulation, and the bringup that makes them run."

ALT = ("Mohammed Abdul Rahman — robotics engineer. Motion planning, "
       "manipulation, and the bringup that makes them run.")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"'
     f' height="{H}" fill="none" role="img" aria-label="{esc(ALT)}">',
     f'<title>{esc(" ".join(NAME))} — {esc(EYEBROW)}</title>',
     f'<desc>{esc(ALT)}</desc>',
     f'''<defs><style>
  text {{ font-family:{SANS} }}
  .mono {{ font-family:{MONO} }}
  @media (prefers-reduced-motion: no-preference) {{
    /* Authored settled; this moves away from settled and back, so switching
       the block off leaves the plate correct rather than stuck at frame zero. */
    .in {{ animation: rise 560ms {EASE_CSS} both }}
    .d1 {{ animation-delay: 40ms }} .d2 {{ animation-delay: 100ms }}
    .d3 {{ animation-delay: 170ms }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(7px) }} }}
  }}
</style></defs>''',
     f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>']

X = 72

# 12px against 76px. The gap between them is the hierarchy; a middle size in
# between would only blur it.
s.append(f'<text class="in d1 mono" x="{X}" y="100" font-size="12" font-weight="500" '
         f'letter-spacing="1" fill="{T["mut"]}">{esc(EYEBROW.upper())}</text>')

# Display type wants negative tracking -- letters read too far apart as they
# grow. -0.03em at 76px is -2.3.
s.append(f'<text class="in d2" x="{X}" y="192" font-size="88" font-weight="600" '
         f'letter-spacing="-2.6" fill="{T["txt"]}">{esc(NAME[0])}</text>')
s.append(f'<text class="in d2" x="{X}" y="276" font-size="88" font-weight="600" '
         f'letter-spacing="-2.6" fill="{T["txt"]}">{esc(NAME[1])}</text>')

s.append(f'<text class="in d3" x="{X}" y="330" font-size="17" font-weight="400" '
         f'letter-spacing="-0.1" fill="{T["mut"]}">{esc(LEDE)}</text>')

s.append('</svg>')

path = f"{OUT}/hero{SFX}.svg"
open(path, "w").write("\n".join(s))
print("hero%s.svg" % SFX, os.path.getsize(path), "bytes")
