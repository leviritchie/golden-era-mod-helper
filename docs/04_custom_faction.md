# Component: Custom faction

A custom faction is a **bundle of other components**. It is not a single JSON file named `homm3_mytown.json`.

## Intent

Add a playable town identity: name, biome, city, dwellings, units, heroes, laws, map objects, and UI membership.

## Identity block

Minimum identity:

- `factionSid` — example `homm3_castle`
- `citySid` — example `homm3_castle_city`
- display name and description tokens
- `nativeBiome`
- `donorFactionSid` / `donorCitySid` — native shells the engine already knows

Core output paths belong next to identity so packers do not guess:

- faction JSON
- city logic
- laws table
- squad tree
- hero subclasses / specializations
- direct city map object id
- direct dwelling prefix

## Unit lines

Each line needs:

- tier
- `baseSid`
- upgrade SIDs (either `baseSid + _upg` / `_upg_alt`, or explicit `variantSids` when the source uses names like `h3_battle_dwarf` instead of `h3_dwarf_upg`)
- donor unit SID and donor faction (mixed-donor factions must declare this per line)
- display names for base / upgrade / alternate

## Donor collision

Legal: many custom units may clone the same donor.

Illegal: looking up “which custom unit is this donor?” from the donor id alone.

When two custom factions share Human barracks donors, reverse lookup without the live hire payload or saved original SID will show the wrong dwelling.

Do not mutate shared donor `ObjectConfig.id` globally if direct custom rows also exist. Map load then throws duplicate key.

## Registration beyond the faction file

Also required, as separate work:

- `DB/data.json` fractions lists and any arena/draft pools the UI uses
- Localization
- Serialized selector support (plugin) if `SoFractions` does not list you
- City map object, dwelling map objects, hire logic
- Heroes, skills with **unique** subskill ids
- Laws
- Portraits, skill icons, unit presentation
- Town world

The studio faction scaffold writes a checklist. Tick boxes with evidence, not hope.

## Helper widget

Studio → Faction scaffold, or:

```powershell
python cli.py scaffold-faction --short-name example --display-name Example --donor castle
```
