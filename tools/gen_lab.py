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
CY = T["c1"]; RED = T["c2"]; VIO = T["c3"]; GRN = T["c4"]; AMB = T["c4"]
MONO = MONO_STACK
W,H=1200,300
PX=[20,411,802]; PW=378; PY=20; PH=260

def hx(c): return tuple(int(c[i:i+2],16) for i in (1,3,5))
def lerp(a,b,t):
    A,B=hx(a),hx(b); return "#%02x%02x%02x"%tuple(int(A[i]+(B[i]-A[i])*t) for i in range(3))

s=[]
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="Three animated robotics simulations: DWA local planner rollouts, reactive replanning with kinematic redundancy on a UR12e, and a quadruped trot gait">')
s.append('<title>The Lab</title><desc>Left: a DWA local planner samples 15 velocity rollouts, scores them and commits to the lowest-cost arc. Middle: a UR12e holds a fixed end-effector pose while switching between two IK solutions on the elbow self-motion circle to dodge an obstacle. Right: a 12-axis quadruped walking a trot gait.</desc>')
s.append(f'''<defs>
<pattern id="g2" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="gl" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<style>
 .m{{font-family:{MONO}}}
 .t{{font-size:11.5px;letter-spacing:2.2px;font-weight:700}}
 .sub{{font-size:9px;letter-spacing:1.3px}}
 .met{{font-size:9px;letter-spacing:1.5px}}
 .idx{{font-size:11.5px;letter-spacing:2.2px;font-weight:700}}
</style>
</defs>''')
s.append(f'<rect width="{W}" height="{H}" fill="{BG0}"/>')

def panel(i,idx,title,sub,metric,accent):
    x=PX[i]
    o=[f'<g><rect x="{x}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="{PANEL}" stroke="{LINE}"/>',
       f'<rect x="{x}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="url(#g2)" opacity="0.5"/>',
       f'<path d="M{x+10} {PY}h58" stroke="{accent}" stroke-width="2"/>',
       f'<text class="m idx" x="{x+16}" y="{PY+30}" fill="{accent}">{idx}</text>',
       f'<text class="m t" x="{x+44}" y="{PY+30}" fill="{TXT}">{title}</text>',
       f'<text class="m sub" x="{x+16}" y="{PY+48}" fill="{MUT}">{sub}</text>',
       f'<path d="M{x+16} {PY+PH-30}h{PW-32}" stroke="{LINE}"/>',
       f'<text class="m met" x="{x+16}" y="{PY+PH-14}" fill="{accent}" opacity="0.9">{metric}</text>',
       '</g>']
    return "\n".join(o)

# ============================================ 01  DWA
s.append(panel(0,"01","LOCAL PLANNER / DWA","argmin  \u03b1\u00b7heading + \u03b2\u00b7clearance + \u03b3\u00b7velocity",
               "15 ROLLOUTS · 20 Hz · C++ 2-3x", CY))
RX,RY=PX[0]+40,PY+172
OBS=[(162,214,16),(177,123,14)]
V,T,N=112.0,2.45,15
INFL=7
XMAX,YMIN,YMAX = PX[0]+PW-22, PY+80, PY+PH-30
def rollout(w):
    x,y,th=RX,RY,0.0; pts=[(x,y)]; hit=False; dt=0.05
    for _ in range(int(T/dt)):
        x+=V*math.cos(th)*dt; y+=V*math.sin(th)*dt; th+=w*dt
        for (ox,oy,orr) in OBS:
            if math.hypot(x-ox,y-oy) < orr+INFL: hit=True
        if x>XMAX or y<YMIN or y>YMAX: break
        pts.append((x,y))
    return pts,hit,th
