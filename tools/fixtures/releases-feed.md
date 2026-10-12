# Releases

[Back to the overview](README.md)

<!-- Generated from releases.json by tools/render_releases_md.py. Do not edit by hand. -->

This page lists the latest version of each Eposyne download, with its release notes and
the fingerprint (SHA-256) of every file. It is regenerated from
[`releases.json`](releases.json) each time a release is published. Compare a download with
its SHA-256 before installing it.

## Line 0.4

### Eposyne for Unity 0.4.0

Released 2026-11-02. [Release notes](https://github.com/Eposyne/how-it-works/releases/tag/unity-0.4.0). Verified on Unity 6000.3. [Install Eposyne for Unity](install-unity.md).

| File | For | Size | SHA-256 |
| --- | --- | --- | --- |
| [`eposyne-unity-0.4.0.unitypackage`](https://github.com/Eposyne/how-it-works/releases/download/unity-0.4.0/eposyne-unity-0.4.0.unitypackage) | Unity package | 2.3 MB (2,418,176 bytes) | `1f0e3dad99908345f7439f8ffabdffc4c1d1a1d2b6f9c7e6d5c4b3a291807f6e` |

### Eposyne for Unreal 0.4.0

Released 2026-11-02. [Release notes](https://github.com/Eposyne/how-it-works/releases/tag/unreal-0.4.0). [Install Eposyne for Unreal](install-unreal.md).

| File | For | Size | SHA-256 |
| --- | --- | --- | --- |
| [`eposyne-unreal-0.4.0-ue5.8-win64.zip`](https://github.com/Eposyne/how-it-works/releases/download/unreal-0.4.0/eposyne-unreal-0.4.0-ue5.8-win64.zip) | Unreal Engine 5.8, Windows x64 | 17.5 MB (18,350,080 bytes) | `9b74c9897bac770ffc029102a200c5de2e1f0a2b3c4d5e6f708192a3b4c5d6e7` |
| [`eposyne-unreal-0.4.0-source.zip`](https://github.com/Eposyne/how-it-works/releases/download/unreal-0.4.0/eposyne-unreal-0.4.0-source.zip) | Source, for other platforms and engine builds | 1.0 MB (1,048,576 bytes) | `3c59dc048e8850243be8079a5c74d079a1b2c3d4e5f60718293a4b5c6d7e8f90` |

### Eposyne Director (local) 0.4.0

Released 2026-11-02. [Release notes](https://github.com/Eposyne/how-it-works/releases/tag/director-0.4.0). [Run Director locally](install-director-local.md).

| File | For | Size | SHA-256 |
| --- | --- | --- | --- |
| [`eposyne-director-0.4.0-windows-x64.zip`](https://github.com/Eposyne/how-it-works/releases/download/director-0.4.0/eposyne-director-0.4.0-windows-x64.zip) | Windows x64 | 35.2 MB (36,913,643 bytes) | `adb60241198ebf143aac645b40ad7d7cccc39104bc63ddaca2225e9c4951544a` |

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
