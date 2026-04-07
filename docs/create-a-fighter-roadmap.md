# Create-a-Fighter Roadmap

## Current Reality

The current `create` flow is strong as a submission and identity system, but it is not yet a true ground-up fighter builder.

Today the pipeline works like this:

1. The web form captures a fighter spec with identity, appearance, stats, AI profile, moveset labels, and league settings.
2. The submission is stored in Supabase and imported locally.
3. `scripts/generate_fighter.py` derives metadata and runtime settings.
4. `scripts/publish_fighter.py` copies an existing folder from `chars/`, renames the `.def`, and patches name/stat values.

That means the created fighter is still fundamentally a template or roster clone.

## North Star

The long-term goal is a creator-driven fighter system where viewers feel like they are building their own competitor, not reskinning someone else's.

The player fantasy should be:

- "I designed this wrestler from scratch."
- "This fighter behaves the way I intended."
- "I want to watch them rise, win belts, lose belts, evolve, and build history."

For the stream, this is the retention loop:

- Create a fighter
- Submit them to the league
- Watch their debut
- Follow their career, rivalries, teams, title shots, and championships
- Return to create another fighter or refine an existing one

## Product Principle

We should separate fighter creation into four layers instead of treating "the character" as one monolithic asset:

1. Identity layer
2. Visual layer
3. Combat layer
4. League/story layer

The system becomes scalable when those layers are modular and composable.

## Target Architecture

### 1. Identity Layer

This is already mostly present in the current form.

Owns:

- name
- nickname
- announcer call
- hometown
- alignment
- short bio
- creator attribution

This layer gives emotional ownership.

### 2. Visual Layer

This is the first major gap between current state and the target.

A true custom fighter needs to be assembled from interchangeable visual parts rather than copied from a single existing roster character.

Recommended model:

- body base
- head or mask base
- hair style
- facial hair
- torso gear
- lower gear
- boots
- gloves
- accessory
- color palette
- portrait style
- aura or entrance effect

Implementation direction:

- Build a curated visual parts library.
- Generate sprite sheets, portraits, and palettes from those parts.
- Publish the final art into a runtime fighter package.

This can begin in a constrained way. It does not need infinite freedom on day one.

## 3. Combat Layer

This is the most important system for making fighters feel unique in motion.

Instead of "pick a base character," the fighter should be built from modular combat packages:

- locomotion package
- normal attack package
- throw package
- anti-air package
- special move package
- super move package
- intro package
- taunt package
- victory package

Each package should expose compatibility tags so we know what can combine safely.

Example:

- a heavyweight locomotion set should not be paired with tiny airborne hitboxes
- a grappler throw kit may require a compatible body skeleton
- a stance package may restrict available idle and walk animations

The created fighter then becomes:

- a skeleton/body class
- a selected animation pack
- a selected move package set
- generated stats
- generated AI tuning

This is still templated internally, but it becomes modular templating rather than "clone one full existing fighter."

That is the right bridge to a real create-a-fighter feature.

## 4. League and Story Layer

This is where your project has a major advantage.

Most fan-made character creators stop at cosmetics. Your stream can turn created fighters into ongoing story objects.

Each fighter should eventually accumulate:

- debut date
- match history
- win/loss record
- streaks
- championship history
- tournament history
- tag partners
- rivals
- crowd identity
- creator identity

This turns creation into a recurring entertainment loop instead of a one-time novelty.

## Why The Current System Still Matters

The current clone/template system is not wasted work. It is the correct first generation because it already gives us:

- a submission schema
- stat budgeting
- AI tuning inputs
- publishing workflow
- roster integration
- debut queue support

We should preserve that pipeline and replace the runtime generation strategy underneath it.

## Recommended Evolution Path

### Phase 1: Modular Fighter Spec

Goal: stop thinking in terms of "base fighter clone" and start thinking in terms of "assembled fighter recipe."

Add explicit fields for:

- body rig or body class
- animation set
- strike package
- grapple package
- special package
- super package
- voice package
- portrait package
- palette package

In this phase, the system may still use internal templates, but users should no longer be choosing a full existing roster fighter as the source.

Success condition:

- a submission can be described as a recipe made of parts
- the publish step consumes parts, not a single parent fighter

### Phase 2: Curated Assembly Pipeline

Goal: generate a runtime MUGEN fighter from compatible modules.

Build:

- a module registry
- compatibility rules
- assembly script that composes files into a final fighter folder
- validation that rejects invalid combinations before publish

Success condition:

- two created fighters can share some modules but still feel materially different
- no published fighter depends on a visible roster clone choice

### Phase 3: Visual Creator Upgrade

Goal: make the fighter feel authored by the player visually.

Build:

- curated appearance part sets
- portrait generation flow
- palette previews
- stronger "this is mine" visual customization

Success condition:

- a viewer can recognize their fighter on the stream as their own creation

### Phase 4: Career Hooks

Goal: maximize retention.

Build:

- creator profile pages
- fighter profile pages
- rivalries and tag history
- title shot history
- tournament consequences
- "watch my fighter" discovery and alerts

Success condition:

- viewers return for outcomes, not just creation

## First Build Slice

The highest-leverage next implementation is not full art generation. It is replacing `base_fighter` with a modular combat assembly model.

Recommended first slice:

1. Introduce a `fighter_modules` or `assembly` section in the fighter schema.
2. Define a small curated set of internal modules:
   - 3 body classes
   - 4 locomotion packages
   - 4 strike packages
   - 3 grapple packages
   - 4 special packages
   - 3 intro/victory packages
3. Add compatibility metadata in config.
4. Change the generator/publisher to build from those modules.
5. Keep appearance customization simple at first.

This gets you out of clone-based design without requiring a full art pipeline immediately.

## Design Standard

A created fighter should pass three tests:

1. Ownership test
   The viewer feels this fighter is theirs.

2. Readability test
   The fighter has a clear combat identity on stream.

3. Replay test
   Watching their long-term journey is compelling enough to bring the viewer back.

## Immediate Repo Direction

The next coding task should be:

- refactor the fighter submission format so it supports modular assembly
- keep current submissions working during the transition
- update generation/publish scripts to resolve modules from config instead of copying a chosen roster fighter

That gives us the right technical foundation for the bigger visual creator later.
