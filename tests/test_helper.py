from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from helper.ability_assigner import (
    assign_focus_ability,
    empty_ability_overrides,
    load_sample_overrides,
    save_ability_overrides,
    set_existing_special,
)
from helper.building_scaffold import build_plan as build_building_plan
from helper.faction_scaffold import DEFAULT_DONORS, scaffold_faction, write_faction_pack
from helper.hero_abilities import build_hero_ability_plan
from helper.isolation import IsolationError, write_text
from helper.markdown import markdown_to_html
from helper.paths import DATA_DIR, DOCS_DIR, HELPER_ROOT, SANDBOX_DIR
from helper.presentation_lane import build_plan as build_presentation_plan
from helper.proof import diagnose
from helper.schemas import SchemaError, validate_ability_overrides, validate_faction_manifest, validate_hero_overrides, validate_presentation_plan


class IsolationTests(unittest.TestCase):
    def test_refuses_helper_root_write(self) -> None:
        with self.assertRaises(IsolationError):
            write_text(HELPER_ROOT / "not_allowed.json", "{}\n")

    def test_refuses_any_path_outside_sandbox(self) -> None:
        with self.assertRaises(IsolationError):
            write_text(Path(tempfile.gettempdir()) / "ge_helper_must_not_write.json", "{}\n")

    def test_refuses_core_zip(self) -> None:
        with self.assertRaises(IsolationError):
            write_text(Path(tempfile.gettempdir()) / "Core.zip" / "x.json", "{}\n")

    def test_allows_sandbox(self) -> None:
        path = write_text(SANDBOX_DIR / "isolation_probe.json", "{\"ok\": true}\n")
        self.assertTrue(path.is_file())
        self.assertEqual(path.parent, SANDBOX_DIR)

    def test_source_has_no_game_install_writer(self) -> None:
        forbidden = ("StreamingAssets/Core.zip",)
        roots = [HELPER_ROOT / "helper", HELPER_ROOT / "studio", HELPER_ROOT / "cli.py"]
        for root in roots:
            paths = [root] if root.is_file() else list(root.rglob("*.py"))
            for path in paths:
                text = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, text, msg=f"{path} mentions {token}")


class SchemaTests(unittest.TestCase):
    def test_sample_faction(self) -> None:
        payload = json.loads((DATA_DIR / "sample" / "faction.json").read_text(encoding="utf-8-sig"))
        validate_faction_manifest(payload)

    def test_sample_abilities(self) -> None:
        validate_ability_overrides(load_sample_overrides())

    def test_sample_heroes(self) -> None:
        payload = json.loads((DATA_DIR / "sample" / "hero_overrides.json").read_text(encoding="utf-8-sig"))
        validate_hero_overrides(payload)

    def test_rejects_localization_icon(self) -> None:
        doc = empty_ability_overrides("homm3_example")
        with self.assertRaises(SchemaError):
            assign_focus_ability(
                doc,
                unit_sid="h3_example_pikeman",
                template_id="focus_melee_buff",
                display_name="X",
                description="Y",
                energy_level=1,
                cooldown=1,
                icon_key="thing_name",
            )

    def test_rejects_mixed_presentation(self) -> None:
        with self.assertRaises(SchemaError):
            validate_presentation_plan(
                {
                    "schemaVersion": 1,
                    "unitSid": "h3_example_pikeman",
                    "battlePresentationLane": "skinned_mesh",
                    "alsoUseBattleBillboardArrays": True,
                }
            )


