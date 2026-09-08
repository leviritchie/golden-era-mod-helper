"""Assign custom Focus abilities onto unit override files.

This is the helper's revival of the older local ability editor: pick a native
template, set Focus cost / cooldown / text / icon, and write a reviewable
override document. Output always lands in the helper sandbox.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .isolation import write_text
from .paths import DATA_DIR, SAMPLE_DIR
from .schemas import SchemaError, require_sid, validate_ability_overrides, validate_icon_key


def load_templates() -> list[dict[str, Any]]:
    path = DATA_DIR / "ability_templates.json"
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    templates = payload.get("templates")
    if not isinstance(templates, list) or not templates:
        raise SchemaError("ability_templates.json must contain a templates list")
    return templates


def template_by_id(template_id: str) -> dict[str, Any]:
    for template in load_templates():
        if template.get("id") == template_id:
            return deepcopy(template)
    raise SchemaError(f"unknown ability template: {template_id!r}")


def empty_ability_overrides(faction_sid: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "factionSid": require_sid(faction_sid, "factionSid"),
        "unitOverrides": {},
    }


def load_sample_overrides() -> dict[str, Any]:
    path = SAMPLE_DIR / "ability_overrides.json"
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _unit_row(doc: dict[str, Any], unit_sid: str) -> dict[str, Any]:
    units = doc.setdefault("unitOverrides", {})
    if unit_sid not in units:
        units[unit_sid] = {
            "abilities": [],
            "existingSpecials": [],
            "replaceExistingAbilities": False,
            "replaceExistingPassives": False,
            "branchRole": "",
            "sourceMechanicId": "",
            "decisionTest": "",
        }
    return units[unit_sid]


def assign_focus_ability(
    doc: dict[str, Any],
    *,
    unit_sid: str,
    template_id: str,
    display_name: str,
    description: str,
    energy_level: int,
    cooldown: int,
    rank: int = 1,
    charges: str | int | None = None,
    icon_key: str = "",
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Attach one templated Focus ability to a unit override document."""
    require_sid(unit_sid, "unit_sid")
    if energy_level < 0:
        raise SchemaError("energyLevel / Focus cost cannot be negative")
    if cooldown < 0:
        raise SchemaError("cooldown cannot be negative")
    validate_icon_key(icon_key, "iconKey")
    template = template_by_id(template_id)
    card: dict[str, Any] = {
        "templateId": template_id,
        "templateLabel": template.get("label"),
        "category": template.get("category"),
        "risk": template.get("risk"),
        "nameText": display_name,
        "descriptionText": description,
        "nameKey": f"{unit_sid}_{template_id}_name",
        "descriptionKey": f"{unit_sid}_{template_id}_description",
        "energyLevel": energy_level,
        "cooldown": cooldown,
        "rank": rank,
        "charges": "" if charges is None else charges,
        "iconKey": icon_key,
        "defaults": template.get("defaults") or {},
        "logic": deepcopy(template.get("logic")),
        "view": deepcopy(template.get("view")),
    }
    if extra_fields:
        for key, value in extra_fields.items():
            if key in card:
                raise SchemaError(f"extra field {key!r} would overwrite a required ability field")
            card[key] = value
    row = _unit_row(doc, unit_sid)
    row.setdefault("abilities", []).append(card)
    validate_ability_overrides(doc)
    return card


def set_existing_special(
    doc: dict[str, Any],
    *,
    unit_sid: str,
    slot_kind: str,
    index: int,
    enabled: bool,
    name_text: str,
    description_text: str,
    energy_level: int,
    cooldown: int,
    icon_key: str = "",
    effect_key: str = "",
    effect_kind: str = "",
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a reviewable edit to a unit's already-generated special slot."""
    require_sid(unit_sid, "unit_sid")
    special = {
        "key": f"{slot_kind}:{index}",
        "slotKind": slot_kind,
        "index": index,
        "enabled": enabled,
        "nameText": name_text,
        "descriptionText": description_text,
        "nameKey": f"{unit_sid}_{slot_kind}_{index}_name",
        "descriptionKey": f"{unit_sid}_{slot_kind}_{index}_description",
        "iconKey": icon_key,
        "energyLevel": energy_level,
        "cooldown": cooldown,
        "rank": 1,
        "charges": "",
        "effectKey": effect_key,
        "effectKind": effect_kind,
        "effectLabel": "",
        "effectPayload": {},
        "notes": "Edited in this clone's sandbox. Does not mutate live Core.zip.",
    }
    if extra_fields:
        special.update(extra_fields)
    row = _unit_row(doc, unit_sid)
    specials: list[dict[str, Any]] = row.setdefault("existingSpecials", [])
    replaced = False
    for position, current in enumerate(specials):
        if current.get("key") == special["key"]:
            specials[position] = special
            replaced = True
            break
    if not replaced:
        specials.append(special)
    validate_ability_overrides(doc)
    return special


def save_ability_overrides(doc: dict[str, Any], dest: Path) -> Path:
    validate_ability_overrides(doc)
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    return write_text(dest, text)
