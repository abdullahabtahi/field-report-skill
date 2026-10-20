#!/usr/bin/env python3
"""Programmatic grader for the ferryline eval. usage: grade.py <run-dir>   (the folder that holds outputs/)

Writes <run-dir>/grading.json with expectations [{text, passed, evidence}] and a summary.
Every check is objective and runs on the files the agent produced.
"""
from __future__ import annotations

import colorsys
import json
import re
import sys
from pathlib import Path

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("run")
ap.add_argument("--eval", default="ferryline", choices=["ferryline", "tern"])
args = ap.parse_args()
run = Path(args.run)
out = run / "outputs"
exp: list[dict] = []


def add(text: str, passed: bool, evidence: str) -> None:
    exp.append({"text": text, "passed": bool(passed), "evidence": evidence})


def read(name: str) -> str:
    p = out / name
    return p.read_text(errors="ignore") if p.exists() else ""


def strip_comments(s: str) -> str:
    return re.sub(r"/\*[\s\S]*?\*/|<!--[\s\S]*?-->", "", s)


page, css, contract = read("page.html"), read("tokens.css"), read("direction-contract.md")
data = "\n".join(p.read_text(errors="ignore") for p in sorted((out / "data").glob("*"))) if (out / "data").is_dir() else ""
prompts, report = read("asset-prompts.md"), read("report.md")
style_blocks = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", page))
allcss = strip_comments(css + "\n" + style_blocks)

# 1 deliverables
needed = ["direction-contract.md", "tokens.css", "page.html", "asset-prompts.md", "report.md"]
missing = [n for n in needed if not (out / n).exists() or not read(n).strip()] + ([] if data.strip() else ["data/*"])
add("All six deliverables exist and are non-empty", not missing, f"missing: {missing}" if missing else "all present")

# 2 contract sections
secs = ["THESIS", "OWN-WORLD", "STORY", "FIRST VIEWPORT", "FORM", "FINISH"]
lost = [s for s in secs if not re.search(s.replace("-", "[- ]?"), contract, re.I)]
add("Direction contract covers thesis, own-world, story, first viewport, form and finish", not lost, f"missing sections: {lost}" if lost else "all six found")

# 3 no effects
bad = []
for pat in [r"gradient\(", r"box-shadow\s*:\s*(?!none)", r"text-shadow\s*:\s*(?!none)", r"backdrop-filter", r"blur\(", r"drop-shadow"]:
    for m in re.finditer(pat, allcss, re.I):
        bad.append(pat)
add("CSS uses no gradients, shadows, glow, blur or glass", not bad, f"found: {sorted(set(bad))}" if bad else "none found")


# 4 colour budget
def colours(s: str):
    found = []
    for m in re.finditer(r"#([0-9a-fA-F]{3,8})\b", s):
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        if len(h) >= 6:
            found.append(tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)))
    for m in re.finditer(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)", s):
        found.append(tuple(int(m.group(i)) / 255 for i in (1, 2, 3)))
    return found


