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
CX, CYY, RMAX, DUR = 988.0, 172.0, 130.0, 4.0

def polar(px,py):
    dx,dy=px-CX,py-CYY
    return math.hypot(dx,dy), math.degrees(math.atan2(dy,dx))%360.0
def seg(p,q,step=8.5,j=1.5):
    (x1,y1),(x2,y2)=p,q; L=math.hypot(x2-x1,y2-y1); n=max(2,int(L/step))
    return [(x1+(x2-x1)*i/n+random.uniform(-j,j), y1+(y2-y1)*i/n+random.uniform(-j,j)) for i in range(n+1)]

random.seed(11)
walls=[((CX-126,CY_ := CYY-86),(CX-18,CYY-114)), ((CX-18,CYY-114),(CX+70,CYY-78)),
       ((CX+84,CYY-52),(CX+112,CYY+46)), ((CX-118,CYY+44),(CX-24,CYY+96)),
       ((CX-132,CYY-40),(CX-124,CYY+30)), ((CX+18,CYY+72),(CX+86,CYY+80)),
       ((CX-40,CYY+2),(CX+4,CYY+2)), ((CX+4,CYY+2),(CX+4,CYY+40)), ((CX-40,CYY+2),(CX-40,CYY+40))]
pts=[]
for a,b in walls: pts+=seg(a,b)
for _ in range(12):
    ang=random.uniform(0,360); rr=random.uniform(45,RMAX)
    pts.append((CX+rr*math.cos(math.radians(ang)), CYY+rr*math.sin(math.radians(ang))))
pts=[p for p in pts if polar(*p)[0]<=RMAX-3]
blips=[(px,py,(polar(px,py)[1]/360.0)*DUR) for px,py in pts]

h=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" width="1200" height="360" fill="none" role="img" aria-label="Mohammed Abdul Rahman, Robotics Engineer, ROS 2 and MoveIt 2 developer, MS Robotics at Northeastern University">',
   '<title>Mohammed Abdul Rahman - Robotics Engineer</title>',
   '<desc>Animated banner. A rotating LiDAR builds a point cloud of a room, a telemetry column streams velocity and planner-latency traces through a ROS node graph, and the job title cycles.</desc>',
   f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T['sunk']}"/><stop offset="0.55" stop-color="{BG0}"/><stop offset="1" stop-color="{T['panel']}"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="{CY}" stop-opacity="0.10"/><stop offset="0.55" stop-color="{CY}" stop-opacity="0.03"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></radialGradient>
<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset="0.6" stop-color="{VIO}"/><stop offset="1" stop-color="{RED}"/></linearGradient>
<pattern id="grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0V34" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="scope"><circle cx="{CX}" cy="{CYY}" r="{RMAX}"/></clipPath>
<clipPath id="spk"><rect x="520" y="0" width="270" height="360"/></clipPath>
<style>
 .m{{font-family:{MONO}}}
 .blip{{animation:ping {DUR}s linear infinite}}
 @keyframes ping{{0%{{opacity:1;r:2.7}}5%{{opacity:1;r:2.7}}28%{{opacity:.34;r:2.1}}100%{{opacity:.13;r:2.1}}}}
 .cursor{{animation:blink 1.05s steps(1,end) infinite}}
 @keyframes blink{{0%,49%{{fill-opacity:1}}50%,100%{{fill-opacity:0}}}}
 .dot{{animation:pulse 1.9s ease-in-out infinite}}
 @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
