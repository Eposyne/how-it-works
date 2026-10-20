# Install Eposyne for Unreal

[Back to the overview](README.md) | [Releases](releases.md)

**Status: not released yet.** No version of Eposyne for Unreal can be downloaded today. This
page describes how installing works once the first release is published; the download links
will then appear on the [releases page](releases.md).

## What you download

Each release offers:

- **A prebuilt plugin per engine version**, `eposyne-unreal-<version>-ue<engine>-win64.zip`,
  for Unreal Engine 5.0 through 5.8 on Windows. Pick the one matching your engine. It opens
  without compiling.
- **The source**, `eposyne-unreal-<version>-source.zip`, for other platforms and custom engine
  builds. Building from source needs Visual Studio 2022 on Windows.

Every file has its SHA-256 listed beside the download.

## Install (prebuilt)

1. Close the Unreal editor.
2. Unzip into your project so the folder `Plugins/Eposyne` sits next to your `.uproject`.
3. Open the project. Under Edit > Plugins, "Eposyne for Unreal" is listed and enabled.
4. Under Edit > Project Settings, the Eposyne section holds the plugin's settings.
5. Sign in from the plugin's editor window: your browser opens with a code filled in; approve
   it with your Eposyne account.

## Install (source)

Unzip into `Plugins/` as above, then open the project and let the editor build the plugin, or
build your editor target in Visual Studio 2022.

## Updating

Replace the `Plugins/Eposyne` folder with the newer one while the editor is closed. The plugin
shows its version beside the Director's and says which side to update when their lines differ.
