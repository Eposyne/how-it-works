#!/usr/bin/env python3
"""Regenerate releases.md from releases.json.

    python tools/render_releases_md.py            write releases.md
    python tools/render_releases_md.py --check    exit 1 when releases.md is not what the feed gives

releases.json is the release feed (format eposyne.releases/v1, written only by the
release workflows of the Unity plugin, the Unreal plugin, and Director). releases.md
is the page people read. This script is its only author: the same feed always gives
the same page, byte for byte, so a pull request that changes the feed also carries
the regenerated page, and the releases-page workflow checks that it does.

Standard library only. The feed is validated against the schema by the workflow, not
here; this script reports a feed it cannot read, and otherwise trusts the schema.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEED = ROOT / "releases.json"
PAGE = ROOT / "releases.md"

FEED_FORMAT = "eposyne.releases/v1"

# Artifacts in page order, with their heading and install page.
ARTIFACTS = (
    ("unity", "Eposyne for Unity", "install-unity.md", "Install Eposyne for Unity"),
    ("unreal", "Eposyne for Unreal", "install-unreal.md", "Install Eposyne for Unreal"),
    ("director", "Eposyne Director (local)", "install-director-local.md", "Run Director locally"),
)

OS_NAMES = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}

HEADER = """# Releases

[Back to the overview](README.md)

<!-- Generated from releases.json by tools/render_releases_md.py. Do not edit by hand. -->
"""

NOTHING_RELEASED = """**Nothing has been released yet.** This page will list the latest version of each Eposyne
download, with its changelog and the fingerprint (SHA-256) of every file. It is regenerated
from [`releases.json`](releases.json) each time a release is published.
"""

RELEASED = """This page lists the latest version of each Eposyne download, with its release notes and
the fingerprint (SHA-256) of every file. It is regenerated from
[`releases.json`](releases.json) each time a release is published. Compare a download with
its SHA-256 before installing it.
"""

FOOTER = """## How versions work

Every download has a version `MAJOR.MINOR.PATCH`, such as `0.4.0`.

- The first two numbers, the **line**, are shared by Eposyne for Unity, Eposyne for Unreal,
  and Director. Products on the same line work together.
- The last number is each product's own fixes. A fix never changes how the products talk to
  each other.
- The hosted Director accepts the current line and the one before it.

## Where releases live

Releases are published on this repository's releases page, one per product version
(`unity-<version>`, `unreal-<version>`, `director-<version>`). Changelogs are copied into
[changelogs](changelogs/). The plugins and the Director website read the same list, so a
download link never points anywhere else.
"""


class FeedError(Exception):
    """The feed cannot be rendered; the message says why."""


# ---------------------------------------------------------------------------
# Formatting helpers


def human_size(size: int) -> str:
    """Binary units, one decimal, as in the release notes of the release workflows."""
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} bytes"


def size_cell(size: int) -> str:
    exact = f"{size:,} bytes"
    readable = human_size(size)
    return exact if readable == exact else f"{readable} ({exact})"


def release_date(stamp: str) -> str:
    """The UTC calendar date of an RFC 3339 date-time, as YYYY-MM-DD."""
    text = stamp[:-1] + "+00:00" if stamp.endswith(("Z", "z")) else stamp
    try:
        moment = _dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise FeedError(f"released_at {stamp!r} is not a date-time") from exc
    if moment.tzinfo is None:
        raise FeedError(f"released_at {stamp!r} has no time zone")
    return moment.astimezone(_dt.timezone.utc).strftime("%Y-%m-%d")


def cell(text: str) -> str:
    """Text safe inside a table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(text: str) -> str:
    """An inline code span that survives backticks in the text."""
    text = str(text)
    fence = "`"
    while fence in text:
        fence += "`"
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def link(label: str, url: str) -> str:
    url = str(url)
    target = f"<{url}>" if any(c in url for c in " ()<>") else url
    return f"[{label}]({target})"


def file_label(entry: dict) -> str:
    kind = entry.get("kind")
    if kind == "unitypackage":
        return "Unity package"
    if kind == "prebuilt":
        return f"Unreal Engine {entry['engine']}, {OS_NAMES.get(entry['os'], entry['os'])} {entry['arch']}"
    if kind == "source":
        return "Source, for other platforms and engine builds"
    if kind == "executable":
        return f"{OS_NAMES.get(entry['os'], entry['os'])} {entry['arch']}"
    return str(kind)