</style></defs>''',
   '<rect width="1200" height="360" fill="url(#bg)"/>',
   '<rect width="1200" height="360" fill="url(#grid)" opacity="0.55"/>',
   f'<ellipse cx="{CX}" cy="{CYY}" rx="235" ry="205" fill="url(#halo)"/>',
   f'<rect x="0.5" y="0.5" width="1199" height="359" stroke="{LINE}"/>']
for x,y,sx,sy in ((1,1,1,1),(1199,1,-1,1),(1,359,1,-1),(1199,359,-1,-1)):
    h.append(f'<path d="M{x} {y+16*sy}V{y}H{x+16*sx}" stroke="{CY}" stroke-width="1.6" opacity="0.85"/>')

# ---------- LEFT
h.append(f'<circle class="dot" cx="66" cy="74" r="3.6" fill="{GRN}"/>')
h.append(f'<text class="m" x="80" y="78" font-size="11.5" letter-spacing="3.4" fill="{GRN}">SYSTEM ONLINE</text>')
h.append(f'<text class="m" x="252" y="78" font-size="11.5" letter-spacing="3.4" fill="{MUT}">//  BERKELEY, CA</text>')
h.append(f'<text class="m" x="64" y="146" font-size="40" font-weight="700" letter-spacing="1.5" fill="{TXT}">MOHAMMED</text>')
h.append(f'<text class="m" x="64" y="196" font-size="40" font-weight="700" letter-spacing="1.5" fill="{TXT}">ABDUL RAHMAN</text>')
h.append(f'<rect x="64" y="212" width="0" height="3" fill="url(#rule)"><animate attributeName="width" values="0;396" dur="1.3s" fill="freeze" calcMode="spline" keySplines="0.2 0.9 0.2 1"/></rect>')
roles=["ROBOTICS ENGINEER","ROS 2 / MOVEIT 2 DEVELOPER","PHYSICAL AI + MOTION PLANNING","MS ROBOTICS · NORTHEASTERN '27"]
TOT=len(roles)*3.4
for i,r in enumerate(roles):
    h.append(f'<text class="m" x="64" y="248" font-size="16" letter-spacing="1.5" fill="{CY}" opacity="0">{r}'
             f'<tspan class="cursor" fill="{RED}"> █</tspan>'
             f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.012;0.235;0.25;1" dur="{TOT}s" begin="{i*3.4}s" repeatCount="indefinite"/></text>')
cx=64
for label,col in (("ROS 2 JAZZY",CY),("ISAAC SIM",AMB),("C++ / PYTHON",GRN),("PHYSICAL AI",RED)):
    w=len(label)*7.3+24
    h.append(f'<rect x="{cx}" y="274" width="{w:.0f}" height="26" rx="13" fill="{col}" fill-opacity="0.09" stroke="{col}" stroke-opacity="0.45"/>'
             f'<text class="m" x="{cx+w/2:.0f}" y="291" font-size="10.5" letter-spacing="1.6" fill="{col}" text-anchor="middle">{label}</text>')
    cx+=w+10
h.append(f'<text class="m" x="64" y="332" font-size="10.5" letter-spacing="2" fill="{MUT}" opacity="0.85">building robots that may work</text>')

# ---------- MIDDLE telemetry
MX,MW=520,270
h.append(f'<text class="m" x="{MX}" y="80" font-size="9.5" letter-spacing="2.6" fill="{MUT}">TELEMETRY</text>')
h.append(f'<path d="M{MX+72} 76H{MX+MW}" stroke="{LINE}"/>')
def spark(y0,label,val,col,seed,amp=11.0):
    n=64; W=MW
    ys=[]
    for i in range(n*2+1):
        t=(i/n)
        v=(0.55*math.sin(2*math.pi*t+seed)+0.30*math.sin(6*math.pi*t+1.1+seed)+0.15*math.sin(10*math.pi*t+2.3+seed))
        ys.append(v)
    mid=y0+30
    d="M"+" L".join(f"{MX+(i/n)*W:.1f} {mid-ys[i]*amp:.1f}" for i in range(n*2+1))
    o=[f'<text class="m" x="{MX}" y="{y0+8}" font-size="9" letter-spacing="1.4" fill="{MUT}">{label}</text>',
       f'<text class="m" x="{MX+MW}" y="{y0+8}" font-size="9" letter-spacing="1.4" fill="{col}" text-anchor="end">{val}</text>',
       f'<path d="M{MX} {mid}H{MX+MW}" stroke="{LINE}" stroke-dasharray="2 4"/>',
       f'<g clip-path="url(#spk)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="{-MW} 0" dur="{5.5+seed:.1f}s" repeatCount="indefinite"/>',
       f'<path d="{d}" stroke="{col}" stroke-width="1.5" fill="none" opacity="0.95"/></g></g>',
       f'<path d="M{MX} {y0+14}h5M{MX} {mid}h5M{MX} {y0+46}h5" stroke="{LINE}"/>']
    return "\n".join(o)
h.append(spark(96,  "/cmd_vel  linear.x",  "0.55 m/s",   CY,  0.0))
h.append(spark(152, "/cmd_vel  angular.z", "-0.21 rad/s", AMB, 0.7))
h.append(spark(208, "planner  cycle",      "41 ms",      GRN, 1.4))
gy=286
nodes=[("/scan",CY),("costmap",VIO),("dwa",GRN),("/cmd_vel",AMB)]
nx=MX; boxes=[]
for label,col in nodes:
    w=len(label)*5.3+16
    boxes.append((nx,w,label,col)); nx+=w+18
scale=(MW-(nx-18-MX))/3 if nx-18-MX < MW else 0
nx=MX; boxes=[]
for label,col in nodes:
    w=len(label)*5.3+16
    boxes.append((nx,w,label,col)); nx+=w+18+scale
for i,(bx,w,label,col) in enumerate(boxes):
    h.append(f'<rect x="{bx:.0f}" y="{gy}" width="{w:.0f}" height="20" rx="4" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-opacity="0.45"/>'
             f'<text class="m" x="{bx+w/2:.0f}" y="{gy+13.5}" font-size="8.5" letter-spacing="0.8" fill="{col}" text-anchor="middle">{label}</text>')
    if i<len(boxes)-1:
        x1=bx+w; x2=boxes[i+1][0]
        h.append(f'<path d="M{x1:.0f} {gy+10}H{x2:.0f}" stroke="{LINE}" stroke-width="1.4"/>'
                 f'<path d="M{x2-5:.0f} {gy+7}l4 3l-4 3" stroke="{MUT}" stroke-width="1.2" fill="none"/>'
                 f'<circle cy="{gy+10}" r="2.1" fill="{CY}"><animate attributeName="cx" values="{x1:.0f};{x2:.0f}" dur="1.1s" begin="{i*0.36:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" dur="1.1s" begin="{i*0.36:.2f}s" repeatCount="indefinite"/></circle>')
h.append(f'<text class="m" x="{MX}" y="{gy+34}" font-size="8.5" letter-spacing="1.5" fill="{MUT}" opacity="0.8">rqt_graph  ·  4 nodes  ·  0 dropped</text>')

# ---------- SCOPE
for i,rr in enumerate((RMAX*0.33,RMAX*0.62,RMAX*0.87,RMAX)):
    h.append(f'<circle cx="{CX}" cy="{CYY}" r="{rr:.1f}" stroke="{CY}" stroke-opacity="{0.16 if i<3 else 0.30}" fill="none"/>')
for ang in range(0,360,30):
    a=math.radians(ang)
    h.append(f'<line x1="{CX+(RMAX-9)*math.cos(a):.1f}" y1="{CYY+(RMAX-9)*math.sin(a):.1f}" x2="{CX+RMAX*math.cos(a):.1f}" y2="{CYY+RMAX*math.sin(a):.1f}" stroke="{CY}" stroke-opacity="0.35"/>')
h.append(f'<circle cx="{CX}" cy="{CYY}" r="14" stroke="{CY}" fill="none"><animate attributeName="r" values="14;{RMAX:.0f}" dur="{DUR}s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values="0.40;0" dur="{DUR}s" repeatCount="indefinite"/></circle>')
h.append(f'<g clip-path="url(#scope)"><g transform="translate({CX} {CYY})"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{DUR}s" repeatCount="indefinite" additive="sum"/>')
ST,SP=14,52.0
for i in range(ST):
    r0,r1=math.radians(-SP+(SP/ST)*i), math.radians(-SP+(SP/ST)*(i+1))
    h.append(f'<path d="M0 0L{RMAX*math.cos(r0):.1f} {RMAX*math.sin(r0):.1f}A{RMAX:.0f} {RMAX:.0f} 0 0 1 {RMAX*math.cos(r1):.1f} {RMAX*math.sin(r1):.1f}Z" fill="{CY}" opacity="{0.020+0.021*i:.3f}"/>')
h.append(f'<line x1="0" y1="0" x2="{RMAX:.0f}" y2="0" stroke="{CY}" stroke-width="1.6" opacity="0.95" filter="url(#glow)"/></g></g>')
for px,py,d in blips:
    h.append(f'<circle class="blip" cx="{px:.1f}" cy="{py:.1f}" r="2.7" fill="{CY}" style="animation-delay:{d:.2f}s"/>')
def bracket(x,y,w,hh,label,delay,col=AMB):
    s=9
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.03;0.30;0.36;1" dur="{DUR}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'<path d="M{x} {y+s}V{y}H{x+s} M{x+w-s} {y}H{x+w}V{y+s} M{x+w} {y+hh-s}V{y+hh}H{x+w-s} M{x+s} {y+hh}H{x}V{y+hh-s}" stroke="{col}" stroke-width="1.6" fill="none"/>'
            f'<text class="m" x="{x}" y="{y-6}" font-size="9.5" letter-spacing="1.2" fill="{col}">{label}</text></g>')
h.append(bracket(CX+72, CYY-64, 52, 122, "WALL 1.62m", 0.24))
h.append(bracket(CX-134, CYY+34, 122, 70, "OBS 2.07m", 2.44, RED))
h.append(bracket(CX-138, CYY-124, 132, 46, "WALL 3.10m", 3.34))
h.append(f'<circle cx="{CX}" cy="{CYY}" r="17" fill="{CY}" opacity="0.10"/>'
         f'<rect x="{CX-9}" y="{CYY-9}" width="18" height="18" rx="4" fill="{PANEL}" stroke="{CY}" stroke-width="1.6"/>'
         f'<path d="M{CX-3} {CYY-3.5}L{CX+4.5} {CYY}L{CX-3} {CYY+3.5}Z" fill="{CY}"/>'
         f'<circle class="dot" cx="{CX}" cy="{CYY}" r="24" stroke="{CY}" fill="none" opacity="0.30"/>')
for lbl,rr in (("2m",RMAX*0.33),("4m",RMAX*0.62),("6m",RMAX*0.87)):
    h.append(f'<text class="m" x="{CX+4}" y="{CYY-rr+11:.0f}" font-size="8.5" fill="{MUT}" opacity="0.7">{lbl}</text>')
h.append(f'<text class="m" x="{CX+RMAX:.0f}" y="{CYY+RMAX+26:.0f}" font-size="9" letter-spacing="1.7" fill="{MUT}" text-anchor="end">/scan  10 Hz  ·  360°  ·  {len(blips)} RETURNS  ·  37.87°N 122.27°W</text>')
h.append('</svg>')
open(f"{OUT}/hero{SFX}.svg","w").write("\n".join(h))
print("hero.svg", os.path.getsize(f"{OUT}/hero{SFX}.svg"), len(blips), "blips")