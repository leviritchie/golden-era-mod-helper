"""Proof-tier labels used by Golden Era work. Teaching copy, not a gameplay claim."""

from __future__ import annotations

from typing import Any

TIERS = [
    {
        "id": "source_static",
        "label": "source / static validated",
        "means": "The file, schema, or decomp pin exists in the worktree and a validator or named dump supports it.",
        "doesNotMean": "The game loaded it, or a player saw it.",
    },
    {
        "id": "generated",
        "label": "generated artifact validated",
        "means": "A generator wrote the row, bundle, or report, and a gate checked that output.",
        "doesNotMean": "The installed game is using that output.",
    },
    {
        "id": "build_target",
        "label": "build target proven",
        "means": "The plugin or Unity target compiled against the intended interop profile.",
        "doesNotMean": "The DLL in the live install is that build.",
    },
    {
        "id": "deployed",
        "label": "deployed or installed payload proven",
        "means": "The live Core.zip, plugin folder, or bundle was read back from the install.",
        "doesNotMean": "Startup succeeded, or combat behaved.",
    },
    {
        "id": "startup_smoke",
        "label": "startup smoke proven",
        "means": "The process launched and required hooks logged REGISTERED (or an equivalent exact success line).",
        "doesNotMean": "The feature presented in battle or town.",
    },
    {
        "id": "runtime",
        "label": "runtime behavior proven",
        "means": "A live probe, log, or bridge capture shows the mutation or bind actually ran.",
        "doesNotMean": "A player-facing screen looked correct.",
    },
    {
        "id": "user_visible",
        "label": "user-visible gameplay proven",
        "means": "A person saw the intended town, battle, map, or UI result on the live install.",
        "doesNotMean": "Nothing. This is the top of the ladder.",
    },
]

SILENT_MISS_QUESTIONS = [
    {
        "id": "nonempty_miss",
        "prompt": "The plan or dictionary has items, but TryGetValue still misses.",
        "diagnosis": "Store key is not the retrieve key. Pin the live Harmony argument type against the map key type. Bridge wrappers (for example the Unit.Init side wrapper versus TransferSide) before lookup. A miss against a non-empty map is a failed check, not 'no plan'.",
    },
    {
        "id": "proxy_identity",
        "prompt": "Types already match, the map is non-empty, and managed GetHashCode or ReferenceEquals still misses.",
        "diagnosis": "Il2Cpp re-wrapped the same native object into a new managed proxy. Key by native pointer, not managed identity. Matching native keys mean the same native object. Distinct native keys mean different objects or the wrong owner.",
    },
    {
        "id": "foreach_empty",
        "prompt": "Another layer shows items, but a managed foreach looks empty or throws.",
        "diagnosis": "Verify the collection API. Prefer Count plus indexer on Il2Cpp lists when foreach has lied.",
    },
    {
        "id": "planned_not_applied",
        "prompt": "Logs say planned or registered, then the later apply hook sees an empty map.",
        "diagnosis": "Producer-to-consumer window. Do not clear state in an earlier postfix than apply. Keep the plan until every consumer has run, or own apply on one shared registration surface. BattleLogic.Init also runs during adventure-map Loader; do not throw fail-closed from optional pilots there.",
    },
    {
        "id": "wrong_proof",
        "prompt": "A log line says stored, planned, or verified, and you want to call the feature done.",
        "diagnosis": "That is not user-visible gameplay. Label the claim at the tier you actually have.",
    },
    {
        "id": "quest_and",
        "prompt": "A map visit fires but a quest dialog never shows, and the trigger ANDs visit with Counter or ItemOwnSide.",
        "diagnosis": "Olden Era conditions are event latches, not state polls. Keep each trigger on one event family.",
    },
    {
        "id": "billboard_suppress",
        "prompt": "An artifact or other map billboard logs applied but stays invisible.",
        "diagnosis": "A town donor suppressor can force-disable child renderers when the SID is mistaken for a city SID. Mark non-town billboards correctly and copy the donor child layer onto the quad.",
    },
]


def diagnose(question_id: str) -> dict[str, Any]:
    for row in SILENT_MISS_QUESTIONS:
        if row["id"] == question_id:
            return row
    raise KeyError(f"unknown silent-miss question: {question_id}")
