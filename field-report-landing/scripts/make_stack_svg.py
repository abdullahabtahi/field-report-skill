#!/usr/bin/env python3
"""Generate the exploded isometric layer-stack hero as a self-contained SVG, in the house grammar.

Layers are listed bottom to top. Each layer gets a 2:1 slab with thickness, hairline artwork chosen from a small
library, a dashed leader to a bracketed legend ([01] label, arrow items, optional outlined tag), and a signal arrow
rising along the left that carries one travelling dash. Strokes keep one weight at any size (vector-effect).
Everything stops under prefers-reduced-motion and the drawing stays complete.

usage:
  make_stack_svg.py --config layers.json --out stack.svg
  make_stack_svg.py --demo --out stack.svg          (five placeholder layers)

layers.json:
  {"title": "...", "desc": "...", "layers": [
     {"label": "WEATHER FEED", "art": "cubes", "items": ["Real public weather data"], "tag": "REAL DATA"},
     ... ]}
art is one of: cubes, grid, graph, rows, panels. 3 to 6 layers. Library use: from make_stack_svg import build_svg.
"""
from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

W = 1180
HW, HH = 230.0, 115.0  # slab half width and half height (2:1 rhombus)
CX = 380.0
STEP = 135.0
TOP_CY = 160.0
EDGE = 9.0
LEG_X = 712.0
ARTS = ("cubes", "grid", "graph", "rows", "panels")
DEFAULT_ARTS = {3: ("cubes", "graph", "panels"), 4: ("cubes", "grid", "graph", "panels"),
                5: ("cubes", "grid", "graph", "rows", "panels"), 6: ("cubes", "grid", "graph", "rows", "panels", "graph")}


def f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def plane(cy: float, u: float, v: float) -> tuple[float, float]:
    return CX + (u - v) * HW / 2, cy + (u + v) * HH / 2


def ptransform(cy: float) -> str:
    return f"matrix({f(HW / 2)} {f(HH / 2)} {f(-HW / 2)} {f(HH / 2)} {f(CX)} {f(cy)})"


def outline(cy: float) -> str:
    return f"M{f(CX)} {f(cy - HH)}L{f(CX + HW)} {f(cy)}L{f(CX)} {f(cy + HH)}L{f(CX - HW)} {f(cy)}Z"


def edge(cy: float) -> str:
    t = EDGE
    return (f"M{f(CX - HW)} {f(cy)}L{f(CX - HW)} {f(cy + t)}L{f(CX)} {f(cy + HH + t)}L{f(CX + HW)} {f(cy + t)}L{f(CX + HW)} {f(cy)}"
            f"M{f(CX)} {f(cy + HH)}L{f(CX)} {f(cy + HH + t)}")


def cube(x: float, y: float, s: float) -> str:
    k = 0.866 * s
    return (f"M{f(x)} {f(y - s)}L{f(x + k)} {f(y - s / 2)}L{f(x + k)} {f(y + s / 2)}L{f(x)} {f(y + s)}L{f(x - k)} {f(y + s / 2)}L{f(x - k)} {f(y - s / 2)}Z"
            f"M{f(x - k)} {f(y - s / 2)}L{f(x)} {f(y)}L{f(x + k)} {f(y - s / 2)}M{f(x)} {f(y)}L{f(x)} {f(y + s)}")


def cylinder(x: float, y: float, s: float) -> str:
    rx, ry, h = 0.78 * s, 0.38 * s, 1.5 * s
    return (f"M{f(x - rx)} {f(y - h)}A{f(rx)} {f(ry)} 0 1 0 {f(x + rx)} {f(y - h)}A{f(rx)} {f(ry)} 0 1 0 {f(x - rx)} {f(y - h)}Z"
            f"M{f(x - rx)} {f(y - h)}L{f(x - rx)} {f(y)}A{f(rx)} {f(ry)} 0 0 0 {f(x + rx)} {f(y)}L{f(x + rx)} {f(y - h)}")


