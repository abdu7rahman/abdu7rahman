#!/usr/bin/env python3
"""Renders a real planner run as an animated SVG for the profile README.

GitHub strips <script> and <iframe> from markdown, so a README cannot host an
interactive demo. It does render animated SVG. This runs the actual planners
from reactive_autonomous_nav on a freshly seeded map and replays the search --
the frames are the expansion order the planner produced, not an illustration.

    python3 tools/gen_run.py            # random map from the clock
    python3 tools/gen_run.py 42         # reproducible
"""
import io, math, os, random, sys, time, types, urllib.request, contextlib
import numpy as np

REPO = "abdu7rahman/reactive_autonomous_nav"
RAW = "https://raw.githubusercontent.com/" + REPO + "/main/reactive_autonomous_nav/"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import EASE_CSS, MONO, SANS, THEMES, suffix                # noqa: E402

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

COLS, ROWS = 78, 46
# Sized so two panels plus their gutters land on 1000, which is roughly the
# width the README column gives an image. Authoring wider meant the browser
# scaled the whole plate down and every label with it.
CELL = 5.72


def stub_ros():
    def mod(name, **attrs):
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[name] = m
        if "." in name:
            p, c = name.rsplit(".", 1)
            if p in sys.modules:
                setattr(sys.modules[p], c, m)
        return m

    class Meta(type):
        def __getattr__(cls, n): return 0

    class Any(metaclass=Meta):
        def __init__(self, *a, **k): pass
        def __getattr__(self, n): return Any()
        def __call__(self, *a, **k): return Any()

    mod("rclpy", init=lambda *a, **k: None, spin=lambda *a, **k: None, shutdown=lambda *a, **k: None)
    mod("rclpy.time", Time=Any); mod("rclpy.duration", Duration=Any)
    mod("rclpy.node", Node=type("Node", (), {"__init__": lambda s, *a, **k: None}))
    mod("rclpy.qos", QoSProfile=Any, DurabilityPolicy=Any, ReliabilityPolicy=Any)
    mod("rclpy.callback_groups", ReentrantCallbackGroup=Any)
    mod("rclpy.executors", MultiThreadedExecutor=Any)
    mod("tf2_ros", TransformListener=Any, Buffer=Any)
    for n, syms in (("nav_msgs", ()), ("nav_msgs.msg", ("OccupancyGrid", "Path", "Odometry")),
                    ("geometry_msgs", ()), ("geometry_msgs.msg", ("PoseStamped", "Point", "Twist", "Pose")),
                    ("std_msgs", ()), ("std_msgs.msg", ("String", "ColorRGBA", "Header")),
                    ("visualization_msgs", ()), ("visualization_msgs.msg", ("Marker", "MarkerArray")),
                    ("builtin_interfaces", ()), ("builtin_interfaces.msg", ("Time",))):
        m = mod(n)
        for s in syms:
            setattr(m, s, Any)


def load(name):
    src = urllib.request.urlopen(RAW + name + ".py", timeout=40).read().decode()
    m = types.ModuleType(name)
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, name, "exec"), m.__dict__)
    sys.modules[name] = m
    return m


def make_map(seed):
    rng = random.Random(seed)
    g = np.zeros((ROWS, COLS), dtype=np.int16)
    g[0, :] = g[-1, :] = g[:, 0] = g[:, -1] = 254
    for _ in range(rng.randint(13, 19)):
        h, w = rng.randint(3, 11), rng.randint(3, 15)
        r, c = rng.randint(2, ROWS - h - 2), rng.randint(2, COLS - w - 2)
        g[r:r + h, c:c + w] = 254
    start, goal = (3, 3), (ROWS - 4, COLS - 4)
    for rc in (start, goal):
        g[rc[0] - 2:rc[0] + 3, rc[1] - 2:rc[1] + 3] = 0
    return g, start, goal


def wire(cls, g):
    n = object.__new__(cls)
    n.global_data = g
    n.global_info = types.SimpleNamespace(resolution=0.05, width=COLS, height=ROWS)
    n.global_origin = (0.0, 0.0)
    n.local_data = None; n.local_info = None; n.local_origin = (0.0, 0.0)
    n.odom_to_map = None; n.current_path = None
    n.get_logger = lambda: types.SimpleNamespace(info=lambda *a, **k: None, warn=lambda *a, **k: None)
    return n


