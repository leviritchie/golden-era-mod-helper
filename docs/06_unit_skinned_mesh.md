# Component: Unit skinned meshes

This component is **3D presentation**. One owner. Not a second billboard path.

## Intent

Ship battle, unit preview, and adventure map as a Unity skinned mesh with bone clips. Preview and map loop Idle. Size comes from your authored scale / hex height contract, not from blindly copying donor `localScale`.

## When to choose this lane

You have:

- an owned bind skeleton (not “whatever Meshy auto-rigged” unless you explicitly accept that exception)
- clips whose pose units and loop seams you control
- a bundle that contains the owned prefab and **does not** contain battle billboard arrays

If you only have DEF frames, use [billboards](05_unit_billboards.md).

## Bundle contract (fail-closed)

Skinned-mesh combat bundles:

- include the owned prefab, map prefab (often the same mesh looping Idle), controller, albedo, normal, metallic-gloss
- omit battle `Texture2DArray`, billboard materials, and billboard anims
- use a runtime-compatible shader path (Olden Era world lighting, as used by Golden Era, is `Hex/Lit` after rebind; a glTF shader will show pink `Hidden/InternalErrorShader`)

Combat Init must load a **cached** battle presentation template, not a ResManager load of the donor on that path. Donor loads on Init have frozen combat.

## Preview and map

- Detail preview keeps the Idle mesh for owned-skinned SIDs. Do not cover those with a 2D portrait overlay.
- Preview factory identity is `UnitViewConfig.id`, not `mesh`. Rewrite that id to the dungeon **catalog** id (`trogl`, not folder leaf `troglodyte`).
- Do not stamp `Sprites/Default` overlay materials onto the skinned mesh. That flattens a 3D character into a warped blob.
- Do not copy vanilla child `localScale` (often huge) onto a Meshy-sized bind mesh.
- Adventure map plays Idle. Skip billboard map finish for skinned instances.

## Facing

Mesh facing is usually a glTF orientation bake (example: −90° yaw in glTF so Unity imports +90°). If the unit looks mirrored, check the prefab rotation before flipping a side-facing hook.

## Clips

- Rebase clip paths off the Animator root or every bone stays in bind pose.
- Do not time-stretch fused clips to a stock Esquire idle duration; that melts in-betweens.
- Cycle clips must close at `N * frameDuration`, not on the last interior key.
- Physics smoothing is polish after deliberate motion is accepted. Smoothness alone is not ship.
- Pose JSON numbers may be degrees. Consumers that treat them as radians over-rotate by ~57×.

## Mesh FX

Fire and sparks parent to a bone or bounds from a catalog. Do not bake AnimationEvents into owned clips. Do not hang 3D fire on a billboard phoenix. Do not `MethodInfo.Invoke` `ResManager.Get` from `LateUpdate`, `MapObject.Init`, or main menu — that AccessViolation’d the running Olden Era process while Golden Era was loading FX. Load Core FX through the generated Il2Cpp invoke path, LateUpdate only.

## Helper widget

Studio → Billboard vs mesh. The widget will refuse `skinned_mesh` plus `alsoUseBattleBillboardArrays: true`.
