# Eposyne Director

Director is a runtime AI game master, in beta. While the game runs, the game asks Director
what should happen next. Director proposes changes to the game's state, each with a short
reason, and only within the limits the game declared. The game decides what to apply.

[Back to the overview](README.md)

## Today

### Where it runs

Today Director is a **hosted beta**: one service that Eposyne runs, reached over the network
for every decision, which calls cloud AI models. It is for building and testing your game. A
shipped game cannot use it yet.

Director is built to also run on the player's device through a native SDK. That SDK is not
yet available (see [In development](#in-development)).

### One decision, step by step

```mermaid
sequenceDiagram
    participant Game as Your game (engine plugin)
    participant Director as Eposyne Director
    participant Model as AI model
    Game->>Director: The situation, the current state,<br/>and which values may change, within which limits
    Director->>Director: Check the account, its modules, and its spending limit
    Director->>Model: Ask for a proposal
    Model-->>Director: Proposed changes
    Director->>Director: Drop every change that is not allowed<br/>or falls outside its limits
    Director-->>Game: The remaining changes, each with a reason
    Game->>Game: Check each change again against its own declarations
    Game->>Game: Apply what is allowed, refuse the rest, keep a record
```

What the game sends has three parts:

- **The situation**, in plain language: what is happening and what is being decided.
- **The current state**: the values that matter right now, such as a character's mood, a
  faction's standing, or a line of dialogue.
- **What may change**: which of those values Director may change, each with its allowed
  values or its range. A value can also be marked as free text, for dialogue.

Two layers protect the game:

1. **Director's own enforcement.** The AI's answer is treated as untrusted. A fixed set of
   rules, not AI, drops any change to a value that may not change, and any value outside its
   allowed values or range. The rest of the answer still comes back.
2. **The engine's check.** The plugin checks every change again against what the game
   declared, applies only what is allowed, and records what it applied and what it refused.

Director proposes; it never executes anything in your game.

```mermaid
flowchart LR
    proposal["AI proposal"] --> rules{"Allowed to change?<br/>Within its limits?"}
    rules -- "no" --> dropped["Dropped"]
    rules -- "yes" --> returned["Returned to the game,<br/>with a reason"]
    returned --> engine{"Engine check"}
    engine -- "allowed" --> applied["Applied and recorded"]
    engine -- "not allowed" --> refused["Refused and recorded"]
```

### Signing in and limits

- **Account.** Developers sign in with their Eposyne account through the browser, from the
  engine plugin or from Director's web console. Studios can also use a studio key.
- **Isolation.** Each account or studio has its own data and its own limits.
- **Spending limits.** Usage is metered, and every account has a spending limit.
- **Models.** You pick from the models the hosted Director offers. Bringing your own model,
  or a local model, is not available.

### Engines

- **Unity and Unreal** connect through the Eposyne plugins (see
  [the engine plugins](engine-plugins.md)).
- **Any other engine** can call Director's HTTP interface directly. There is no Godot plugin.

### The console

Director has a web console where a signed-in developer sees their usage and spending, which
modules are switched on, and which models they may use. A playground lets you send a test
decision and read the result in plain words.

### What Director does not do

- It does not create new values: it only changes the values the game declared as changeable.
- It does not check types beyond allowed values and ranges.
- It does not read Architect worlds. Architect content reaches the game through the plugin's
  import, and the game sends Director what a decision needs.
- It does not remember on its own. Today the game passes what happened as part of the state
  it sends.

## In development

- **On-device.** A native SDK that runs Director on the player's device: no network calls
  during play, no player data leaving the game, and no per-token cloud bill at play time.
  Not yet available.
- **Story arcs.** An optional module for plot progression: it follows what happens in the
  game and gives Director a sense of where the story is going, including events that start
  without the player asking.
- **NPC memory.** An optional module that lets characters remember what they saw and heard,
  across scenes and sessions.
- **The event stream.** The game reports what happens as it happens, so the story-arc and
  memory modules can follow along.
- **Runtime creation.** Creating new characters, factions, or quests while the game runs.
- **Shipped games.** A way for a released game, and its players, to reach Director.

The story-arc and memory modules already exist in the service, switched off by default; the
engine plugins do not feed them yet.
