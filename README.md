<!-- print(''.join(chr(x-7) for x in [104,105,107,124,115,39,121,104,111,116,104,117])) -->
<!-- assets/*.svg are hand-authored and animated. the numbers in them are measured, not quoted. -->

<div align="center">

<img src="assets/hero.svg" alt="Mohammed Abdul Rahman — Robotics Engineer, ROS 2 / MoveIt 2, Physical AI, MS Robotics at Northeastern University" width="100%">

<br>

[![LinkedIn](https://img.shields.io/badge/LINKEDIN-abdu7rahman-0A66C2?style=for-the-badge&labelColor=0a0f16&logo=linkedin&logoColor=22d3ee)](https://linkedin.com/in/abdu7rahman)
[![Email](https://img.shields.io/badge/EMAIL-mohammedabdulr.1-ff4d5e?style=for-the-badge&labelColor=0a0f16&logo=maildotru&logoColor=ff4d5e)](mailto:mohammedabdulr.1@northeastern.edu)
[![Portfolio](https://img.shields.io/badge/PORTFOLIO-abdu7rahman.github.io-35e08a?style=for-the-badge&labelColor=0a0f16&logo=githubpages&logoColor=35e08a)](https://abdu7rahman.github.io/)
![Visitors](https://komarev.com/ghpvc/?username=abdu7rahman&style=for-the-badge&color=22d3ee&label=SCANS)

<br>

[![Run the planners](https://img.shields.io/badge/▶%20RUN%20MY%20PLANNERS%20IN%20YOUR%20BROWSER-A*%20·%20Theta*%20·%20RRT%2C%20fetched%20live%20from%20this%20account-ffb020?style=for-the-badge&labelColor=0a0f16)](https://abdu7rahman.github.io/demo.html)

</div>

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; WHOAMI

```console
$ rosnode info /abdu7rahman
```

Advanced Robotics and AI intern at **Siemens**. MS Robotics at **Northeastern University** ('27), BE in Computer Science
from **Osmania University**. Before grad school I spent five years on **Team Robocon MJCET**, working up
from junior programmer to leading a 20+ member team to its first national competition in five years.

I work on physical AI and the motion stack underneath it — planning, reactive replanning, legged
locomotion, and the unglamorous bringup that makes any of it run on real hardware. Lately I've been
pointing learned policies at deformable objects and watching them fail in instructive ways.

| | |
| --- | --- |
| **Now** | Advanced Robotics and AI intern at **Siemens**, Berkeley |
| **Building** | Sim-to-real transfer of bimanual garment policies onto a UR12e |
| **Next** | Inverse RL on quadruped locomotion, aimed at a **Unitree Go2** |
| **Always** | Planners written from scratch, then measured rather than assumed |

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; THE LAB

<div align="center">
<img src="assets/lab.svg" alt="Three animated simulations: a DWA local planner scoring 15 velocity rollouts and committing to the lowest-cost arc; a UR12e holding one end-effector pose while switching IK solutions along the elbow self-motion manifold to dodge an obstacle; a 12-axis quadruped walking a trot gait." width="100%">
</div>

> Three things I actually built, simulated in SVG rather than screenshotted. **Left:** velocity rollouts get
> sampled, scored on heading, clearance and speed, and the winner is committed while the rest are discarded.
> **Middle:** the end-effector pose never moves — the arm changes *which* IK solution reaches it, travelling
> along the elbow self-motion manifold to clear the obstacle. **Right:** a diagonal trot, knee bending
> backward on the front pair and forward on the rear.

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; BOARD

<div align="center">
<img src="assets/board.svg" alt="Systems board: five robotics systems with live status bars, a UR12e running a pick-and-place cycle that replans when an obstacle appears, and a scrolling telemetry log." width="100%">
</div>

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; SYSTEMS

<table>
<tr><th align="left" width="33%">System</th><th align="left">What it does</th><th align="left" width="20%">Numbers</th></tr>

<tr><td valign="top">

**Bimanual Garment Manipulation**

`Isaac Sim` `π0 / π0.5` `OpenPI`
`ACT` `Diffusion Policy` `smolVLA`

</td><td valign="top">

Trained and evaluated ACT, Diffusion Policy and smolVLA on multi-garment folding in a bimanual
setup, alongside work with π0, π0.5 and OpenPI across the VLA stack. Sim-to-real transfer onto a
UR12e is in progress.

</td><td valign="top">

**60.4%** success<br>
across 4 categories<br>
**78%** peak, long top

</td></tr>

<tr><td valign="top">

**[Dynamic Bin Picking + Reactive Replanning](https://github.com/abdu7rahman/reactive-replanning-ur12e)**

`ROS 2 Jazzy` `MoveIt 2` `BIT*`
`RealSense D435i` `OctoMap`

</td><td valign="top">

UR12e + Robotiq Hand-E. A depth pipeline with workspace filtering, robot self-masking and colour-based
body exclusion isolates live obstacles; the arm cancels cleanly and re-plans from its current state
mid-motion.

</td><td valign="top">

**100%** detection<br>
≥4 cm, 0.10 s<br>
blind within **11 cm**

</td></tr>

<tr><td valign="top">

**[Reactive Autonomous Nav Stack](https://github.com/abdu7rahman/reactive_autonomous_nav)**

`ROS 2 Jazzy` `TurtleBot4` `C++`
`nav2_costmap_2d`

</td><td valign="top">

A modular planner/controller architecture built from scratch — no Nav2 BT server. A\*, Theta\*, SMAC and
RRT behind one global interface; DWA shipped, with Pure Pursuit, Stanley, TEB and MPPI in progress.

</td><td valign="top">

**99–192×** faster<br>
after the C++ port<br>
[(measured)](#measured)

</td></tr>

<tr><td valign="top">

**[K.A.L.B — Legged Robot](https://github.com/abdu7rahman/K.A.L.B)** · [▶ demo](https://youtu.be/ESjXvtUxYeM)

`ROS 2` `Gazebo` `gmapping` `AMCL`

</td><td valign="top">

A quadruped with locomotion modelled after the MIT Cheetah. Gait stability and autonomous navigation
validated with SLAM in Gazebo; now collecting demonstrations for inverse RL.

</td><td valign="top">

**12** axes<br>
SLAM + AMCL<br>
→ Unitree Go2

</td></tr>

<tr><td valign="top">

**[Custom DWA Local Planner](https://github.com/abdu7rahman/Custom-DWA-Local-Planner)** · [▶ demo](https://youtu.be/yFtexC6-Z1g)

`ROS 2 Humble` `TurtleBot3` `RViz`

</td><td valign="top">

DWA written from scratch rather than pulling in `nav2_dwb_controller` — velocity sampling, trajectory
rollout, cost evaluation, and marker visualisation of every candidate.

</td><td valign="top">

⭐ **6** stars<br>
most-starred repo

</td></tr>


</table>

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; STACK

<div align="center">

<img src="https://skillicons.dev/icons?i=ros,python,cpp,c,linux,docker,git,github,opencv,pytorch,cmake,bash,arduino,raspberrypi,matlab,vscode&theme=dark&perline=16" alt="ROS, Python, C++, C, Linux, Docker, Git, GitHub, OpenCV, PyTorch, CMake, Bash, Arduino, Raspberry Pi, MATLAB, VS Code">

</div>

| | |
| --- | --- |
| **Frameworks** | ROS / ROS 2 (Humble, Jazzy) · MoveIt 2 · Nav2 · Gazebo · RViz · Isaac Sim · Autoware |
| **Planning** | A\* · Theta\* · SMAC · RRT / RRT-Connect · BIT\* · DWA · Pure Pursuit · Stanley · TEB · MPPI |
| **Physical AI** | π0 · π0.5 · OpenPI · ACT · Diffusion Policy · smolVLA · VLA fine-tuning · inverse RL · sim-to-real transfer |
| **Perception** | YOLO · OpenCV · depth estimation · sensor fusion · OctoMap · visual SLAM (PySLAM) |
| **Hardware** | UR12e / UR5 · Robotiq Hand-E & 2F-85 · TurtleBot3/4 · Unitree Go2 · Jetson Nano · Raspberry Pi · Arduino |
| **Sensors** | LiDAR · IMU · wheel encoders · Intel RealSense D435i · GPS/GNSS RTK |
| **Design** | SolidWorks · OnShape · Eagle PCB · URDF / XACRO |

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; TELEMETRY

<div align="center">
<img src="assets/stats.svg" alt="Two charts. Left: monthly commit cadence — 240 commits authored across 61 months from 2021-07 to 2026-07, 20 active months, median 8, peak 49. Right: source-byte mix across 27 repositories — Python 30.7%, CMake 18.1%, YAML 15.0%, XML/URDF 14.8%, C++ 8.5%, Other 12.9%." width="100%">
</div>

<details>
<summary>Data behind the charts</summary>

<br>

Counted from the git history of every repo on this account. Commits are filtered to my own authorship;
the language mix excludes two repos built on forked upstreams (`K.A.L.B`, `lehome-challenge`) so vendored
code doesn't skew the split.

| Language | Share | Bytes |
| --- | ---: | ---: |
| Python | 30.7% | 594 KiB |
| CMake | 18.1% | 351 KiB |
| YAML | 15.0% | 290 KiB |
| XML / URDF / XACRO | 14.8% | 286 KiB |
| C++ | 8.5% | 164 KiB |
| Other (C, Shell, Arduino, HTML) | 12.9% | 249 KiB |
| **Total** | **100%** | **1.89 MiB** |

| Commit cadence | |
| --- | ---: |
| Commits authored | 240 |
| Window | Jul 2021 → Jul 2026 (61 months) |
| Active months | 20 |
| Median, active month | 8 |
| Peak month | 49 (Apr 2026) |

</details>

<div align="center">

<img src="https://streak-stats.demolab.com?user=abdu7rahman&theme=dark&background=0a0f16&border=1b2634&stroke=1b2634&ring=22d3ee&fire=ff4d5e&currStreakLabel=22d3ee&sideLabels=7d8da1&currStreakNum=e6edf3&sideNums=e6edf3&dates=6e7d90&border_radius=10&card_width=470" alt="GitHub commit streak" height="180">

<img src="https://github-readme-activity-graph.vercel.app/graph?username=abdu7rahman&bg_color=0a0f16&color=e6edf3&line=22d3ee&point=ff4d5e&area_color=22d3ee&title_color=22d3ee&area=true&hide_border=false&border_color=1b2634&radius=10&custom_title=CONTRIBUTION%20TRACE%20%E2%80%94%20LAST%2031%20DAYS" alt="Contribution activity graph, last 31 days" width="100%">

<!-- Snake: populated by .github/workflows/snake.yml. Run it once (Actions → Contribution Snake →
     Run workflow) after merging, or wait for the daily schedule, and this starts rendering. -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/abdu7rahman/abdu7rahman/output/snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/abdu7rahman/abdu7rahman/output/snake.svg">
  <img alt="A snake eating my contribution graph" src="https://raw.githubusercontent.com/abdu7rahman/abdu7rahman/output/snake.svg" width="100%">
</picture>

</div>

<img src="assets/divider.svg" alt="" width="100%">

## &nbsp;▸&nbsp; TRAJECTORY

```
2026 ──●  Siemens · Advanced Robotics and AI Intern        Jun 2026 –
       │  Berkeley, California. On-site.
       │
       ●  Northeastern University · Graduate Lab Assistant  Apr – Jun 2026
       │  ROS 2 bag collection from a Ford Mustang Mach-E autonomous
       │  vehicle platform, with visual SLAM run over the recorded drives
       │  for trajectory analysis. UR12e URDF with Robotiq integration and
       │  the MoveIt 2 stack for faculty research, plus an end-effector
       │  camera mount now used across several setups.
       │
2025 ──●  MS Robotics, Electrical & Computer Engineering    2025 – 2027
       │  Northeastern University
       │
2020 ──●  BE Computer Science & Engineering                 2020 – 2024
       │  Osmania University, Hyderabad
       │
       ●  Team Robocon MJCET                          Dec 2020 – Jul 2025
       │  Junior Programmer → Programmer → Robotics Control Engineer
       │  → Team Lead/Captain → Team Mentor
       │
       │  ABU Robocon 2021 · pitch-pot        holonomic chassis, pneumatic
       │    arrow handling, spring-based shooter
       │  ABU Robocon 2022 · lagori           omni shooter + swerve, CV for
       │    incoming balls, ML predicting where the stack would fall
       │  ABU Robocon 2023 · Angkor Wat       omni + mecanum, ring and pole
       │    detection, collection and shooting
       │  ABU Robocon 2024 · Harvest Day      the team's first national
       │    appearance in over five years. Two holonomic drives, ball
       │    shooters, pneumatic seedling collection, silo placement. ROS
       │    waypoint navigation, colour-based ball detection, and an ML
       │    policy that picked silo placements against the opponent.
       │  ABU Robocon 2025 · robot basketball 2v2, as mentor — ROS guidance
       │    and play strategy
       │
2022 ──●  Consciente Technologies · Robotics Engineer Intern  Aug – Sep 2022
       │  DH parameters and MoveIt configuration for a custom 5-DOF
       ●  manipulator; coordinate-based autonomous navigation on hardware.
```

<img src="assets/divider.svg" alt="" width="100%">

<div align="center">

### `▸` Get in touch

[![Email](https://img.shields.io/badge/SEND%20A%20GOAL%20POSE-mohammedabdulr.1%40northeastern.edu-22d3ee?style=for-the-badge&labelColor=0a0f16)](mailto:mohammedabdulr.1@northeastern.edu)

<br>

<sub>`/status` &nbsp;·&nbsp; **building robots that may work** &nbsp;·&nbsp; if it planned on the first try, the obstacle was imaginary</sub>

</div>
