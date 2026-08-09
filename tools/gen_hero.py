#!/usr/bin/env python3
"""The banner at the top of the README.

What this used to be: a rotating LiDAR scope building a point cloud of a room
that does not exist, three telemetry sparklines labelled /cmd_vel linear.x with
invented values, a four-node rqt_graph with packets animating along the edges,
and SYSTEM ONLINE next to a pulsing dot. None of it was measured and none of it
was connected to anything. It read as a sci-fi prop, and it undercut the one
plate on the page that is real -- assets/run.svg, where a nightly job runs the
actual planners on a fresh map and draws whatever came out.

So the fiction is gone and what is left is a name, a role, a sentence, and four
facts that are true. The plate carries its weight through material and type
rather than through decoration: a raised surface with a lit top edge and a warm
shadow under it, one accent rule, and a type scale where tracking is chosen per
size rather than set to 3.4 everywhere.

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
W, H = 1000, 300

# Two lines, as on the site. One line of this name at display size runs past the
# divider and into the facts column; shrinking it until it fits would give up
# the size that makes it the first thing read.
NAME = ("Mohammed", "Abdul Rahman")
ROLE = "Robotics engineer"
# Short enough to clear the divider at x=606. The longer version of this ran
# under the facts column, which is the kind of thing that only shows up once the
# plate is authored at the width it is actually displayed at.
LEDE = "Motion planning, manipulation, and the bringup that makes them run."
CHIPS = ("ROS 2", "MoveIt 2", "Isaac Sim", "Physical AI")
FACTS = (("Now", "Advanced Robotics and AI intern, Siemens"),
         ("Study", "MS Robotics, Northeastern ’27"),
         ("Based", "Berkeley, California"))

ALT = ("Mohammed Abdul Rahman — robotics engineer. Motion planning, "
       "manipulation and hardware bringup. Advanced Robotics and AI intern at "
       "Siemens; MS Robotics at Northeastern University, class of 2027; based "
       "in Berkeley, California. Works in ROS 2, MoveIt 2, Isaac Sim and "
       "physical AI.")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"'
     f' height="{H}" fill="none" role="img" aria-label="{esc(ALT)}">',
     f'<title>{esc(" ".join(NAME))} — {esc(ROLE)}</title>',
     f'<desc>{esc(ALT)}</desc>']

# ── material ──────────────────────────────────────────────────────────────
# A raised surface reads as raised because of three things together: a shadow
# beneath it, a lit edge along its top, and a gradient that is brighter where
# the light lands. Any one of them alone just looks like a rectangle.
s.append(f'''<defs>
<linearGradient id="plate" x1="0" y1="0" x2="0.35" y2="1">
  <stop offset="0" stop-color="{T['panel']}"/>
  <stop offset="1" stop-color="{T['bg']}"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{T['edge']}" stop-opacity="0"/>
  <stop offset="0.28" stop-color="{T['edge']}" stop-opacity="0.9"/>
  <stop offset="0.75" stop-color="{T['edge']}" stop-opacity="0.35"/>
  <stop offset="1" stop-color="{T['edge']}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{T['c1']}"/>
  <stop offset="1" stop-color="{T['c1']}" stop-opacity="0.25"/>
</linearGradient>
<filter id="lift" x="-12%" y="-30%" width="124%" height="180%">
  <feDropShadow dx="0" dy="10" stdDeviation="16" flood-color="{T['shadow']}"
                flood-opacity="{0.10 if T['name'] == 'light' else 0.5}"/>
</filter>
<pattern id="paper" width="48" height="48" patternUnits="userSpaceOnUse">
  <path d="M48 0H0V48" stroke="{T['grid']}" stroke-width="1"/>
</pattern>
<clipPath id="plateclip"><rect x="16" y="10" width="{W-32}" height="{H-32}" rx="16"/></clipPath>
<style>
  text {{ font-family:{SANS} }}
  .mono {{ font-family:{MONO} }}
  @media (prefers-reduced-motion: no-preference) {{
    /* Authored settled, animated away from settled and back, so switching this
       block off leaves the plate correct rather than stuck at frame zero. */
    .in {{ animation: rise 620ms {EASE_CSS} both }}
    .d1 {{ animation-delay: 60ms }}  .d2 {{ animation-delay: 120ms }}
    .d3 {{ animation-delay: 180ms }} .d4 {{ animation-delay: 240ms }}
    .d5 {{ animation-delay: 300ms }}
    .wipe {{ animation: wipe 900ms {EASE_CSS} both; animation-delay: 140ms }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px) }} }}
    @keyframes wipe {{ from {{ transform: scaleX(0) }} }}
  }}
</style>
</defs>''')

# plate
s.append(f'<rect x="16" y="10" width="{W-32}" height="{H-32}" rx="16" '
         f'fill="url(#plate)" filter="url(#lift)"/>')
s.append(f'<g clip-path="url(#plateclip)">'
         f'<rect x="16" y="10" width="{W-32}" height="{H-32}" fill="url(#paper)" '
         f'opacity="{0.5 if T["name"] == "light" else 0.75}"/></g>')
s.append(f'<rect x="16.5" y="10.5" width="{W-33}" height="{H-33}" rx="15.5" '
         f'stroke="{T["line"]}"/>')
s.append(f'<path d="M40 11H{W-40}" stroke="url(#edge)" stroke-width="1.2"/>')

# ── left column: who ──────────────────────────────────────────────────────
X = 64
s.append(f'<text class="in d1 mono" x="{X}" y="68" font-size="11" font-weight="500" '
         f'letter-spacing="0.9" fill="{T["c1"]}">{esc(ROLE.upper())}</text>')

# Display type wants negative tracking -- letters read too far apart as they
# grow. This said letter-spacing 1.5 at 40px before, which is the rule
# backwards. Leading goes the other way: 52px on a 52px line.
s.append(f'<text class="in d2" x="{X}" y="120" font-size="46" font-weight="700" '
         f'letter-spacing="-1.2" fill="{T["txt"]}">{esc(NAME[0])}</text>')
s.append(f'<text class="in d2" x="{X}" y="166" font-size="46" font-weight="700" '
         f'letter-spacing="-1.2" fill="{T["txt"]}">{esc(NAME[1])}</text>')
s.append(f'<rect class="wipe" x="{X}" y="184" width="300" height="3" rx="1.5" '
         f'fill="url(#rule)" style="transform-origin:{X}px 185px"/>')

s.append(f'<text class="in d3" x="{X}" y="222" font-size="14.5" font-weight="400" '
         f'letter-spacing="-0.1" fill="{T["mut"]}">{esc(LEDE)}</text>')

cx = X
for chip in CHIPS:
    w = len(chip) * 7.6 + 26
    s.append(f'<g class="in d4">'
             f'<rect x="{cx:.0f}" y="244" width="{w:.0f}" height="27" rx="8" '
             f'fill="{T["sunk"]}" stroke="{T["line"]}"/>'
             f'<text class="mono" x="{cx + w / 2:.0f}" y="261.5" font-size="11" '
             f'font-weight="500" letter-spacing="0.35" fill="{T["mut"]}" '
             f'text-anchor="middle">{esc(chip)}</text></g>')
    cx += w + 8

# ── right column: three facts, all of them true ───────────────────────────
RX = 646
s.append(f'<path d="M{RX-40} 58V252" stroke="{T["line"]}"/>')
y = 74
for i, (k, v) in enumerate(FACTS):
    s.append(f'<g class="in d{min(5, 3 + i)}">'
             f'<text class="mono" x="{RX}" y="{y}" font-size="9.5" font-weight="500" '
             f'letter-spacing="0.5" fill="{T["mut"]}">{esc(k.upper())}</text>'
             f'<text x="{RX}" y="{y + 23}" font-size="13.5" font-weight="500" '
             f'letter-spacing="-0.1" fill="{T["txt"]}">{esc(v)}</text></g>')
    y += 58

s.append(f'<text class="in d5 mono" x="{RX}" y="262" font-size="10.5" '
         f'font-weight="400" letter-spacing="0.4" fill="{T["mut"]}" '
         f'opacity="0.8">building robots that may work</text>')

s.append('</svg>')

path = f"{OUT}/hero{SFX}.svg"
open(path, "w").write("\n".join(s))
print("hero%s.svg" % SFX, os.path.getsize(path), "bytes")
