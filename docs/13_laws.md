# Component: Faction laws

This component is **the law tree**. Elite Strategem-style spellbook toggles are **not** law rows.

## Intent

Ship faction laws as native Core bonus primitives whenever that preserves identity.

Typical primitives: `unitStat`, `heroStat`, `sideRes`, `cityUnitsIncrement`, `battleSubskillBonus`, construction/astrology primitives.

## Default product

Native-data replacement. Clone a live law row shape, then change ids and parameters.

Faction-locked donor laws (heroStat that names another faction, battleSubskill to another faction’s subskills) must be redesigned. Copying them will point at missing keys or steal vanilla identity.

## Hook-required laws

If the table cannot say “when X happens, do Y,” you need a runtime. Keep it behind an explicit packet/proof gate. A CSV mentioning an effect is not permission to mutate combat.

Do not register a committed-damage Harmony mutator and a Direct State damage adapter as dual owners.

`Homm3TrainingDamageLawRuntime`-style prefixes stay inert until the gate and a single registration owner say otherwise. `NOT_ATTEMPTED` in a startup audit is expected, not a secret on-switch.

## Icons

Law icons may be creature SIDs (`h3_pikeman`) as well as `fraction_law_*_icon` keys. Your icon browser should resolve both.

## Editor rule

Do not give creators only a raw JSON textarea for law effects. If a bonus shape cannot round-trip through structured controls, extend the controls.

This helper’s sandbox `law_overrides.json` is an empty shell plus docs. The Focus assigner is the fully rebuilt GUI; laws remain documented and scaffolded so they stay uncoupled.