WORLD = [(-0.62, -0.5), (-0.2, -0.62), (0.28, -0.56), (0.66, -0.3), (-0.66, -0.06), (-0.22, -0.1),
         (0.24, -0.02), (0.62, 0.22), (-0.5, 0.42), (-0.06, 0.34), (0.38, 0.5), (0.0, 0.66)]
NODES = [(-0.7, -0.35), (-0.35, -0.7), (-0.4, 0.1), (0.05, -0.3), (0.1, 0.45), (0.5, -0.1), (0.62, 0.55), (-0.15, 0.7), (0.55, -0.62)]
EDGES = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6), (2, 7), (4, 7), (5, 8), (1, 8)]


def grid_lines(n: int) -> str:
    step = 2 / n
    d = ""
    for i in range(n + 1):
        t = -1 + i * step
        d += f"M{t:.3f} -1L{t:.3f} 1M-1 {t:.3f}L1 {t:.3f}"
    return d


def art_cubes(cy: float) -> str:
    items = sorted(((i, plane(cy, u, v)) for i, (u, v) in enumerate(WORLD)), key=lambda t: t[1][1])
    out = ['<g class="art">']
    for i, (x, y) in items:
        d = cylinder(x, y + 4, 11) if i % 3 == 1 else cube(x, y - 10, 13 if i % 3 == 0 else 10)
        out.append(f'<path d="{d}" class="solid"/>')
    out.append("</g>")
    return "".join(out)


def art_grid(cy: float) -> str:
    cell = 2 / 14
    rects = "".join(f'<rect x="{-1 + i * cell:.3f}" y="{-1 + j * cell:.3f}" width="{cell:.3f}" height="{cell:.3f}" class="fill-sig"/>'
                    for i, j in [(3, 5), (4, 5), (4, 6), (5, 7), (6, 7), (6, 8), (7, 9), (8, 9)])
    return (f'<g transform="{ptransform(cy)}" class="art"><path d="{grid_lines(14)}" class="line fine"/>{rects}'
            f'<rect x="{-1 + 10 * cell:.3f}" y="{-1 + 3 * cell:.3f}" width="{cell:.3f}" height="{cell:.3f}" class="line dash"/>'
            f'<path d="M-1 0.12L1 0.12" class="line dash"/></g>')


def art_graph(cy: float) -> str:
    es = "".join(f'<path d="M{NODES[a][0]} {NODES[a][1]}L{NODES[b][0]} {NODES[b][1]}" class="line"/>' for a, b in EDGES)
    ns = "".join(f'<circle cx="{u}" cy="{v}" r="{0.13 if i == 3 else 0.07}" class="{"hub" if i == 3 else "node"}"/>' for i, (u, v) in enumerate(NODES))
    return f'<g transform="{ptransform(cy)}" class="art">{es}{ns}</g>'


def art_rows(cy: float) -> str:
    rows = [-0.8 + i * 0.2 for i in range(9)]
    out = []
    for i, v in enumerate(rows):
        out.append(f'<rect x="-0.85" y="{v:.2f}" width="0.5" height="0.1" class="{"fill-sig" if i == 4 else "line"}"/>')
        out.append(f'<rect x="-0.28" y="{v:.2f}" width="{0.4 + ((i * 7) % 5) * 0.08:.2f}" height="0.1" class="line"/>')
        out.append(f'<rect x="0.62" y="{v:.2f}" width="0.22" height="0.1" class="{"fill-ink" if i == 4 else "line"}"/>')
    return f'<g transform="{ptransform(cy)}" class="art">{"".join(out)}</g>'


def art_panels(cy: float) -> str:
    lines = "".join(f'<path d="M-0.8 {v}L-0.46 {v}" class="line fine"/>' for v in (-0.66, -0.46, -0.26, -0.06))
    return (f'<g transform="{ptransform(cy)}" class="art"><rect x="-0.88" y="-0.82" width="0.5" height="1.64" class="line"/>'
            f'<rect x="-0.3" y="-0.82" width="1.18" height="0.84" class="line"/><rect x="-0.3" y="0.1" width="0.56" height="0.72" class="line"/>'
            f'<rect x="0.34" y="0.1" width="0.54" height="0.72" class="line"/>'
            f'<path d="M-0.22 -0.2L-0.05 -0.5L0.18 -0.28L0.4 -0.62L0.62 -0.4L0.8 -0.7" class="line signal"/>{lines}</g>')


