"""Scaffold an uncoupled custom-faction starter pack in the sandbox."""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .kit_meta import OVERLAY_REVIEW_NOTE, overlay_review_meta
from .schemas import require_sid, validate_faction_manifest

# Example identity blocks copied from the Golden Era mod's custom_factions/homm3_*.json
# files. They are not a HoMM3-name lookup table. Tower is Human/Tundra in that mod,
# not Dungeon/Snow. Stronghold is Dungeon/Wasteland, not an Orc town. Inferno is
# demons/Molten (donorCitySid remains demon_city). Copy donorFactionSid and
# nativeBiome from a live Core faction row if you are not cloning that example.
#
# exampleT1DonorBaseSid is a placeholder from the same vanilla family. Golden Era
# mixed donors per line; replace this SID from live Core for each creature line.
DEFAULT_DONORS: dict[str, dict[str, str]] = {
    "castle": {
        "donorFactionSid": "humans",
        "donorCitySid": "human_city",
        "donorFactionCoreSid": "human",
        "nativeBiome": "Valleys",
        "exampleT1DonorBaseSid": "esquire",
        "exampleSource": "Golden Era homm3_castle.json identity block",
    },
    "rampart": {
        "donorFactionSid": "nature",
        "donorCitySid": "nature_city",
        "donorFactionCoreSid": "nature",
        "nativeBiome": "Hills",
        "exampleT1DonorBaseSid": "twinkle",
        "exampleSource": "Golden Era homm3_rampart.json identity block",
    },
    "tower": {
        "donorFactionSid": "humans",
        "donorCitySid": "human_city",
        "donorFactionCoreSid": "human",
        "nativeBiome": "Tundra",
        "exampleT1DonorBaseSid": "esquire",
        "exampleSource": "Golden Era homm3_tower.json identity block",
    },
    "inferno": {
        "donorFactionSid": "demons",
        "donorCitySid": "demon_city",
        "donorFactionCoreSid": "demon",
        "nativeBiome": "Molten",
        "exampleT1DonorBaseSid": "trick_demon",
        "exampleSource": "Golden Era homm3_inferno.json identity block",
    },
    "necropolis": {
        "donorFactionSid": "undead",
        "donorCitySid": "undead_city",
        "donorFactionCoreSid": "undead",
        "nativeBiome": "Curselands",
        "exampleT1DonorBaseSid": "skeleton",
        "exampleSource": "Golden Era homm3_necropolis.json identity block",
    },
    "dungeon": {
        "donorFactionSid": "dungeon",
        "donorCitySid": "dungeon_city",
        "donorFactionCoreSid": "dungeon",
        "nativeBiome": "Burrow",
        "exampleT1DonorBaseSid": "trogl",
        "exampleSource": "Golden Era homm3_dungeon.json identity block",
    },
    "stronghold": {
        "donorFactionSid": "dungeon",
        "donorCitySid": "dungeon_city",
        "donorFactionCoreSid": "dungeon",
        "nativeBiome": "Wasteland",
        "exampleT1DonorBaseSid": "trogl",
        "exampleSource": "Golden Era homm3_stronghold.json identity block",
    },
    "fortress": {
        "donorFactionSid": "nature",
        "donorCitySid": "nature_city",
        "donorFactionCoreSid": "nature",
        "nativeBiome": "Swamp",
        "exampleT1DonorBaseSid": "twinkle",
        "exampleSource": "Golden Era homm3_fortress.json identity block",
    },
    "conflux": {
        "donorFactionSid": "nature",
        "donorCitySid": "nature_city",
        "donorFactionCoreSid": "nature",
        "nativeBiome": "Greenlands",
        "exampleT1DonorBaseSid": "twinkle",
        "exampleSource": "Golden Era homm3_conflux.json identity block",
    },
    "cove": {
        "donorFactionSid": "humans",
        "donorCitySid": "human_city",
        "donorFactionCoreSid": "human",
        "nativeBiome": "Tropical",
        "exampleT1DonorBaseSid": "esquire",
        "exampleSource": "Golden Era homm3_cove.json identity block",
    },
    "factory": {
        "donorFactionSid": "humans",
        "donorCitySid": "human_city",
        "donorFactionCoreSid": "human",
        "nativeBiome": "Foundry",
        "exampleT1DonorBaseSid": "esquire",
        "exampleSource": "Golden Era homm3_factory.json identity block",
    },
    "bulwark": {
        "donorFactionSid": "nature",
        "donorCitySid": "nature_city",
        "donorFactionCoreSid": "nature",
        "nativeBiome": "Permafrost",
        "exampleT1DonorBaseSid": "twinkle",
        "exampleSource": "Golden Era homm3_bulwark.json identity block",
    },
}

# Biome strings that appear on Golden Era faction identity blocks. Several of
# these are custom and need a full terrain pipeline. Copy from live Core; do
# not guess a HoMM3 terrain name (Snow, Rough, Subterranean, Water, …).
EXAMPLE_BIOMES = tuple(
    sorted({row["nativeBiome"] for row in DEFAULT_DONORS.values()})
)

