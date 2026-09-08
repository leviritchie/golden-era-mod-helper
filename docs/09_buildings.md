# Component: Custom buildings

This component is **city-logic rows and their bonuses**. Town presentation is [the town scene](10_town_scene.md). External map dwellings are part of this component plus map-object hooks.

## Intent

Give the faction a build tree the native city UI already understands.

Olden Era does not expect you to invent `MyCoolGuildHall` as a new engine type. You occupy native SIDs:

| Native SID | Vanilla name / role | Common port rename |
| --- | --- | --- |
| `Build_Main` | Village Hall → Capitol | |
| `Build_Wall` | Fort → Castle | |
| `Build_Magic_Guild` | Mage Guild levels | |
| `Build_Tavern` | Tavern | |
| `Build_Market` | Marketplace | |
| `Build_Treasury` | Treasury (gold / day) | Blacksmith / war machine |
| `Build_Artifact_Market` | Artifact merchants | |
| `Build_Resource_Depot` | Resource silo | |
| `Build_Bank` / `Build_Mother_Nature` / `Build_Mycelium_Roots` / … | Vanilla special / visitor / horde slots | HoMM3-style unique buildings |
| `Build_Spring_of_Life` / `Build_Golden_Calf` | Grail-style | |
| `Build_Tier_1` … `Build_Tier_7` | Dwellings | |

You change display names, costs, prerequisites, hire payloads, and `bonuses`. You keep the SID the native `BhBuilding` graph already uses. A HoMM3-style Blacksmith is still `Build_Treasury`.

## Bonuses versus visuals versus clicks

- **Bonuses** live on the city-logic row. If the native bonus primitive can say “+gold” or “+growth”, use it.
- **Art** is painted onto the native slot in the owned city world.
- **Clicks** stay on native `BhBuilding`. Do not add a RawImage click relay as the product path.

Which city-logic **array** holds a building matters. Example: a mess-hall-style bonus must not stay on `artifactChangers` if native code only applies bank-style bonuses from `cityBonusBanks`. Put the row in the array that matches the mechanic.

## External dwellings

A town dwelling upgrade is not the adventure-map dwelling.

Adventure-map dwellings need all of:

- direct map-object row
- hire logic row (`barracks.json`)
- billboard art
- localization that names the **custom** creature, not the donor

Tooltip text that still reads the donor `sidConfig` while art is custom is a different bug from missing art. Repair tooltip identity per instance. Do not mutate the shared donor object row.

Random hire must join using the live payload. “A custom city exists” is not a join key.

## Construction laws

Laws that care about “tavern” or “elemental building” must name exact city-logic SIDs from your rows. Do not infer category from icon art or donor city identity.

## Helper widget

Studio → Buildings and town.
