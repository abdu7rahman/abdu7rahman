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
W,H=1200,340

s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" '
   f'aria-label="Mission board: five robotics systems with live status, a UR12e running a pick and place cycle that replans around an obstacle, and a scrolling telemetry log.">',
   '<title>Systems board</title>',
   f'''<defs>
<pattern id="gb" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" stroke="{GRID}" stroke-width="1"/></pattern>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset="0.7" stop-color="{CY}" stop-opacity="0.8"/><stop offset="1" stop-color="{TXT}"/>
</linearGradient>
<filter id="gl2" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="logclip"><rect x="24" y="292" width="700" height="34"/></clipPath>
<style>
 .m{{font-family:{MONO}}}
 .led{{animation:bl 1.6s ease-in-out infinite}}
 @keyframes bl{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
 .t{{font-size:11px;letter-spacing:2.2px;font-weight:700}}
</style></defs>''',
   f'<rect width="{W}" height="{H}" fill="{BG0}"/>',
   f'<rect width="{W}" height="{H}" fill="url(#gb)" opacity="0.5"/>',
   f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" stroke="{LINE}"/>']
for x,y,sx,sy in ((1,1,1,1),(W-1,1,-1,1),(1,H-1,1,-1),(W-1,H-1,-1,-1)):
    s.append(f'<path d="M{x} {y+14*sy}V{y}H{x+14*sx}" stroke="{CY}" stroke-width="1.6" opacity="0.8"/>')

s.append(f'<text class="m t" x="24" y="34" fill="{CY}">SYSTEMS BOARD</text>')
s.append(f'<text class="m" x="176" y="34" font-size="9.5" letter-spacing="1.8" fill="{MUT}">5 ACTIVE  ·  ROS 2 JAZZY  ·  UPTIME 5y</text>')
s.append(f'<path d="M24 46H724" stroke="{LINE}"/>')

mods=[("REACTIVE REPLANNING","UR12e + Hand-E",GRN,0.92,"NOMINAL"),
      ("NAV STACK","A* / Theta* / SMAC / DWA",CY,0.78,"C++ PORT"),
      ("GARMENT POLICIES","pi0 / ACT / Diffusion",VIO,0.604,"TRAINING"),
      ("K.A.L.B QUADRUPED","12 axes, trot",AMB,0.66,"IRL DEMOS"),
      ("SWERVE / OMNI DRIVE","5 Robocon seasons",RED,1.0,"SHIPPED")]
y0=68
for i,(name,sub,col,frac,state) in enumerate(mods):
    y=y0+i*44
    s.append(f'<circle class="led" cx="34" cy="{y+10}" r="4" fill="{col}" style="animation-delay:{i*0.24:.2f}s"/>')
    s.append(f'<text class="m" x="50" y="{y+8}" font-size="11.5" letter-spacing="1.4" fill="{TXT}" font-weight="700">{name}</text>')
    s.append(f'<text class="m" x="50" y="{y+22}" font-size="9" letter-spacing="1.1" fill="{MUT}">{sub}</text>')
    bx,bw=330,300
    s.append(f'<rect x="{bx}" y="{y+3}" width="{bw}" height="7" rx="3.5" fill="{LINE}" opacity="0.7"/>')
    s.append(f'<rect x="{bx}" y="{y+3}" width="0" height="7" rx="3.5" fill="{col}">'
             f'<animate attributeName="width" values="0;{bw*frac:.0f}" dur="1.1s" begin="{0.3+i*0.15:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.9 0.2 1"/></rect>')
    s.append(f'<text class="m" x="{bx+bw+10}" y="{y+11}" font-size="9.5" letter-spacing="1.2" fill="{col}">{state}</text>')
    s.append(f'<path d="M24 {y+32}H724" stroke="{LINE}" opacity="0.45"/>')

# ---------------- animated UR12e pick and place, right side
BX,BY=980,236
L1,L2,L3=86,74,26
def fk(a1,a2,a3):
    j1=(BX+L1*math.cos(a1), BY-L1*math.sin(a1))
    j2=(j1[0]+L2*math.cos(a1+a2), j1[1]-L2*math.sin(a1+a2))
    e =(j2[0]+L3*math.cos(a1+a2+a3), j2[1]-L3*math.sin(a1+a2+a3))
    return j1,j2,e
KEY=[(1.75,-1.15,-0.30),(1.30,-1.05,-0.35),(1.05,-0.75,-0.45),
     (1.55,-1.30,-0.10),(2.20,-1.35,0.10),(2.45,-1.05,0.05),(1.75,-1.15,-0.30)]
pts_seq=[]; j1s=[]; j2s=[]; ees=[]
for a in KEY:
    j1,j2,e=fk(*a)
    pts_seq.append(f"{BX} {BY} {j1[0]:.1f} {j1[1]:.1f} {j2[0]:.1f} {j2[1]:.1f} {e[0]:.1f} {e[1]:.1f}")
    j1s.append(j1); j2s.append(j2); ees.append(e)
