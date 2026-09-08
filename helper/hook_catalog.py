"""Load the creator-facing Harmony / Core / Direct State hook catalog."""

from __future__ import annotations

import json
from typing import Any

from .paths import DATA_DIR


def load_catalog() -> dict[str, Any]:
    path = DATA_DIR / "hook_catalog.json"
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schemaVersion") != 1:
        raise ValueError("hook_catalog.json schemaVersion must be 1")
    return payload


def families() -> list[dict[str, Any]]:
    return list(load_catalog().get("families") or [])


def search_hooks(query: str) -> list[dict[str, Any]]:
    needle = query.strip().lower()
    hits: list[dict[str, Any]] = []
    for family in families():
        blob = json.dumps(family, ensure_ascii=False).lower()
        if needle in blob:
            hits.append(family)
            continue
        for hook in family.get("hooks") or []:
            hook_blob = json.dumps(hook, ensure_ascii=False).lower()
            if needle in hook_blob:
                row = dict(hook)
                row["familyId"] = family.get("id")
                row["familyTitle"] = family.get("title")
                hits.append(row)
    return hits


def family_by_component(component_id: str) -> list[dict[str, Any]]:
    return [family for family in families() if component_id in (family.get("components") or [])]
