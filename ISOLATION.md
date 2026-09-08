# Isolation (why this kit cannot install your mod)

This repository is a **teaching kit**. It writes practice files only.

## What it will never do

- Write outside the `sandbox/` folder inside this clone
- Write into a game install (`Core.zip`, `StreamingAssets`, `BepInEx`, `GameAssembly.dll` in the path)
- Pack or patch the game
- Import a private overlay generator from some other repo

There is no command-line flag that turns those writes on. That omission is the product.

## Why sandbox exists

If a documentation tool could write into a live `Core.zip` or plugin folder, a form click could damage a working game. Practice files stay here. **You** copy them into your own pipeline when you are ready.

## How to prove isolation on your machine

From this clone:

```text
python cli.py test
```

Those tests fail if a writer can save outside `sandbox/`.
