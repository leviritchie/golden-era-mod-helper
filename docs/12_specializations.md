# Component: Hero specializations

This component is **specialty bonus rows**. It is not the commander-attack damage script.

## Intent

Author a hero specialty the overlay will accept into `DB/heroes_specializations`.

## Supported specialty types

These are the types the Golden Era mod’s cleaner keeps. Use the same list unless you have a reason to support more:

- `unitStat` — army combat scalars (`modifierSet`, `outDmgMods`, …)
- `heroStat` / `heroStatBattle`
- `cityUnitsIncrement` — growth specialists
- `sideRes` — resource specialists
- `battleSubskillBonus` — stacks onto hero ability info deltas (Heroic Strike / mage twins)
- `heroMagicReplace` — masterful spell specialists; keep ownership in the override file, not a silent post-pass

`heroBattleAbility` is usually **common machinery** (warrior/mage commander + siege + extras), not a free-form specialty toy. Know which layer you are editing.

Unknown `type` strings should raise, not drop on the floor.

## Class split

Might heroes get `skill_warrior_ability` in common grants. Magic heroes get `skill_mage_ability`. Editing only warrior specialization deltas will not scale mage heroes.

## Text

Specialty description should match the bonus rows you actually emit. Empty bonus arrays with flavor text are audit debt.

## Helper

Sample hero overrides live in `data/sample/hero_overrides.json`. The studio does not yet include a full specialty-row GUI; author JSON in the sandbox and validate with `helper.schemas.validate_hero_overrides`.