def plan(seed):
    """Try seeds until both planners solve the same map."""
    for s in range(seed, seed + 60):
        g, start, goal = make_map(s)
        try:
            a = wire(A_CLS, g); t0 = time.perf_counter()
            ap, ae = a._astar(start, goal); a_ms = (time.perf_counter() - t0) * 1000
            th = wire(T_CLS, g); t0 = time.perf_counter()
            tp, te = th._theta_star(start, goal); t_ms = (time.perf_counter() - t0) * 1000
        except Exception:
            continue
        if ap and tp and len(ae) > 120:
            return g, start, goal, (ap, ae, a_ms), (tp, te, t_ms), s
    raise SystemExit("no solvable map found")


def frames_of(explored, n=54):
    step = max(1, math.ceil(len(explored) / n))
    return [explored[i:i + step] for i in range(0, len(explored), step)]


def panel(T, ox, title, sub, accent, g, start, goal, path, explored, ms, dur):
    """One planner's map.

    Everything here is authored in its settled state -- the wavefront at its
    resting opacity, the path fully drawn -- and the animation in the stylesheet
    moves away from that and back. That ordering is what lets the whole thing be
    switched off for a reader who asked for less motion without leaving them an
    empty map and no path, which is what the SMIL version did.
    """
    W = COLS * CELL
    out = [f'<g transform="translate({ox} 130)">']
    out.append(f'<text x="0" y="-38" font-family="{SANS}" font-size="14.5" font-weight="600" '
               f'letter-spacing="-0.1" fill="{T["txt"]}">{title}</text>')
    out.append(f'<text x="0" y="-20" font-family="{SANS}" font-size="11" '
               f'fill="{T["mut"]}">{sub}</text>')
    out.append(f'<rect x="-6" y="-6" width="{W+12}" height="{ROWS*CELL+12}" rx="8" '
               f'fill="{T["sunk"]}" stroke="{T["line"]}"/>')
    for r in range(ROWS):
        run = None
        for c in range(COLS + 1):
            solid = c < COLS and g[r, c] >= 253
            if solid and run is None:
                run = c
            elif not solid and run is not None:
                out.append(f'<rect x="{run*CELL:.1f}" y="{r*CELL:.1f}" '
                           f'width="{(c-run)*CELL:.1f}" height="{CELL:.1f}" '
                           f'fill="{T["line"]}"/>')
                run = None
    fr = frames_of(explored)
    per = dur * 0.62 / max(1, len(fr))
    for i, chunk in enumerate(fr):
        d = "".join(f"M{c*CELL:.1f} {r*CELL:.1f}h{CELL:.1f}v{CELL:.1f}h-{CELL:.1f}z"
                    for r, c in chunk)
        # 0.16 was the settled opacity when this was a saturated accent. A
        # neutral at that opacity is invisible, and the difference between the
        # two wavefronts -- 376 cells against 163 -- is the only thing this
        # plate exists to show, so it has to be the second-strongest mark here
        # after the path.
        out.append(f'<path class="wave" style="animation-delay:{i*per:.2f}s" d="{d}" '
                   f'fill="{accent}" opacity="0.7"/>')
    pts = " ".join(f"{c*CELL+CELL/2:.1f},{r*CELL+CELL/2:.1f}" for r, c in path)
    length = sum(math.hypot((path[i+1][0]-path[i][0])*CELL, (path[i+1][1]-path[i][1])*CELL)
                 for i in range(len(path)-1)) + 4
    out.append(f'<polyline class="path" style="--len:{length:.0f}" points="{pts}" fill="none" '
               f'stroke="{T["txt"]}" stroke-width="2.2" stroke-linecap="round" '
               f'stroke-linejoin="round" stroke-dasharray="{length:.0f}" '
               f'stroke-dashoffset="0"/>')
    # Start is filled, goal is a ring. On a monochrome plate the two markers
    # have to differ by shape, because there is no second hue to spend on them.
    sx, sy = start[1] * CELL + CELL / 2, start[0] * CELL + CELL / 2
    gx, gy = goal[1] * CELL + CELL / 2, goal[0] * CELL + CELL / 2
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.5" fill="{T["txt"]}" '
               f'stroke="{T["sunk"]}" stroke-width="2"><title>start</title></circle>')
    out.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="4.5" fill="{T["sunk"]}" '
               f'stroke="{T["txt"]}" stroke-width="2.4"><title>goal</title></circle>')
    out.append(f'<text x="0" y="{ROWS*CELL+26}" font-family="{MONO}" font-size="10.5" '
               f'letter-spacing="0.2" fill="{T["mut"]}">{len(explored):,} expanded  ·  '
               f'{len(path)} waypoints  ·  {ms:.1f} ms</text>')
    out.append("</g>")
    return "\n".join(out)


