"""Choose a unit presentation lane without mixing owners."""

from __future__ import annotations

import json
from typing import Any

from .isolation import sandbox_join, write_text
from .kit_meta import OVERLAY_REVIEW_NOTE, overlay_review_meta
from .schemas import require_sid, validate_presentation_plan

LANE_HELP = {
    "billboard": {
        "title": "Battle and map billboards",
        "summary": (
            "The unit stays a camera-facing sprite sheet (Texture2DArray in battle, "
            "a sanitized Hex/Lit quad on the adventure map). Core UnitView mesh "
            "fields stay on a native donor prefab so construction cannot miss a "
            "custom path. A runtime hook hides the donor visual and shows yours."
        ),
        "useWhen": [
            "You have HoMM3 DEF frames and want the classic 2D look.",
            "You do not have a rigged 3D mesh with battle clips.",
            "You need a shippable visual before a skinned mesh is ready.",
        ],
        "doNot": [
            "Point UnitView.mesh at a custom homm3_import path unless the native loader already understands it.",
            "Clone a town/building Hex/Lit material onto a unit quad without sanitizing terrain blend and wave state.",
            "Assume a battle billboard fix also repaired map, preview, portrait, or town art.",
        ],
        "requiredHooks": [
            "Your battle visual replacement hook after native construction",
            "Adventure-map billboard finish (skip this if the unit later moves to skinned_mesh)",
            "Portrait / preview hooks as separate surfaces",
        ],
    },
    "skinned_mesh": {
        "title": "Owned skinned mesh",
        "summary": (
            "The unit is a Unity skinned mesh with bone clips. Battle, unit preview, "
            "and adventure map all use that mesh. The bundle must omit battle "
            "billboard arrays. Mixing a skinned-only pack over a billboard bundle "
            "removes battle.prefab and combat Init null-dereferences."
        ),
        "useWhen": [
            "You have an owned bind skeleton and authored clips.",
            "You want 3D lighting, facing, and mesh FX (fire, sparks) in combat.",
        ],
        "doNot": [
            "Keep battle Texture2DArray / billboard materials in the same combat bundle.",
            "Copy donor localScale onto a Meshy-sized mesh.",
            "Time-stretch clips to a stock Esquire idle length.",
            "Treat physics smoothing as ship readiness.",
            "Flip side-facing as a first fix; check the GLB yaw bake first.",
        ],
        "requiredHooks": [
            "Skinned battle-lane marker recognition",
            "Cache-only battle presentation template on combat Init",
            "Preview factory may use a shorter catalog id than the gameplay SID; copy the live preview id",
            "Idle loop on the adventure-map visual",
        ],
    },
    "depth_billboard_experiment": {
        "title": "Depth billboard (experiment only)",
        "summary": (
            "The unit remains a camera-facing billboard, but opaque pixels are "
            "displaced by a Video Depth Anything map. This is not the product 3D "
            "creature lane and must not replace skinned_mesh."
        ),
        "useWhen": [
            "You are experimenting with 2.5D relief on an existing sprite clip.",
        ],
        "doNot": [
            "Retarget skinned bone clips onto this displaced quad.",
            "Ship it as the faction's combat visual owner.",
            "Turn it on without a packed depth Texture2DArray; the shader must fail closed to the flat billboard.",
        ],
        "requiredHooks": [
            "Optional array-depth shader swap, flag-gated",
            "Existing battle array billboard frame driver",
        ],
    },
}


def recommend_lane(
    *,
    has_def_frames: bool,
    has_owned_rig_and_clips: bool,
    wants_true_3d: bool,
    experimenting_with_depth: bool,
) -> str:
    if wants_true_3d and has_owned_rig_and_clips:
        return "skinned_mesh"
    if experimenting_with_depth and has_def_frames:
        return "depth_billboard_experiment"
    if has_def_frames:
        return "billboard"
    if has_owned_rig_and_clips:
        return "skinned_mesh"
    raise ValueError(
        "No presentation lane fits. You need either decoded DEF frames (billboard) "
        "or an owned rig plus clips (skinned_mesh)."
    )


def build_plan(
    *,
    unit_sid: str,
    lane: str,
    donor_base_sid: str,
    notes: str = "",
) -> dict[str, Any]:
    require_sid(unit_sid, "unit_sid")
    require_sid(donor_base_sid, "donor_base_sid")
    if lane not in LANE_HELP:
        raise ValueError(f"unknown lane {lane!r}")
    help_block = LANE_HELP[lane]
    plan = {
        "schemaVersion": 1,
        "unitSid": unit_sid,
        "donorBaseSid": donor_base_sid,
        "battlePresentationLane": lane,
        "alsoUseBattleBillboardArrays": False if lane == "skinned_mesh" else True,
        "keepNativeSafeDonorMeshFields": True,
        "independentSurfaces": [
            "battle",
            "adventure_map",
            "unit_preview",
            "hire_portrait",
            "timeline_portrait",
            "tooltip",
            "sounds",
        ],
        "title": help_block["title"],
        "summary": help_block["summary"],
        "useWhen": help_block["useWhen"],
        "doNot": help_block["doNot"],
        "requiredHooks": help_block["requiredHooks"],
        "kitMeta": overlay_review_meta("presentation_lane"),
        "notes": notes or OVERLAY_REVIEW_NOTE,
    }
    validate_presentation_plan(plan)
    return plan


def save_plan(plan: dict[str, Any]) -> str:
    validate_presentation_plan(plan)
    path = sandbox_join(f"presentation_{plan['unitSid']}.json")
    write_text(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    return str(path)
