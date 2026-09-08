"""Assign custom Focus abilities onto unit override files.

This is the helper's revival of the older local ability editor: pick a native
template, set Focus cost / cooldown / text / icon, and write a reviewable
override document. Output always lands in the helper sandbox.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .isolation import write_text
from .kit_meta import OVERLAY_REVIEW_NOTE, WEAKEN_EXAMPLE_BUFF_SID, overlay_review_meta
from .paths import DATA_DIR, SAMPLE_DIR
from .schemas import SchemaError, require_sid, validate_ability_overrides, validate_icon_key

_CONTROL_CLAIM = re.compile(
    r"\b(stun|stunning|stagger|staggers|petrify|petrifies|sleep|sleeps)\b",
    re.IGNORECASE,
)


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
        "kitMeta": overlay_review_meta("ability_assigner"),
        "notes": OVERLAY_REVIEW_NOTE,
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


def _merge_mechanic_defaults(
    defaults: dict[str, Any],
    *,
    buff_sid: str,
    unit_special_key: str,
    source_unit_sid: str,
    spell_sid: str,
) -> dict[str, Any]:
    merged = deepcopy(defaults)
    if buff_sid:
        merged["buffSid"] = buff_sid
    if unit_special_key:
        merged["unitSpecialKey"] = unit_special_key
    if source_unit_sid:
        merged["sourceUnitSid"] = source_unit_sid
    if spell_sid:
        merged["spellSid"] = spell_sid
    return merged


def _require_mechanic_fields(template: dict[str, Any], defaults: dict[str, Any]) -> None:
    required = template.get("requiredMechanicFields") or []
    missing: list[str] = []
    for field in required:
        value = defaults.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(str(field))
    if not missing:
        return
    template_id = template.get("id")
    example = ""
    if "buffSid" in missing:
        example = (
            f" For a Weaken Attack/Defense strike, copy live Core `{WEAKEN_EXAMPLE_BUFF_SID}`. "
            "This kit does not invent a stun buff SID."
        )
    raise SchemaError(
        f"template {template_id!r} requires non-empty {missing} copied from live Core.{example}"
    )


def _refuse_tooltip_mechanic_mismatch(description: str, defaults: dict[str, Any], template_id: str) -> None:
    buff_sid = str(defaults.get("buffSid") or "")
    if buff_sid == WEAKEN_EXAMPLE_BUFF_SID and _CONTROL_CLAIM.search(description):
        raise SchemaError(
            "Player-facing text claims stun/stagger/petrify/sleep, but buffSid is "
            f"{WEAKEN_EXAMPLE_BUFF_SID} (Weaken Attack and Defense in live Core, not stun). "
            "Change the tooltip to match Weaken, or use focus_stun_melee with a live Core stun buff SID."
        )
    if template_id == "focus_stun_melee" and buff_sid == WEAKEN_EXAMPLE_BUFF_SID:
        raise SchemaError(
            f"focus_stun_melee cannot use {WEAKEN_EXAMPLE_BUFF_SID}; that SID is Weaken, not stun."
        )


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
    buff_sid: str = "",
    unit_special_key: str = "",
    source_unit_sid: str = "",
    spell_sid: str = "",
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
    defaults = _merge_mechanic_defaults(
        template.get("defaults") or {},
        buff_sid=buff_sid,
        unit_special_key=unit_special_key,
        source_unit_sid=source_unit_sid,
        spell_sid=spell_sid,
    )
    _require_mechanic_fields(template, defaults)
    _refuse_tooltip_mechanic_mismatch(description, defaults, template_id)
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
        "buffSid": defaults.get("buffSid") or "",
        "unitSpecialKey": defaults.get("unitSpecialKey") or "",
        "sourceUnitSid": defaults.get("sourceUnitSid") or "",
        "spellSid": defaults.get("spellSid") or "",
        "mustConfirmFromLiveCore": list(template.get("requiredMechanicFields") or []),
        "defaults": defaults,
        "logic": deepcopy(template.get("logic")),
        "view": deepcopy(template.get("view")),
        "notes": OVERLAY_REVIEW_NOTE,
    }
    if extra_fields:
        for key, value in extra_fields.items():
            if key in card:
                raise SchemaError(f"extra field {key!r} would overwrite a required ability field")
            card[key] = value
    row = _unit_row(doc, unit_sid)
    row.setdefault("abilities", []).append(card)
    doc.setdefault("kitMeta", overlay_review_meta("ability_assigner"))
    doc.setdefault("notes", OVERLAY_REVIEW_NOTE)
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
    notes = [
        "Edited in this clone's sandbox. Does not mutate live Core.zip.",
        OVERLAY_REVIEW_NOTE,
        "Confirm the native special's real effect in live Core before writing stun/stagger in the tooltip.",
    ]
    if _CONTROL_CLAIM.search(description_text) and not (effect_key or "").strip():
        notes.append(
            "Tooltip claims a control effect but effectKey is empty. Fill the copied native special key, or the tooltip is fiction."
        )
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
        "notes": " ".join(notes),
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
    doc.setdefault("kitMeta", overlay_review_meta("ability_assigner"))
    doc.setdefault("notes", OVERLAY_REVIEW_NOTE)
    validate_ability_overrides(doc)
    return special


def save_ability_overrides(doc: dict[str, Any], dest: Path) -> Path:
    validate_ability_overrides(doc)
    doc.setdefault("kitMeta", overlay_review_meta("ability_assigner"))
    doc.setdefault("notes", OVERLAY_REVIEW_NOTE)
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    return write_text(dest, text)
