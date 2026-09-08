# What every tool does

If you have never used this kit, and you have never modded Olden Era, this page is the map.

**Olden Era** is the game. **Golden Era** is an example *mod* for that game. The tools and jobs below are how Golden Era was made. Use them for any Olden Era mod. This page does not install Golden Era.

You can **read** this page in a browser with no Python:

https://leviritchie.github.io/golden-era-mod-helper/21_tools.html

Nothing here is a Steam installer. Nothing here finds your game folder. Every local tool either **explains** a job or **writes a practice file** into a folder named `sandbox` at the root of this clone. The running game will not change until **you** copy those files into an overlay and plugin that you own.

There are two ways to run the same writers on your computer (GitHub Pages cannot do this; it can only show documentation):

1. **Studio** — a local web page with forms.
2. **CLI** — commands that start with `python cli.py`.

They write the same kinds of JSON. Use whichever you can operate.

If a word on this page is new (SID, Core.zip, Focus, Harmony, donor), open [20_glossary.md](20_glossary.md) first.

---

## What this kit is, in one picture

Imagine three separate desks:

| Desk | What lives there | Does this kit sit there? |
| --- | --- | --- |
| This clone | Docs, forms, and a `sandbox/` folder of practice JSON | Yes. This is the only desk the tools write to. |
| Your overlay / plugin | The packer and C# that actually change Olden Era | No. You copy shapes from sandbox into that work. |
| The installed game | `Core.zip`, BepInEx, Steam | No. The tools refuse those paths. |

If you click **Assign Focus ability to sandbox** and then launch Olden Era, the new button will **not** be there. That is expected. The click only created a text file in this clone.

---

## First 15 minutes (do this once)

