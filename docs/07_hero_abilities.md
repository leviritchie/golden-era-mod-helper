# Component: Custom hero abilities

This component is **hero battle buttons**. It is not creature Focus abilities and it is not the spellbook.

## Two different designs

### 1. Commander attack (stock)

| Class | SID | Player-facing idea |
| --- | --- | --- |
| Might | `skill_warrior_ability` | Heroic Strike |
| Magic | `skill_mage_ability` | Mage commander blast |

Both stock rows use `absolute_damage` with `ignoreCasterOffence` and `ignoreEnemyDefence`. The info script sums offence + defence + spell power + intelligence, then applies per-level multipliers. This is **not** classic Attack minus Defense.

They share some English name tokens in stock Core. Changing one token can change both unless you fork tokens.

Magic commander attack is still a Focus hero ability. It is not a spell-school spell with mana.

Grant via specialization common bonus:

```json
{ "type": "heroBattleAbility", "parameters": ["skill_warrior_ability", "0"] }
```

Siege attack is a separate common grant (`attack_siege_ability` with `battleType: forCity`).

### 2. Extra actions

Warcry, Gating, Avenger, Arcane Battery, Elite Strategem, and similar are **additional** `heroBattleAbility` rows. Do not overwrite the commander slot unless the design is explicitly “this hero no longer has Heroic Strike.”

Each extra action still needs:

- a Core ability row
- a grant on skill/specialization/subskill
- icons (generated Core icon keys + plugin PNG cache)
- runtime behavior (prefer native envelopes; packet-gate laws if Core cannot speak)

## UI pitfalls

- A hero-ability icon cache that reports success with **zero rows loaded** is a failure.
- Write exact disabled / normal / hover children. Do not guess from image filenames.
- Legacy Warcry “normalize availability” paths may be quarantined. Icon/bind is the release-safe slice.
- Elite Strategem-style toggles must key pending mode by the casting hero id. A process-global mode leaks into the next battle.

## What you can change in Core without a new pipeline

Focus cost (`energyLevel`), cooldown, charges, VFX paths, base damage, per-level multiplier, specialization `battleSubskillBonus` deltas.

## What you cannot assume

- That raising creature Attack changes Heroic Strike (it does not, on stock rows)
- That mage uses Spell Power only
- That the combat action-bar fix also fixed the hero bar

## Helper widget

Studio → Hero abilities.
