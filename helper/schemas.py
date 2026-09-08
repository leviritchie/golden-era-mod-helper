"""JSON schemas and validators for uncoupled Olden Era creator files.

These schemas describe the *shape* other creators should author. They are
not a Core.zip packer. Invalid input raises; nothing is silently dropped.
"""

from __future__ import annotations

import re
from typing import Any

SID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

SPECIALIZATION_BONUS_TYPES = frozenset(
    {
        "battleSubskillBonus",
        "cityUnitsIncrement",
        "heroMagicReplace",
        "heroStat",
        "heroStatBattle",
        "sideRes",
        "unitStat",
    }
)

# Common grants are separate from designer specialty bonuses.
COMMON_GRANT_BONUS_TYPES = frozenset({"heroBattleAbility"})

PRESENTATION_LANES = frozenset({"billboard", "skinned_mesh", "depth_billboard_experiment"})

ABILITY_SLOT_KINDS = frozenset({"abilities", "passives", "alternativeAttacks"})


class SchemaError(ValueError):
    """Raised when a creator file does not match the documented contract."""


def require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value


def require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{label} must be a non-empty string")
    return value


def optional_str(value: Any, label: str) -> str:
    if value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise SchemaError(f"{label} must be a string")
    return value


def require_sid(value: Any, label: str) -> str:
    text = require_str(value, label)
    if not SID_RE.fullmatch(text):
        raise SchemaError(
            f"{label} must be a SID: letters, digits, underscore, starting with a letter. Got {text!r}"
        )
    return text


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise SchemaError(f"{label} must be true or false, not {value!r}")
    return value


