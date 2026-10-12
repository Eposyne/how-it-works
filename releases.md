# Releases

[Back to the overview](README.md)

<!-- Generated from releases.json by tools/render_releases_md.py. Do not edit by hand. -->

**Nothing has been released yet.** This page will list the latest version of each Eposyne
download, with its changelog and the fingerprint (SHA-256) of every file. It is regenerated
from [`releases.json`](releases.json) each time a release is published.

## How versions work

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
