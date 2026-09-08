# Component: Hooks catalog

This component lists **runtime families**. Live obfuscated names are not a public API. After every **Olden Era** game update, re-pin in your own `GameSymbols` file. Names that worked in the Golden Era plugin on last week’s game build may be wrong on this week’s.

The studio Hook catalog searches `data/hook_catalog.json`.

## How to use a family

1. Confirm Core cannot express the design.
2. Read the family `when` and `doNot`.
3. Put type hints and MethodSymbols in one registry.
4. Register from one startup owner. Log exact success or skip.
5. Label proof: registration is startup smoke, not gameplay.

## Families (summary)

| Family | Typical job |
| --- | --- |
| Symbol registry | One place for live names |
| Battle unit init | Unit.Init, side wrapper versus TransferSide, no throw on Loader Init |
| Selected-unit HUD | Custom Focus buttons, hotkeys, overlays |
| Hero ability UI | Commander / extra action icons |
| Focus / energy | Grant and display Focus; Core field remains `energyLevel` |
| Committed damage | Last-resort law mutator; one owner; no stale method fallbacks |
| Buff dispatch | Got-buff raise is a pinned Method_N, not DiffableCs index |
| Import visuals | Billboard vs skinned mesh after native construction |
| Town world | Owned city scene, hall open, visually-open panel close |
| Map objects | Town/dwelling billboards, hire joins, no shared id mutation |
| Portraits / icons | Custom keys absent from serialized sprite registry |
| Law runtime | Packet-gated; native-data laws are default |
| Direct State | Traced store writes only |
| Terrain / biome | Full pipeline, not one biome string |
| Session / menu | Custom-game lists and serialized faction assets |
| Extra hero actions | Additive grants + matching UI/runtime |

## Harmony argument identity

Example that has burned real patches: `Unit.Init` argument 2 is a **battle-side wrapper**, not `TransferSide`. If your map is keyed by `TransferSide`, bridge first. A miss against a non-empty map is a bug.

Then key by native pointer if proxies re-wrap.

## Event hub Method_N

Counting `void(object, BattleEventArgs)` methods in DiffableCs and picking `Method_Public_Void_Object_BattleEventArgs_<index>` invents the wrong raise.

Pin: field offset → interop field short name → `field_…_N` → matching raise `Method_…_N`.

Buff got-buff: DiffableCs index 39 is **not** live Method_39 (that one raises ChangeAbility and live-negatives with a cast). The got-buff pin is a different Method_N (`cfin` / Method_35 on one Olden Era game build used while making Golden Era). Your Olden Era build may differ. Re-pin.

## C# examples

See `csharp/Examples/`. They use placeholder names on purpose.
