#!/usr/bin/env python3
"""The banner at the top of the README.

Minimal, and on purpose. GitHub is a neutral page -- near-white or near-black,
one hairline weight, no accent anywhere -- so a plate that arrives with a red
rule on warm paper does not sit in that page, it sits on top of it. This one
uses GitHub's own surface, border and text values, which means the edge of the
plate is the same hairline as the edge of a table three sections down.

What that leaves is a name, a role, a sentence and three facts, set in the
system font the rest of the page is set in. No gradient, no grid pattern, no
drop shadow, no chips, no accent. The hierarchy is size and space.

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
W, H = 1000, 260

NAME = "Mohammed Abdul Rahman"
ROLE = "Robotics engineer"
LEDE = "Motion planning, manipulation, and the bringup that makes them run."
FACTS = (("Now", "Advanced Robotics and AI intern, Siemens"),
         ("Study", "MS Robotics, Northeastern ’27"),
         ("Based", "Berkeley, California"))

ALT = ("Mohammed Abdul Rahman — robotics engineer. Motion planning, "
       "manipulation and hardware bringup. Advanced Robotics and AI intern at "
       "Siemens; MS Robotics at Northeastern University, class of 2027; based "
       "in Berkeley, California.")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"'
     f' height="{H}" fill="none" role="img" aria-label="{esc(ALT)}">',
     f'<title>{esc(NAME)} — {esc(ROLE)}</title>',
     f'<desc>{esc(ALT)}</desc>',
     f'''<defs><style>
  text {{ font-family:{SANS}; fill:{T['txt']} }}
  .mono {{ font-family:{MONO} }}
  .mut {{ fill:{T['mut']} }}
  @media (prefers-reduced-motion: no-preference) {{
    /* Authored settled; this moves away from settled and back, so switching
       the block off leaves the plate correct rather than stuck at frame zero. */
    .in {{ animation: rise 520ms {EASE_CSS} both }}
    .d1 {{ animation-delay: 40ms }}  .d2 {{ animation-delay: 90ms }}
    .d3 {{ animation-delay: 140ms }} .d4 {{ animation-delay: 190ms }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(6px) }} }}
  }}
</style></defs>''']

# One hairline, at the weight GitHub draws a table border. Nothing else.
s.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" '
         f'fill="{T["bg"]}" stroke="{T["line"]}"/>')

X, RX = 56, 620

s.append(f'<text class="in d1 mono mut" x="{X}" y="60" font-size="11.5" '
         f'font-weight="500" letter-spacing="0.4">{esc(ROLE.upper())}</text>')

# Display type wants negative tracking -- letters read too far apart as they
# grow. The old plate set 40px at letter-spacing 1.5, which is the rule
# inverted. It fits on one line at 44px, so it gets one line.
s.append(f'<text class="in d2" x="{X}" y="118" font-size="44" font-weight="600" '
         f'letter-spacing="-1.1">{esc(NAME)}</text>')

s.append(f'<text class="in d3 mut" x="{X}" y="156" font-size="15" '
         f'letter-spacing="-0.1">{esc(LEDE)}</text>')

# The facts sit on a rule rather than in a boxed column: one line, not a panel.
s.append(f'<path class="in d4" d="M{X} 190H{W-X}" stroke="{T["line"]}"/>')
fx = X
for k, v in FACTS:
    s.append(f'<g class="in d4">'
             f'<text class="mono mut" x="{fx}" y="216" font-size="10" '
             f'font-weight="500" letter-spacing="0.5">{esc(k.upper())}</text>'
             f'<text x="{fx}" y="238" font-size="13" font-weight="500" '
             f'letter-spacing="-0.05">{esc(v)}</text></g>')
    fx += 300

s.append('</svg>')

path = f"{OUT}/hero{SFX}.svg"
open(path, "w").write("\n".join(s))
print("hero%s.svg" % SFX, os.path.getsize(path), "bytes")