def require_int(value: Any, label: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise SchemaError(f"{label} must be >= {minimum}")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be a list")
    return value


def validate_icon_key(icon_key: str, label: str) -> str:
    key = optional_str(icon_key, label)
    if not key:
        return ""
    lowered = key.lower()
    if lowered.endswith("_name") or lowered.endswith("_description"):
        raise SchemaError(
            f"{label} looks like a localization token ({key!r}). "
            "Use a runtime sprite key such as assassin_buff_icon."
        )
    if "@" in key or "orientation" in lowered:
        raise SchemaError(
            f"{label} looks like an atlas/export filename ({key!r}). "
            "Do not use scale suffixes such as Orientation@4x."
        )
    return key


def validate_existing_special(entry: Any, unit_sid: str, index: int) -> dict[str, Any]:
    row = require_dict(entry, f"{unit_sid} existingSpecials[{index}]")
    slot = require_str(row.get("slotKind"), f"{unit_sid} existingSpecials[{index}].slotKind")
    if slot not in ABILITY_SLOT_KINDS:
        raise SchemaError(
            f"{unit_sid} existingSpecials[{index}].slotKind must be one of {sorted(ABILITY_SLOT_KINDS)}"
        )
    energy = row.get("energyLevel", 0)
    if energy in ("", None):
        energy = 0
    require_int(energy, f"{unit_sid} existingSpecials[{index}].energyLevel", minimum=0)
    validate_icon_key(row.get("iconKey") or "", f"{unit_sid} existingSpecials[{index}].iconKey")
    require_bool(row.get("enabled"), f"{unit_sid} existingSpecials[{index}].enabled")
    # Preserve creator metadata. Do not strip unknown keys.
    return row


def validate_ability_card(entry: Any, unit_sid: str, index: int) -> dict[str, Any]:
    row = require_dict(entry, f"{unit_sid} abilities[{index}]")
    require_str(row.get("templateId") or row.get("id"), f"{unit_sid} abilities[{index}] templateId")
    energy = row.get("energyLevel", 0)
    if energy in ("", None):
        energy = 0
    require_int(energy, f"{unit_sid} abilities[{index}].energyLevel", minimum=0)
    validate_icon_key(row.get("iconKey") or "", f"{unit_sid} abilities[{index}].iconKey")
    return row


def validate_unit_override(unit_sid: str, payload: Any) -> dict[str, Any]:
    require_sid(unit_sid, "unit SID")
    row = require_dict(payload, f"unitOverrides.{unit_sid}")
    require_bool(
        row.get("replaceExistingAbilities", False),
        f"{unit_sid}.replaceExistingAbilities",
    )
    require_bool(
        row.get("replaceExistingPassives", False),
        f"{unit_sid}.replaceExistingPassives",
    )
    optional_str(row.get("branchRole"), f"{unit_sid}.branchRole")
    optional_str(row.get("sourceMechanicId"), f"{unit_sid}.sourceMechanicId")
    optional_str(row.get("decisionTest"), f"{unit_sid}.decisionTest")
    abilities = require_list(row.get("abilities") or [], f"{unit_sid}.abilities")
    for index, ability in enumerate(abilities):
        validate_ability_card(ability, unit_sid, index)
    specials = require_list(row.get("existingSpecials") or [], f"{unit_sid}.existingSpecials")
    for index, special in enumerate(specials):
        validate_existing_special(special, unit_sid, index)
    return row


def validate_ability_overrides(payload: Any) -> dict[str, Any]:
    doc = require_dict(payload, "ability overrides")
    if doc.get("schemaVersion") != 1:
        raise SchemaError("ability overrides schemaVersion must be 1")
    require_sid(doc.get("factionSid"), "factionSid")
    units = require_dict(doc.get("unitOverrides") or {}, "unitOverrides")
    for unit_sid, row in units.items():
        validate_unit_override(unit_sid, row)
    return doc


def validate_specialization_bonus(hero_sid: str, bonus: Any, index: int) -> dict[str, Any]:
    row = require_dict(bonus, f"{hero_sid} bonuses[{index}]")
    bonus_type = require_str(row.get("type"), f"{hero_sid} bonuses[{index}].type")
    allowed = SPECIALIZATION_BONUS_TYPES | COMMON_GRANT_BONUS_TYPES
    if bonus_type not in allowed:
        raise SchemaError(
            f"{hero_sid} bonuses[{index}] has unsupported type {bonus_type!r}. "
            f"Allowed specialty types: {sorted(SPECIALIZATION_BONUS_TYPES)}. "
            f"Common grant type: heroBattleAbility."
        )
    params = row.get("parameters")
    if params is not None:
        require_list(params, f"{hero_sid} bonuses[{index}].parameters")
    return row


def validate_hero_override(hero_sid: str, payload: Any) -> dict[str, Any]:
    require_sid(hero_sid, "hero SID")
    row = require_dict(payload, f"heroOverrides.{hero_sid}")
    require_bool(row.get("enabled", True), f"{hero_sid}.enabled")
    class_type = row.get("classType")
    if class_type not in ("might", "magic"):
        raise SchemaError(f"{hero_sid}.classType must be 'might' or 'magic'")
    spec = row.get("specialization")
    if spec is not None:
        spec_row = require_dict(spec, f"{hero_sid}.specialization")
        bonuses = require_list(spec_row.get("bonuses") or [], f"{hero_sid}.specialization.bonuses")
        for index, bonus in enumerate(bonuses):
            validate_specialization_bonus(hero_sid, bonus, index)
    return row


def validate_hero_overrides(payload: Any) -> dict[str, Any]:
    doc = require_dict(payload, "hero overrides")
    if doc.get("schemaVersion") != 1:
        raise SchemaError("hero overrides schemaVersion must be 1")
    require_sid(doc.get("factionSid"), "factionSid")
    heroes = require_dict(doc.get("heroOverrides") or {}, "heroOverrides")
    for hero_sid, row in heroes.items():
        validate_hero_override(hero_sid, row)
    return doc


def validate_faction_manifest(payload: Any) -> dict[str, Any]:
    doc = require_dict(payload, "faction manifest")
    if doc.get("schemaVersion") != 1:
        raise SchemaError("faction manifest schemaVersion must be 1")
    identity = require_dict(doc.get("identity"), "identity")
    require_sid(identity.get("factionSid"), "identity.factionSid")
    require_sid(identity.get("citySid"), "identity.citySid")
    require_sid(identity.get("donorFactionSid"), "identity.donorFactionSid")
    require_sid(identity.get("donorCitySid"), "identity.donorCitySid")
    require_str(identity.get("nativeBiome"), "identity.nativeBiome")
    overlay = require_dict(doc.get("coreOverlay"), "coreOverlay")
    for key in (
        "factionJson",
        "cityLogic",
        "lawsTable",
        "squadTree",
        "heroSpecializations",
        "directCityMapObject",
        "directDwellingPrefix",
    ):
        require_str(overlay.get(key), f"coreOverlay.{key}")
    lines = require_list(doc.get("unitLines"), "unitLines")
    if len(lines) < 1:
        raise SchemaError("unitLines must contain at least one creature line")
    for index, line in enumerate(lines):
        row = require_dict(line, f"unitLines[{index}]")
        require_int(row.get("tier"), f"unitLines[{index}].tier", minimum=1)
        require_sid(row.get("baseSid"), f"unitLines[{index}].baseSid")
        require_sid(row.get("donorBaseSid"), f"unitLines[{index}].donorBaseSid")
        names = require_list(row.get("names") or [], f"unitLines[{index}].names")
        if not names:
            raise SchemaError(f"unitLines[{index}].names must list base and upgrade display names")
    return doc


def validate_presentation_plan(payload: Any) -> dict[str, Any]:
    doc = require_dict(payload, "presentation plan")
    if doc.get("schemaVersion") != 1:
        raise SchemaError("presentation plan schemaVersion must be 1")
    require_sid(doc.get("unitSid"), "unitSid")
    lane = require_str(doc.get("battlePresentationLane"), "battlePresentationLane")
    if lane not in PRESENTATION_LANES:
        raise SchemaError(
            f"battlePresentationLane must be one of {sorted(PRESENTATION_LANES)}, not {lane!r}"
        )
    if lane == "skinned_mesh" and doc.get("alsoUseBattleBillboardArrays") is True:
        raise SchemaError(
            "skinned_mesh omits battle billboard arrays. Mixing both crashes combat Init."
        )
    return doc


def validate_building_plan(payload: Any) -> dict[str, Any]:
    doc = require_dict(payload, "building plan")
    if doc.get("schemaVersion") != 1:
        raise SchemaError("building plan schemaVersion must be 1")
    require_sid(doc.get("factionSid"), "factionSid")
    require_sid(doc.get("citySid"), "citySid")
    paradigm = require_str(doc.get("townParadigm"), "townParadigm")
    if paradigm != "owned_city_world":
        raise SchemaError(
            "townParadigm must be 'owned_city_world'. Route A posters are not the product path."
        )
    buildings = require_list(doc.get("buildings"), "buildings")
    if not buildings:
        raise SchemaError("buildings must list at least the native hall/wall/guild/dwelling slots")
    seen: set[str] = set()
    for index, building in enumerate(buildings):
        row = require_dict(building, f"buildings[{index}]")
        sid = require_str(row.get("nativeSid"), f"buildings[{index}].nativeSid")
        if sid in seen:
            raise SchemaError(f"duplicate native building SID {sid}")
        seen.add(sid)
        require_str(row.get("displayName"), f"buildings[{index}].displayName")
        require_str(row.get("role"), f"buildings[{index}].role")
    return doc
