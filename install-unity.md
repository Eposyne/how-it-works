# Install Eposyne for Unity

[Back to the overview](README.md) | [Releases](releases.md)

**Status: not released yet.** No version of Eposyne for Unity can be downloaded today. This
page describes how installing works once the first release is published; the download link
will then appear on the [releases page](releases.md).

## What you download

One file per release: `eposyne-unity-<version>.unitypackage`. It holds only the plugin, no
sample scenes or test assets, and its SHA-256 is listed beside the download so you can check
the file.

## Which Unity versions

Unity 6 (6000.x). Each release names the exact versions it was checked on. Older Unity
versions are not supported.

## Install

1. Open your project in Unity 6.
2. Drag the `.unitypackage` into the Project window, or use Assets > Import Package > Custom
   Package, and import everything it lists.
3. Open Window > Eposyne > Eposyne.
4. In Settings, choose Sign in. Your browser opens with a code filled in; approve it with your
   Eposyne account. Nothing else needs a password in the editor.
5. Ask Director something from the Director tab to check the connection.

## Updating

Import the newer `.unitypackage` over the old one. The plugin shows its own version and the
version of the Director it talks to; when they are on different lines, it tells you which one
to update.

## Running Director on your own machine

Optional. See [Run Director locally](install-director-local.md). You do this from inside the
plugin, not by downloading anything yourself.
