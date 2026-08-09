#!/usr/bin/env python3
"""Two charts of things that were counted rather than claimed.

Left: commits per month, filtered to my own authorship. Right: the source-byte
mix across my own repos, with forked upstreams excluded so vendored code does
not skew the split. Both read from tools/data/*.json, which is generated from
the git history rather than typed in.

No panels. Each chart used to sit inside a rounded rectangle with a hairline
around it, which is how you group things when you have not decided how much
space they get. They are grouped by space now, with one rule under each title,
and the plate is taller than it needs to be on purpose.

The bars are also authored at full size rather than at zero. They used to be
drawn at zero and animated up with SMIL fill="freeze", which meant the settled
state of the file -- what a reader sees with animation off, and what any
renderer that does not run SMIL shows -- was two empty charts.

    python3 tools/gen_stats.py light
    python3 tools/gen_stats.py dark
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import EASE_CSS, MONO, SANS, theme_from_argv, suffix

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

T = theme_from_argv(sys.argv)
SFX = suffix(T)

# Six slices, six steps of the neutral ramp, largest share darkest. Adjacent
# steps are what a stacked bar has to separate, and tools/check_palette.py holds
# them at least 8 dL* apart -- a separation every form of colour vision agrees
# on, unlike the four hues this used to reach for.
SER = T["ramp"]

W, H = 1000, 360
X = 72                                   # the hero's margin, so they line up
AW = 520                                 # commit cadence
BX, BW = 648, 280                        # source mix

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
months = json.load(open(os.path.join(DATA, "mine.json")))["months"]
lang = json.load(open(os.path.join(DATA, "lang.json")))


def mseq(a, b):
    y, m = map(int, a.split('-'))
    Y, M = map(int, b.split('-'))
    out = []
    while (y, m) <= (Y, M):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


keys = mseq(min(months), max(months))
vals = [months.get(k, 0) for k in keys]
tot = sum(vals)
act = sum(1 for v in vals if v > 0)
nz = sorted(v for v in vals if v > 0)
med = (nz[len(nz) // 2 - 1] + nz[len(nz) // 2]) / 2 if len(nz) % 2 == 0 else nz[len(nz) // 2]
peak = max(vals)
peak_i = vals.index(peak)

L = lang['lang']
ltot = sum(L.values())
top = sorted(L.items(), key=lambda kv: -kv[1])[:5]
other = ltot - sum(v for _, v in top)
segs = [(k, 100 * v / ltot) for k, v in top] + [("Other", 100 * other / ltot)]

ALT = ("Two charts. Left: monthly commit cadence, %d commits authored across %d "
       "months from %s to %s, %d active months, median %.0f, peak %d. Right: "
       "source-byte mix across %s repositories - %s."
       % (tot, len(keys), keys[0], keys[-1], act, med, peak, lang["repos"],
          ", ".join("%s %.1f percent" % (k, p) for k, p in segs)))

s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"'
     f' height="{H}" fill="none" role="img" aria-label="{ALT}">',
     '<title>Counted, not claimed</title>',
     f'''<defs><style>
  text {{ font-family:{SANS}; fill:{T['txt']} }}
  .mono {{ font-family:{MONO} }}
  .mut {{ fill:{T['mut']} }}
  .head {{ font-size:19px; font-weight:600; letter-spacing:-0.4px }}
  .sub  {{ font-size:12px; font-weight:400 }}
  .ax   {{ font-size:10.5px; font-weight:500 }}
  .lg   {{ font-size:12px; font-weight:450 }}
  @media (prefers-reduced-motion: no-preference) {{
    .bar {{ animation: grow 620ms {EASE_CSS} both; transform-origin: center bottom }}
    .seg {{ animation: wide 700ms {EASE_CSS} both }}
    @keyframes grow {{ from {{ transform: scaleY(0) }} }}
    @keyframes wide {{ from {{ transform: scaleX(0) }} }}
  }}
</style></defs>''',
     f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>']

TOP = 62


def head(x, w, title, sub):
    """A title, a line under it, and a caption. No box."""
    return "\n".join([
        f'<text class="head" x="{x}" y="{TOP}">{title}</text>',
        f'<path d="M{x} {TOP+18}H{x+w}" stroke="{T["line"]}"/>',
        f'<text class="sub mut" x="{x}" y="{TOP+40}">{sub}</text>'])


# ── commits per month ─────────────────────────────────────────────────────
s.append(head(X, AW, "Commit cadence",
              f'{tot} commits · {act} active months · median {med:.0f} · peak {peak}'))
x0, x1 = X + 30, X + AW
yb, yt = TOP + 210, TOP + 96
pitch = (x1 - x0) / len(keys)
bw = min(8.0, pitch - 2.0)
ymax = 50
for gv in (0, 25, 50):
    gy = yb - (gv / ymax) * (yb - yt)
    s.append(f'<path d="M{x0} {gy:.1f}H{x1:.0f}" stroke="{T["line"]}" '
             f'stroke-dasharray="{"none" if gv == 0 else "2 5"}"/>')
    s.append(f'<text class="mono ax mut" x="{x0-10}" y="{gy+3.5:.1f}" '
             f'text-anchor="end">{gv}</text>')
for i, (k, v) in enumerate(zip(keys, vals)):
    if v == 0:
        continue
    bx = x0 + i * pitch + (pitch - bw) / 2
    bh = (v / ymax) * (yb - yt)
    r = min(3.5, bw / 2, bh)
    s.append(f'<path class="bar" style="animation-delay:{i*0.012:.2f}s" '
             f'd="M{bx:.1f} {yb}v{-(bh-r):.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {-r:.1f}'
             f'h{bw-2*r:.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {r:.1f}V{yb}z" '
             f'fill="{T["ramp"][1]}"/>')
bx = x0 + peak_i * pitch + pitch / 2
s.append(f'<text class="mono ax" x="{bx:.1f}" y="{yb-(peak/ymax)*(yb-yt)-8:.1f}" '
         f'text-anchor="middle">{peak}</text>')
seen = set()
for i, k in enumerate(keys):
    y, m = k.split('-')
    if m == '01' and y not in seen:
        seen.add(y)
        tx = x0 + i * pitch + pitch / 2
        s.append(f'<text class="mono ax mut" x="{tx:.1f}" y="{yb+20}" '
                 f'text-anchor="middle">{y}</text>')

# ── source mix ────────────────────────────────────────────────────────────
s.append(head(BX, BW, "Source mix",
              f'{lang["repos"]} own repos · {ltot/1048576:.2f} MiB'))
sy, sh = TOP + 62, 22
GAP = 2.0
cur = BX
for i, ((name, pct), c) in enumerate(zip(segs, SER)):
    w = BW * pct / 100 - (GAP if i < len(segs) - 1 else 0)
    rx = 3 if (i == 0 or i == len(segs) - 1) else 0
    s.append(f'<rect class="seg" style="animation-delay:{0.06*i:.2f}s;'
             f'transform-origin:{cur:.1f}px {sy}px" x="{cur:.1f}" y="{sy}" '
             f'width="{max(1, w):.1f}" height="{sh}" rx="{rx}" fill="{c}"/>')
    cur += w + GAP
for i, ((name, pct), c) in enumerate(zip(segs, SER)):
    ey = sy + 52 + i * 24
    s.append(f'<rect x="{BX}" y="{ey-9}" width="10" height="10" rx="2.5" fill="{c}"/>')
    s.append(f'<text class="lg" x="{BX+18}" y="{ey}">{name}</text>')
    s.append(f'<text class="mono lg mut" x="{BX+BW}" y="{ey}" '
             f'text-anchor="end">{pct:.1f}%</text>')

s.append('</svg>')

path = f"{OUT}/stats{SFX}.svg"
open(path, "w").write("\n".join(s))
print("stats%s.svg" % SFX, os.path.getsize(path), "bytes ·", tot, "commits ·",
      len(segs), "slices")
