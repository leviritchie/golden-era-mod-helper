# Isolation

This repository is a **teaching kit**. It writes overlay-review files under `sandbox/` only.

## Writers never

- Write outside `sandbox/` in the local repository
- Write into a game install (`Core.zip`, `StreamingAssets`, `BepInEx`, `GameAssembly.dll` in the path)
- Pack or patch the game
- Emit Core.zip members (`units_logics`, numbered `DB/fractions/13_….json`, …)

Sandbox JSON is overlay-review only. There is no flag that aims writers at a game install.

## Why sandbox exists

A form that could write into a live `Core.zip` or plugin folder could damage a working game. Practice files stay in `sandbox/`. Copy shapes into a Core overlay pipeline separately.

## How to prove isolation

From the folder that contains `cli.py`:

```text
python cli.py test
```

Those tests fail if a writer can save outside `sandbox/`.

`python cli.py pages` builds static documentation. That output still cannot write into a game install.