WS=[-0.52+1.04*k/(N-1) for k in range(N)]
sims=[rollout(w) for w in WS]
# place the goal just beyond the best-looking clear upward arc, so the winner is honest
cand=[(i,p,th) for i,(p,h,th) in enumerate(sims) if not h and p[-1][1] < RY-18]
si,sp,sth = max(cand, key=lambda c: c[1][-1][0])
GOAL=(min(XMAX-8, sp[-1][0]+32*math.cos(sth)), max(YMIN+16, sp[-1][1]+32*math.sin(sth)))
rolls=[{"pts":p,"hit":h,"cost":math.hypot(p[-1][0]-GOAL[0], p[-1][1]-GOAL[1])} for p,h,th in sims]
ok=[r for r in rolls if not r["hit"]]
lo,hi=min(r["cost"] for r in ok), max(r["cost"] for r in ok)
best=min(ok,key=lambda r:r["cost"])
s_local=[]
s.append(f'<rect x="{PX[0]+22}" y="{YMIN-2}" width="{XMAX-PX[0]-14}" height="{YMAX-YMIN+8}" rx="4" stroke="{LINE}" stroke-dasharray="3 5" fill="none" opacity="0.8"/>')
s.append(f'<text class="m" x="{XMAX-4}" y="{YMIN-8}" font-size="8" letter-spacing="1.2" fill="{MUT}" opacity="0.75" text-anchor="end">LOCAL COSTMAP</text>')
for (ox,oy,orr) in OBS:
    s.append(f'<circle cx="{ox}" cy="{oy}" r="{orr+INFL}" stroke="{RED}" stroke-opacity="0.30" stroke-dasharray="3 4" fill="none"/>')
    s.append(f'<circle cx="{ox}" cy="{oy}" r="{orr}" fill="{RED}" fill-opacity="0.16" stroke="{RED}" stroke-opacity="0.75"/>')
bd=None
for j,r in enumerate(rolls):
    d="M"+" L".join(f"{q[0]:.1f} {q[1]:.1f}" for q in r["pts"])
    L=sum(math.hypot(r["pts"][i+1][0]-r["pts"][i][0], r["pts"][i+1][1]-r["pts"][i][1]) for i in range(len(r["pts"])-1))+4
    isb = r is best
    if isb: bd=d
    if r["hit"]: col,op=RED,0.5
    else:
        t=(r["cost"]-lo)/max(1e-6,hi-lo); col,op=lerp(CY,AMB,t),0.8
    s.append(f'<path d="{d}" stroke="{GRN if isb else col}" stroke-width="{2.6 if isb else 1.35}" fill="none" opacity="0" stroke-linecap="round" '
             f'stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}">'
             f'<animate attributeName="stroke-dashoffset" values="{L:.0f};0;0;0" keyTimes="0;0.20;0.86;1" dur="5s" begin="{j*0.022:.2f}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;{op};{op};{1 if isb else 0.09};{0.9 if isb else 0}" keyTimes="0;0.06;0.40;0.52;1" dur="5s" begin="{j*0.022:.2f}s" repeatCount="indefinite"/>'
             + (f'<animate attributeName="stroke-width" values="2.6;3.4;2.6" dur="1.1s" begin="2.6s" repeatCount="indefinite"/>' if isb else '') + '</path>')
s.append(f'<path id="bestp" d="{bd}" fill="none" stroke="none"/>')
gx,gy=int(GOAL[0]),int(GOAL[1])
s.append(f'<circle cx="{gx}" cy="{gy}" r="13" stroke="{GRN}" stroke-opacity="0.35" stroke-dasharray="2 3" fill="none"/>')
s.append(f'<path d="M{gx} {gy-7}L{gx+2.1} {gy-2.1}L{gx+7} {gy}L{gx+2.1} {gy+2.1}L{gx} {gy+7}L{gx-2.1} {gy+2.1}L{gx-7} {gy}L{gx-2.1} {gy-2.1}Z" fill="{GRN}"/>')
s.append(f'<text class="m" x="{gx}" y="{gy+25}" font-size="8.5" letter-spacing="1.4" fill="{GRN}" text-anchor="middle">GOAL</text>')
s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.52;0.58;0.95;1" dur="5s" repeatCount="indefinite"/>'
         f'<g><path d="M-6 -5.5L7 0L-6 5.5L-3.4 0Z" fill="{GRN}" filter="url(#gl)"/>'
         f'<animateMotion dur="5s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;0.55;0.94;1" calcMode="linear" rotate="auto"><mpath href="#bestp"/></animateMotion></g></g>')
