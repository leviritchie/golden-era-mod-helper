"""Scaffold an uncoupled custom-faction starter pack in the sandbox."""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .schemas import require_sid, validate_faction_manifest


DEFAULT_BIOMES = (
    "Valleys",
    "Forest",
    "Swamp",
    "Snow",
    "Sand",
    "Dirt",
    "Rough",
    "Lava",
    "Subterranean",
    "Water",
)

DEFAULT_DONORS = {
    "castle": ("humans", "human_city", "Valleys"),
    "rampart": ("nature", "nature_city", "Forest"),
    "tower": ("dungeon", "dungeon_city", "Snow"),
    "inferno": ("demon", "demon_city", "Lava"),
    "necropolis": ("undead", "undead_city", "Dirt"),
    "dungeon": ("dungeon", "dungeon_city", "Subterranean"),
    "stronghold": ("orc", "orc_city", "Rough"),
    "fortress": ("nature", "nature_city", "Swamp"),
    "conflux": ("nature", "nature_city", "Valleys"),
    "cove": ("humans", "human_city", "Water"),
}


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
            f"unknown donor_key {donor_key!r}. Known keys: {sorted(DEFAULT_DONORS)}"
        )
    donor_faction, donor_city, default_biome = DEFAULT_DONORS[donor_key]
    identity_name = slug.removeprefix("homm3_")
    lines = unit_lines or [
        {
            "tier": 1,
            "baseSid": f"h3_{identity_name}_t1",
            "donorFactionSid": donor_faction,
            "donorBaseSid": "esquire",
            "names": [f"{display_name} Recruit", f"{display_name} Veteran", f"{display_name} Elite"],
        }
    ]
    manifest = {
        "schemaVersion": 1,
        "identity": {
            "factionSid": slug,
            "citySid": f"{slug}_city",
            "displayNameToken": f"{slug}_name",
            "descriptionToken": f"{slug}_desc",
            "nativeBiome": biome or default_biome,
            "donorFactionSid": donor_faction,
            "donorCitySid": donor_city,
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
            "donorFactionCoreSid": donor_faction.rstrip("s") if donor_faction.endswith("s") else donor_faction,
        },
        "unitVariants": ["", "_upg", "_upg_alt"],
        "unitLines": lines,
        "notes": (
            "Sandbox scaffold from this teaching kit. "
            "This file is not installed into the game."
        ),
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
        {"schemaVersion": 1, "factionSid": faction_sid, "unitOverrides": {}},
    )
    dump(
        "hero_overrides.json",
        {"schemaVersion": 1, "factionSid": faction_sid, "heroOverrides": {}},
    )
    dump(
        "law_overrides.json",
        {
            "schemaVersion": 1,
            "factionSid": faction_sid,
            "notes": "Prefer native Core bonus primitives. Hook-required laws stay behind an explicit proof gate.",
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
    lines = ["# Custom faction checklist", "", f"Faction SID: `{faction_sid}`", ""]
    lines.extend(
        [
            "This checklist is the uncoupled work order. Each box is a separate component.",
            "Do not treat finishing one box as proof that another box works.",
            "",
            "## Identity and Core data",
            "",
            f"- [ ] Faction row `{identity['factionSid']}` exists in Core `DB/data.json` fractions lists.",
            f"- [ ] City logic `{identity['citySid']}` exists.",
            f"- [ ] Direct city map object `{manifest['coreOverlay']['directCityMapObject']}` exists.",
            "- [ ] Localization tokens for faction name and description exist in `Lang/english/texts`.",
            "- [ ] Every custom id is unique. Duplicate ids crash native dictionaries.",
            "",
            "## Units",
            "",
        ]
    )
    for line in manifest["unitLines"]:
        names = ", ".join(line["names"])
        lines.append(
            f"- [ ] Tier {line['tier']}: `{line['baseSid']}` / upgrades ({names}). "
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
            "- [ ] Town uses owned Unity city world + native `BhBuilding` clicks. Not Route A posters.",
            "- [ ] External dwellings have direct map-object rows, hire logic, billboard art, and matching tooltip text.",
            "",
            "## Focus abilities",
            "",
            "- [ ] Each active lists a real native mechanic (copied special, buff SID, spell effect, or known template).",
            "- [ ] Focus cost is `energyLevel`. Cooldown is `cd` / `cooldown`.",
            "- [ ] Icon keys are runtime sprite keys, not localization tokens.",
            "- [ ] Player-facing text describes shipped behavior only.",
            "",
            "## Hooks",
            "",
            "- [ ] Needed runtime hooks are listed by family, with symbols in one registry.",
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
