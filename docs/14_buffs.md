# Component: Buffs and statuses

This component is **buff table rows and apply/query**. Wrong table = silent missing effect.

## Which table

| Table (inside Core) | Typical owner |
| --- | --- |
| `DB/buffs/sub_skills_battle_hero_ability_buffs.json` | Hero ability / Warcry-style effects |
| `DB/buffs/sub_skills_battle_hero_buffs.json` | Broader battle hero buffs |
| `DB/buffs/sub_skills_battle_hero_skill_*.json` | Leadership / luck / tactics packs |
| `DB/buffs/buffs_space_magics.json` | Spell buffs |

Clone a live donor envelope: duration, dispel, hidden flags, tags.

## Speed and stats

Speed-modifying buffs need donor movement tags (`movementPositive` / `movementNegative`, plus haste/slow family tags when cloning those spells). Rows present in the buff manager without those tags have failed to change combat Speed.

Live-proven while building the Golden Era mod against Olden Era: even with tags and `config.data.stats.speed`, got-buff dispatch may leave `Unit.get_stats().get_speed` unchanged until you fold `config.data.stats` additively (`set_speed(current + delta)`). Replacing the whole `UnitStat` clobbers other fields. Do not do that for deltas.

Battle-long army buffs typically need Core `infinite: true` and `addition: "data"` (not `addition: "duration"`), or they apply and then decay immediately.

## Identity

Exact-id custom rows often apply at level ≥ 1. Vanilla leveled rows use base sid + level (`magic_haste_effect` → `magic_haste_effect_1`). Hire UI NRE is often a null BuffConfig from a bad SID.

After add, probe presence with list-by-SID `Count`, not a guessed `Boolean_String` method, and not managed foreach on Il2Cpp lists.

## Plugin dispatch

Use your buff-law symbol registry only. Sender is the ability/native source. Never pass the event hub as both `this` and argument 0. See [hooks](11_hooks.md) for Method_N pinning.