s.append(f'<rect x="{RX-9}" y="{RY-9}" width="18" height="18" rx="4" fill="{PANEL}" stroke="{CY}" stroke-width="1.5"/>')
s.append(f'<path d="M{RX-3} {RY-3.5}L{RX+4.5} {RY}L{RX-3} {RY+3.5}Z" fill="{CY}"/>')
s.append(f'<text class="m met" x="{PX[0]+PW-16}" y="{PY+PH-14}" fill="{GRN}" text-anchor="end" opacity="0">'
         f'v 0.55 \u00b7 \u03c9 {WS[rolls.index(best)]:+.2f}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.52;0.58;0.95;1" dur="5s" repeatCount="indefinite"/></text>')

# ============================================ 02  IK redundancy
s.append(panel(1,"02","REACTIVE REPLANNING / UR12e","one EE pose \u00b7 many arm solutions",
               "120 IK SOLUTIONS  ·  BIT*  ·  REPLAN 1-3 s", VIO))
BX,BY=PX[1]+130,PY+200
TXP,TYP=PX[1]+205,PY+126
L1,L2=80.0,70.0
dx,dy=TXP-BX,TYP-BY; d=math.hypot(dx,dy)
a=(d*d+L1*L1-L2*L2)/(2*d); hh=math.sqrt(max(0.0,L1*L1-a*a))
ux,uy=dx/d,dy/d
Mx,My=BX+ux*a,BY+uy*a
J1=(Mx-uy*hh, My+ux*hh)   # elbow "down/right"
J2=(Mx+uy*hh, My-ux*hh)   # elbow "up/left"
OBX,OBY,OBR = J1[0]-6, J1[1]+4, 19
# self-motion circle through both elbow solutions
s.append(f'<circle cx="{Mx:.1f}" cy="{My:.1f}" r="{hh:.1f}" stroke="{VIO}" stroke-opacity="0.30" stroke-dasharray="3 5" fill="none"/>')
s.append(f'<text class="m" x="{Mx:.0f}" y="{My-hh-9:.0f}" font-size="8" letter-spacing="1.3" fill="{VIO}" opacity="0.75" text-anchor="middle">SELF-MOTION MANIFOLD</text>')
for i in range(16):
    th=2*math.pi*i/16
    px,py=Mx+hh*math.cos(th), My+hh*math.sin(th)
    s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.9" fill="{VIO}" opacity="0.16">'
             f'<animate attributeName="opacity" values="0.16;0.7;0.16" dur="2.6s" begin="{i*0.09:.2f}s" repeatCount="indefinite"/></circle>')
s.append(f'<path d="M{BX-34} {BY}h68l-9 20h-50Z" fill="{PANEL}" stroke="{LINE}"/>')
for i in range(6):
    s.append(f'<line x1="{BX-30+i*12}" y1="{BY+3}" x2="{BX-34+i*12}" y2="{BY+17}" stroke="{LINE}"/>')
P1=f"{BX} {BY} {J1[0]:.1f} {J1[1]:.1f} {TXP} {TYP}"
P2=f"{BX} {BY} {J2[0]:.1f} {J2[1]:.1f} {TXP} {TYP}"
KT="0;0.277;0.354;0.508;0.831;0.923;1"
VALS=f"{P1};{P1};{P1};{P2};{P2};{P1};{P1}"
DUR="6.5s"
s.append(f'<polyline points="{P1}" stroke="{TXT}" stroke-opacity="0.20" stroke-width="15" fill="none" stroke-linecap="round" stroke-linejoin="round">'
         f'<animate attributeName="points" values="{VALS}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" keySplines="0 0 1 1;0 0 1 1;.4 0 .2 1;0 0 1 1;.4 0 .2 1;0 0 1 1" repeatCount="indefinite"/></polyline>')
