import json, math, os, random, sys
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
# Five slices need five slots but only four hues clear every gate, so the
# fifth is the fill tint and the order keeps it away from clay, which it is
# a lightness variant of. Adjacent pairs are what a stacked bar has to
# separate; tools/check_palette.py checks them.
SER = [T["c2"], T["c1"], T["c3"], T["c4"], T["tint"]]
OTHER = T["mut"]
BAR = T["c1"]                     # commit cadence is a single series
W,H=1200,300; PY=20; PH=260
AX,AW=20,738; BX,BW=770,410

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
months = json.load(open(os.path.join(DATA, "mine.json")))["months"]
lang = json.load(open(os.path.join(DATA, "lang.json")))
def mseq(a,b):
    y,m=map(int,a.split('-')); Y,M=map(int,b.split('-')); out=[]
    while (y,m)<=(Y,M):
        out.append(f"{y:04d}-{m:02d}"); m+=1
        if m==13: y,m=y+1,1
    return out
keys=mseq(min(months),max(months))
vals=[months.get(k,0) for k in keys]
tot=sum(vals); act=sum(1 for v in vals if v>0)
nz=sorted(v for v in vals if v>0); med=(nz[len(nz)//2-1]+nz[len(nz)//2])/2 if len(nz)%2==0 else nz[len(nz)//2]
peak=max(vals); peak_i=vals.index(peak); last_i=max(i for i,v in enumerate(vals) if v>0)

L=lang['lang']; ltot=sum(L.values())
top=sorted(L.items(), key=lambda kv:-kv[1])[:5]
other=ltot-sum(v for _,v in top)
segs=[(k, 100*v/ltot) for k,v in top]+[("Other", 100*other/ltot)]
cols=SER+[OTHER]

s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" '
   f'aria-label="Two charts. Left: monthly commit cadence, {tot} commits authored across {len(keys)} months from {keys[0]} to {keys[-1]}, peaking at {peak} in one month, median {med:.0f} in active months. '
   f'Right: source-byte mix across {lang["repos"]} repositories - ' + ", ".join(f"{k} {p:.1f} percent" for k,p in segs) + '.">',
   '<title>Repository telemetry</title>',
   f'''<defs>
<pattern id="g3" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" stroke="{GRID}" stroke-width="1"/></pattern>
<style>.m{{font-family:{MONO}}} .t{{font-size:11.5px;letter-spacing:2.2px;font-weight:700}}
 .sub{{font-size:9px;letter-spacing:1.3px}} .met{{font-size:9px;letter-spacing:1.5px}}
 .ax{{font-size:9.5px;letter-spacing:1.1px}} .lg{{font-size:9.5px;letter-spacing:0.9px}}</style>
</defs>''',
   f'<rect width="{W}" height="{H}" fill="{BG0}"/>']

def frame(x,w,idx,title,sub,metric,accent):
    return "\n".join([f'<rect x="{x}" y="{PY}" width="{w}" height="{PH}" rx="10" fill="{PANEL}" stroke="{LINE}"/>',
      f'<rect x="{x}" y="{PY}" width="{w}" height="{PH}" rx="10" fill="url(#g3)" opacity="0.5"/>',
      f'<path d="M{x+10} {PY}h58" stroke="{accent}" stroke-width="2"/>',
      f'<text class="m t" x="{x+16}" y="{PY+30}" fill="{accent}">{idx}</text>',
      f'<text class="m t" x="{x+44}" y="{PY+30}" fill="{TXT}">{title}</text>',
      f'<text class="m sub" x="{x+16}" y="{PY+48}" fill="{MUT}">{sub}</text>',
      f'<path d="M{x+16} {PY+PH-30}h{w-32}" stroke="{LINE}"/>',
      f'<text class="m met" x="{x+16}" y="{PY+PH-14}" fill="{accent}" opacity="0.9">{metric}</text>'])

# ---------------- 04 commit cadence (single series -> no legend)
s.append(frame(AX,AW,"06","COMMIT CADENCE",
   f'{tot} commits authored · {keys[0]} → {keys[-1]} · per month',
   f'{act} ACTIVE MONTHS · MEDIAN {med:.0f} · PEAK {peak}', CY))
x0,x1 = AX+40, AX+AW-18
yb, yt = PY+208, PY+92
pitch=(x1-x0)/len(keys); bw=min(9.0, pitch-2.0)
ymax=50
for gv in (0,25,50):
    gy=yb-(gv/ymax)*(yb-yt)
    s.append(f'<path d="M{x0} {gy:.1f}H{x1:.0f}" stroke="{LINE}" stroke-dasharray="{"none" if gv==0 else "2 5"}" opacity="{1 if gv==0 else 0.8}"/>')
    s.append(f'<text class="m ax" x="{x0-8}" y="{gy+3:.1f}" fill="{MUT}" text-anchor="end">{gv}</text>')
for i,(k,v) in enumerate(zip(keys,vals)):
    if v==0: continue
    bx=x0+i*pitch+(pitch-bw)/2; bh=(v/ymax)*(yb-yt); r=min(4.0,bw/2,bh)
    s.append(f'<path d="M{bx:.1f} {yb}v{-(bh-r):.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {-r:.1f}h{bw-2*r:.1f}a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {r:.1f}V{yb}z" fill="{BAR}">'
             f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{0.5+i*0.018:.2f}s" fill="freeze"/></path>')
for i,lab in ((peak_i,f"{peak}"),(last_i,f"{vals[last_i]}")):
    if i==peak_i or vals[i]>=12:
        bx=x0+i*pitch+pitch/2; bh=(vals[i]/ymax)*(yb-yt)
        s.append(f'<text class="m ax" x="{bx:.1f}" y="{yb-bh-7:.1f}" fill="{TXT}" text-anchor="middle">{lab}</text>')
seen=set()
for i,k in enumerate(keys):
    y,m=k.split('-')
    if m=='01' and y not in seen:
        seen.add(y); tx=x0+i*pitch+pitch/2
        s.append(f'<path d="M{tx:.1f} {yb}v5" stroke="{LINE}"/>')
        s.append(f'<text class="m ax" x="{tx:.1f}" y="{yb+17}" fill="{MUT}" text-anchor="middle">{y}</text>')
if keys[0].split('-')[1] != '01':
    s.append(f'<path d="M{x0+pitch/2:.1f} {yb}v5" stroke="{LINE}"/>')
    s.append(f'<text class="m ax" x="{x0+pitch/2:.1f}" y="{yb+17}" fill="{MUT}" text-anchor="middle">{keys[0].split("-")[0]}</text>')
s.append(f'<text class="m ax" x="{x0}" y="{yt-8}" fill="{MUT}">commits / month</text>')

# ---------------- 05 source mix (stacked share bar + legend)
s.append(frame(BX,BW,"07","SOURCE MIX",
   f'bytes tracked across {lang["repos"]} own repos', "PYTHON + C++ ON ROS 2 · URDF/XACRO · CMAKE", VIO))
sx0,sw = BX+16, BW-32
sy, sh = PY+84, 28
GAP=2.0
cur=sx0
for i,((name,pct),c) in enumerate(zip(segs,cols)):
    w=sw*pct/100 - (GAP if i<len(segs)-1 else 0)
    rx = 4 if (i==0 or i==len(segs)-1) else 0
    s.append(f'<rect x="{cur:.1f}" y="{sy}" width="{max(1,w):.1f}" height="{sh}" rx="{rx}" fill="{c}">'
             f'<animate attributeName="width" values="0;{max(1,w):.1f}" dur="0.8s" begin="{0.3+i*0.09:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.9 0.2 1"/></rect>')
    if i<4 and w>52:
        s.append(f'<text class="m ax" x="{cur+w/2:.1f}" y="{sy+sh/2+3.4:.1f}" fill="{PANEL}" text-anchor="middle" opacity="0.95">{pct:.1f}%</text>')
    cur+=w+GAP
lx=[BX+16, BX+16+196]
for i,((name,pct),c) in enumerate(zip(segs,cols)):
    col,row=i//3,i%3
    ex,ey = lx[col], PY+142+row*24
    s.append(f'<rect x="{ex}" y="{ey-8}" width="10" height="10" rx="2.5" fill="{c}"/>')
    s.append(f'<text class="m lg" x="{ex+17}" y="{ey}" fill="{TXT}">{name}</text>')
    s.append(f'<text class="m lg" x="{ex+172}" y="{ey}" fill="{MUT}" text-anchor="end">{pct:.1f}%</text>')
s.append(f'<text class="m ax" x="{BX+16}" y="{PY+214}" fill="{MUT}" opacity="0.85">{ltot/1048576:.2f} MiB tracked  ·  forked upstreams excluded</text>')
s.append('</svg>')
open(f"{OUT}/stats{SFX}.svg","w").write("\n".join(s))
print("stats.svg", os.path.getsize(f"{OUT}/stats{SFX}.svg"))
print("months",len(keys),"total",tot,"active",act,"median",med,"peak",peak)
print("segs", [(k, round(p,1)) for k,p in segs])