ART_FN = {"cubes": art_cubes, "grid": art_grid, "graph": art_graph, "rows": art_rows, "panels": art_panels}

CSS = """
.layer{--stroke:var(--ink,#ecebe6);--soft:rgba(236,235,230,.62);--sigc:var(--sig,#9db7cf);animation:rise 1s cubic-bezier(.16,1,.3,1) both;animation-delay:calc(var(--i)*130ms)}
.slab{fill:var(--ground,#0e1116);stroke:var(--stroke);stroke-width:1.2;stroke-linejoin:round;stroke-dasharray:1;animation:draw 1.4s cubic-bezier(.16,1,.3,1) both;animation-delay:calc(var(--i)*130ms)}
.edge{fill:none;stroke:var(--stroke);stroke-width:1.2;stroke-linejoin:round}
.line{fill:none;stroke:var(--soft);stroke-width:1;vector-effect:non-scaling-stroke}.fine{stroke-width:.6}.dash{stroke-dasharray:3 4}
.signal{stroke:var(--sigc);stroke-width:1.6}
.solid{fill:var(--ground,#0e1116);stroke:var(--stroke);stroke-width:1;stroke-linejoin:round}
.fill-sig{fill:var(--sigc);stroke:none}.fill-ink{fill:var(--stroke);stroke:none}
.node{fill:var(--ground,#0e1116);stroke:var(--stroke);vector-effect:non-scaling-stroke}
.hub{fill:none;stroke:var(--sigc);stroke-dasharray:3 3;vector-effect:non-scaling-stroke}
.art{animation:fade 1.2s cubic-bezier(.16,1,.3,1) both;animation-delay:calc(var(--i)*130ms + 500ms)}
.leader{fill:none;stroke:var(--ink-3,rgba(236,235,230,.34));stroke-width:1;stroke-dasharray:2 4}
.arrow-line,.arrow-run{fill:none;stroke-width:2.4;stroke-linecap:round}
.arrow-line{stroke:rgba(157,183,207,.55);stroke-dasharray:1;animation:draw 2s cubic-bezier(.16,1,.3,1) .4s both}
.arrow-head{fill:none;stroke:var(--sig,#9db7cf);stroke-width:2.4;stroke-linecap:round;animation:fade .6s ease 2s both}
.arrow-run{stroke:var(--ink,#ecebe6);stroke-dasharray:.05 .95;animation:run 5.5s linear 2.4s infinite}
.br{fill:none;stroke:var(--ink-3,rgba(236,235,230,.34));stroke-width:1}
.num{font:500 13px ui-monospace,Menlo,monospace;fill:var(--ink-2,rgba(236,235,230,.68));letter-spacing:.06em}
.lab{font:500 14px var(--fde-sans,system-ui,sans-serif);fill:var(--ink,#ecebe6);letter-spacing:.14em}
.itm{font:400 15px var(--fde-sans,system-ui,sans-serif);fill:var(--ink-2,rgba(236,235,230,.68))}
.tag{fill:none;stroke:var(--rule,rgba(236,235,230,.4));stroke-width:1}
.tagt{font:500 11px ui-monospace,Menlo,monospace;fill:var(--ink-2,rgba(236,235,230,.68));letter-spacing:.08em}
@keyframes rise{from{opacity:0;transform:translateY(-22px)}}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes fade{from{opacity:0}}
@keyframes run{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){.layer,.slab,.art,.arrow-line,.arrow-head,.arrow-run{animation:none!important}.arrow-run{display:none}}
""".strip()


