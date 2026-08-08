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
from palette import WARMDAY, NIGHT, MONO as MONO_STACK, suffix          # noqa: E402

THEME = NIGHT if os.environ.get("PLATE_THEME") == "night" else WARMDAY
ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
OUT = os.path.join(ASSETS, "run%s.svg" % suffix(THEME))

BG = THEME["bg"]; PANEL = THEME["panel"]; GRID = THEME["grid"]; LINE = THEME["line"]
TXT = THEME["txt"]; MUT = THEME["mut"]
CY = THEME["c1"]; VIO = THEME["c3"]; GRN = THEME["c4"]; AMB = THEME["c4"]
MONO = MONO_STACK

COLS, ROWS = 78, 46
CELL = 7.2


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


def panel(ox, title, sub, accent, g, start, goal, path, explored, ms, dur):
    W = COLS * CELL
    out = [f'<g transform="translate({ox} 92)">']
    out.append(f'<text x="0" y="-30" font-family="{MONO}" font-size="12" font-weight="700" '
               f'letter-spacing="2.2" fill="{accent}">{title}</text>')
    out.append(f'<text x="0" y="-14" font-family="{MONO}" font-size="9" letter-spacing="1.2" fill="{MUT}">{sub}</text>')
    out.append(f'<rect x="-2" y="-2" width="{W+4}" height="{ROWS*CELL+4}" fill="{PANEL}" stroke="{LINE}"/>')
    for r in range(ROWS):
        run = None
        for c in range(COLS + 1):
            solid = c < COLS and g[r, c] >= 253
            if solid and run is None:
                run = c
            elif not solid and run is not None:
                out.append(f'<rect x="{run*CELL:.1f}" y="{r*CELL:.1f}" '
                           f'width="{(c-run)*CELL:.1f}" height="{CELL:.1f}" fill="{LINE}"/>')
                run = None
    fr = frames_of(explored)
    per = dur * 0.62 / max(1, len(fr))
    for i, chunk in enumerate(fr):
        d = "".join(f"M{c*CELL:.1f} {r*CELL:.1f}h{CELL:.1f}v{CELL:.1f}h-{CELL:.1f}z" for r, c in chunk)
        out.append(f'<path d="{d}" fill="{accent}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0.42;0.16" keyTimes="0;0.25;1" '
                   f'dur="{dur}s" begin="{i*per:.2f}s" fill="freeze"/></path>')
    pts = " ".join(f"{c*CELL+CELL/2:.1f},{r*CELL+CELL/2:.1f}" for r, c in path)
    length = sum(math.hypot((path[i+1][0]-path[i][0])*CELL, (path[i+1][1]-path[i][1])*CELL)
                 for i in range(len(path)-1)) + 4
    out.append(f'<polyline points="{pts}" fill="none" stroke="{GRN}" stroke-width="2.6" '
               f'stroke-linecap="round" stroke-linejoin="round" '
               f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
               f'<animate attributeName="stroke-dashoffset" values="{length:.0f};{length:.0f};0" '
               f'keyTimes="0;{0.62};1" dur="{dur}s" begin="0s" fill="freeze"/></polyline>')
    for rc, col in ((start, CY), (goal, GRN)):
        x, y = rc[1]*CELL+CELL/2, rc[0]*CELL+CELL/2
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{col}"/>')
    out.append(f'<text x="0" y="{ROWS*CELL+18}" font-family="{MONO}" font-size="9" '
               f'letter-spacing="1.2" fill="{MUT}">{len(explored):,} expanded  ·  '
               f'{len(path)} waypoints  ·  {ms:.1f} ms</text>')
    out.append("</g>")
    return "\n".join(out)


if __name__ == "__main__":
    stub_ros()
    A_CLS = load("astar_planner").AStarPlannerNode
    T_CLS = load("theta_star_planner").ThetaStarPlannerNode
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.time()) % 100000
    g, start, goal, (ap, ae, a_ms), (tp, te, t_ms), used = plan(seed)

    W = COLS * CELL * 2 + 96
    H = ROWS * CELL + 144
    DUR = 9.0
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
         f'fill="none" role="img" aria-label="A real planner run: A* expanded {len(ae)} nodes for a '
         f'{len(ap)}-waypoint path in {a_ms:.1f} ms; Theta* expanded {len(te)} for {len(tp)} waypoints '
         f'in {t_ms:.1f} ms, on the same map.">',
         f'<title>A live run of the planners</title>',
         f'<rect width="{W:.0f}" height="{H:.0f}" fill="{BG}"/>',
         f'<text x="24" y="28" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing="2.4" '
         f'fill="{TXT}">SAME MAP, TWO PLANNERS</text>',
         f'<text x="24" y="46" font-family="{MONO}" font-size="9.5" letter-spacing="1.6" fill="{MUT}">'
         f'seed {used}  ·  regenerated daily  ·  this is the real search, replayed in expansion order</text>']
    s.append(panel(24, "A*", "8-connected, octile heuristic", CY, g, start, goal, ap, ae, a_ms, DUR))
    s.append(panel(24 + COLS*CELL + 48, "THETA*", "any-angle, line-of-sight reparenting", VIO,
                   g, start, goal, tp, te, t_ms, DUR))
    s.append('</svg>')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(s))
    print(f"seed {used}: A* {len(ae)} expanded / {len(ap)} pts / {a_ms:.1f} ms | "
          f"Theta* {len(te)} / {len(tp)} / {t_ms:.1f} ms -> {OUT} "
          f"({os.path.getsize(OUT)//1024} KiB)")