class AssignerTests(unittest.TestCase):
    def test_assign_and_save(self) -> None:
        doc = load_sample_overrides()
        card = assign_focus_ability(
            doc,
            unit_sid="h3_example_archer",
            template_id="focus_ranged_shot",
            display_name="Focus Shot",
            description="Spend 2 Focus to fire.",
            energy_level=2,
            cooldown=2,
            icon_key="assassin_buff_icon",
        )
        self.assertEqual(card["energyLevel"], 2)
        path = save_ability_overrides(doc, SANDBOX_DIR / "ability_overrides_homm3_example.json")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        validate_ability_overrides(loaded)
        self.assertEqual(loaded["kitMeta"]["fileKind"], "overlay-review")

    def test_melee_buff_requires_live_buff_sid(self) -> None:
        doc = empty_ability_overrides("homm3_example")
        with self.assertRaises(SchemaError) as raised:
            assign_focus_ability(
                doc,
                unit_sid="h3_example_pikeman",
                template_id="focus_melee_buff",
                display_name="Weakening Strike",
                description="Spend 2 Focus to strike and apply Weaken Attack and Defense.",
                energy_level=2,
                cooldown=2,
            )
        self.assertIn("buffSid", str(raised.exception))

    def test_refuses_stun_tooltip_with_weaken_buff(self) -> None:
        doc = empty_ability_overrides("homm3_example")
        with self.assertRaises(SchemaError) as raised:
            assign_focus_ability(
                doc,
                unit_sid="h3_example_pikeman",
                template_id="focus_melee_buff",
                display_name="Halberd Hook",
                description="Spend 2 Focus to stun.",
                energy_level=2,
                cooldown=2,
                buff_sid="magic_shorten_shadow_effect_1",
            )
        self.assertIn("Weaken", str(raised.exception))

    def test_melee_buff_accepts_matching_weaken_text(self) -> None:
        doc = empty_ability_overrides("homm3_example")
        card = assign_focus_ability(
            doc,
            unit_sid="h3_example_pikeman",
            template_id="focus_melee_buff",
            display_name="Weakening Strike",
            description="Spend 2 Focus to strike and apply Weaken Attack and Defense.",
            energy_level=2,
            cooldown=2,
            buff_sid="magic_shorten_shadow_effect_1",
        )
        self.assertEqual(card["buffSid"], "magic_shorten_shadow_effect_1")

    def test_existing_special(self) -> None:
        doc = load_sample_overrides()
        special = set_existing_special(
            doc,
            unit_sid="h3_example_pikeman_upg",
            slot_kind="abilities",
            index=0,
            enabled=True,
            name_text="Copied special retune",
            description_text="Spend 2 Focus in melee range to use the copied native special.",
            energy_level=2,
            cooldown=2,
            icon_key="assassin_buff_icon",
            effect_key="assassin_ability_2_name",
        )
        self.assertTrue(special["enabled"])
        save_ability_overrides(doc, SANDBOX_DIR / "ability_overrides_homm3_example.json")


class ScaffoldTests(unittest.TestCase):
    def test_golden_era_donor_examples_are_not_homm3_guesses(self) -> None:
        self.assertEqual(DEFAULT_DONORS["tower"]["donorFactionSid"], "humans")
        self.assertEqual(DEFAULT_DONORS["tower"]["nativeBiome"], "Tundra")
        self.assertEqual(DEFAULT_DONORS["inferno"]["donorFactionSid"], "demons")
        self.assertEqual(DEFAULT_DONORS["inferno"]["nativeBiome"], "Molten")
        self.assertEqual(DEFAULT_DONORS["stronghold"]["donorFactionSid"], "dungeon")
        self.assertEqual(DEFAULT_DONORS["stronghold"]["nativeBiome"], "Wasteland")
        self.assertEqual(DEFAULT_DONORS["rampart"]["nativeBiome"], "Hills")
        self.assertNotEqual(DEFAULT_DONORS["tower"]["nativeBiome"], "Snow")
        self.assertNotIn("orc", DEFAULT_DONORS["stronghold"]["donorFactionSid"])

    def test_faction_pack(self) -> None:
        manifest = scaffold_faction(short_name="helpertest", display_name="Helper Test", donor_key="castle")
        written = write_faction_pack(manifest)
        self.assertIn("faction.json", written)
        payload = json.loads(Path(written["faction.json"]).read_text(encoding="utf-8"))
        self.assertEqual(payload["kitMeta"]["fileKind"], "overlay-review")
        self.assertEqual(payload["identity"]["donorFactionSid"], "humans")
        self.assertEqual(payload["unitLines"][0]["donorBaseSid"], "esquire")
        checklist = Path(written["CHECKLIST.md"])
        self.assertTrue(checklist.is_file())
        self.assertIn("owned Unity city world", checklist.read_text(encoding="utf-8"))

    def test_tower_scaffold_uses_human_tundra(self) -> None:
        manifest = scaffold_faction(short_name="towertest", display_name="Tower Test", donor_key="tower")
        self.assertEqual(manifest["identity"]["donorFactionSid"], "humans")
        self.assertEqual(manifest["identity"]["nativeBiome"], "Tundra")
        self.assertEqual(manifest["unitLines"][0]["donorBaseSid"], "esquire")
        self.assertNotEqual(manifest["identity"]["donorCitySid"], "dungeon_city")

    def test_inferno_placeholder_is_not_esquire(self) -> None:
        manifest = scaffold_faction(short_name="infernoth", display_name="Inferno Test", donor_key="inferno")
        self.assertEqual(manifest["unitLines"][0]["donorBaseSid"], "trick_demon")
        self.assertEqual(manifest["identity"]["donorFactionSid"], "demons")

    def test_presentation_and_buildings_and_hero(self) -> None:
        present = build_presentation_plan(
            unit_sid="h3_example_pikeman",
            lane="billboard",
            donor_base_sid="esquire",
        )
        self.assertEqual(present["battlePresentationLane"], "billboard")
        buildings = build_building_plan(faction_sid="homm3_example")
        self.assertEqual(buildings["townParadigm"], "owned_city_world")
        treasury = next(row for row in buildings["buildings"] if row["nativeSid"] == "Build_Treasury")
        self.assertEqual(treasury["displayName"], "Treasury")
        self.assertEqual(treasury["typicalPortRename"], "Blacksmith")
        hero = build_hero_ability_plan(
            hero_sid="homm3_example_hero_1",
            class_type="might",
            extra_ability_sids=["homm3_example_warcry"],
        )
        self.assertEqual(hero["grants"][0]["parameters"][0], "skill_warrior_ability")
        self.assertEqual(hero["grants"][-1]["parameters"][0], "homm3_example_warcry")
        from helper.law_scaffold import build_law_doc, save_law_doc

        law = build_law_doc(
            faction_sid="homm3_example",
            law_sid="homm3_example_growth",
            name_text="Example Growth",
            description_text="Native growth example.",
            effect_type="cityUnitsIncrement",
            parameters=["h3_example_pikeman", "1"],
        )
        self.assertTrue(Path(save_law_doc(law)).is_file())


