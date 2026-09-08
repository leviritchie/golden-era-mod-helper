# Golden Era Mod Helper

A **teaching kit** for people who have never modded *Heroes of Might and Magic: Olden Era* (the Golden Era PC build) and need the jobs named, in order, in plain language.

Public clone: https://github.com/leviritchie/golden-era-mod-helper

This repository does **not** install a faction into your game. It does not need your Steam folder. Clone it anywhere, run Python, get practice JSON in `sandbox/`, then copy those shapes into **your** overlay and plugin.

## If you have never done this

Read these three files in order:

1. [docs/20_glossary.md](docs/20_glossary.md) — what words like Core.zip, SID, Focus, Harmony, and donor mean.
2. [docs/21_tools.md](docs/21_tools.md) — what every studio page and `python cli.py` command does, field by field, and what it will not do.
3. [docs/18_getting_started.md](docs/18_getting_started.md) — a day-one order for a new faction (identity → data → selector → map objects → art lane → Focus → heroes → town → laws → proof).

Then open [PRINCIPLES.md](PRINCIPLES.md) before you write a Harmony patch.

## Requirements

- Python 3.10 or newer on PATH
- A web browser (only for the studio)
- No game install is required to run the kit

## Run the studio

In a terminal, change directory to **this clone** (the folder that contains `cli.py`):

```text
python cli.py studio --port 8777
```

Open `http://127.0.0.1:8777`. Leave the terminal open while you use the site. The site is only on your computer.

The first two items in the documentation list inside the studio are **Glossary** and **What every tool does**.

## Run the same writers from the terminal

```text
python cli.py test
python cli.py templates
python cli.py scaffold-faction --short-name example --display-name Example --donor castle
```

Full command list and argument meanings: [docs/21_tools.md](docs/21_tools.md).

## What gets written

Only files under `sandbox/` in this clone. The writers refuse paths outside that folder, and they refuse path pieces that look like a game install (`Core.zip`, `StreamingAssets`, `BepInEx`, `GameAssembly.dll`).

Generated sandbox files are gitignored except `sandbox/README.md`.

## What this is not

- Not official Ubisoft / Unfrozen documentation
- Not a BepInEx plugin you drop into the game
- Not permission to copy copyrighted Heroes art into your own repo
- Not a claim that a sandbox JSON file is live in combat

## License

See [LICENSE](LICENSE). Heroes of Might and Magic and related names are trademarks of their owners. This project is unofficial.