cols = colours(allcss + "\n" + re.sub(r"<style[\s\S]*?</style>", "", page))
buckets = set()
for r, g, b in cols:
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s > 0.18 and v > 0.5:
        buckets.add(int(h * 360 // 30))
add("At most two chromatic hues in the whole page (one signal, one state colour)", len(buckets) <= 2, f"{len(buckets)} hue buckets: {sorted(buckets)}")
hsv = [colorsys.rgb_to_hsv(*c) for c in cols]
sig = [c for c in hsv if 195 <= c[0] * 360 <= 225 and 0.08 < c[1] < 0.45 and c[2] > 0.5]
warm = [c for c in hsv if 25 <= c[0] * 360 <= 45 and c[1] > 0.35 and c[2] > 0.5]
add("Signal colour is a muted steel-blue (the house accent: hue 195-225, saturation under 0.45)", bool(sig), f"{len(sig)} matching colours" + ("" if sig else f"; chromatic hues present: {sorted(set(int(c[0]*360) for c in hsv if c[1] > 0.18))}"))
add("State colour is a warm amber (the house warn: hue 25-45)", bool(warm), f"{len(warm)} matching colours")


# 5 dark ground
def lum(c):
    f = lambda x: x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


m = re.search(r"(?:body|html|:root|\.[\w-]+)\s*\{[^}]*?background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8})", allcss) or re.search(r"--(?:ground|bg|background)[\w-]*\s*:\s*(#[0-9a-fA-F]{3,8})", allcss)
if m:
    c = colours(m.group(1))[0]
    add("Page ground is matte near-black", lum(c) < 0.03, f"ground {m.group(1)}, luminance {lum(c):.3f}")
else:
    add("Page ground is matte near-black", False, "no ground colour found")

# 6 no pure white text
pw = re.search(r"(?<!background-)color\s*:\s*(#fff\b|#ffffff\b|white\b)", allcss, re.I)
add("Ink is warm off-white, not pure white", not pw, "pure white text colour found" if pw else "no pure white text colour")

# 7 type families
fams = set(f.strip(" '\"").lower() for f in re.findall(r"font-family\s*:\s*([^,;}]+)", allcss))
fams = {f for f in fams if f not in {"inherit", "sans-serif", "monospace", "serif", "system-ui", "ui-monospace"} and not f.startswith("var(")}
add("At most two type families", len(fams) <= 2, f"families: {sorted(fams)}")

# 8 reduced motion and mobile
add("Honours prefers-reduced-motion", "prefers-reduced-motion" in allcss or "prefers-reduced-motion" in page, "found" if "prefers-reduced-motion" in page + allcss else "not found")
mq = []
for val, unit in re.findall(r"max-width\s*:\s*([\d.]+)(px|em|rem)", allcss + page):
    mq.append(float(val) * (16 if unit in ("em", "rem") else 1))
mq += [float(v) * 1 for v in re.findall(r"max-inline-size\s*:\s*(\d+)px", allcss)]
add("Has a mobile breakpoint at or below 800px (px, em or rem)", any(x <= 800 for x in mq), f"max-width queries in px: {mq}")


# 9 visible-text checks
def visible(s: str) -> str:
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s)


vis = visible(page)
if args.eval == "ferryline":
    add("Uses 'dispatch desk' and never 'control room'", bool(re.search(r"dispatch desk", vis, re.I)) and not re.search(r"control room", page, re.I), f"dispatch desk: {bool(re.search('dispatch desk', vis, re.I))}, control room: {bool(re.search('control room', page, re.I))}")
    named = re.findall(r"\b[A-Z][a-z]+ (?:Ferries|Ferry Co|Lines|Line Ltd|Ltd)\b", vis + report)
    add("Does not name the operator", not named, f"names found: {named}" if named else "operator not named")
ab = re.findall(r"\b(?:never(?! (?:been|measured|run|tried|tested))|always|guarantee[ds]?|perfect(?:ly)?|flawless|zero (?:errors|bugs|risk))\b|\b100\s?%", vis, re.I)
add("Page copy contains no absolutes", not ab, f"found: {ab}" if ab else "none")
if args.eval == "ferryline":
    add("Shows the miss (9 of 120) and the unmeasured pilot on the page", bool(re.search(r"\b9\s*(?:of|/)\s*120", vis)) and bool(re.search(r"not measured", vis, re.I)), f"9 of 120: {bool(re.search(r'9 *(?:of|/) *120', vis))}, not measured: {bool(re.search('not measured', vis, re.I))}")
else:
    add("Shows the miss (12 of 30) and the unmeasured field trial on the page", bool(re.search(r"\b12\s*(?:of|/)\s*30", vis)) and bool(re.search(r"not measured|none yet", vis, re.I)), "checked")
    add("Uses 'coordinator' and never 'admin'", bool(re.search(r"coordinator", vis, re.I)) and not re.search(r"\badmin(?:istrator)?\b", vis, re.I), "checked")
    add("Does not print derived numbers (174 correct photos, 40%, 60%)", not re.search(r"\b174\b|\b40\s?%|\b60\s?%", vis), "derived number found" if re.search(r"\b174\b|\b40\s?%|\b60\s?%", vis) else "none printed")
    add("Sample figures are tagged SAMPLE and none is tagged MEASURED", bool(re.search(r"\bSAMPLE\b", vis)) and not re.search(r"(?<!NOT )\bMEASURED\b", vis), f"SAMPLE shown: {bool(re.search(r'SAMPLE', vis))}; MEASURED tag shown: {bool(re.search(r'(?<!NOT )\bMEASURED\b', vis))}")
    names = [vis.lower().find(x) for x in ("datastore", "vision", "run")]
    add("Platform services are listed strongest first (Datastore, Vision, Run) and all three appear", all(i >= 0 for i in names) and names == sorted(names) or (all(i >= 0 for i in names) and bool(re.search(r"datastore[\s\S]{0,400}vision[\s\S]{0,400}\brun\b", vis, re.I))), f"first positions: {names}")
    add("Page has capabilities, problem, response and the prototype link", all(re.search(x, vis, re.I) for x in ("problem", "response", "classif")) and "example.org/tern" in page, "checked")


# 10 numbers traced to the data file
def nums(s: str) -> set[str]:
    return {n.rstrip(".,") for n in re.findall(r"\d[\d,.]*", s)}


allowed = nums(data)
printed = set()
for n in nums(vis):
    if re.fullmatch(r"0\d", n) or re.fullmatch(r"20\d\d", n) or n in {"10", "11"} and "2026-10-11" in vis:
        continue
    printed.add(n)
stray = sorted(n for n in printed if n not in allowed)
add("Every number printed on the page appears in the data file", not stray, f"not in data file: {stray}" if stray else f"{len(printed)} numbers all traced")
add("Data file names its sources", bool(re.search(r"(source|sim-2026-10-11|eval-2026-10-12|as[- ]of)", data, re.I)), "checked")

# 11 asset prompts
blocks = prompts
add("Asset prompts say 'no text' at least twice and use a start frame", len(re.findall(r"no text", blocks, re.I)) >= 2 and bool(re.search(r"start frame|keyframe", blocks, re.I)), f"'no text' x{len(re.findall('no text', blocks, re.I))}, start frame: {bool(re.search('start frame|keyframe', blocks, re.I))}")
add("Asset prompts or report ask for cost approval before generating", bool(re.search(r"(simulate_cost|cost estimate|estimate the cost|approv|credits|your go|before (?:generating|spending))", prompts + report, re.I)), "found" if re.search(r"(simulate_cost|cost estimate|estimate the cost|approv|credits|before (?:generating|spending))", prompts + report, re.I) else "not found")

# 12 report
add("Report lists what was not verified and decisions for the owner", bool(re.search(r"not verified|did not verify|unverified|not tested|untested", report, re.I)) and bool(re.search(r"decision", report, re.I)), "checked")

summary = {"passed": sum(e["passed"] for e in exp), "failed": sum(not e["passed"] for e in exp), "total": len(exp)}
summary["pass_rate"] = round(summary["passed"] / summary["total"], 2)
(run / "grading.json").write_text(json.dumps({"expectations": exp, "summary": summary}, indent=1))
print(f"{run.name}: {summary['passed']}/{summary['total']}")
for e in exp:
    print(("PASS " if e["passed"] else "FAIL ") + e["text"] + "  --  " + e["evidence"])
