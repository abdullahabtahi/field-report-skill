#!/usr/bin/env python3
"""Scaffold a complete single-file field-report page from one config file, and refuse to if the config breaks
the honesty rules.

One config is the single source of truth: the page, its ledger and results.json are all generated from it, so a
number on the page cannot drift from its data. The page is plain HTML and CSS (no JavaScript, no external requests),
in the house design world: tokens, hero stack, problem and response, capability frames, platform list, results
ledger with misses in the warn colour, and a close. It is a starting point; interactive figures, the scroll
sequence and the map are added on top (see references/build-checklist.md).

usage: scaffold_page.py --config landing.config.json --out dist/
       scaffold_page.py --example > landing.config.json      (print a filled example)

Checks (errors stop the build): banned words, absolutes, unknown tags, rows missing source or as-of, a bar percentage
that is not the printed number, no misses shown. Warnings: digits in prose outside the ledger.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_stack_svg import build_svg  # noqa: E402

TAGS = {"MEASURED", "TESTED", "NOT MEASURED", "BY DESIGN", "SAMPLE", "ILLUSTRATIVE", "DERIVED", "REAL DATA"}
NEEDS_SOURCE = {"MEASURED", "TESTED", "SAMPLE", "ILLUSTRATIVE", "DERIVED"}
GAP_TAGS = {"NOT MEASURED"}
ABSOLUTES = re.compile(r"\b(?:never(?! (?:been|measured|run|tried|tested))|always|guarantee[ds]?|perfect(?:ly)?|flawless(?:ly)?|zero (?:errors|bugs|risk))\b|\b100\s?%", re.I)
QUANTITY = re.compile(r"\b(?:hundreds|thousands|millions|dozens|majority|most of|nearly all|almost all|half of|twice as|several times)\b", re.I)
ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = {
    "project": "Northwind Ledger", "event": "Example Hackathon", "link": "#", "link_label": "Open the live prototype",
    "crumbs": ["Case study", "Example Hackathon", "Northwind Ledger"],
    "kicker": "Field report: an audit trail for a farm-credit co-op",
    "headline": "Every loan decision, traceable to its evidence.",
    "lede": "A copilot proposes a credit decision with the evidence beside it; an officer approves; the ledger remembers. The diagram reads bottom to top; the ledger below lists the figures, their sources, and what has not been measured.",
    "data_statement": "The co-op and its members are fictional. The loan records are synthetic; the rainfall series is real public data. This is a hackathon prototype, not a production system.",
    "layers": [
        {"label": "Records", "items": ["Synthetic loan records", "Rainfall and prices"], "tag": "REAL DATA"},
        {"label": "Checks", "items": ["Every record validated on entry"]},
        {"label": "Model", "items": ["Members, farms, loans, one meaning"]},
        {"label": "Assistant", "items": ["Proposes; cites every figure"]},
        {"label": "Officer", "items": ["A person approves", "Each approval is recorded"], "tag": "BY DESIGN"}],
    "problem": {"title": "Decisions nobody could explain", "body": "Credit decisions lived in spreadsheets and phone calls. When a loan was questioned months later, nobody could say what the officer had seen."},
    "response": {"title": "A copilot that shows its evidence", "body": "The assistant proposes a decision and lists the records behind each figure. An officer decides. The decision and its evidence are stored together."},
    "capabilities": [
        {"title": "Evidence beside every figure", "body": "Each number in an answer links to the record and rule that produced it.", "source": "Prototype run, example scenario set"},
        {"title": "A second pair of eyes", "body": "Large loans need two officers; the assistant has no approve action.", "source": "Prototype design"}],
    "platform": {"title": "How it runs", "intro": "The services that carry each step, strongest first.",
                 "services": [{"name": "Service A", "does": "Stores and queries the records", "first": True}, {"name": "Service B", "does": "Hosts the assistant"}]},
    "results": {"run": "Example run, 2026-01-01", "rows": [
        {"id": "R1", "label": "Median time to a drafted decision", "value": "12 s", "caption": "Over the scenario set.", "source": "example-run-01", "as_of": "2026-01-01", "tag": "SAMPLE"},
        {"id": "R2", "label": "Decisions matched to their evidence", "value": "90%", "pct": 90, "caption": "Sampled decisions.", "source": "example-run-01", "as_of": "2026-01-01", "tag": "SAMPLE"}]},
    "misses": [{"id": "M1", "label": "Live pilot with a co-op", "value": "None yet", "caption": "No real members have used it.", "source": "-", "as_of": "-", "tag": "NOT MEASURED"}],
    "close": {"title": "See it work", "cta_label": "Open the live prototype", "credit": "Built for Example Hackathon"},
    "words": {"banned": []},
}


def text_fields(cfg: dict):
    """(label, text, prose) for every string the page prints. Prose fields should not carry numbers."""
    for k in ("kicker", "headline", "lede", "data_statement"):
        yield k, cfg.get(k, ""), k in ("lede",)
    for k in ("problem", "response"):
        for kk, v in cfg.get(k, {}).items():
            yield f"{k}.{kk}", v, kk == "body"
    for i, c in enumerate(cfg.get("capabilities", [])):
        for kk, v in c.items():
            yield f"capabilities[{i}].{kk}", v, kk == "body"
    p = cfg.get("platform", {})
    yield "platform.intro", p.get("intro", ""), True
    for i, s in enumerate(p.get("services", [])):
        yield f"platform.services[{i}].does", s.get("does", ""), True
    for i, l in enumerate(cfg.get("layers", [])):
        yield f"layers[{i}].label", l.get("label", ""), False
        for j, it in enumerate(l.get("items", [])):
            yield f"layers[{i}].items[{j}]", it, True
    for sect in ("rows",):
        for i, r in enumerate(cfg.get("results", {}).get(sect, [])):
            for kk in ("label", "value", "caption"):
                yield f"results.rows[{i}].{kk}", str(r.get(kk, "")), False
    for i, r in enumerate(cfg.get("misses", [])):
        for kk in ("label", "value", "caption"):
            yield f"misses[{i}].{kk}", str(r.get(kk, "")), False
    for kk, v in cfg.get("close", {}).items():
        yield f"close.{kk}", v, False


def validate(cfg: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    banned = [w for w in cfg.get("words", {}).get("banned", []) if w]
    banned_re = re.compile(r"\b(" + "|".join(re.escape(w) for w in banned) + r")\b", re.I) if banned else None
    for label, text, prose in text_fields(cfg):
        if not isinstance(text, str):
            continue
        if banned_re and (m := banned_re.search(text)):
            errors.append(f"{label}: banned word {m.group(0)!r}")
        if (m := ABSOLUTES.search(text)):
            errors.append(f"{label}: absolute {m.group(0)!r} (say what is checked and how)")
        if prose and QUANTITY.search(text):
            warnings.append(f"{label}: quantity word with no source ({QUANTITY.search(text).group(0)!r}); give it a ledger row or reword: {text[:60]!r}")
        if prose and re.search(r"\d", text):
            warnings.append(f"{label}: digits in prose; numbers belong in a ledger row with a source: {text[:60]!r}")
    rows = cfg.get("results", {}).get("rows", []) + cfg.get("misses", [])
    if not cfg.get("misses") and not cfg.get("allow_no_misses"):
        errors.append("no misses: a page with no gaps is not believed. List what was not measured or what failed (or set allow_no_misses with a reason).")
    for r in rows:
        rid = r.get("id", "?")
        tag = r.get("tag", "")
        if tag not in TAGS:
            errors.append(f"{rid}: unknown tag {tag!r}; use one of {sorted(TAGS)}")
        if tag in NEEDS_SOURCE and (not r.get("source") or r.get("source") == "-" or not r.get("as_of") or r.get("as_of") == "-"):
            errors.append(f"{rid}: a {tag} figure needs a source and an as_of date")
        if "pct" in r:
            nums = re.findall(r"\d+(?:\.\d+)?", str(r.get("value", "")))
            if not nums or float(nums[0]) != float(r["pct"]):
                errors.append(f"{rid}: bar percentage {r['pct']} is not the printed value {r.get('value')!r}; a bar may draw only a printed number")
    return errors, warnings


CSS = """
*{box-sizing:border-box}body{margin:0}
.skip{position:absolute;left:-999px}.skip:focus{left:var(--pad);top:8px;background:var(--ink);color:var(--ground);padding:6px 10px;z-index:9}
.fde-nav{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:0 var(--pad);height:var(--nav-h);border-bottom:1px solid var(--rule)}
.fde-crumbs{display:flex;gap:10px;flex-wrap:wrap;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2)}
.fde-crumbs span+span::before{content:"/";margin-right:10px;color:var(--ink-2)}.fde-crumbs span:last-child{color:var(--ink)}
.fde-cta{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;border-bottom:1px solid var(--ink-3);padding-bottom:2px;white-space:nowrap}
.fde-hero{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:clamp(16px,3vw,56px);padding:clamp(32px,6vh,72px) var(--pad) 48px;min-height:calc(100vh - var(--nav-h));align-items:center}
.fde-kicker{margin:0 0 24px}.fde-display{margin:0 0 24px;max-width:14ch}
.fde-lede{color:var(--ink-2);max-width:46ch;margin:0 0 32px}
.fde-cue{display:inline-block;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;border-left:1px solid var(--ink-3);padding-left:12px;margin-bottom:24px}
.fde-data{color:var(--ink-2);font-size:.82rem;max-width:52ch;border-left:1px solid var(--rule);padding-left:12px;margin:0}
.fde-art-wrap svg{width:100%;height:auto;display:block;overflow:visible}.fde-art-wrap .m{display:none}
.fde-legend-list{display:none;list-style:none;margin:16px 0 0;padding:0}
.fde-legend-list li{border-left:1px solid var(--rule);padding:6px 0 6px 12px;margin-bottom:8px}.fde-legend-list b{font-weight:500;letter-spacing:.14em;text-transform:uppercase;font-size:.78rem}
.fde-legend-list .n{font-family:var(--fde-mono),ui-monospace,monospace;color:var(--ink-2);margin-right:8px;font-size:.78rem}.fde-legend-list span{display:block;color:var(--ink-2);font-size:.9rem}
.fde-sec{padding:clamp(48px,9vh,112px) var(--pad);border-top:1px solid var(--rule)}
.fde-two{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,5vw,96px)}
.fde-two h3,.fde-frame h3{font-weight:400;font-size:1.35rem;letter-spacing:-.01em;margin:10px 0 12px}.fde-two p{color:var(--ink-2);max-width:48ch;margin:0}
.fde-frames{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr));gap:24px;margin-top:32px}
.fde-frame{border:1px solid var(--rule);margin:0}.fde-bar{display:flex;justify-content:space-between;padding:10px 16px;border-bottom:1px solid var(--rule)}
.fde-frame .body{padding:20px 16px}.fde-frame p{color:var(--ink-2);margin:0}.fde-frame figcaption{padding:10px 16px;border-top:1px solid var(--rule);font-size:.78rem;color:var(--ink-2)}
.fde-svc{list-style:none;margin:28px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:12px 24px}
.fde-svc li{border-left:1px solid var(--rule);padding:4px 0 4px 14px}.fde-svc li[data-first]{border-left-color:var(--sig)}.fde-svc b{display:block;font-weight:500}.fde-svc span{color:var(--ink-2);font-size:.9rem}
.fde-run{margin:12px 0 28px;color:var(--ink-2);font-size:.85rem}
.fde-ledger{width:100%;border-collapse:collapse}.fde-ledger th{font-weight:400;text-align:left;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2);padding:0 12px 10px 0}
.fde-ledger td{padding:18px 12px 18px 0;border-top:1px solid var(--rule);vertical-align:top}
.fde-ledger .id{width:48px;color:var(--ink-2)}.fde-ledger .val{font-size:clamp(1.6rem,2.6vw,2.4rem);letter-spacing:-.02em;white-space:nowrap}
.fde-ledger .lbl{max-width:34ch}.fde-ledger .cap{display:block;color:var(--ink-2);font-size:.85rem;margin-top:4px}
.fde-ledger .src{font-size:.75rem;color:var(--ink-2)}.fde-track{height:3px;background:var(--rule);margin-top:10px;position:relative}.fde-track i{position:absolute;left:0;top:0;bottom:0;background:var(--ink)}
.fde-ledger tr.gap .val{color:var(--warn)}.fde-ledger tr.gap .fde-track i{background:var(--warn)}
.fde-ledger .grp th{padding:36px 0 10px;color:var(--warn);border-top:1px solid var(--rule)}.fde-miss-h{color:var(--warn)}.fde-sample{color:var(--ink-2);font-size:.8rem;margin:0 0 16px}
.fde-close{text-align:left}.fde-close h2{margin:0 0 24px}.fde-close .credit{color:var(--ink-2);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;margin-top:32px}
.fde-foot{display:flex;justify-content:space-between;gap:16px;padding:24px var(--pad);border-top:1px solid var(--rule);font-size:.78rem;color:var(--ink-2)}
@media (max-width:600px){.fde-crumbs span:not(:nth-last-child(-n+2)){display:none}.fde-crumbs span:nth-last-child(2)::before{content:none}.fde-foot{flex-direction:column}.fde-nav{height:auto;flex-wrap:wrap;padding:14px var(--pad);row-gap:10px}}
@media (max-width:900px){.fde-hero{grid-template-columns:1fr;min-height:0}.fde-two{grid-template-columns:1fr}
.fde-art-wrap .d{display:none}.fde-art-wrap .m{display:block;max-width:420px}.fde-legend-list{display:block}
.fde-ledger thead{display:none}.fde-ledger,.fde-ledger tbody,.fde-ledger tr,.fde-ledger td,.fde-ledger .grp th{display:block}.fde-ledger td{border:0;padding:4px 0}.fde-ledger tr{border-top:1px solid var(--rule);padding:16px 0}.fde-ledger .id{width:auto}}
""".strip()


def tag_html(tag: str) -> str:
    gap = " data-gap" if tag in GAP_TAGS else ""
    return f'<span class="fde-tag fde-mono"{gap}>{escape(tag)}</span>'


def row_html(r: dict, gap: bool) -> str:
    bar = f'<div class="fde-track" aria-hidden="true"><i style="width:{r["pct"]}%"></i></div>' if "pct" in r else ""
    src = f'{escape(r["source"])} · as of {escape(r["as_of"])}' if r.get("source") not in (None, "-") else "no run yet"
    return (f'<tr class="{"gap" if gap else ""}"><td class="id fde-mono">{escape(r["id"])}</td>'
            f'<td class="lbl">{escape(r["label"])}<span class="cap">{escape(r.get("caption", ""))}</span></td>'
            f'<td class="val fde-mono">{escape(str(r["value"]))}{bar}</td>'
            f'<td class="src fde-mono">{src}</td><td>{tag_html(r["tag"])}</td></tr>')


def build_page(cfg: dict) -> str:
    stack_cfg = {"title": cfg.get("stack_title", f"Exploded isometric diagram of the {cfg['project']} layers, bottom to top, with a signal rising through them."), "layers": cfg["layers"]}
    desktop = build_svg(stack_cfg, legend=True, uid="sd")
    mobile = build_svg(stack_cfg, legend=False, uid="sm")
    legend_list = "".join(f'<li><span class="n">[{i + 1:02d}]</span><b>{escape(l["label"])}</b>' + "".join(f"<span>→ {escape(it)}</span>" for it in l.get("items", [])) + "</li>"
                          for i, l in reversed(list(enumerate(cfg["layers"]))))
    caps = "".join(f'<figure class="fde-frame"><div class="fde-bar"><span class="fde-label">{i + 1:02d}</span><span class="fde-label">{escape(c["title"])}</span></div>'
                   f'<div class="body"><h3>{escape(c["title"])}</h3><p>{escape(c["body"])}</p></div>'
                   f'<!-- add the interactive figure here, drawing from a data file whose header names its source -->'
                   f'<figcaption class="fde-mono">origin: {escape(c.get("source", ""))}</figcaption></figure>' for i, c in enumerate(cfg.get("capabilities", [])))
    plat = cfg.get("platform", {})
    svc = "".join(f'<li{" data-first" if s.get("first") else ""}><b>{escape(s["name"])}</b><span>{escape(s["does"])}</span></li>' for s in plat.get("services", []))
    res = cfg["results"]
    tags = {r["tag"] for r in res["rows"] + cfg.get("misses", [])}
    placeholder = bool(tags & {"SAMPLE", "ILLUSTRATIVE"})
    ledger_title = "Sample figures, and what was not measured" if placeholder else "Measured, and what was not"
    sample = '<p class="fde-sample fde-mono">Figures tagged SAMPLE are placeholders, not measured results.</p>' if "SAMPLE" in tags else ""
    rows = "".join(row_html(r, False) for r in res["rows"])
    misses = "".join(row_html(r, True) for r in cfg.get("misses", []))
    head = '<thead><tr><th>#</th><th>Result</th><th>Value</th><th>Source</th><th>Tag</th></tr></thead>'
    cl = cfg.get("close", {})
    crumbs = "".join(f"<span>{escape(c)}</span>" for c in cfg.get("crumbs", []))
    link = escape(cfg.get("link", "#"))
    tokens = (ROOT / "assets" / "tokens.css").read_text()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(cfg['project'])}: {escape(cfg.get('event', 'case study'))}</title>
<style>{tokens}
{CSS}</style></head>
<body><div class="fde"><a class="skip" href="#case">Skip to the case study</a>
<header class="fde-nav"><nav class="fde-crumbs" aria-label="Breadcrumb">{crumbs}</nav><a class="fde-cta" href="{link}">{escape(cfg.get('link_label', 'Open the prototype'))}</a></header>
<main>
<section class="fde-hero" aria-labelledby="h">
<div><p class="fde-label fde-kicker">{escape(cfg['kicker'])}</p><h1 id="h" class="fde-display">{escape(cfg['headline'])}</h1><p class="fde-lede">{escape(cfg['lede'])}</p>
<a class="fde-cue" href="#case">Read the case study</a><p class="fde-data">{escape(cfg['data_statement'])}</p></div>
<div class="fde-art-wrap"><div class="d">{desktop}</div><div class="m">{mobile}<ol class="fde-legend-list" aria-label="Layers, top to bottom">{legend_list}</ol></div></div>
</section>
<section id="case" class="fde-sec"><div class="fde-two"><div><p class="fde-label">The problem</p><h3>{escape(cfg['problem']['title'])}</h3><p>{escape(cfg['problem']['body'])}</p></div>
<div><p class="fde-label">The response</p><h3>{escape(cfg['response']['title'])}</h3><p>{escape(cfg['response']['body'])}</p></div></div></section>
<section class="fde-sec" aria-labelledby="cap"><h2 id="cap" class="fde-h2">What it can do</h2><div class="fde-frames">{caps}</div></section>
<section class="fde-sec" aria-labelledby="plat"><h2 id="plat" class="fde-h2">{escape(plat.get('title', 'How it runs'))}</h2><p class="fde-run">{escape(plat.get('intro', ''))}</p><ul class="fde-svc">{svc}</ul></section>
<section class="fde-sec" aria-labelledby="res"><h2 id="res" class="fde-h2">{ledger_title}</h2><p class="fde-run fde-mono">{escape(res.get('run', ''))}</p>{sample}
<table class="fde-ledger">{head}<tbody>{rows}</tbody><tbody><tr class="grp"><th colspan="5" class="fde-miss-h">Misses and gaps</th></tr>{misses}</tbody></table></section>
<section class="fde-sec fde-close"><h2 class="fde-h2">{escape(cl.get('title', ''))}</h2><a class="fde-cta" href="{link}">{escape(cl.get('cta_label', 'Open the prototype'))}</a><p class="credit">{escape(cl.get('credit', ''))}</p></section>
</main>
<footer class="fde-foot"><span>{escape(cfg['data_statement'])}</span><a href="#h">Back to top</a></footer></div></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--example", action="store_true")
    a = ap.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if not a.config or not a.out:
        ap.error("pass --config and --out (or --example)")
    cfg = json.loads(a.config.read_text())
    errors, warnings = validate(cfg)
    for w in warnings:
        print("WARN ", w)
    if errors:
        for e in errors:
            print("ERROR", e, file=sys.stderr)
        print(f"{len(errors)} errors: nothing written", file=sys.stderr)
        return 1
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "index.html").write_text(build_page(cfg))
    design = (ROOT / "assets" / "design-entry.template.md").read_text().format(
        project=cfg["project"], event=cfg.get("event", "the event"), contract=cfg.get("contract_path", "the direction contract for this page"))
    for name, body in (("DESIGN-landing.md", design),
                       ("PROVENANCE.md", f"# Provenance, {cfg['project']} landing\n\nNo generated or photographic rasters ship with this page yet; the hero is drawn SVG. When a raster is added, list it here with the tool, model, prompt, date and where it is used, and say on the page that it is generated.\n")):
        if not (a.out / name).exists():
            (a.out / name).write_text(body)
    (a.out / "results.json").write_text(json.dumps({"run": cfg["results"].get("run"), "rows": cfg["results"]["rows"], "misses": cfg.get("misses", [])}, indent=2))
    print(f"wrote {a.out}/index.html, results.json, DESIGN-landing.md and PROVENANCE.md ({len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
