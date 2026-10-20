"""Tests for the skill's scripts. Run: python3 -m unittest discover -s tests"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "field-report-landing" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import make_stack_svg  # noqa: E402
import scaffold_page  # noqa: E402


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


class ScaffoldValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = copy.deepcopy(scaffold_page.EXAMPLE)

    def errors(self) -> list[str]:
        return scaffold_page.validate(self.cfg)[0]

    def test_example_is_valid(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_banned_word_is_rejected(self) -> None:
        self.cfg["words"] = {"banned": ["fictional"]}
        self.assertTrue(any("banned word" in e for e in self.errors()))

    def test_absolute_is_rejected(self) -> None:
        self.cfg["lede"] = "It never makes mistakes."
        self.assertTrue(any("absolute" in e for e in self.errors()))

    def test_never_measured_is_allowed(self) -> None:
        self.cfg["problem"]["body"] = "What was never measured is listed below."
        self.assertEqual(self.errors(), [])

    def test_hundred_percent_is_rejected(self) -> None:
        self.cfg["problem"]["body"] = "Accurate 100% of the time."
        self.assertTrue(any("absolute" in e for e in self.errors()))

    def test_unknown_tag_is_rejected(self) -> None:
        self.cfg["results"]["rows"][0]["tag"] = "PROVEN"
        self.assertTrue(any("unknown tag" in e for e in self.errors()))

    def test_figure_needs_source_and_date(self) -> None:
        self.cfg["results"]["rows"][0].pop("source")
        self.assertTrue(any("needs a source" in e for e in self.errors()))

    def test_bar_must_be_the_printed_number(self) -> None:
        self.cfg["results"]["rows"][1]["pct"] = 70
        self.assertTrue(any("bar percentage" in e for e in self.errors()))

    def test_no_misses_is_rejected_unless_allowed(self) -> None:
        self.cfg["misses"] = []
        self.assertTrue(any("no misses" in e for e in self.errors()))
        self.cfg["allow_no_misses"] = "nothing failed in the single run"
        self.assertEqual(self.errors(), [])

    def test_quantity_word_warns(self) -> None:
        self.cfg["problem"]["body"] = "Volunteers file hundreds of photos."
        self.assertTrue(any("quantity word" in w for w in scaffold_page.validate(self.cfg)[1]))

    def test_digits_in_prose_warn(self) -> None:
        self.cfg["problem"]["body"] = "It took 40 hours."
        self.assertTrue(any("digits in prose" in w for w in scaffold_page.validate(self.cfg)[1]))


class ScaffoldBuild(unittest.TestCase):
    def test_builds_a_self_contained_page(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            cfg = Path(t) / "c.json"
            cfg.write_text(json.dumps(scaffold_page.EXAMPLE))
            r = run(str(SCRIPTS / "scaffold_page.py"), "--config", str(cfg), "--out", str(Path(t) / "out"))
            self.assertEqual(r.returncode, 0, r.stderr)
            html = (Path(t) / "out" / "index.html").read_text()
            self.assertIn("<svg", html)
            self.assertIn("prefers-reduced-motion", html)
            self.assertNotIn("http://", html.replace("http://www.w3.org/2000/svg", ""))
            self.assertIn("SAMPLE", html)  # sample figures are labelled as such
            self.assertTrue((Path(t) / "out" / "results.json").exists())
            self.assertTrue((Path(t) / "out" / "DESIGN-landing.md").exists())
            self.assertTrue((Path(t) / "out" / "PROVENANCE.md").exists())
            self.assertIn("Sample figures, and what was not measured", html)  # heading agrees with the SAMPLE tags

    def test_no_text_uses_the_low_contrast_token(self) -> None:
        html = scaffold_page.build_page(scaffold_page.EXAMPLE)
        self.assertNotIn("color:var(--ink-3)", html.replace(" ", ""))

    def test_refuses_and_writes_nothing_when_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            bad = copy.deepcopy(scaffold_page.EXAMPLE)
            bad["misses"] = []
            cfg = Path(t) / "c.json"
            cfg.write_text(json.dumps(bad))
            r = run(str(SCRIPTS / "scaffold_page.py"), "--config", str(cfg), "--out", str(Path(t) / "out"))
            self.assertEqual(r.returncode, 1)
            self.assertFalse((Path(t) / "out").exists())


class StackSvg(unittest.TestCase):
    def test_layer_counts(self) -> None:
        for n in range(3, 7):
            cfg = {"layers": [{"label": f"L{i}"} for i in range(n)]}
            self.assertEqual(make_stack_svg.build_svg(cfg).count('class="layer"'), n)

    def test_rejects_bad_counts_and_art(self) -> None:
        with self.assertRaises(ValueError):
            make_stack_svg.build_svg({"layers": [{"label": "a"}, {"label": "b"}]})
        with self.assertRaises(ValueError):
            make_stack_svg.build_svg({"layers": [{"label": "a", "art": "nope"}, {"label": "b"}, {"label": "c"}]})

    def test_legend_free_variant(self) -> None:
        a = make_stack_svg.build_svg(make_stack_svg.DEMO, legend=True)
        b = make_stack_svg.build_svg(make_stack_svg.DEMO, legend=False)
        self.assertIn('class="legend"', a)
        self.assertNotIn('class="legend"', b)

    def test_honours_reduced_motion(self) -> None:
        self.assertIn("prefers-reduced-motion", make_stack_svg.build_svg(make_stack_svg.DEMO))


class HonestyScan(unittest.TestCase):
    def test_flags_banned_absolute_and_stray_number_but_not_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "data").mkdir()
            (d / "data" / "r.ts").write_text("/** Source: run 1, as of 2026-01-01. */\nexport const R = [{ v: '2.7 s' }];\n")
            (d / "Hero.tsx").write_text(
                'export const H = () => (<section><h1>The cockpit never lies</h1><p>Median 2.7 s</p>'
                '<path d="M 12 3 L 40 9.5" style="width:81%" /></section>);\n')
            r = run(str(SCRIPTS / "honesty_scan.py"), str(d), "--banned", "cockpit")
            self.assertEqual(r.returncode, 1)
            self.assertIn("banned word 'cockpit'", r.stdout)
            self.assertIn("absolute 'never'", r.stdout)
            self.assertIn("2.7 s", r.stdout)
            self.assertNotIn("M 12 3", r.stdout)
            self.assertNotIn("width:81%", r.stdout)

    def test_missing_source_header_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "data").mkdir()
            (d / "data" / "r.ts").write_text("export const R = [{ v: '1' }];\n")
            r = run(str(SCRIPTS / "honesty_scan.py"), str(d))
            self.assertEqual(r.returncode, 1)
            self.assertIn("no header comment naming its source", r.stdout)


class AssetVersion(unittest.TestCase):
    def test_flags_change_without_bump(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "public").mkdir()
            (d / "public" / "a.webp").write_text("x")
            ver = d / "assets.ts"
            ver.write_text('export const ASSET_VERSION = "1";\n')
            base = [str(SCRIPTS / "asset_version_check.py"), "--dir", str(d / "public"), "--version-file", str(ver)]
            self.assertEqual(run(*base).returncode, 0)  # records the manifest
            (d / "public" / "a.webp").write_text("y")
            self.assertEqual(run(*base).returncode, 1)
            ver.write_text('export const ASSET_VERSION = "2";\n')
            self.assertEqual(run(*base).returncode, 0)


if __name__ == "__main__":
    unittest.main()
