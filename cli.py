"""Command-line entry for the Olden Era mod helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helper.ability_assigner import (  # noqa: E402
    assign_focus_ability,
    empty_ability_overrides,
    load_sample_overrides,
    load_templates,
    save_ability_overrides,
    set_existing_special,
)
from helper.building_scaffold import build_plan as build_building_plan
from helper.building_scaffold import save_plan as save_building_plan
from helper.faction_scaffold import donor_key_help, scaffold_faction, write_faction_pack
from helper.hero_abilities import build_hero_ability_plan, save_plan as save_hero_plan
from helper.isolation import IsolationError, sandbox_join
from helper.law_scaffold import build_law_doc, save_law_doc
from helper.presentation_lane import build_plan as build_presentation_plan
from helper.presentation_lane import recommend_lane, save_plan as save_presentation_plan
from helper.schemas import SchemaError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Olden Era mod helper (examples from how the Golden Era mod was made). "
            "Run this from the folder that contains cli.py. "
            "Every writer saves only under ./sandbox in the local repository. "
            "This does not install files into Olden Era or install Golden Era. "
            "Read docs/20_glossary.md and docs/21_tools.md before the first command."
        )
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    studio = sub.add_parser(
        "studio",
        help="Start a local website (http://127.0.0.1:8777) with docs and forms. Does not install a mod.",
    )
    studio.add_argument("--port", type=int, default=8777, help="Local TCP port. Default 8777.")
    studio.add_argument("--host", default="127.0.0.1", help="Bind address. Keep 127.0.0.1 unless you need LAN access.")

    tests = sub.add_parser(
        "test",
        help="Run isolation and schema tests. Proves writers cannot save outside sandbox/. Does not launch the game.",
    )

    faction = sub.add_parser(
        "scaffold-faction",
        help="Write a starter faction pack (identity JSON, empty overrides, CHECKLIST.md) into sandbox/.",
    )
    faction.add_argument("--short-name", required=True, help="Becomes homm3_<name> if you omit the homm3_ prefix. Example: example")
    faction.add_argument("--display-name", required=True, help="Human label, for example Example")
    faction.add_argument(
        "--donor",
        required=True,
        help=(
            "Example donor family from the Golden Era mod (not a HoMM3-name lookup). "
            f"Keys: {donor_key_help()}. Tower in that example is Human/Tundra, not Dungeon."
        ),
    )
    faction.add_argument(
        "--biome",
        help="Optional biome string copied from live Core. If omitted, the Golden Era example for that donor key is used (Hills for rampart, Tundra for tower, …). Do not guess Snow/Rough/Water from HoMM3.",
    )

    ability = sub.add_parser(
        "assign-focus",
        help="Append a Focus-ability template onto a unit override JSON in sandbox/. Focus cost is --focus-cost (JSON field energyLevel).",
    )
    ability.add_argument("--faction-sid", required=True, help="Faction machine id, for example homm3_example")
    ability.add_argument("--unit-sid", required=True, help="Creature machine id, for example h3_example_pikeman_upg")
    ability.add_argument("--template", required=True, help="Template id from: python cli.py templates")
    ability.add_argument("--name", required=True, help="Player-facing ability name")
    ability.add_argument("--description", required=True, help="Player-facing tooltip. Describe shipped behavior only.")
    ability.add_argument("--focus-cost", type=int, required=True, help="Focus spent. Written as JSON energyLevel.")
    ability.add_argument("--cooldown", type=int, required=True, help="Rounds before the action can be used again")
    ability.add_argument("--rank", type=int, default=1, help="Native rank field. Default 1.")
    ability.add_argument("--icon-key", default="", help="Runtime sprite key already in the live registry, or a key your plugin allowlists. Not a _name token. Not Orientation@4x.")
    ability.add_argument("--buff-sid", default="", help="Live Core buff SID. Required for focus_melee_buff and focus_stun_melee. Example Weaken SID: magic_shorten_shadow_effect_1 (not stun).")
    ability.add_argument("--unit-special-key", default="", help="Live Core unit special key. Required for copied_unit_special.")
    ability.add_argument("--source-unit-sid", default="", help="Live Core unit SID to copy the special from. Required for copied_unit_special.")
    ability.add_argument("--spell-sid", default="", help="Live Core spell SID. Required for focus_spell_effect.")
    ability.add_argument("--from-sample", action="store_true", help="Start from data/sample/ability_overrides.json")

    existing = sub.add_parser(
        "edit-existing-special",
        help="Record an edit to a unit special that already exists (enable/disable, Focus, text, icon).",
    )
    existing.add_argument("--faction-sid", required=True, help="Faction machine id")
    existing.add_argument("--unit-sid", required=True, help="Creature machine id")
    existing.add_argument("--slot", default="abilities", help="abilities, passives, or alternativeAttacks")
    existing.add_argument("--index", type=int, default=0, help="0-based slot index")
    existing.add_argument("--enabled", action="store_true", help="Turn this slot on")
    existing.add_argument("--disabled", action="store_true", help="Turn this slot off")
    existing.add_argument("--name", required=True, help="Player-facing name")
    existing.add_argument("--description", required=True, help="Player-facing tooltip")
    existing.add_argument("--focus-cost", type=int, required=True, help="Focus spent (energyLevel)")
    existing.add_argument("--cooldown", type=int, required=True, help="Cooldown in rounds")
    existing.add_argument("--icon-key", default="", help="Runtime sprite key")
    existing.add_argument("--from-sample", action="store_true", help="Start from the packaged sample file")

    present = sub.add_parser(
        "presentation",
        help="Write a plan choosing 2D billboard vs 3D skinned mesh for one unit. Does not build Unity bundles.",
    )
    present.add_argument("--unit-sid", required=True, help="Creature machine id")
    present.add_argument("--donor-base-sid", required=True, help="Vanilla unit SID whose prefab the engine can load, for example esquire")
    present.add_argument("--lane", choices=["billboard", "skinned_mesh", "depth_billboard_experiment"], help="Omit this to let the asset flags recommend a lane")
    present.add_argument("--has-def-frames", action="store_true", help="You have decoded HoMM3 DEF / sprite frames")
    present.add_argument("--has-rig", action="store_true", help="You have an owned skeleton and battle clips")
    present.add_argument("--want-3d", action="store_true", help="You want a true 3D mesh in combat")
    present.add_argument("--depth-experiment", action="store_true", help="2.5D depth billboard experiment only, not the product 3D lane")

    buildings = sub.add_parser(
        "buildings",
        help="Write a list of native town building slots (Build_Main, Build_Tier_1, ...) plus the owned-city-world rule.",
    )
    buildings.add_argument("--faction-sid", required=True, help="Faction machine id")

    hero = sub.add_parser(
        "hero-ability",
        help="Write which hero battle buttons to grant. Might vs magic selects the stock commander attack SID.",
    )
    hero.add_argument("--hero-sid", required=True, help="Hero machine id")
    hero.add_argument("--class-type", choices=["might", "magic"], required=True, help="might -> skill_warrior_ability; magic -> skill_mage_ability")
    hero.add_argument("--extra", action="append", default=[], help="Extra hero-button ability SID. Repeat the flag for more than one.")
    hero.add_argument("--replace-commander", action="store_true", help="Only if this hero should lose the stock commander attack")
    hero.add_argument("--replacement-sid", help="Required with --replace-commander")

    laws = sub.add_parser(
        "law",
        help="Write one native-data law bonus (unitStat, growth, ...). Refuses unknown effect types.",
    )
    laws.add_argument("--faction-sid", required=True, help="Faction machine id")
    laws.add_argument("--law-sid", required=True, help="Law machine id")
    laws.add_argument("--name", required=True, help="Player-facing name")
    laws.add_argument("--description", required=True, help="Player-facing description")
    laws.add_argument("--effect-type", required=True, help="unitStat, heroStat, sideRes, cityUnitsIncrement, or battleSubskillBonus")
    laws.add_argument("--parameters", required=True, help="Comma-separated tokens copied from a live Core example")

    templates = sub.add_parser("templates", help="Print Focus template ids. Use these with assign-focus --template.")

    pages = sub.add_parser(
        "pages",
        help="Build static documentation into ./site. Does not install a mod and does not write sandbox JSON.",
    )

    args = parser.parse_args(argv)
    try:
        if args.cmd == "studio":
            from studio.server import serve

            serve(args.host, args.port)
            return 0
        if args.cmd == "test":
            from tests.run_tests import run

            return run()
        if args.cmd == "templates":
            for template in load_templates():
                print(f"{template['id']}\t{template['label']}\t{template['category']}\t{template['risk']}")
            return 0
        if args.cmd == "pages":
            from helper.build_pages import build_site
            from helper.paths import HELPER_ROOT

            dest = build_site(HELPER_ROOT / "site")
            print(dest)
            return 0
        if args.cmd == "scaffold-faction":
            manifest = scaffold_faction(
                short_name=args.short_name,
                display_name=args.display_name,
                donor_key=args.donor,
                biome=args.biome,
            )
            written = write_faction_pack(manifest)
            print(json.dumps(written, indent=2))
            return 0
        if args.cmd == "assign-focus":
            doc = load_sample_overrides() if args.from_sample else empty_ability_overrides(args.faction_sid)
            if not args.from_sample:
                doc["factionSid"] = args.faction_sid
            assign_focus_ability(
                doc,
                unit_sid=args.unit_sid,
                template_id=args.template,
                display_name=args.name,
                description=args.description,
                energy_level=args.focus_cost,
                cooldown=args.cooldown,
                rank=args.rank,
                icon_key=args.icon_key,
                buff_sid=args.buff_sid,
                unit_special_key=args.unit_special_key,
                source_unit_sid=args.source_unit_sid,
                spell_sid=args.spell_sid,
            )
            dest = sandbox_join(f"ability_overrides_{args.faction_sid}.json")
            save_ability_overrides(doc, dest)
            print(dest)
            return 0
        if args.cmd == "edit-existing-special":
            if args.enabled and args.disabled:
                raise SchemaError("use only one of --enabled or --disabled")
            enabled = True if args.enabled or not args.disabled else False
            doc = load_sample_overrides() if args.from_sample else empty_ability_overrides(args.faction_sid)
            if not args.from_sample:
                doc["factionSid"] = args.faction_sid
            set_existing_special(
                doc,
                unit_sid=args.unit_sid,
                slot_kind=args.slot,
                index=args.index,
                enabled=enabled,
                name_text=args.name,
                description_text=args.description,
                energy_level=args.focus_cost,
                cooldown=args.cooldown,
                icon_key=args.icon_key,
            )
            dest = sandbox_join(f"ability_overrides_{args.faction_sid}.json")
            save_ability_overrides(doc, dest)
            print(dest)
            return 0
        if args.cmd == "presentation":
            lane = args.lane or recommend_lane(
                has_def_frames=args.has_def_frames,
                has_owned_rig_and_clips=args.has_rig,
                wants_true_3d=args.want_3d,
                experimenting_with_depth=args.depth_experiment,
            )
            plan = build_presentation_plan(
                unit_sid=args.unit_sid,
                lane=lane,
                donor_base_sid=args.donor_base_sid,
            )
            print(save_presentation_plan(plan))
            return 0
        if args.cmd == "buildings":
            plan = build_building_plan(faction_sid=args.faction_sid)
            print(save_building_plan(plan))
            return 0
        if args.cmd == "hero-ability":
            plan = build_hero_ability_plan(
                hero_sid=args.hero_sid,
                class_type=args.class_type,
                extra_ability_sids=args.extra,
                replace_commander=args.replace_commander,
                replacement_ability_sid=args.replacement_sid,
            )
            print(save_hero_plan(plan))
            return 0
        if args.cmd == "law":
            params = [part.strip() for part in args.parameters.split(",") if part.strip()]
            doc = build_law_doc(
                faction_sid=args.faction_sid,
                law_sid=args.law_sid,
                name_text=args.name,
                description_text=args.description,
                effect_type=args.effect_type,
                parameters=params,
            )
            print(save_law_doc(doc))
            return 0
    except (IsolationError, SchemaError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unhandled command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
