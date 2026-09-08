# Studio widgets (short index)

If you have never used this kit, do not stop on this page. Read [21_tools.md](21_tools.md). That document explains every page, every form field, every CLI argument, what a successful save looks like, and what the game will not do.

This page is only a map.

The studio is a website that runs on **your** computer:

```text
python cli.py studio --port 8777
```

Then open `http://127.0.0.1:8777`. It does not deploy mods. Leave the terminal open while you use the site.

| Left-nav page | What you are doing | Writes under `sandbox/` |
| --- | --- | --- |
| Focus ability assigner | Give a creature a Focus special (JSON field `energyLevel`) | `ability_overrides_<faction>.json` |
| Faction scaffold | Start a town identity plus a checklist of the other jobs | `faction_<sid>/` pack + checklist |
| Billboard vs mesh | Choose 2D sprite vs 3D model for one unit | `presentation_<unit>.json` |
| Hero abilities | Commander attack vs extra hero buttons | `hero_abilities_<hero>.json` |
| Buildings and town | Native building slots plus owned town world | `buildings_<faction>.json` |
| Faction laws | One native law-tree bonus | `law_overrides_<faction>.json` |
| Hook catalog, silent miss, proof, sandbox list | Look up families, diagnose “data exists but UI does nothing,” list files | Nothing (read only) |

Invalid Focus icon keys (localization tokens, `@4x` atlas names) are refused.

After a save, open **Sandbox files** in the left nav, or look on disk under `sandbox/` in this clone. Those files are not in the game until you copy them into your own overlay.
