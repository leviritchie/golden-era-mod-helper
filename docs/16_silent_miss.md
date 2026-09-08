# Silent miss / wrong proof

Use this when “the data is there” but battle or UI still fails. Do not invent a second path first.

## Failure classes

### Store key ≠ retrieve key

**Looks like:** dictionary has items; `TryGetValue` misses.

**Do:** pin live Harmony argument type against map key type. Bridge wrappers (Unit.Init side wrapper versus `TransferSide`). A miss with a non-empty map is a failed check, not “no plan.”

### Managed proxy ≠ native identity

**Looks like:** types already match; map still misses under `GetHashCode` / `ReferenceEquals`.

**Do:** key by native pointer. Matching native keys = same native object. Distinct native keys = different objects or wrong owner. Pointer keying does not by itself prove store and retrieve used the same TransferSide instance if the keys differ.

### Wrong collection surface

**Looks like:** another layer shows items; foreach is empty or throws.

**Do:** `Count` + indexer on Il2Cpp lists. Verify the API before copying a foreach from C# desktop habits.

### Producer → consumer window

**Looks like:** planned/registered, then empty at apply; miss logs stay quiet.

**Do:** keep producer state until every consumer ran. Do not clear in an earlier postfix than apply. Do not throw from optional pilots on `BattleLogic.Init` (also runs under adventure-map Loader).

### Wrong proof bar

**Looks like:** logs say planned / registered / stored / verified.

**Do:** that is not applied / presented / user-visible. Label the tier you have.

### QuestScript AND of different event families

**Looks like:** visit fires; dialog never shows.

**Do:** OE conditions are event latches, not state polls. Do not AND visit with Counter/ItemOwnSide in one trigger.

### Town suppressor kills a non-town billboard

**Looks like:** artifact map billboard logs applied, stays invisible.

**Do:** do not pass non-city SIDs as `citySid` into a town donor suppressor. Mark billboard type correctly. Copy donor child layer onto the quad.

### Pattern copy without identity

**Looks like:** you copied a working hook from another feature.

**Do:** re-check object identity, key type, and who mutates. One ownership path.

### Wrong Method_N

**Looks like:** `InvalidCastException` to another EventArgs type, or “success” with empty listeners.

**Do:** DiffableCs declaration index ≠ live Method_N. Pin via field short name.

## Helper widget

Studio → Silent miss doctor.
