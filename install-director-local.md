# Run Director locally

[Back to the overview](README.md) | [Releases](releases.md)

**Status: in development.** The hosted Director is the way to use Director today. Running it on
your own machine works in development builds of the plugins and has no public release yet.

## What it is

The same Director service that runs hosted, packaged as one program that runs on your machine
and listens only to your machine. Your game project talks to it instead of the hosted
Director when you choose so; switching is always your action, and if the local Director is
not running, the plugin tells you instead of quietly using the hosted one.

## How you get it

You do not download it by hand. In the plugin's Director area, choose `Run Director locally`.
The plugin reads the signed list of releases, downloads the Director for your system, checks
its fingerprint (SHA-256), and starts it. Windows comes first; other systems follow.

## Models

The local Director needs a model to think with:

- **Ollama.** If Ollama runs on your machine, the plugin lists its models and can download a
  model for you, after showing where it comes from, its license, its size, and whether your
  machine can run it. The plugin never installs, starts, or removes Ollama itself.
- **Any compatible server.** You can point the plugin at another local or remote server that
  speaks the common OpenAI-style API.

## Your account

You sign in once while online. After that, the local Director keeps working offline for a
limited time, and the plugin renews its access the next time you are online.
