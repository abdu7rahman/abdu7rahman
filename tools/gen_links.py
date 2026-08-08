import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import WARMDAY, NIGHT, MONO as MONO_STACK, suffix

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)
T = NIGHT if (len(sys.argv) > 1 and sys.argv[1] == "night") else WARMDAY
SFX = suffix(T)
# The old names are kept so the drawing code below reads unchanged; what they
# point at now comes from tools/palette.py, which is checked rather than picked.
BG0 = T["bg"]; PANEL = T["panel"]; GRID = T["grid"]; LINE = T["line"]
TXT = T["txt"]; MUT = T["mut"]
CY = T["c1"]; RED = T["c2"]; VIO = T["c3"]; GRN = T["c4"]; AMB = T["tint"]
MONO = MONO_STACK

# hand-drawn glyphs, 24x24 viewBox paths
GLYPH = {
 "linkedin": '<path fill="{c}" d="M6.94 8.5H3.9V20h3.04V8.5ZM5.42 3.7a1.77 1.77 0 1 0 0 3.53 1.77 1.77 0 0 0 0-3.53ZM20.1 20h-3.03v-5.6c0-1.34-.03-3.06-1.87-3.06-1.87 0-2.16 1.46-2.16 2.96V20H9.99V8.5h2.91v1.57h.04c.4-.77 1.4-1.58 2.87-1.58 3.07 0 3.64 2.02 3.64 4.65V20Z"/>',
 "mail": '<path fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" d="M3.6 6.4h16.8v11.2H3.6z"/><path fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" d="m3.9 7 8.1 5.4L20.1 7"/>',
 "globe": '<circle cx="12" cy="12" r="8.3" fill="none" stroke="{c}" stroke-width="1.7"/><path fill="none" stroke="{c}" stroke-width="1.7" d="M3.7 12h16.6M12 3.7c2.2 2.4 3.3 5.3 3.3 8.3s-1.1 5.9-3.3 8.3c-2.2-2.4-3.3-5.3-3.3-8.3S9.8 6.1 12 3.7Z"/>',
 "play": '<path fill="{c}" d="M8.5 5.2 19 12 8.5 18.8Z"/>',
}

def card(name, glyph, label, sub, accent, w=306):
    h = 56
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" fill="none" role="img" aria-label="{label} — {sub}">',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="3" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0.5" y="0.5" width="3.5" height="{h-1}" fill="{accent}"/>',
         f'<g transform="translate(20 16)">{GLYPH[glyph].format(c=accent)}</g>'.replace('viewBox','')]
    # scale the 24px glyph into place
    s[-1] = f'<g transform="translate(20 16) scale(1)">{GLYPH[glyph].format(c=accent)}</g>'
    s.append(f'<text x="58" y="24" font-family="{MONO}" font-size="12.5" font-weight="700" letter-spacing="1.6" fill="{TXT}">{label}</text>')
    s.append(f'<text x="58" y="40" font-family="{MONO}" font-size="9.5" letter-spacing="1.2" fill="{MUT}">{sub}</text>')
    # corner tick
    s.append(f'<path d="M{w-13} 6H{w-6}V13" stroke="{accent}" stroke-width="1.4" opacity="0.8"/>')
    s.append('</svg>')
    open(f"{OUT}/link-{name}{SFX}.svg","w").write("\n".join(s))
    return f"{OUT}/link-{name}{SFX}.svg"

card("linkedin","linkedin","LINKEDIN","in/abdu7rahman",T["c3"])
card("email","mail","EMAIL","mohammedabdulr.1@northeastern.edu",T["c2"], 360)
card("site","globe","PORTFOLIO","abdu7rahman.github.io",T["c1"])
card("demo","play","RUN MY ROBOTS","search a map · chase a cursor · reach into the cell",T["c4"], 448)
print("wrote 4 link cards")