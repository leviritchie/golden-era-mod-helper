"""Author hero battle abilities as uncoupled grants.

Stock commander attacks (Heroic Strike / mage blast) are Core rows.
Extra buttons are additional heroBattleAbility grants.
"""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .kit_meta import OVERLAY_REVIEW_NOTE, overlay_review_meta
from .schemas import require_sid

WARRIOR_ABILITY_SID = "skill_warrior_ability"
MAGE_ABILITY_SID = "skill_mage_ability"
SIEGE_ABILITY_SID = "attack_siege_ability"

STOCK_COMMANDER = {
    WARRIOR_ABILITY_SID: {
        "playerName": "Heroic Strike (might commander attack)",
        "classType": "might",
        "damageModel": "absolute_damage",
        "ignoresOffenceAndDefence": True,
        "scriptSum": ["offence", "defence", "spellPower", "intelligence"],
        "notClassicAttackDefenseGap": True,
        "coreRow": "DB/heroes_abilities/heroes_abilities_base/hero_abilities.json",
        "script": "DB/info/info_hero_ability/hero_ability.script",
        "specializationDeltas": [
            "specializations_skill_warrior_ability_base_bonus",
            "specializations_skill_warrior_ability_level_bonus",
        ],
    },
    MAGE_ABILITY_SID: {
        "playerName": "Mage commander attack",
        "classType": "magic",
        "damageModel": "absolute_damage",
        "ignoresOffenceAndDefence": True,
        "scriptSum": ["offence", "defence", "spellPower", "intelligence"],
        "presentation": "projectile / magic VFX, not a melee slash",
        "notASpellbookSpell": True,
        "coreRow": "DB/heroes_abilities/heroes_abilities_base/hero_abilities.json",
        "specializationDeltas": [
            "specializations_skill_mage_ability_base_bonus",
            "specializations_skill_mage_ability_level_bonus",
        ],
    },
}


def commander_grant(class_type: str) -> dict[str, Any]:
    if class_type not in ("might", "magic"):
        raise ValueError("class_type must be 'might' or 'magic'")
    sid = MAGE_ABILITY_SID if class_type == "magic" else WARRIOR_ABILITY_SID
    return {"type": "heroBattleAbility", "parameters": [sid, "0"]}


def siege_grant() -> dict[str, Any]:
    return {
        "type": "heroBattleAbility",
        "battleType": "forCity",
        "receiverRole": "attacker",
        "parameters": [SIEGE_ABILITY_SID, "0"],
    }


def extra_action_grant(ability_sid: str) -> dict[str, Any]:
    return {"type": "heroBattleAbility", "parameters": [require_sid(ability_sid, "ability_sid"), "0"]}


def build_hero_ability_plan(
    *,
    hero_sid: str,
    class_type: str,
    extra_ability_sids: list[str] | None = None,
    replace_commander: bool = False,
    replacement_ability_sid: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    require_sid(hero_sid, "hero_sid")
    grants = [commander_grant(class_type), siege_grant()]
    extras = extra_ability_sids or []
    if replace_commander:
        if not replacement_ability_sid:
            raise ValueError("replace_commander requires replacement_ability_sid")
        grants[0] = extra_action_grant(replacement_ability_sid)
    for sid in extras:
        grants.append(extra_action_grant(sid))
    plan = {
        "schemaVersion": 1,
        "heroSid": hero_sid,
        "classType": class_type,
        "replaceCommander": replace_commander,
        "stockCommander": STOCK_COMMANDER[MAGE_ABILITY_SID if class_type == "magic" else WARRIOR_ABILITY_SID],
        "grants": grants,
        "warnings": [
            "Do not assume Attack minus Defense controls Heroic Strike. Stock rows ignore both.",
            "Extra actions are additional buttons. Overwriting the commander slot is a different design.",
            "Icon caches that report success with zero loaded rows are a failure, not a skip.",
            "Might and magic share some English name tokens in stock Core. Fork tokens if the text must differ.",
        ],
        "uiHooksOftenRequired": [
            "Custom hero-ability icon cache (generated Core icon rows + plugin PNG payload)",
            "Warcry-style bind surfaces if the extra action is a faction shout",
        ],
        "kitMeta": overlay_review_meta("hero_abilities"),
        "notes": notes or OVERLAY_REVIEW_NOTE,
    }
    return plan


def save_plan(plan: dict[str, Any]) -> str:
    path = sandbox_join(f"hero_abilities_{plan['heroSid']}.json")
    write_text(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    return str(path)