# ---------------------------------------------------------------------------
# Rendering


def render_artifact(artifact: str, entry: dict, heading: str) -> list[str]:
    title, install_page, install_label = next((t, p, l) for a, t, p, l in ARTIFACTS if a == artifact)
    out = [f"{heading} {title} {entry['version']}", ""]
    facts = [
        f"Released {release_date(entry['released_at'])}.",
        link("Release notes", entry["notes_url"]) + ".",
    ]
    if artifact == "unity":
        facts.append(f"Verified on Unity {', '.join(entry['unity_versions'])}.")
    facts.append(link(install_label, install_page) + ".")
    out += [" ".join(facts), ""]
    out += ["| File | For | Size | SHA-256 |", "| --- | --- | --- | --- |"]
    for item in entry["files"]:
        name = link(code(cell(item["name"])), item["url"])
        out.append(
            f"| {name} | {cell(file_label(item))} | {size_cell(item['size_bytes'])} | {code(item['sha256'])} |"
        )
    out.append("")
    return out


def render_artifact_set(artifacts: dict, heading: str) -> list[str]:
    known = {a for a, *_ in ARTIFACTS}
    unknown = sorted(set(artifacts) - known)
    if unknown:
        raise FeedError(f"unknown artifacts {unknown}")
    out: list[str] = []
    for artifact, *_ in ARTIFACTS:
        if artifact in artifacts:
            out += render_artifact(artifact, artifacts[artifact], heading)
    return out


def render(feed: dict) -> str:
    """The text of releases.md for this feed. Pure: same feed, same text."""
    if not isinstance(feed, dict):
        raise FeedError("the feed is not a JSON object")
    if feed.get("format") != FEED_FORMAT:
        raise FeedError(f"format is {feed.get('format')!r}, expected {FEED_FORMAT!r}")
    try:
        line = feed["line"]
        artifacts = feed["artifacts"]
        previous = feed["previous"]
    except KeyError as exc:
        raise FeedError(f"the feed has no {exc.args[0]!r}") from exc

    parts = [HEADER]
    if not line and not artifacts and not previous:
        parts.append(NOTHING_RELEASED)
    elif not line:
        raise FeedError("line is empty while releases are listed")
    else:
        body = [RELEASED.rstrip("\n"), "", f"## Line {line}", ""]
        try:
            body += render_artifact_set(artifacts, "###")
            if previous:
                body += [
                    "## Earlier lines",
                    "",
                    "Still listed so that a plugin on an earlier line finds the Director of its own line.",
                    "",
                ]
                for item in previous:
                    body += [f"### Line {item['line']}", ""]
                    body += render_artifact_set(item["artifacts"], "####")
        except KeyError as exc:
            raise FeedError(f"a release entry has no {exc.args[0]!r}") from exc
        parts.append("\n".join(body))
    parts.append(FOOTER)
    return "\n".join(part.rstrip("\n") + "\n" for part in parts).rstrip("\n") + "\n"


def load_feed(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FeedError(f"cannot read {path}: {exc}") from exc
    except ValueError as exc:
        raise FeedError(f"{path} is not JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Command line


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate releases.md from releases.json.")
    parser.add_argument("--feed", type=Path, default=FEED, help="the feed to read (default: releases.json)")
    parser.add_argument("--out", type=Path, default=PAGE, help="the page to write (default: releases.md)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 and show the difference when the page is not what the feed gives",
    )
    args = parser.parse_args(argv)

    try:
        text = render(load_feed(args.feed))
    except FeedError as exc:
        print(f"error: {args.feed}: {exc}", file=sys.stderr)
        return 1

    if args.check:
        try:
            # A Windows checkout may have turned the page's line endings into CRLF.
            current = args.out.read_text(encoding="utf-8").replace("\r\n", "\n")
        except OSError as exc:
            print(f"error: cannot read {args.out}: {exc}", file=sys.stderr)
            return 1
        if current == text:
            print(f"{args.out} matches {args.feed}.")
            return 0
        sys.stdout.writelines(
            difflib.unified_diff(
                current.splitlines(keepends=True),
                text.splitlines(keepends=True),
                fromfile=f"{args.out} (committed)",
                tofile=f"{args.out} (from {args.feed})",
            )
        )
        print(
            f"error: {args.out} is out of date; run python tools/render_releases_md.py and commit the result.",
            file=sys.stderr,
        )
        return 1

    with args.out.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    print(f"Wrote {args.out} from {args.feed}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
