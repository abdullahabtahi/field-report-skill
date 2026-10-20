#!/usr/bin/env python3
"""Fail when a long-cached raster changed but the asset version constant did not.

Landing rasters are served with a one-year immutable cache and addressed with ?v=<VERSION>. Change a file
without bumping VERSION and visitors keep the old file for a year. This keeps a manifest of file hashes next
to the version it was recorded with.

usage:
  asset_version_check.py --dir public/landing --version-file src/components/landing/assets.ts
  asset_version_check.py --dir public/landing --version-file src/components/landing/assets.ts --update
Options:
  --pattern   regex whose group 1 is the version (default: ASSET_VERSION\\s*=\\s*["']([^"']+)["'])
  --manifest  manifest path (default: <dir>/../.asset-manifest.json)
  --update    record the current hashes and version (run after bumping, or the first time)
Exit code 0 = fine, 1 = files changed without a version bump, 2 = bad input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SKIP_SUFFIXES = {".json", ".md", ".txt"}  # sidecars and notes are not served assets


def hashes(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() not in SKIP_SUFFIXES and not p.name.startswith("."):
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def read_version(path: Path, pattern: str) -> str:
    m = re.search(pattern, path.read_text())
    if not m:
        sys.exit(f"could not find the version in {path} with pattern {pattern!r}")
    return m.group(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--version-file", required=True, type=Path)
    ap.add_argument("--pattern", default=r"ASSET_VERSION\s*=\s*[\"']([^\"']+)[\"']")
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--update", action="store_true")
    a = ap.parse_args()

    if not a.dir.is_dir() or not a.version_file.is_file():
        print("--dir must be a directory and --version-file a file", file=sys.stderr)
        return 2
    manifest = a.manifest or a.dir.parent / ".asset-manifest.json"
    version = read_version(a.version_file, a.pattern)
    now = hashes(a.dir)

    if a.update or not manifest.exists():
        manifest.write_text(json.dumps({"version": version, "files": now}, indent=1, sort_keys=True) + "\n")
        print(f"recorded {len(now)} files at version {version} in {manifest}")
        return 0

    old = json.loads(manifest.read_text())
    changed = sorted(k for k in now if old["files"].get(k) != now[k])
    removed = sorted(k for k in old["files"] if k not in now)
    if not changed and not removed:
        print(f"ok: {len(now)} files unchanged at version {version}")
        return 0
    if version == old["version"]:
        print(f"FAIL: version is still {version} but files changed:", file=sys.stderr)
        for k in changed:
            print(f"  changed: {k}", file=sys.stderr)
        for k in removed:
            print(f"  removed: {k}", file=sys.stderr)
        print("bump the version constant, then run with --update", file=sys.stderr)
        return 1
    print(f"version bumped {old['version']} -> {version}; run with --update to record the new hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
