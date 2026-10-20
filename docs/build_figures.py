#!/usr/bin/env python3
"""Rebuild the README figures in docs/img from the raw captures in docs/src.

Each figure is a labelled, framed panel (or two, with a divider) in the skill's own look, so a side-by-side
reads as a comparison and not as two crops glued together.
Run: python3 docs/build_figures.py     (needs Playwright with Chromium)
"""
from __future__ import annotations

import sys
from html import escape
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "src", ROOT / "img"
OUT.mkdir(exist_ok=True)

CSS = """
*{box-sizing:border-box}body{margin:0;background:#0e1116;color:#ecebe6;font-family:Inter,'Helvetica Neue',Arial,sans-serif}
.fig{display:inline-block;padding:36px 40px 40px;background:#0e1116}
.title{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 22px;font:500 14px Menlo,monospace;letter-spacing:.16em;text-transform:uppercase;color:rgba(236,235,230,.68)}
.title b{color:#ecebe6;font-weight:500}
.row{display:flex;gap:0;align-items:stretch}
.panel{border:1px solid rgba(236,235,230,.24);display:flex;flex-direction:column}
.bar{display:flex;justify-content:space-between;align-items:center;padding:0 18px;height:48px;border-bottom:1px solid rgba(236,235,230,.24)}
.lab{display:flex;align-items:center;gap:12px;font:500 14px Menlo,monospace;letter-spacing:.16em;text-transform:uppercase}
.lab i{display:block;width:3px;height:18px;background:var(--tick,rgba(236,235,230,.34))}
.sub{font:400 13px Menlo,monospace;letter-spacing:.04em;color:rgba(236,235,230,.68)}
.panel img{display:block;width:100%;height:auto}
.gap{width:72px;position:relative;flex:none}
.gap::before{content:"";position:absolute;left:50%;top:0;bottom:0;border-left:1px dashed rgba(236,235,230,.3)}
.gap span{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);background:#0e1116;padding:8px 0;font:500 13px Menlo,monospace;letter-spacing:.14em;color:rgba(236,235,230,.68)}
.steps{display:grid;grid-template-columns:repeat(3,1fr);width:1240px;border:1px solid rgba(236,235,230,.24)}
.step{padding:20px 22px 24px;border-right:1px solid rgba(236,235,230,.24);border-bottom:1px solid rgba(236,235,230,.24);min-height:150px}
.step:nth-child(3n){border-right:0}.step:nth-last-child(-n+3){border-bottom:0}.step .n{font:500 13px Menlo,monospace;color:#9db7cf;letter-spacing:.08em}
.step h4{margin:10px 0 8px;font:400 26px Inter,sans-serif;letter-spacing:-.01em}
.step p{margin:0;font:400 16px/1.45 Inter,sans-serif;color:rgba(236,235,230,.68)}
.step code{display:block;margin-top:12px;font:500 13px Menlo,monospace;color:#9db7cf;letter-spacing:.02em}
"""


def img(name: str) -> str:
    return f"file://{SRC / name}"


def panel(label: str, sub: str, src: str, width: int, tick: str | None = None) -> str:
    style = f' style="--tick:{tick}"' if tick else ""
    return (f'<div class="panel" style="width:{width}px"><div class="bar"{style}><span class="lab"><i></i>{escape(label)}</span>'
            f'<span class="sub">{escape(sub)}</span></div><img src="{img(src)}"></div>')


def figure(title: str, note: str, body: str) -> str:
    return f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><div class="fig" id="fig"><div class="title"><b>{escape(title)}</b><span>{escape(note)}</span></div>{body}</div>'


SIG = "#9db7cf"
FIGS = {
    "compare-tern": figure("Same brief, built twice", "Tern, a made-up shorebird-monitoring tool", '<div class="row">'
        + panel("With the skill", "23 / 23 checks · 269 s", "tern-with.png", 1100, SIG)
        + '<div class="gap"><span>VS</span></div>'
        + panel("Without the skill", "18 / 23 checks · 511 s", "tern-without.png", 1100) + "</div>"),
    "compare-ferryline": figure("Same brief, built twice", "Ferryline, a made-up ferry-dispatch copilot", '<div class="row">'
        + panel("With the skill", "20 / 20 checks · 405 s", "ferry-with.png", 1100, SIG)
        + '<div class="gap"><span>VS</span></div>'
        + panel("Without the skill", "17 / 20 checks · 282 s", "ferry-without.png", 1100) + "</div>"),
    "mobile": figure("On a phone", "390 px wide, from the generated example page", '<div class="row">'
        + panel("Hero", "diagram, then legend", "mobile-hero.png", 520, SIG)
        + '<div class="gap"></div>'
        + panel("Ledger", "stacked cards", "mobile-ledger.png", 520, SIG) + "</div>"),
    "hero": figure("Generated hero", "from the example config", panel("Hero", "scripts/make_stack_svg.py", "hero.png", 1360, SIG)),
    "ledger": figure("Generated ledger", "from the example config", panel("Results ledger", "sources, tags and misses in one table", "ledger.png", 1360, SIG)),
    "stack": figure("Hero generator", "scripts/make_stack_svg.py, five layers", panel("Exploded layer stack", "bracketed legend, signal arrow", "stack.png", 1100, SIG)),
}

STEPS = [("01", "Brief", "Audience, thesis, beats, proof sources", ""), ("02", "Ground", "Take the grammar from references, not the artwork", ""),
         ("03", "Contract", "Thesis, own-world, story, form, finish", ""), ("04", "Story", "Problem, response, capabilities, platform, proof", ""),
         ("05", "Assets", "Still, clip, graded frames. Ask before spending", "frames_from_clip.sh"), ("06", "Build", "One config makes the page", "scaffold_page.py"),
         ("07", "Honesty", "Sources, tags, no absolutes, misses shown", "honesty_scan.py"), ("08", "Verify", "One bounded pass, then an independent review", ""),
         ("09", "Document", "Design entry and provenance", "")]
FIGS["process"] = figure("The process", "nine steps, the tools that automate them in blue", '<div class="steps">' + "".join(
    f'<div class="step"><div class="n">{n}</div><h4>{escape(t)}</h4><p>{escape(d)}</p>' + (f"<code>{escape(c)}</code>" if c else "") + "</div>" for n, t, d, c in STEPS) + "</div>")


def main() -> int:
    missing = [p for p in SRC.glob("*.png")] or None
    if not missing:
        print("no captures in docs/src", file=sys.stderr)
        return 2
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_context(viewport={"width": 2600, "height": 1000}).new_page()
        for name, html in FIGS.items():
            tmp = OUT / f".{name}.html"
            tmp.write_text(html)
            pg.goto(f"file://{tmp}")
            pg.wait_for_timeout(500)
            pg.locator("#fig").screenshot(path=str(OUT / f"{name}.png"))
            tmp.unlink()
            print("wrote", OUT / f"{name}.png")
        b.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
