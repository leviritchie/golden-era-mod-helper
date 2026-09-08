"""Scaffold custom town buildings onto native Olden Era slots."""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .schemas import require_sid, validate_building_plan

# Native city-logic SIDs the overlay already knows how to name.
# Creators rename and re-bonus these slots; they do not invent a second
# click system.
NATIVE_BUILDING_SLOTS: list[dict[str, str]] = [
    {"nativeSid": "Build_Main", "role": "hall", "displayName": "Village Hall", "levels": "Village Hall / Town Hall / City Hall / Capitol"},
    {"nativeSid": "Build_Wall", "role": "fortification", "displayName": "Fort", "levels": "Fort / Citadel / Castle"},
    {"nativeSid": "Build_Magic_Guild", "role": "mage_guild", "displayName": "Mage Guild", "levels": "Mage Guild 1–5"},
    {"nativeSid": "Build_Tavern", "role": "tavern", "displayName": "Tavern", "levels": "1"},
    {"nativeSid": "Build_Market", "role": "marketplace", "displayName": "Marketplace", "levels": "1"},
    {"nativeSid": "Build_Treasury", "role": "blacksmith", "displayName": "Blacksmith", "levels": "1"},
    {"nativeSid": "Build_Artifact_Market", "role": "artifact_merchants", "displayName": "Artifact Merchants", "levels": "1"},
    {"nativeSid": "Build_Resource_Depot", "role": "resource_silo", "displayName": "Resource Silo", "levels": "1"},
    {"nativeSid": "Build_Bank", "role": "special", "displayName": "Special Building", "levels": "1"},
    {"nativeSid": "Build_Mother_Nature", "role": "special", "displayName": "Visitor Stat Building", "levels": "1"},
    {"nativeSid": "Build_Mycelium_Roots", "role": "horde", "displayName": "Horde Building", "levels": "1"},
    {"nativeSid": "Build_Resource_Depot_level_2", "role": "horde", "displayName": "Horde Building (alt slot)", "levels": "1"},
    {"nativeSid": "Build_Spring_of_Life", "role": "grail", "displayName": "Grail Building", "levels": "1"},
    {"nativeSid": "Build_Intelligence_Academy", "role": "lookout", "displayName": "Lookout / sight radius", "levels": "1"},
    {"nativeSid": "Build_Training_Range", "role": "training", "displayName": "Stat trainer", "levels": "1"},
]


def default_dwellings(unit_lines: list[dict[str, Any]]) -> list[dict[str, str]]:
    dwellings: list[dict[str, str]] = []
    for line in unit_lines:
        tier = int(line["tier"])
        names = line.get("names") or [f"Tier {tier}"]
        base_name = str(names[0])
        dwellings.append(
            {
                "nativeSid": f"Build_Tier_{tier}",
                "role": "dwelling",
                "displayName": f"{base_name} Dwelling",
                "levels": f"{base_name} Dwelling / upgrade",
            }
        )
    return dwellings


def build_plan(
    *,
    faction_sid: str,
    city_sid: str | None = None,
    city_scene_name: str = "cityFactory",
    unit_lines: list[dict[str, Any]] | None = None,
    extra_buildings: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    faction = require_sid(faction_sid, "faction_sid")
    city = require_sid(city_sid or f"{faction}_city", "city_sid")
    buildings = [dict(slot) for slot in NATIVE_BUILDING_SLOTS]
    buildings.extend(default_dwellings(unit_lines or []))
    if extra_buildings:
        buildings.extend(extra_buildings)
    plan = {
        "schemaVersion": 1,
        "factionSid": faction,
        "citySid": city,
        "citySceneName": city_scene_name,
        "townParadigm": "owned_city_world",
        "rejectedParadigms": [
            "Route A CanvasCityPanel posters",
            "UI click relays from world clicks into RawImage town layers",
            "Aliasing this town onto another live faction city",
        ],
        "interactionRule": (
            "Clicks stay on native BhBuilding / BhBuildingsManager. "
            "Construction opens through HUD BuildingsConstruction navigation."
        ),
        "visualRule": (
            "Paint custom art onto native building slots in an owned Unity city world. "
            "Do not force-activate unbound slots every presentation pass."
        ),
        "buildings": buildings,
        "externalDwellings": {
            "needDirectMapObjectRows": True,
            "needHireLogicRows": True,
            "needBillboardArt": True,
            "needMatchingTooltipText": True,
            "doNotMutateSharedDonorObjectConfigId": True,
        },
        "notes": "Sandbox building plan. Not applied to live Core.zip.",
    }
    validate_building_plan(plan)
    return plan


def save_plan(plan: dict[str, Any]) -> str:
    validate_building_plan(plan)
    path = sandbox_join(f"buildings_{plan['factionSid']}.json")
    write_text(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    return str(path)