class DocsTests(unittest.TestCase):
    def test_index_files_exist(self) -> None:
        index = json.loads((DATA_DIR / "components_index.json").read_text(encoding="utf-8-sig"))
        for row in index:
            path = DOCS_DIR / row["file"]
            self.assertTrue(path.is_file(), msg=row["file"])
            self.assertGreater(path.stat().st_size, 200)
        names = {row["id"] for row in index}
        self.assertIn("glossary", names)
        self.assertIn("tools", names)
        glossary = (DOCS_DIR / "20_glossary.md").read_text(encoding="utf-8")
        self.assertIn("Golden Era** is a **mod**", glossary)
        self.assertIn("it means Olden Era", glossary)
        self.assertIn("overlay-review", glossary)
        self.assertIn("magic_shorten_shadow_effect_1", glossary)
        self.assertNotIn("specific installed build of that game", glossary)
        self.assertNotIn("the Golden Era PC build", glossary)
        tools = (DOCS_DIR / "21_tools.md").read_text(encoding="utf-8")
        self.assertIn("Human/`Tundra`", tools)
        self.assertNotIn("Spend 2 Focus to stun.", tools)
        self.assertNotIn("GitHub Wiki", tools)
        self.assertNotIn("packer you own", tools)
        faction_doc = (DOCS_DIR / "04_custom_faction.md").read_text(encoding="utf-8")
        self.assertIn("| tower | humans | human_city | Tundra |", faction_doc)
        self.assertNotIn("orc_city", faction_doc)

    def test_markdown_tables(self) -> None:
        html = markdown_to_html("# Title\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n")
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<table>", html)

    def test_silent_miss(self) -> None:
        row = diagnose("nonempty_miss")
        self.assertIn("TryGetValue", row["prompt"])

    def test_pages_build(self) -> None:
        from helper.build_pages import SITE_URL, build_site

        with tempfile.TemporaryDirectory() as raw:
            dest = build_site(Path(raw) / "site")
            index = dest / "index.html"
            tools = dest / "21_tools.html"
            glossary_alias = dest / "glossary.html"
            self.assertTrue(index.is_file())
            self.assertTrue(tools.is_file())
            self.assertTrue(glossary_alias.is_file())
            text = index.read_text(encoding="utf-8")
            self.assertIn("20_glossary.html", text)
            self.assertIn(SITE_URL, text)
            self.assertNotIn("GitHub Wiki", text)
            self.assertNotIn("That product is called", text)
            self.assertNotIn("packer you own", text)
            writers = dest / "writers.html"
            self.assertTrue(writers.is_file())
            writers_text = writers.read_text(encoding="utf-8")
            self.assertNotIn("GitHub Wiki", writers_text)
            self.assertNotIn("packer you own", writers_text)
            self.assertTrue((dest / ".nojekyll").is_file())
            self.assertTrue((dest / "styles.css").is_file())
            hooks = (dest / "hooks.html").read_text(encoding="utf-8")
            self.assertIn("Hook catalog", hooks)
            self.assertIn("not a public API", hooks)

    def test_hook_catalog(self) -> None:
        catalog = json.loads((DATA_DIR / "hook_catalog.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(catalog["schemaVersion"], 1)
        self.assertGreaterEqual(len(catalog["families"]), 10)
        blob = json.dumps(catalog)
        self.assertNotIn("Homm3CustomUiIconHook", blob)
        self.assertIn("not a public API", catalog["proof"])


if __name__ == "__main__":
    unittest.main()
