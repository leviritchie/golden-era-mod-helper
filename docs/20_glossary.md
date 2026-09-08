# Glossary (read this first if you have never modded Olden Era)

This kit uses words that are ordinary in this community and meaningless if you have not seen them. Each definition is the meaning used here. If two words look similar, they are still different jobs.

## The game, the example mod, and this kit

These three names are not the same thing.

**Olden Era** is the Unity game *Heroes of Might and Magic: Olden Era*. That is what you install from Steam and launch. When this kit says **the game**, it means Olden Era. The instructions here are for **modding Olden Era**.

**Golden Era** is a **mod** for Olden Era (a large BepInEx plugin plus Core.zip overlay). It is not the game, and it is not a special edition of the game. This kit is a set of **worked examples taken from how Golden Era was made**. You can follow the same jobs for a different Olden Era mod. You do not need to install Golden Era to use this kit.

**Golden Era Mod Helper** (this repository and website) is the teaching kit. It is not Golden Era, and it does not install Golden Era or any other mod.

**Vanilla** / **stock** means an unmodded Olden Era table or behavior: the rows and buttons the game already ships.

**IL2CPP** is how Unity shipped Olden Era’s gameplay code: it is compiled to native code (`GameAssembly.dll`), not to easy-to-edit C#. You do not open the game’s combat code in a text editor. You add data files and, when data is not enough, a plugin that patches running methods.

## What a mod is here

A **mod** in this kit is extra data and/or extra plugin code that the game loads:

1. Rows inside the game’s data archive (**Core.zip**).
2. Optional **plugin** files (a `.dll`, pictures, 3D bundles) loaded by **BepInEx**.

This GitHub kit is **not** a finished faction you install. It writes **practice files** into a folder named `sandbox/` inside this clone. You copy those shapes into *your* overlay and plugin later.

## Files and ids

**JSON** is a text format for structured data (`{ "name": "Pikeman" }`). Almost all game tables are JSON.

A **SID** (string id) is the stable machine name of a thing, such as `h3_pikeman` or `homm3_castle`. The player may see “Pikeman.” The engine looks up `h3_pikeman`. If two rows share a SID, the game often crashes with a duplicate-key error.

A **token** is a localization key such as `h3_pikeman_stunning_blow_name`. The English (and other language) sentence lives in a language file. The combat row points at the token, not at the sentence.

An **icon key** is a different string: the name the UI uses to find a sprite. Vanilla example: `assassin_buff_icon` (already in the live registry). A custom key only works if your plugin allowlists it and ships the PNG. It is not a token. It is not a Photoshop filename like `Icon_Orientation@4x.png`.

## Core.zip (layer 1)

**Core.zip** lives under the game folder:

`HeroesOldenEra_Data/StreamingAssets/Core.zip`

It is a zip archive of JSON (and related files). The running game reads **this archive**, not a random file in your Documents folder. If you edit a copy on disk and never pack it into the installed `Core.zip`, the game will not see it.

**Logic** rows say what a unit *does* in combat (damage, Focus cost, cooldown).

**View** rows say how that action is *shown* (name token, icon, animation index). If logic has three abilities and view has two, combat can crash while it builds the action bar.

**Localization** files (`Lang/english/texts/…` inside Core) hold the sentences the player reads.

**Packing / overlay** means a tool you own that writes your JSON into `Core.zip`. This kit does not pack. There is no “install to my Steam folder” button, on purpose.

## Plugin, BepInEx, Harmony (layer 2)

**BepInEx** is a loader that starts with the game and can load extra .NET plugins.

A **plugin** is your C# project compiled to a `.dll` that BepInEx loads.

**Harmony** is a library that **patches** (redirects or wraps) a method that already exists in the game. A patch is often called a **hook**.

Example of why a hook exists: you put a new icon key in JSON, but the game’s UI sprite dictionary was baked without that key. JSON cannot teach that dictionary. A hook can supply the picture at lookup time.

**Obfuscation** means the live method names look like `bdrf` instead of `OnHotkey`. They change after game updates. A **GameSymbols** file is one list of those live names so you do not scatter them through every feature.

**Fail closed** means: if the live method is missing, skip your feature or leave the vanilla behavior alone. Do not guess another method with a similar name.

## Direct State (layer 3)

**Direct State** is an advanced way to write into native battle memory with a journal (so a write can be rolled back). It is **not** how you add a “spend 2 Focus to stun” button. That button is Core data. Use Direct State only when no Core verb exists and you need a traced store transaction.

## Combat words

