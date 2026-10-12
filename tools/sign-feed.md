# Signing the release feed

These are the owner's steps for signing `releases.json`. They assume you have never used
minisign before.

## Why the feed is signed

`releases.json` tells the engine plugins which Director program to download and which
SHA-256 it must have. Anyone who could change that file could make a plugin download
something else. So the feed carries a signature, `releases.json.minisig`, made with a key
only you hold. Each plugin has the matching public key built in and refuses a feed whose
signature does not check out. The plugins only trust what you sign.

minisign is a small, free program that makes and checks such signatures. A signature
covers the exact bytes of the file: change one character after signing, even a line
ending, and the signature no longer matches.

## What you need

- minisign, from <https://jedisct1.github.io/minisign/>. On Windows, take the zip for
  your system from <https://github.com/jedisct1/minisign/releases>, or use a package
  manager such as Scoop (`scoop install minisign`). On macOS, `brew install minisign`.
  Check it works with `minisign -v`, which prints its version.
- A clone of this repository, and the GitHub command line (`gh`) to check out pull
  requests. Python 3 to regenerate `releases.md`.
- A place for the secret key that is not on a machine you use every day, such as a USB
  drive you keep in a drawer.

## Once: create the key pair

Do this one time, ever. The same key signs every release.

1. Plug in the drive that will hold the secret key. Below it is `E:`; use your own.
2. In a terminal, run:

   ```
   minisign -G -p eposyne-feed.pub -s E:\eposyne-feed.key
   ```

3. minisign asks for a password twice. Choose a long one and store it in your password
   manager. It protects the secret key if the drive is ever lost.
4. You now have two files:
   - `E:\eposyne-feed.key`, the **secret key**. It never goes into any repository, chat,
     email, or cloud folder. Keep the drive offline and plug it in only to sign.
     Make a second copy on another drive and keep that one somewhere else.
   - `eposyne-feed.pub`, the **public key**. It is not secret. Open it in a text editor:
     the second line, starting with `RW`, is the public key itself.
5. Give the public key (the whole `eposyne-feed.pub` file, or just its `RW` line) to the
   maintainers of Eposyne for Unity, Eposyne for Unreal, and Director. They build it into
   the plugins. Keep a copy of `eposyne-feed.pub` beside the secret key as well.

If the secret key is ever lost or seen by someone else, the plugins have to ship with a
new public key, and plugins already installed can no longer check the feed. Treat it
like the key to the building.

## Every release: sign the feed pull request

Each release workflow opens a pull request on this repository that changes
`releases.json` and a changelog. Before you merge it:

1. Check out the pull request's branch, with its number from GitHub:

   ```
   gh pr checkout <number>
   ```

2. Read the changes to `releases.json`: the version, the files, and their SHA-256 should
   match the draft release the workflow made.
3. Regenerate the releases page and look at it:

   ```
   python tools/render_releases_md.py
   ```

4. Plug in the drive and sign the feed:

   ```
   minisign -Sm releases.json -s E:\eposyne-feed.key
   ```

   minisign asks for the key's password, then writes `releases.json.minisig` beside
   `releases.json`. Unplug the drive.
5. Check the signature with the public key, given either as its `RW` line or as the file:

   ```
   minisign -Vm releases.json -P <public key>
   minisign -Vm releases.json -p eposyne-feed.pub
   ```

   It prints `Signature and comment signature verified`. Anything else means the
   signature does not match: sign again.
6. Make sure only the expected files changed (`git status` lists `releases.md` and
   `releases.json.minisig`, and never `releases.json`), then commit and push:

   ```
   git add releases.md releases.json.minisig
   git commit -m "docs: sign the feed for <artifact> <version>"
   git push
   ```

7. Wait for the "Releases page" check on the pull request to pass. It checks the feed
   against its schema, that the signature is there, and that `releases.md` matches the
   feed. Then merge the pull request and publish the draft release in the same sitting,
   so the feed and the download go live together.

## When something changed after you signed

The signature covers `releases.json` as it was when you signed. If the file changes
afterwards, for example because another feed pull request was merged first and this one
had to be rebuilt, sign it again from step 3. The check on the pull request does not
hold the public key, so it cannot tell a stale signature from a good one; step 5 can.

`releases.json` and `releases.json.minisig` are marked in `.gitattributes` so Git never
changes their line endings on Windows, which would break the signature. Do not open and
save `releases.json` in an editor after signing.

## An empty feed

Before the first release the feed lists nothing, and a signature is optional.
