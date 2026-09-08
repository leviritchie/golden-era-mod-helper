# Component: Core.zip data

This component is **data**. It is not Harmony and it is not a Unity scene.

## Intent

Put ids, stats, abilities, buildings, laws, and text where the engine already deserializes them.

## Ownership

Your repo owns source JSON. A packer/overlay writes `Core.zip`. The installed archive is what the game reads.

Do not hand-edit Steam `Core.zip` as the long-term source.

## Logic versus view

Creature rows come in pairs:

- `units_logics` — what the action does (`energyLevel`, `cd`, damage dealer, mechanics)
- `units_views` — how it is shown (name token, icon, animation index, projectile)

If logic has an extra ability or alternative attack and view does not, combat initialization can throw inside native ability setup. The exception may not name your JSON file.

Keep native buckets: `defaultAttacks`, `alternativeAttacks`, `counterAttacks`, `abilities`.

## Localization

Visible strings live under `Lang/<locale>/texts/`. Member names matter. A file named like `fractionLaws.json` can be ignored while `factionLaws.json` is read. Inspect the live archive instead of assuming.

Player-facing rows must describe shipped behavior. Keep implementation debt out of these files.

## Resources

Olden Era resource ids are not always HoMM3 names. Example: `gems` rather than `gemstones`. Copy ids from live Core examples.

## Duplicate keys

Native dictionaries crash on duplicate ids. Common causes:

- A backup `Core.zip.*` sitting where the loader still scans zip files
- Direct custom map-object rows plus mutated donor `ObjectConfig.id` values equal to those custom ids
- Shallow-cloned donor `subSkills` reused across ranks

## Custom biome

A faction `biome` field is not enough. Coordinated coverage includes map tiles, waters, `waterForBiome`, generator environment, `DB/biomes_info.json`, arena views, obstruction models, and biome-keyed sounds. Keep biome work generator-owned.

## What this component cannot do

- Make the faction appear in a serialized Unity selector that has a hard-coded list
- Bind a plugin PNG to a JSON icon key
- Replace a donor town visual
- Prove combat feel

Those are plugin, town, and proof components.

## Helper widget

`python cli.py scaffold-faction` writes a sandbox identity file that lists the Core members you will eventually pack. It does not pack them.
