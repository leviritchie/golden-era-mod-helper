"""Author a native-data law row in the sandbox. Not a Harmony mutator."""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .schemas import require_sid

NATIVE_EFFECT_TYPES = (
    "unitStat",
    "heroStat",
    "sideRes",
    "cityUnitsIncrement",
    "battleSubskillBonus",
)


def build_law_doc(
    *,
    faction_sid: str,
    law_sid: str,
    name_text: str,
    description_text: str,
    effect_type: str,
    parameters: list[str],
) -> dict[str, Any]:
    require_sid(faction_sid, "faction_sid")
    require_sid(law_sid, "law_sid")
    if effect_type not in NATIVE_EFFECT_TYPES:
        raise ValueError(
            f"effect_type must be a native primitive {NATIVE_EFFECT_TYPES}, not {effect_type!r}. "
            "Hook-required laws are a different component and stay behind a proof gate."
        )
    if not parameters:
        raise ValueError("parameters must copy a live Core example, not an empty list")
    return {
        "schemaVersion": 1,
        "factionSid": faction_sid,
        "notes": "Native-data law sandbox file. Not packed into Core.zip by this helper.",
        "lawOverrides": {
            law_sid: {
                "enabled": True,
                "nameText": name_text,
                "descriptionText": description_text,
                "effects": [{"type": effect_type, "parameters": parameters}],
            }
        },
    }


def save_law_doc(doc: dict[str, Any]) -> str:
    path = sandbox_join(f"law_overrides_{doc['factionSid']}.json")
    write_text(path, json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    return str(path)
