# Studio widgets (short index)

Read [21_tools.md](21_tools.md) for every page, form field, CLI argument, what a successful save looks like, and what the game will not do.

This page is a map.

The studio is a local form UI:

```text
python cli.py studio --port 8777
```

Then open `http://127.0.0.1:8777`. It does not deploy mods. Keep that process running while using the studio.

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

After a save, open **Sandbox files** in the left nav, or look on disk under `sandbox/` in the repository folder. Those files are not in the game until they are copied into a Core overlay.