A **unit** is a creature type (`h3_pikeman`). In battle you see a **stack** (many of that type in one hex).

**Focus** is the battle resource the player spends on special actions. In JSON the cost field is named **`energyLevel`**, not `focus`. If this kit says “Focus cost 2,” the file will contain `"energyLevel": 2`.

A **cooldown** is how many rounds before that action can be used again. In Core this is often `cd`.

A **creature Focus ability** is a button on the selected-unit action bar (the unit you clicked). It is not a hero spell, and it is not Heroic Strike.

A **hero ability** is a button on the **hero** bar. Stock might heroes have **Heroic Strike** (`skill_warrior_ability`). Stock magic heroes have a mage commander attack (`skill_mage_ability`). Extra shouts and summons are **additional** buttons.

**Heroic Strike** on stock Olden Era rows (the commander attack Golden Era kept) uses **absolute damage** and ignores the caster’s offence and the enemy’s defence. Raising a creature’s Attack stat does not make Heroic Strike work like classic Heroes of Might and Magic Attack-minus-Defense. That surprise is documented because people assume the old formula.

A **buff** is a status table row (stun, bless, haste, Weaken Attack/Defense). An ability can apply a buff SID. Example live Core SID: `magic_shorten_shadow_effect_1` is Weaken Attack/Defense, **not** stun. If that SID is missing from Core, hire/UI screens can crash with a null config. That is a data bug, not a missing picture.

## Town and faction words

A **faction** is a town identity: name, units, heroes, laws, city, map objects. It is not one JSON file.

A **donor** is a vanilla faction/unit/building the engine already knows (for example Human / `esquire`). Custom content often **wears a donor shell** so native code can construct an object, then a hook swaps the art. Forward map: your SID → donor SID. Reverse map (donor → your SID) without exact context is how two custom factions steal each other’s dwellings. Do not guess the donor from a Heroes 3 town name: in the Golden Era example, Tower uses Human/`Tundra`, Stronghold uses Dungeon/`Wasteland`.

A **billboard** is a camera-facing 2D sprite (the classic Heroes 3 look).

A **skinned mesh** is a 3D model with bones and animation clips. Battle, preview, and map can use that mesh. You must not mix a skinned-only combat bundle with a billboard `battle.prefab`. Combat then crashes on startup.

A **building SID** such as `Build_Main` or `Build_Tier_1` is a slot the native town UI already understands. You rename and re-bonus those slots. You do not invent a second click system.

A **town scene / city world** is the 3D (or world-quad) place you enter when you visit a town. Clicks should stay on native building objects (`BhBuilding`). Poster-on-a-UI-canvas towns are a rejected product path in this kit.

A **law** is a row on the faction law tree (passive bonuses you buy with law points). Most laws should be native table primitives (`unitStat`, growth, and similar). A Harmony damage mutator is a different, gated job.

A **specialization** is a hero’s specialty bonus list, not the commander-attack button.

## This kit’s own words

The **studio** is a small website that runs on your computer (`http://127.0.0.1:8777`). Only you can open it. It is not a website on the internet unless you host it yourself.

A **widget** is one studio page with a form. Each widget writes JSON (or Markdown) into `sandbox/`.

The **CLI** is the same writers, run from a terminal (`python cli.py …`).

The **sandbox** is the only folder this kit is allowed to write. It will not write into Steam, `Core.zip`, or your plugin folder.

A **template** (Focus templates) is a known-good *shape* of a creature ability copied from how vanilla actions look (melee + buff, heal percent, and similar). You still must point it at real buff SIDs and icons that exist in live Core.

An **overlay-review** file is sandbox JSON this kit writes. It is a checklist of fields for a packer you own. It is **not** a Core.zip row (`units_logics`, `DB/fractions/…`). `kitMeta.fileKind` is `overlay-review`. Proof: source/static only.

An **overlay** is software **you** own that copies your JSON into the installed `Core.zip`. This kit is not an overlay. Golden Era’s packer is not included.

**Proof labels** are honesty tags: “this JSON exists” is not “a player saw it in combat.” See [17_proof.md](17_proof.md).

## What this kit will never do

- Install a faction into Olden Era
- Compile your plugin
- Patch `GameAssembly.dll`
- Pack overlay-review JSON into Core.zip
- Guess a donor reverse-lookup because “a custom town exists”
- Invent a stun buff SID, or treat Weaken (`magic_shorten_shadow_effect_1`) as stun
- Treat Golden Era plugin class names as a public API
- Treat a log line that says “registered” as proof the player saw the feature
