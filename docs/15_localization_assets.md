# Component: Localization and icons

This component is **text tokens and sprite keys**. It is not mechanics.

## Localization

- Own tokens in `Lang/<locale>/texts/*.json` inside Core.
- English cleanup does not automatically fix other locales. Stale “placeholder / MVP” translations can remain.
- Member filenames are exact. Inspect live Core.
- Do not describe implementation debt to the player.

## Icon keys

Runtime sprite keys look like `assassin_buff_icon` or `space_6_magic_blink` when those keys already exist in the live serialized sprite registry.

A custom key such as Golden Era’s `sub_skill_faction_homm3_ability_halberd_hook` only works if your plugin allowlists that exact key and ships the PNG. Pasting a custom key into this kit does not create the art.

Not icon keys:

- `h3_pikeman_stunning_blow_name` (localization)
- `SomeAtlas_Orientation@4x` (export filename)

Custom keys that are not in the serialized Unity sprite registry need a plugin resolver **and** a deployed PNG/payload. Missing art is often the wrong key, a placeholder overlay sitting above the portrait, or a resolver that never saw the key — not a missing file in source control.

## Skill and hero-bar icons

Faction skill icons are often an exact filename contract:

`skill_faction_<faction>.png`, `_2.png`, `_3.png`

Hero-bar custom abilities read packed Core `hero_abilities.json` rows. A blank button with registered hooks is a cache load-count bug until proven otherwise.

## Portraits

Hero JSON `icon` fields do not automatically display plugin PNGs. Patch the owning UI component. Avoid global `Image.sprite` hooks. Clear `overrideSprite` on pooled rows.

## Preview versus combat

Combat ability icons and preview-window ability icons are different binders. Fixing one does not fix the other.