s.append(f'<polyline points="{P1}" stroke="{CY}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round">'
         f'<animate attributeName="points" values="{VALS}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" keySplines="0 0 1 1;0 0 1 1;.4 0 .2 1;0 0 1 1;.4 0 .2 1;0 0 1 1" repeatCount="indefinite"/></polyline>')
s.append(f'<circle cx="{J1[0]:.1f}" cy="{J1[1]:.1f}" r="6" fill="{PANEL}" stroke="{CY}" stroke-width="2.2">'
         f'<animate attributeName="cx" values="{J1[0]:.1f};{J1[0]:.1f};{J1[0]:.1f};{J2[0]:.1f};{J2[0]:.1f};{J1[0]:.1f};{J1[0]:.1f}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" keySplines="0 0 1 1;0 0 1 1;.4 0 .2 1;0 0 1 1;.4 0 .2 1;0 0 1 1" repeatCount="indefinite"/>'
         f'<animate attributeName="cy" values="{J1[1]:.1f};{J1[1]:.1f};{J1[1]:.1f};{J2[1]:.1f};{J2[1]:.1f};{J1[1]:.1f};{J1[1]:.1f}" keyTimes="{KT}" dur="{DUR}" calcMode="spline" keySplines="0 0 1 1;0 0 1 1;.4 0 .2 1;0 0 1 1;.4 0 .2 1;0 0 1 1" repeatCount="indefinite"/></circle>')
s.append(f'<circle cx="{BX}" cy="{BY}" r="7" fill="{PANEL}" stroke="{CY}" stroke-width="2.2"/>')
ang=math.degrees(math.atan2(TYP-J1[1],TXP-J1[0]))
s.append(f'<g transform="translate({TXP} {TYP})"><circle r="12" fill="{GRN}" fill-opacity="0.10" stroke="{GRN}" stroke-opacity="0.5" stroke-dasharray="2 3"/>'
         f'<path d="M-4 -9v18M4 -9v18" stroke="{GRN}" stroke-width="2.6" stroke-linecap="round"/>'
         f'<path d="M-9 0h18" stroke="{GRN}" stroke-width="1" opacity="0.5"/></g>')
s.append(f'<text class="m" x="{J1[0]+13:.0f}" y="{J1[1]+16:.0f}" font-size="8" letter-spacing="1.1" fill="{CY}" opacity="0">IK #12'
         f'<animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="0;0.26;0.30;0.84;0.88;1" dur="{DUR}" repeatCount="indefinite"/></text>')
s.append(f'<text class="m" x="{J2[0]-13:.0f}" y="{J2[1]-11:.0f}" font-size="8" letter-spacing="1.1" fill="{VIO}" text-anchor="end" opacity="0">IK #47'
         f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.36;0.40;0.82;0.86;1" dur="{DUR}" repeatCount="indefinite"/></text>')
s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;1;0;0" keyTimes="0;0.26;0.30;0.83;0.86;0.92;1" dur="{DUR}" repeatCount="indefinite"/>'
         f'<circle cx="{OBX:.0f}" cy="{OBY:.0f}" r="{OBR+8}" stroke="{RED}" stroke-opacity="0.28" stroke-dasharray="3 4" fill="none"/>'
         f'<circle cx="{OBX:.0f}" cy="{OBY:.0f}" r="{OBR}" fill="{RED}" fill-opacity="0.18" stroke="{RED}" stroke-width="1.6"/>'
         f'<path d="M{OBX-6:.0f} {OBY-6:.0f}l12 12M{OBX+6:.0f} {OBY-6:.0f}l-12 12" stroke="{RED}" stroke-width="1.6"/></g>')
