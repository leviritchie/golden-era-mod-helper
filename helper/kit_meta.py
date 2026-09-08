"""Shared honesty fields for sandbox JSON.

Sandbox files are overlay-review checklists. They are not Core.zip members.
"""

from __future__ import annotations

from typing import Any

KIT_NAME = "golden-era-mod-helper"

OVERLAY_REVIEW_NOTE = (
    "Sandbox overlay-review file from this teaching kit. "
    "It is not a Core.zip row. A Core overlay packer must emit the live archive members "
    "(for creatures: units_logics and units_views with matching array lengths). "
    "This kit does not pack or install a mod. Proof: source/static only."
)

WEAKEN_EXAMPLE_BUFF_SID = "magic_shorten_shadow_effect_1"
WEAKEN_EXAMPLE_BUFF_MEANING = (
    "Live Core SID for Weaken Attack and Defense. "
    "Golden Era Weakening / Cavalier-style overlays used this id. It is not stun."
)


def overlay_review_meta(writer: str) -> dict[str, Any]:
    return {
        "kit": KIT_NAME,
        "writer": writer,
        "fileKind": "overlay-review",
        "proof": "source/static",
        "packed": False,
        "installed": False,
        "gameplayProven": False,
        "note": OVERLAY_REVIEW_NOTE,
    }