if __name__ == "__main__":
    stub_ros()
    A_CLS = load("astar_planner").AStarPlannerNode
    T_CLS = load("theta_star_planner").ThetaStarPlannerNode
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.time()) % 100000
    g, start, goal, (ap, ae, a_ms), (tp, te, t_ms), used = plan(seed)

    W = COLS * CELL * 2 + 108
    H = ROWS * CELL + 188
    DUR = 9.0

    # One search, both themes. Rendering them in separate processes meant two
    # searches on two seeds, so the light and dark plates showed different maps
    # and a reader switching theme saw the page change its own history.
    os.makedirs(ASSETS, exist_ok=True)
    for T in THEMES:
        out = os.path.join(ASSETS, "run%s.svg" % suffix(T))
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
             f'width="{W:.0f}" height="{H:.0f}" fill="none" role="img" '
             f'aria-label="A real planner run: A* expanded {len(ae)} nodes for a '
             f'{len(ap)}-waypoint path in {a_ms:.1f} ms; Theta* expanded {len(te)} for '
             f'{len(tp)} waypoints in {t_ms:.1f} ms, on the same map.">',
             '<title>Tonight&#8217;s search</title>',
             f'''<defs>
<style>
  @media (prefers-reduced-motion: no-preference) {{
    .wave {{ animation: sweep {DUR}s {EASE_CSS} both }}
    .path {{ animation: draw {DUR}s {EASE_CSS} both }}
    @keyframes sweep {{ from {{ opacity: 0 }} 25% {{ opacity: 1 }} }}
    @keyframes draw  {{ from {{ stroke-dashoffset: var(--len) }}
                        62% {{ stroke-dashoffset: var(--len) }} }}
  }}
</style>
</defs>''',
             f'<rect width="{W:.0f}" height="{H:.0f}" rx="6" fill="{T["bg"]}"/>',
             f'<rect x="0.5" y="0.5" width="{W-1:.0f}" height="{H-1:.0f}" rx="6" '
             f'stroke="{T["line"]}"/>',
             f'<text x="28" y="38" font-family="{SANS}" font-size="17" font-weight="650" '
             f'letter-spacing="-0.3" fill="{T["txt"]}">Same map, two planners</text>',
             f'<text x="28" y="60" font-family="{SANS}" font-size="12" '
             f'fill="{T["mut"]}">seed {used} · regenerated nightly · the real search, '
             f'replayed in the order the planner expanded it</text>']
        s.append(panel(T, 28, "A*", "8-connected, octile heuristic", T["ramp"][4],
                       g, start, goal, ap, ae, a_ms, DUR))
        s.append(panel(T, 28 + COLS * CELL + 52, "Theta*",
                       "any-angle, line-of-sight reparenting", T["ramp"][4],
                       g, start, goal, tp, te, t_ms, DUR))
        s.append('</svg>')
        open(out, "w").write("\n".join(s))
        print("%-14s %d KiB" % (os.path.basename(out), os.path.getsize(out) // 1024))

    print(f"seed {used}: A* {len(ae)} expanded / {len(ap)} pts / {a_ms:.1f} ms | "
          f"Theta* {len(te)} / {len(tp)} / {t_ms:.1f} ms")