for txt,col,kt,vals in (("NOMINAL",GRN,"0;0.26;0.28;0.86;0.88;1","1;1;0;0;1;1"),
                        ("COLLISION",RED,"0;0.27;0.29;0.35;0.37;1","0;0;1;1;0;0"),
                        ("REPLANNED",VIO,"0;0.36;0.38;0.84;0.86;1","0;0;1;1;0;0")):
    s.append(f'<text class="m met" x="{PX[1]+PW-16}" y="{PY+PH-14}" fill="{col}" text-anchor="end" opacity="0">{txt}'
             f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="{DUR}" repeatCount="indefinite"/></text>')

# ============================================ 03  Quadruped
s.append(panel(2,"03","LEGGED LOCOMOTION / K.A.L.B","MIT Cheetah-derived  ·  trot gait  ·  SLAM in Gazebo",
               "12 AXES  ·  ROS 2  ·  IRL DEMOS -> UNITREE GO2", AMB))
BCX,BCY=PX[2]+PW/2,PY+128
BW,BH=132,30
GY=PY+213
LL1,LL2=40.0,40.0
STRIDE,LIFT,DUTY=18.0,17.0,0.60
NS=18; CYC=0.95
def foot(ph):
    ph%=1.0
    if ph<DUTY:
        t=ph/DUTY; return (STRIDE-2*STRIDE*t, GY)
    t=(ph-DUTY)/(1-DUTY); return (-STRIDE+2*STRIDE*t, GY-LIFT*math.sin(math.pi*t))
def leg(hx_,hy_,fx,fy,back):
    ddx,ddy=fx-hx_,fy-hy_; dd=math.hypot(ddx,ddy)
    dd=min(dd,LL1+LL2-0.6)
    ddx,ddy=ddx/max(1e-6,math.hypot(fx-hx_,fy-hy_))*dd, ddy/max(1e-6,math.hypot(fx-hx_,fy-hy_))*dd
    aa=(dd*dd+LL1*LL1-LL2*LL2)/(2*dd); hgt=math.sqrt(max(0.0,LL1*LL1-aa*aa))
    ux_,uy_=ddx/dd,ddy/dd
    mx,my=hx_+ux_*aa,hy_+uy_*aa
    sgn=-1 if back else 1
    return (mx+sgn*(-uy_)*hgt, my+sgn*(ux_)*hgt), (hx_+ddx,hy_+ddy)
LEGS=[("FL",-46,0.0,False,1.0),("RL",46,0.5,True,1.0),("FR",-46,0.5,False,0.34),("RR",46,0.0,True,0.34)]
body_vals=[]
for i in range(NS+1):
    t=(i%NS)/NS
    body_vals.append(f"0 {2.6*math.sin(4*math.pi*t):.2f}")
s.append(f'<line x1="{PX[2]+16}" y1="{GY}" x2="{PX[2]+PW-16}" y2="{GY}" stroke="{LINE}" stroke-width="1.5"/>')
s.append(f'<line x1="{PX[2]+16}" y1="{GY+5}" x2="{PX[2]+PW-16}" y2="{GY+5}" stroke="{AMB}" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="10 12">'
         f'<animate attributeName="stroke-dashoffset" values="22;0" dur="{CYC}s" repeatCount="indefinite"/></line>')
for name,hoff,phase,back,op in LEGS:
    dz = 7 if op<0.5 else 0
    pts_vals=[]
    for i in range(NS+1):
        t=(i%NS)/NS
        bob=2.6*math.sin(4*math.pi*t)
        hx_,hy_=BCX+hoff+dz, BCY+BH/2-2+bob-dz*0.7
        fx,fy=foot(t+phase); fx+=hx_; 
        knee,ft=leg(hx_,hy_,fx,fy,back)
        pts_vals.append(f"{hx_:.1f} {hy_:.1f} {knee[0]:.1f} {knee[1]:.1f} {ft[0]:.1f} {ft[1]:.1f}")
    v=";".join(pts_vals)
    s.append(f'<polyline points="{pts_vals[0]}" stroke="{AMB}" stroke-opacity="{op*0.9:.2f}" stroke-width="{5 if op>0.5 else 4}" fill="none" stroke-linecap="round" stroke-linejoin="round">'
             f'<animate attributeName="points" values="{v}" dur="{CYC}s" calcMode="linear" repeatCount="indefinite"/></polyline>')
s.append(f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(body_vals)}" dur="{CYC}s" calcMode="linear" repeatCount="indefinite"/>'
         f'<rect x="{BCX-BW/2}" y="{BCY-BH/2}" width="{BW}" height="{BH}" rx="11" fill="{PANEL}" stroke="{AMB}" stroke-width="2"/>'
         f'<rect x="{BCX-BW/2+8}" y="{BCY-BH/2+7}" width="{BW-16}" height="{BH-14}" rx="6" fill="{AMB}" fill-opacity="0.08"/>'
         f'<circle cx="{BCX+BW/2-16}" cy="{BCY}" r="3.4" fill="{AMB}"><animate attributeName="opacity" values="1;0.2;1" dur="1.3s" repeatCount="indefinite"/></circle>'
         f'<path d="M{BCX+BW/2} {BCY-6}h14" stroke="{AMB}" stroke-width="2"/>'
         f'<circle cx="{BCX+BW/2+18}" cy="{BCY-6}" r="5" fill="{PANEL}" stroke="{CY}" stroke-width="1.8"/>'
         f'<path d="M{BCX-BW/2-4} {BCY-BH/2-14}h22v-6" stroke="{LINE}" stroke-width="1.5"/>'
         f'<text class="m" x="{BCX-BW/2+20}" y="{BCY-BH/2-18}" font-size="8" letter-spacing="1.2" fill="{MUT}">IMU + JOINT ENC</text></g>')
