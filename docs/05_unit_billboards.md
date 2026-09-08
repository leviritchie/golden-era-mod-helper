# Component: Unit billboards

This component is **2D presentation**. It is not Core stats and it is not a skinned mesh.

## Intent

Show a custom creature as a camera-facing sprite in battle and/or as a sanitized upright quad on the adventure map, while native construction still uses a donor prefab the engine can load.

## Why Core mesh fields often stay native

If UnitView `mesh` / construction fields point at a custom path the native loader does not know, combat or preview can crash **before** your replacement hook runs.

Pattern:

1. Core keeps a native-safe donor prefab path.
2. An import table maps your SID to bundle frames, materials, and sounds.
3. After the donor exists, the plugin hides it and shows your billboard.

## Battle billboards

Battle sprites are typically packed `Texture2DArray` frames driven by a frame index matching the DEF group. Sounds are a separate payload.

## Adventure-map billboards

A reliable map quad:

- Sit under a native map shell.
- Use a sanitized `Hex/Lit` material, not a UI sprite material.
- Copy only safe native renderer flags.
- Bind the custom texture into the slots the shader samples.
- Strip terrain blend, vertex displacement, and donor wave state.
- Copy the donor **child** layer onto the quad. Root layer 0 is a common “applied but invisible” failure.
- Check fog, shroud, hover outline, occlusion, and shadows in-game.

Bare `Shader.Find("Hex/Lit")` without donor state can render invisible. Cloning a town building material can leak terrain into a unit quad.

## Independent surfaces

A correct battle billboard does not prove:

- map unit
- hire portrait
- detail preview
- tooltip
- town dwelling billboard

Each is its own bind.

## Depth billboard experiment

There is a 2.5D experiment that displaces billboard pixels with a Video Depth Anything map. The unit **stays a billboard**. It is not the product 3D creature lane. If the depth texture is missing, the shader must leave the flat billboard alone.

## Do not mix with skinned_mesh

If the bundle is `battlePresentationLane: skinned_mesh`, omit battle billboard arrays. Replacing a billboard pack with a skinned-only pack that has no `battle.prefab` causes combat Init to null-dereference.

## Helper widget

Studio → Billboard vs mesh.
