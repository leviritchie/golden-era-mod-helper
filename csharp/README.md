# C# example patterns

These files are **teaching copies**. They are not a game plugin. They will not compile against live Olden Era interop as-is.

Placeholder names such as `LiveType_UnitInitSideWrapper` stand in for obfuscated IL2CPP names. Put the live pins in your own `GameSymbols` class after you re-pin against the current `GameAssembly.dll`.

| File | Lesson |
| --- | --- |
| `GameSymbolsPattern.cs` | One registry for live names |
| `FailClosedPatch.cs` | Skip the feature if the symbol is missing |
| `NativePointerKeyedPlan.cs` | Type bridge, then native-pointer keys |
| `DonorForwardLookup.cs` | Custom → donor allowed; donor → custom needs context |
| `FocusAbilityOverlay.cs` | Overlay icons; do not stain native pics |
| `OwnedTownWorld.cs` | Native BhBuilding clicks; visually-open panels |