def build_svg(cfg: dict, legend: bool = True, uid: str = "stack") -> str:
    layers = cfg.get("layers", [])
    n = len(layers)
    if not 3 <= n <= 6:
        raise ValueError("a stack needs 3 to 6 layers")
    bottom = TOP_CY + (n - 1) * STEP
    h = bottom + 140
    arts = DEFAULT_ARTS[n]
    title = cfg.get("title", "Exploded isometric diagram of the system layers")
    desc = cfg.get("desc", "")
    width = W if legend else 700
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" class="stack" viewBox="0 0 {width} {f(h)}" role="img" aria-labelledby="{uid}-t {uid}-d">',
             f'<title id="{uid}-t">{escape(title)}</title><desc id="{uid}-d">{escape(desc or title)}</desc>', f"<style>{CSS}</style>"]
    for k, layer in enumerate(layers):  # k = 0 is the bottom layer
        cy = bottom - k * STEP
        art = layer.get("art") or arts[k]
        if art not in ART_FN:
            raise ValueError(f"unknown art {art!r}; use one of {ARTS}")
        parts.append(f'<g class="layer" style="--i:{k}"><path d="{edge(cy)}" class="edge"/>'
                     f'<path d="{outline(cy)}" class="slab" pathLength="1"/>'
                     + (f'<path d="M{f(CX + HW + 8)} {f(cy)}L{f(LEG_X - 14)} {f(cy)}" class="leader" aria-hidden="true"/>' if legend else "")
                     + f"{ART_FN[art](cy)}</g>")
    # legend, one bracketed band per slab, aligned to the slab height
    for k, layer in enumerate(layers if legend else []):
        cy = bottom - k * STEP
        top = cy - 38
        parts.append(f'<g class="legend"><path d="M{f(LEG_X + 8)} {f(top)}L{f(LEG_X)} {f(top)}L{f(LEG_X)} {f(cy + 44)}L{f(LEG_X + 8)} {f(cy + 44)}" class="br"/>'
                     f'<text x="{f(LEG_X + 18)}" y="{f(cy - 14)}"><tspan class="num">[{k + 1:02d}]</tspan><tspan class="lab" dx="10">{escape(layer["label"].upper())}</tspan></text>')
        tag = layer.get("tag")
        if tag:
            tw = len(tag) * 6.6 + 14
            tx = LEG_X + 18 + 40 + len(layer["label"]) * 10.6 + 14
            parts.append(f'<rect x="{f(tx)}" y="{f(cy - 27)}" width="{f(tw)}" height="17" class="tag"/>'
                         f'<text x="{f(tx + 7)}" y="{f(cy - 15)}" class="tagt">{escape(tag.upper())}</text>')
        for j, item in enumerate(layer.get("items", [])[:2]):
            parts.append(f'<text x="{f(LEG_X + 18)}" y="{f(cy + 8 + j * 22)}" class="itm">→ {escape(item)}</text>')
        parts.append("</g>")
    ay0, ay1 = bottom + 5, TOP_CY + 12
    path = f"M118 {f(ay0)}C14 {f(ay0 - 105)} 14 {f(ay1 + 108)} 118 {f(ay1)}"
    parts.append(f'<g aria-hidden="true"><path d="{path}" class="arrow-line" pathLength="1"/>'
                 f'<path d="M118 {f(ay1)}L103 {f(ay1 + 5.6)}M118 {f(ay1)}L114.2 {f(ay1 + 15.6)}" class="arrow-head"/>'
                 f'<path d="{path}" class="arrow-run" pathLength="1"/></g></svg>')
    return "".join(parts)


DEMO = {"title": "Exploded isometric diagram of five system layers, from data sources at the bottom to the operator surface at the top, with a signal rising through them.",
        "layers": [
            {"label": "Sources", "items": ["Public and partner data", "Event streams"], "tag": "REAL DATA"},
            {"label": "Ingestion", "items": ["Contract-checked, replayable"]},
            {"label": "Model", "items": ["Entities and relationships", "The one place meaning lives"]},
            {"label": "Assistant", "items": ["Proposes; cites every figure"]},
            {"label": "Operator", "items": ["A person approves", "Every action is recorded"], "tag": "BY DESIGN"}]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if not a.demo and not a.config:
        ap.error("pass --config or --demo")
    try:
        cfg = DEMO if a.demo else json.loads(a.config.read_text())
        svg = build_svg(cfg)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    a.out.write_text(svg)
    print(f"wrote {a.out} ({len(cfg['layers'])} layers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
