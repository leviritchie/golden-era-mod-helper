# Component: Direct State

This component is **opt-in native store transactions**. It is not the default combat tool.

## Intent

When you need a journaled write to a native battle store (with rollback semantics), and no Core donor verb already does the job.

## Ownership preference

1. Native Core envelope: unit special, buff, `teleport`, law `unitStat`, trap, etc.
2. Plugin presentation/UI only.
3. Direct State adapter with a traced store recipe.

Older notes that said “reach for Direct State first” are stale.

## What Direct State is for

Traced multi-step writes such as hex occupancy triads, when static tracing has named the store and the publish path.

## What Direct State is not for

- Ordinary Focus abilities (those are Core `energyLevel` actions)
- Passive damage percent (those are law `outDmgMods` / `inDmgMods`)
- Town clicks
- Billboard swaps
- “The Core row looks hard”

## Proof bar

A finished static dossier is not permission to ship MovementPush or Teleport. CapLog store agreement is not a player seeing the unit move.

Banned product patterns (summary):

- Dual-write occupancy through a helper plus a second native write
- Treating donor restore as the product
- Inventing `Method_N` from DiffableCs declaration order
- Owning damage in both a committed-damage Harmony mutator and a Direct State damage adapter

## Related

If you are choosing native versus Direct State for occupancy/push/teleport, you need live decomp evidence, not this teaching kit. This kit only records the ownership rule.
