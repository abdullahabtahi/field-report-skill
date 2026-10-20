#!/usr/bin/env python3
"""Heuristic honesty scan for landing-page source.

Flags, in text the visitor would read (string literals and JSX text):
  1. banned words or names from the brief (--banned), whole-word, case-insensitive;
  2. absolutes ("never", "always", "100%", "guaranteed", "perfect", ...);
  3. numbers that appear outside the content/data files (they should live in one sourced file).
Also checks that each data/content file starts with a header comment that names a source.

It is a heuristic and will miss things and over-flag. Read every finding; do not just silence it.

usage: honesty_scan.py SRC_DIR [--banned "word1,word2"] [--content-dirs data,content] [--strict]
Exit code 1 if there are banned words, absolutes or missing source headers; with --strict also for stray numbers.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".html", ".md", ".mdx"}
ABSOLUTES = re.compile(r"\b(?:never(?! (?:been|measured|run|tried|tested))|always|guarantee[ds]?|perfect(?:ly)?|flawless(?:ly)?|zero (?:errors|bugs|risk))\b|\b100\s?%", re.I)
NUMBER = re.compile(r"(?<![\w.#-])(\$\s?\d[\d,.]*[kKmMbB]?|\d[\d,.]*\s?(?:%|ms|s\b|x\b|×|k\b|M\b|MB|GB))")
STRING = re.compile(r"""(["'`])((?:\\.|(?!\1).)*)\1""")
JSX_TEXT = re.compile(r">([^<>{}]+)<")
QUANTITY = re.compile(r"\b(?:hundreds|thousands|millions|dozens|majority|most of|nearly all|almost all|half of|twice as|several times)\b", re.I)
SOURCE_HINT = re.compile(r"(source|from|as[- ]of|endpoint|query|doc|measured|snapshot|read from|pulled|records?)", re.I)


# Strings that are geometry or style, not words a visitor reads: SVG path/points data, a lone CSS declaration
# such as "width:81%", transforms, ids, URLs.
NON_VISIBLE = re.compile(
    r"^\s*(?:[MmLlHhVvCcSsQqTtAaZz0-9\s,.\-+]+|[\w-]+\s*:\s*[\w.%#()\s,-]+;?|(?:translate|rotate|scale|matrix)\([^)]*\)|https?://\S+|#[\w-]+|[\w./-]+\.(?:webp|png|svg|jpg|css|js))\s*$"
)


def visible_text(line: str) -> list[str]:
    parts = [m.group(2) for m in STRING.finditer(line)]
    parts += [m.group(1).strip() for m in JSX_TEXT.finditer(line)]
    parts = [p for p in parts if not NON_VISIBLE.match(p)]
    return [p for p in parts if re.search(r"[A-Za-z]{3}", p) or NUMBER.search(p)]


def is_content_file(path: Path, content_dirs: set[str]) -> bool:
    return bool(content_dirs & set(path.parts)) or path.stem in content_dirs


def header_has_source(text: str) -> bool:
    head = "\n".join(text.splitlines()[:25])
    m = re.search(r"/\*[\s\S]*?\*/|(?://[^\n]*\n?)+|^\s*#[^\n]*", head)
    return bool(m and SOURCE_HINT.search(m.group(0)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("--banned", default="")
    ap.add_argument("--content-dirs", default="data,content")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    if not a.src.is_dir():
        print("SRC_DIR must be a directory", file=sys.stderr)
        return 2

    banned = [w.strip() for w in a.banned.split(",") if w.strip()]
    banned_re = re.compile(r"\b(" + "|".join(re.escape(w) for w in banned) + r")\b", re.I) if banned else None
    content_dirs = {d.strip() for d in a.content_dirs.split(",") if d.strip()}

    errors: list[str] = []
    warnings: list[str] = []
    for p in sorted(a.src.rglob("*")):
        if not p.is_file() or p.suffix not in TEXT_SUFFIXES or "node_modules" in p.parts:
            continue
        text = p.read_text(errors="ignore")
        content = is_content_file(p, content_dirs)
        if content and p.suffix in {".ts", ".tsx", ".js", ".jsx"} and not header_has_source(text):
            errors.append(f"{p}:1 content file has no header comment naming its source")
        for n, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith(("//", "*", "/*", "import ")):
                continue
            for t in visible_text(line):
                if banned_re and (m := banned_re.search(t)):
                    errors.append(f"{p}:{n} banned word {m.group(0)!r} in: {t[:80]}")
                if (m := ABSOLUTES.search(t)):
                    errors.append(f"{p}:{n} absolute {m.group(0)!r} in: {t[:80]}")
                if not content and (m := QUANTITY.search(t)):
                    warnings.append(f"{p}:{n} quantity word {m.group(0)!r} with no source in: {t[:80]}")
                if not content and (m := NUMBER.search(t)):
                    warnings.append(f"{p}:{n} number {m.group(0)!r} outside a data file in: {t[:80]}")

    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("WARN   ", w)
    print(f"{len(errors)} errors, {len(warnings)} warnings (heuristic: read each one)")
    return 1 if errors or (a.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
