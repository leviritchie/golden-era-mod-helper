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

## Donor shells are not a HoMM3-name lookup

Do not guess “Tower uses Dungeon” or “Stronghold uses Orcs” from Heroes 3 town names. In the Golden Era example files:

| Example key | Vanilla family | City shell | Biome |
| --- | --- | --- | --- |
| castle | humans | human_city | Valleys |
| rampart | nature | nature_city | Hills |
| tower | humans | human_city | Tundra |
| inferno | demons | demon_city | Molten |
| necropolis | undead | undead_city | Curselands |
| dungeon | dungeon | dungeon_city | Burrow |
| stronghold | dungeon | dungeon_city | Wasteland |
| fortress | nature | nature_city | Swamp |
| conflux | nature | nature_city | Greenlands |
| cove | humans | human_city | Tropical |
| factory | humans | human_city | Foundry |
| bulwark | nature | nature_city | Permafrost |

Copy `donorFactionSid` and `nativeBiome` from a live Core faction row if you are not cloning that example. A biome string the terrain dictionaries do not already know is a full terrain pipeline.

The scaffold’s sample creature line uses a placeholder donor unit from the same vanilla family. Golden Era mixed donors per line. Replace it.

## Core output paths

Core output paths belong next to identity so packers do not guess. Treat them as a member list, not a drop-in filename. Live overlays often prefix faction files (`DB/fractions/13_homm3_castle.json`). The packer you own chooses the number.

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
- Serialized selector support (plugin) if the baked faction-selector asset does not list you (on one Golden Era pin the type was `SoFractions`; re-pin)
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
