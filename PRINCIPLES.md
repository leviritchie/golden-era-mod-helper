# Golden Era principles for other creators

These rules come from shipping custom factions, abilities, towns, and visuals against the Golden Era IL2CPP build. They are not style preferences. Breaking them is how mods look finished in JSON and then crash at map load or combat Init.

## 1. Olden Era is three layers, not one table

| Layer | What it is | Typical contents |
| --- | --- | --- |
| **Core data** | JSON and scripts inside `HeroesOldenEra_Data/StreamingAssets/Core.zip` | Factions, city logic, units, UnitViews, heroes, abilities, laws, buffs, localization |
| **Plugin runtime** | A BepInEx IL2CPP plugin with Harmony patches | Icon resolvers, visual replacement after native construction, HUD binds, fail-closed symbol pins |
| **Direct State** | Opt-in journaled native store writes | Occupancy/teleport-style transactions when no Core donor verb exists |

A feature often needs more than one layer. A custom unit can have correct logic rows and still crash combat if UnitView arrays do not match. A custom faction can exist in `DB/fractions` and still be missing from the faction selector because a serialized Unity asset does not know the id.

**Default order:** express the design with a native Core envelope first. Use a plugin hook only when Core cannot say it. Use Direct State only when you need a traced store transaction with journal/rollback.

## 2. One problem, one owner

Do not add a second damage path, a second town click system, or a second battle visual owner “just in case.” Silent fallbacks hide the real fault and create later crashes.

If a Core donor already does the job (a unit special, a buff SID, `teleport`, a law `unitStat` row), use that donor. Do not invent Harmony mutation beside it.

## 3. Fail closed

If a required symbol, row, or payload is missing:

- skip that feature, or
- leave native behavior alone.

Do not invent a broad compatibility path that guesses ids from visible names, sprite filenames, or “a custom city was seen.” Those guesses work with one custom faction and cross-wire two.

## 4. Donor shells are allowed. Donor reverse lookup without context is not

Native code often needs a prefab path or building SID it already understands. Forward mapping is legal:

`custom SID -> donor SID`

Reverse mapping is legal only with exact context:

- saved original custom SID
- live hire payload
- current city SID plus an unambiguous join
- current bound unit/hero config

Illegal: “this donor barracks belongs to whichever custom faction we saw last.”

## 5. Copy complete native shapes

Olden Era native code expects arrays to line up. If unit logic has an alternative attack, UnitView needs the matching alternative attack view. Keep buckets such as `defaultAttacks`, `alternativeAttacks`, `counterAttacks`, and `abilities` even when some actions are unused, unless you have native evidence that a smaller shape is safe.

The same rule applies to city logic, skill graphs, and biome rows. A biome is not one string on the faction file. It is tiles, water, generator config, arena views, sounds, and runtime materials.

## 6. Live artifacts beat source files

| Question | Authoritative place |
| --- | --- |
| What data did the game load? | Installed `Core.zip` (and `Lang` inside it) |
| What code ran? | Installed plugin DLL + `GameAssembly.dll` + metadata |
| What did Harmony patch? | `BepInEx/LogOutput.log` registration lines |
| Why did the process die? | Unity `Player.log` and `BepInEx/ErrorLog.log` |

Generator output in a git worktree is not proof the game used it. Steam updates replace `Core.zip`. Backup zips next to `Core.zip` can be ingested as another archive and cause duplicate-key errors.

## 7. Obfuscated names live in one registry

IL2CPP type and method names change after hotfixes. Put live pins in a `GameSymbols`-style file. Match by signature and call flow, not by a name you remember from a dump.

Dump is not live. DiffableCs method-declaration index is not live `Method_N`.

## 8. After types match, key by native identity

Il2Cpp will re-wrap the same native object into a new managed proxy. `GetHashCode` and `ReferenceEquals` on those proxies miss.

1. Pin live argument type against map key type. Bridge wrappers (example: Unit.Init side wrapper versus `TransferSide`).
2. Then key caches by native pointer, not managed identity.
3. Matching native keys = same native object. Distinct native keys = different objects or the wrong owner.

A non-empty dictionary plus `TryGetValue` false is a failed check, not “no plan.”

## 9. Producer state must still exist when the consumer runs

If you fill a plan in one Harmony postfix and apply it in a later postfix, do not clear the map in the earlier postfix. Logs that say “planned” while apply sees empty are a timing/ownership bug.

`BattleLogic.Init` also runs during adventure-map / session Loader. Do not throw fail-closed from optional pilots on that prefix or you can brick map load.

## 10. Visual surfaces are independent

Battle, adventure-map unit, town billboard, unit portrait, hero portrait, detail preview, recruitment card, timeline portrait, sound, and town world are different owners. Fixing combat art does not prove the hire list portrait.

For creatures, pick **one** battle presentation lane:

- **billboard** — camera-facing sprite arrays / map quad
- **skinned_mesh** — owned Unity mesh and clips; omit battle billboard arrays
- **depth_billboard_experiment** — still a billboard; not the product 3D lane

Do not mix skinned-only packs with billboard `battle.prefab` payloads.

## 11. Player-facing text describes shipped behavior

Do not put “placeholder”, “not implemented”, or generator debt in localization. Keep debt in internal metadata or docs.

Icon keys are runtime sprite keys (`assassin_buff_icon`), not localization tokens (`*_name`) and not export filenames (`Orientation@4x`).

## 12. Label proof. Do not promote it

These are different states:

1. source/static validated
2. generated artifact validated
3. build target proven
4. deployed / installed payload proven
5. startup smoke proven
6. runtime behavior proven
7. user-visible gameplay proven

A log line that says planned, registered, or stored is not user-visible gameplay.

## 13. Town product path is an owned city world

Preferred town: own a Unity city world, paint art onto native `BhBuilding` slots, keep CityUI native, open construction through HUD navigation.

Rejected as the destination: Route A UI posters, click relays into RawImage layers, aliasing onto another faction’s city.

## 14. Focus cost is a Core field named energyLevel

Creatures and hero abilities spend **Focus**. In JSON that field is `energyLevel`. Cooldown is `cd` / `cooldown`. Do not invent a second resource counter for ordinary actives.

Stock Heroic Strike / mage commander attacks use `absolute_damage` and ignore caster offence and enemy defence. They are not classic HoMM Attack-minus-Defense.

## 15. This helper cannot ship your mod

The widgets write sandbox files so you can learn the shapes. Connecting those files to a live overlay, plugin, and install is your pipeline. Keep that pipeline fail-closed and validated.
