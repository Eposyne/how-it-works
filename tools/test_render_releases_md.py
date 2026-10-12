"""Tests for render_releases_md.py.

    python -m unittest discover -s tools

The fixtures in tools/fixtures/releases-feed.json and releases-feed-empty.json are
byte-exact copies of the release feed fixtures of the shared contract
(contracts/director/v1/fixtures in the Eposyne architecture repository). The .md files
beside them are the pages this script renders from them; when the rendering changes on
purpose, regenerate them with

    python tools/render_releases_md.py --feed tools/fixtures/releases-feed.json --out tools/fixtures/releases-feed.md
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_releases_md as tool  # noqa: E402

FIXTURES = HERE / "fixtures"
ROOT = HERE.parent


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = tool.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class EmptyFeedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.page = tool.render(load("releases-feed-empty.json"))

    def test_says_nothing_is_released(self) -> None:
        self.assertIn("**Nothing has been released yet.**", self.page)

    def test_lists_no_line_and_no_files(self) -> None:
        self.assertNotIn("## Line", self.page)
        self.assertNotIn("## Earlier lines", self.page)
        self.assertNotIn("| File |", self.page)

    def test_keeps_the_fixed_sections(self) -> None:
        self.assertTrue(self.page.startswith("# Releases\n\n[Back to the overview](README.md)\n"))
        self.assertIn("## How versions work", self.page)
        self.assertIn("## Where releases live", self.page)

    def test_matches_the_expected_page(self) -> None:
        self.assertEqual(self.page, text(FIXTURES / "releases-feed-empty.md"))


class ReleasedFeedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.feed = load("releases-feed.json")
        self.page = tool.render(self.feed)

    def test_does_not_say_nothing_is_released(self) -> None:
        self.assertNotIn("Nothing has been released", self.page)
        self.assertIn("## Line 0.4\n", self.page)

    def test_every_artifact_has_its_version_date_notes_and_install_page(self) -> None:
        for artifact, title, install_page, _ in tool.ARTIFACTS:
            entry = self.feed["artifacts"][artifact]
            self.assertIn(f"### {title} {entry['version']}\n", self.page)
            self.assertIn(f"[Release notes]({entry['notes_url']})", self.page)
            self.assertIn(f"]({install_page})", self.page)
        self.assertIn("Released 2026-11-02.", self.page)
        self.assertIn("Verified on Unity 6000.3.", self.page)

    def test_every_file_has_its_link_size_and_sha256(self) -> None:
        for entry in self.feed["artifacts"].values():
            for item in entry["files"]:
                row = next(line for line in self.page.splitlines() if f"`{item['name']}`" in line)
                self.assertIn(f"]({item['url']})", row)
                self.assertIn(f"`{item['sha256']}`", row)
                self.assertIn(f"{item['size_bytes']:,} bytes", row)

    def test_file_labels(self) -> None:
        self.assertIn("| Unity package | 2.3 MB (2,418,176 bytes) |", self.page)
        self.assertIn("| Unreal Engine 5.8, Windows x64 | 17.5 MB (18,350,080 bytes) |", self.page)
        self.assertIn("| Source, for other platforms and engine builds | 1.0 MB (1,048,576 bytes) |", self.page)
        self.assertIn("| Windows x64 | 35.2 MB (36,913,643 bytes) |", self.page)

    def test_artifacts_appear_in_fixed_order(self) -> None:
        positions = [self.page.index(f"### {title} ") for _, title, _, _ in tool.ARTIFACTS]
        self.assertEqual(positions, sorted(positions))

    def test_matches_the_expected_page(self) -> None:
        self.assertEqual(self.page, text(FIXTURES / "releases-feed.md"))


class EarlierLinesTest(unittest.TestCase):
    def feed_with_earlier_line(self) -> dict:
        feed = load("releases-feed.json")
        older = copy.deepcopy(feed["artifacts"]["director"])
        older["version"] = "0.3.2"
        older["released_at"] = "2026-10-20T23:30:00-02:00"
        older["notes_url"] = "https://github.com/Eposyne/how-it-works/releases/tag/director-0.3.2"
        older["files"][0]["name"] = "eposyne-director-0.3.2-windows-x64.zip"
        older["files"][0]["url"] = (
            "https://github.com/Eposyne/how-it-works/releases/download/director-0.3.2/"
            "eposyne-director-0.3.2-windows-x64.zip"
        )
        older["files"][0]["size_bytes"] = 900
        feed["previous"] = [{"line": "0.3", "artifacts": {"director": older}}]
        return feed

    def test_lists_earlier_lines_after_the_current_one(self) -> None:
        page = tool.render(self.feed_with_earlier_line())
        self.assertIn("## Earlier lines\n", page)
        self.assertIn("### Line 0.3\n", page)
        self.assertIn("#### Eposyne Director (local) 0.3.2\n", page)
        self.assertLess(page.index("## Line 0.4"), page.index("## Earlier lines"))
        self.assertLess(page.index("## Earlier lines"), page.index("## How versions work"))

    def test_dates_are_utc_calendar_dates(self) -> None:
        page = tool.render(self.feed_with_earlier_line())
        # 23:30 at -02:00 on 2026-10-20 is 01:30 UTC on 2026-10-21.
        self.assertIn("Released 2026-10-21.", page)

    def test_small_sizes_are_in_bytes(self) -> None:
        page = tool.render(self.feed_with_earlier_line())
        self.assertIn("| Windows x64 | 900 bytes |", page)


class DeterminismTest(unittest.TestCase):
    def test_same_feed_same_page(self) -> None:
        feed = load("releases-feed.json")
        self.assertEqual(tool.render(feed), tool.render(copy.deepcopy(feed)))

    def test_key_order_in_the_feed_does_not_matter(self) -> None:
        feed = load("releases-feed.json")
        reordered = json.loads(json.dumps(feed, sort_keys=True))
        reordered["artifacts"] = dict(reversed(list(reordered["artifacts"].items())))
        self.assertEqual(tool.render(feed), tool.render(reordered))

    def test_page_ends_with_one_new_line_and_has_no_trailing_spaces(self) -> None:
        for name in ("releases-feed.json", "releases-feed-empty.json"):
            page = tool.render(load(name))
            self.assertTrue(page.endswith("\n") and not page.endswith("\n\n"), name)
            self.assertFalse(any(line != line.rstrip() for line in page.splitlines()), name)
            self.assertNotIn("\n\n\n", page, name)

    def test_page_has_no_long_dashes(self) -> None:
        for name in ("releases-feed.json", "releases-feed-empty.json"):
            page = tool.render(load(name))
            for dash in (chr(0x2013), chr(0x2014)):
                self.assertNotIn(dash, page, name)


class RefusalTest(unittest.TestCase):
    def test_wrong_format(self) -> None:
        feed = load("releases-feed-empty.json")
        feed["format"] = "eposyne.releases/v2"
        with self.assertRaises(tool.FeedError):
            tool.render(feed)

    def test_releases_without_a_line(self) -> None:
        feed = load("releases-feed.json")
        feed["line"] = ""
        with self.assertRaises(tool.FeedError):
            tool.render(feed)

    def test_unknown_artifact(self) -> None:
        feed = load("releases-feed.json")
        feed["artifacts"]["godot"] = feed["artifacts"]["unity"]
        with self.assertRaises(tool.FeedError):
            tool.render(feed)

    def test_missing_field(self) -> None:
        feed = load("releases-feed.json")
        del feed["artifacts"]["unity"]["notes_url"]
        with self.assertRaises(tool.FeedError):
            tool.render(feed)

    def test_date_without_zone(self) -> None:
        feed = load("releases-feed.json")
        feed["artifacts"]["unity"]["released_at"] = "2026-11-02T10:00:00"
        with self.assertRaises(tool.FeedError):
            tool.render(feed)


class CommandLineTest(unittest.TestCase):
    def test_write_then_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "releases.md"
            feed = str(FIXTURES / "releases-feed.json")
            self.assertEqual(run("--feed", feed, "--out", str(out))[0], 0)
            self.assertEqual(out.read_bytes(), (FIXTURES / "releases-feed.md").read_bytes().replace(b"\r\n", b"\n"))
            self.assertEqual(run("--feed", feed, "--out", str(out), "--check")[0], 0)

    def test_check_accepts_crlf_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "releases.md"
            page = tool.render(load("releases-feed.json"))
            out.write_bytes(page.replace("\n", "\r\n").encode("utf-8"))
            self.assertEqual(run("--feed", str(FIXTURES / "releases-feed.json"), "--out", str(out), "--check")[0], 0)

    def test_check_fails_on_a_stale_page_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "releases.md"
            stale = tool.render(load("releases-feed-empty.json"))
            out.write_text(stale, encoding="utf-8", newline="\n")
            code, stdout, stderr = run("--feed", str(FIXTURES / "releases-feed.json"), "--out", str(out), "--check")
            self.assertEqual(code, 1)
            self.assertIn("+## Line 0.4", stdout)
            self.assertIn("out of date", stderr)
            self.assertEqual(out.read_text(encoding="utf-8"), stale)

    def test_unreadable_feed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "releases.json"
            bad.write_text("{", encoding="utf-8")
            code, _, stderr = run("--feed", str(bad), "--out", str(Path(tmp) / "releases.md"))
            self.assertEqual(code, 1)
            self.assertIn("not JSON", stderr)


class RepositoryTest(unittest.TestCase):
    def test_committed_page_matches_committed_feed(self) -> None:
        feed = json.loads((ROOT / "releases.json").read_text(encoding="utf-8"))
        self.assertEqual(tool.render(feed), text(ROOT / "releases.md"))


if __name__ == "__main__":
    unittest.main()
