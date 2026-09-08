# Component: Custom town scene

This component is **the 3D/2D town you walk into**. It is not the build-tree JSON.

## Preferred paradigm (one sentence)

Own a vanilla-shaped Unity **city world**, paint custom art onto native `BhBuilding` slots, keep CityUI native, and open construction through HUD navigation.

Factory-style name: `cityFactory` (your faction should use its own dedicated world name, not silently reuse `cityHuman2`).

## What to ship

| Layer | Rule |
| --- | --- |
| Town world | Load a donor city scene, move contents into an owned scene, leave the active world name as the custom scene |
| Building interaction | Native `BhBuilding` / `BhBuildingsManager` + PhysicsRaycaster |
| Building visuals | World quads or meshes on native slots. Art follows native activation. Do not force-activate unbound slots every frame (load storms / black screens) |
| Menus | Native `BUILDING VIEW PANEL`, hire, upgrade |
| Hall construction | HUD `BuildingsConstruction` select. Skip native Main Visit only when it diverges and you have proof |
| Music | If you ship a city-music sidecar, Core `city_music_sounds` must not keep a vanilla donor `soundSetName` or two tracks layer |

## Closed-panel rule

CityUI panels often stay `activeInHierarchy` while closed by disabling `Canvas` or zeroing `CanvasGroup`. Calling native escape on a visually closed upgrade panel can hide the hall menu you just opened.

**Visible open** means Canvas enabled and CanvasGroup actually shown. Hierarchy-active means “exists in the stack.”

## Rejected destinations

Do not treat these as the product end state:

- Route A / Route C: posters on `CanvasCityPanel`, donor-renderer suppress, black CityCamera workarounds as the town world
- Aliasing onto another live faction city (`cityDemon`, hive helpers)
- UI click relays that forward world clicks into RawImage town layers
- Next-frame hall opens assumed to fix “open then close”

Route A can remain a comparison lane. It is not the preferred town.

## Map cursor

Adventure-map hover can keep applying city interact cursors while the owned town world is loaded. That is a separate suppress hook, not a reason to change building clicks.

## Town layers versus hit targets

Visual plates are usually not the click targets. Moving native `BhBuildingView` roots onto a backdrop to “line up the art” breaks the build tree and can show blue hit rectangles. If clicks are wrong, trace native screen state, not the poster.

If a panel is clickable but invisible, lift only the named panel canvas (`BUILDING VIEW PANEL`, `HIRE VIEW PANEL`, `UPGRADE UNIT PANEL`). Do not recursively activate every child (inactive templates become visible).

## Helper widget

The building planner records `townParadigm: owned_city_world` and refuses other values.
