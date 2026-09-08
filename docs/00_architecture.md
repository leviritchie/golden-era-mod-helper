# How an Olden Era mod is put together

**Olden Era** is a Unity IL2CPP game. Gameplay code is native inside `GameAssembly.dll`. Mods (including the example mod **Golden Era**) usually attach with BepInEx 6 IL2CPP, generated interop wrappers, Harmony patches, and JSON in `Core.zip`. This page describes that game-plus-mod shape. It is not a claim that Golden Era *is* the game.

If you treat it as “a folder of JSON to edit,” you will get a faction that exists in data and then fails in the selector, in town, or in combat.

## The three layers

### Core data

`HeroesOldenEra_Data/StreamingAssets/Core.zip` holds `DB/**` and `Lang/**`. The game deserializes many of these files into dictionaries keyed by id. Duplicate ids usually crash hard.

Important members:

- `DB/data.json` — available factions and global lists
- `DB/fractions/*.json` — faction identity, icons, city name, biome. Overlays often use a numbered prefix (`13_homm3_castle.json`). That prefix is packer-owned, not a drop-in filename from this kit.
- `DB/objects_logic/cities/*.json` — city logic, build tree, hire rows, building costs
- `DB/map/objects/4_interactables.json` — towns, dwellings, interactables
- `DB/objects_logic/hires/barracks.json` — external dwelling hire
- `DB/units/units_logics/**` and `DB/units/units_views/**` — combat logic versus presentation/UI
- `DB/heroes/**`, `DB/heroes_specializations/**`, `DB/heroes_abilities/**`
- `DB/fractions_laws/**`
- `DB/buffs/**`
- `Lang/<locale>/texts/*.json`

Hand-editing the installed `Core.zip` as your source of truth is how Steam updates and later generators destroy work. Own files in your repo, then pack them.

### Plugin runtime

A BepInEx plugin starts after Unity starts. Typical startup:

1. Read config.
2. Register Harmony patches that have stable names.
3. Manually bind fragile surfaces by signature.
4. Load plugin-side portraits, icons, bundles.
5. Fail closed if a required surface is missing.

JSON icon keys do not automatically teach serialized Unity UI about plugin PNGs. That is why icon and portrait hooks exist.

Do not scan every IL2CPP type at startup. Broad reflection has crashed launch.

### Direct State

This is an opt-in lane for journaled native writes (for example occupancy/hex stores) when you need rollback semantics. Prefer a native Core verb (`teleport`, a buff, a unit special) when one exists.

CapLog / dual-readback of stores is not user-visible combat.

## What a “working custom faction” actually is

All of these, not one of them:

- Core faction, city, units, heroes, laws, squads, map objects, dwellings, localization
- Native-safe donor shells where the engine requires a known prefab
- Plugin payload: DLL, config, portraits, skill icons, unit bundles
- Runtime hooks for lookups the serialized game does not know
- Matching logic/view arrays
- Unique skill/subskill ids
- A biome pipeline if you are not on a vanilla biome the dictionaries already contain

## Config and feature gates

A hook can be compiled and still be off in config. A DLL can be current while `Core.zip` is stale. Capture the config printed at plugin load and compare it to the deployed file.

## Logs

- `BepInEx/LogOutput.log` — plugin startup, patch registration
- Unity `Player.log` — map load, battle init, native exceptions
- `BepInEx/ErrorLog.log` — process-killing trampoline crashes

Healthy hook registration plus a `Player.log` NRE means the data/native layer failed, not that you need another fallback.

## Related components

- [Core data](01_core_data.md)
- [Plugin runtime](02_plugin_runtime.md)
- [Direct State](03_direct_state.md)
- [Silent miss](16_silent_miss.md)
- [Proof labels](17_proof.md)