1. Install [Python 3.10 or newer](https://www.python.org/downloads/). On Windows setup, enable **Add python.exe to PATH**.
2. Clone this repository to any folder you can write. There is no required drive letter and no required Steam path.
3. Open a terminal **inside the cloned folder** (the folder that contains `cli.py` and `README.md`).
4. Check Python:

```text
python --version
```

You should see 3.10 or higher. On some Windows installs the command is `py` instead of `python`. If so, use `py` in every example on this page.

5. List the tools:

```text
python cli.py -h
```

You should see words such as `studio`, `test`, `scaffold-faction`, `assign-focus`. If you see `No module named` or `cannot find cli.py`, you are not in the clone folder yet.

6. Start the local website:

```text
python cli.py studio --port 8777
```

Leave that terminal window open. In a browser, open `http://127.0.0.1:8777`.

You should see a dark page titled **Golden Era Mod Helper** and a list of links on the left. The site runs only on your computer. Closing the terminal stops it.

7. Click **Glossary**, then come back to **What the tools do**. Then click **Faction scaffold**, keep the example values, and click the gold button.

Under the form you should see a green status line and a list of file paths. Those files now exist under `sandbox/faction_homm3_example/` in this clone. Olden Era still has not changed.

8. Click **Sandbox files** on the left. You should see the same paths listed.

That is the whole loop: fill a form (or run a CLI command) → a practice file appears in `sandbox/` → you later copy it into your own pipeline.

---

## What a successful save looks like

After a form submit or a CLI writer:

- A **green status line** (studio) or a printed path (CLI) names the file.
- A **JSON block** may appear on the page. That is the contents of the file, shown for review.
- The same file is on disk under `sandbox/`.
- The game install is untouched.

If the status line is red, read the error. Typical causes:

- A SID contains spaces or illegal characters.
- An icon key looks like a localization token (`something_name`) or a Photoshop filename (`Icon@4x.png`).
- A law effect type is not one of the native types this kit allows.
- You asked the CLI for a path outside `sandbox/` (the writers will refuse).

---

## How to find the files on disk

The clone folder contains `cli.py`, `README.md`, and `sandbox/`.

Examples after a first try:

- `sandbox/faction_homm3_example/CHECKLIST.md`
- `sandbox/ability_overrides_homm3_example.json`
- `sandbox/presentation_h3_example_pikeman.json`

Generated JSON in `sandbox/` is gitignored so practice dumps do not get committed by accident. `sandbox/README.md` stays.

---

## Studio pages (left navigation)

Each row is one page. “Writes” means a file under `sandbox/`. Read-only pages write nothing.

| Page | What it is for | What a successful submit writes |
| --- | --- | --- |
| Overview | Short map of the three layers (Core data, plugin, Direct State) | Nothing |
| Glossary | Word meanings | Nothing |
| What the tools do | This document | Nothing |
| Getting started | Day-one order for a new faction | Nothing |
| Principles | Architecture rules | Nothing |
| Component docs | Longer articles, one job each | Nothing |
| Focus ability assigner | Give a **creature** a special that spends Focus | `sandbox/ability_overrides_<factionSid>.json` |
| Faction scaffold | Start a town identity plus a checklist of the other jobs | `sandbox/faction_<sid>/` (several files) |
| Billboard vs mesh | Choose 2D sprite vs 3D model for one unit | `sandbox/presentation_<unitSid>.json` |
| Hero abilities | Commander attack vs extra **hero** buttons | `sandbox/hero_abilities_<heroSid>.json` |
| Buildings and town | Native building slots plus the owned-town rule | `sandbox/buildings_<factionSid>.json` |
| Faction laws | One native law-tree bonus | `sandbox/law_overrides_<factionSid>.json` |
| Hook catalog | Which runtime family you are in | Nothing (search only) |
| Silent miss doctor | “The data exists but nothing happens on screen” | Nothing |
| Proof labels | Honesty ladder for claims | Nothing |
| Sandbox files | List of files already written | Nothing |

**Optional studio arguments** (when you start it from the terminal):

| Argument | Meaning |
| --- | --- |
| `--port 8777` | Which local TCP port to listen on. Change it if 8777 is already used. |
| `--host 127.0.0.1` | Who can connect. Keep `127.0.0.1` unless you know you want other machines on your LAN to open the page. |

The studio does not upload anything. It does not find Steam.

---

## Tool: Focus ability assigner

**Problem it solves.** You want a creature you clicked in combat to have a special button that spends **Focus**. Players say Focus. The JSON field is named `energyLevel`. This tool writes a reviewable file that lists cost, cooldown, name, and mechanic *shape*.

**This is not** a hero button. Hero buttons are the Hero abilities page.

**Two forms on the same page**

1. **Assign Focus ability** — append a **template card** (a new override ability) onto a unit.
2. **Edit an existing special slot** — record a change to a slot that already exists (enable/disable, rename, change Focus cost) without claiming you invented a new engine verb.

### Fields (assign form)

| Field | Meaning |
| --- | --- |
| Start from the in-package sample | If checked, loads `data/sample/ability_overrides.json` (Example Pikeman line) so you can see a real shape. If unchecked, starts an empty file for the faction SID you type. |
| Faction SID | Machine id of the faction, usually `homm3_` plus a short name. Example: `homm3_example`. |
| Unit SID | Machine id of the creature. Example: `h3_example_pikeman_upg`. |
| Template | Which known ability *shape* to copy. See the table below. |
| Player-facing name | English title you want the UI to show. |
| Runtime icon key | Sprite id the UI uses to find a picture, such as `assassin_buff_icon`. Not a `_name` token. Not a filename like `Orientation@4x.png`. Leave blank if you do not know yet. |
| Description | Tooltip sentence. Describe only behavior you will actually ship. |
| Focus cost (`energyLevel`) | Integer ≥ 0. This is Focus, even though the JSON field has another name. |
| Cooldown in rounds | Integer ≥ 0. |
| Rank | Native rank field. Copy vanilla if unsure. |

### Templates

A template is a *shape*, not a finished combat verb. You still must point it at real buff SIDs, spell SIDs, and icons that exist in live Core when you pack.

| Template id | What the shape is | When to pick it |
| --- | --- | --- |
| `copied_unit_special` | Points at another unit’s existing special (including alternate attacks) | You found a vanilla special that already does the job |
| `focus_melee_buff` | Melee hit + apply a buff SID | Stun, weaken, and similar on a melee strike |
| `focus_ranged_shot` | Ranged attack with optional projectile key | Shooters |
| `repair_heal_percent` | Ally `heal_percent`, Gremlin Mechanic-like | Repair / heal |
| `focus_spell_effect` | Apply a vanilla spell effect envelope | You will fill a real spell SID from live Core |
| `focus_stun_melee` | Melee + stun-style buff (you must still set a real buff SID) | Stun actives |
| `passive_text_only` | Text only | The behavior already exists; you only need a card |

### Fields (edit-existing form)

| Field | Meaning |
| --- | --- |
| Slot | `abilities` (active buttons), `passives` (always-on), or `alternativeAttacks` (extra attack modes) |
| Slot index | `0` is the first item in that list, `1` is the second, and so on |
| Enabled | Uncheck this to turn that slot off on purpose |

**After you click save.** Open the JSON it printed. That file is **not** in the game yet. Your overlay (the packer you write or adopt) must turn it into `units_logics` + `units_views` + language rows. Logic and view array lengths must match or combat can crash while it builds the action bar.

**Common mistakes**

- Treating this file as an installed ability.
- Using a localization token as `iconKey`.
- Adding a logic row and forgetting the matching view row later in your overlay.
- Using this page for Heroic Strike. That is a hero ability.

---

## Tool: Faction scaffold

**Problem it solves.** People start with one `myfaction.json` and then discover they also needed a city, dwellings, heroes, unique skill ids, and a town scene. This tool writes a **starter pack** and a **checklist** so those jobs stay named and separate.

**This is not** a playable town. It will not appear in New Game.

### Fields

| Field | Meaning |
| --- | --- |
| Short name | Used to build `homm3_<short>` if you did not already type a `homm3_` SID. Example: `example` → `homm3_example`. |
| Display name | Human label for the checklist, for example `Example`. |
| Donor town family | Which vanilla town family you will clone **shells** from. `castle` means native code already knows Human prefabs. This is not “your town is Castle.” You still give your faction its own SIDs. |
| Biome | Optional. If blank, the donor family’s default biome string is used. A brand-new biome is a full terrain pipeline, not this one field. |

Allowed donor keys: `castle`, `rampart`, `tower`, `inferno`, `necropolis`, `dungeon`, `stronghold`, `fortress`, `conflux`, `cove`.

### Files written under `sandbox/faction_<sid>/`

| File | Role |
| --- | --- |
| `faction.json` | Identity, Core member paths, one sample unit line |
| `ability_overrides.json` | Empty creature-ability overrides |
| `hero_overrides.json` | Empty hero overrides |
| `law_overrides.json` | Disabled example of a native growth law |
| `CHECKLIST.md` | Boxes for Core, units, presentation, heroes, buildings, Focus, hooks, proof |

Open `CHECKLIST.md` next. Each checkbox is a different job. Finishing `faction.json` does not mean the faction is pickable in the UI.

---

## Tool: Billboard versus skinned mesh

**Problem it solves.** Battle **art** is a separate job from stats. Mixing a 3D-only bundle with a 2D battle prefab crashes combat while the battle is loading.

**This is not** damage, growth, or Focus. It is only how the creature looks.

| Word | Meaning |
| --- | --- |
| Billboard | Camera-facing 2D sprite (classic Heroes 3 look) |
| Skinned mesh | 3D model with bones and animation clips |
| Depth billboard experiment | Still 2D, with displaced pixels. Not the product 3D lane |

### Fields

| Field | Meaning |
| --- | --- |
| Unit SID | Which creature this plan is for |
| Native donor base SID | Vanilla unit whose prefab the engine can load, for example `esquire`. Custom units often wear a donor shell. |
| Lane | `billboard`, `skinned_mesh`, `depth_billboard_experiment`, or blank to let the checkboxes recommend |
| I have decoded DEF / sprite frames | You extracted Heroes 3 animation frames |
| I have an owned rig and battle clips | You have a skeleton and combat animations you own |
| I want true 3D in combat | Product 3D lane, not a 2.5D experiment |
| Depth experiment only | 2.5D only |

The written plan lists required follow-up jobs and a “do not” list for that lane. It does **not** build a Unity bundle. It does not copy art.

**Common mistakes**

- Putting a skinned-mesh pack where the game still expects `battle.prefab`.
- Treating this JSON as installed art.

---

## Tool: Hero abilities

**Problem it solves.** People overwrite Heroic Strike when they meant to add a second button, or they give a magic hero the warrior commander SID.

**This is not** a creature Focus button. Creature Focus is the Focus ability assigner.

Stock **might** heroes get Heroic Strike (`skill_warrior_ability`). Stock **magic** heroes get the mage commander attack (`skill_mage_ability`). Extra shouts and summons are **additional** SIDs. Do not replace the commander slot unless that is the explicit design.

Stock Olden Era Heroic Strike (the commander attack Golden Era kept) uses **absolute damage** and ignores the caster’s offence and the enemy’s defence. Raising Attack does not make it work like classic Heroes Attack-minus-Defense.

### Fields

| Field | Meaning |
| --- | --- |
| Hero SID | Machine id of one hero, not a creature |
| Class | `might` grants `skill_warrior_ability`; `magic` grants `skill_mage_ability` |
| Extra ability SIDs | Comma-separated extra buttons (Warcry-like). Empty is fine. |
| Replace commander | Only if the design is “this hero no longer has the stock commander attack” |
| Replacement SID | Required if that box is checked |

The JSON is a **grant plan** (which specialization/skill rows should contain). It is not a complete `hero_abilities.json` Core row.

---

## Tool: Buildings and town

**Problem it solves.** Olden Era towns already have building slots with ids such as `Build_Main` (hall) and `Build_Tier_1` (tier 1 dwelling). People invent a second click system or a poster UI. This tool lists the native slots and writes a plan that insists on an **owned city world**: a Unity town scene whose clicks stay on native building objects.

**This is not** a finished town. It does not place art. It does not compile Unity.

### Fields

| Field | Meaning |
| --- | --- |
| Faction SID | Town identity this list belongs to |
| City SID | Optional machine name of the city object |
| Owned city scene name | Pattern name for the Unity town scene. Default `cityFactory` is a pattern, not “reuse the vanilla scene.” Your scene should be dedicated to your faction. |

The table on the studio page is the native slot list (hall, marketplace, dwellings, and so on). You rename those slots and give them bonuses. You do not add a parallel building id system.

---

## Tool: Faction laws

**Problem it solves.** People write a Harmony combat patch for “+10% weekly growth.” That is usually a native table row such as `cityUnitsIncrement`.

A **law** is a bonus on the faction law tree (the point-spend chart in town). It is not a creature Focus button and not Heroic Strike.

### Fields

| Field | Meaning |
| --- | --- |
| Faction SID | Town this law belongs to |
| Law SID | Unique machine name of this law row |
| Player-facing name / description | What the player should read. Describe only the bonus you will emit. |
| Native effect type | One of the types this kit allows: `unitStat`, `heroStat`, `sideRes`, `cityUnitsIncrement`, `battleSubskillBonus` |
| Parameters | Comma-separated tokens **copied from a live Core example** of the same type. Example for growth: unit SID, then the amount. |

If the form rejects the effect type, stop. Do not invent a new `type` string here. Do not use this page to author a damage hook.

---

## Tool: Hook catalog (read only)

**Problem it solves.** You need to know *which family* of running-game patches you are in (selected-unit bar, town scene, icons, and so on) before you write C#.

A **hook** is a plugin patch on a method that already exists in the game. Live method names look like random letters and **change after game updates**. This catalog does **not** give you copy-paste names that survive the next patch. After an update you must re-pin names in your own plugin’s symbol list.

Type a search word or click Search with a blank box to list families. Each card says what that family is for and what not to do.

---

## Tool: Silent miss doctor (read only)

**Problem it solves.** You believe the data is present (a JSON row, a plan dictionary, a registered patch) but the player still sees nothing.

Click the sentence that matches. The answer is a **diagnosis** (wrong key type, cleared too early, Core row missing, and similar). It is not a second patch to paste blindly.

---

## Tool: Proof labels (read only)

**Problem it solves.** People say “it works” when they only meant “a file exists.”

These labels are an honesty ladder. A generated JSON file is not the installed game. A log line that says registered is not a player seeing the button. Combat feel is a later label. Read [17_proof.md](17_proof.md) for the full list.

---

## Tool: Sandbox files (read only)

Lists practice files this kit already wrote in this clone. If the list is empty, you have not submitted a writer yet. These files are not in the game.

---

## CLI commands (same writers, no browser)

Run these from the clone root (the folder with `cli.py`). Add `-h` after any command to see its arguments, for example `python cli.py assign-focus -h`.

### `python cli.py test`

Runs the automated checks in `tests/`. These prove the writers refuse to save outside `sandbox/` and that sample JSON matches the schemas.

**What a pass means.** Isolation and schemas are intact on this clone.

**What a pass does not mean.** Your game install is fine. A faction is playable. Combat works.

### `python cli.py templates`

Prints the Focus template ids, labels, categories, and risk tags, one per line, tab-separated. Use this when you cannot remember the `--template` string for `assign-focus`.

### `python cli.py pages`

Builds a static documentation website into `./site`. GitHub Actions publishes that folder to GitHub Pages. This command does **not** write sandbox JSON and does not install a mod. Open `site/index.html` locally if you want to preview without deploying.

### `python cli.py studio`

Starts the local website. See [First 15 minutes](#first-15-minutes-do-this-once). Stop it with Ctrl+C in that terminal.

### `python cli.py scaffold-faction`

```text
python cli.py scaffold-faction --short-name example --display-name Example --donor castle
```

| Argument | Required | Meaning |
| --- | --- | --- |
| `--short-name` | yes | Becomes `homm3_example` if you did not pass a `homm3_` prefix |
| `--display-name` | yes | Human label |
| `--donor` | yes | One of: castle, rampart, tower, inferno, necropolis, dungeon, stronghold, fortress, conflux, cove |
| `--biome` | no | Override biome string |

Same output as the Faction scaffold widget. The command prints the paths it wrote.

### `python cli.py assign-focus`

```text
python cli.py assign-focus --faction-sid homm3_example --unit-sid h3_example_pikeman_upg --template focus_melee_buff --name "Halberd Hook" --description "Spend 2 Focus to stun." --focus-cost 2 --cooldown 2 --from-sample
```

| Argument | Meaning |
| --- | --- |
| `--faction-sid` | Faction machine id |
| `--unit-sid` | Creature machine id |
| `--template` | A template id from `templates` |
| `--name` / `--description` | Player-facing strings |
| `--focus-cost` | Writes `energyLevel` |
| `--cooldown` | Rounds |
| `--rank` | Optional, default 1 |
| `--icon-key` | Optional runtime sprite key |
| `--from-sample` | Start from the packaged sample instead of an empty file |

Writes `sandbox/ability_overrides_<faction-sid>.json`.

### `python cli.py edit-existing-special`

Same idea as the second studio form: retune a slot that already exists.

```text
python cli.py edit-existing-special --faction-sid homm3_example --unit-sid h3_example_pikeman_upg --name "Halberd Hook" --description "Spend 2 Focus to stun." --focus-cost 2 --cooldown 2 --icon-key assassin_buff_icon --from-sample --enabled
```

| Argument | Meaning |
| --- | --- |
| `--slot` | `abilities`, `passives`, or `alternativeAttacks` |
| `--index` | 0-based slot index |
| `--enabled` or `--disabled` | Whether that slot should be on |
| `--from-sample` | Start from the packaged sample |

### `python cli.py presentation`

```text
python cli.py presentation --unit-sid h3_example_pikeman --donor-base-sid esquire --has-def-frames
```

Pass `--lane billboard` (or `skinned_mesh` / `depth_billboard_experiment`) **or** use the asset flags `--has-def-frames`, `--has-rig`, `--want-3d`, `--depth-experiment` so the tool can recommend a lane.

Writes `sandbox/presentation_<unit-sid>.json`.

### `python cli.py buildings --faction-sid homm3_example`

Writes the native-slot building plan to `sandbox/buildings_<faction-sid>.json`.

### `python cli.py hero-ability`

```text
python cli.py hero-ability --hero-sid homm3_example_hero_1 --class-type might --extra homm3_example_warcry
```

`--extra` may be repeated. `--replace-commander` plus `--replacement-sid` overwrites the stock commander grant.

Writes `sandbox/hero_abilities_<hero-sid>.json`.

### `python cli.py law`

```text
python cli.py law --faction-sid homm3_example --law-sid homm3_example_growth --name "Example Growth" --description "Native growth." --effect-type cityUnitsIncrement --parameters "h3_example_pikeman,1"
```

`--parameters` is a comma-separated list. Copy the shape from a vanilla law in live Core. Do not invent a new `type` string.

Writes `sandbox/law_overrides_<faction-sid>.json`.

---

## What to do with sandbox files

| You have | Next job (not this kit) |
| --- | --- |
| `faction.json` + checklist | Author real Core rows; pack `Core.zip`; make the faction pickable |
| `ability_overrides_*.json` | Overlay into unit logic/view + language; then test the action bar |
| `presentation_*.json` | Build the matching Unity bundle and plugin visual hooks |
| `hero_abilities_*.json` | Emit specialization/skill grants + ability rows + icons |
| `buildings_*.json` | Fill city-logic bonuses and owned town scene art |
| `law_overrides_*.json` | Emit `DB/fractions_laws` rows |

If you skip packing and only look at sandbox JSON, the game will not change. That is expected.

Day-one order for a whole faction: [18_getting_started.md](18_getting_started.md).
