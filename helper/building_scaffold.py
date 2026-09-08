"""Scaffold custom town buildings onto native Olden Era slots."""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .kit_meta import OVERLAY_REVIEW_NOTE, overlay_review_meta
from .schemas import require_sid, validate_building_plan

# Native city-logic SIDs. displayName is the vanilla Olden Era name where known.
# HoMM3-style ports often rename a slot (Treasury -> Blacksmith) without changing the SID.
NATIVE_BUILDING_SLOTS: list[dict[str, str]] = [
    {"nativeSid": "Build_Main", "role": "hall", "displayName": "Village Hall", "vanillaName": "Village Hall", "typicalPortRename": "", "levels": "Village Hall / Town Hall / City Hall / Capitol"},
    {"nativeSid": "Build_Wall", "role": "fortification", "displayName": "Fort", "vanillaName": "Fort", "typicalPortRename": "", "levels": "Fort / Citadel / Castle"},
    {"nativeSid": "Build_Magic_Guild", "role": "mage_guild", "displayName": "Mage Guild", "vanillaName": "Mage Guild", "typicalPortRename": "", "levels": "Mage Guild 1–5"},
    {"nativeSid": "Build_Tavern", "role": "tavern", "displayName": "Tavern", "vanillaName": "Tavern", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Market", "role": "marketplace", "displayName": "Marketplace", "vanillaName": "Marketplace", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Treasury", "role": "gold_income", "displayName": "Treasury", "vanillaName": "Treasury", "typicalPortRename": "Blacksmith", "vanillaEffect": "Produces gold daily.", "levels": "1"},
    {"nativeSid": "Build_Artifact_Market", "role": "artifact_merchants", "displayName": "Artifact Merchants", "vanillaName": "Artifact Merchants", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Resource_Depot", "role": "resource_silo", "displayName": "Resource Silo", "vanillaName": "Resource Silo", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Bank", "role": "special", "displayName": "Bank", "vanillaName": "Bank", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Mother_Nature", "role": "visitor_stat", "displayName": "Mother Nature", "vanillaName": "Mother Nature", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Mycelium_Roots", "role": "horde", "displayName": "Mycelium Roots", "vanillaName": "Mycelium Roots", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Resource_Depot_level_2", "role": "horde_alt", "displayName": "Resource Depot level 2", "vanillaName": "Resource Depot level 2", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Spring_of_Life", "role": "grail", "displayName": "Spring of Life", "vanillaName": "Spring of Life", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Intelligence_Academy", "role": "lookout", "displayName": "Intelligence Academy", "vanillaName": "Intelligence Academy", "typicalPortRename": "", "levels": "1"},
    {"nativeSid": "Build_Training_Range", "role": "training", "displayName": "Training Range", "vanillaName": "Training Range", "typicalPortRename": "", "levels": "1"},
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
        "citySceneNameNote": (
            "cityFactory is a Golden Era Unity scene-pattern name. It is not "
            "'reuse the vanilla Factory town.' Give your faction its own dedicated world."
        ),
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
        "kitMeta": overlay_review_meta("building_scaffold"),
        "notes": OVERLAY_REVIEW_NOTE,
    }
    validate_building_plan(plan)
    return plan


def save_plan(plan: dict[str, Any]) -> str:
    validate_building_plan(plan)
    path = sandbox_join(f"buildings_{plan['factionSid']}.json")
    write_text(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    return str(path)
