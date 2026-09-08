# Getting started (split the job)

If the words Core.zip, SID, Focus, or Harmony are new, read [20_glossary.md](20_glossary.md) first, then [21_tools.md](21_tools.md) so you know what each button and command actually writes.

This page is the **order of jobs** for a new custom town. It is not a promise that this kit installs anything. This kit only writes practice files into `sandbox/`.

Do not start by writing a Harmony patch. Do not start by replacing town clicks. Do not start by pointing a unit’s `mesh` field at a custom folder the game cannot load.

## What “done” means at each step

A later step is not implied by an earlier one. A JSON file on disk is not a pickable faction. A pickable faction is not a working town click. A working town click is not a working Focus button.

## Day-one order for a new faction

1. **Identity**
   - Pick SIDs (machine names) that will not collide with vanilla or another mod.
   - Pick which vanilla town family you will use as a **donor shell** (native prefabs the engine already knows).
   - Decide whether you stay on a vanilla biome string or build a full custom terrain pipeline.
   - **This kit:** Faction scaffold writes a starter pack and `CHECKLIST.md`.

2. **Core rows**
   - Faction row, city logic, **one** unit line whose logic arrays match view arrays, localization.
   - Pack into installed `Core.zip` with **your** packer. This kit does not pack.
   - **Success looks like:** the packed archive actually contains your SIDs. Opening a sandbox JSON is not this step.

3. **Selector**
   - Confirm the faction is pickable in new game / custom game.
   - If the JSON exists but the UI list does not show it, that is a serialized Unity asset / plugin job, not “more JSON.”

4. **Map objects**
   - City and one dwelling, with hire payload and tooltip text that names **your** creature, not the donor’s creature.

5. **Presentation**
   - Pick billboard (2D) or skinned_mesh (3D) for that unit. Do not mix those bundle types.
   - **This kit:** Billboard vs mesh writes a plan. You still build Unity files yourself.

6. **Focus ability**
   - Assign a native template or copied special. Test the selected-unit action bar and Focus pips.
   - **This kit:** Focus ability assigner writes review JSON. Combat will not show it until you overlay and pack.

7. **Hero**
   - Might heroes get `skill_warrior_ability`. Magic heroes get `skill_mage_ability`. Add extra buttons only after the commander button works.
   - **This kit:** Hero abilities writes a grant plan.

8. **Town world**
   - Owned city scene + native building clicks. Not posters on a UI canvas.
   - **This kit:** Buildings and town writes the native slot list and the town rule.

9. **Laws**
   - Native table primitives first (`cityUnitsIncrement`, `unitStat`, and similar).
   - **This kit:** Faction laws refuses unknown effect types.

10. **Proof**
    - Label each step honestly. Stop claiming “faction done” after step 2.
    - **This kit:** Proof labels and Silent miss doctor are read-only helpers.

## Use the widgets or the CLI

See [21_tools.md](21_tools.md) for what each form and CLI command writes, field by field.

All writes stay in `sandbox/` inside this clone.

## Connecting to a live game

That connection is **your** overlay, plugin, and install. Copy shapes from the sandbox into your pipeline. Do not point this helper at `Core.zip` as a write target. There is no switch for that, on purpose.
