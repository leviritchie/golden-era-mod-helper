# Component: Custom Focus abilities

This component is **creature actives** (and the utility that assigns them). It is not hero commander attacks.

## Intent

Give a unit a battle button that spends **Focus**, has a cooldown, and runs a native-shaped effect.

In Core JSON:

- Focus cost = `energyLevel`
- Cooldown = `cd` (overrides often use `cooldown`)
- Rank / charges are native fields when the donor uses them

Combat Focus pips are native UI children on the ability view. On one Golden Era pin that container was `BhAbilityViewBase.energyContainer`. Re-pin. If your overlay sprite sits on top of those children, pips vanish even when the cost is correct.

## Authoring model

Do not start by inventing Direct State mid-damage behavior.

Preferred order:

1. **Copy a live donor unit special** (`effectKind: unit-special` / copied special template), including alternate attacks.
2. **Native template**: melee+buff, ranged shot, heal_percent, spell-effect wrapper.
3. **Disable or retune an existing slot** (`existingSpecials`) without replacing the mechanic: text, icon, Focus, cooldown, rank.
4. Only then a plugin law/runtime, packet-gated.

Empty `effectKey` with `enabled: false` is a deliberate disable. Do not “helpfully” invent a mechanic.

## Logic and view must match

Every active you add to logic needs a view row (name, icon, animation index). Array length mismatches crash native ability Init.

## Text and icons

- `nameText` / `descriptionText` are for humans.
- `nameKey` / `descriptionKey` are localization tokens.
- `iconKey` is a **runtime sprite key**. Illegal: `*_name`, `*_description`, `Orientation@4x`.
- If a vanilla key is not in the serialized sprite registry, your plugin must allowlist that exact key. Do not open the resolver to arbitrary strings.

Player-facing text must describe the shipped effect. Probability-on-hit HoMM3 traits are often converted to guaranteed Focus actives in Olden Era design notes. If you do that, say so in the tooltip honestly.

## Action bar runtime

Custom actives need the selected-unit HUD to see the current unit SID and to bind clicks and number keys. Number keys go through a `HotkeyAbilityArgs` handler. A standalone `Input.GetKeyDown` poll is a second owner. Do not add it.

On the release path, overlay custom icons. Do not write into native `pics` images that later vanilla binds reuse.

## Branch metadata

Keep design fields that your packer expects, even if Core does not store them:

- `branchRole` (base-line / standard-upgrade / alternate)
- `sourceMechanicId`
- `decisionTest`

Validators that strip unknown-but-owned fields will destroy your review notes.

## Focus assigner

Studio → Focus ability assigner. Field-by-field help: [21_tools.md](21_tools.md).

The assigner writes overlay-review `ability_overrides` JSON: templates, existing specials, Focus, cooldown, icons. Output lands in `sandbox/`.

CLI (run from the folder that contains `cli.py`):

```text
python cli.py assign-focus --faction-sid homm3_example --unit-sid h3_example_pikeman_upg --template focus_melee_buff --name "Weakening Strike" --description "Spend 2 Focus to strike and apply Weaken Attack and Defense." --focus-cost 2 --cooldown 2 --buff-sid magic_shorten_shadow_effect_1 --from-sample
```

```text
python cli.py edit-existing-special --faction-sid homm3_example --unit-sid h3_example_pikeman_upg --name "Copied special retune" --description "Spend 2 Focus in melee range to use the copied native special." --focus-cost 2 --cooldown 2 --icon-key assassin_buff_icon --from-sample --enabled
```

Output: `sandbox/ability_overrides_<faction>.json` (overlay-review JSON, not a Core row).

A Core overlay packer in a separate project is what later turns that file into `units_logics` / `units_views`. This helper does not pack. Tooltip text must match the buff SID. `magic_shorten_shadow_effect_1` is Weaken Attack/Defense, not stun.

## Hire UI NREs

A missing or wrong buff SID in Core produces a null BuffConfig. Hire/ability UI then NRE. That is a Core identity bug, not missing art. Validate buff SIDs before blaming bundles.
