# Component: Plugin runtime and Harmony

This component is **runtime**. Use it when Core data cannot express the design, or when serialized Unity assets do not know your ids.

## Intent

Load after Unity, patch exact methods, supply missing sprites, replace visuals after native construction, and fail closed when symbols moved.

## Startup shape

1. Read config. Absent keys keep defaults. Present keys override.
2. Register stable Harmony patches.
3. Bind fragile patches by parameter shape, not by a nickname from last month.
4. Load plugin-side files (portraits, icons, bundles).
5. Log exact success (`REGISTERED_...`) or skip the feature.

A compiled hook that is config-gated off is not a runtime feature.

## Symbol registry

Create one `GameSymbols` class (or equivalent). Feature code reads `GameSymbols.SelectedUnitHud.ControlsHotkey`, not a string literal in a HUD file.

After a Steam hotfix:

- Interop DLLs under `BepInEx/interop` can be stale even if you rebuilt your plugin.
- Confirm against current `GameAssembly.dll` and `global-metadata.dat`.

Dump-era names are leads. They are not pins.

## Patching rules

- Match exact parameter types when the same method name exists several times.
- Log one capped “hook fired” line on important surfaces.
- Do not postfix every `Image.sprite` setter.
- Do not intercept every generic button as Back/Close.
- Do not call `Camera.allCameras` from fragile UI postfixes.
- Prefer typed components over `GetComponent(string)`.

## Identity in hooks

Before any dictionary lookup from a Harmony argument:

1. Live argument type equals map key type, or you have an explicit bridge.
2. Then key Il2Cpp objects by native pointer. Managed `GetHashCode` on separately marshaled proxies misses.

See [Silent miss](16_silent_miss.md).

## Pooled UI

Unity UI rows are reused. If you set `overrideSprite`, clear it when the row binds a non-custom id. If you add an overlay object, name it and destroy it on rebind. Do not mutate a native `RawImage` that later vanilla screens reuse.

## Visual replacement pattern

Reliable custom visuals:

1. Let native code instantiate a donor shell it understands.
2. Hide or redirect that shell.
3. Parent your quad/mesh/prefab.
4. Copy only safe renderer flags.
5. Bind textures into the shader slots the game samples (`Hex/Lit` for world quads, not a UI sprite shader).

## What this component cannot do

- Invent stats that Core never reads
- Replace a missing Core row with a guess
- Prove user-visible gameplay by printing “planned”

## Helper widget

The [hook catalog](11_hooks.md) and studio Hook catalog list families. Re-pin names in your own registry; do not paste Golden Era obfuscated strings as if they were an API.