DUR="7s"; KT="0;0.16;0.30;0.46;0.62;0.80;1"
s.append(f'<path d="M{BX-150} {BY+22}H{BX+120}" stroke="{LINE}" stroke-width="1.5"/>')
s.append(f'<rect x="{BX-140}" y="{BY+4}" width="60" height="18" rx="3" fill="{PANEL}" stroke="{AMB}" stroke-opacity="0.6"/>')
s.append(f'<text class="m" x="{BX-110}" y="{BY+17}" font-size="8" letter-spacing="1" fill="{AMB}" text-anchor="middle">BIN A</text>')
s.append(f'<rect x="{BX+42}" y="{BY+4}" width="60" height="18" rx="3" fill="{PANEL}" stroke="{GRN}" stroke-opacity="0.6"/>')
s.append(f'<text class="m" x="{BX+72}" y="{BY+17}" font-size="8" letter-spacing="1" fill="{GRN}" text-anchor="middle">BIN B</text>')
# obstacle appears mid-cycle
s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.30;0.35;0.60;0.66;1" dur="{DUR}" repeatCount="indefinite"/>'
         f'<circle cx="{BX-30}" cy="{BY-96}" r="20" fill="{RED}" fill-opacity="0.14" stroke="{RED}" stroke-dasharray="3 3"/>'
         f'<path d="M{BX-38} {BY-104}l16 16M{BX-22} {BY-104}l-16 16" stroke="{RED}" stroke-width="1.6"/></g>')
s.append(f'<rect x="{BX-34}" y="{BY-18}" width="68" height="18" rx="4" fill="{PANEL}" stroke="{CY}" stroke-width="1.5"/>')
s.append(f'<polyline points="{pts_seq[0]}" stroke="{TXT}" stroke-opacity="0.16" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round">'
         f'<animate attributeName="points" values="{";".join(pts_seq)}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" '
         f'keySplines="{";".join([".4 0 .2 1"]*6)}" repeatCount="indefinite"/></polyline>')
s.append(f'<polyline points="{pts_seq[0]}" stroke="{CY}" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round">'
         f'<animate attributeName="points" values="{";".join(pts_seq)}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" '
         f'keySplines="{";".join([".4 0 .2 1"]*6)}" repeatCount="indefinite"/></polyline>')
for pts,r in ((j1s,6.0),(j2s,5.2),(ees,4.4)):
    xs=";".join(f"{p[0]:.1f}" for p in pts); ys=";".join(f"{p[1]:.1f}" for p in pts)
    col = GRN if r==4.4 else CY
    s.append(f'<circle cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="{r}" fill="{PANEL}" stroke="{col}" stroke-width="2">'
             f'<animate attributeName="cx" values="{xs}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" keySplines="{";".join([".4 0 .2 1"]*6)}" repeatCount="indefinite"/>'
             f'<animate attributeName="cy" values="{ys}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" keySplines="{";".join([".4 0 .2 1"]*6)}" repeatCount="indefinite"/></circle>')
s.append(f'<text class="m t" x="{BX-150}" y="34" fill="{CY}">UR12e</text>')
s.append(f'<text class="m" x="{BX-150}" y="50" font-size="9" letter-spacing="1.2" fill="{MUT}">pick / place  ·  replans on contact</text>')
for txt,col,kt,vals in (("EXECUTING",CY,"0;0.28;0.33;0.62;0.66;1","1;1;0;0;1;1"),
                        ("OBSTACLE  ·  REPLAN",RED,"0;0.30;0.34;0.60;0.64;1","0;0;1;1;0;0")):
    s.append(f'<text class="m" x="{W-24}" y="34" font-size="9.5" letter-spacing="1.5" fill="{col}" text-anchor="end" opacity="0">{txt}'
             f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="{DUR}" repeatCount="indefinite"/></text>')

# ---------------- scrolling log
logs=["[ok] tf tree complete: map -> odom -> base_link",
      "[ok] octomap updated, 41,208 voxels",
      "[warn] obstacle within 0.18 m of planned path -- cancelling",
      "[ok] ik pool 120 solutions, 8 candidates ranked",
      "[ok] replanned via BIT* in 1.42 s",
      "[ok] gripper closed, object acquired",
      "[ok] cmd_vel 0.55 m/s, controller 20 Hz"]
s.append(f'<path d="M24 286H724" stroke="{LINE}"/>')
s.append('<g clip-path="url(#logclip)">')
line_h=17
total=len(logs)*line_h
s.append(f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="0 {-total}" dur="{len(logs)*1.5:.0f}s" repeatCount="indefinite"/>')
for rep in range(2):
    for i,l in enumerate(logs):
        col = AMB if l.startswith("[warn]") else MUT
        s.append(f'<text class="m" x="24" y="{308+rep*total+i*line_h}" font-size="9.5" letter-spacing="0.8" fill="{col}">{l}</text>')
s.append('</g></g>')
s.append(f'<rect x="740" y="24" width="1" height="{H-48}" fill="{LINE}"/>')
s.append('</svg>')
open(f"{OUT}/board{SFX}.svg","w").write("\n".join(s))
print("board.svg", os.path.getsize(f"{OUT}/board{SFX}.svg"))