# Kept as an alias so older imports keep working. Not a complete vanilla list.
DEFAULT_BIOMES = EXAMPLE_BIOMES


def donor_key_help() -> str:
    return ", ".join(sorted(DEFAULT_DONORS))


def scaffold_faction(
    *,
    short_name: str,
    display_name: str,
    donor_key: str,
    biome: str | None = None,
    unit_lines: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    slug = require_sid(f"homm3_{short_name}" if not short_name.startswith("homm3_") else short_name, "short_name")
    if donor_key not in DEFAULT_DONORS:
        raise ValueError(
            f"unknown donor_key {donor_key!r}. Known example keys: {sorted(DEFAULT_DONORS)}"
        )
    example = DEFAULT_DONORS[donor_key]
    identity_name = slug.removeprefix("homm3_")
    placeholder_unit = example["exampleT1DonorBaseSid"]
    lines = unit_lines or [
        {
            "tier": 1,
            "baseSid": f"h3_{identity_name}_t1",
            "donorFactionSid": example["donorFactionSid"],
            "donorBaseSid": placeholder_unit,
            "names": [f"{display_name} Recruit", f"{display_name} Veteran", f"{display_name} Elite"],
            "notes": (
                f"Placeholder donor unit {placeholder_unit!r} from the same vanilla family as "
                f"{example['exampleSource']}. Golden Era mixed donors per line. Replace this "
                "SID from live Core for every creature line."
            ),
        }
    ]
    manifest = {
        "schemaVersion": 1,
        "identity": {
            "factionSid": slug,
            "citySid": f"{slug}_city",
            "displayNameToken": f"{slug}_name",
            "descriptionToken": f"{slug}_desc",
            "nativeBiome": biome or example["nativeBiome"],
            "donorFactionSid": example["donorFactionSid"],
            "donorCitySid": example["donorCitySid"],
        },
        "coreOverlay": {
            "factionJson": f"DB/fractions/{slug}.json",
            "cityLogic": f"DB/objects_logic/cities/{slug}_city.json",
            "lawsTable": f"DB/fractions_laws/fractions_laws_table_{slug}.json",
            "squadTree": f"DB/squads/squads_{slug}/",
            "heroSubClasses": f"DB/heroes_sub_classes/sub_classes_{slug}.json",
            "heroSpecializations": f"DB/heroes_specializations/specializations_{slug}.json",
            "directCityMapObject": f"{slug}_city",
            "directDwellingPrefix": f"barracks_{slug}_",
            "donorFactionCoreSid": example["donorFactionCoreSid"],
            "pathNote": (
                "These paths are a sketch of Core members. A live overlay often prefixes "
                "faction files (example: DB/fractions/13_homm3_castle.json). The overlay packer "
                "chooses the numbered prefix. Do not treat this sketch as a drop-in path."
            ),
        },
        "unitVariants": ["", "_upg", "_upg_alt"],
        "unitLines": lines,
        "donorExample": {
            "donorKey": donor_key,
            "source": example["exampleSource"],
            "warning": (
                "Do not invent a donor from the HoMM3 town name. Tower in the Golden Era "
                "example uses humans/Tundra. Stronghold uses dungeon/Wasteland. Inferno uses "
                "demons (city shell demon_city) / Molten. Confirm every string in live Core."
            ),
        },
        "kitMeta": overlay_review_meta("scaffold_faction"),
        "notes": OVERLAY_REVIEW_NOTE,
    }
    validate_faction_manifest(manifest)
    return manifest


def write_faction_pack(manifest: dict[str, Any]) -> dict[str, str]:
    validate_faction_manifest(manifest)
    faction_sid = manifest["identity"]["factionSid"]
    folder_name = f"faction_{faction_sid}"
    written: dict[str, str] = {}

    def dump(name: str, payload: dict[str, Any]) -> None:
        path = sandbox_join(folder_name, name)
        write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        written[name] = str(path)

    dump("faction.json", manifest)
    dump(
        "ability_overrides.json",
        {
            "schemaVersion": 1,
            "factionSid": faction_sid,
            "kitMeta": overlay_review_meta("scaffold_faction.ability_overrides"),
            "notes": OVERLAY_REVIEW_NOTE,
            "unitOverrides": {},
        },
    )
    dump(
        "hero_overrides.json",
        {
            "schemaVersion": 1,
            "factionSid": faction_sid,
            "kitMeta": overlay_review_meta("scaffold_faction.hero_overrides"),
            "notes": OVERLAY_REVIEW_NOTE,
            "heroOverrides": {},
        },
    )
    dump(
        "law_overrides.json",
        {
            "schemaVersion": 1,
            "factionSid": faction_sid,
            "kitMeta": overlay_review_meta("scaffold_faction.law_overrides"),
            "notes": (
                "Prefer native Core bonus primitives. Hook-required laws stay behind an "
                "explicit proof gate. " + OVERLAY_REVIEW_NOTE
            ),
            "lawOverrides": {
                f"{faction_sid}_example_growth": {
                    "enabled": False,
                    "nameText": "Example Growth",
                    "descriptionText": "Disabled sandbox example. Native cityUnitsIncrement, not a Harmony mutator.",
                    "effects": [
                        {
                            "type": "cityUnitsIncrement",
                            "parameters": ["REPLACE_WITH_UNIT_SID", "1"],
                        }
                    ],
                }
            },
        },
    )
    checklist = _checklist_markdown(manifest)
    write_text(sandbox_join(folder_name, "CHECKLIST.md"), checklist)
    written["CHECKLIST.md"] = str(sandbox_join(folder_name, "CHECKLIST.md"))
    return written


def _checklist_markdown(manifest: dict[str, Any]) -> str:
    identity = manifest["identity"]
    faction_sid = identity["factionSid"]
    example = manifest.get("donorExample") or {}
    lines = ["# Custom faction checklist", "", f"Faction SID: `{faction_sid}`", ""]
    lines.extend(
        [
            "This checklist is the uncoupled work order. Each box is a separate component.",
            "Do not treat finishing one box as proof that another box works.",
            "",
            OVERLAY_REVIEW_NOTE,
            "",
            "## Identity and Core data",
            "",
            f"- [ ] Faction row `{identity['factionSid']}` exists in Core `DB/data.json` fractions lists.",
            f"- [ ] City logic `{identity['citySid']}` exists.",
            f"- [ ] Direct city map object `{manifest['coreOverlay']['directCityMapObject']}` exists.",
            "- [ ] Localization tokens for faction name and description exist in `Lang/english/texts`.",
            "- [ ] Every custom id is unique. Duplicate ids crash native dictionaries.",
            f"- [ ] `donorFactionSid` `{identity['donorFactionSid']}` and `nativeBiome` `{identity['nativeBiome']}` were copied from live Core (example source: {example.get('source', 'n/a')}).",
            "- [ ] Core faction JSON path uses the numbered prefix the overlay packer assigns (`DB/fractions/13_homm3_castle.json` is an overlay example, not a drop-in name).",
            "",
            "## Units",
            "",
        ]
    )
    for line in manifest["unitLines"]:
        names = ", ".join(line["names"])
        lines.append(
            f"- [ ] Tier {line['tier']}: `{line['baseSid']}` / upgrades ({names}). "
            f"Donor unit `{line['donorBaseSid']}` copied from live Core, not guessed. "
            "Logic arrays match view arrays."
        )
    lines.extend(
        [
            "",
            "## Presentation (pick one lane per unit)",
            "",
            "- [ ] Billboard lane: native-safe donor mesh fields + bundle billboard + map quad.",
            "- [ ] Skinned-mesh lane: `battlePresentationLane: skinned_mesh`, no battle billboard arrays.",
            "- [ ] Do not mix both lanes in one combat bundle.",
            "",
            "## Heroes",
            "",
            "- [ ] Might heroes grant `skill_warrior_ability`. Magic heroes grant `skill_mage_ability`.",
            "- [ ] Extra battle buttons are additional `heroBattleAbility` rows, not overwrites of the commander attack unless that is the explicit design.",
            "- [ ] Specialization bonuses use only supported types.",
            "",
            "## Buildings and town",
            "",
            "- [ ] Native building SIDs (`Build_Main`, `Build_Wall`, `Build_Magic_Guild`, `Build_Tier_*`, …) have custom text.",
            "- [ ] `Build_Treasury` vanilla name is Treasury (gold/day). A HoMM3-style Blacksmith is a rename of that slot, not a new engine type.",
            "- [ ] Town uses owned Unity city world + native `BhBuilding` clicks. Not Route A posters. `cityFactory` is a Golden Era scene-pattern name, not “reuse vanilla Factory town.”",
            "- [ ] External dwellings have direct map-object rows, hire logic, billboard art, and matching tooltip text.",
            "",
            "## Focus abilities",
            "",
            "- [ ] Each active lists a real native mechanic (copied special, buff SID, spell effect, or known template).",
            "- [ ] Tooltip text matches that mechanic. Do not write stun if the buff SID is Weaken Attack/Defense.",
            "- [ ] Focus cost is `energyLevel`. Cooldown is `cd` / `cooldown`.",
            "- [ ] Icon keys are runtime sprite keys already in the live sprite registry, or keys your plugin allowlists. A made-up key is missing art.",
            "- [ ] Player-facing text describes shipped behavior only.",
            "",
            "## Hooks",
            "",
            "- [ ] Needed runtime hooks are listed by family, with symbols in one registry.",
            "- [ ] Golden Era class names in the catalog are examples, not a public API. Re-pin after every Olden Era patch.",
            "- [ ] No donor-SID reverse lookup without exact context.",
            "- [ ] Fail closed if a required symbol is missing.",
            "",
            "## Proof",
            "",
            "- [ ] Packed Core.zip inspected (not only generator output).",
            "- [ ] Startup log shows the hook registered, if a hook is required.",
            "- [ ] User-visible gameplay is tested separately and labeled.",
            "",
        ]
    )
    return "\n".join(lines)
