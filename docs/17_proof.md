# Proof labels

Do not promote a claim up this ladder without new evidence.

| Id | Label | Means | Does not mean |
| --- | --- | --- | --- |
| source_static | source / static validated | File, schema, or named dump exists | Game loaded it |
| generated | generated artifact validated | Generator output passed a gate | Install has that output |
| build_target | build target proven | Compiled against the intended interop | Live DLL is that build |
| deployed | deployed / installed payload proven | Read back from the install | Combat or town worked |
| startup_smoke | startup smoke proven | Process launched; required hooks logged exact success | Feature presented |
| runtime | runtime behavior proven | Probe/log shows the mutation ran | A person saw it |
| user_visible | user-visible gameplay proven | A person saw the intended result | (top of ladder) |

## Practical order when something fails

1. Which live artifact is running? DLL, config, Core.zip, bundles.
2. Which layer? Data load, sprite resolve, map object, battle init, material, clicks.
3. Which log has the fatal line? Often `Player.log`.
4. Is a custom id entering a native dictionary that lacks it?
5. Is a donor id reverse-mapped without context?
6. Do logic and view arrays match?
7. Is a serialized Unity asset involved?
8. Did a symbol drift?
9. Is the “fix” a fallback that hides a missing contract?
10. Can you validate packed JSON without launching the whole game?

## This helper’s proof

The kit itself is source/static plus sandbox generation. Running the studio does not prove Olden Era gameplay, and it does not prove the Golden Era mod is installed.