for i in range(3):
    s.append(f'<circle cx="{BCX+BW/2+18}" cy="{BCY-6}" r="7" stroke="{CY}" stroke-opacity="0.5" fill="none">'
             f'<animate attributeName="r" values="7;30" dur="2.4s" begin="{i*0.8:.1f}s" repeatCount="indefinite"/>'
             f'<animate attributeName="stroke-opacity" values="0.5;0" dur="2.4s" begin="{i*0.8:.1f}s" repeatCount="indefinite"/></circle>')
s.append('</svg>')
open(f"{OUT}/lab{SFX}.svg","w").write("\n".join(s))
print("lab.svg", os.path.getsize(f"{OUT}/lab{SFX}.svg"))

# ============================================ divider
d=[]
d.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 16" width="{W}" height="16" fill="none" role="img" aria-label="divider">')
d.append(f'<defs><linearGradient id="sw" x1="0" y1="0" x2="1" y2="0">'
         f'<stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset="0.72" stop-color="{CY}" stop-opacity="0.85"/>'
         f'<stop offset="1" stop-color="{TXT}" stop-opacity="1"/></linearGradient>'
         f'<linearGradient id="bl" x1="0" y1="0" x2="1" y2="0">'
         f'<stop offset="0" stop-color="{LINE}" stop-opacity="0"/><stop offset="0.15" stop-color="{LINE}"/>'
         f'<stop offset="0.85" stop-color="{LINE}"/><stop offset="1" stop-color="{LINE}" stop-opacity="0"/></linearGradient></defs>')
d.append(f'<rect width="{W}" height="16" fill="{BG0}"/>')
d.append(f'<rect x="0" y="8" width="{W}" height="1" fill="url(#bl)"/>')
for x in range(40,W-20,40):
    tall = (x//40)%5==0
    d.append(f'<line x1="{x}" y1="{8-(5 if tall else 2.5)}" x2="{x}" y2="{8+(5 if tall else 2.5)}" stroke="{LINE}" stroke-width="1"/>')
d.append(f'<rect x="-220" y="7" width="220" height="2" fill="url(#sw)" rx="1"><animate attributeName="x" values="-220;{W}" dur="3.4s" repeatCount="indefinite"/></rect>')
d.append('</svg>')
open(f"{OUT}/divider{SFX}.svg","w").write("\n".join(d))
print("divider.svg", os.path.getsize(f"{OUT}/divider{SFX}.svg"))